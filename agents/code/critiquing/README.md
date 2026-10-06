# Critique stage

`await critique(state, ctx, proposal, testing)` calls OpenAI with the actual proposal and proposed test cases. It validates `CritiqueResult` and returns concrete review notes. It does not execute tests, repair a repository or run an iterative coding loop.
