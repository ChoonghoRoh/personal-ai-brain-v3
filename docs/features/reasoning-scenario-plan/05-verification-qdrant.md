# Verification — Qdrant (Vector DB)

**Purpose**: Reasoning Lab–related Qdrant verification.
**Source**: [01-verification-data-index.md](01-verification-data-index.md) §3, [reasoning-lab-feature-report.md](../reasoning-lab-feature-report.md) §7.
**Do not modify**: Original feature report.

---

## 1. Scope

- **Collection**: `brain_documents` (COLLECTION_NAME in config).
- **Usage**: Semantic search by question (collect_chunks_by_question); additional semantic boost (add_semantic_search_results); recommendation service (hybrid_search for related chunks).
- **Mapping**: Qdrant point_id → PostgreSQL chunk id (qdrant_point_id on knowledge_chunks).

---

## 2. Config and Environment

| Item                     | Location                | Verification                                                                       |
| ------------------------ | ----------------------- | ---------------------------------------------------------------------------------- |
| QDRANT_HOST, QDRANT_PORT | backend/config.py; .env | Config load; connect to Qdrant.                                                    |
| COLLECTION_NAME          | backend/config.py       | Value `brain_documents`.                                                           |
| EMBEDDING_MODEL          | backend/config.py       | e.g. paraphrase-multilingual-MiniLM-L12-v2; used for question and chunk embedding. |

---

## 3. Usage Patterns to Verify

1. **collect_chunks_by_question (reason.py)**

   - Question → embedding → vector search on `brain_documents` → top_k (e.g. 20) → point_ids mapped to PostgreSQL chunk ids (qdrant_point_id); only approved chunks.

2. **add_semantic_search_results (reason.py)**

   - Same collection; additional search with top_k (e.g. 5); merge with existing chunk set (dedupe).

3. **recommendation_service**
   - hybrid_search(chunk_content, top_k) for related chunks; uses same collection and embedding.

---

## 4. Verification Checklist

- [ ] Qdrant is reachable (host/port); collection `brain_documents` exists.
- [ ] Points exist (e.g. after ingest/embed); payload or metadata allows mapping to chunk id.
- [ ] search_simple(question, top_k) returns results; point_id → chunk id resolution works in reason.py.
- [ ] hybrid_search used by recommendation service returns relevant points; mapping to chunks works.
- [ ] Config (COLLECTION*NAME, EMBEDDING*\*) matches runtime; no hardcoded alternate collection in reason path.

Use this with [06-verification-backend.md](06-verification-backend.md) and [04-verification-database.md](04-verification-database.md) for full flow. See [01-verification-data-index.md](01-verification-data-index.md) for code paths.
