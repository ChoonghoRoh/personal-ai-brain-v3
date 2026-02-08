# Phase 11-1 MCP(Cursor) 웹테스트·검증 시나리오 — Task당 10개

**대상**: Phase 11-1 DB 스키마·마이그레이션  
**기준**: [phase-11-1-0-todo-list.md](../../phases/phase-11-1/phase-11-1-0-todo-list.md), Task 11-1-1~11-1-3  
**전제**: PostgreSQL 기동, 필요 시 Phase 11-2 Admin API 기동 (GET /api/admin/* 로 테이블 연동 검증)  
**환경**: http://localhost:8000 (Admin API 검증 시)

**참고**: 11-1은 웹 UI가 없어, 검증은 **마이그레이션·시딩 실행**, **테이블 존재 확인**, **Admin API(11-2) 목록 200** 으로 수행합니다.

---

## 공통 준비

- PostgreSQL 컨테이너 기동 (`pab-postgres`)
- 마이그레이션 순서: migrate_phase11_1_1.sql → migrate_phase11_1_2.sql → migrate_phase11_1_3.sql
- 시딩(선택): seed_phase11_1_1.sql ~ seed_phase11_1_3.sql
- Admin API 검증 시: 백엔드 기동 후 GET /api/admin/schemas 등 호출

---

## Task 11-1-1: schemas, templates, prompt_presets — 시나리오 10개

| # | 시나리오 | 조치 | 기대 결과 | 검증 방법 |
|---|----------|------|-----------|-----------|
| **1** | 마이그레이션 11_1_1 실행 | `docker exec -i pab-postgres psql -U brain -d knowledge < scripts/db/migrate_phase11_1_1.sql` | COMMIT 완료, 에러 없음 | exit code 0 |
| **2** | schemas 테이블 존재 | `SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='schemas'` | 1행 반환 | 쿼리 결과 행 수 |
| **3** | templates 테이블 존재 | 동일, table_name='templates' | 1행 반환 | 쿼리 결과 |
| **4** | prompt_presets 테이블 존재 | 동일, table_name='prompt_presets' | 1행 반환 | 쿼리 결과 |
| **5** | 시딩 11_1_1 실행 | `docker exec -i pab-postgres psql -U brain -d knowledge < scripts/db/seed_phase11_1_1.sql` | 에러 없음 | exit code 0 |
| **6** | schemas 행 수 확인 | `SELECT COUNT(*) FROM schemas` | 0 이상 | count ≥ 0 |
| **7** | Admin API schemas 목록 | GET http://localhost:8000/api/admin/schemas?limit=5 | 200, body에 items·total | status 200, JSON items/total |
| **8** | Admin API templates 목록 | GET /api/admin/templates?limit=5 | 200, items·total | 동일 |
| **9** | Admin API presets 목록 | GET /api/admin/presets?limit=5 | 200, items·total | 동일 |
| **10** | 인덱스 존재 | `SELECT indexname FROM pg_indexes WHERE tablename IN ('templates','prompt_presets')` | idx_templates_*, idx_prompt_presets_* 존재 | index 목록 |

---

## Task 11-1-2: rag_profiles, context_rules, policy_sets — 시나리오 10개

| # | 시나리오 | 조치 | 기대 결과 | 검증 방법 |
|---|----------|------|-----------|-----------|
| **1** | 마이그레이션 11_1_2 실행 | `docker exec -i pab-postgres psql -U brain -d knowledge < scripts/db/migrate_phase11_1_2.sql` | COMMIT 완료 | exit code 0 |
| **2** | rag_profiles 테이블 존재 | information_schema.tables WHERE table_name='rag_profiles' | 1행 | 쿼리 결과 |
| **3** | context_rules 테이블 존재 | table_name='context_rules' | 1행 | 쿼리 결과 |
| **4** | policy_sets 테이블 존재 | table_name='policy_sets' | 1행 | 쿼리 결과 |
| **5** | 시딩 11_1_2 실행 | seed_phase11_1_2.sql 실행 | 에러 없음 | exit code 0 |
| **6** | policy_sets FK(templates) | INSERT 또는 조회 시 FK 오류 없음 | 정상 | FK 제약 |
| **7** | Admin API rag-profiles 목록 | GET /api/admin/rag-profiles?limit=5 | 200, items·total | status 200 |
| **8** | Admin API policy-sets 목록 | GET /api/admin/policy-sets?limit=5 | 200, items·total | 동일 |
| **9** | idx_policy_sets_* 존재 | pg_indexes WHERE tablename='policy_sets' | 2개 이상 | index 목록 |
| **10** | 기존 projects 테이블 무변경 | SELECT column_name FROM information_schema.columns WHERE table_name='projects' | 기존 컬럼만 | 스키마 변경 없음 |

---

## Task 11-1-3: audit_logs, 시딩·관계 검증 — 시나리오 10개

| # | 시나리오 | 조치 | 기대 결과 | 검증 방법 |
|---|----------|------|-----------|-----------|
| **1** | 마이그레이션 11_1_3 실행 | migrate_phase11_1_3.sql 실행 | COMMIT 완료 | exit code 0 |
| **2** | audit_logs 테이블 존재 | information_schema.tables WHERE table_name='audit_logs' | 1행 | 쿼리 결과 |
| **3** | audit_logs 컬럼 | id, table_name, record_id, action, changed_by, old_values, new_values, created_at | 모두 존재 | information_schema.columns |
| **4** | 시딩 11_1_3 실행 | seed_phase11_1_3.sql 실행 | 에러 없음 | exit code 0 |
| **5** | idx_audit_logs_* 존재 | pg_indexes WHERE tablename='audit_logs' | 2개 이상 | index 목록 |
| **6** | Admin API audit-logs 목록 | GET /api/admin/audit-logs?limit=5 | 200, items·total | status 200 (11-2 audit_log_crud 연동 시) |
| **7** | 7종 테이블 일괄 존재 | SELECT table_name FROM information_schema.tables WHERE table_name IN ('schemas','templates','prompt_presets','rag_profiles','context_rules','policy_sets','audit_logs') | 7행 | 행 수 = 7 |
| **8** | 기존 테이블 스키마 무변경 | documents, knowledge_chunks 등 컬럼 수 동일 | 변경 없음 | 영향도 0 |
| **9** | 백업 존재(선택) | 마이그레이션 전 backup 실행 여부 | 백업 ID 있음 | scripts/backup |
| **10** | Phase 11-1 검증 체크리스트 | phase-11-1-0-plan §3.3 체크리스트 | 신규 테이블만 생성·시딩 행 수·FK·회귀 없음 | plan 문서 기준 |

---

## MCP 실행 체크리스트 (권장 순서)

1. **11-1-1**: 시나리오 1→2→3→4→5→6→7→8→9→10 (마이그레이션·시딩 후 API 검증)
2. **11-1-2**: 시나리오 1→2→3→4→5→6→7→8→9→10
3. **11-1-3**: 시나리오 1→2→3→4→5→6→7→8→9→10

---

## 결과 기록 템플릿

| Task | 시나리오 1~10 | 통과 | 비고 |
|------|----------------|------|------|
| 11-1-1 | 1 2 3 4 5 6 7 8 9 10 | ?/10 | |
| 11-1-2 | 1 2 3 4 5 6 7 8 9 10 | ?/10 | |
| 11-1-3 | 1 2 3 4 5 6 7 8 9 10 | ?/10 | |
| **합계** | **30** | ?/30 | |

상세 결과: [phase-11-1-mcp-webtest-result.md](phase-11-1-mcp-webtest-result.md)
