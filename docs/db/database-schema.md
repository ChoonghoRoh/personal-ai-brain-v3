# 데이터베이스 스키마 문서

**데이터베이스**: `knowledge`  
**PostgreSQL 버전**: 15.15  
**생성일**: 2026-01-27  
**마지막 업데이트**: 2026-01-27

## 목차

1. [개요](#개요)
2. [테이블 목록](#테이블-목록)
3. [테이블 상세 구조](#테이블-상세-구조)
4. [외래키 관계](#외래키-관계)
5. [인덱스 목록](#인덱스-목록)
6. [ERD 다이어그램](#erd-다이어그램)

---

## 개요

Personal AI Brain 시스템의 지식 관리 데이터베이스 스키마입니다. 총 **9개의 테이블**로 구성되어 있으며, 프로젝트, 문서, 지식 청크, 라벨, 관계, 기억, 대화, 추론 결과 등을 관리합니다.

### 주요 기능 영역

- **프로젝트 관리**: `projects`, `documents`
- **지식 관리**: `knowledge_chunks`, `knowledge_labels`, `knowledge_relations`
- **라벨 시스템**: `labels`
- **기억 시스템**: `memories`
- **대화 기록**: `conversations`
- **추론 결과**: `reasoning_results`

---

## 테이블 목록

| 테이블명 | 설명 | 레코드 수 (예상) |
|---------|------|----------------|
| `projects` | 프로젝트 정보 | 6 |
| `documents` | 문서 메타데이터 | 90 |
| `knowledge_chunks` | 지식 청크 | 425 |
| `labels` | 라벨 정의 | - |
| `knowledge_labels` | 청크-라벨 관계 | - |
| `knowledge_relations` | 청크 간 관계 | - |
| `memories` | 기억 시스템 | - |
| `conversations` | 대화 기록 | - |
| `reasoning_results` | 추론 결과 | - |

---

## 테이블 상세 구조

### 1. projects

프로젝트 정보를 저장하는 테이블입니다.

| 컬럼명 | 데이터 타입 | NULL 허용 | 기본값 | 설명 |
|--------|------------|----------|--------|------|
| `id` | INTEGER | NO | `nextval('projects_id_seq'::regclass)` | 기본키 (자동 증가) |
| `name` | VARCHAR | NO | - | 프로젝트 이름 (고유) |
| `path` | VARCHAR | NO | - | 프로젝트 경로 |
| `description` | TEXT | YES | - | 프로젝트 설명 |
| `created_at` | TIMESTAMP | YES | - | 생성 시간 |
| `updated_at` | TIMESTAMP | YES | - | 수정 시간 |

**제약조건:**
- PRIMARY KEY: `id`
- UNIQUE: `name`

**인덱스:**
- `projects_pkey` (PRIMARY KEY)
- `ix_projects_id`
- `ix_projects_name` (UNIQUE)

**관계:**
- `documents.project_id` → `projects.id` (1:N)

---

### 2. documents

문서 메타데이터를 저장하는 테이블입니다.

| 컬럼명 | 데이터 타입 | NULL 허용 | 기본값 | 설명 |
|--------|------------|----------|--------|------|
| `id` | INTEGER | NO | `nextval('documents_id_seq'::regclass)` | 기본키 (자동 증가) |
| `project_id` | INTEGER | YES | - | 프로젝트 ID (외래키) |
| `file_path` | VARCHAR | NO | - | 파일 경로 (고유) |
| `file_name` | VARCHAR | NO | - | 파일명 |
| `file_type` | VARCHAR | NO | - | 파일 타입 (md, pdf, docx 등) |
| `size` | INTEGER | NO | - | 파일 크기 (바이트) |
| `qdrant_collection` | VARCHAR | YES | - | Qdrant 컬렉션명 |
| `category_label_id` | INTEGER | YES | - | 카테고리 라벨 ID (외래키) |
| `created_at` | TIMESTAMP | YES | - | 생성 시간 |
| `updated_at` | TIMESTAMP | YES | - | 수정 시간 |

**제약조건:**
- PRIMARY KEY: `id`
- FOREIGN KEY: `project_id` → `projects.id`
- FOREIGN KEY: `category_label_id` → `labels.id`
- UNIQUE: `file_path`

**인덱스:**
- `documents_pkey` (PRIMARY KEY)
- `ix_documents_id`
- `ix_documents_file_path` (UNIQUE)
- `idx_documents_category_label_id`

**관계:**
- `documents.project_id` → `projects.id` (N:1)
- `documents.category_label_id` → `labels.id` (N:1)
- `knowledge_chunks.document_id` → `documents.id` (1:N)

---

### 3. knowledge_chunks

지식 청크(문서의 작은 단위)를 저장하는 테이블입니다.

| 컬럼명 | 데이터 타입 | NULL 허용 | 기본값 | 설명 |
|--------|------------|----------|--------|------|
| `id` | INTEGER | NO | `nextval('knowledge_chunks_id_seq'::regclass)` | 기본키 (자동 증가) |
| `document_id` | INTEGER | NO | - | 문서 ID (외래키) |
| `chunk_index` | INTEGER | NO | - | 청크 인덱스 (문서 내 순서) |
| `content` | TEXT | NO | - | 청크 내용 |
| `qdrant_point_id` | VARCHAR | YES | - | Qdrant 포인트 ID |
| `embedding_model` | VARCHAR | YES | - | 임베딩 모델명 |
| `status` | VARCHAR | NO | `'draft'` | 상태 (draft, approved, rejected) |
| `source` | VARCHAR | NO | `'human_created'` | 생성 소스 (ai_generated, human_created) |
| `approved_at` | TIMESTAMP | YES | - | 승인 시간 |
| `approved_by` | VARCHAR | YES | - | 승인자 |
| `version` | INTEGER | NO | `1` | 버전 |
| `title` | VARCHAR | YES | - | 청크 제목 |
| `title_source` | VARCHAR | YES | - | 제목 출처 (heading, ai_extracted, manual) |
| `created_at` | TIMESTAMP | YES | - | 생성 시간 |
| `updated_at` | TIMESTAMP | YES | - | 수정 시간 |

**제약조건:**
- PRIMARY KEY: `id`
- FOREIGN KEY: `document_id` → `documents.id`

**인덱스:**
- `knowledge_chunks_pkey` (PRIMARY KEY)
- `ix_knowledge_chunks_id`
- `idx_knowledge_chunks_status`

**관계:**
- `knowledge_chunks.document_id` → `documents.id` (N:1)
- `knowledge_labels.chunk_id` → `knowledge_chunks.id` (1:N)
- `knowledge_relations.source_chunk_id` → `knowledge_chunks.id` (1:N)
- `knowledge_relations.target_chunk_id` → `knowledge_chunks.id` (1:N)
- `memories.related_chunk_id` → `knowledge_chunks.id` (1:N)

---

### 4. labels

라벨 정의를 저장하는 테이블입니다. 계층 구조를 지원합니다.

| 컬럼명 | 데이터 타입 | NULL 허용 | 기본값 | 설명 |
|--------|------------|----------|--------|------|
| `id` | INTEGER | NO | `nextval('labels_id_seq'::regclass)` | 기본키 (자동 증가) |
| `name` | VARCHAR | NO | - | 라벨 이름 |
| `label_type` | VARCHAR | NO | - | 라벨 타입 (keyword, keyword_group, category, project, domain, project_phase, role, importance 등) |
| `description` | TEXT | YES | - | 라벨 설명 |
| `parent_label_id` | INTEGER | YES | - | 부모 라벨 ID (자기 참조) |
| `color` | VARCHAR | YES | - | UI용 색상 정보 |
| `created_at` | TIMESTAMP | YES | - | 생성 시간 |
| `updated_at` | TIMESTAMP | YES | `CURRENT_TIMESTAMP` | 수정 시간 |

**제약조건:**
- PRIMARY KEY: `id`
- FOREIGN KEY: `parent_label_id` → `labels.id` (자기 참조)
- UNIQUE: `(name, label_type)` - 같은 이름의 라벨이 다른 타입으로 존재 가능

**인덱스:**
- `labels_pkey` (PRIMARY KEY)
- `ix_labels_id`
- `idx_labels_name`
- `idx_labels_label_type`
- `idx_labels_name_label_type`
- `idx_labels_parent_label_id`
- `labels_name_label_type_unique` (UNIQUE)

**관계:**
- `labels.parent_label_id` → `labels.id` (자기 참조, 계층 구조)
- `documents.category_label_id` → `labels.id` (1:N)
- `knowledge_labels.label_id` → `labels.id` (1:N)

---

### 5. knowledge_labels

지식 청크와 라벨의 관계를 저장하는 테이블입니다.

| 컬럼명 | 데이터 타입 | NULL 허용 | 기본값 | 설명 |
|--------|------------|----------|--------|------|
| `id` | INTEGER | NO | `nextval('knowledge_labels_id_seq'::regclass)` | 기본키 (자동 증가) |
| `chunk_id` | INTEGER | NO | - | 청크 ID (외래키) |
| `label_id` | INTEGER | NO | - | 라벨 ID (외래키) |
| `confidence` | DOUBLE PRECISION | YES | - | 신뢰도 (0.0 - 1.0) |
| `status` | VARCHAR | NO | `'confirmed'` | 상태 (suggested, confirmed, rejected) |
| `source` | VARCHAR | NO | `'human'` | 소스 (ai, human) |
| `created_at` | TIMESTAMP | YES | - | 생성 시간 |

**제약조건:**
- PRIMARY KEY: `id`
- FOREIGN KEY: `chunk_id` → `knowledge_chunks.id`
- FOREIGN KEY: `label_id` → `labels.id`

**인덱스:**
- `knowledge_labels_pkey` (PRIMARY KEY)
- `ix_knowledge_labels_id`
- `idx_knowledge_labels_status`

**관계:**
- `knowledge_labels.chunk_id` → `knowledge_chunks.id` (N:1)
- `knowledge_labels.label_id` → `labels.id` (N:1)

---

### 6. knowledge_relations

지식 청크 간의 관계를 저장하는 테이블입니다.

| 컬럼명 | 데이터 타입 | NULL 허용 | 기본값 | 설명 |
|--------|------------|----------|--------|------|
| `id` | INTEGER | NO | `nextval('knowledge_relations_id_seq'::regclass)` | 기본키 (자동 증가) |
| `source_chunk_id` | INTEGER | NO | - | 소스 청크 ID (외래키) |
| `target_chunk_id` | INTEGER | NO | - | 타겟 청크 ID (외래키) |
| `relation_type` | VARCHAR | NO | - | 관계 타입 (cause-of, result-of, refers-to, explains, evolved-from, risk-related-to 등) |
| `confidence` | DOUBLE PRECISION | YES | - | 신뢰도 (0.0 - 1.0) |
| `description` | TEXT | YES | - | 관계 설명 |
| `score` | DOUBLE PRECISION | YES | - | 유사도 점수 (AI 제안용) |
| `confirmed` | VARCHAR | NO | `'true'` | 확인 여부 (true, false) |
| `source` | VARCHAR | NO | `'human'` | 소스 (ai, human) |
| `created_at` | TIMESTAMP | YES | - | 생성 시간 |

**제약조건:**
- PRIMARY KEY: `id`
- FOREIGN KEY: `source_chunk_id` → `knowledge_chunks.id`
- FOREIGN KEY: `target_chunk_id` → `knowledge_chunks.id`

**인덱스:**
- `knowledge_relations_pkey` (PRIMARY KEY)
- `ix_knowledge_relations_id`

**관계:**
- `knowledge_relations.source_chunk_id` → `knowledge_chunks.id` (N:1)
- `knowledge_relations.target_chunk_id` → `knowledge_chunks.id` (N:1)

---

### 7. memories

기억 시스템 데이터를 저장하는 테이블입니다. (Phase 8.0.5)

| 컬럼명 | 데이터 타입 | NULL 허용 | 기본값 | 설명 |
|--------|------------|----------|--------|------|
| `id` | INTEGER | NO | `nextval('memories_id_seq'::regclass)` | 기본키 (자동 증가) |
| `memory_type` | VARCHAR | NO | - | 기억 타입 (long_term, short_term, working) |
| `content` | TEXT | NO | - | 기억 내용 |
| `importance_score` | DOUBLE PRECISION | NO | - | 중요도 점수 (0.0 - 1.0) |
| `category` | VARCHAR | YES | - | 카테고리 (principle, value, knowledge, conversation, context) |
| `related_chunk_id` | INTEGER | YES | - | 관련 청크 ID (외래키) |
| `meta_data` | TEXT | YES | - | 메타데이터 (JSON 문자열) |
| `access_count` | INTEGER | NO | - | 접근 횟수 |
| `last_accessed_at` | TIMESTAMP | YES | - | 마지막 접근 시간 |
| `expires_at` | TIMESTAMP | YES | - | 만료 시간 (단기 기억용) |
| `created_at` | TIMESTAMP | YES | - | 생성 시간 |
| `updated_at` | TIMESTAMP | YES | - | 수정 시간 |

**제약조건:**
- PRIMARY KEY: `id`
- FOREIGN KEY: `related_chunk_id` → `knowledge_chunks.id`

**인덱스:**
- `memories_pkey` (PRIMARY KEY)
- `ix_memories_id`
- `ix_memories_memory_type`
- `ix_memories_category`
- `ix_memories_related_chunk_id`

**관계:**
- `memories.related_chunk_id` → `knowledge_chunks.id` (N:1)

---

### 8. conversations

대화 기록을 저장하는 테이블입니다. (Phase 8.0.13)

| 컬럼명 | 데이터 타입 | NULL 허용 | 기본값 | 설명 |
|--------|------------|----------|--------|------|
| `id` | INTEGER | NO | `nextval('conversations_id_seq'::regclass)` | 기본키 (자동 증가) |
| `question` | TEXT | NO | - | 질문 |
| `answer` | TEXT | NO | - | 답변 |
| `sources` | TEXT | YES | - | 출처 (JSON 문자열) |
| `model_used` | VARCHAR | YES | - | 사용된 모델 정보 |
| `session_id` | VARCHAR | YES | - | 세션 ID |
| `meta_data` | TEXT | YES | - | 메타데이터 (JSON 문자열) |
| `created_at` | TIMESTAMP | YES | - | 생성 시간 |

**제약조건:**
- PRIMARY KEY: `id`

**인덱스:**
- `conversations_pkey` (PRIMARY KEY)
- `ix_conversations_id`
- `ix_conversations_created_at`
- `ix_conversations_session_id`

**관계:**
- 없음 (독립 테이블)

---

### 9. reasoning_results

추론 결과를 저장하는 테이블입니다. (Phase 8.0.15-4)

| 컬럼명 | 데이터 타입 | NULL 허용 | 기본값 | 설명 |
|--------|------------|----------|--------|------|
| `id` | INTEGER | NO | `nextval('reasoning_results_id_seq'::regclass)` | 기본키 (자동 증가) |
| `question` | TEXT | NO | - | 질문 |
| `answer` | TEXT | NO | - | 답변 |
| `reasoning_steps` | TEXT | YES | - | 추론 단계 (JSON 문자열) |
| `context_chunks` | TEXT | YES | - | 컨텍스트 청크 (JSON 문자열) |
| `relations` | TEXT | YES | - | 관계 (JSON 문자열) |
| `mode` | VARCHAR | YES | - | 추론 모드 |
| `session_id` | VARCHAR | YES | - | 세션 ID |
| `meta_data` | TEXT | YES | - | 메타데이터 (JSON 문자열) |
| `created_at` | TIMESTAMP | YES | - | 생성 시간 |

**제약조건:**
- PRIMARY KEY: `id`

**인덱스:**
- `reasoning_results_pkey` (PRIMARY KEY)
- `ix_reasoning_results_id`
- `ix_reasoning_results_created_at`
- `ix_reasoning_results_session_id`

**관계:**
- 없음 (독립 테이블)

---

## 외래키 관계

### 관계 다이어그램

```
projects (1) ──< (N) documents
  │
  └──< (N) documents.category_label_id ──> (1) labels
                                              │
                                              └──< (N) labels.parent_label_id (자기 참조)

documents (1) ──< (N) knowledge_chunks
                        │
                        ├──< (N) knowledge_labels
                        │         │
                        │         └──> (1) labels
                        │
                        ├──< (N) knowledge_relations.source_chunk_id
                        │
                        ├──< (N) knowledge_relations.target_chunk_id
                        │
                        └──< (N) memories.related_chunk_id
```

### 외래키 상세

| 테이블 | 컬럼 | 참조 테이블 | 참조 컬럼 | 설명 |
|--------|------|------------|----------|------|
| `documents` | `project_id` | `projects` | `id` | 문서가 속한 프로젝트 |
| `documents` | `category_label_id` | `labels` | `id` | 문서의 카테고리 라벨 |
| `knowledge_chunks` | `document_id` | `documents` | `id` | 청크가 속한 문서 |
| `knowledge_labels` | `chunk_id` | `knowledge_chunks` | `id` | 라벨이 붙은 청크 |
| `knowledge_labels` | `label_id` | `labels` | `id` | 라벨 정의 |
| `knowledge_relations` | `source_chunk_id` | `knowledge_chunks` | `id` | 관계의 소스 청크 |
| `knowledge_relations` | `target_chunk_id` | `knowledge_chunks` | `id` | 관계의 타겟 청크 |
| `labels` | `parent_label_id` | `labels` | `id` | 부모 라벨 (자기 참조) |
| `memories` | `related_chunk_id` | `knowledge_chunks` | `id` | 관련 청크 |

---

## 인덱스 목록

### Primary Key 인덱스

모든 테이블에 기본키 인덱스가 있습니다:
- `projects_pkey`
- `documents_pkey`
- `knowledge_chunks_pkey`
- `knowledge_labels_pkey`
- `knowledge_relations_pkey`
- `labels_pkey`
- `memories_pkey`
- `conversations_pkey`
- `reasoning_results_pkey`

### Unique 인덱스

- `ix_projects_name` - projects.name
- `ix_documents_file_path` - documents.file_path
- `labels_name_label_type_unique` - labels(name, label_type)

### 일반 인덱스

#### projects
- `ix_projects_id`

#### documents
- `ix_documents_id`
- `idx_documents_category_label_id`

#### knowledge_chunks
- `ix_knowledge_chunks_id`
- `idx_knowledge_chunks_status`

#### knowledge_labels
- `ix_knowledge_labels_id`
- `idx_knowledge_labels_status`

#### knowledge_relations
- `ix_knowledge_relations_id`

#### labels
- `ix_labels_id`
- `idx_labels_name`
- `idx_labels_label_type`
- `idx_labels_name_label_type`
- `idx_labels_parent_label_id`

#### memories
- `ix_memories_id`
- `ix_memories_memory_type`
- `ix_memories_category`
- `ix_memories_related_chunk_id`

#### conversations
- `ix_conversations_id`
- `ix_conversations_created_at`
- `ix_conversations_session_id`

#### reasoning_results
- `ix_reasoning_results_id`
- `ix_reasoning_results_created_at`
- `ix_reasoning_results_session_id`

---

## ERD 다이어그램

### 텍스트 기반 ERD

```
┌─────────────┐
│  projects   │
├─────────────┤
│ id (PK)     │
│ name (UQ)   │
│ path        │
│ description │
│ created_at  │
│ updated_at  │
└──────┬──────┘
       │ 1
       │
       │ N
┌──────▼──────┐      ┌──────────────┐
│  documents  │──────│    labels    │
├─────────────┤  N:1 │──────────────│
│ id (PK)     │      │ id (PK)      │
│ project_id  │      │ name         │
│ file_path   │      │ label_type   │
│ file_name   │      │ parent_id    │◄──┐
│ file_type   │      │ color        │   │
│ size        │      │ ...          │   │
│ category_   │      └──────────────┘   │
│   label_id  │                         │
│ ...         │                         │
└──────┬──────┘                         │
       │ 1                              │
       │                                │
       │ N                              │
┌──────▼──────────────┐                 │
│ knowledge_chunks    │                 │
├─────────────────────┤                 │
│ id (PK)             │                 │
│ document_id (FK)    │                 │
│ chunk_index         │                 │
│ content             │                 │
│ status              │                 │
│ title               │                 │
│ ...                 │                 │
└───┬──────────────┬──┘                 │
    │              │                    │
    │ N            │ N                  │
    │              │                    │
┌───▼──────┐  ┌───▼──────────┐         │
│knowledge │  │knowledge_    │         │
│_labels   │  │relations     │         │
├──────────┤  ├──────────────┤         │
│id (PK)   │  │id (PK)       │         │
│chunk_id  │  │source_chunk  │         │
│label_id  │  │target_chunk  │         │
│status    │  │relation_type │         │
│...       │  │...           │         │
└───┬──────┘  └──────────────┘         │
    │                                  │
    │ N                                │
    │                                  │
    └──────────────────────────────────┘
```

### 주요 관계 요약

1. **프로젝트 → 문서**: 1:N
2. **문서 → 청크**: 1:N
3. **청크 → 라벨**: N:M (knowledge_labels 중간 테이블)
4. **청크 → 관계**: N:N (knowledge_relations, 자기 참조)
5. **라벨 → 라벨**: 계층 구조 (자기 참조)
6. **문서 → 라벨**: N:1 (카테고리 라벨)
7. **청크 → 기억**: 1:N (memories)

---

## 데이터 타입 참고

### 주요 데이터 타입

- **INTEGER**: 정수 (기본키, 외래키, 숫자 값)
- **VARCHAR / CHARACTER VARYING**: 가변 길이 문자열
- **TEXT**: 무제한 텍스트
- **TIMESTAMP**: 날짜/시간 (타임존 없음)
- **DOUBLE PRECISION**: 배정밀도 부동소수점 (신뢰도, 점수 등)
- **BOOLEAN**: 불린 값 (일부 컬럼에서 사용 가능)

### 특수 값

- **SERIAL**: 자동 증가 정수 (기본키에 사용)
- **JSON 문자열**: `meta_data`, `sources`, `reasoning_steps` 등은 TEXT 타입에 JSON 문자열로 저장

---

## 스키마 버전 히스토리

### Phase 5.1
- 초기 스키마 생성 (projects, documents, knowledge_chunks)

### Phase 7.0
- Approval workflow 추가 (knowledge_chunks.status, source, approved_at, approved_by, version)
- AI suggestion workflow 추가 (knowledge_labels.status, source, knowledge_relations.confirmed, source)

### Phase 7.7
- 라벨 계층 구조 추가 (labels.parent_label_id, color, updated_at)
- 문서 카테고리 라벨 추가 (documents.category_label_id)

### Phase 7.9.5
- 청크 제목 필드 추가 (knowledge_chunks.title, title_source)

### Phase 8.0.5
- 기억 시스템 테이블 추가 (memories)

### Phase 8.0.13
- 대화 기록 테이블 추가 (conversations)

### Phase 8.0.15-4
- 추론 결과 테이블 추가 (reasoning_results)

---

## 유지보수 참고

### 스키마 확인 명령어

```bash
# 모든 테이블 목록
docker exec pab-postgres psql -U brain -d knowledge -c "\dt"

# 특정 테이블 구조 확인
docker exec pab-postgres psql -U brain -d knowledge -c "\d+ table_name"

# 외래키 확인
docker exec pab-postgres psql -U brain -d knowledge -c "
SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY';
"

# 인덱스 확인
docker exec pab-postgres psql -U brain -d knowledge -c "
SELECT tablename, indexname, indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;
"
```

### 스키마 변경 시 주의사항

1. **외래키 제약조건**: 테이블 삭제 시 CASCADE 옵션 확인
2. **인덱스 성능**: 큰 테이블에 인덱스 추가 시 `CONCURRENTLY` 옵션 고려
3. **데이터 마이그레이션**: 기존 데이터가 있는 경우 기본값 설정 필요
4. **트랜잭션**: 여러 변경사항은 트랜잭션으로 묶어서 실행

---

**문서 버전**: 1.0  
**최종 업데이트**: 2026-01-27
