"""Small live Jev routing smoke benchmark; running this consumes OpenRouter credits."""
import asyncio
import json
from caesaros.config import Settings
from caesaros.decision.router import route
from caesaros.services.jev import Jev
from caesaros.state.models import RunRequest
from caesaros.state.workflow_state import new_state

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


async def evaluate():
    settings = Settings.from_env()
    jev, results = Jev(settings), []
    for request, expected in CASES:
        state = new_state(RunRequest(user_input=request), settings.timezone)
        decision = await route(state, jev)
        results.append({'request': request, 'expected': expected, 'actual': decision['workflow'],
                        'decision': decision, 'metrics': state['metrics']})
    return {'correct': sum(r['expected'] == r['actual'] for r in results), 'total': len(results), 'cases': results,
            'note': 'Live smoke cases only; not a held-out routing accuracy benchmark.'}


if __name__ == '__main__':
    print(json.dumps(asyncio.run(evaluate()), indent=2))
