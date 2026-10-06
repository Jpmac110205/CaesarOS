from caesaros.services.model_outputs import TestReview


async def review(state, ctx, proposal):
    generated = await ctx.reasoner.generate('code', state, TestReview,
        'Perform the testing stage: inspect the coding proposal and generate specific test cases '
        'for its artifact and steps. No execution tool exists; these are proposed tests.', coding_proposal=proposal)
    return {**generated, 'status': 'test_cases_generated', 'executed': False}
