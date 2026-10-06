# Tutor Agent

Retrieves candidate documents and memory from the service layer. Jev evaluates source relevance through OpenRouter. OpenAI creates a source-grounded lesson and practice questions using `prompt.md`; these are validated as `TutorResult`.

`documents_used` and `needs_context` are derived from the actual selected source list. If no sources match, the model must explain the missing context and return no practice questions. Course materials remain synthetic until `DemoServices.documents()` and `.memory()` are replaced with Prodigy adapters.
