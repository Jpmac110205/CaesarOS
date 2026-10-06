"""Small routing smoke benchmark; replace with a held-out labeled set for Jev."""
from caesaros.decision.router import route

CASES = [
    ('Can I fit a workout into my schedule today?', 'workout'),
    ('Explain virtual memory.', 'tutor'),
    ('I have a physics exam Thursday. Figure out what I should study tonight.', 'study'),
    ('I got an interview email. Help me prepare.', 'interview'),
    ('Figure out what I should do tonight.', 'daily_plan'),
    ('Summarize my inbox.', 'email'),
    ('Review the architecture of CaesarOS.', 'code'),
    ('Prepare my morning digest.', 'morning_digest'),
    ('Review my day.', 'evening_review'),
    ('hmm', ''),
]


def evaluate():
    results = [{'request': request, 'expected': expected, 'actual': route(request)['workflow']} for request, expected in CASES]
    return {'correct': sum(r['expected'] == r['actual'] for r in results), 'total': len(results), 'cases': results,
            'note': 'Demo smoke cases only; this is not a measurement of general routing accuracy.'}


if __name__ == '__main__':
    import json
    print(json.dumps(evaluate(), indent=2))
