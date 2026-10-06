from copy import deepcopy
from agents.fitness.tools import load_context
from caesaros.services.catalog import reserve


async def run(state, ctx):
    await load_context(state, ctx)
    data = state['fitness_data']
    available = deepcopy(state['planner_output'].get('available_blocks', []))
    workout = reserve(available, data['duration_minutes'], data['next_workout'] + ' workout', earliest_hour=17)
    state['fitness_output'] = {'workout': workout,
        'exercises': data['exercises'] if workout else [], 'weekly_sessions': data['weekly_sessions'], 'goal': data['goal']}
