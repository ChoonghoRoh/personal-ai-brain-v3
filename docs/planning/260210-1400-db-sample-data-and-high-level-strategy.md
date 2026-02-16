# DB 서비스 샘플 데이터 및 고도화 전략

**작성일**: 2026-02-10 14:00  
**형식**: YYMMDD-HHMM-문서명  
**범위**: 현재 DB 구조 분석, 카테고리별 100+ 임의 데이터 생성 방안, .md 기반 단계별 고도화 전략  
**제약**: 개발 소스 수정 없음 — 분석·리포트만 작성  

**Phase 14 연동**: 본 문서는 [Phase 14 Master Plan Guide](../phases/phase-14-master-plan-guide.md)와 연동·호환된다. Phase 14의 **14-6 DB 샘플 데이터·고도화·검증** 블록에서 본 문서를 기준으로 Task를 세분화·실행하며, **개발 완료 후 데이터 2차 검증**(14-6-5) 지침을 §12에서 정의한다. Phase 14 가이드 참고 문서에 본 문서가 링크되어 누락되지 않도록 명시되어 있다.

---

## 1. 현재 DB 구조 요약

### 1.1 테이블 목록 (backend/models)

| 구분           | 테이블명            | 모델 클래스       | 용도                                                      |
| -------------- | ------------------- | ----------------- | --------------------------------------------------------- |
| **지식·문서**  | projects            | Project           | 프로젝트 단위                                             |
|                | documents           | Document          | 문서 메타 (file_path, file_type, category_label_id)       |
|                | knowledge_chunks    | KnowledgeChunk    | 청크 본문, status, title, qdrant_point_id                 |
|                | labels              | Label             | 키워드·카테고리·프로젝트·도메인 등 (label_type)           |
|                | knowledge_labels    | KnowledgeLabel    | 청크-라벨 다대다                                          |
|                | knowledge_relations | KnowledgeRelation | 청크 간 관계 (source/target_chunk_id, relation_type)      |
| **인지·대화**  | memories            | Memory            | long_term/short_term/working, expires_at                  |
|                | conversations       | Conversation      | 질문-답변, session_id, sources                            |
|                | reasoning_results   | ReasoningResult   | 추론 결과, session_id, share_id, expires_at               |
| **Admin 설정** | schemas             | AdminSchema       | 역할 스키마 (role_key, display_name)                      |
|                | templates           | AdminTemplate     | 판단 문서 템플릿                                          |
|                | prompt_presets      | AdminPromptPreset | 프롬프트 프리셋 (task_type, system_prompt)                |
|                | rag_profiles        | AdminRagProfile   | RAG 파라미터 (chunk_size, top_k, score_threshold)         |
|                | context_rules       | AdminContextRule  | 문서/도메인별 분류 규칙                                   |
|                | policy_sets         | AdminPolicySet    | 정책 (template/preset/rag_profile 연결)                   |
|                | audit_logs          | AdminAuditLog     | 변경 이력 (table_name, record_id, action, old/new_values) |

### 1.2 관계·인덱스 요약

- **documents** → projects(1:N), labels(category_label_id).
- **knowledge_chunks** → documents(1:N). GIN 인덱스: content (Phase 12-2-3).
- **labels** → (name, label_type) 복합 unique, parent_label_id 계층.
- **knowledge_labels** → knowledge_chunks, labels.
- **knowledge_relations** → knowledge_chunks (source/target).
- **memories** → knowledge_chunks(related_chunk_id). expires_at 인덱스.
- **conversations** / **reasoning_results** → session_id, expires_at 인덱스.
- **Admin** 테이블: UUID PK, PostgreSQL JSONB/ARRAY 사용. **policy_sets** → templates, prompt_presets, rag_profiles FK.

### 1.3 Phase 14 가이드와의 호환성 요약

| Phase 14 항목 | 본 문서·DB 반영 |
|---------------|------------------|
| **역할(role)** | Phase 14-1: UserInfo/JWT에 role 추가. DB에 users 테이블 없음 시 JWT claim만 사용. 회원관리(14-5) 도입 시 users·roles 테이블 설계 시 본 문서의 Admin 테이블·시드 순서와 충돌 없이 확장. |
| **audit_logs.changed_by** | 현재 컬럼 존재. 샘플 시드 시 `changed_by`는 시드 스크립트 사용자 또는 고정값. Phase 14 권한 적용 후 실제 username/role과 연동 가능. |
| **page_access_logs** | Phase 13-4 테이블. 본 문서 테이블 목록(1.1)에 없으나 백업·복구(§8) 시 PostgreSQL 전체 덤프에 포함. 시드 대상 아님(애플리케이션 로그). |
| **Admin schemas.role_key** | AdminSchema.role_key는 **스키마 정의용** 키(display_order 등). RBAC용 user role과 혼동 금지. Phase 14 역할은 JWT/ users 테이블에서 관리. |

---

## 2. 로컬 .md 파일 종합과 카테고리 분리

### 2.1 .md 파일 카테고리 (docs 기준)

