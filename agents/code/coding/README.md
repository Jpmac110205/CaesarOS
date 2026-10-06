# Coding stage

This is the first stage inside the Code Agent. `agent.py` receives the full workflow state and creates a structured proposal.

For interview preparation it uses the recruiter context and returns a timed practice sequence plus a small sliding-window example. For general engineering requests it returns an implementation plan focused on service contracts, authenticated adapters, normalized data, and validation.

It does not write files, execute code, or call another agent. Its return value is passed by `agents/code/agent.py` to the testing stage. `prompt.md` records the intended role if this stage later receives its own model call; `tools.py` is intentionally empty because project data is loaded once by the parent Code Agent.

