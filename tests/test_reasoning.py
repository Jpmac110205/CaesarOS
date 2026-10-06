import json
import httpx
import pytest
from caesaros.config import Settings
from caesaros.services.reasoning import Reasoner
from caesaros.state.models import RunRequest
from caesaros.state.workflow_state import new_state

REAL_ASYNC_CLIENT = httpx.AsyncClient


def mock_provider(monkeypatch, content, status=200):
    requests = []
    def handle(request):
        requests.append(request)
        return httpx.Response(status, json={'content': [{'type': 'text', 'text': content}],
                                           'usage': {'input_tokens': 120, 'output_tokens': 30}})
    transport = httpx.MockTransport(handle)
    monkeypatch.setattr(httpx, 'AsyncClient', lambda **kwargs: REAL_ASYNC_CLIENT(**kwargs, transport=transport))
    return requests


@pytest.mark.asyncio
async def test_claude_payload_usage_and_deterministic_schedule(monkeypatch):
    requests = mock_provider(monkeypatch, 'A grounded summary.')
    reasoner = Reasoner(Settings(reasoner='claude', api_key='test-key', claude_model='test-model'))
    state = new_state(RunRequest(user_input='Plan my day'), 'America/New_York')
    output = {'summary': 'Demo summary', 'planned_blocks': [{'start': '2026-10-05T19:00:00-04:00'}]}
    text = await reasoner.narrate('planner', state, output)
    assert text == 'A grounded summary.'
    request = requests[0]
    assert request.url.path == '/v1/messages'
    assert request.headers['x-api-key'] == 'test-key'
    payload = json.loads(request.content)
    assert payload['model'] == 'test-model'
    assert json.loads(payload['messages'][0]['content'])['structured_result'] == output
    assert output['planned_blocks'][0]['start'] == '2026-10-05T19:00:00-04:00'
    assert state['metrics']['input_tokens'] == 120
    assert state['metrics']['output_tokens'] == 30
    assert state['metrics']['model_calls'] == 1


@pytest.mark.asyncio
async def test_escalation_validates_workflow_and_provider_errors(monkeypatch):
    mock_provider(monkeypatch, '{"workflow":"execute_shell","reason":"unsafe"}')
    reasoner = Reasoner(Settings(reasoner='claude', api_key='test-key', claude_model='test-model'))
    state = new_state(RunRequest(user_input='Organize my priorities'), 'America/New_York')
    with pytest.raises(ValueError, match='unsupported workflow'):
        await reasoner.escalate(state)
    mock_provider(monkeypatch, 'Error', status=401)
    with pytest.raises(httpx.HTTPStatusError):
        await reasoner.narrate('planner', state, {'summary': 'No silent demo fallback'})
