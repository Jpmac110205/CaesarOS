from caesaros.services.model_outputs import CodingResult


async def propose(state, ctx):
    return await ctx.reasoner.generate('code', state, CodingResult,
        'Perform the coding stage: produce a title, request-specific implementation or preparation steps, '
        'and a code artifact when useful (otherwise null). Use the supplied repository context, '
        'interview details and notes. Identify missing source files instead of inventing repository contents.')
