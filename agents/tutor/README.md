# Tutor Agent

Tutor answers educational requests from retrieved personal material rather than pretending it has searched Prodigy when it has not.

`tools.py` obtains candidate documents and memory through service adapters. It runs the bounded relevance filter, adds selected documents to `retrieved_documents`, and exposes citations in `sources`. `agent.py` builds the explanation, connects it to Planner's study blocks when present, generates practice questions, and writes `tutor_output`.

For the demo, available topics include physics, virtual memory, kernels, and sliding-window interview problems. An unknown topic sets `needs_context: true` and clearly reports that matching personal course material was not found.

The separation between retrieval and explanation matters:

1. Prodigy or the demo service returns candidate chunks.
2. The decision layer filters them for relevance.
3. Tutor reasons from the selected chunks.
4. The response exposes the source title, ID, and score.

`prompt.md` governs optional Claude narration and requires source-grounded answers. When Prodigy is connected, replace `DemoServices.documents()` and `.memory()` while preserving normalized source IDs and user scoping. Embeddings, vector search, ingestion, and reranking should remain inside Prodigy.

