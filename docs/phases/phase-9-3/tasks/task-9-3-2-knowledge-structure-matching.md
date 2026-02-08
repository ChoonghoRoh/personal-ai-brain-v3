# Task 9-3-2: Data Import/CRUD 지식구조 자동 매칭

**우선순위**: 3 (Phase 9-3 내 세 번째)
**예상 작업량**: 2.5일
**의존성**: Task 9-3-3 (RAG 기능 강화) 완료 후 진행
**상태**: ⏳ 대기

---

## 1. 개요

### 1.1 목표
데이터 생성/수정/승인 시 자동으로 지식 구조(라벨, 관계, 카테고리)를 추천하여 수동 작업 최소화

### 1.2 현재 상태 분석
| 항목 | 현재 | 목표 |
|------|------|------|
| 청크 생성 시 | 라벨 없음 (수동 추가) | 자동 라벨 추천 |
| 문서 생성 시 | 카테고리 수동 설정 | 자동 카테고리 추천 |
| 청크 승인 시 | 관계 수동 생성 | 관계 자동 제안 |
| 유사 문서 | 그룹핑 없음 | 자동 그룹핑 제안 |

### 1.3 현재 Import/CRUD 흐름
```
현재 파일:
- backend/routers/knowledge/knowledge.py (청크 CRUD)
- backend/routers/knowledge/labels.py (라벨 관리)
- backend/routers/knowledge/relations.py (관계 관리)
- backend/routers/knowledge/approval.py (승인 워크플로우)
- backend/routers/search/documents.py (문서 관리)

현재 흐름:
1. 문서 업로드 → 청크 생성 (라벨 없음)
2. 수동으로 라벨 추가 (/chunks/{id}/labels)
3. 수동으로 관계 생성 (/relations)
4. 수동으로 카테고리 설정 (/documents/{id}/category)
```

---

## 2. 파일 변경 계획

### 2.1 신규 생성 파일

| 파일 경로 | 용도 | 우선순위 |
|----------|------|----------|
| `backend/services/knowledge/structure_matcher.py` | 지식구조 매칭 서비스 | 1 |
| `backend/services/knowledge/auto_labeler.py` | 자동 라벨링 서비스 | 2 |
| `tests/test_structure_matching.py` | 자동 매칭 테스트 | 3 |

### 2.2 수정 파일

| 파일 경로 | 수정 내용 | 영향도 |
|----------|----------|--------|
| `backend/routers/knowledge/knowledge.py` | 청크 생성 응답에 추천 추가 | 높음 |
| `backend/routers/knowledge/approval.py` | 승인 시 관계 추천 반환 | 중간 |
| `backend/routers/search/documents.py` | 문서 생성 응답에 카테고리 추천 | 중간 |
| `backend/services/knowledge/__init__.py` | 새 서비스 export | 낮음 |
| `backend/config.py` | 자동 매칭 설정 상수 | 낮음 |

### 2.3 삭제 파일
- 없음

---

## 3. 개발 순서 (우선순위별)

### Step 1: StructureMatcher 서비스 구현 (1일)

#### 1-1. structure_matcher.py 기본 구조
```
구현할 클래스/함수:
- class StructureMatcher
  - __init__(db, hybrid_search, recommendation_service)

핵심 메서드:
- match_on_chunk_create(chunk) -> StructureMatchResult
- suggest_relations_on_approve(chunk) -> List[RelationSuggestion]
- find_similar_documents(document) -> List[SimilarDocument]
```

#### 1-2. match_on_chunk_create 구현
```
입력: KnowledgeChunk (새로 생성된 청크)

처리 로직:
1. 청크 content에서 키워드 추출
   - extract_keywords_from_markdown() 활용 (기존 함수)

2. 기존 Label과 키워드 매칭
   - Label.name ILIKE '%keyword%'
   - 또는 Label.name = keyword (정확 매칭)

3. HybridSearch로 유사 청크 검색 (9-3-3 활용)
   - 유사 청크들의 라벨 수집
   - 라벨 빈도 계산

4. 카테고리 추론
   - 문서 경로 분석 (docs/phases/ → development)
   - 유사 문서의 카테고리 참조

5. 결과 구성 및 반환

반환 형식 (StructureMatchResult):
{
    "suggested_labels": [
        {"label_id": int, "name": str, "confidence": float, "source": str}
    ],
    "similar_chunks": [
        {"chunk_id": int, "title": str, "similarity": float}
    ],
    "suggested_category": {
        "label_id": int, "name": str, "confidence": float
    }
}
```

