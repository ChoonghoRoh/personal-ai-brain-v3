# Phase 11-1 통합 테스트 시나리오

**Phase ID**: 11-1
**Phase 명**: DB 스키마·마이그레이션
**작성일**: 2026-02-07
**총 Task 수**: 3개
**총 시나리오 수**: 23개

---

## Task 11-1-1: DB 스키마 정의 (10개 시나리오)

### 시나리오 11-1-1-S01: schemas 스키마 생성 확인

**분류**: 기능
**우선순위**: 높음

#### 전제 조건

- PostgreSQL 실행 중
- 마이그레이션 미실행 상태

#### 실행 단계

1. `docker compose exec postgres psql -U user -d personalai` 접속
2. `\dn` 명령으로 스키마 목록 확인
3. `schemas` 스키마 존재 확인

#### 기대 결과

- `schemas` 스키마가 목록에 표시됨

#### 실제 결과

- [ ] 성공 / [ ] 실패
- 실행 일시:
- 결과:

---

### 시나리오 11-1-1-S02: templates 테이블 생성 확인

**분류**: 기능
**우선순위**: 높음

#### 전제 조건

- 11-1-2 마이그레이션 실행 완료

#### 실행 단계

1. `\dt schemas.*` 명령 실행
2. `templates` 테이블 존재 확인
3. `\d schemas.templates` 명령으로 컬럼 확인

#### 기대 결과

- templates 테이블 존재
- 컬럼: id, name, description, template_type, content, output_format, citation_rule, status, version, published_at, created_by, created_at, updated_at

#### 실제 결과

- [ ] 성공 / [ ] 실패
- 실행 일시:
- 결과:

---

### 시나리오 11-1-1-S03: prompt_presets 테이블 생성 확인

**분류**: 기능
**우선순위**: 높음

#### 전제 조건

- 11-1-2 마이그레이션 실행 완료

#### 실행 단계

1. `\d schemas.prompt_presets` 명령 실행
2. 컬럼 구조 확인

#### 기대 결과

- prompt_presets 테이블 존재
- 컬럼: id, name, task_type, description, system_prompt, model_name, temperature, top_p, max_tokens, constraints, examples, status, version, published_at, created_by, created_at, updated_at

#### 실제 결과

- [ ] 성공 / [ ] 실패
- 실행 일시:
- 결과:

---

### 시나리오 11-1-1-S04: rag_profiles 테이블 생성 확인

**분류**: 기능
**우선순위**: 높음

#### 전제 조건

- 11-1-3 마이그레이션 실행 완료

#### 실행 단계

1. `\d schemas.rag_profiles` 명령 실행
2. 컬럼 구조 확인

#### 기대 결과

- rag_profiles 테이블 존재
- 컬럼: id, name, description, chunk_size, chunk_overlap, top_k, score_threshold, use_rerank, filter_rules, status, version, published_at, created_by, created_at, updated_at

#### 실제 결과

- [ ] 성공 / [ ] 실패
- 실행 일시:
- 결과:

---

### 시나리오 11-1-1-S05: policy_sets 테이블 생성 확인

**분류**: 기능
**우선순위**: 높음

#### 전제 조건

- 11-1-3 마이그레이션 실행 완료

#### 실행 단계

1. `\d schemas.policy_sets` 명령 실행
2. 컬럼 구조 확인

#### 기대 결과

- policy_sets 테이블 존재
- 컬럼: id, name, description, priority, project_domain, template_id, preset_id, rag_profile_id, is_active, created_by, created_at, updated_at

#### 실제 결과

- [ ] 성공 / [ ] 실패
- 실행 일시:
- 결과:

---

### 시나리오 11-1-1-S06: audit_logs 테이블 생성 확인

**분류**: 기능
**우선순위**: 중간

#### 전제 조건

- 11-1-3 마이그레이션 실행 완료

#### 실행 단계

1. `\d schemas.audit_logs` 명령 실행
2. 컬럼 구조 확인

