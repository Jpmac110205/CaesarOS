from caesaros.services.catalog import available_blocks, reserve

async def load_context(state, ctx):
    state['calendar_events'] = await ctx.tool(state, 'calendar.list', ctx.services.calendar)
    state['tasks'] = await ctx.tool(state, 'tasks.list', ctx.services.tasks)
    state['memory_context'] = await ctx.tool(state, 'memory.retrieve', ctx.services.memory)
