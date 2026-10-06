"""Offline provider fixtures exist only in tests; production has no mock mode."""
import json
import httpx
import pytest

REAL_ASYNC_CLIENT = httpx.AsyncClient
ROUTES = {
    'Can I fit a workout into my schedule today?': 'workout',
    'Fit a workout into today': 'workout',
    'I have a physics exam Thursday. Figure out what I should study tonight.': 'study',
    'I got an interview email. Help me prepare.': 'interview',
    'Figure out what I should do tonight.': 'daily_plan',
    'Explain virtual memory.': 'tutor', 'Explain the kernel.': 'tutor',
    'Explain quantum field theory': 'tutor', 'hmm': 'clarify',
    'Help me organize my priorities': 'daily_plan',
}


def fixture_result(name, context):
    workflow = context.get('selected_workflow')
    if name == 'PlanningSelection':
        pending = sorted((t for t in context['tasks'] if not t['completed']), key=lambda t: (t['priority'], t['due']))
        items = []
        if workflow == 'study':
            items = [{'title': f'Study block {i}', 'minutes': m} for i, m in enumerate([60, 45, 30])]
        elif workflow == 'interview':
            items = [{'title': 'Interview preparation', 'minutes': 90}]
        elif workflow in {'daily_plan', 'morning_digest', 'afternoon_checkin'}:
            items = [{'title': t['title'], 'minutes': t['minutes']} for t in pending[:2]]
        return {'priority_ids': [t['id'] for t in pending], 'focus_items': items}
    if name == 'TutorResult':
        return {'summary': 'Provider-generated lesson.' if context['retrieved_documents'] else 'Please supply course material.',
                'practice_questions': ['Explain the retrieved concept.'] if context['retrieved_documents'] else []}
    if name == 'EmailResult':
        return {'summary': 'Provider-generated inbox analysis.', 'draft': 'Provider-generated reply draft.'}
    if name == 'CodingResult':
        return {'title': 'Provider-generated implementation', 'steps': ['Implement the requested feature.'], 'artifact': 'print(1)'}
    if name == 'TestReview':
        return {'cases': ['Verify the expected output.']}
    if name == 'CritiqueResult':
        return {'notes': ['Review input validation.']}
    if name == 'RouteSelection':
        return {'workflow': 'daily_plan', 'reason': 'Provider resolved planning intent.'}
    raise AssertionError(f'Unexpected model schema: {name}')


@pytest.fixture(autouse=True)
def offline_providers(monkeypatch):
    def handle(request):
        payload = json.loads(request.content)
        if request.url.host == 'api.openai.com':
            context = json.loads(payload['input'][0]['content'])
            name = payload.get('text', {}).get('format', {}).get('name')
            text = json.dumps(fixture_result(name, context)) if name else 'Provider-generated summary of validated context.'
            return httpx.Response(200, json={'id': 'test-response', 'model': payload['model'], 'status': 'completed',
                'output': [{'type': 'message', 'content': [{'type': 'output_text', 'text': text}]}],
                'usage': {'input_tokens': 120, 'output_tokens': 30}})
        if request.url.host == 'openrouter.ai':
            context, answers = payload['state'], {}
            for name, question in payload['questions'].items():
                if name == 'workflow':
                    choice = ROUTES[context['request']]
                    confidence = .78 if context['request'] == 'Help me organize my priorities' else .96
                elif name == 'category':
                    choice = {'recruiter': 'interview', 'course': 'coursework', 'newsletter': 'newsletter'}.get(context['email']['id'], 'other')
                    if choice not in question['criteria']:
                        choice = 'other'
                    confidence = .96
                elif name == 'action_required':
                    answers[name] = {'type': 'noul', 'noul': .95 if context['email']['id'] in {'recruiter', 'course'} else .05}
                    continue
                elif name == 'relevant':
                    query, doc_id = context['query'].lower(), context['document']['id']
                    relevant = ((('physics' in query or 'tonight' in query) and doc_id.startswith('physics')) or
                                ('virtual memory' in query and doc_id == 'os-memory') or
                                ('kernel' in query and doc_id == 'os-kernel') or
                                ('interview' in query and doc_id == 'algorithms'))
                    answers[name] = {'type': 'noul', 'noul': .95 if relevant else .05}
                    continue
                else:
                    raise AssertionError(f'Unexpected Jev question: {name}')
                answers[name] = {'type': 'choice', 'choice': choice, 'confidence': confidence,
                                 'probabilities': {key: 1 if key == choice else 0 for key in question['criteria']}}
            return httpx.Response(200, json={'id': 'test-decision', 'model': payload['model'], 'answers': answers,
                                            'usage': {'input_tokens': 80, 'output_tokens': 0, 'cost': .00001}})
        raise AssertionError(f'Unexpected provider host: {request.url.host}')
    transport = httpx.MockTransport(handle)
    monkeypatch.setattr(httpx, 'AsyncClient', lambda **kwargs: REAL_ASYNC_CLIENT(**kwargs, transport=transport))
