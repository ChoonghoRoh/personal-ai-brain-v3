# Orchestration Loop Stabilization Rules (Extracted)

## SECTION 1 — SSOT DEFINITION

### Project SSOT

- overview

- architecture

- requirements

### Rules SSOT

- `docs/rules/rules-index.md`
- `docs/rules/ai-execution-workflow.md`

SSOT usage priority: `Status 파일 > ai-execution-workflow.md > System Prompts > Templates > AI rules > Guide 문서`를 우선 적용한다.

## SECTION 2 — FAILURE HANDLING

- Failure reporting:
  - 검증 실패는 `verification-report`의 `최종 판정(PASS|FAIL|PARTIAL)`, `코드 오류(Section 5)`, `미해결 이슈(Section 6)`로 보고.
  - 통합 테스트 실패/부분 실패는 실행 결과 리포트의 `코드 오류`, `미해결 이슈`, `시나리오 결과 요약`으로 보고.
  - 실패 원인은 `phase-X-Y-status.md`의 `blockers` 배열에 기록.
- Failure report storage:
  - `docs/phases/phase-X-Y/phase-X-Y-verification-report.md`
  - `docs/devtest/reports/phase-{X-Y}-task-{X-Y-Z}-execution-report.md` (또는 `docs/phases/phase-{X-Y}/`)
  - `docs/phases/phase-X-Y/phase-X-Y-status.md` (`blockers`)
- Responsible for fixing:
  - **Tester**: 실패 검출/문서화 및 Pass/Fail 판정.
  - **Orchestrator**: 롤백 결정, blockers 반영, `task-X-Y-Z-fix.md` 생성 지시.
  - **Builder**: Fix Task 구현 및 재검증 대상 수정.

## SECTION 3 — ROLLBACK POINTS

Failure → rollback state mapping

- Backend failure (API/Logic/DB 검증 FAIL) → `3. Task 생성 및 개발 단계 (Fix)`로 롤백, `task-X-Y-Z-fix.md` 생성, 이후 `4. 검증 단계` 재진입
- Frontend failure (UI 동작 검증 FAIL) → `3. Task 생성 및 개발 단계 (Fix)`로 롤백, `task-X-Y-Z-fix.md` 생성, 이후 `4. 검증 단계` 재진입
- Integration failure:
  - `All Pass` 아님 + `Critical/High Blocker` 존재 → `3. Task 생성 및 개발 단계` 롤백
  - `Partial Pass` + `Low/Medium`만 존재 → Technical Debt 등록 후 다음 단계 진행

## SECTION 4 — RETRY LIMITS

- Retry attempts / re-execution limits:
  - Each task may be retried up to 3 times.
  - After 3 failures, orchestration must stop.
  - 실패 시 `Fix Task` 생성 후 실패했던 단계부터 재실행.
- Escalation rules:
  - `3x Fail` → `STOP & Human Help` / 수동 개입 요청.

## SECTION 5 — TASK COMPLETION FLOW

### Task lifecycle states:

- READY
- IN_DEV
- VERIFYING
- FIXING
- VERIFIED
- COMPLETED
- BLOCKED

```text
[Init]
  -> Load rules-index
  -> Load phase-X-Y-status
  -> Step 1 Plan
  -> Step 2 Dev (Builder)
  -> Step 3 Verify (Tester, template 필수)
      Gate A: 최종 판정
        - PASS -> todo [x] -> (남은 todo 있으면 Step 2, 없으면 Step 4)
        - FAIL -> blockers 기록 -> Fix Task 생성 -> Step 2(Fix) -> Step 3 재검증
        - PARTIAL -> 이슈 등급 평가
            - Low/Medium만 -> Technical Debt 등록 -> Step 4
            - Critical/High 포함 -> FAIL 처리 -> Step 2(Fix)
  -> Step 4 Integration Test
      Gate B: 통합 테스트 결과
        - All Pass -> Step 5
        - Partial/Fail + Critical/High -> Step 2(Fix)
        - Partial + Low/Medium -> 기록 후 Step 5
  -> Step 5 E2E & Web Test
  -> Step 6 Complete (phase-X-Y-final-summary.md, status=Completed)
```
