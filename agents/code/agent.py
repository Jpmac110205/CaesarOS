from agents.code.tools import load_context
from agents.code.coding.agent import propose
from agents.code.testing.agent import review
from agents.code.critiquing.agent import critique
from agents.tutor.tools import retrieve


async def run(state, ctx):
    await load_context(state, ctx)
    if state['selected_workflow'] == 'interview':
        await retrieve(state, ctx, state['user_input'] + '\n' + str(state['email_output'].get('interview')))
    coding = await propose(state, ctx)
    testing = await review(state, ctx, coding)
    critiquing = await critique(state, ctx, coding, testing)
    state['code_output'] = {'coder_output': coding, 'testing_output': testing, 'critiquing_output': critiquing,
        'preparation_blocks': state['planner_output'].get('planned_blocks', []),
        'request': state['user_input'], 'mode': 'OpenAI generation; proposed code and tests are not executed'}