프로젝트 내 **docs/** 및 루트 부근 .md를 다음 파트로 분리하여 샘플 데이터·고도화에 반영한다.

| 파트                   | 설명                               | 예시 경로/패턴                                                       | DB 반영                                                                     |
| ---------------------- | ---------------------------------- | -------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| **개발 (development)** | Phase Task, 구현 가이드, 코드 리뷰 | docs/phases/\*_/tasks/_.md, docs/dev, scripts/\*.md                  | documents.file_path, knowledge_chunks.content, labels(category=development) |
| **계획 (planning)**    | 마스터 플랜, 시나리오, 로드맵      | docs/planning/_.md, docs/phases/_-master-plan\*.md                   | documents, chunks, labels(category=planning)                                |
| **검토 (review)**      | QC, 검증, 테스트 리포트            | docs/phases/\**/*verification*.md, *qc-report*.md, *test-report\*.md | documents, chunks, labels(category=review)                                  |
| **룰 (rules)**         | 페르소나, SSOT, 코딩 규칙          | docs/rules/**/\*.md, docs/SSOT/**/\*.md, .cursor/rules               | documents, chunks, labels(category=rules)                                   |
| **AI**                 | LLM, RAG, 추론, 프롬프트 관련      | docs/overview/_llm_.md, docs/features/reasoning*/*.md, docs/prompts  | documents, chunks, labels(category=ai)                                      |
| **기타**               | README, webtest, overview 기타     | docs/README, docs/webtest, docs/overview 기타                        | documents, labels(category=general)                                         |

### 2.2 .md → documents / chunks 매핑 전략

1. **documents**: 각 .md 파일 1건 (file_path=상대경로, file_type=md, size=파일 크기).
2. **projects**: 1건 "personal-ai-brain-v3" 또는 docs / web / scripts 등 경로별로 여러 프로젝트.
3. **knowledge_chunks**: .md 내용을 heading/paragraph 단위로 분할, chunk_index 부여. 1문서당 1~50+ 청크 가능.
4. **labels**: label_type=category, name=development|planning|review|rules|ai|general. 필요 시 keyword, project, domain 추가.
5. **knowledge_labels**: 청크별로 해당 문서 경로의 파트(development/planning/…)에 따라 label_id 연결.

---

## 3. 카테고리별 100+ 샘플 데이터 생성 방안

### 3.1 목표 건수 (테이블별)

| 테이블              | 목표 건수 | 생성 방식                                                                             |
| ------------------- | --------- | ------------------------------------------------------------------------------------- |
| projects            | 5~10      | 고정 5~10개 (docs, web, backend, scripts, brain 등)                                   |
| documents           | **100+**  | 로컬 .md 파일 스캔 → 1파일 1행. 739개 .md 있으므로 100+ 충족                          |
| knowledge_chunks    | **300+**  | documents 100+ × 평균 3~5 청크. 또는 상위 100개 .md만 청크화                          |
| labels              | **100+**  | keyword 50 + category 6 + project 10 + domain 20 + 기타. 중복 제거 (name, label_type) |
| knowledge_labels    | **500+**  | 청크당 1~5 라벨 연결 (문서 카테고리·키워드 추출)                                      |
| knowledge_relations | 50~200    | 청크 간 relation_type (references, similar, parent_child 등)                          |
| memories            | **100+**  | long_term 30, short_term 40, working 30. content·category·expires_at 다양화           |
| conversations       | **100+**  | question/answer/session_id/sources. 시나리오·QA 로그 유사                             |
| reasoning_results   | **100+**  | question/answer/reasoning_steps/mode/session_id. share_id·expires_at 일부             |
| schemas             | 20~50     | role_key·display_name·description (reasoning, search, admin 등)                       |
| templates           | **100+**  | template_type별 (judgment, summary, extraction 등). content 마크다운                  |
| prompt_presets      | **100+**  | task_type별 (reasoning, search, ask 등). system_prompt·temperature·max_tokens         |
| rag_profiles        | 20~50     | name·chunk_size·top_k·score_threshold·use_rerank 조합                                 |
| context_rules       | 20~50     | document_type·domain_tags·classification_logic                                        |
| policy_sets         | 20~50     | template/preset/rag_profile FK, priority·is_active                                    |
| audit_logs          | **100+**  | table_name·record_id·action·changed_by·old_values/new_values                          |

### 3.2 생성 순서 (의존성 고려)

1. **projects** → **labels** (category 등)
2. **documents** (projects, category_label_id optional)
3. **knowledge_chunks** (documents)
4. **knowledge_labels** (chunks, labels)
5. **knowledge_relations** (chunks)
6. **memories**, **conversations**, **reasoning_results** (독립 또는 chunk 참조)
7. **schemas** → **templates**, **prompt_presets**, **rag_profiles** → **context_rules**, **policy_sets**
8. **audit_logs** (다른 테이블 CRUD 시뮬레이션)

### 3.3 데이터 소스 (임의 데이터)

| 소스              | 활용                                                                                                      |
| ----------------- | --------------------------------------------------------------------------------------------------------- |
| **로컬 .md 파일** | documents 경로·개수, knowledge_chunks 내용·제목. 개발/계획/검토/룰/AI 파트 분류로 labels·knowledge_labels |
| **고정 시드**     | Faker 또는 고정 문자열로 memories/conversations/reasoning_results question·answer·content 생성            |
| **Admin 시드**    | templates/prompt_presets/rag_profiles는 문서(docs)에 있는 예시 문구·설정값을 참고해 100+ 조합             |
| **audit_logs**    | 위 테이블에 대한 create/update/delete 시뮬레이션으로 100+ 행                                              |

---

## 4. 단계별 고도화 전략

### 4.1 1단계: .md 수집·분류 (분석)

- **작업**: docs/ 및 선택 경로의 모든 .md 목록 수집, 경로 규칙으로 development/planning/review/rules/ai/general 분류.
- **산출물**: `docs/planning/260210-1400-md-inventory-by-category.md` (목록 표, 건수).
- **DB 반영**: 없음 (분석만).

### 4.2 2단계: documents·projects·labels 시드

- **작업**: projects 5~10건, labels 100+ (category 6 + keyword 등). documents 100+ (.md 1:1, file_path/file_type/size).
- **산출물**: SQL 시드 또는 Alembic/스크립트로 INSERT. 기존 DB 백업 후 실행.
- **검증**: documents count ≥ 100, labels count ≥ 100.

### 4.3 3단계: knowledge_chunks·knowledge_labels

- **작업**: 선택 documents(100+)에 대해 청크 분할(heading/paragraph). knowledge_labels는 문서 카테고리·키워드로 연결.
- **산출물**: 청크 INSERT, 라벨 연결. Qdrant 연동은 별도(임베딩·벡터 저장).
- **검증**: knowledge_chunks ≥ 300, knowledge_labels ≥ 500.

### 4.4 4단계: memories·conversations·reasoning_results

- **작업**: 시드 데이터 100+ 건씩. memories는 category·memory_type·expires_at 다양화. conversations/reasoning_results는 session_id·모드 다양화.
- **산출물**: INSERT 스크립트 또는 Fixture.
- **검증**: 각 100+ 건.

### 4.5 5단계: Admin 설정 테이블 (schemas, templates, prompt_presets, rag_profiles, context_rules, policy_sets)

- **작업**: schemas 20~50, templates 100+, prompt_presets 100+, rag_profiles 20~50, context_rules 20~50, policy_sets 20~50. docs/planning·docs/phases·docs/rules 문구 참고.
- **산출물**: 시드 SQL/스크립트. FK 순서 준수.
- **검증**: templates·prompt_presets ≥ 100.

### 4.6 6단계: audit_logs·knowledge_relations

- **작업**: audit_logs 100+ (다른 테이블 CRUD 시뮬레이션). knowledge_relations는 chunks 기반으로 references/similar 등 50~200건.
- **산출물**: 시드 스크립트.
- **검증**: audit_logs ≥ 100.

### 4.7 7단계: Qdrant 연동 (선택)

- **작업**: knowledge_chunks 300+에 대해 임베딩 생성·Qdrant upsert. qdrant_point_id 역저장.
- **산출물**: 기존 embed_and_store 또는 전용 스크립트. 현재 개발 소스 수정 없이 **설계만** 본 문서에 반영.

---

## 5. 파트별 상세 전략 (개발·계획·검토·룰·AI)

### 5.1 개발 (development)

- **대상 .md**: docs/phases/\*_/tasks/_.md, docs/dev, scripts/_.md, phase-_-plan.md 등.
- **labels**: category=development, keyword=phase|task|implementation 등.
- **용도**: 지식 검색·RAG 시 "개발" 문서 우선, 통계·대시보드에서 development 문서/청크 수 집계.

### 5.2 계획 (planning)

- **대상 .md**: docs/planning/*.md, *master-plan*.md, *scenarios*.md, *roadmap\*.md.
- **labels**: category=planning, keyword=plan|scenario|roadmap 등.
- **용도**: 계획서 검색, 메뉴/시나리오 문서와 1:1 대응 확인.

### 5.3 검토 (review)

- **대상 .md**: _verification_.md, _qc-report_.md, _test-report_.md, _final-summary_.md.
- **labels**: category=review, keyword=qc|test|verification 등.
- **용도**: QA·검증 문서 검색, 회귀 테스트 시나리오 참조.

### 5.4 룰 (rules)

- **대상 .md**: docs/rules/**/\*.md, docs/SSOT/**/\*.md, AGENTS.md, .cursor/rules 참조 경로.
- **labels**: category=rules, keyword=ssot|persona|convention 등.
- **용도**: AI/에이전트가 참조하는 규칙 문서 우선 검색.

