import re

WORKFLOWS = {
    'workout': ['planner', 'fitness'], 'study': ['planner', 'tutor'],
    'interview': ['email', 'planner', 'code'],
    'daily_plan': ['email', 'planner', 'tutor', 'fitness'],
    'tutor': ['tutor'], 'email': ['email'], 'code': ['code'],
    'morning_digest': ['email', 'planner', 'fitness'],
    'afternoon_checkin': ['planner'], 'evening_review': ['email', 'planner']}


def contains(text, phrases):
    return any(re.search(r'\b' + re.escape(word) + r'\b', text) for word in phrases)


def route(user_input: str, requested='auto') -> dict:
    """Jev stand-in: scores are inspectable rules, not calibrated probabilities.

    TODO(JEV): Replace with your model, validate against WORKFLOWS, and calibrate
    confidence on labeled requests. No Jev endpoint contract was supplied.
    """
    q = user_input.lower()
    rules = [
        (['morning digest', 'good morning'], 'morning_digest', .98, 'Summarize email, calendar and fitness.'),
        (['evening review', 'review my day'], 'evening_review', .97, 'Review completed and remaining tasks.'),
        (['check-in', 'check my progress', 'remaining priorities'], 'afternoon_checkin', .95, 'Re-evaluate unfinished tasks.'),
        (['interview', 'recruiter', 'technical assessment'], 'interview', .96, 'Extract interview details, find time, prepare technical practice.'),
        (['workout', 'gym', 'fitness', 'exercise'], 'workout', .96, 'Check availability before recommending a workout.'),
        (['exam', 'study tonight', 'study plan', 'prepare for class'], 'study', .94, 'Combine available time with retrieved course notes.'),
        (['explain', 'teach', 'virtual memory', 'kernel', 'physics', 'newton'], 'tutor', .95, 'Answer an educational question using personal documents.'),
        (['email', 'inbox', 'mail'], 'email', .95, 'Prioritize communication and prepare a draft.'),
        (['code', 'debug', 'github', 'architecture', 'repository', 'software'], 'code', .94, 'Inspect project context and build an engineering plan.'),
        (['what should i do', 'what i should do', 'plan my day', 'plan tonight', 'plan my evening', 'daily plan', 'schedule today'], 'daily_plan', .93, 'Coordinate deadlines, communication, study and fitness.'),
        (['organize', 'priorities', 'productive', 'help me plan'], 'daily_plan', .78, 'Planning intent is plausible; escalate the bounded decision.')]
    if requested != 'auto':
        workflow, confidence, reason = requested, 1., 'Explicit workflow selected by the user.'
    else:
        workflow, confidence, reason = '', .4, 'Intent is unclear; ask for a goal before executing agents.'
        for phrases, chosen, score, explanation in rules:
            if contains(q, phrases):
                workflow, confidence, reason = chosen, score, explanation
                break
    return {'workflow': workflow, 'confidence': confidence, 'reason': reason,
            'provider': 'demo rules (Jev adapter)',
            'gate': 'execute' if confidence >= .9 else 'escalate' if confidence >= .65 else 'clarify'}
