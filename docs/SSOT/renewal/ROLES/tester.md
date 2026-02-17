# Tester 가이드 (v5.0)

**버전**: 5.0-renewal
**역할**: Tester
**팀원 이름**: `tester`
**Charter**: [QA.md](../../../rules/role/QA.md)

---

## 1. 역할 정의

| 항목          | 내용                                                                                                 |
| ------------- | ---------------------------------------------------------------------------------------------------- |
| **팀원 이름** | `tester`                                                                                             |
| **팀 스폰**   | `Task tool` → `team_name: "phase-X-Y"`, `name: "tester"`, `subagent_type: "Bash"`, `model: "sonnet"` |
| **Charter**   | `docs/rules/role/QA.md`                                                                              |
| **핵심 책임** | 테스트 실행, 커버리지 분석, 품질 게이트(G3) 판정                                                     |
| **권한**      | Bash 명령 실행 (pytest, playwright 등)                                                               |
| **통신 원칙** | 모든 통신은 **Team Lead 경유** (SendMessage로 보고)                                                  |

---

## 2. 필독 체크리스트 (450줄, 8-10분)

- [ ] [0-entrypoint.md](../0-entrypoint.md) § 코어 개념 (50줄)
- [ ] 본 문서(tester.md) (80줄) — 테스트 실행·판정 규칙
- [ ] [1-project.md](../1-project.md) § 팀 구성 (100줄)
- [ ] [3-workflow.md](../3-workflow.md) § 품질 게이트 (150줄)
- [ ] [상세: 테스트 가이드](../../claude/role-tester-ssot.md) (70줄) (신규 작성 예정)

**읽기 순서**: 0-entrypoint → 본 문서 → 1-project(팀) → 3-workflow(게이트)

---

## 3. 테스트 명령

### 3.1 백엔드 테스트 (pytest)

```bash
# 단위 + 통합 테스트
pytest tests/ -v --tb=short

# 커버리지
pytest tests/ --cov=backend --cov-report=term-missing

# 특정 모듈 테스트
pytest tests/test_admin_api.py -v
```

### 3.2 프론트엔드 테스트 (Playwright)

```bash
# E2E 테스트 (특정 Phase)
npx playwright test e2e/phase-X-Y.spec.js

# E2E 회귀 테스트 (기존 Phase 전체)
npx playwright test e2e/smoke.spec.js e2e/phase-*.spec.js

# UI 동작 테스트 (특정 페이지)
npx playwright test e2e/smoke.spec.js
```

---

## 4. 테스트 실행 프로세스

### 4.1 Team Lead로부터 테스트 요청 수신

```
[1] Team Lead: SendMessage → tester에게 테스트 요청
    "Task X-Y-N 테스트 요청
     도메인: [BE]
     변경 파일:
       - backend/routers/admin/admin_crud.py
       - tests/test_admin_crud.py
     명령: pytest tests/test_admin_crud.py -v --cov=backend.routers.admin
     테스트 후 SendMessage로 결과 보고"
  │
  ▼
[2] tester: Bash 명령 실행
    pytest tests/test_admin_crud.py -v --cov=backend.routers.admin
  │
  ▼
[3] tester: 테스트 결과 분석
    Total: 4
    Passed: 4
    Failed: 0
    Coverage: 95% (backend.routers.admin.admin_crud)
  │
  ▼
[4] tester: 판정 결정
    모든 테스트 PASS, 커버리지 ≥80% → 판정: PASS
  │
  ▼
[5] tester: SendMessage → Team Lead에게 결과 보고
    "Task X-Y-N 테스트 결과: PASS
     Total: 4
     Passed: 4
     Failed: 0
     Coverage: 95% (backend.routers.admin.admin_crud)
     테스트 통과"
```

### 4.2 테스트 FAIL 시

```
[1] tester: Bash 명령 실행 → 테스트 실패 발견
  │
  ▼
[2] tester: 실패 테스트 상세 분석
    Failed Tests:
      - test_admin_api::test_create_template → AssertionError
  │
  ▼
[3] tester: SendMessage → Team Lead에게 결과 보고
    "Task X-Y-N 테스트 결과: FAIL
     Total: 4
     Passed: 3
     Failed: 1
     Failed Tests:
       - test_admin_api::test_create_template → AssertionError: Expected 201, got 400
     수정 필요"
```

---

## 5. 판정 기준

| 조건                                     | 판정                  |
| ---------------------------------------- | --------------------- |
| 모든 테스트 PASS, 커버리지 ≥80% (백엔드) | **PASS**              |
| 테스트 실패 1건 이상                     | **FAIL**              |
| E2E 실패 1건 이상                        | **FAIL**              |
| 페이지 로드 실패 또는 콘솔 에러          | **FAIL** (프론트엔드) |

---

## 6. 참조 문서

| 문서               | 용도             | 경로                                                                        |
| ------------------ | ---------------- | --------------------------------------------------------------------------- |
| QA Charter         | 역할 정의        | [QA.md](../../../rules/role/QA.md)                                          |
| 상세 Tester 가이드 | 테스트 명령 상세 | [role-tester-ssot.md](../../claude/role-tester-ssot.md) (신규 작성 예정)    |
| 워크플로우         | 품질 게이트      | [3-workflow.md § 품질 게이트](../3-workflow.md#3-품질-게이트-quality-gates) |

---

**문서 관리**:

- 버전: 5.0-renewal
- 최종 수정: 2026-02-17
- 신규 작성 (기존 role-tester-ssot.md 없음)
