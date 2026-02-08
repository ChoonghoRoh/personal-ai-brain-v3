# AI Exec Workflow (Lite)

**Rule**: Load `docs/rules/rules-index.md` first.
**State**: Track via `docs/phases/phase-X-Y/phase-X-Y-status.md`.

---

## 0. Init

1. **Load Status**: If missing, create (`phase: X-Y`, `step: 1`).
2. **Set Role**: Orchestrator (Default).
3. **Goto**: `Current Step` in Status.

---

## 1. Workflow Loop

### Step 1: Plan

**Trigger**: New Phase / Start
**Action**:

1. Analyze Req -> Write `phase-X-Y-plan.md`.
2. Break down tasks -> Write `phase-X-Y-todo-list.md`.
3. **Update Status**: `step: 2 (Dev)`, `next: Task-1`.

### Step 2: Dev (Builder)

**Trigger**: `todo-list` has `[ ]`
**Action**:

1. Pick top `[ ]` task.
2. **Read**: `rules-index.md` (Code Conv).
3. **Coding**: Implement logic. (No side effects).
4. **Self-Check**: Syntax scan.
5. **Update Status**: `step: 3 (Verify)`, `target: [TaskID]`.

### Step 3: Verify (Tester)

**Trigger**: Code changed
**Action**:

1. Load `templates/verification-report-template.md`.
2. Check: Syntax, Logic, Conv.
3. **Decision**:
   - **[PASS]**: Mark `todo` as `[x]`. Goto **Step 2** (Next Task) or **Step 4** (All Done).
   - **[FAIL]**: Log error. Goto **Step 2** (Fix Mode).
     - _Constraint_: If 3x Fail -> **STOP** (Human Help).

### Step 4: Integration

**Trigger**: All `todo` `[x]`
**Action**:

1. Write scenarios -> `docs/devtest/scenarios/`.
2. Run Test -> Write `docs/devtest/reports/`.
3. If Error -> Goto **Step 2** (Fix). Else -> **Step 5**.

### Step 5: E2E & Web

**Trigger**: Integration Pass
**Action**:

1. Check/Create `e2e/phase-X-Y.spec.js`.
2. Run Web Test -> Capture results.
3. If Pass -> **Step 6**.

### Step 6: Complete

**Action**:

1. Write `phase-X-Y-final-summary.md`.
2. **Update Status**: `step: Completed`.

---

## 2. Exception Handling

- **Loop (3x Fail)**: STOP & Alert User.
- **Missing File**: STOP & Report "File Not Found: [Path]".

---

## 3. Path Ref

- Status: `docs/phases/phase-X-Y/phase-X-Y-status.md`
- Reports: `docs/phases/phase-X-Y/reports/`
- Prompts: `docs/rules/prompts/`
