from agents.code.tools import load_context
from agents.code.coding.agent import propose
from agents.code.testing.agent import review
from agents.code.critiquing.agent import critique
from agents.tutor.tools import retrieve

async def run(state, ctx):
    await load_context(state, ctx)
    if state['selected_workflow'] == 'interview':
        await retrieve(state, ctx, 'interview sliding window')
    coding = propose(state)
    testing = review(coding)
    critiquing = critique(coding, testing)
    state['code_output'] = {'summary': coding['title'] + '\n' + '\n'.join(coding['steps']),
        'coder_output': coding, 'testing_output': testing, 'critiquing_output': critiquing,
        'preparation_blocks': state['planner_output'].get('planned_blocks', []),
        'request': state['user_input'], 'mode': 'Demo template; live Claude mode can reason about supplied context.'}
