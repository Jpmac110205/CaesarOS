import asyncio
import importlib
import logging
from copy import deepcopy
from datetime import datetime
from time import perf_counter
from zoneinfo import ZoneInfo
import httpx

from caesaros.graphs.main_graph import build_graph
from caesaros.services.catalog import DemoServices
from caesaros.services.reasoning import Reasoner
from caesaros.services.jev import Jev
from caesaros.state.workflow_state import TERMINAL, new_state

logger = logging.getLogger(__name__)


def label_time(value, timezone):
    return datetime.fromisoformat(value).astimezone(ZoneInfo(timezone)).strftime('%I:%M %p').lstrip('0')


class Runtime:
    def __init__(self, store, settings):
        self.store, self.settings = store, settings
        self.services, self.reasoner = DemoServices(store), Reasoner(settings, save=self.save)
        self.jev = Jev(settings, save=self.save)
        self.graph = build_graph(self)
        self.tasks = {}
        self.semaphore = asyncio.Semaphore(4)
        # Persisted snapshots survive restarts; interrupted executions are explicit.
        with store.connect() as db:
            import json
            interrupted = [json.loads(row[0]) for row in db.execute('SELECT body FROM runs')]
        for state in interrupted:
            if state['workflow_status'] not in TERMINAL:
                for agent in state['agents'].values():
                    if agent['status'] == 'running':
                        agent['status'] = 'failed'
                state.update(workflow_status='failed', error='Server restarted during execution. Retry this request.', current_agent=None)
                self.save(state)

    def save(self, state):
        self.store.save_run(state)

    def event(self, state, node, message):
        state['events'].append({'at': datetime.now(ZoneInfo(state['timezone'])).isoformat(), 'node': node, 'message': message})

    async def pause(self):
        await asyncio.sleep(self.settings.step_delay)

    async def tool(self, state, name, call):
        start = perf_counter()
        result = call()
        state['tool_results'].append({'tool': name, 'provider': 'local demo service', 'status': 'completed',
                                      'duration_ms': round((perf_counter() - start) * 1000), 'result': result})
        self.event(state, state['current_agent'], f'{name} · local demo data retrieved')
        self.save(state)
        return result

    def agent_node(self, name):
        run = importlib.import_module(f'agents.{name}.agent').run

        async def execute(original):
            state = deepcopy(original)
            state['current_agent'] = name
            state['agents'][name]['status'] = 'running'
            self.event(state, name, 'Reading shared state and loading service context.')
            self.save(state)
            await self.pause()
            start = perf_counter()
            for attempt in range(1, 3):
                state['agents'][name]['attempts'] = attempt
                baseline = deepcopy(state)
                try:
                    await run(state, self)
                    output = state[f'{name}_output']
                    if name in {'planner', 'fitness', 'code'}:
                        output['summary'] = await self.reasoner.narrate(name, state, output)
                    break
                except (httpx.TransportError, httpx.HTTPStatusError, ConnectionError) as exc:
                    transient = not isinstance(exc, httpx.HTTPStatusError) or exc.response.status_code in {429, 500, 502, 503, 504}
                    if not transient or attempt == 2:
                        raise
                    # Keep accounting for successful calls before a later stage failed.
                    metrics = state['metrics']
                    state = baseline
                    state['metrics'] = metrics
                    state['metrics']['retries'] += 1
                    self.event(state, name, 'Transient provider failure; retrying once.')
                    self.save(state)
                    await asyncio.sleep(.5)
            state['agents'][name].update(status='completed', summary=output['summary'],
                                         duration_ms=round((perf_counter() - start) * 1000))
            state['cursor'] += 1
            self.event(state, name, f"Wrote {name}_output to shared state.")
            self.save(state)
            return state
        return execute

    async def respond(self, original):
        state = deepcopy(original)
        state['current_agent'] = 'response'
        workflow = state['selected_workflow']
        if state['decision']['gate'] == 'clarify':
            state.update(workflow_status='needs_clarification',
                final_response='What would you like to work on: your schedule, a workout, coursework, email, or a software project? Add a goal or choose a workflow above.')
        else:
            sections, blocks = [], []
            if state['email_output']:
                output = state['email_output']
                sections.append('Inbox\n' + output['summary'])
                sections.extend('• ' + e['subject'] + ' — ' + e['body'] for e in output['important_emails'])
                if workflow in {'email', 'interview'} and output['draft']:
                    sections.append('Reply draft (not sent)\n' + output['draft'])
            if state['planner_output']:
                output = state['planner_output']
                sections.append('Plan for ' + output['date'] + '\n' + output['summary'])
                blocks.extend(output['planned_blocks'])
                if output['priorities']:
                    sections.append('Priorities\n' + '\n'.join('• ' + t['title'] for t in output['priorities']))
            if state['tutor_output']:
                output = state['tutor_output']
                sections.append('Study context\n' + output['summary'])
                if output['practice_questions']:
                    sections.append('Practice\n' + '\n'.join('• ' + q for q in output['practice_questions']))
            if state['fitness_output']:
                output = state['fitness_output']
                sections.append('Training\n' + output['summary'])
                if output['workout']:
                    blocks.append(output['workout'])
            if state['code_output']:
                sections.append('Engineering\n' + state['code_output']['summary'])
            for i, item in enumerate(sorted(blocks, key=lambda b: b['start'])):
                sections.append(f"{label_time(item['start'], state['timezone'])}–{label_time(item['end'], state['timezone'])} · {item['title']}")
                state['proposed_actions'].append({'id': f"{state['id']}:calendar:{i}", 'type': 'calendar.create',
                    'title': item['title'], 'status': 'pending', 'requires_approval': True,
                    'payload': {'title': item['title'], 'start': item['start'], 'end': item['end']},
                    'target': 'local demo calendar'})
            if blocks:
                sections.append('Review the proposed calendar blocks below. Each requires your approval before being added to the demo calendar.')
            state['final_response'] = '\n\n'.join(sections)
            state['workflow_status'] = 'awaiting_approval' if blocks else 'completed'
            if workflow == 'evening_review':
                self.services.review_memory(state['id'], state['planner_output']['summary'])
                self.event(state, 'memory', 'Saved evening review to local demo memory.')
            if workflow in {'morning_digest', 'afternoon_checkin', 'evening_review'}:
                self.services.notify(state['id'], state['final_response'])
                self.event(state, 'notifications', 'Digest saved to the local notification feed.')
        state.update(current_agent=None, finished_at=datetime.now(ZoneInfo(state['timezone'])).isoformat())
        state['metrics']['duration_ms'] = round((datetime.fromisoformat(state['finished_at']) - datetime.fromisoformat(state['created_at'])).total_seconds() * 1000)
        self.event(state, 'response', state['workflow_status'].replace('_', ' ').capitalize())
        self.save(state)
        return state

    def submit(self, request):
        state = new_state(request, self.settings.timezone)
        state['metrics']['reasoner'] = self.settings.reasoner
        self.save(state)
        task = asyncio.create_task(self.execute(state))
        self.tasks[state['id']] = task
        task.add_done_callback(lambda _: self.tasks.pop(state['id'], None))
        return state

    async def execute(self, state):
        try:
            async with self.semaphore:
                await self.graph.ainvoke(state, config={'recursion_limit': 24})
        except asyncio.CancelledError:
            latest = self.store.run(state['id'])
            if latest['workflow_status'] in TERMINAL:
                return
            for agent in latest['agents'].values():
                if agent['status'] == 'running':
                    agent['status'] = 'cancelled'
            latest.update(workflow_status='cancelled', current_agent=None, error='Execution cancelled. Retry the request to run again.')
            self.event(latest, 'runtime', 'Execution cancelled.')
            self.save(latest)
            raise
        except Exception as exc:
            # Never return provider response bodies or credentials to API clients.
            logger.warning('Workflow %s failed (%s)', state['id'], type(exc).__name__)
            latest = self.store.run(state['id'])
            active = latest['current_agent']
            if active in latest['agents']:
                latest['agents'][active]['status'] = 'failed'
            latest.update(workflow_status='failed', current_agent=None,
                          error=f'{type(exc).__name__}: workflow could not finish. Check the configured provider and retry.')
            self.event(latest, active or 'runtime', latest['error'])
            self.save(latest)

    async def close(self):
        tasks = list(self.tasks.values())
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
