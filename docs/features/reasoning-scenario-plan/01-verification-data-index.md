# Verification Data Index — Reasoning Lab

**Purpose**: Map source documents ([reasoning-lab-feature-report.md](../reasoning-lab-feature-report.md), [reason-lab-refactoring-design.md](../reason-lab-refactoring-design.md)) to project paths for verification and testable data.
**Do not modify**: Original feature report and refactoring design.

---

## 1. Source Document Section → Project Path Mapping

| Feature report § | Topic                             | Project path / verification target                                                                                                                                                                                          |
| ---------------- | --------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| §1               | Implementation goals              | Conceptual; no direct path.                                                                                                                                                                                                 |
| §2               | 4 reasoning modes                 | `backend/services/reasoning/dynamic_reasoning_service.py` (MODE_PROMPTS); `web/public/js/reason/reason-model.js` (mode descriptions).                                                                                       |
| §3               | System architecture               | `backend/routers/reasoning/reason.py`; `web/src/pages/reason.html`; `backend/services/search/`, `backend/models/`.                                                                                                          |
| §4.1–4.2         | Backend router, API endpoints     | `backend/routers/reasoning/reason.py`, `reasoning_chain.py`, `reasoning_results.py`, `recommendations.py`; `reason_stream.py`, `reason_store.py`.                                                                           |
| §4.3–4.4         | Request/response schema, services | `backend/routers/reasoning/reason.py` (Pydantic); `backend/services/reasoning/dynamic_reasoning_service.py`, `recommendation_service.py`.                                                                                   |
| §5               | Frontend                          | `web/src/pages/reason.html`, `web/public/js/reason/reason.js`, `reason-model.js`, `reason-common.js`, `reason-control.js`, `reason-render.js`, `reason-viz-loader.js`, `reason-pdf-export.js`; `web/public/css/reason.css`. |
| §6               | Database (PostgreSQL)             | `backend/models/models.py` (ReasoningResult, KnowledgeChunk, KnowledgeRelation, etc.); `scripts/db/` (migrations, seed if any).                                                                                             |
| §7               | Qdrant                            | `backend/config.py` (QDRANT\_\*, COLLECTION_NAME); `backend/services/search/search_service.py`, `hybrid_search.py`; collection `brain_documents`.                                                                           |
| §8               | Search flow, LLM, recommendations | `backend/routers/reasoning/reason.py` (collect_chunks_by_question, expand_chunks_with_relations, etc.); `backend/services/reasoning/recommendation_service.py`.                                                             |
| §9               | Config / env                      | `backend/config.py`; `.env`, `.env.example`.                                                                                                                                                                                |
| §10              | Data flow                         | End-to-end: reason.py → search_service → models → dynamic_reasoning_service → recommendation_service.                                                                                                                       |
| §11              | File locations                    | See tables below.                                                                                                                                                                                                           |

---

## 2. DB — Verification / Testable Data

| Item                    | Path / identifier                                                           | Verification method                                              |
| ----------------------- | --------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| **reasoning_results**   | `backend/models/models.py` (ReasoningResult); DB table `reasoning_results`  | CRUD via `/api/reasoning-results`; pytest or manual SQL.         |
| **knowledge_chunks**    | `backend/models/models.py` (KnowledgeChunk); table `knowledge_chunks`       | Filter by status=approved, project_id, label; used in reason.py. |
| **knowledge_relations** | `backend/models/models.py` (KnowledgeRelation); table `knowledge_relations` | expand_chunks_with_relations in reason.py; 2-depth.              |
| **knowledge_labels**    | `backend/models/models.py`; chunk–label linkage                             | Filter chunks by label_ids; recommendation_service.              |
| **Migrations / seed**   | `scripts/db/` (e.g. migrate*phase11_1*_.sql, seed*phase11_1*_.sql)          | Run migrations; run seed; query tables.                          |

---

## 3. Qdrant — Verification / Testable Data