#### 기대 결과

- audit_logs 테이블 존재
- 컬럼: id, entity_type, entity_id, action, changed_by, old_value, new_value, created_at

#### 실제 결과

- [ ] 성공 / [ ] 실패
- 실행 일시:
- 결과:

---

### 시나리오 11-1-1-S07: Foreign Key 제약조건 확인 (policy_sets → templates)

**분류**: 통합
**우선순위**: 중간

#### 전제 조건

- 모든 테이블 생성 완료

#### 실행 단계

1. `\d schemas.policy_sets` 명령 실행
2. Foreign keys 섹션에서 `fk_template` 확인

#### 기대 결과

- `fk_template FOREIGN KEY (template_id) REFERENCES schemas.templates(id)` 존재

#### 실제 결과

- [ ] 성공 / [ ] 실패
- 실행 일시:
- 결과:

---

### 시나리오 11-1-1-S08: Foreign Key 제약조건 확인 (policy_sets → prompt_presets)

**분류**: 통합
**우선순위**: 중간

#### 전제 조건

- 모든 테이블 생성 완료

#### 실행 단계

1. `\d schemas.policy_sets` 명령 실행
2. Foreign keys 섹션에서 `fk_preset` 확인

#### 기대 결과

- `fk_preset FOREIGN KEY (preset_id) REFERENCES schemas.prompt_presets(id)` 존재

#### 실제 결과

- [ ] 성공 / [ ] 실패
- 실행 일시:
- 결과:

---

### 시나리오 11-1-1-S09: Foreign Key 제약조건 확인 (policy_sets → rag_profiles)

**분류**: 통합
**우선순위**: 중간

#### 전제 조건

- 모든 테이블 생성 완료

#### 실행 단계

1. `\d schemas.policy_sets` 명령 실행
2. Foreign keys 섹션에서 `fk_rag_profile` 확인

#### 기대 결과

- `fk_rag_profile FOREIGN KEY (rag_profile_id) REFERENCES schemas.rag_profiles(id)` 존재

#### 실제 결과

- [ ] 성공 / [ ] 실패
- 실행 일시:
- 결과:

---

### 시나리오 11-1-1-S10: 테이블 권한 확인

**분류**: 에러처리
**우선순위**: 낮음

#### 전제 조건

- 모든 테이블 생성 완료
- DB 사용자: `user`

#### 실행 단계

1. `\dp schemas.templates` 명령 실행
2. Access privileges 확인

#### 기대 결과

- `user` 사용자가 테이블에 대한 권한 보유

#### 실제 결과

- [ ] 성공 / [ ] 실패
- 실행 일시:
- 결과:

---

## Task 11-1-2: 마이그레이션 스크립트 (8개 시나리오)

### 시나리오 11-1-2-S01: migrate_phase11_1_2.sql 실행 성공

**분류**: 기능
**우선순위**: 높음

#### 전제 조건

- 초기 DB 상태 (migrations 테이블 존재)

#### 실행 단계

1. `docker compose exec backend python -m alembic upgrade head` 실행
2. 에러 메시지 확인
3. 마이그레이션 버전 확인: `docker compose exec backend python -m alembic current`

#### 기대 결과

- 마이그레이션 성공
- 에러 없음
- 최신 버전 표시

#### 실제 결과

- [ ] 성공 / [ ] 실패
- 실행 일시:
- 결과:

---

### 시나리오 11-1-2-S02: templates 테이블 데이터 타입 검증

**분류**: 기능
**우선순위**: 높음

#### 전제 조건

- 마이그레이션 실행 완료

#### 실행 단계

1. `SELECT column_name, data_type FROM information_schema.columns WHERE table_schema='schemas' AND table_name='templates';`
2. 각 컬럼의 데이터 타입 확인

#### 기대 결과

- id: uuid
- name: character varying(255)
- content: text
- status: character varying(50)
- version: integer

