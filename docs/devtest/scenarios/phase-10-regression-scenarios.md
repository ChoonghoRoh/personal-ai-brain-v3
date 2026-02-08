# Phase 10 Reasoning Lab 회귀 시나리오 (devtest·webtest 연계)

**대상**: Phase 10-1~10-4 (Reasoning Lab)  
**목적**: Phase 10 E2E 회귀·Phase 11 연동 검증 시나리오를 devtest·webtest와 공유합니다.  
**상세**: [phase-11-5/regression-e2e-phase11-scenarios.md](../../phases/phase-11-5/regression-e2e-phase11-scenarios.md)

---

## 1. Phase 10 E2E 회귀 실행

| Phase | E2E 스펙 | 실행 명령 | 시나리오 수 |
|-------|-----------|-----------|-------------|
| 10-1 | `e2e/phase-10-1.spec.js` | `python3 scripts/webtest.py 10-1 start` | 6 |
| 10-2 | `e2e/phase-10-2.spec.js` | `python3 scripts/webtest.py 10-2 start` | 6 |
| 10-3 | `e2e/phase-10-3.spec.js` | `npx playwright test e2e/phase-10-3.spec.js` | 7 |
| 10-4 | `e2e/phase-10-4.spec.js` | `npx playwright test e2e/phase-10-4.spec.js` | 10 |
| **전체** | `e2e/phase-10-*.spec.js` | `npx playwright test e2e/phase-10-1.spec.js e2e/phase-10-2.spec.js e2e/phase-10-3.spec.js e2e/phase-10-4.spec.js` | **29** |

---

## 2. 추가 권장 시나리오 (향후 보강)

- **에러 경로**: LLM/API 오류 시 에러 메시지, 빈 질의·유효성 검사
- **취소**: 스트리밍 중 취소 후 UI 초기화·재실행
- **공유 만료**: 만료된 공유 URL 접근 시 안내

---

## 3. Phase 11 연동 검증

- Admin 설정(템플릿·프리셋·RAG) 변경 후 Reasoning 요청 정상 동작 확인.
- 시나리오 상세: [regression-e2e-phase11-scenarios.md](../../phases/phase-11-5/regression-e2e-phase11-scenarios.md) §2.

---

## 4. webtest 결과

- **Phase 11-5 webtest 실행 리포트**: [docs/webtest/phase-11-5/phase-11-5-webtest-execution-report.md](../../webtest/phase-11-5/phase-11-5-webtest-execution-report.md)
- **User Test Plan**: [docs/webtest/phase-11-5/phase-11-5-user-test-plan.md](../../webtest/phase-11-5/phase-11-5-user-test-plan.md)
