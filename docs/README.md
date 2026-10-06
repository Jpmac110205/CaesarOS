# Project documentation

This folder contains the design source and the integration handoff material.

- `PROJECT_OVERVIEW.txt` preserves the complete project description that drove the demo.
- `INTEGRATIONS.md` explains what is implemented, what remains a TODO, the expected contracts, and the credentials or external setup you must provide.

The root `README.md` is the operational starting point: installation, demo scenarios, architecture overview, API summary, and test commands. The README inside every source folder explains local ownership and how that folder participates in the larger request lifecycle.

When architecture changes, update the closest folder README first and then update the root overview if the public behavior, startup process, or cross-layer flow changed. Never place credentials, personal message contents, or OAuth tokens in documentation examples.

