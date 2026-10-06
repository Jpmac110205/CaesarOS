# CaesarOS bounded decision layer

Select a workflow from the registry in caesaros/decision/router.py.
Return a structured workflow, confidence, reason and provider.
At confidence >= 0.90, run the selected read/recommendation workflow.
At 0.65–0.89, escalate to the reasoning provider; below 0.65 ask for clarification.
LangGraph owns execution order and state. Never call an agent directly.
All calendar writes still require explicit action approval.

The live adapter asks a typed Jev Choice question through OpenRouter. Jev returns a choice and confidence; Python applies the gates. OpenAI resolves medium-confidence choices.
