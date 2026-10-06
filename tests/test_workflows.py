import asyncio
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient

from caesaros.api.app import create_app
from caesaros.config import Settings
from caesaros.services.catalog import available_blocks
from caesaros.state.workflow_state import TERMINAL


@pytest.fixture
def settings(tmp_path):
    return Settings(database=tmp_path / 'demo.sqlite3', step_delay=0)


@pytest.fixture
def client(settings):
    with TestClient(create_app(settings)) as client:
        yield client


def wait_run(client, run_id):
    for _ in range(300):
        state = client.get('/api/runs/' + run_id).json()
        if state['workflow_status'] in TERMINAL:
            return state
        time.sleep(.01)
    pytest.fail('Workflow did not reach a terminal state')


def run(client, prompt, workflow='auto'):
    response = client.post('/api/runs', json={'user_input': prompt, 'workflow': workflow})
    assert response.status_code == 202
    return wait_run(client, response.json()['id'])


def test_workout_shared_state_and_approval(client):
    state = run(client, 'Can I fit a workout into my schedule today?')
    assert state['agent_sequence'] == ['planner', 'fitness']
    assert state['agents']['planner']['status'] == state['agents']['fitness']['status'] == 'completed'
    workout = state['fitness_output']['workout']
    assert workout['minutes'] == 75
    assert datetime.fromisoformat(workout['start']).hour == 17
    assert state['workflow_status'] == 'awaiting_approval'
    before = client.get('/api/overview').json()['data']['calendar_events']
    action = state['proposed_actions'][0]
    url = f"/api/runs/{state['id']}/actions/{action['id']}"
    for _ in range(2):
        response = client.post(url, json={'decision': 'approve'})
        assert response.status_code == 200
    after = client.get('/api/overview').json()['data']['calendar_events']
    assert len(after) == len(before) + 1  # Idempotent deterministic execution.
    next_state = run(client, 'Can I fit a workout into my schedule today?')
    assert next_state['fitness_output']['workout']['start'] != workout['start']


def test_study_retrieval_and_nonoverlapping_blocks(client):
    state = run(client, 'I have a physics exam Thursday. Figure out what I should study tonight.')
    assert state['agent_sequence'] == ['planner', 'tutor']
    assert {d['id'] for d in state['retrieved_documents']} == {'physics-forces', 'physics-energy'}
    blocks = state['planner_output']['planned_blocks']
    assert len(blocks) == 3
    for previous, current in zip(blocks, blocks[1:]):
        assert datetime.fromisoformat(current['start']) - datetime.fromisoformat(previous['end']) >= timedelta(minutes=10)
    for block in blocks:
        for event in state['calendar_events']:
            assert not (datetime.fromisoformat(block['start']) < datetime.fromisoformat(event['end']) and
                        datetime.fromisoformat(block['end']) > datetime.fromisoformat(event['start']))


def test_interview_chain_uses_email_and_planner_state(client):
    state = run(client, 'I got an interview email. Help me prepare.')
    assert state['agent_sequence'] == ['email', 'planner', 'code']
    assert state['email_output']['interview']['id'] == 'recruiter'
    assert state['code_output']['preparation_blocks'] == state['planner_output']['planned_blocks']
    assert state['code_output']['testing_output']['executed'] is False
    assert state['sources'][0]['id'] == 'algorithms'
    assert 'not sent' in state['final_response']


def test_confidence_gates(client):
    ambiguous = run(client, 'hmm')
    assert ambiguous['workflow_status'] == 'needs_clarification'
    assert not ambiguous['tool_results'] and not ambiguous['proposed_actions']
    escalated = run(client, 'Help me organize my priorities')
    assert escalated['decision']['gate'] == 'escalate'
    assert escalated['decision']['escalation']
    assert any(e['node'] == 'reasoning' for e in escalated['events'])


def test_daily_plan_from_overview_example(client):
    state = run(client, 'Figure out what I should do tonight.')
    assert state['agent_sequence'] == ['email', 'planner', 'tutor', 'fitness']
    assert state['workflow_status'] == 'awaiting_approval'
    assert all(state['agents'][name]['status'] == 'completed' for name in state['agent_sequence'])
    blocks = sorted([a['payload'] for a in state['proposed_actions']], key=lambda b: b['start'])
    for previous, current in zip(blocks, blocks[1:]):
        assert previous['end'] <= current['start']


def test_concurrent_state_isolation(client):
    first = client.post('/api/runs', json={'user_input': 'Explain virtual memory.'}).json()
    second = client.post('/api/runs', json={'user_input': 'Can I fit a workout into my schedule today?'}).json()
    first, second = wait_run(client, first['id']), wait_run(client, second['id'])
    assert first['id'] != second['id']
    assert first['tutor_output'] and not first['fitness_output']
    assert second['fitness_output'] and not second['tutor_output']
    assert all(e['node'] != 'fitness' for e in first['events'])


