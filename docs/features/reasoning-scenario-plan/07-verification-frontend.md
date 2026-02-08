# Verification — Frontend (Reasoning Lab /reason)

**Purpose**: Reasoning Lab frontend verification (reason.html and reason JS).
**Source**: [01-verification-data-index.md](01-verification-data-index.md) §5; [reasoning-lab-feature-report.md](../reasoning-lab-feature-report.md) §5; [reason-lab-refactoring-design.md](../reason-lab-refactoring-design.md).
**Do not modify**: Original feature report or refactoring design.

---

## 1. Scope

- **Page**: `web/src/pages/reason.html` — structure, sections, element IDs.
- **Scripts**: `web/public/js/reason/reason.js` (entry), reason-model.js, reason-common.js, reason-control.js, reason-render.js, reason-viz-loader.js, reason-pdf-export.js.
- **Styles**: `web/public/css/reason.css`.
- **Verification**: DOM presence, init, events, render (summary, conclusion, context, steps, mode viz, recommendations), mode switch, cancel, ETA.

---

## 2. UI Sections and Elements (Representative)

| Section             | Purpose                                                | Representative IDs / selectors                                                                                          |
| ------------------- | ------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------- |
| **Form**            | Question, mode, model                                  | #question, mode selector (name or id), model selector                                                                   |
| **Filters**         | Project/label                                          | Project dropdown, label dropdown (multi-select)                                                                         |
| **Progress**        | Stages, ETA, elapsed                                   | #progress-stages, .progress-stage, #progress-bar, #progress-message, #reasoning-elapsed-text, #eta-display or #eta-text |
| **Cancel**          | Cancel run                                             | #cancel-btn                                                                                                             |
| **Submit**          | Run reasoning                                          | #submit-btn or similar                                                                                                  |
| **Loading**         | During run                                             | #results-loading                                                                                                        |
| **Results**         | Summary, conclusion, context, steps                    | #results-content, summary block, conclusion block, context tabs, #reasoning-steps                                       |
| **Mode viz**        | design_explain, risk_review, next_steps, history_trace | Container for Mermaid, matrix, roadmap, timeline                                                                        |
| **Recommendations** | Chunks, questions, labels, explore                     | Recommendation panels/sections                                                                                          |

Exact IDs may differ; use DOM snapshot or devtools to confirm.

---

## 3. Script Roles (Refactoring Design)

- **reason.js**: DOMContentLoaded, mode description binding, cancel and submit bindings, init.
- **reason-model.js**: MODE_DESCRIPTIONS, state/shape.
- **reason-common.js**: loadReasoningOptions, loadSeedChunk, URL params.
- **reason-control.js**: runReasoning, cancelReasoning, progress, ETA, clearResults, init/restore UI.
- **reason-render.js**: renderSummary, renderConclusion, context tabs, renderSteps, renderModeViz, displayRecommendations.
- **reason-viz-loader.js**: Mode-specific viz (design_explain, risk_review, next_steps, history_trace).
- **reason-pdf-export.js**: PDF export if present.

---

## 4. Verification Checklist

- [ ] /reason loads; no fatal JS errors; #question and mode selector present.
- [ ] Options (projects/labels) load (reason-common); filters visible.
- [ ] Submit runs POST /api/reason; progress/ETA/cancel appear (reason-control).
- [ ] Cancel button visible during run; cancel stops run; submit re-enabled (reason-control).
- [ ] Results: summary, conclusion, context tabs, reasoning steps populated (reason-render).
- [ ] Mode-specific viz renders for design_explain, risk_review, next_steps, history_trace (reason-render, reason-viz-loader).
- [ ] Recommendations section shows related chunks, sample questions, labels, explore; sample question click fills question or runs (if implemented).
- [ ] URL param (e.g. chunk_id) triggers loadSeedChunk when supported.
- [ ] Script load order: utils → model → common → render → control → reason.js (per refactoring design).

Use with [08-webtest-mcp-reasoning-scenarios.md](08-webtest-mcp-reasoning-scenarios.md) for browser-level checks and [01-verification-data-index.md](01-verification-data-index.md) for paths.
