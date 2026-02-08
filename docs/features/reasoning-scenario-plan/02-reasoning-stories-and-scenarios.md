# Reasoning Lab — Stories and Scenarios

**Purpose**: Restate [reasoning-lab-feature-report.md](../reasoning-lab-feature-report.md) as user-facing stories and scenarios.
**Source**: Feature report §1–§2 (goals, modes), §3–§5 (architecture, backend, frontend), §6–§8 (DB, Qdrant, search/LLM/recommendations), §10 (data flow).
**Verification targets**: See [01-verification-data-index.md](01-verification-data-index.md). Linked components: DB / Qdrant / Backend / Frontend / Webtest.

---

## 1. Story: User Runs Reasoning with a Question and Mode

**Title**: User enters a question, selects a reasoning mode, and receives an answer.

**Preconditions**

- Backend and web server running at `http://localhost:8000`.
- At least one approved chunk in the knowledge base (PostgreSQL + Qdrant).
- Ollama (or configured LLM) available if full answer is required.

**Steps**

1. User opens `/reason` (Reasoning Lab).
2. User types a question in the question textarea.
3. User selects one of the four modes: design_explain, risk_review, next_steps, history_trace.
4. User optionally selects project/label filters.
5. User clicks the run (submit) button.
6. System shows progress (stages, ETA, elapsed time).
7. System returns answer, context summary, reasoning steps, and recommendations.

**Expected results**

- POST `/api/reason` is called with mode, question, and optional filters.
- Qdrant semantic search runs; PostgreSQL filter and relation expansion run; context is built; LLM generates answer; recommendations are computed.
- Frontend displays summary, conclusion, context tabs, reasoning steps, and recommendation panels.

**Verification targets**

- Backend: [06-verification-backend.md](06-verification-backend.md).
- Qdrant: [05-verification-qdrant.md](05-verification-qdrant.md).
- DB: [04-verification-database.md](04-verification-database.md).
- Frontend: [07-verification-frontend.md](07-verification-frontend.md).
- Webtest: [08-webtest-mcp-reasoning-scenarios.md](08-webtest-mcp-reasoning-scenarios.md).

---

## 2. Story: User Cancels a Running Reasoning

**Title**: User starts reasoning and then cancels.

**Preconditions**

- Same as Story 1; user has started a run.

**Steps**

1. User starts a reasoning run (question + mode + submit).
2. While progress is shown, user clicks the cancel button.
3. System sends cancel request and stops the run.
4. UI shows cancelled state; submit button is available again.

**Expected results**

- Cancel API is called (or SSE/stream aborted).
- Progress UI shows “cancelled”; submit button is re-enabled.

**Verification targets**

- Backend: cancel/abort handling.
- Frontend: cancel button visibility, state reset.
- Webtest: run/cancel scenarios.

---

## 3. Story: User Views Results and Mode-Specific Visualization

**Title**: User sees summary, conclusion, context, steps, and mode-specific viz.

**Preconditions**

- A reasoning run has completed (Story 1).

**Steps**

1. User views the results area: summary (document/chunk/relation counts), final conclusion (LLM answer).
2. User switches context tabs (e.g. chunks, documents).
3. User scrolls reasoning steps.
4. User sees mode-specific visualization: design_explain (Mermaid), risk_review (matrix), next_steps (roadmap), history_trace (timeline).

**Expected results**

- Summary, conclusion, context tabs, and reasoning steps are populated from the API response.
- Mode viz is rendered according to mode (design_explain / risk_review / next_steps / history_trace).

**Verification targets**

- Frontend: [07-verification-frontend.md](07-verification-frontend.md).
- Webtest: result and viz scenarios.

---

## 4. Story: User Uses Recommendations (Chunks, Questions, Labels, Explore)

**Title**: User sees and uses recommendation panels.

**Preconditions**

- A reasoning run has completed; recommendations are returned.

**Steps**

1. User sees related chunks, sample questions, suggested labels, and explore suggestions.
2. User clicks a sample question → question field is filled (or run is triggered).
3. User uses related chunks or explore links if implemented.

**Expected results**

- Recommendation panels show data from `recommendations` in the reason response.
- Sample question click updates question and/or triggers a new run.

**Verification targets**

- Backend: [06-verification-backend.md](06-verification-backend.md) (recommendation endpoints).
- Frontend: recommendation section and click handlers.
- Webtest: recommendation scenarios.

---

## 5. Story: User Saves or Retrieves a Reasoning Result

**Title**: User saves a result and later retrieves it.

**Preconditions**

- Reasoning result save/load is available (POST/GET reasoning-results).

**Steps**

1. After a run, user saves the result (if UI exposes it).
2. User opens “saved results” or list view.
3. User selects a saved result and views it.

**Expected results**

- POST `/api/reasoning-results` stores the result; GET `/api/reasoning-results` and GET `/api/reasoning-results/{id}` return data.
- UI shows list and detail when implemented.

**Verification targets**

- Backend: [06-verification-backend.md](06-verification-backend.md).
- DB: [04-verification-database.md](04-verification-database.md) (reasoning_results table).

---

## 6. Scenario: Design Explain Mode End-to-End

**Title**: Full flow for design_explain mode.

**Preconditions**

- Knowledge base has chunks; Ollama (or LLM) is up.

**Steps**

