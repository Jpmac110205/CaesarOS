from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from agents.planner.tools import available_blocks, load_context, reserve
from caesaros.services.model_outputs import PlanningSelection


async def run(state, ctx):
    await load_context(state, ctx)
    day = datetime.fromisoformat(ctx.store.data()['date']).replace(tzinfo=ZoneInfo(state['timezone']))
    if state['selected_workflow'] == 'evening_review':
        day += timedelta(days=1)
    free = available_blocks(state['calendar_events'], day.replace(hour=17), day.replace(hour=22, minute=30))
    pending = {t['id']: t for t in state['tasks'] if not t['completed']}
    selection = await ctx.reasoner.generate('planner', state, PlanningSelection,
        'Select priority_ids from the unfinished tasks. Order by the user goal, deadlines, and memory preferences. '
        'Generate focus_items (title and minutes) appropriate to this workflow and request. '
        'For a workout request, leave time for Fitness and return no focus_items. '
        'For evening review, select tomorrow priorities but return no focus_items. '
        'Do not invent personal deadlines or tasks. Python will allocate each focus item into actual free windows.',
        available_blocks=free, planning_date=day.date().isoformat())
    ids = selection['priority_ids']
    if len(ids) != len(set(ids)) or any(task_id not in pending for task_id in ids):
        raise ValueError('OpenAI selected unknown or completed task IDs')
    blocks = []
    for item in selection['focus_items']:
        allocated = reserve(free, item['minutes'], item['title'], earliest_hour=19)
        if allocated:
            blocks.append(allocated)
    state['planner_output'] = {'date': day.date().isoformat(),
        'available_blocks': free, 'planned_blocks': blocks, 'priorities': [pending[task_id] for task_id in ids],
        'completed_tasks': sum(t['completed'] for t in state['tasks']),
        'planning_basis': 'Synthetic sample day, 5 PM–10:30 PM; OpenAI selects focus items, Python allocates time'}
