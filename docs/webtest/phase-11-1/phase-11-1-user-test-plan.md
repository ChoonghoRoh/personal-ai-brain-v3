# Phase 11-1: DB 스키마·마이그레이션 — 웹테스트·검증 계획

**대상 Phase**: Phase 11-1 (DB 스키마·마이그레이션)  
**목표**: Phase 11-1 범위(7종 Admin 테이블 마이그레이션·시딩)의 **검증**을 수행합니다.  
**특이사항**: 11-1은 **웹 UI가 없음**. 검증은 마이그레이션·시딩 실행, 테이블 존재 확인, 및 **Phase 11-2 Admin API** 연동(목록 200)으로 수행합니다.

---

## 1. 범위

| Task | 대상 | 검증 방법 |
|------|------|------------|
| 11-1-1 | schemas, templates, prompt_presets 테이블 | 마이그레이션·시딩 실행 → 테이블 존재·행 수 확인 → Admin API GET 목록 200 |
| 11-1-2 | rag_profiles, context_rules, policy_sets 테이블 | 동일 |
| 11-1-3 | audit_logs 테이블, 관계 검증 | 동일 |

---

## 2. 참고 문서

| 문서 | 용도 |
|------|------|
| [phase-11-1-0-plan.md](../../phases/phase-11-1/phase-11-1-0-plan.md) | Phase 11-1 계획·검증 체크리스트 |
| [phase-11-1-0-todo-list.md](../../phases/phase-11-1/phase-11-1-0-todo-list.md) | Task 목록 |
| [phase-11-1-11-2-development-verification.md](../../phases/phase-11-2/phase-11-1-11-2-development-verification.md) | 11-1·11-2 개발 검증 보고서 |
| [phase-10-test-scenario-guide.md](../phase-10-test-scenario-guide.md) | E2E + MCP 시나리오 가이드(참고) |

---

## 3. 테스트 환경

- **Base URL**: http://localhost:8000 (Admin API·웹 서버)
- **DB**: PostgreSQL (마이그레이션·시딩 실행 환경)
- **전제**: Phase 11-2 Admin API 배포 후, GET /api/admin/schemas 등으로 11-1 테이블 연동 검증 가능

---

## 4. 수행 절차

1. **마이그레이션·시딩**  
   `scripts/db/migrate_phase11_1_1.sql` → `migrate_phase11_1_2.sql` → `migrate_phase11_1_3.sql`  
   필요 시 `seed_phase11_1_1.sql` ~ `seed_phase11_1_3.sql` 실행.
2. **시나리오 문서**  
   [phase-11-1-mcp-webtest-scenarios.md](phase-11-1-mcp-webtest-scenarios.md) 기준으로 Task 11-1-1·11-1-2·11-1-3 검증 시나리오 수행.
3. **결과 기록**  
   [phase-11-1-mcp-webtest-result.md](phase-11-1-mcp-webtest-result.md) 시나리오별 통과/실패 기록.

**E2E**: Phase 11-1은 웹 UI가 없어 `scripts/webtest.py 11-1 start` 시 E2E 스펙 없음 안내가 나옵니다. 방안 A(MCP)·방안 B(페르소나) 또는 본 검증 시나리오(API/DB)로 수행합니다.

---

## 5. 결과 기록 요약

| Task | 시나리오 수 | 성공 | 비고 |
|------|-------------|------|------|
| 11-1-1 | 10 | ?/10 | |
| 11-1-2 | 10 | ?/10 | |
| 11-1-3 | 10 | ?/10 | |
| **합계** | **30** | ?/30 | |

**테스트 수행일**: \_\_\_\_\_\_\_\_  
**테스트 수행자**: \_\_\_\_\_\_\_\_