def test_approval_conflict_rejection_and_reset(client):
    first = run(client, 'Fit a workout into today')
    second = run(client, 'Fit a workout into today')
    def approve(state, decision):
        action = state['proposed_actions'][0]
        return client.post(f"/api/runs/{state['id']}/actions/{action['id']}", json={'decision': decision})
    assert approve(first, 'approve').status_code == 200
    assert approve(second, 'approve').status_code == 409  # Stale plan cannot overwrite calendar.
    assert approve(second, 'reject').status_code == 200
    assert approve(second, 'approve').status_code == 409
    third = run(client, 'Fit a workout into today')
    assert client.post('/api/demo/reset').status_code == 200
    assert approve(third, 'approve').status_code == 409


def test_scheduled_review_observes_tasks_and_saves_memory(client):
    assert client.patch('/api/tasks/physics', json={'completed': True}).status_code == 200
    response = client.post('/api/schedules/evening_review/run')
    state = wait_run(client, response.json()['id'])
    assert state['planner_output']['completed_tasks'] == 1
    assert 'Physics problem set' not in [t['title'] for t in state['planner_output']['priorities']]
    data = client.get('/api/overview').json()['data']
    assert any(m['id'] == state['id'] for m in data['memory'])
    assert any(n['run_id'] == state['id'] for n in data['notifications'])


def test_persistence_and_schedule_restore(settings):
    with TestClient(create_app(settings)) as first:
        state = run(first, 'Explain the kernel.')
        assert first.patch('/api/schedules/morning_digest', json={'enabled': True, 'hour': 8, 'minute': 15}).status_code == 200
    with TestClient(create_app(settings)) as second:
        assert second.get('/api/runs/'+state['id']).json()['tutor_output'] == state['tutor_output']
        schedule = next(s for s in second.get('/api/overview').json()['schedules'] if s['id'] == 'morning_digest')
        assert schedule['enabled'] and schedule['minute'] == 15
        next_run = datetime.fromisoformat(schedule['next_run'])
        assert next_run.hour == 8 and next_run.minute == 15
        assert next_run.utcoffset() == next_run.astimezone(ZoneInfo(settings.timezone)).utcoffset()


def test_sse_validation_unknown_topic_and_no_time(client):
    assert client.get('/').status_code == 200
    assert client.post('/api/runs', json={'user_input': '  '}).status_code == 422
    assert client.post('/api/runs', json={'user_input': 'x', 'workflow': 'bad'}).status_code == 422
    assert client.get('/api/runs/missing/events').status_code == 404
    state = run(client, 'Explain quantum field theory')
    assert state['tutor_output']['needs_context']
    assert not state['sources']
    response = client.get(f"/api/runs/{state['id']}/events")
    assert response.headers['content-type'].startswith('text/event-stream')
    assert 'event: state' in response.text
    assert state['id'] in response.text
    # Completely busy calendars should yield no fitness proposal.
    def busy(data):
        day = datetime.fromisoformat(data['calendar_events'][0]['start'])
        data['calendar_events'].append({'id': 'busy', 'title': 'Busy evening', 'source': 'Demo',
            'start': day.replace(hour=17, minute=0).isoformat(), 'end': day.replace(hour=23, minute=0).isoformat()})
    client.app.state.store.update_data(busy)
    workout = run(client, 'Fit a workout into today')
    assert workout['fitness_output']['workout'] is None
    assert not workout['proposed_actions']


def test_overlapping_busy_intervals():
    start = datetime(2026, 10, 5, 17, tzinfo=ZoneInfo('America/New_York'))
    events = [{'start': (start + timedelta(minutes=a)).isoformat(), 'end': (start + timedelta(minutes=b)).isoformat()}
              for a, b in [(30, 90), (60, 120), (180, 210)]]
    free = available_blocks(events, start, start + timedelta(hours=4))
    assert [b['minutes'] for b in free] == [30, 60, 30]


def test_retry_and_failure_do_not_claim_completion(client):
    original = client.app.state.runtime.services.fitness
    calls = 0
    def transient():
        nonlocal calls
        calls += 1
        if calls == 1:
            raise ConnectionError('temporary service failure')
        return original()
    client.app.state.runtime.services.fitness = transient
    state = run(client, 'Fit a workout into today')
    assert calls == 2 and state['metrics']['retries'] == 1
    assert state['agents']['fitness']['attempts'] == 2
    def broken():
        raise ValueError('sensitive provider payload must not leak')
    client.app.state.runtime.services.fitness = broken
    state = run(client, 'Fit a workout into today')
    assert state['workflow_status'] == 'failed'
    assert state['agents']['fitness']['status'] == 'failed'
    assert not state['final_response'] and not state['proposed_actions']
    assert 'sensitive' not in state['error']


def test_cancel_running_workflow(tmp_path):
    settings = Settings(database=tmp_path/'cancel.sqlite3', step_delay=.2)
    with TestClient(create_app(settings)) as client:
        state = client.post('/api/runs', json={'user_input': 'Fit a workout into today'}).json()
        result = client.post('/api/runs/'+state['id']+'/cancel')
        assert result.status_code == 200
        assert result.json()['workflow_status'] == 'cancelled'
        assert not result.json()['proposed_actions']
