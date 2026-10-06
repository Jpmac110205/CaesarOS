import asyncio
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from caesaros.config import ROOT, Settings
from caesaros.decision.router import WORKFLOWS
from caesaros.graphs.runtime import Runtime
from caesaros.scheduling.scheduler import Scheduler
from caesaros.services.fixtures import seed_data
from caesaros.services.store import Store
from caesaros.state.models import ApprovalRequest, RunRequest, ScheduleUpdate, TaskUpdate
from caesaros.state.workflow_state import TERMINAL


def create_app(settings=None):
    settings = settings or Settings.from_env()
    settings.validate()

    @asynccontextmanager
    async def lifespan(app):
        app.state.store = Store(settings.database, settings.timezone)
        app.state.runtime = Runtime(app.state.store, settings)
        app.state.scheduler = Scheduler(app.state.runtime)
        app.state.scheduler.start()
        yield
        app.state.scheduler.close()
        await app.state.runtime.close()

    app = FastAPI(title='CaesarOS', version='0.1.0', lifespan=lifespan,
                  description='Live OpenAI reasoning and OpenRouter Jev decisions with labeled synthetic integration data.')
    app.mount('/static', StaticFiles(directory=ROOT / 'frontend'), name='static')

    def get_run(run_id):
        state = app.state.store.run(run_id)
        if not state:
            raise HTTPException(404, 'Workflow not found')
        return state

    @app.get('/')
    async def index():
        return FileResponse(ROOT / 'frontend' / 'index.html')

    @app.get('/api/health')
    async def health():
        return {'status': 'ok', 'reasoner': settings.reasoner, 'router': 'openrouter/jev',
                'data_mode': 'demo', 'timezone': settings.timezone,
                'models': {'reasoner': settings.openai_model, 'router': settings.jev_model}}

    @app.get('/api/overview')
    async def overview():
        data = app.state.store.data()
        runs = app.state.store.runs()
        return {'data': data, 'schedules': app.state.scheduler.list(),
                'mode': {'data': 'demo', 'reasoner': settings.reasoner, 'router': 'openrouter/jev', 'timezone': settings.timezone},
                'workflows': WORKFLOWS,
                'integrations': [{'name': name, 'status': 'demo', 'todo': todo} for name, todo in [
                    ('Google Calendar & Tasks', 'OAuth + normalized calendar/task adapters'),
                    ('Gmail', 'Read-only OAuth + Gmail adapter'),
                    ('Prodigy', 'User-scoped retrieval and memory APIs'),
                    ('BeneFIT', 'Authenticated workout history API'),
                    ('GitHub', 'Fine-grained read-only token + repository adapter')]] + [
                    {'name': 'Jev / OpenRouter', 'status': 'configured', 'todo': f'{settings.jev_model}: real decisions API; usage recorded per call'},
                    {'name': 'OpenAI', 'status': 'configured', 'todo': f'{settings.openai_model}: real Responses API; usage recorded per call'},
                    {'name': 'Discord', 'status': 'setup required', 'todo': 'Set bot token, owner and channel; start the client separately'}],
                'metrics': {'runs': len(runs), 'completed': sum(r['workflow_status'] in {'completed', 'awaiting_approval'} for r in runs),
                            'pending': sum(a['status'] == 'pending' for r in runs for a in r['proposed_actions']),
                            'average_ms': round(sum(r['metrics']['duration_ms'] for r in runs) / len(runs)) if runs else 0}}

    @app.post('/api/runs', status_code=202)
    async def submit(request: RunRequest):
        if not request.user_input.strip():
            raise HTTPException(422, 'Enter a request')
        if len(app.state.runtime.tasks) >= 20:
            raise HTTPException(429, 'Workflow queue is full; try again shortly')
        return app.state.runtime.submit(request)

    @app.get('/api/runs')
    async def history():
        return app.state.store.runs()

    @app.get('/api/runs/{run_id}')
    async def run(run_id: str):
        return get_run(run_id)

    @app.get('/api/runs/{run_id}/events')
    async def events(run_id: str, request: Request):
        get_run(run_id)
        async def stream():
            revision = -1
            while not await request.is_disconnected():
                state = get_run(run_id)
                if state['revision'] != revision:
                    revision = state['revision']
                    yield f'id: {revision}\nevent: state\ndata: {json.dumps(state)}\n\n'
                if state['workflow_status'] in TERMINAL:
                    break
                await asyncio.sleep(.15)
        return StreamingResponse(stream(), media_type='text/event-stream', headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})

    @app.post('/api/runs/{run_id}/cancel')
    async def cancel(run_id: str):
        state = get_run(run_id)
        task = app.state.runtime.tasks.get(run_id)
        if not task or state['workflow_status'] in TERMINAL:
            raise HTTPException(409, 'Workflow is no longer running')
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        # A task cancelled before its coroutine starts still needs a terminal record.
        state = get_run(run_id)
        if state['workflow_status'] not in TERMINAL:
            state.update(workflow_status='cancelled', current_agent=None)
            app.state.store.save_run(state)
        return get_run(run_id)

    @app.post('/api/runs/{run_id}/actions/{action_id}')
    async def approve(run_id: str, action_id: str, request: ApprovalRequest):
        try:
            return app.state.store.approve(run_id, action_id, request.decision)
        except KeyError as exc:
            raise HTTPException(404, str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(409, str(exc)) from exc

    @app.patch('/api/tasks/{task_id}')
    async def task(task_id: str, request: TaskUpdate):
        def update(data):
            item = next((t for t in data['tasks'] if t['id'] == task_id), None)
            if not item:
                raise HTTPException(404, 'Task not found')
            item['completed'] = request.completed
            return item
        return app.state.store.update_data(update)

    @app.patch('/api/schedules/{name}')
    async def schedule(name: str, request: ScheduleUpdate):
        item = next((s for s in app.state.store.schedules() if s['id'] == name), None)
        if not item:
            raise HTTPException(404, 'Schedule not found')
        item.update(request.model_dump())
        app.state.store.save_schedule(item)
        app.state.scheduler.configure(item)
        return app.state.scheduler.list()

    @app.post('/api/schedules/{name}/run', status_code=202)
    async def run_schedule(name: str):
        if not any(s['id'] == name for s in app.state.store.schedules()):
            raise HTTPException(404, 'Schedule not found')
        return await app.state.scheduler.trigger(name)

    @app.post('/api/demo/reset')
    async def reset():
        tasks = list(app.state.runtime.tasks.items())
        if any(app.state.store.run(run_id)['workflow_status'] not in TERMINAL for run_id, _ in tasks):
            raise HTTPException(409, 'Wait for running workflows before resetting demo data')
        # The last snapshot can be terminal just before LangGraph releases its task.
        if tasks:
            await asyncio.gather(*(task for _, task in tasks), return_exceptions=True)
        # Explicit reset invalidates old pending proposals while preserving history.
        with app.state.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            db.execute('UPDATE data SET body=? WHERE id=1', (json.dumps(seed_data(settings.timezone)),))
            for run_id, body in db.execute('SELECT id, body FROM runs').fetchall():
                state = json.loads(body)
                for action in state['proposed_actions']:
                    if action['status'] == 'pending':
                        action['status'] = 'rejected'
                if state['workflow_status'] == 'awaiting_approval':
                    state['workflow_status'] = 'completed'
                state['revision'] += 1
                db.execute('UPDATE runs SET body=? WHERE id=?', (json.dumps(state), run_id))
        return {'status': 'reset'}

    return app
