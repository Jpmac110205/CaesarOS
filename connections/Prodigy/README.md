# Prodigy integration placeholder

Prodigy remains the knowledge, retrieval, memory, document-ingestion, and rich frontend application. CaesarOS consumes it as a separate service rather than importing its database or ChromaDB directly.

The intended read contract returns document chunks with stable ID, title, text content, tags/metadata, and a human-readable source. The memory contract returns user-scoped preferences and long-term context. Write operations such as an evening-review memory should be idempotent and attributable to a CaesarOS run ID.

The standalone `/frontend` dashboard is the reference implementation for Prodigy's future Agents Mode. Prodigy can submit to `/api/runs`, subscribe to `/api/runs/{id}/events`, render agent/state/source information, and post action decisions.

Keep document ingestion, embeddings, vector search, metadata filtering, reranking, and conversation memory inside Prodigy. The adapter TODOs are in `caesaros/services/catalog.py`; a minimal frontend call pattern is in `docs/INTEGRATIONS.md`.

