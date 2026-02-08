# Verification — Database (PostgreSQL)

**Purpose**: Reasoning Lab–related PostgreSQL verification.
**Source**: [01-verification-data-index.md](01-verification-data-index.md) §2, [reasoning-lab-feature-report.md](../reasoning-lab-feature-report.md) §6.
**Do not modify**: Original feature report.

---

## 1. Scope

- **reasoning_results**: CRUD for saved reasoning results.
- **knowledge_chunks**: Approved chunks; filter by project/label; qdrant_point_id mapping.
- **knowledge_relations**: Chunk-to-chunk relations; 2-depth expansion.
- **knowledge_labels** (chunk–label linkage): Filter chunks by label; confirmed status.

---

## 2. Tables and Verification Targets

| Table / concept         | Purpose                                                                                                     | Verification method                                                                                                                                  |
| ----------------------- | ----------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| **reasoning_results**   | Store question, answer, reasoning_steps, context_chunks, relations, mode, session_id, meta_data, created_at | POST/GET/DELETE `/api/reasoning-results`; manual SQL: `SELECT * FROM reasoning_results LIMIT 1`.                                                     |
| **knowledge_chunks**    | Chunk content, title, status (approved/pending), qdrant_point_id, document_id                               | Filter by status=approved in reason.py; pytest or SQL: `SELECT id, status, qdrant_point_id FROM knowledge_chunks WHERE status = 'approved' LIMIT 5`. |
| **knowledge_relations** | source_chunk_id, target_chunk_id, relation_type, confirmed                                                  | expand_chunks_with_relations in reason.py; SQL: `SELECT * FROM knowledge_relations WHERE confirmed = 'true' LIMIT 5`.                                |
| **Chunk–label linkage** | knowledge_labels (or equivalent); chunk_id, label_id, status                                                | Filter by label_ids in reason.py; join with chunks.                                                                                                  |

---

## 3. Schema / Model Location

- **Models**: `backend/models/models.py` (ReasoningResult, KnowledgeChunk, KnowledgeRelation, and label-related models).
- **Migrations / seed**: `scripts/db/` (e.g. migrate*phase11_1*_.sql, seed*phase11_1*_.sql). Run migrations and seed; then verify tables exist and have expected columns.

---

## 4. Query Patterns to Verify

1. **Approved chunks only**: `KnowledgeChunk.status == "approved"`.
2. **Filter by project_ids**: Join with Document; `Document.project_id.in_(project_ids)`.
3. **Filter by label_ids**: Join with chunk–label table; `label_id.in_(label_ids)`, status confirmed.
4. **Relation expansion (2-depth)**: Iterate from initial chunk IDs; query KnowledgeRelation where source_chunk_id in current set, confirmed=true; add target_chunk_id to next set; repeat up to MULTIHOP_MAX_DEPTH.

---

## 5. Verification Checklist

- [ ] reasoning_results table exists; INSERT/SELECT/DELETE work (via API or SQL).
- [ ] knowledge_chunks has status, qdrant_point_id, document_id; approved filter used in reason flow.
- [ ] knowledge_relations has source_chunk_id, target_chunk_id, confirmed; relation expansion returns related chunks.
- [ ] Chunk–label linkage supports label filter; reason request with label_ids returns only chunks with those labels (and confirmed status where applicable).
- [ ] Migrations and seed scripts run without errors; DB state consistent with backend expectations.

Use this with [06-verification-backend.md](06-verification-backend.md) for API-level checks and [01-verification-data-index.md](01-verification-data-index.md) for paths.
