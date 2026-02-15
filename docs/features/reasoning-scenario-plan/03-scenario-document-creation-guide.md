# Scenario Document Creation Guide

**Purpose**: Define how to copy originals and create separate scenario documents without modifying existing source files.
**Location**: New scenario documents live under `docs/features/reasoning-scenario-plan/` (or subfolders). File names in English.

---

## 1. References Folder Rules

### 1.1 Role of `references/`

- **Use**: When you need a local copy of an original document for reference while writing new scenario or verification docs.
- **Do not edit originals**: [reasoning-lab-feature-report.md](../reasoning-lab-feature-report.md) and [reason-lab-refactoring-design.md](../reason-lab-refactoring-design.md) must not be modified.
- **Copies**: Store copies under `docs/features/reasoning-scenario-plan/references/` with a distinct name so it is clear they are reference copies.

### 1.2 Naming Convention for Copies

| Original                           | Reference copy name (in `references/`) |
| ---------------------------------- | -------------------------------------- |
| reasoning-lab-feature-report.md    | reasoning-lab-feature-report-ref.md    |
| reason-lab-refactoring-design.md   | reason-lab-refactoring-design-ref.md   |
| Other docs (e.g. webtest scenario) | `<short-name>-ref.md`                  |

### 1.3 When to Use a Copy vs. Link

- **Link only**: Prefer linking to the original path (e.g. `../reasoning-lab-feature-report.md`) when you only need to point readers to the source.
- **Copy**: Create a copy in `references/` when the guide or procedure explicitly says “copy the original” or when you need a stable snapshot for procedure steps (e.g. “open references/reasoning-lab-feature-report-ref.md and extract §4”).

---

## 2. Copy Procedure (Original → Reference)

### 2.1 Steps

1. **Confirm original path**

   - e.g. `docs/features/reasoning-lab-feature-report.md`, `docs/features/reason-lab-refactoring-design.md`.

2. **Choose copy name**

   - Use the naming convention above (e.g. `reasoning-lab-feature-report-ref.md`).

3. **Copy file**

   - Copy the file byte-for-byte (or content-only) into `docs/features/reasoning-scenario-plan/references/<chosen-name>`.
   - Do not change the original file.

4. **Optional: add header to copy**
   - If desired, add a one-line header at the top of the copy:
     `**Reference copy — do not edit; original:** [path to original].`
   - This is optional; the important rule is: do not edit the original.

### 2.2 What Not to Do

- Do not edit the original feature report or refactoring design.
- Do not use the references folder for the “canonical” version of the feature report; the canonical version remains in `docs/features/`.

---

## 3. Creating a New Scenario Document

### 3.1 When to Create a New Document

- When adding a **new scenario** (e.g. a new user story or test scenario) that does not belong in an existing file (e.g. 02-reasoning-stories-and-scenarios.md or 08-webtest-mcp-reasoning-scenarios.md).
- When splitting 08 into sub-documents (e.g. 08a-entry-navigation.md, 08b-run-cancel.md) and you need a new file per category.

### 3.2 Steps

1. **Decide location**

   - Directly under `reasoning-scenario-plan/` (e.g. `09-my-scenarios.md`) or in a subfolder (e.g. `webtest/09a-entry.md`).
   - Use English file names.

2. **Use the scenario template**

   - For each scenario, include the fields in §4 below.

3. **Reference source material**

   - In the new document, link to the original (or to the reference copy) when citing content, e.g.:
     “See [reasoning-lab-feature-report.md](../reasoning-lab-feature-report.md) §4.2 for API endpoints.”

4. **Do not modify originals**

   - All new content goes only into the new file (and optionally references/ copies). No edits to reasoning-lab-feature-report.md or reason-lab-refactoring-design.md.

5. **Update index**
   - Add the new file to [README.md](README.md) (file list and optional “recommended order”).

---

## 4. Scenario Document Template (Per Scenario)

Use this structure for each scenario you add to a scenario document (e.g. 02 or 08 or a new file).

### 4.1 Required Fields

| Field                   | Description                                                                                                                                 |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| **Scenario ID**         | Unique id (e.g. S01, REASON-ENTRY-01, or task-based like 08-ENTRY-01).                                                                      |
| **Title**               | One-line summary of the scenario.                                                                                                           |
| **Preconditions**       | Environment, data, and UI state required before steps (e.g. backend up, /reason open, options loaded).                                      |
| **Steps**               | Numbered list of user or system actions (e.g. 1. Open /reason. 2. Enter question. 3. Select mode. 4. Click submit).                         |
| **Expected result**     | What should be observed after the steps (e.g. “Answer and context are shown”, “Progress stages update”).                                    |
| **Verification method** | How to verify (e.g. “Check DOM for #results-content”, “Call GET /api/reasoning-results", “Run pytest test_reason_post_returns_200_or_500”). |
| **Related component**   | One or more of: DB / Qdrant / Backend / Frontend / Webtest. Link to 04–07 or 08 if useful.                                                  |

### 4.2 Optional Fields

- **Priority** (e.g. high/medium/low).
- **Dependencies** (e.g. “Requires Scenario S02”).
- **Notes** (e.g. known limitations, browser-specific behavior).

### 4.3 Example (Table Form)

| #   | Scenario title     | Action                            | Expected result                          | Verification method                      |
| --- | ------------------ | --------------------------------- | ---------------------------------------- | ---------------------------------------- |
| 1   | /reason page loads | Open http://localhost:8001/reason | Page loads; question and mode UI visible | Snapshot has #question and mode selector |

### 4.4 Example (Structured Form)

**Scenario ID**: REASON-ENTRY-01
**Title**: Reasoning Lab page loads.
**Preconditions**: Backend and web server running at http://localhost:8001.
**Steps**:

1. Navigate to http://localhost:8001/reason.
2. Wait for page load.
   **Expected result**: Page shows question input and mode selector; no fatal errors.
   **Verification method**: DOM snapshot contains #question and mode dropdown/buttons.
   **Related component**: Frontend; Webtest.

---

## 5. Checklist Before Publishing a New Scenario Doc

- [ ] File is under `reasoning-scenario-plan/` (or subfolder); name is in English.
- [ ] No edits were made to reasoning-lab-feature-report.md or reason-lab-refactoring-design.md.
- [ ] Any copy used is in `references/` with a distinct name (e.g. `-ref.md`).
- [ ] Each scenario has at least: ID, title, preconditions, steps, expected result, verification method, related component.
- [ ] README.md (index) is updated with the new file and purpose.

This guide is the single place for “copy original → reference” and “create new scenario document” procedures. Use it together with [00-reasoning-scenario-master-plan.md](00-reasoning-scenario-master-plan.md) and [01-verification-data-index.md](01-verification-data-index.md).