#### 실제 결과

- [ ] 성공 / [ ] 실패
- 실행 일시:
- 결과:

---

### 시나리오 11-1-2-S03: 중복 실행 시 에러 확인

**분류**: 에러처리
**우선순위**: 중간

#### 전제 조건

- 마이그레이션 이미 실행됨

#### 실행 단계

1. `docker compose exec backend python -m alembic upgrade head` 재실행
2. 결과 확인

#### 기대 결과

- "Already at head" 또는 유사 메시지
- 에러 없음

#### 실제 결과

- [ ] 성공 / [ ] 실패
- 실행 일시:
- 결과:

---

### 시나리오 11-1-2-S04: 롤백 테스트 (downgrade)

**분류**: 기능
**우선순위**: 낮음

#### 전제 조건

- 마이그레이션 실행 완료

#### 실행 단계

1. 현재 버전 확인
2. `docker compose exec backend python -m alembic downgrade -1` 실행
3. 테이블 존재 확인

#### 기대 결과

- 이전 버전으로 롤백
- 최신 마이그레이션으로 생성된 테이블 삭제됨

#### 실제 결과

- [ ] 성공 / [ ] 실패
- 실행 일시:
- 결과:

---

### 시나리오 11-1-2-S05: migrate_phase11_1_3.sql 실행 성공

**분류**: 기능
**우선순위**: 높음

#### 전제 조건

- 11-1-2 마이그레이션 완료

#### 실행 단계

1. `docker compose exec backend python -m alembic upgrade head` 실행
2. audit_logs 테이블 생성 확인

#### 기대 결과

- 마이그레이션 성공
- audit_logs, policy_sets 테이블 생성됨

#### 실제 결과

- [ ] 성공 / [ ] 실패
- 실행 일시:
- 결과:

---

### 시나리오 11-1-2-S06: NOT NULL 제약조건 확인 (templates.name)

**분류**: 에러처리
**우선순위**: 중간

#### 전제 조건

- templates 테이블 생성 완료

#### 실행 단계

1. `INSERT INTO schemas.templates (id, template_type, content, output_format, created_by) VALUES (gen_random_uuid(), 'summary', 'test', 'markdown', 'test');` 실행
2. 에러 메시지 확인

#### 기대 결과

- NOT NULL 제약조건 위반 에러 발생
- 메시지: `null value in column "name" violates not-null constraint`

#### 실제 결과

- [ ] 성공 / [ ] 실패
- 실행 일시:
- 결과:

---

### 시나리오 11-1-2-S07: UNIQUE 제약조건 확인 (templates.name+version)

**분류**: 에러처리
**우선순위**: 중간

#### 전제 조건

- templates 테이블에 데이터 1건 존재

#### 실행 단계

1. 동일한 name + version 값으로 INSERT 시도
2. 에러 메시지 확인

#### 기대 결과

- UNIQUE 제약조건 위반 에러 발생

#### 실제 결과

- [ ] 성공 / [ ] 실패
- 실행 일시:
- 결과:

---

### 시나리오 11-1-2-S08: 인덱스 생성 확인

**분류**: 성능
**우선순위**: 낮음

#### 전제 조건

- 마이그레이션 완료

#### 실행 단계

1. `\di schemas.*` 명령으로 인덱스 목록 확인
2. templates, prompt_presets, rag_profiles 관련 인덱스 확인

#### 기대 결과

- 각 테이블에 적절한 인덱스 생성됨

#### 실제 결과

- [ ] 성공 / [ ] 실패
- 실행 일시:
- 결과:

---

## Task 11-1-3: 시드 데이터 (5개 시나리오)

### 시나리오 11-1-3-S01: seed_phase11_1_2.sql 실행 성공

**분류**: 기능
**우선순위**: 높음

#### 전제 조건

- 11-1-2 마이그레이션 완료
- templates, prompt_presets 테이블 비어있음

#### 실행 단계

