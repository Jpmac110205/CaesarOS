# Code Agent

Loads repository context and, for interview workflows, retrieves relevant notes. Its coding → testing → critiquing stages each call OpenAI and validate a structured result. The actual proposal and tests are passed to the next stage. OpenAI then summarizes their combined result.

`code_output` contains `coder_output`, `testing_output`, `critiquing_output`, and Planner preparation blocks. There are no fixed example artifacts or canned reviews. Repository context is still synthetic; source-file retrieval, repository edits and code execution are unimplemented. Python sets `testing_output.executed: false` because no execution tool exists.