#### 1-3. suggest_relations_on_approve 구현
```
입력: KnowledgeChunk (승인된 청크)

처리 로직:
1. 동일 문서 내 청크와의 관계 분석
   - 순서 관계 (previous/next)
   - 상위/하위 관계 (parent/child)

2. 유사 청크와의 의미 관계
   - HybridSearch로 유사 청크 검색
   - 유사도 > 0.8 → "related_to" 관계 제안

3. 동일 라벨 청크와의 관계
   - 같은 라벨 가진 다른 청크
   - "shares_topic" 관계 제안

4. 중복 관계 필터링
   - 이미 존재하는 KnowledgeRelation 제외

반환 형식 (List[RelationSuggestion]):
[
    {
        "source_chunk_id": int,
        "target_chunk_id": int,
        "relation_type": str,
        "confidence": float,
        "reason": str
    }
]
```

#### 1-4. find_similar_documents 구현
```
입력: Document (새로 생성된 문서)

처리 로직:
1. 문서의 모든 청크 수집
2. 각 청크의 유사 청크 검색
3. 유사 청크들의 document_id 수집
4. 문서별 유사도 점수 계산
5. 상위 N개 문서 반환

반환 형식 (List[SimilarDocument]):
[
    {
        "document_id": int,
        "file_name": str,
        "similarity": float,
        "shared_topics": List[str]
    }
]
```

---

### Step 2: AutoLabeler 서비스 구현 (0.5일)

#### 2-1. auto_labeler.py 구현
```
구현할 클래스/함수:
- class AutoLabeler
  - __init__(db, structure_matcher)

핵심 메서드:
- label_on_import(document, chunks) -> AutoLabelResult
- suggest_category(document) -> CategorySuggestion
- apply_suggested_labels(chunk_id, label_ids, auto_confirm) -> int
```

#### 2-2. label_on_import 구현
```
입력: Document, List[KnowledgeChunk]

처리 로직:
1. 문서 전체 분석 → 문서 레벨 라벨
   - 문서 제목/경로에서 추출

2. 각 청크별 StructureMatcher 호출
   - match_on_chunk_create() 활용

3. 라벨 통합 및 중복 제거
4. 신뢰도 기준 정렬

반환 형식 (AutoLabelResult):
{
    "document_labels": [...],
    "chunk_labels": {
        chunk_id: [...]
    },
    "suggested_category": {...},
    "total_suggestions": int
}
```

#### 2-3. suggest_category 구현
```
입력: Document

처리 로직:
1. 파일 경로 분석
   - docs/phases/ → "development"
   - brain/ → "knowledge"
   - backend/ → "code"

2. 컨텐츠 분석 (첫 번째 청크)
   - 키워드 기반 카테고리 매칭

3. 유사 문서 카테고리 참조
   - find_similar_documents() 활용
   - 가장 빈번한 카테고리

반환 형식 (CategorySuggestion):
{
    "label_id": int,
    "name": str,
    "label_type": "category",
    "confidence": float,
    "reason": str
}
```

---

### Step 3: 기존 API 확장 (0.5일)

#### 3-1. knowledge.py 수정 (청크 생성 API)
```
현재 POST /api/knowledge/chunks 응답:
{
    "id": int,
    "content": str,
    ...
}

변경 후 응답:
{
    "id": int,
    "content": str,
    ...,
    "structure_suggestions": {  # 새로 추가
        "suggested_labels": [...],
        "similar_chunks": [...],
        "suggested_category": {...}
    }
}

구현 방법:
- 청크 생성 후 StructureMatcher.match_on_chunk_create() 호출
- 결과를 응답에 포함
- 설정으로 자동 매칭 활성화/비활성화 가능
```

#### 3-2. approval.py 수정 (승인 API)
```
현재 POST /api/knowledge/approval 응답:
{
    "chunk_id": int,
    "status": str,
    ...
}

변경 후 응답:
{
    "chunk_id": int,
    "status": str,
    ...,
    "suggested_relations": [...]  # 새로 추가
}

구현 방법:
- 승인 처리 후 StructureMatcher.suggest_relations_on_approve() 호출
- status가 "approved"일 때만 관계 추천
```

