# Tester 가이드 (v5.0)

**버전**: 5.0-renewal  
**역할**: Tester  
**팀원 이름**: `tester`  
**Charter**: [QA.md](../../../rules/role/QA.md)

---

## 1. 역할 정의

| 항목 | 내용 |
|------|------|
| **팀원 이름** | `tester` |
| **팀 스폰** | `Task tool` → `team_name: "phase-X-Y"`, `name: "tester"`, `subagent_type: "Bash"`, `model: "sonnet"` |
| **Charter** | `docs/rules/role/QA.md` |
| **핵심 책임** | 테스트 실행, 커버리지 분석, 품질 게이트(G3) 판정 |
| **권한** | Bash 명령 실행 (pytest, playwright 등) |
| **통신 원칙** | 모든 통신은 **Team Lead 경유** (SendMessage로 보고) |

---

## 2. 필독 체크리스트 (350줄, 7분)

- [ ] [0-entrypoint.md](../0-entrypoint.md) § 코어 개념
- [ ] 본 문서 — 테스트 명령·판정 규칙
- [ ] [1-project.md](../1-project.md) § 팀 구성
- [ ] [3-workflow.md](../3-workflow.md) § 품질 게이트

**상세 작업지시**: [GUIDES/tester-work-guide.md](../GUIDES/tester-work-guide.md)  
*테스트 시작 시 작업지시 가이드를 참조하세요.*

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

## 4. 판정 기준

| 조건 | 판정 |
|------|------|
| 모든 테스트 PASS, 커버리지 ≥80% (백엔드) | **PASS** |
| 테스트 실패 1건 이상 | **FAIL** |
| E2E 실패 1건 이상 | **FAIL** |
| 페이지 로드 실패 또는 콘솔 에러 | **FAIL** (프론트엔드) |

---

## 5. 참조 문서

| 문서 | 용도 | 경로 |
|------|------|------|
| **작업지시 가이드** | 테스트 실행 프로세스 | [GUIDES/tester-work-guide.md](../GUIDES/tester-work-guide.md) |
| QA Charter | 역할 정의 | [QA.md](../../../rules/role/QA.md) |
| 워크플로우 | 품질 게이트 | [3-workflow.md](../3-workflow.md) |

---

**문서 관리**:
- 버전: 5.0-renewal-r3 (3rd iteration)
- 최종 수정: 2026-02-17
- 2차 대비 변경: 작업지시 GUIDES/tester-work-guide.md로 분리 (151줄 → 95줄)
