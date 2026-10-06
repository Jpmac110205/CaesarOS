from caesaros.services.model_outputs import CritiqueResult


async def critique(state, ctx, proposal, testing):
    generated = await ctx.reasoner.generate('code', state, CritiqueResult,
        'Perform the critique stage: review the actual coding proposal and proposed tests. '
        'Identify concrete defects, missing cases and improvements. Do not claim any tests passed.',
        coding_proposal=proposal, testing=testing)
    return {**generated, 'status': 'reviewed'}
