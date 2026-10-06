from agents.tutor.tools import retrieve
from caesaros.services.model_outputs import TutorResult


async def run(state, ctx):
    priorities = state['planner_output'].get('priorities', [])
    query = state['user_input']
    if state['selected_workflow'] == 'daily_plan' and priorities:
        query += '\nSelected priorities: ' + ', '.join(t['title'] for t in priorities)
    docs = await retrieve(state, ctx, query)
    generated = await ctx.reasoner.generate('tutor', state, TutorResult,
        'Answer the educational request from the retrieved documents and generate relevant practice_questions. '
        'Cite document IDs or titles. If no matching documents exist, explain the missing context and '
        'return no practice questions. Do not substitute a canned lesson.')
    if not docs and generated['practice_questions']:
        raise ValueError('Tutor generated practice without source context')
    state['tutor_output'] = {**generated, 'documents_used': [d['id'] for d in docs],
        'study_blocks': state['planner_output'].get('planned_blocks', []), 'needs_context': not bool(docs)}
