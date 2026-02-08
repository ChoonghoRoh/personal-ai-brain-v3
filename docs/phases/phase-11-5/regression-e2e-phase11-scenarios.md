# Phase 10 E2E 회귀·Phase 11 연동 검증 시나리오

**Task ID**: 11-5-7  
**기준**: [phase-10-improvement-plan.md](phase-10-improvement-plan.md) §2.5  
**작성일**: 2026-02-07  
**목적**: Phase 10 E2E 범위 확장·회귀 시나리오 문서화, Phase 11 Admin 설정 변경 시 Reasoning 동작 검증 범위 정의.

---

## 1. Phase 10 E2E 회귀 범위

### 1.1 현재 E2E 스펙 (회귀 대상)

| Phase | E2E 스펙 | 시나리오 수 | 비고 |
|-------|-----------|-------------|------|
| 10-1 | `e2e/phase-10-1.spec.js` | 6 | 진행 상태·취소·ETA |
| 10-2 | `e2e/phase-10-2.spec.js` | 6 | 모드별 시각화 |
| 10-3 | `e2e/phase-10-3.spec.js` | 7 | 공통 결과·PDF·인사이트 |
| 10-4 | `e2e/phase-10-4.spec.js` | 10 | 스트리밍·공유·저장·회귀 |
| **합계** | | **29** | 회귀 시 실행 대상 |

### 1.2 추가 권장 시나리오 (향후 E2E 보강)

| ID | 시나리오 | 우선순위 | 비고 |
|----|----------|----------|------|
| W10.ERR.1 | **에러 경로**: LLM/API 오류 시 에러 메시지 표시 | 상 | Phase 10-1·10-4 연계 |
| W10.ERR.2 | **에러 경로**: 빈 질의·잘못된 입력 시 유효성 검사 | 중 | |
| W10.CANCEL.1 | **취소**: 스트리밍 중 취소 후 UI 초기화·재실행 가능 | 상 | phase-10-4 W10.4.2 확장 |
| W10.SHARE.1 | **공유 만료**: 만료된 공유 URL 접근 시 만료 안내 | 중 | §2.4 공유 URL 고도화 시 |
| W10.REGR.1 | **회귀**: Admin 설정(템플릿·프리셋·RAG) 변경 후 Reasoning 요청 정상 동작 | 상 | §1.3 Phase 11 연동 검증과 동일 |

---

## 2. Phase 11 연동 후 회귀 검증 범위

### 2.1 검증 목표

Admin 설정(템플릿·프리셋·RAG 프로필·정책) 변경 시 **Reasoning Lab**이 해당 설정을 반영하여 정상 동작하는지 검증한다.

### 2.2 검증 시나리오

| ID | 시나리오 | 전제 조건 | 단계 | 기대 결과 |
|----|----------|-----------|------|-----------|
| P11.REG.1 | Admin에서 템플릿 수정 후 Reasoning 요청 | Admin UI·API 기동, Phase 10 Reasoning 페이지 접근 가능 | 1) Admin에서 템플릿 일부 수정·저장<br>2) Reasoning Lab에서 동일 템플릿으로 질의 | 수정된 템플릿 내용이 Reasoning 요청에 반영됨 |
| P11.REG.2 | Admin에서 프리셋 수정 후 Reasoning 요청 | 동일 | 1) Admin에서 프리셋 수정·저장<br>2) Reasoning Lab에서 해당 프리셋 선택 후 질의 | 수정된 프리셋이 적용됨 |
| P11.REG.3 | Admin에서 RAG 프로필 수정 후 Reasoning 요청 | 동일 | 1) Admin에서 RAG 프로필 수정·저장<br>2) Reasoning Lab에서 RAG 설정 적용 후 질의 | RAG 설정이 반영됨 |
| P11.REG.4 | Phase 10 E2E 전체 회귀(10-1~10-4) | Admin·Backend·Phase 10 UI 기동 | `webtest: 10-1 start` ~ 10-4 E2E 실행 | 29개 시나리오 통과 |

### 2.3 검증 방법

- **수동**: Admin UI에서 설정 변경 → Reasoning Lab 브라우저에서 요청 후 결과 확인.
- **자동(부분)**: Phase 10 E2E(`npx playwright test e2e/phase-10-*.spec.js`) 실행 후, Admin API·UI HTTP/목록 확인(`curl`, HTTP 200).
- **webtest 연계**: [docs/webtest/phase-11-5/phase-11-5-user-test-plan.md](../../webtest/phase-11-5/phase-11-5-user-test-plan.md), [phase-11-5-webtest-execution-report.md](../../webtest/phase-11-5/phase-11-5-webtest-execution-report.md).

---

## 3. devtest·webtest 연계

| 구분 | 문서·위치 | 용도 |
|------|-----------|------|
| **devtest** | [docs/devtest/integration-test-guide.md](../../devtest/integration-test-guide.md) | Phase 11 통합 테스트 가이드; Phase 10 회귀·Phase 11 연동 참조 추가 |
| **devtest 시나리오** | [docs/devtest/scenarios/phase-10-regression-scenarios.md](../../devtest/scenarios/phase-10-regression-scenarios.md) | Phase 10 회귀 시나리오 요약(webtest와 공유) |
| **webtest** | [docs/webtest/phase-11-5/](../../webtest/phase-11-5/) | Phase 11-5 user-test-plan, webtest-execution-report |
| **실행** | `python3 scripts/webtest.py 10-1 start` … 10-4, `webtest: 11-5 start` | Phase 10 E2E 실행, Phase 11-5 회귀·연동 검증 |

---

## 4. 산출물·체크리스트

- [x] **Phase 10 E2E 범위**: 회귀 시나리오 문서화(§1), 추가 권장 시나리오(에러·취소·공유 만료) 정리(§1.2)
- [x] **Phase 11 연동 후 회귀**: Admin 설정 변경 시 Reasoning 검증 시나리오·검증 범위 정의(§2)
- [x] **devtest·webtest 연계**: 본 문서 및 devtest/webtest 경로 명시(§3)
- [x] **산출물**: `phase-11-5/regression-e2e-phase11-scenarios.md`, `docs/devtest/scenarios/phase-10-regression-scenarios.md`, integration-test-guide 보완
