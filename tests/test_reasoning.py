import json
import httpx
import pytest
from pydantic import ValidationError
from caesaros.config import Settings
from caesaros.services.reasoning import Reasoner
from caesaros.services.jev import Jev
from caesaros.services.model_api import ProviderResponseError
from caesaros.services.model_outputs import TutorResult
from caesaros.decision.router import route
from caesaros.state.models import RunRequest
from caesaros.state.workflow_state import new_state

REAL_ASYNC_CLIENT = httpx.AsyncClient


def mock_provider(monkeypatch, body, status=200):
    requests = []
    def handle(request):
        requests.append(request)
        return httpx.Response(status, json=body)
    transport = httpx.MockTransport(handle)
    monkeypatch.setattr(httpx, 'AsyncClient', lambda **kwargs: REAL_ASYNC_CLIENT(**kwargs, transport=transport))
    return requests


def openai_body(text, **overrides):
    return {'id': 'resp-test', 'model': 'test-model', 'status': 'completed',
            'output': [{'type': 'message', 'content': [{'type': 'output_text', 'text': text}]}],
            'usage': {'input_tokens': 120, 'output_tokens': 30}, **overrides}


def state():
    return new_state(RunRequest(user_input='Organize my priorities'), 'America/New_York')


@pytest.mark.asyncio
async def test_openai_payload_usage_and_deterministic_schedule(monkeypatch):
    requests = mock_provider(monkeypatch, openai_body('A grounded summary.'))
    reasoner = Reasoner(Settings(api_key='test-key', openai_model='test-model'))
    current = state()
    output = {'planned_blocks': [{'start': '2026-10-05T19:00:00-04:00'}]}
    assert await reasoner.narrate('planner', current, output) == 'A grounded summary.'
    request = requests[0]
    assert request.url == 'https://api.openai.com/v1/responses'
    assert request.headers['authorization'] == 'Bearer test-key'
    payload = json.loads(request.content)
    assert payload['model'] == 'test-model' and payload['store'] is False
    assert json.loads(payload['input'][0]['content'])['structured_result'] == output
    assert output['planned_blocks'][0]['start'] == '2026-10-05T19:00:00-04:00'
    assert current['metrics']['input_tokens'] == 120
    assert current['metrics']['output_tokens'] == 30
    assert current['metrics']['model_calls'] == 1
    assert current['metrics']['provider_calls'][0]['provider'] == 'openai'


@pytest.mark.asyncio
async def test_structured_results_and_escalation_validation(monkeypatch):
    requests = mock_provider(monkeypatch, openai_body('{"summary":"A source-grounded lesson","practice_questions":["Why?"]}'))
    reasoner = Reasoner(Settings(api_key='test-key'))
    generated = await reasoner.generate('tutor', state(), TutorResult, 'Teach from context.')
    assert generated['practice_questions'] == ['Why?']
    fmt = json.loads(requests[0].content)['text']['format']
    assert fmt['type'] == 'json_schema' and fmt['strict'] is True
    mock_provider(monkeypatch, openai_body('{"workflow":"execute_shell","reason":"unsafe"}'))
    with pytest.raises(ValidationError):
        await reasoner.escalate(state())


@pytest.mark.asyncio
@pytest.mark.parametrize('body,status,expected', [
    ({'error': 'unauthorized'}, 401, httpx.HTTPStatusError),
    (openai_body('', status='incomplete'), 200, ProviderResponseError),
    (openai_body(''), 200, ProviderResponseError),
    (openai_body('', output=[{'type': 'message', 'content': [{'type': 'refusal', 'refusal': 'No'}]}]), 200, ProviderResponseError),
])
async def test_provider_failures_never_fall_back(monkeypatch, body, status, expected):
    mock_provider(monkeypatch, body, status)
    with pytest.raises(expected):
        await Reasoner(Settings(api_key='test-key')).narrate('planner', state(), {})


@pytest.mark.asyncio
async def test_real_jev_contract_confidence_and_usage(monkeypatch):
    from caesaros.decision.router import WORKFLOW_DESCRIPTIONS
    body = {'model': 'typesafe/jev-1.13', 'answers': {'workflow': {
        'type': 'choice', 'choice': 'daily_plan', 'confidence': .78,
        'probabilities': {key: 1 if key == 'daily_plan' else 0 for key in WORKFLOW_DESCRIPTIONS}}},
        'usage': {'input_tokens': 50, 'output_tokens': 0, 'cost': .001}}
    requests = mock_provider(monkeypatch, body)
    current = state()
    result = await route(current, Jev(Settings(jev_api_key='router-key')))
    assert result['gate'] == 'escalate' and result['confidence'] == .78
    request = requests[0]
    assert request.url == 'https://openrouter.ai/api/alpha/decisions'
    assert request.headers['authorization'] == 'Bearer router-key'
    payload = json.loads(request.content)
    assert payload['state'] == {'request': current['user_input']}
    assert payload['questions']['workflow']['type'] == 'choice'
    assert current['metrics']['provider_calls'][0]['cost_usd'] == .001


@pytest.mark.asyncio
@pytest.mark.parametrize('answer', [
    {'type': 'choice', 'choice': 'execute_shell', 'confidence': .99},
    {'type': 'choice', 'choice': 'daily_plan', 'confidence': 1.1},
    {'type': 'choice', 'choice': 'daily_plan', 'confidence': float('nan')},
    {'type': 'noul', 'noul': .9},
])
async def test_jev_rejects_invalid_decisions(monkeypatch, answer):
    # NaN cannot be encoded by httpx; exercise the validator directly for that case.
    if isinstance(answer.get('confidence'), float) and answer['confidence'] != answer['confidence']:
        from caesaros.services.jev import probability
        with pytest.raises(ProviderResponseError):
            probability(answer['confidence'])
        return
    mock_provider(monkeypatch, {'answers': {'workflow': answer}})
    with pytest.raises(ProviderResponseError):
        await route(state(), Jev(Settings(jev_api_key='test')))


@pytest.mark.asyncio
async def test_explicit_workflow_has_no_fabricated_confidence(monkeypatch):
    requests = mock_provider(monkeypatch, {})
    current = new_state(RunRequest(user_input='Plan this', workflow='daily_plan'), 'America/New_York')
    decision = await route(current, Jev(Settings()))
    assert decision['provider'] == 'user selection' and decision['confidence'] is None
    assert not requests
