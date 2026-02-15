# Reasoning Scenario Master Plan

**Purpose**: Reasoning Lab feature verification, story/scenario organization, and webtest MCP scenarios.
**Source documents**: [reasoning-lab-feature-report.md](../reasoning-lab-feature-report.md), [reason-lab-refactoring-design.md](../reason-lab-refactoring-design.md)
**Constraints**: Do not modify existing source files. Use [references/](references/) for copies when needed.
**Location**: `docs/features/reasoning-scenario-plan/` (file names in English).

---

## 1. Goals and Constraints

| Item                      | Description                                                                                              |
| ------------------------- | -------------------------------------------------------------------------------------------------------- |
| **No edits to originals** | reasoning-lab-feature-report.md, reason-lab-refactoring-design.md, and other source files are read-only. |
| **references folder**     | When citing originals, store copies under `references/` with a distinct name (e.g. `-ref.md`) if needed. |
| **Output location**       | All new artifacts under `docs/features/reasoning-scenario-plan/`.                                        |

---

## 2. Step Overview and Dependencies

| Step       | Document                                                                         | Purpose                                                                           | Depends on        |
| ---------- | -------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- | ----------------- |
| **Step 1** | [01-verification-data-index.md](01-verification-data-index.md)                   | Map source docs and project folders to verification/testable data and code paths. | -                 |
| **Step 2** | [02-reasoning-stories-and-scenarios.md](02-reasoning-stories-and-scenarios.md)   | Restate feature report as user-facing stories and scenarios.                      | Step 1 (optional) |
| **Step 3** | [03-scenario-document-creation-guide.md](03-scenario-document-creation-guide.md) | Guide: copy originals and create separate scenario documents.                     | -                 |
| **Step 4** | [04–07 verification docs](04-verification-database.md)                           | DB, Qdrant, Backend, Frontend verification items.                                 | Step 1, Step 2    |
| **Step 5** | [08-webtest-mcp-reasoning-scenarios.md](08-webtest-mcp-reasoning-scenarios.md)   | MCP Cursor webtest scenarios for /reason (10+ per category).                      | Step 2            |

**Execution order**: 00 (this plan) → 01 → 02 → 03 → [references] → 04 → 05 → 06 → 07 → 08 → README.

---

## 3. Step 1 — Verification Data Index

- **Output**: [01-verification-data-index.md](01-verification-data-index.md)
- **Content**: Table mapping source document sections and tables to project paths (DB, Qdrant, Backend, Frontend, E2E/webtest). Include test files, seeding scripts, API endpoints, DOM IDs.

---

## 4. Step 2 — Reasoning Stories and Scenarios

- **Output**: [02-reasoning-stories-and-scenarios.md](02-reasoning-stories-and-scenarios.md)
- **Content**: Stories/scenarios derived from the feature report (e.g. “User enters question and selects design_explain mode…”). Each with: title, preconditions, steps, expected results, and linked verification target (DB/Qdrant/Backend/Frontend/Webtest).

---

## 5. Step 3 — Scenario Document Creation Guide

- **Output**: [03-scenario-document-creation-guide.md](03-scenario-document-creation-guide.md)
- **Content**: (1) How to use the references folder, (2) Copy procedure and file-naming rules, (3) Procedure for creating new scenario documents, (4) Scenario document template (ID, title, preconditions, steps, expected result, verification method, related component).

---

## 6. Step 4 — DB / Qdrant / Backend / Frontend Verification

- **Outputs**:
  - [04-verification-database.md](04-verification-database.md) — PostgreSQL: reasoning_results, knowledge_chunks/relations/labels; schema, seeding, verification method.
  - [05-verification-qdrant.md](05-verification-qdrant.md) — Collection brain_documents, search_simple/hybrid_search, point_id ↔ chunk mapping.
  - [06-verification-backend.md](06-verification-backend.md) — /api/reason, /api/reasoning-results, /api/reason/recommendations/\*; tests/test_reasoning_api.py, test_reasoning_recommendations.py.
  - [07-verification-frontend.md](07-verification-frontend.md) — reason.html sections/element IDs, reason.js (or reason-\*.js) init, events, render; DOM and mode-switch checks.

---

## 7. Step 5 — Webtest MCP Scenarios

- **Output**: [08-webtest-mcp-reasoning-scenarios.md](08-webtest-mcp-reasoning-scenarios.md)
- **Content**: User-executable MCP Cursor browser scenarios for Reasoning Lab (/reason). At least **10 scenarios per category**, 6 categories (entry/navigation, question/mode, run/progress/cancel, results, recommendations, save/share/errors). Format: scenario # | title | action | expected result | verification method. Base URL: `http://localhost:8001`.

---

## 8. Index

- **Output**: [README.md](README.md)
- **Content**: Folder purpose, full file list (filename | purpose | dependencies), recommended read/implementation order, references folder description.

---

## 9. References

| Source                    | Path (do not edit)                                                                                                                                               |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Feature report            | [docs/features/reasoning-lab-feature-report.md](../reasoning-lab-feature-report.md)                                                                              |
| Refactoring design        | [docs/features/reason-lab-refactoring-design.md](../reason-lab-refactoring-design.md)                                                                            |
| Webbtest scenario example | [docs/webtest/phase-10-1/phase-10-1-mcp-webtest-scenarios.md](../../webtest/phase-10-1/phase-10-1-mcp-webtest-scenarios.md)                                      |
| MCP test guide            | [docs/webtest/mcp-cursor-test-guide.md](../../webtest/mcp-cursor-test-guide.md)                                                                                  |
| Reasoning API tests       | [tests/test_reasoning_api.py](../../../tests/test_reasoning_api.py), [tests/test_reasoning_recommendations.py](../../../tests/test_reasoning_recommendations.py) |
| E2E /reason               | [e2e/phase-10-1.spec.js](../../../e2e/phase-10-1.spec.js), [e2e/phase-10-1-mcp-scenarios.spec.js](../../../e2e/phase-10-1-mcp-scenarios.spec.js)                 |