#### 3-3. documents.py 수정 (문서 생성 API)
```
현재 POST /api/documents 응답:
{
    "id": int,
    "file_name": str,
    ...
}

변경 후 응답:
{
    "id": int,
    "file_name": str,
    ...,
    "suggestions": {  # 새로 추가
        "category": {...},
        "similar_documents": [...]
    }
}
```

---

### Step 4: 설정 및 옵션 (0.25일)

#### 4-1. config.py 설정 추가
```python
# 자동 매칭 설정
AUTO_STRUCTURE_MATCHING_ENABLED = True
AUTO_LABEL_MIN_CONFIDENCE = 0.5
AUTO_RELATION_MIN_CONFIDENCE = 0.7
AUTO_CATEGORY_MIN_CONFIDENCE = 0.6
MAX_LABEL_SUGGESTIONS = 10
MAX_RELATION_SUGGESTIONS = 5
MAX_SIMILAR_DOCUMENTS = 5
```

#### 4-2. API 옵션 파라미터
```
POST /api/knowledge/chunks
Query params:
- auto_suggest: bool (default: True)
- auto_apply_labels: bool (default: False)

POST /api/knowledge/approval
Query params:
- suggest_relations: bool (default: True)
```

---

### Step 5: 테스트 (0.25일)

#### 5-1. 단위 테스트
```
테스트 파일: tests/test_structure_matching.py

테스트 케이스:
- test_match_on_chunk_create_returns_labels
- test_match_on_chunk_create_finds_similar
- test_suggest_relations_excludes_existing
- test_suggest_relations_includes_document_relations
- test_suggest_category_from_path
- test_suggest_category_from_content
- test_auto_labeler_on_import
```

#### 5-2. API 테스트
```
테스트 케이스:
- test_create_chunk_includes_suggestions
- test_approve_chunk_includes_relations
- test_create_document_includes_category
- test_auto_suggest_disabled
```

---

## 4. 개발 주의사항

### 4.1 코드 품질 기준

| 항목 | 기준 |
|------|------|
| 타입 힌트 | 모든 함수/메서드에 적용 |
| Docstring | 모든 클래스/함수에 작성 |
| 에러 처리 | 매칭 실패 시 빈 결과 반환 (에러 아님) |
| 로깅 | 매칭 과정 및 결과 로깅 |
| 트랜잭션 | 자동 적용 시 트랜잭션 관리 |

### 4.2 성능 기준

| 항목 | 기준 |
|------|------|
| 청크 생성 시 추천 | 기존 응답 시간 + 500ms 이내 |
| 문서 생성 시 추천 | 기존 응답 시간 + 1초 이내 |
| 배치 Import (10개 청크) | < 5초 |

### 4.3 품질 통과 기준

| 항목 | 통과 기준 |
|------|----------|
| 단위 테스트 | 100% 통과 |
| API 테스트 | 100% 통과 |
| 기존 API 호환 | 기존 필드 모두 유지 |
| 라벨 추천 정확도 | 관련 라벨 60% 이상 |
| 관계 추천 정확도 | 유효한 관계 50% 이상 |

### 4.4 주의사항 체크리스트

- [ ] 기존 API 응답 필드 변경 없음 (추가만)
- [ ] 자동 매칭 비활성화 옵션 제공
- [ ] 대량 Import 시 성능 영향 최소화
- [ ] 추천 결과 없을 때 빈 배열 반환
- [ ] 순환 관계 방지 (A→B, B→A 중복 체크)
- [ ] 자기 참조 관계 방지 (A→A 금지)

---

## 5. API 엔드포인트 상세 스펙

### 5.1 POST /api/knowledge/chunks (기존 API 확장)
**용도**: 청크 생성 (structure_suggestions 필드 추가)

**Request Body** (기존과 동일)
```json
{
    "content": "# Phase 9 설계\n\n아키텍처 개선 계획...",
    "document_id": 1,
    "chunk_type": "markdown"
}
```

**Query Parameters** (신규 추가)
```
- auto_suggest: bool (optional, default=true) - 자동 추천 활성화
- auto_apply_labels: bool (optional, default=false) - 추천 라벨 자동 적용
```