| Item                 | Path / identifier                                                            | Verification method                                                        |
| -------------------- | ---------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| **Collection**       | `brain_documents` (COLLECTION_NAME in config)                                | List collections; check points.                                            |
| **Config**           | `backend/config.py`: QDRANT*HOST, QDRANT_PORT, COLLECTION_NAME, EMBEDDING*\* | Env and config load.                                                       |
| **search_simple**    | `backend/services/search/search_service.py` (or equivalent)                  | Used by reason.py collect_chunks_by_question, add_semantic_search_results. |
| **hybrid_search**    | `backend/services/search/hybrid_search.py`                                   | Used by recommendation_service; tests in test_hybrid_search.py if present. |
| **point_id ↔ chunk** | reason.py: Qdrant results → PostgreSQL chunk by qdrant_point_id              | Trace from search result to KnowledgeChunk.                                |

---

## 4. Backend — Verification / Testable Data

| Item                       | Path                                                            | Verification method                                                                                                                                                                                                        |
| -------------------------- | --------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **POST /api/reason**       | `backend/routers/reasoning/reason.py`                           | `tests/test_reasoning_api.py`: test_reason_post_returns_200_or_500, test_reason_post_empty_question, test_reason_modes.                                                                                                    |
| **Recommendations**        | `backend/routers/reasoning/recommendations.py`                  | `tests/test_reasoning_api.py`: test*recommendations_chunks*\*, test_recommendations_labels, test_recommendations_questions, test_recommendations_explore.                                                                  |
| **Recommendation service** | `backend/services/reasoning/recommendation_service.py`          | `tests/test_reasoning_recommendations.py`: test_recommend_related_chunks_empty, test_recommend_labels_empty_content, test_suggest_exploration_empty, test_build_prompt, test_postprocess, test_mode_prompts_has_all_modes. |
| **Reasoning results CRUD** | `backend/routers/reasoning/reasoning_results.py`                | POST/GET/DELETE `/api/reasoning-results`; pytest or HTTP client.                                                                                                                                                           |
| **Reasoning chain**        | `backend/routers/reasoning/reasoning_chain.py`                  | POST `/api/reasoning-chain/build`, `/api/reasoning-chain/visualize`.                                                                                                                                                       |
| **Streaming / store**      | `backend/routers/reasoning/reason_stream.py`, `reason_store.py` | If exposed: SSE and store endpoints.                                                                                                                                                                                       |

**Test files (do not modify)**

- [tests/test_reasoning_api.py](../../../tests/test_reasoning_api.py)
- [tests/test_reasoning_recommendations.py](../../../tests/test_reasoning_recommendations.py)

---

## 5. Frontend — Verification / Testable Data

| Item           | Path                                        | Verification method                                                                                                        |
| -------------- | ------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| **Page**       | `web/src/pages/reason.html`                 | DOM: form, #question, mode select, filters, #progress-stages, #results-content, #reasoning-steps, recommendation sections. |
| **Styles**     | `web/public/css/reason.css`                 | Visual and layout checks.                                                                                                  |
| **Entry**      | `web/public/js/reason/reason.js`            | DOMContentLoaded, event bindings.                                                                                          |
| **Model**      | `web/public/js/reason/reason-model.js`      | Mode descriptions, state shape.                                                                                            |
| **Common**     | `web/public/js/reason/reason-common.js`     | loadReasoningOptions, loadSeedChunk.                                                                                       |
| **Control**    | `web/public/js/reason/reason-control.js`    | runReasoning, cancel, progress, ETA.                                                                                       |
| **Render**     | `web/public/js/reason/reason-render.js`     | Summary, conclusion, context tabs, steps, mode viz.                                                                        |
| **Viz loader** | `web/public/js/reason/reason-viz-loader.js` | Design/risk/next_steps/history_trace viz.                                                                                  |
| **PDF export** | `web/public/js/reason/reason-pdf-export.js` | PDF export flow.                                                                                                           |

