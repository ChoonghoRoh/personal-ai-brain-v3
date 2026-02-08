# docs/devtest — 통합 테스트

Phase 11 통합 테스트의 **가이드·시나리오·실행 결과 리포트**를 관리하는 디렉토리입니다.

---

## 목적

- Phase 11-1(DB), 11-2(API), 11-3(Admin UI) 구간에 대한 **통합 테스트** 수행 방법과 산출물을 한곳에서 관리합니다.
- **Task당 최대 20가지** 통합 테스트 시나리오를 작성하고, **Task당 실행 결과**(코드 오류·미해결/해결)를 리포트로 남깁니다.

---

## 디렉토리 구조(예시)

```
docs/devtest/
├── README.md                    # 본 문서
├── integration-test-guide.md    # 통합 테스트 가이드(상세)
├── report-format.md             # 실행 결과 리포트 형식·규정(선택)
├── phase-11-1-scenarios.md      # Phase 11-1 시나리오(또는 task별 파일)
├── phase-11-2-scenarios.md      # Phase 11-2 시나리오
├── phase-11-3-scenarios.md      # Phase 11-3 시나리오
└── reports/                     # Task별 실행 결과 리포트
    ├── phase11-4-2-task-11-1-1-execution-report.md
    ├── phase11-4-2-task-11-1-2-execution-report.md
    └── ...
```

---

## 통합 테스트 가이드

상세 절차·환경·시나리오 작성 규칙·리포트 규정은 다음 문서를 참조합니다.

- **[integration-test-guide.md](integration-test-guide.md)** — 통합 테스트 가이드
- **[report-format.md](report-format.md)** — 실행 결과 리포트 형식

---

## Phase 11 Task별 시나리오·리포트

| Phase | Task | 시나리오 수(상한) | 실행 결과 리포트 |
|-------|------|-------------------|------------------|
| 11-1 | 11-1-1, 11-1-2, 11-1-3 | 각 최대 20가지 | Task당 1건 |
| 11-2 | 11-2-1 ~ 11-2-5 | 각 최대 20가지 | Task당 1건 |
| 11-3 | 11-3-1 ~ 11-3-4 | 각 최대 20가지 | Task당 1건 |

---

## Phase 10 회귀·Phase 11 연동 (11-5-7)

Phase 10 (Reasoning Lab) E2E 회귀 및 Phase 11 Admin 연동 검증 시나리오는 다음 문서를 참조합니다.

- **[scenarios/phase-10-regression-scenarios.md](scenarios/phase-10-regression-scenarios.md)** — Phase 10 회귀 시나리오 요약(webtest 연계)
- **[integration-test-guide.md](integration-test-guide.md)** §7 — Phase 10 회귀·Phase 11 연동 참조
- **[phase-11-5/regression-e2e-phase11-scenarios.md](../phases/phase-11-5/regression-e2e-phase11-scenarios.md)** — 상세 시나리오·검증 범위

---

## 관련 문서

| 문서 | 용도 |
|------|------|
| [phase-11-4-0-plan.md](../phases/phase-11-4/phase-11-4-0-plan.md) | Phase 11-4 통합 테스트 Plan |
| [phase-11-4-0-todo-list.md](../phases/phase-11-4/phase-11-4-0-todo-list.md) | Phase 11-4 Todo List |
| [phase-11-master-plan.md](../phases/phase-11-master-plan.md) | Phase 11 전체 계획 |
