# Decision layer

`router.py` defines allowed workflows and calls live Jev through OpenRouter for automatic intent routing. It preserves returned confidence and probabilities. Explicit workflow selections bypass the model and have `confidence: null`.

Confidence ≥0.90 executes; 0.65–0.89 escalates to OpenAI; lower confidence or the `clarify` choice asks for clarification. Invalid provider outputs fail the workflow. Thresholds are application policy, not a measured accuracy claim. Calendar approval remains separate.

`relevance.py` asks Jev a Noul question for each candidate document, keeps probabilities ≥0.65, sorts them, and returns at most three. There is no lexical scoring or fake confidence. Candidate data remains synthetic until Prodigy is connected.

The HTTP adapter and typed-answer validation live in `caesaros/services/jev.py`.
