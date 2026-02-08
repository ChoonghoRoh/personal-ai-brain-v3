# Verification — Backend (Reasoning API)

**Purpose**: Reasoning Lab backend API and service verification.
**Source**: [01-verification-data-index.md](01-verification-data-index.md) §4, §7, §8; [reasoning-lab-feature-report.md](../reasoning-lab-feature-report.md) §4.
**Do not modify**: Original feature report or existing test files.

---

## 1. Scope

- **Main reason API**: POST `/api/reason` (request/response schema, modes, filters, errors).
- **Reasoning results CRUD**: POST/GET/DELETE `/api/reasoning-results`.
- **Recommendations**: GET `/api/reason/recommendations/chunks`, `/labels`, `/questions`, `/explore`.
- **Reasoning chain** (if used): POST `/api/reasoning-chain/build`, `/api/reasoning-chain/visualize`.
- **Pytest**: tests/test_reasoning_api.py, tests/test_reasoning_recommendations.py.

---

## 2. Endpoints and Verification

| Method | Endpoint                              | Verification                                                                                                                                                                                                                             |
| ------ | ------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| POST   | /api/reason                           | test_reason_post_returns_200_or_500; test_reason_post_empty_question; test_reason_modes. Request: mode, question, inputs (project_ids, label_ids), model. Response: answer, context_chunks, relations, reasoning_steps, recommendations. |
| POST   | /api/reasoning-results                | Create saved result; verify 201 and body.                                                                                                                                                                                                |
| GET    | /api/reasoning-results                | List results; verify 200 and array.                                                                                                                                                                                                      |
| GET    | /api/reasoning-results/{id}           | Get one; verify 200 and schema.                                                                                                                                                                                                          |
| DELETE | /api/reasoning-results/{id}           | Delete; verify 204 or 200.                                                                                                                                                                                                               |
| GET    | /api/reason/recommendations/chunks    | test*recommendations_chunks*\*; requires chunk_ids (or similar).                                                                                                                                                                         |
| GET    | /api/reason/recommendations/labels    | test_recommendations_labels.                                                                                                                                                                                                             |
| GET    | /api/reason/recommendations/questions | test_recommendations_questions.                                                                                                                                                                                                          |
| GET    | /api/reason/recommendations/explore   | test_recommendations_explore.                                                                                                                                                                                                            |

---

## 3. Request/Response Schema (Reason)

- **Request**: mode (design_explain | risk_review | next_steps | history_trace), question, inputs: { project_ids, label_ids }, filters, model.
- **Response**: answer, context_chunks, relations, reasoning_steps, recommendations: { related_chunks, sample_questions, labels, explore }.
- **Errors**: Empty question → 4xx or handled; no context → 200 with template or message; LLM failure → fallback or 5xx per implementation.

---

## 4. Pytest Tests (Do Not Modify)

- **test_reasoning_api.py**: test_reason_post_returns_200_or_500, test_reason_post_empty_question, test_reason_modes, test_recommendations_chunks_requires_chunk_ids, test_recommendations_chunks_with_ids, test_recommendations_labels, test_recommendations_questions, test_recommendations_explore.
- **test_reasoning_recommendations.py**: test_recommend_related_chunks_empty, test_recommend_labels_empty_content, test_suggest_exploration_empty, test_build_prompt, test_postprocess, test_mode_prompts_has_all_modes.

Run: `pytest tests/test_reasoning_api.py tests/test_reasoning_recommendations.py -v`.

---

## 5. Verification Checklist

- [ ] POST /api/reason with valid mode and question returns 200 (or 500 only on server/LLM failure); body has answer, context_chunks, reasoning_steps, recommendations.
- [ ] Empty question handled (4xx or message in body).
- [ ] All four modes accepted; response structure unchanged.
- [ ] Recommendation endpoints return 200 with expected shape; chunks endpoint respects chunk_ids.
- [ ] reasoning-results CRUD: create, list, get by id, delete.
- [ ] Pytest tests above pass (or document known failures).

Use with [04-verification-database.md](04-verification-database.md), [05-verification-qdrant.md](05-verification-qdrant.md), and [01-verification-data-index.md](01-verification-data-index.md).
