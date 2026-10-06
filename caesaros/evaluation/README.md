# Evaluation

This folder holds small, executable checks for decision quality. `routing_eval.py` runs ten representative requests through the bounded router and compares the selected workflow with the expected one.

Run it with:

```bash
.venv-demo/bin/python -m caesaros.evaluation.routing_eval
```

The current cases are smoke tests that protect obvious routing behavior. A `10/10` result does not establish real-world accuracy or confidence calibration.

The evaluator calls live Jev and consumes OpenRouter credits. Add a versioned, held-out dataset that includes ambiguous requests, multi-domain requests, adversarial content, and requests that should ask for clarification. Track per-workflow precision/recall, calibration, latency, tokens, cost, retries, and failure rate. Keep evaluation data separate from the examples used to tune the router.