**Response 200** (확장된 응답)
```json
{
    "id": 25,
    "content": "# Phase 9 설계\n\n아키텍처 개선 계획...",
    "document_id": 1,
    "chunk_type": "markdown",
    "status": "pending",
    "created_at": "2026-02-01T10:30:00Z",
    "structure_suggestions": {
        "suggested_labels": [
            {
                "label_id": 3,
                "name": "architecture",
                "label_type": "topic",
                "confidence": 0.88,
                "source": "keyword"
            },
            {
                "label_id": 7,
                "name": "planning",
                "label_type": "category",
                "confidence": 0.75,
                "source": "similar_chunk"
            }
        ],
        "similar_chunks": [
            {
                "chunk_id": 12,
                "title": "Phase 8 아키텍처",
                "similarity": 0.82
            },
            {
                "chunk_id": 18,
                "title": "시스템 설계 원칙",
                "similarity": 0.76
            }
        ],
        "suggested_category": {
            "label_id": 5,
            "name": "development",
            "confidence": 0.91,
            "reason": "파일 경로 분석: docs/phases/"
        }
    }
}
```

**Response 200** (auto_suggest=false 시)
```json
{
    "id": 25,
    "content": "...",
    "document_id": 1,
    "chunk_type": "markdown",
    "status": "pending",
    "created_at": "2026-02-01T10:30:00Z"
}
```
> structure_suggestions 필드 없음 (기존 응답 형식 유지)

---

### 5.2 POST /api/knowledge/approval (기존 API 확장)
**용도**: 청크 승인 (suggested_relations 필드 추가)

**Request Body** (기존과 동일)
```json
{
    "chunk_id": 25,
    "status": "approved",
    "comment": "검토 완료"
}
```

**Query Parameters** (신규 추가)
```
- suggest_relations: bool (optional, default=true) - 관계 추천 활성화
```

**Response 200** (확장된 응답, status="approved" 시)
```json
{
    "chunk_id": 25,
    "status": "approved",
    "approved_at": "2026-02-01T11:00:00Z",
    "approved_by": "user",
    "suggested_relations": [
        {
            "source_chunk_id": 25,
            "target_chunk_id": 12,
            "relation_type": "related_to",
            "confidence": 0.85,
            "reason": "유사한 아키텍처 주제 (similarity: 0.82)"
        },
        {
            "source_chunk_id": 25,
            "target_chunk_id": 20,
            "relation_type": "follows",
            "confidence": 0.78,
            "reason": "동일 문서 내 순서 관계"
        },
        {
            "source_chunk_id": 25,
            "target_chunk_id": 30,
            "relation_type": "shares_topic",
            "confidence": 0.72,
            "reason": "동일 라벨 공유: architecture"
        }
    ]
}
```

**Response 200** (status="rejected" 시)
```json
{
    "chunk_id": 25,
    "status": "rejected",
    "rejected_at": "2026-02-01T11:00:00Z",
    "comment": "내용 수정 필요"
}
```
> suggested_relations 필드 없음 (승인 시에만 제공)

---

### 5.3 POST /api/documents (기존 API 확장)
**용도**: 문서 생성 (suggestions 필드 추가)

**Request Body** (기존과 동일)
```json
{
    "file_name": "phase-9-design.md",
    "file_path": "/docs/phases/phase-9/",
    "content": "..."
}
```

**Response 200** (확장된 응답)
```json
{
    "id": 15,
    "file_name": "phase-9-design.md",
    "file_path": "/docs/phases/phase-9/",
    "created_at": "2026-02-01T10:00:00Z",
    "chunk_count": 5,
    "suggestions": {
        "category": {
            "label_id": 5,
            "name": "development",
            "label_type": "category",
            "confidence": 0.95,
            "reason": "파일 경로 분석: /docs/phases/"
        },
        "similar_documents": [
            {
                "document_id": 8,
                "file_name": "phase-8-design.md",
                "similarity": 0.78,
                "shared_topics": ["architecture", "planning"]
            },
            {
                "document_id": 10,
                "file_name": "system-overview.md",
                "similarity": 0.65,
                "shared_topics": ["architecture"]
            }
        ]
    }
}
```

---