### 5.5 AI

- **대상 .md**: docs/overview/_llm_.md, docs/features/reasoning*/*.md, docs/prompts/\*.md, Local LLM·Ollama 관련.
- **labels**: category=ai, keyword=llm|rag|reasoning|prompt 등.
- **용도**: RAG·Reasoning·프롬프트 개선 시 참조.

---

## 6. 현재 DB 구조와의 최적화 상태 제안

### 6.1 유지 권장

- **테이블 구조**: 현재 16개 테이블·관계·인덱스(Phase 12-2-3 GIN 등) 유지.
- **Admin UUID·JSONB**: PostgreSQL 호환, 확장에 유리.
- **labels (name, label_type) unique**: 카테고리별 동일 이름 허용.

### 6.2 선택 개선 (구현 없이 설계만)

| 항목                           | 제안                                                 | 비고                                 |
| ------------------------------ | ---------------------------------------------------- | ------------------------------------ |
| **documents.file_path**        | 인덱스 유지, 길이 제한(예: 512) 검토                 | 대용량 .md 시 경로 길이              |
| **knowledge_chunks.content**   | GIN 유지. 대용량 텍스트 시 TOAST·부분 인덱스 검토    | 현재 구조로 100+ 문서·300+ 청크 가능 |
| **memories.expires_at**        | TTL 스케줄러(Phase 12-3-4) 유지. 인덱스 유지         |                                      |
| **audit_logs**                 | table_name·record_id·created_at 복합 인덱스 검토     | 조회 성능                            |
| **샘플 데이터 전용 DB/스키마** | 개발·테스트용 DB에만 100+ 시드 적용, 프로덕션과 분리 | 데이터 품질·보안                     |

### 6.3 데이터 생성 도구 제안

- **스크립트 위치**: `scripts/db/` 또는 `scripts/seed/`.
- **형식**: Python + SQLAlchemy 또는 순수 SQL. Faker optional.
- **실행**: `python scripts/db/seed_sample_data.py --category all --target 100` 등. 환경변수로 DB URL 지정.

---

## 7. 요약 및 다음 단계

- **카테고리별 100+ 건**: documents, knowledge_chunks, labels, knowledge_labels, memories, conversations, reasoning_results, templates, prompt_presets, audit_logs에서 목표 건수 달성 가능.
- **.md 기반 전략**: development/planning/review/rules/ai 파트로 분리해 documents·chunks·labels와 매핑.
- **단계**: (1) .md 인벤토리·분류 → (2) projects·labels·documents → (3) chunks·knowledge_labels → (4) memories·conversations·reasoning_results → (5) Admin 설정 100+ → (6) audit_logs·relations → (7) Qdrant 연동(선택).
- **현재 개발 소스**: 수정하지 않고, 본 문서는 분석·리포트·계획만 제시. 실제 시드 스크립트·마이그레이션은 별도 Task에서 진행 권장.

### 7.1 Phase 14 Master Plan Task 동기화

[Phase 14 Master Plan Guide](../phases/phase-14-master-plan-guide.md) §5.2·§8.5의 **14-6 DB 샘플 데이터·고도화·검증** 블록과 본 문서의 대응 관계는 아래와 같다. Phase 14 착수 시 본 문서를 누락 없이 참조한다.

| Phase 14 Task ID | 본 문서 대응 | 산출물·검증 |
|------------------|--------------|-------------|
| **14-6-1** | §1.3 Phase 14 호환성, 전 문서 점검 | 호환성 점검·보완 |
| **14-6-2a** | §8.1 백업 | backup_system.py backup --type full |
| **14-6-2b** | §4.1 .md 수집·분류 | md-inventory-by-category (분석만) |
| **14-6-2c** | §4.2 projects·labels 시드 | projects 5~10, labels 100+ |
| **14-6-2d** | §4.2 documents 시드 | documents 100+ |
| **14-6-2e** | §4.3 knowledge_chunks·knowledge_labels | chunks 300+, knowledge_labels 500+ |
| **14-6-2f** | §4.4 memories·conversations·reasoning_results | 각 100+ |
| **14-6-2g** | §4.5 Admin 설정 시드 | schemas, templates, presets, rag_profiles, context_rules, policy_sets (templates·presets 100+) |
| **14-6-2h** | §4.6 audit_logs·knowledge_relations | audit_logs 100+, relations 50~200 |
| **14-6-3** | §9 검증 전략, §11.3 투입 후 검증 | validate_sample_data.py, /api/integrity/* (1차 검증) |
| **14-6-4** | §4.7 Qdrant 연동 (선택) | 임베딩·upsert, qdrant_point_id 역저장 |
| **14-6-5** | §12 개발 완료 후 데이터 2차 검증 | 재검증 스크립트·리포트·성공 기준 |

---

## 8. 백업 및 복구 방안

### 8.1 백업 전략 (샘플 데이터 투입 전 필수)

#### 8.1.1 PostgreSQL 백업

- **도구**: `pg_dump` (Custom Format `-F c`)
- **실행 스크립트**: `scripts/devtool/backup_system.py`
- **백업 경로**: `backups/backup_YYYYMMDD_HHMMSS/`
- **백업 명령**:

```bash
python scripts/devtool/backup_system.py backup --type full
```

- **백업 내용**:
  - 모든 테이블 스키마 (CREATE TABLE, INDEX, CONSTRAINT)
  - 모든 데이터 (INSERT 문)
  - Foreign Key 제약조건
  - Sequence 현재값

#### 8.1.2 Qdrant 백업

- **도구**: tar.gz 압축
- **백업 대상**: `qdrant-data-ver3/` 디렉토리 전체
- **실행**: `backup_system.py`가 자동으로 Qdrant 데이터 디렉토리를 tar.gz로 압축
- **주의**: Qdrant 서비스 중지 후 백업 권장 (데이터 일관성)

#### 8.1.3 메타데이터 백업

- **대상**: `brain/system/`, 작업 로그, 설정 파일
- **형식**: tar.gz 압축
- **목적**: 샘플 데이터 투입 전 현재 상태 보존

#### 8.1.4 백업 검증

- **파일 존재 확인**: 백업 파일 경로 및 크기 검증
- **메타데이터 기록**: `backups/backup_metadata.json`에 백업 정보 저장
  - backup_name, timestamp, status, files (type, path, size)
- **무결성 체크**: 백업 파일 해시(선택) 또는 크기 비교

### 8.2 복구 시나리오별 절차

#### 시나리오 A: 전체 복구 (샘플 데이터 투입 실패 시)

1. **PostgreSQL 복구**:

```bash
python scripts/devtool/backup_system.py restore --name backup_20260210_140000
```

- `pg_restore -c` (기존 데이터 삭제 후 복원)
- Foreign Key 제약조건 자동 복구
- Sequence 값 복구

2. **Qdrant 복구**:
   - 기존 `qdrant-data-ver3/` 디렉토리 삭제
   - 백업 tar.gz 압축 해제
   - Qdrant 서비스 재시작 → 자동 인덱스 재구성

3. **메타데이터 복구** (선택):
   - `brain/system/` 디렉토리 복원

4. **검증**:
   - PostgreSQL 테이블 count 확인
   - Qdrant 포인트 수 확인
   - `/api/integrity/check` API 호출로 데이터 무결성 확인

#### 시나리오 B: 부분 복구 (특정 테이블만 복구)

- **테이블별 복구** (수동):

```sql
-- 백업에서 특정 테이블만 추출
pg_restore -t table_name backup_file.dump -d knowledge
```

- **주의**: Foreign Key 제약조건 순서 준수 (부모 → 자식 테이블)

#### 시나리오 C: 샘플 데이터만 삭제 (기존 데이터 유지)

- **태그/플래그 기반**: 샘플 데이터 INSERT 시 `is_sample=true` 플래그 또는 특정 project_id 사용
- **삭제 쿼리**:

```sql
DELETE FROM knowledge_chunks WHERE document_id IN (
    SELECT id FROM documents WHERE project_id = (SELECT id FROM projects WHERE name = 'SAMPLE_DATA')
);
DELETE FROM documents WHERE project_id = (SELECT id FROM projects WHERE name = 'SAMPLE_DATA');
DELETE FROM projects WHERE name = 'SAMPLE_DATA';
```

- **Cascade 삭제**: `cascade="all, delete-orphan"` 설정으로 자동 연쇄 삭제
  - Project 삭제 → Documents 자동 삭제
  - Document 삭제 → KnowledgeChunks 자동 삭제
  - Chunk 삭제 → KnowledgeLabels, KnowledgeRelations 자동 삭제

### 8.3 롤백 계획

- **복구 소요 시간**: 약 5-10분 (데이터 크기에 따라)
- **데이터 손실**: 백업 시점 이후 변경 사항 손실 (샘플 데이터 투입 전 백업이므로 영향 없음)
- **서비스 중단**: 복구 중 Backend API 중지 필요 (약 5분)
- **테스트 환경**: 개발/테스트 DB에서 먼저 복구 테스트 후 프로덕션 적용

---

## 9. 샘플 데이터 유효성 및 정합성 검증 전략

### 9.1 데이터 유효성 검증 (Validation)

#### 9.1.1 스키마 준수 검증

| 테이블               | 검증 항목                                   | 검증 방법             | 예시 SQL                                                                                       |
| -------------------- | ------------------------------------------- | --------------------- | ---------------------------------------------------------------------------------------------- |
| **projects**         | name NOT NULL, 길이 ≤ 255                   | INSERT 전 검증        | `SELECT name FROM projects WHERE name IS NULL OR length(name) > 255;`                          |
| **documents**        | file_path NOT NULL, file_type 허용값        | ENUM/CHECK 제약       | `SELECT * FROM documents WHERE file_type NOT IN ('md', 'txt', 'pdf', 'docx');`                 |
| **knowledge_chunks** | content NOT NULL, status 허용값             | ENUM 체크             | `SELECT * FROM knowledge_chunks WHERE status NOT IN ('active', 'archived', 'draft');`          |
| **labels**           | (name, label_type) unique                   | UniqueConstraint 검증 | `SELECT name, label_type, COUNT(*) FROM labels GROUP BY name, label_type HAVING COUNT(*) > 1;` |
| **memories**         | memory_type 허용값, expires_at ≥ created_at | CHECK 제약            | `SELECT * FROM memories WHERE expires_at IS NOT NULL AND expires_at < created_at;`             |

#### 9.1.2 데이터 타입 및 범위 검증

- **정수형 (Integer)**: id, chunk_index, score (0~100)
- **타임스탬프 (DateTime)**: created_at, updated_at, expires_at (미래 날짜 허용)
- **텍스트 (String/Text)**: 최대 길이 검증 (name: 255, file_path: 512, content: TEXT 무제한)
- **JSON/JSONB (Admin)**: JSON 파싱 가능 여부 확인

#### 9.1.3 필수 필드 검증

- **NOT NULL 제약**: projects.name, documents.file_path, knowledge_chunks.content 등
- **검증 쿼리**:

```sql
-- 예: documents 테이블 필수 필드
SELECT COUNT(*) FROM documents WHERE file_path IS NULL OR file_type IS NULL;
-- 결과: 0 (샘플 데이터 투입 후)
```

### 9.2 데이터 정합성 검증 (Consistency)

#### 9.2.1 Foreign Key 제약조건 검증

| 테이블                  | FK 관계                                                | 검증 쿼리                                                                                                                                                                       | 예상 결과            |
| ----------------------- | ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------- |
| **documents**           | project_id → projects.id                               | `SELECT COUNT(*) FROM documents d LEFT JOIN projects p ON d.project_id = p.id WHERE d.project_id IS NOT NULL AND p.id IS NULL;`                                                 | 0 (고아 레코드 없음) |
| **knowledge_chunks**    | document_id → documents.id                             | `SELECT COUNT(*) FROM knowledge_chunks c WHERE c.document_id NOT IN (SELECT id FROM documents);`                                                                                | 0                    |
| **knowledge_labels**    | chunk_id → knowledge_chunks.id                         | `SELECT COUNT(*) FROM knowledge_labels kl WHERE kl.chunk_id NOT IN (SELECT id FROM knowledge_chunks);`                                                                          | 0                    |
| **knowledge_labels**    | label_id → labels.id                                   | `SELECT COUNT(*) FROM knowledge_labels kl WHERE kl.label_id NOT IN (SELECT id FROM labels);`                                                                                    | 0                    |
| **knowledge_relations** | source_chunk_id, target_chunk_id → knowledge_chunks.id | `SELECT COUNT(*) FROM knowledge_relations kr WHERE kr.source_chunk_id NOT IN (SELECT id FROM knowledge_chunks) OR kr.target_chunk_id NOT IN (SELECT id FROM knowledge_chunks);` | 0                    |
| **policy_sets**         | template_id, prompt_preset_id, rag_profile_id          | Admin FK 제약                                                                                                                                                                   | 0 (고아 정책 없음)   |

#### 9.2.2 참조 무결성 검증 (Qdrant - PostgreSQL)

- **도구**: `backend/services/system/integrity_service.py`
- **검증 API**: `GET /api/integrity/sync`
- **검증 항목**:
  1. Qdrant 포인트 수 = PostgreSQL knowledge_chunks 수
  2. 각 chunk의 qdrant_point_id가 Qdrant에 실제 존재
  3. Qdrant 포인트의 payload에 chunk_id, document_id 메타데이터 존재
- **자동 수정**: `POST /api/integrity/fix/orphan-chunks` (고아 청크 삭제)

#### 9.2.3 중복 데이터 검증

- **labels (name, label_type) unique**:

```sql
SELECT name, label_type, COUNT(*)
FROM labels
GROUP BY name, label_type
HAVING COUNT(*) > 1;
-- 결과: 0 rows (중복 없음)
```

- **documents file_path 중복** (unique는 아니지만 논리적 중복 확인):

```sql
SELECT file_path, COUNT(*)
FROM documents
GROUP BY file_path
HAVING COUNT(*) > 1;
```

#### 9.2.4 관계 일관성 검증

- **청크-문서 관계**: 모든 청크는 유효한 문서에 속함
- **라벨-청크 관계**: 모든 KnowledgeLabel은 유효한 청크와 라벨 연결
- **청크-청크 관계**: KnowledgeRelation의 source/target 모두 유효
- **검증 API**: `GET /api/integrity/consistency`

### 9.3 데이터 품질 검증 (Quality)

#### 9.3.1 샘플 데이터 현실성 검증

- **documents.file_path**: 실제 로컬 .md 파일 경로 사용 (docs/_, scripts/_ 등)
- **knowledge_chunks.content**: 실제 .md 파일 내용 청크화 (빈 content 금지)
- **labels.name**: 의미 있는 키워드/카테고리명 (예: "development", "planning", "Python")
- **memories.content**: 자연스러운 문장 (Faker 또는 고정 시드 사용)
- **conversations.question**: QA 형식 준수, 한글/영문 혼용

#### 9.3.2 데이터 분포 검증

- **카테고리별 건수 균형**: development 100+, planning 100+, review 50+, rules 50+, AI 100+
- **청크 크기 분포**: 평균 500~2000자, 최소 100자 이상
- **라벨당 청크 수**: 평균 3~10개 청크 (극단값 확인)
- **통계 쿼리**:

```sql
-- 카테고리별 문서 수
SELECT l.name AS category, COUNT(d.id) AS doc_count
FROM documents d
JOIN labels l ON d.category_label_id = l.id
GROUP BY l.name;

-- 청크 크기 통계
SELECT
    AVG(LENGTH(content)) AS avg_length,
    MIN(LENGTH(content)) AS min_length,
    MAX(LENGTH(content)) AS max_length
FROM knowledge_chunks;
```

### 9.4 검증 자동화 스크립트

#### 9.4.1 검증 스크립트 구조

- **위치**: `scripts/db/validate_sample_data.py`
- **기능**:
  1. 스키마 준수 검증 (데이터 타입, 제약조건)
  2. FK 제약조건 검증 (고아 레코드 검출)
  3. Qdrant-PostgreSQL 동기화 검증
  4. 중복 데이터 검증 (unique 제약)
  5. 데이터 품질 검증 (빈 content, 분포)
- **출력**: 검증 리포트 (Pass/Fail, 문제 건수, SQL 쿼리 결과)

#### 9.4.2 실행 예시

```bash
# 전체 검증
python scripts/db/validate_sample_data.py --all

# 특정 검증만 실행
python scripts/db/validate_sample_data.py --fk-check --sync-check

# 리포트 출력
python scripts/db/validate_sample_data.py --report validation_report.md
```

---

## 10. 위험 리스크 분석 및 대응 방안

### 10.1 프로덕션 DB 영향도 분석

| 리스크                           | 심각도      | 발생 확률 | 영향 범위              | 대응 방안                                                      |
| -------------------------------- | ----------- | --------- | ---------------------- | -------------------------------------------------------------- |
| **기존 데이터 덮어쓰기**         | 🔴 Critical | Low       | 전체 DB                | ✅ 백업 필수 (8.1 참조), 샘플 데이터는 별도 project_id로 구분  |
| **FK 제약 위반으로 INSERT 실패** | 🟡 Medium   | Medium    | 샘플 데이터만          | ✅ 생성 순서 준수 (3.2 참조), 트랜잭션 롤백                    |
| **Unique 제약 위반**             | 🟡 Medium   | Low       | labels, schemas 테이블 | ✅ 중복 체크 후 INSERT IGNORE 또는 ON CONFLICT DO NOTHING      |
| **디스크 공간 부족**             | 🟠 High     | Low       | 전체 시스템            | ✅ 샘플 데이터 크기 추정 (약 50~100MB), 사전 용량 확인         |
| **Qdrant 동기화 불일치**         | 🟡 Medium   | Medium    | 검색 기능              | ✅ 샘플 데이터 투입 후 `/api/integrity/sync` 검증, 수동 재색인 |
| **성능 저하 (대량 INSERT)**      | 🟢 Low      | Medium    | Backend API 응답 시간  | ✅ 배치 INSERT (100행 단위), INDEX 비활성화 후 재생성          |

### 10.2 데이터 손실 가능성

#### 10.2.1 백업 실패 시나리오

- **원인**: 디스크 용량 부족, pg_dump 권한 오류, Qdrant 서비스 중지
- **영향**: 복구 불가능
- **대응**:
  - 백업 전 디스크 용량 확인 (`df -h`)
  - 백업 스크립트 실행 로그 확인
  - 백업 파일 검증 (`backup_system.py verify`)

#### 10.2.2 복구 실패 시나리오

- **원인**: 백업 파일 손상, DB URL 오류, Foreign Key 순서 오류
- **영향**: 일부 데이터 복구 실패, DB 불일치 상태
- **대응**:
  - 백업 파일 해시 체크 (무결성 검증)
  - pg_restore 로그 확인 (에러 메시지)
  - 복구 후 `/api/integrity/check` 실행

#### 10.2.3 샘플 데이터 투입 중 실패

- **원인**: FK 제약 위반, Unique 제약 위반, OOM (메모리 부족)
- **영향**: 일부 샘플 데이터만 투입, DB 불완전 상태
- **대응**:
  - 트랜잭션 사용 (BEGIN; ... COMMIT; 또는 ROLLBACK;)
  - 에러 로그 확인 후 재시도
  - 전체 롤백 후 백업 복구

### 10.3 성능 저하 요인

#### 10.3.1 대량 INSERT 성능 이슈

- **원인**: 100+ 건 documents, 300+ 건 chunks, 500+ 건 knowledge_labels 동시 INSERT
- **영향**: INSERT 소요 시간 증가 (단건 INSERT: 수 초 → 배치 INSERT: 수십 초)
- **대응**:
  - SQLAlchemy bulk_insert_mappings() 사용
  - 단건 INSERT 대신 배치 INSERT (예: 100행 단위)
  - INDEX 임시 비활성화 (INSERT 후 재생성)

#### 10.3.2 Qdrant 임베딩 병목

- **원인**: 300+ 청크에 대한 임베딩 생성 (Ollama API 호출)
- **영향**: 샘플 데이터 투입 시간 증가 (1청크당 0.5초 = 총 150초)
- **대응**:
  - 임베딩 병렬 처리 (asyncio, 동시 5~10개)
  - 고정 임베딩 벡터 사용 (테스트용, 랜덤 벡터)
  - Qdrant 투입은 선택적 (7단계, 4.7 참조)

#### 10.3.3 GIN 인덱스 재구성 시간

- **원인**: knowledge_chunks.content GIN 인덱스 (Phase 12-2-3)
- **영향**: 대량 INSERT 후 인덱스 재구성 (약 10~30초)
- **대응**:
  - 인덱스 비활성화 후 INSERT → 재생성

```sql
DROP INDEX IF EXISTS idx_knowledge_chunks_content_gin;
-- ... 샘플 데이터 INSERT ...
CREATE INDEX idx_knowledge_chunks_content_gin ON knowledge_chunks USING gin(to_tsvector('english', content));
```

### 10.4 보안 리스크

#### 10.4.1 SQL Injection 위험

- **원인**: 샘플 데이터 생성 시 사용자 입력 또는 외부 파일 내용 직접 SQL 문자열 조합
- **영향**: 악의적인 SQL 실행 가능
- **대응**:
  - SQLAlchemy ORM 사용 (parameterized query 자동)
  - 파일 내용 sanitize (`backend/utils/validation.py` 활용)
  - raw SQL 사용 금지 (f-string + SQL)

#### 10.4.2 민감 정보 노출

- **원인**: 샘플 데이터에 실제 API Key, 비밀번호 포함 가능
- **영향**: 보안 취약점
- **대응**:
  - 샘플 데이터는 고정 시드 또는 Faker 사용 (실제 민감 정보 배제)
  - 로컬 .md 파일 스캔 시 credential 필터링

#### 10.4.3 권한 오류

- **원인**: PostgreSQL 사용자 권한 부족 (CREATE, INSERT, ALTER)
- **영향**: 샘플 데이터 투입 실패
- **대응**:
  - DB URL 확인 (`backend/config.py`)
  - PostgreSQL 사용자 권한 점검

```sql
GRANT ALL PRIVILEGES ON DATABASE knowledge TO brain;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO brain;
```

### 10.5 롤백 실패 리스크

#### 10.5.1 백업 없이 진행

- **리스크**: 복구 불가능, 기존 데이터 손실
- **대응**: **백업 필수 (8.1)**, 프로덕션 DB 대상 시 이중 백업 (로컬 + 원격)

#### 10.5.2 Cascade 삭제 오류

- **리스크**: Project 삭제 시 연쇄 삭제로 의도하지 않은 데이터 삭제
- **대응**:
  - Cascade 설정 확인 (`cascade="all, delete-orphan"`)
  - 샘플 데이터는 별도 project_id로 분리
  - 삭제 전 관련 레코드 수 확인

```sql
-- 삭제 시뮬레이션 (DRY RUN)
BEGIN;
DELETE FROM projects WHERE name = 'SAMPLE_DATA';
SELECT COUNT(*) FROM documents;  -- 기대값과 일치?
ROLLBACK;  -- 롤백
```

#### 10.5.3 부분 복구 시 데이터 불일치

- **리스크**: PostgreSQL은 복구했지만 Qdrant는 복구 안 됨
- **대응**:
  - 전체 복구 우선 (PostgreSQL + Qdrant 동시)
  - 복구 후 `/api/integrity/check` 실행
  - 수동 재색인 (`POST /api/knowledge/reindex`)

---

## 11. 샘플 데이터 투입 작업 지침 (최종)

### 11.1 사전 준비 체크리스트

- [ ] **백업 완료**: `python scripts/devtool/backup_system.py backup --type full` 실행
- [ ] **백업 검증**: `backup_system.py verify --name <backup_name>` 성공
- [ ] **디스크 용량 확인**: 최소 500MB 여유 공간
- [ ] **DB 권한 확인**: PostgreSQL 사용자 권한 (CREATE, INSERT, ALTER)
- [ ] **Docker 서비스 확인**: PostgreSQL, Qdrant 컨테이너 실행 중
- [ ] **API 서버 중지** (선택): Backend API 중지하여 동시 쓰기 방지

### 11.2 샘플 데이터 투입 순서

1. **1단계: .md 인벤토리 생성** (분석만, DB 변경 없음)
   - `python scripts/db/analyze_md_files.py --output docs/planning/260210-1400-md-inventory-by-category.md`
   - 목표: development/planning/review/rules/ai 카테고리별 .md 파일 목록 확인

2. **2단계: Projects, Labels 시드** (필수)
   - `python scripts/db/seed_sample_data.py --step projects_labels --target 100`
   - 검증: `SELECT COUNT(*) FROM projects;` (5~10), `SELECT COUNT(*) FROM labels;` (100+)

3. **3단계: Documents 시드** (100+ 건)
   - `python scripts/db/seed_sample_data.py --step documents --target 100`
   - 검증: `SELECT COUNT(*) FROM documents WHERE project_id IS NOT NULL;` (100+)

4. **4단계: Knowledge Chunks, Knowledge Labels** (300+, 500+ 건)
   - `python scripts/db/seed_sample_data.py --step chunks_labels --target 300`
   - 검증: `SELECT COUNT(*) FROM knowledge_chunks;` (300+), `SELECT COUNT(*) FROM knowledge_labels;` (500+)

5. **5단계: Memories, Conversations, Reasoning Results** (각 100+ 건)
   - `python scripts/db/seed_sample_data.py --step cognitive --target 100`
   - 검증: 각 테이블 count ≥ 100

6. **6단계: Admin 설정 테이블** (templates 100+, prompt_presets 100+)
   - `python scripts/db/seed_sample_data.py --step admin --target 100`
   - 검증: `SELECT COUNT(*) FROM schemas.templates;` (100+)

7. **7단계: Audit Logs, Knowledge Relations** (각 100+, 50~200)
   - `python scripts/db/seed_sample_data.py --step audit_relations --target 100`

8. **8단계: Qdrant 임베딩** (선택, 시간 소요)
   - `python scripts/db/embed_sample_chunks.py --batch-size 10`

### 11.3 투입 후 검증

- [ ] **데이터 건수 확인**: 각 테이블 목표 건수 달성 (3.1 참조)
- [ ] **FK 제약조건 검증**: `GET /api/integrity/consistency` → `consistent: true`
- [ ] **Qdrant 동기화 검증**: `GET /api/integrity/sync` → `synced: true`
- [ ] **중복 데이터 확인**: labels (name, label_type) 중복 0건
- [ ] **데이터 품질 확인**: `SELECT MIN(LENGTH(content)) FROM knowledge_chunks;` (≥ 10)
- [ ] **API 동작 확인**: `/api/knowledge/search?query=test` (검색 결과 반환)

### 11.4 롤백 절차 (문제 발생 시)

1. **즉시 API 서버 중지**: `docker-compose stop backend`
2. **백업 복구 실행**: `python scripts/devtool/backup_system.py restore --name <backup_name>`
3. **Qdrant 복구 확인**: Qdrant 서비스 재시작 → 포인트 수 확인
4. **무결성 검증**: `GET /api/integrity/check` 실행
5. **에러 로그 분석**: 샘플 데이터 투입 스크립트 로그 확인
6. **수정 후 재시도**: FK 순서 오류 수정 → 재투입

### 11.5 프로덕션 적용 시 주의사항

- **개발/테스트 DB에서 먼저 검증**: 프로덕션 DB 적용 전 테스트 환경에서 전체 프로세스 검증
- **백업 주기**: 샘플 데이터 투입 전후 각각 백업 (롤백 옵션)
- **투입 시간**: 업무 시간 외 (새벽 또는 주말)
- **모니터링**: 투입 중 CPU, 메모리, 디스크 I/O 모니터링
- **점진적 투입**: 소량 투입 (10건) → 검증 → 전체 투입 (100+ 건)

---

## 12. 개발 완료 후 데이터 2차 검증 (Phase 14-6-5)

시드·권한·API 변경 등 **개발 완료 시점**에 데이터 정합성·품질을 재확인하기 위한 2차 검증을 수행한다. Phase 14 Master Plan의 **14-6-5** Task에 해당한다.

### 12.1 실행 시점

- 샘플 데이터 1차 시드·1차 검증(14-6-3) 완료 후
- Phase 14 권한·메뉴·API·UI 변경 등 개발 작업이 일단 완료된 후
- 배포 전 최종 데이터 품질 확인

### 12.2 검증 항목 (1차와 동일 + 회귀)

| # | 항목 | 방법 | 성공 기준 |
|---|------|------|-----------|
| 1 | **건수** | 각 테이블 COUNT 쿼리 | documents ≥ 100, knowledge_chunks ≥ 300, labels ≥ 100, knowledge_labels ≥ 500, templates·prompt_presets ≥ 100, audit_logs ≥ 100 등 (§3.1 목표 건수) |
| 2 | **FK·고아 레코드** | §9.2.1 검증 쿼리 또는 `GET /api/integrity/consistency` | 고아 0건 |
| 3 | **Qdrant 동기화** | `GET /api/integrity/sync` | PostgreSQL chunks 수 = Qdrant 포인트 수 (Qdrant 시드 적용 시) |
| 4 | **중복** | labels (name, label_type) unique 등 §9.2.3 | 중복 0건 |
| 5 | **데이터 품질** | knowledge_chunks content 최소 길이, 카테고리별 분포 §9.3 | MIN(LENGTH(content)) ≥ 10, 분포 이상 없음 |
| 6 | **회귀** | 1차 검증 대비 건수·정합성 변화 없음 (의도된 변경 제외) | 회귀 없음 또는 변경 사항 문서화 |

### 12.3 재검증 스크립트·리포트

- **스크립트**: `scripts/db/validate_sample_data.py` (또는 동일 검증 로직)를 **2차 검증 전용** 실행. 옵션 예: `--phase second` 또는 `--report validation_report_2nd.md`.
- **리포트**: 검증 일시, 항목별 Pass/Fail, 건수·에러 요약, 실패 시 원인·조치를 기록한 문서(예: `docs/planning/260210-1400-validation-report-2nd.md`).
- **성공 기준**: 위 12.2 항목 모두 Pass. 1건이라도 Fail 시 원인 해소 후 재실행.

### 12.4 Task 체크리스트 (14-6-5)

- [ ] 2차 검증 실행 시점 확정 (개발 완료 또는 배포 전).
- [ ] 재검증 스크립트 실행 (`validate_sample_data.py --phase second` 등).
- [ ] 리포트 생성·보관.
- [ ] 성공 기준 충족 확인. 미충족 시 수정 후 재검증.

---

**문서 상태**: 분석·전략 + 백업/복구/검증 최종 지침. Phase 14 가이드(14-6)와 연동·호환. 개발 완료 후 데이터 2차 검증(§12) 반영.
**파일명**: YYMMDD-HHMM 형식 — 260210-1400-db-sample-data-and-high-level-strategy.md  
**Phase 14 연동**: [phase-14-master-plan-guide.md](../phases/phase-14-master-plan-guide.md) §5.2·§8.5·§8.7 — 14-6 블록 및 14-6-5(2차 검증) Task.  
**관련**:

- backend/models/models.py, backend/models/admin_models.py
- scripts/devtool/backup_system.py (백업/복구)
- backend/services/system/integrity_service.py (무결성 검증)
- docs/phases/phase-14-master-plan-guide.md (Phase 14 14-6 Task·참고 문서 링크)
- docs/planning/\*.md, Phase 12-2-3 GIN 인덱스
