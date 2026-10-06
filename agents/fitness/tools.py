async def load_context(state, ctx):
    state['fitness_data'] = await ctx.tool(state, 'benefit.training_context', ctx.services.fitness)
