# Decision layer

This folder contains small, bounded decisions that do not need long-form generation.

`router.py` maps a user request to an allowed workflow and returns a score, explanation, provider label, and confidence gate. It also defines the workflow registry—the ordered agent sequence for every supported workflow. Explicit workflow selection receives confidence `1.0`.

`relevance.py` scores candidate personal documents using transparent tag matches and returns at most three. The demo score is a useful inspection aid, not retrieval science or a calibrated probability.

This is the place to integrate Jev because the outputs are constrained and easy to validate. A production adapter should:

1. Return only workflow names present in `WORKFLOWS`.
2. Produce calibrated confidence from a labeled evaluation set.
3. Fail closed when output is malformed.
4. Preserve the high/medium/low gating policy.
5. Leave action approval independent of confidence.

Complex explanations remain the reasoning provider's responsibility. Deterministic actions remain Python's responsibility.