1. Open `/reason`.
2. Enter question: e.g. “시스템 아키텍처는?”
3. Select mode: design_explain.
4. Submit.
5. Wait for completion.
6. Check: answer is present; context chunks and relations are shown; reasoning steps list stages; design_explain viz (e.g. Mermaid) is rendered.

**Expected results**

- Backend uses design_explain prompt; response includes answer, context_chunks, relations, reasoning_steps, recommendations.
- Frontend shows conclusion and design_explain visualization.

**Verification targets**

- All: DB, Qdrant, Backend, Frontend, Webtest.

---

## 7. Scenario: Risk Review Mode End-to-End

**Title**: Full flow for risk_review mode.

**Preconditions**

- Same as Scenario 6.

**Steps**

1. Open `/reason`.
2. Enter question (e.g. risk-related).
3. Select mode: risk_review.
4. Submit and wait.
5. Check: answer; risk_review viz (e.g. 5x5 matrix) is rendered.

**Expected results**

- risk_review prompt and matrix visualization.

**Verification targets**

- Backend (mode handling), Frontend (risk_review viz), Webtest.

---

## 8. Scenario: Next Steps Mode End-to-End

**Title**: Full flow for next_steps mode.

**Preconditions**

- Same as Scenario 6.

**Steps**

1. Open `/reason`.
2. Enter question (e.g. next steps).
3. Select mode: next_steps.
4. Submit and wait.
5. Check: answer; next_steps viz (e.g. roadmap/timeline) is rendered.

**Expected results**

- next_steps prompt and roadmap/timeline visualization.

**Verification targets**

- Backend, Frontend, Webtest.

---

## 9. Scenario: History Trace Mode End-to-End

**Title**: Full flow for history_trace mode.

**Preconditions**

- Same as Scenario 6.

**Steps**

1. Open `/reason`.
2. Enter question (e.g. change history).
3. Select mode: history_trace.
4. Submit and wait.
5. Check: answer; history_trace viz (e.g. timeline) is rendered.

**Expected results**

- history_trace prompt and timeline visualization.

**Verification targets**

- Backend, Frontend, Webtest.

---

## 10. Scenario: Filter by Project and Label

**Title**: User applies project and label filters.

**Preconditions**

- Projects and labels exist; chunks are linked to them.

**Steps**

1. Open `/reason`.
2. Load options (projects/labels) if not auto-loaded.
3. Select one or more projects and/or labels.
4. Enter question and submit.
5. Check: only chunks matching filters (and relations) are used; answer reflects filtered context.

**Expected results**

- Request includes project_ids and/or label_ids; backend filters chunks accordingly (PostgreSQL); context is limited to filtered set.

**Verification targets**

- DB: [04-verification-database.md](04-verification-database.md). Backend: [06-verification-backend.md](06-verification-backend.md).

---

## 11. Scenario: Empty or No Context

**Title**: Question has no or insufficient context.

**Preconditions**

- No approved chunks, or question unrelated to any chunk.

**Steps**

1. Open `/reason`.
2. Enter a question that does not match any chunk (or use empty DB).
3. Submit.
4. Check: backend returns gracefully (e.g. “no context” or template answer); frontend shows message without crash.

**Expected results**

- No 500; optional template or “관련 지식이 없습니다” style message.

**Verification targets**

- Backend: [06-verification-backend.md](06-verification-backend.md). Frontend: [07-verification-frontend.md](07-verification-frontend.md).

---

## 12. Scenario: URL Parameter (Seed Chunk)

**Title**: User opens /reason with a seed chunk (e.g. chunk_id) in URL.

**Preconditions**

- Frontend supports URL params for seed chunk; backend or UI uses it.

**Steps**

1. Open `/reason?chunk_id=123` (or equivalent param).
2. Check: question or context is pre-filled or biased by chunk 123 if supported.

**Expected results**

- loadSeedChunk (or equivalent) runs; UI reflects seed chunk when implemented.

**Verification targets**

- Frontend: [07-verification-frontend.md](07-verification-frontend.md). Webtest: entry/navigation.

---

## Summary Table: Stories/Scenarios and Verification

| #   | Story / scenario                                                           | DB  | Qdrant | Backend | Frontend | Webtest  |
| --- | -------------------------------------------------------------------------- | --- | ------ | ------- | -------- | -------- |
| 1   | Run reasoning (question + mode)                                            | ✓   | ✓      | ✓       | ✓        | ✓        |
| 2   | Cancel run                                                                 | -   | -      | ✓       | ✓        | ✓        |
| 3   | View results and mode viz                                                  | -   | -      | -       | ✓        | ✓        |
| 4   | Use recommendations                                                        | -   | ✓      | ✓       | ✓        | ✓        |
| 5   | Save/retrieve result                                                       | ✓   | -      | ✓       | ✓        | Optional |
| 6–9 | Mode-specific E2E (design_explain, risk_review, next_steps, history_trace) | ✓   | ✓      | ✓       | ✓        | ✓        |
| 10  | Filter by project/label                                                    | ✓   | -      | ✓       | ✓        | ✓        |
| 11  | Empty/no context                                                           | -   | ✓      | ✓       | ✓        | ✓        |
| 12  | URL seed chunk                                                             | -   | -      | -       | ✓        | ✓        |

Use this document together with [01-verification-data-index.md](01-verification-data-index.md) and verification docs 04–07 and 08 for test design and execution.
