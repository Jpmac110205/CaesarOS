from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from agents.planner.tools import available_blocks, load_context, reserve

async def run(state, ctx):
    await load_context(state, ctx)
    day = datetime.fromisoformat(ctx.store.data()['date']).replace(tzinfo=ZoneInfo(state['timezone']))
    workflow = state['selected_workflow']
    if workflow == 'evening_review':
        day += timedelta(days=1)
    free = available_blocks(state['calendar_events'], day.replace(hour=17), day.replace(hour=22, minute=30))
    pending = sorted((t for t in state['tasks'] if not t['completed']), key=lambda t: (t['priority'], t['due']))
    blocks = []
    titles = []
    if workflow == 'study':
        titles = [('Study · concepts and worked examples', 60), ('Study · applications', 45), ('Study · practice problems', 30)]
    elif workflow == 'interview':
        interview = state['email_output'].get('interview')
        if interview:
            titles = [('Technical interview preparation · ' + interview['sender'], 90)]
    elif workflow in {'daily_plan', 'morning_digest'}:
        titles = [(pending[0]['title'], pending[0]['minutes'])] if pending else []
        if workflow == 'daily_plan' and len(pending) > 1:
            titles += [(pending[1]['title'], pending[1]['minutes'])]
    elif workflow == 'afternoon_checkin':
        titles = [(t['title'], t['minutes']) for t in pending[:2]]
    for title, minutes in titles:
        allocated = reserve(free, minutes, title, earliest_hour=19)
        if allocated:
            blocks.append(allocated)
    completed = sum(t['completed'] for t in state['tasks'])
    summary = f"{len(free)} remaining time windows; {len(pending)} open priorities."
    if workflow == 'evening_review':
        summary = f"{completed}/{len(state['tasks'])} tasks complete. Tomorrow’s first priority: {pending[0]['title'] if pending else 'no outstanding tasks'}."
    state['planner_output'] = {'summary': summary, 'date': day.date().isoformat(),
        'available_blocks': free, 'planned_blocks': blocks, 'priorities': pending,
        'completed_tasks': completed, 'planning_basis': 'Synthetic demo day, 5 PM–10:30 PM'}
