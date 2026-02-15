# Phase 11-5: 사용자·회귀 테스트 계획 (Phase 10 고도화)

**대상 Phase**: phase-11-5 (Phase 10 고도화)  
**목표**: Phase 10 (Reasoning Lab) 회귀 검증 및 Phase 11 연동 후 동작을 webtest/E2E 관점에서 검증합니다. §2.1~§2.5 고도화 항목이 구현된 경우 해당 시나리오도 포함합니다.

---

## 1. 범위

| 영역 | 내용 |
|------|------|
| **§2.5 회귀·E2E·Phase 11 연동** | Phase 10 E2E 범위 재실행, Admin 설정(템플릿·프리셋·RAG) 변경 시 Reasoning 동작 검증 |
| **Phase 10 회귀** | 10-1~10-4 기능(진행 상태·취소·ETA·시각화·결과물·공유·저장) 회귀 |
| **§2.1 (선택)** | Reasoning Lab 성능·안정성(대용량 시각화·스트리밍 취소·ETA) |
| **§2.2 (선택)** | 시각화 고도화(에러·폴백·반응형·모바일) |
| **§2.3 (선택)** | 결과물·접근성(PDF·WCAG·다크 모드 일관성) |
| **§2.4 (선택)** | 공유·저장 고도화(공유 URL·의사결정 문서) |

---

## 2. 참고 문서

| 문서 | 용도 |
|------|------|
| [phase-11-5-0-plan.md](../../phases/phase-11-5/phase-11-5-0-plan.md) | Phase 11-5 Task·검증 기준 |
| [phase-10-improvement-plan.md](../../phases/phase-11-5/phase-10-improvement-plan.md) | §2.1~§2.5 고도화 항목 상세 |
| [phase-10-test-scenario-guide.md](../phase-10-test-scenario-guide.md) | Phase 10 E2E·MCP 시나리오 가이드 |
| [phase-10-1-mcp-webtest-scenarios.md](../phase-10-1/phase-10-1-mcp-webtest-scenarios.md) | 10-1 시나리오 |
| [phase-10-2-mcp-webtest-scenarios.md](../phase-10-2/phase-10-2-mcp-webtest-scenarios.md) | 10-2 시나리오 |

---

## 3. 테스트 환경

- **Base URL**: http://localhost:8001
- **백엔드**: [web-user-test-setup-guide.md](../web-user-test-setup-guide.md) 참조
- **Phase 11**: Admin API·UI 기동 상태(연동 검증 시)
- **E2E**: `e2e/phase-10-1.spec.js`, `phase-10-2.spec.js` 등

---

## 4. 수행 절차

[phase-unit-user-test-guide.md](../phase-unit-user-test-guide.md)에 따릅니다.

1. 본 테스트 계획에서 범위·시나리오 확인
2. Phase 10 E2E 스펙 실행 또는 MCP/페르소나 기반 Phase 10 시나리오 수행
3. Phase 11 연동 후 Reasoning Lab 동작 검증(Admin 설정 변경 → Reasoning 요청 확인)
4. 고도화 Task(11-5-3~11-5-6) 수행 시 해당 §2.1~§2.4 시나리오 추가
5. 결과는 [phase-11-5-webtest-execution-report.md](phase-11-5-webtest-execution-report.md)에 기록

---

## 5. 결과 기록 요약

| 영역 | 총 항목 | 성공 | 실패 | 비고 |
|------|---------|------|------|------|
| Phase 10 회귀 (10-1~10-4) | | | | |
| Phase 11 연동 검증 | | | | |
| §2.1~§2.4 고도화 (선택) | | | | |
| **합계** | | | | |

**테스트 수행일**: \_\_\_\_\_\_\_\_  
**테스트 수행자**: \_\_\_\_\_\_\_\_  

---

**webtest 실행**: `[webtest: 11-5 start]` — Phase 10 E2E 실행 후 Phase 11 연동 시나리오·회귀 결과를 위 리포트에 기록.