**Refactoring design (do not modify)**

- [reason-lab-refactoring-design.md](../reason-lab-refactoring-design.md) — file split and layer roles.

---

## 6. E2E / Webtest — Verification / Testable Data

| Item                  | Path                                                                                       | Verification method                                                  |
| --------------------- | ------------------------------------------------------------------------------------------ | -------------------------------------------------------------------- |
| **E2E specs**         | `e2e/phase-10-1.spec.js`, `phase-10-2.spec.js`, `phase-10-3.spec.js`, `phase-10-4.spec.js` | Playwright: /reason navigation, DOM, run, cancel, ETA, results, viz. |
| **E2E MCP scenarios** | `e2e/phase-10-1-mcp-scenarios.spec.js`                                                     | MCP-aligned Playwright scenarios for /reason.                        |
| **Webtest scenarios** | `docs/webtest/phase-10-1/phase-10-1-mcp-webtest-scenarios.md`                              | Human/MCP checklist: progress, cancel, ETA (10 per task).            |
| **MCP test guide**    | `docs/webtest/mcp-cursor-test-guide.md`                                                    | How to run MCP Cursor browser tests.                                 |
| **Base URL**          | `http://localhost:8000`                                                                    | Backend and web server must be up.                                   |

---

## 7. API Endpoints Summary (for verification)

| Method | Endpoint                                | Source               |
| ------ | --------------------------------------- | -------------------- |
| POST   | `/api/reason`                           | reason.py            |
| POST   | `/api/reasoning-chain/build`            | reasoning_chain.py   |
| POST   | `/api/reasoning-chain/visualize`        | reasoning_chain.py   |
| POST   | `/api/reasoning-results`                | reasoning_results.py |
| GET    | `/api/reasoning-results`                | reasoning_results.py |
| GET    | `/api/reasoning-results/{id}`           | reasoning_results.py |
| DELETE | `/api/reasoning-results/{id}`           | reasoning_results.py |
| GET    | `/api/reason/recommendations/chunks`    | recommendations.py   |
| GET    | `/api/reason/recommendations/labels`    | recommendations.py   |
| GET    | `/api/reason/recommendations/questions` | recommendations.py   |
| GET    | `/api/reason/recommendations/explore`   | recommendations.py   |

---

## 8. Pytest Test Cases (reasoning)

| File                              | Test function                                                        | Covers                                     |
| --------------------------------- | -------------------------------------------------------------------- | ------------------------------------------ |
| test_reasoning_api.py             | test_reason_post_returns_200_or_500                                  | POST /api/reason success or server error   |
| test_reasoning_api.py             | test_reason_post_empty_question                                      | Empty question handling                    |
| test_reasoning_api.py             | test_reason_modes                                                    | Mode parameter (design_explain, etc.)      |
| test_reasoning_api.py             | test_recommendations_chunks_requires_chunk_ids                       | Chunks recommendation params               |
| test_reasoning_api.py             | test_recommendations_chunks_with_ids                                 | Chunks recommendation with IDs             |
| test_reasoning_api.py             | test_recommendations_labels                                          | Labels recommendation                      |
| test_reasoning_api.py             | test_recommendations_questions                                       | Sample questions                           |
| test_reasoning_api.py             | test_recommendations_explore                                         | Explore recommendation                     |
| test_reasoning_recommendations.py | test_recommend_related_chunks_empty                                  | Recommendation service, empty input        |
| test_reasoning_recommendations.py | test_recommend_labels_empty_content                                  | Labels, empty content                      |
| test_reasoning_recommendations.py | test_suggest_exploration_empty                                       | Explore, empty                             |
| test_reasoning_recommendations.py | test_build_prompt, test_postprocess, test_mode_prompts_has_all_modes | Recommendation service internals and modes |

This index is the reference for [02-reasoning-stories-and-scenarios.md](02-reasoning-stories-and-scenarios.md) and for verification documents 04–07.