1. `docker compose exec -T postgres psql -U user -d personalai < scripts/db/seed_phase11_1_2.sql` 실행
2. 결과 확인

#### 기대 결과

- 시드 데이터 삽입 성공
- 에러 없음

#### 실제 결과

- [ ] 성공 / [ ] 실패
- 실행 일시:
- 결과:

---

### 시나리오 11-1-3-S02: 템플릿 시드 데이터 확인

**분류**: 기능
**우선순위**: 높음

#### 전제 조건

- seed_phase11_1_2.sql 실행 완료

#### 실행 단계

1. `SELECT COUNT(*) FROM schemas.templates;` 실행
2. `SELECT name FROM schemas.templates ORDER BY name;` 실행

#### 기대 결과

- 템플릿 2개 이상 존재
- "요약 보고서", "기본 의사결정 문서" 등 기본 템플릿 포함

#### 실제 결과

- [ ] 성공 / [ ] 실패
- 실행 일시:
- 결과:

---

### 시나리오 11-1-3-S03: 프리셋 시드 데이터 확인

**분류**: 기능
**우선순위**: 높음

#### 전제 조건

- seed_phase11_1_2.sql 실행 완료

#### 실행 단계

1. `SELECT COUNT(*) FROM schemas.prompt_presets;` 실행
2. `SELECT name FROM schemas.prompt_presets ORDER BY name;` 실행

#### 기대 결과

- 프리셋 2개 이상 존재
- 기본 프리셋 포함

#### 실제 결과

- [ ] 성공 / [ ] 실패
- 실행 일시:
- 결과:

---

### 시나리오 11-1-3-S04: seed_phase11_1_3.sql 실행 성공

**분류**: 기능
**우선순위**: 높음

#### 전제 조건

- 11-1-3 마이그레이션 완료
- rag_profiles, policy_sets 테이블 비어있음

#### 실행 단계

1. `docker compose exec -T postgres psql -U user -d personalai < scripts/db/seed_phase11_1_3.sql` 실행
2. 결과 확인

#### 기대 결과

- 시드 데이터 삽입 성공
- 에러 없음

#### 실제 결과

- [ ] 성공 / [ ] 실패
- 실행 일시:
- 결과:

---

### 시나리오 11-1-3-S05: RAG 프로필 및 정책 시드 데이터 확인

**분류**: 기능
**우선순위**: 높음

#### 전제 조건

- seed_phase11_1_3.sql 실행 완료

#### 실행 단계

1. `SELECT COUNT(*) FROM schemas.rag_profiles;` 실행
2. `SELECT COUNT(*) FROM schemas.policy_sets;` 실행

#### 기대 결과

- rag_profiles 1개 이상 존재
- policy_sets 1개 이상 존재

#### 실제 결과

- [ ] 성공 / [ ] 실패
- 실행 일시:
- 결과:

---

## 통합 시나리오 (Phase 11-1 전체)

### 시나리오 11-1-INT-01: 전체 마이그레이션 + 시드 데이터 파이프라인

**분류**: 통합
**우선순위**: 높음

#### 전제 조건

- 초기 DB 상태

#### 실행 단계

1. `docker compose down && docker volume rm personal-ai-brain-v2_postgres-data`
2. `docker compose up -d postgres`
3. `docker compose exec backend python -m alembic upgrade head`
4. `docker compose exec -T postgres psql -U user -d personalai < scripts/db/seed_phase11_1_2.sql`
5. `docker compose exec -T postgres psql -U user -d personalai < scripts/db/seed_phase11_1_3.sql`
6. 모든 테이블 및 데이터 확인

#### 기대 결과

- 전체 파이프라인 성공
- 모든 테이블 생성됨
- 시드 데이터 삽입됨

#### 실제 결과

- [ ] 성공 / [ ] 실패
- 실행 일시:
- 결과:

---

**총 시나리오**: 23개 (10 + 8 + 5)
**작성 완료일**: 2026-02-07
