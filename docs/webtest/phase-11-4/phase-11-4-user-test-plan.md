# Phase 11-4: 사용자·통합 테스트 계획

**대상 Phase**: phase-11-4 (통합 테스트·운영 준비)  
**목표**: Phase 11-1~11-3 구축 범위(DB·Admin API·Admin UI)의 통합 테스트 시나리오를 수행하고, 회귀·운영 관점 검증을 기록합니다.

---

## 1. 범위

다음 영역을 대상으로 합니다.

| 영역 | 내용 |
|------|------|
| **11-1** | DB 스키마·마이그레이션·시딩·테이블 관계 |
| **11-2** | Admin CRUD API (schemas, templates, presets, rag-profiles, policy-sets, 버전·Publish/Rollback·Audit·resolve) |
| **11-3** | Admin UI (Templates, Presets, RAG Profiles, Policy Sets, Audit Logs) |
| **통합** | Draft→Publish→Rollback 시나리오, API↔UI 연동, 회귀 |

---

## 2. 참고 문서

| 문서 | 용도 |
|------|------|
| [phase-11-4-0-plan.md](../../phases/phase-11-4/phase-11-4-0-plan.md) | Phase 11-4 Task·시나리오 수·리포트 규정 |
| [integration-test-guide.md](../../devtest/integration-test-guide.md) | 통합 테스트 가이드·환경·리포트 규칙 |
| [phase-11-1-mcp-webtest-scenarios.md](../phase-11-1/phase-11-1-mcp-webtest-scenarios.md) | 11-1 시나리오 참고 |
| [phase-11-2-webtest-execution-report.md](../phase-11-2/phase-11-2-webtest-execution-report.md) | 11-2 API 검증 결과 |
| [phase-11-3-webtest-execution-report.md](../phase-11-3/phase-11-3-webtest-execution-report.md) | 11-3 UI 검증 결과 |

---

## 3. 테스트 환경

- **Base URL**: http://localhost:8000
- **백엔드**: [web-user-test-setup-guide.md](../web-user-test-setup-guide.md) 참조
- **DB**: PostgreSQL (마이그레이션·시딩 완료 상태)
- **선택**: curl, MCP 브라우저, E2E(Playwright) 조합

---

## 4. 수행 절차

[phase-unit-user-test-guide.md](../phase-unit-user-test-guide.md)에 따릅니다.

1. 본 테스트 계획에서 범위·시나리오 확인
2. [docs/devtest](../../devtest/) 시나리오 문서(Phase 11-1·11-2·11-3) 기준으로 통합 테스트 실행
3. Draft→Publish→Rollback·Admin UI 연동 등 통합 시나리오 수행
4. 결과는 [phase-11-4-webtest-execution-report.md](phase-11-4-webtest-execution-report.md)에 기록

---

## 5. 결과 기록 요약

| 영역 | 총 항목 | 성공 | 실패 | 비고 |
|------|---------|------|------|------|
| 11-1 (DB) | | | | |
| 11-2 (API) | | | | |
| 11-3 (UI) | | | | |
| 통합 시나리오 | | | | |
| **합계** | | | | |

**테스트 수행일**: \_\_\_\_\_\_\_\_  
**테스트 수행자**: \_\_\_\_\_\_\_\_  

---

**webtest 실행**: `[webtest: 11-4 start]` — E2E 스펙 없을 경우 대체 테스트(curl·HTTP 확인·MCP)로 수행 후 위 리포트에 기록.
