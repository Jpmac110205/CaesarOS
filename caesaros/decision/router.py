"""Workflow allowlist and live Jev intent routing; no keyword classifier."""
WORKFLOWS = {
    'workout': ['planner', 'fitness'], 'study': ['planner', 'tutor'],
    'interview': ['email', 'planner', 'code'],
    'daily_plan': ['email', 'planner', 'tutor', 'fitness'],
    'tutor': ['tutor'], 'email': ['email'], 'code': ['code'],
    'morning_digest': ['email', 'planner', 'fitness'],
    'afternoon_checkin': ['planner'], 'evening_review': ['email', 'planner']}

WORKFLOW_DESCRIPTIONS = {
    'workout': 'Find time for exercise and recommend training.',
    'study': 'Allocate study time and teach from course materials for an exam or class.',
    'interview': 'Read interview email, allocate preparation time, and prepare technical practice.',
    'daily_plan': 'Coordinate multiple personal priorities across the day or evening.',
    'tutor': 'Explain or teach a concept without scheduling a study session.',
    'email': 'Summarize or prioritize an inbox and draft a reply.',
    'code': 'Help with software implementation, debugging or architecture.',
    'morning_digest': 'Produce a morning summary of messages, calendar and fitness.',
    'afternoon_checkin': 'Review progress and remaining priorities in the afternoon.',
    'evening_review': 'Review completed tasks and prepare tomorrow.',
    'clarify': 'The request is unclear, unsupported, or lacks a goal.'}


async def route(state, jev):
    requested = state['requested_workflow']
    if requested != 'auto':
        if requested not in WORKFLOWS:
            raise ValueError('Unsupported requested workflow')
        return {'workflow': requested, 'confidence': None, 'reason': 'Explicit workflow selected by the user.',
                'provider': 'user selection', 'gate': 'execute'}
    answers = await jev.decide(state, {'request': state['user_input']}, {
        'workflow': {'type': 'choice', 'instructions': 'Select the workflow that best serves this request. '
                     'Use clarify if no supported workflow is appropriate.', 'criteria': WORKFLOW_DESCRIPTIONS}})
    answer = answers['workflow']
    workflow = '' if answer['choice'] == 'clarify' else answer['choice']
    confidence = answer['confidence']
    return {'workflow': workflow, 'confidence': confidence, 'probabilities': answer['probabilities'],
            'reason': f"Jev selected {answer['choice']}.", 'provider': 'openrouter/jev',
            'gate': 'clarify' if not workflow or confidence < .65 else 'escalate' if confidence < .9 else 'execute'}
