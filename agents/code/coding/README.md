# Coding stage

`await propose(state, ctx)` asks OpenAI for a request-specific title, implementation/preparation steps, and an optional code artifact. It validates `CodingResult` and uses supplied repository/interview/source context. It has no repository write or execution tool.
