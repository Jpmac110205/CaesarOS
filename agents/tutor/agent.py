from agents.tutor.tools import retrieve

async def run(state, ctx):
    query = 'physics exam' if state['selected_workflow'] == 'daily_plan' else state['user_input']
    docs = await retrieve(state, ctx, query)
    if not docs:
        summary = 'No matching demo course materials were found. Connect Prodigy or try physics, virtual memory, the kernel, or sliding window.'
    else:
        summary = '\n\n'.join(f"{d['title']}\n{d['content']}" for d in docs)
    blocks = state['planner_output'].get('planned_blocks', [])
    questions = ['Draw a free-body diagram for a block on an incline.', 'When can mechanical energy be treated as conserved?'] if any('physics' in d['id'] for d in docs) else ['Explain the concept in your own words.', 'Give one example and explain its failure cases.']
    state['tutor_output'] = {'summary': summary, 'documents_used': [d['id'] for d in docs],
                            'study_blocks': blocks, 'practice_questions': questions if docs else [],
                            'needs_context': not bool(docs)}
