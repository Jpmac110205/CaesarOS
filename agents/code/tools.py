async def load_context(state, ctx):
    state['github_context'] = await ctx.tool(state, 'github.project_context', ctx.services.github)
