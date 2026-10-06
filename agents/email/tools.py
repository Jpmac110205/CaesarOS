async def load_context(state, ctx):
    state['emails'] = await ctx.tool(state, 'email.list', ctx.services.emails)