### 5.4 POST /api/knowledge/chunks/{chunk_id}/labels/apply
**용도**: 추천 라벨 일괄 적용 (신규 API)

**Path Parameters**
```
- chunk_id: int (required) - 청크 ID
```

**Request Body**
```json
{
    "label_ids": [3, 7, 12],
    "auto_confirm": false
}
```

**Response 200**
```json
{
    "chunk_id": 25,
    "applied_labels": [
        {"label_id": 3, "name": "architecture"},
        {"label_id": 7, "name": "planning"}
    ],
    "skipped_labels": [
        {"label_id": 12, "reason": "already_exists"}
    ],
    "total_applied": 2
}
```

**Response 404**
```json
{
    "detail": "Chunk not found"
}
```

---

### 5.5 POST /api/knowledge/relations/apply
**용도**: 추천 관계 일괄 적용 (신규 API)

**Request Body**
```json
{
    "relations": [
        {
            "source_chunk_id": 25,
            "target_chunk_id": 12,
            "relation_type": "related_to"
        },
        {
            "source_chunk_id": 25,
            "target_chunk_id": 20,
            "relation_type": "follows"
        }
    ]
}
```

**Response 200**
```json
{
    "created_relations": [
        {
            "id": 50,
            "source_chunk_id": 25,
            "target_chunk_id": 12,
            "relation_type": "related_to"
        }
    ],
    "skipped_relations": [
        {
            "source_chunk_id": 25,
            "target_chunk_id": 20,
            "reason": "already_exists"
        }
    ],
    "total_created": 1
}
```

**Response 400**
```json
{
    "detail": "Self-referencing relation not allowed",
    "invalid_relation": {
        "source_chunk_id": 25,
        "target_chunk_id": 25
    }
}
```

---

### 5.6 공통 에러 응답

**400 Bad Request** (유효성 검사 실패)
```json
{
    "detail": "Validation error",
    "errors": [
        {
            "field": "label_ids",
            "message": "At least one label_id is required"
        }
    ]
}
```

**404 Not Found**
```json
{
    "detail": "Resource not found",
    "resource_type": "chunk",
    "resource_id": 999
}
```

**500 Internal Server Error**
```json
{
    "detail": "Structure matching failed",
    "error_code": "MATCHER_ERROR"
}
```

---

## 6. 의존성 활용

### 5.1 Task 9-3-3에서 가져올 것
- `HybridSearchService`: 유사 청크/문서 검색

### 5.2 Task 9-3-1에서 재사용 가능
- `RecommendationService.recommend_labels()` 로직 일부 공유

### 5.3 기존 코드 활용
```python
# 기존 키워드 추출 함수 활용
from backend.routers.knowledge.knowledge import extract_keywords_from_markdown

# 기존 검색 서비스 활용
from backend.services.search.search_service import SearchService
```

---

## 6. Pydantic 모델 정의

### 6.1 응답 모델
```python
# 추가할 Pydantic 모델

class LabelSuggestion(BaseModel):
    label_id: int
    name: str
    label_type: str
    confidence: float
    source: str  # "keyword" | "similar_chunk" | "path"

class ChunkSuggestion(BaseModel):
    chunk_id: int
    title: Optional[str]
    similarity: float

class CategorySuggestion(BaseModel):
    label_id: int
    name: str
    confidence: float
    reason: str

class RelationSuggestion(BaseModel):
    source_chunk_id: int
    target_chunk_id: int
    relation_type: str
    confidence: float
    reason: str

class StructureMatchResult(BaseModel):
    suggested_labels: List[LabelSuggestion]
    similar_chunks: List[ChunkSuggestion]
    suggested_category: Optional[CategorySuggestion]

class SimilarDocument(BaseModel):
    document_id: int
    file_name: str
    similarity: float
    shared_topics: List[str]
```

---

## 7. 참고 자료

- 현재 Knowledge API: `backend/routers/knowledge/knowledge.py`
- 현재 Labels API: `backend/routers/knowledge/labels.py`
- 현재 Relations API: `backend/routers/knowledge/relations.py`
- 현재 Approval API: `backend/routers/knowledge/approval.py`
- 모델 정의: `backend/models/models.py`
- 기존 키워드 추출: `extract_keywords_from_markdown()` in knowledge.py
