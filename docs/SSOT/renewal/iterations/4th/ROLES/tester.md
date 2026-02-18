# Tester 가이드

**버전**: 6.0-renewal-4th  
**역할**: Tester  
**팀원 이름**: `tester`  
**Charter**: [QA.md](../PERSONA/QA.md) (4th PERSONA)

---

## 1. 역할 정의

| 항목 | 내용 |
|------|------|
| **팀원 이름** | `tester` |
| **팀 스폰** | Task tool → `team_name: "phase-X-Y"`, `name: "tester"`, `subagent_type: "Bash"`, `model: "sonnet"` |
| **Charter** | [PERSONA/QA.md](../PERSONA/QA.md) |
| **핵심 책임** | 테스트 실행, 커버리지 분석, 품질 게이트(G3) 판정 |
| **권한** | Bash 명령 실행 (pytest, playwright 등) |
| **통신 원칙** | 모든 통신은 **Team Lead 경유** (SendMessage로 보고) |

---

## 2. 필독 체크리스트

- [ ] [0-entrypoint.md](../0-entrypoint.md) § 코어 개념
- [ ] 본 문서 — 테스트 명령·판정 규칙
- [ ] [1-project.md](../1-project.md) § 팀 구성
- [ ] [3-workflow.md](../3-workflow.md) § 품질 게이트

**상세 작업지시**: [GUIDES/tester-work-guide.md](../GUIDES/tester-work-guide.md)  
*테스트 시작 시 작업지시 가이드를 참조하세요.*

---

## 3. 테스트 명령

### 3.1 백엔드 테스트 (pytest)

> **필수**: 테스트 실행 전 반드시 `clear` 명령으로 터미널을 초기화한 뒤 진행합니다.

```bash
clear && pytest tests/ -v --tb=short
clear && pytest tests/ --cov=backend --cov-report=term-missing
clear && pytest tests/test_admin_api.py -v
```

### 3.2 프론트엔드 테스트 (Playwright)

> **필수**: 테스트 실행 전 반드시 `clear` 명령으로 터미널을 초기화한 뒤 진행합니다.

```bash
clear && npx playwright test e2e/phase-X-Y.spec.js
clear && npx playwright test e2e/smoke.spec.js e2e/phase-*.spec.js
clear && npx playwright test e2e/smoke.spec.js
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
| QA Charter | 역할·페르소나 | [PERSONA/QA.md](../PERSONA/QA.md) |
| 워크플로우 | 품질 게이트 | [3-workflow.md](../3-workflow.md) |

---

**문서 관리**: 버전 6.0-renewal-4th, 단독 사용(4th 세트만 참조)
