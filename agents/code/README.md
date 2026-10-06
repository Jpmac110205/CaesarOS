# Code Agent

The Code Agent supports software-project planning and technical interview preparation. It is structured internally as coding, testing, and critique stages, all within one LangGraph agent node.

`tools.py` retrieves normalized project context. For interview workflows, the agent also retrieves the relevant Prodigy interview guide. `agent.py` then passes structured data through:

1. `coding/`: proposes the implementation steps or interview exercise.
2. `testing/`: generates an edge-case checklist.
3. `critiquing/`: reviews boundaries, credentials, coupling, and validation.

The combined result is written to `code_output`, including each sub-stage result and Planner's preparation blocks. In demo mode it may include a small example function, but it never executes user code or claims that tests passed. `testing_output.executed` remains false.

This internal pipeline demonstrates the desired review loop without granting repository write or shell-execution capabilities. To turn it into a real coding worker, add an isolated execution service, explicit repository scope, test result capture, iteration limits, and approval for repository mutations. Provider credentials belong in the service layer.

