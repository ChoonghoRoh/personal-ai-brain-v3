# Task 9-3-3: RAG 기능 강화

**우선순위**: 1 (Phase 9-3 내 최우선, 기반 작업)
**예상 작업량**: 3일
**의존성**: 없음
**상태**: ⏳ 대기

---

## 1. 개요

### 1.1 목표
현재 단순 벡터 검색 기반 RAG를 Hybrid Search, Reranking, Context 최적화로 업그레이드하여 검색 정확도와 응답 품질 향상

### 1.2 현재 상태 분석
| 항목 | 현재 | 목표 |
|------|------|------|
| 검색 방식 | 벡터 검색만 | Hybrid (키워드 + 벡터) |
| 결과 정렬 | 유사도 순 | Reranking 적용 |
| 컨텍스트 | 고정 1000자 | 동적 + 압축 |
| 검색 깊이 | Single-hop | Multi-hop 지원 |

---

## 2. 파일 변경 계획

### 2.1 신규 생성 파일

| 파일 경로 | 용도 | 우선순위 |
|----------|------|----------|
| `backend/services/search/hybrid_search.py` | Hybrid Search 서비스 | 1 |
| `backend/services/search/reranker.py` | Reranking 서비스 | 2 |
| `backend/services/ai/context_manager.py` | 컨텍스트 관리 서비스 | 3 |
| `backend/services/search/multi_hop_rag.py` | Multi-hop RAG 서비스 | 4 |
| `tests/test_hybrid_search.py` | Hybrid Search 테스트 | 5 |
| `tests/test_rag_enhancement.py` | RAG 통합 테스트 | 6 |

### 2.2 수정 파일

| 파일 경로 | 수정 내용 | 영향도 |
|----------|----------|--------|
| `backend/services/search/search_service.py` | Hybrid Search 통합, 인터페이스 확장 | 높음 |
| `backend/services/search/__init__.py` | 새 모듈 export 추가 | 낮음 |
| `backend/services/ai/__init__.py` | context_manager 모듈 추가 | 낮음 |
| `backend/routers/ai/ai.py` | 개선된 RAG 파이프라인 적용 | 높음 |
| `backend/routers/search/search.py` | Hybrid Search 옵션 추가 | 중간 |
| `backend/config.py` | RAG 관련 설정 상수 추가 | 낮음 |
| `requirements.txt` | 필요 라이브러리 추가 | 낮음 |

### 2.3 삭제 파일
- 없음 (기존 기능 유지하며 확장)

---

## 3. 개발 순서 (우선순위별)

### Step 1: Hybrid Search 구현 (1일)

#### 1-1. PostgreSQL Full-text Search 설정
```
작업 내용:
- knowledge_chunks 테이블에 tsvector 컬럼 추가 고려
- 또는 LIKE/ILIKE 기반 간단한 키워드 검색 구현
- GIN 인덱스 설정 (성능 최적화)

주의사항:
- 기존 테이블 스키마 변경 최소화
- 마이그레이션 스크립트 필요시 작성
```

#### 1-2. hybrid_search.py 서비스 구현
```
구현할 클래스/함수:
- class HybridSearchService
- def search_hybrid(query, top_k, semantic_weight, keyword_weight)
- def semantic_search(query, top_k) - 기존 Qdrant 검색 래핑
- def keyword_search(query, top_k) - PostgreSQL 검색
- def fuse_results(semantic, keyword, weights) - RRF 결합

의존성:
- SearchService (기존)
- SQLAlchemy Session
- Qdrant Client
```

#### 1-3. 기존 SearchService 통합
```
수정 내용:
- search() 메서드에 search_mode 파라미터 추가
- search_mode: "semantic" | "keyword" | "hybrid"
- 기본값은 "semantic" (하위 호환성)
```

---

### Step 2: Reranking 구현 (0.5일)

#### 2-1. reranker.py 서비스 구현
```
구현할 클래스/함수:
- class Reranker
- def rerank(query, candidates, top_k)
- def _compute_relevance_score(query, document)

모델 선택:
- 옵션 1: cross-encoder/ms-marco-MiniLM-L-6-v2 (가벼움)
- 옵션 2: LLM 기반 점수 매기기 (비용 주의)
- 권장: 옵션 1 (sentence-transformers 활용)

주의사항:
- 모델 로딩 시간 고려 (싱글톤 또는 lazy loading)
- 배치 처리로 성능 최적화
```

---

### Step 3: Context Manager 구현 (0.5일)

#### 3-1. context_manager.py 서비스 구현
```
구현할 클래스/함수:
- class ContextManager
- def build_context(question, search_results, max_tokens)
- def analyze_question_complexity(question) -> "simple" | "complex"
- def compress_context(content, question, max_length)
- def extract_relevant_sentences(content, question)

컨텍스트 크기 결정 로직:
- 단순 질문: 500~800 토큰
- 복잡한 질문: 1500~2000 토큰
- 복잡도 판단: 질문 길이, 키워드 수, 질문 유형

주의사항:
- 토큰 수 정확히 계산 (tiktoken 또는 근사치)
- 문장 단위 추출로 의미 보존
```

---

### Step 4: Multi-hop RAG 구현 (0.5일)

#### 4-1. multi_hop_rag.py 서비스 구현
```
구현할 클래스/함수:
- class MultiHopRAG
- def search(question, max_hops)
- def _initial_search(question)
- def _follow_relations(chunk_ids)
- def _additional_search(context)

Multi-hop 로직:
- Hop 1: 초기 검색 (top_k=5)
- Hop 2: 관계 추적 (KnowledgeRelation 활용)
- Hop 3: 추가 검색 (필요시)

반환값:
- chunks: 최종 청크 목록
- hop_trace: 각 hop별 검색 경로 (디버깅용)

주의사항:
- 무한 루프 방지 (visited 체크)
- 최대 hop 수 제한 (기본 2)
```

---

### Step 5: AI 라우터 통합 (0.5일)

#### 5-1. ai.py 라우터 수정
```
수정 내용:
- prepare_question_context() 함수 개선
  - HybridSearchService 사용
  - Reranker 적용
  - ContextManager로 컨텍스트 구성

- 새 파라미터 추가 (선택적):
  - search_mode: "semantic" | "hybrid"
  - use_reranking: bool
  - use_multihop: bool

주의사항:
- 기존 API 호환성 유지
- 새 파라미터는 기본값으로 기존 동작 유지
```

---

### Step 6: 테스트 및 검증 (0.5일)

#### 6-1. 단위 테스트 작성
```
테스트 파일: tests/test_hybrid_search.py

테스트 케이스:
- test_semantic_search_only
- test_keyword_search_only
- test_hybrid_search_fusion
- test_reranking_improves_relevance
- test_context_compression
- test_multihop_follows_relations
```

#### 6-2. 통합 테스트 작성
```
테스트 파일: tests/test_rag_enhancement.py

테스트 케이스:
- test_ask_api_with_hybrid_search
- test_ask_api_quality_improvement
- test_ask_api_backwards_compatible
```

---

## 4. 개발 주의사항

### 4.1 코드 품질 기준

| 항목 | 기준 |
|------|------|
| 타입 힌트 | 모든 함수/메서드에 적용 |
| Docstring | 모든 클래스/함수에 작성 |
| 에러 처리 | try-except로 graceful 처리 |
| 로깅 | 주요 동작에 logger 사용 |
| 테스트 | 각 함수별 최소 2개 테스트 케이스 |

### 4.2 성능 기준

| 항목 | 기준 |
|------|------|
| Hybrid Search 응답 시간 | < 500ms (top_k=10 기준) |
| Reranking 추가 시간 | < 200ms (10개 문서 기준) |
| 메모리 사용량 | 기존 대비 +20% 이내 |

### 4.3 품질 통과 기준

| 항목 | 통과 기준 |
|------|----------|
| 단위 테스트 | 100% 통과 |
| 통합 테스트 | 100% 통과 |
| 기존 테스트 | 영향 없음 (100% 통과) |
| RAG 정확도 | 샘플 질문 10개 중 8개 이상 적절한 응답 |
| API 호환성 | 기존 클라이언트 정상 동작 |

### 4.4 주의사항 체크리스트

- [ ] 기존 SearchService 인터페이스 변경 시 하위 호환성 확인
- [ ] Reranker 모델 로딩 시간 측정 및 최적화
- [ ] PostgreSQL 인덱스 추가 시 마이그레이션 계획
- [ ] 메모리 사용량 모니터링 (특히 Reranker 모델)
- [ ] 에러 발생 시 기존 검색으로 폴백 로직
- [ ] 설정값 (weight, threshold 등) 환경변수로 관리

---

## 5. 설정 추가 항목

### 5.1 config.py 추가 상수
```python
# RAG Enhancement 설정
HYBRID_SEARCH_SEMANTIC_WEIGHT = 0.7
HYBRID_SEARCH_KEYWORD_WEIGHT = 0.3
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
RERANKER_ENABLED = True
CONTEXT_MAX_TOKENS_SIMPLE = 800
CONTEXT_MAX_TOKENS_COMPLEX = 2000
MULTIHOP_MAX_DEPTH = 2
```

### 5.2 requirements.txt 추가
```
# RAG Enhancement (Phase 9-3-3)
# cross-encoder 모델은 sentence-transformers에 포함
```

---

## 6. Pydantic 모델 정의

### 6.1 Hybrid Search 관련 모델
```python
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class SearchMode(str, Enum):
    SEMANTIC = "semantic"
    KEYWORD = "keyword"
    HYBRID = "hybrid"

class SearchResultItem(BaseModel):
    """개별 검색 결과 아이템"""
    chunk_id: int
    content: str
    score: float = Field(ge=0.0, le=1.0, description="정규화된 점수 (0~1)")
    source: str = Field(description="검색 소스: semantic | keyword | hybrid")
    document_id: Optional[int] = None
    document_name: Optional[str] = None

class HybridSearchRequest(BaseModel):
    """Hybrid Search 요청"""
    query: str = Field(min_length=1, description="검색 쿼리")
    top_k: int = Field(default=10, ge=1, le=100)
    search_mode: SearchMode = Field(default=SearchMode.HYBRID)
    semantic_weight: float = Field(default=0.7, ge=0.0, le=1.0)
    keyword_weight: float = Field(default=0.3, ge=0.0, le=1.0)
    project_id: Optional[int] = None
    label_ids: Optional[List[int]] = None

class HybridSearchResponse(BaseModel):
    """Hybrid Search 응답"""
    results: List[SearchResultItem]
    total: int
    search_mode: SearchMode
    query: str
```

### 6.2 Reranking 관련 모델
```python
class RerankedItem(BaseModel):
    """Reranking 후 결과 아이템"""
    chunk_id: int
    content: str
    original_score: float = Field(description="원본 검색 점수")
    rerank_score: float = Field(description="Reranking 점수")
    final_score: float = Field(description="최종 결합 점수")

class RerankRequest(BaseModel):
    """Reranking 요청"""
    query: str
    candidates: List[SearchResultItem]
    top_k: int = Field(default=5, ge=1, le=50)

class RerankResponse(BaseModel):
    """Reranking 응답"""
    results: List[RerankedItem]
    model_used: str = Field(default="cross-encoder/ms-marco-MiniLM-L-6-v2")
```

### 6.3 Context Manager 관련 모델
```python
class QuestionComplexity(str, Enum):
    SIMPLE = "simple"
    COMPLEX = "complex"

class ContextChunk(BaseModel):
    """컨텍스트에 포함된 청크"""
    chunk_id: int
    content: str
    relevance_score: float
    included_sentences: Optional[List[str]] = Field(
        default=None,
        description="압축 시 추출된 문장들"
    )

class ContextBuildRequest(BaseModel):
    """컨텍스트 구성 요청"""
    question: str
    search_results: List[SearchResultItem]
    max_tokens: Optional[int] = Field(default=None, description="None이면 자동 결정")

class ContextBuildResponse(BaseModel):
    """컨텍스트 구성 응답"""
    context: str = Field(description="LLM에 전달할 최종 컨텍스트")
    chunks_used: List[ContextChunk]
    question_complexity: QuestionComplexity
    total_tokens: int
    compressed: bool = Field(description="압축 적용 여부")
```

### 6.4 Multi-hop RAG 관련 모델
```python
class HopTrace(BaseModel):
    """각 Hop의 추적 정보"""
    hop_number: int
    action: str = Field(description="search | follow_relation | additional")
    chunk_ids_found: List[int]
    query_used: Optional[str] = None
    relation_type_followed: Optional[str] = None

class MultiHopRequest(BaseModel):
    """Multi-hop RAG 요청"""
    question: str
    max_hops: int = Field(default=2, ge=1, le=5)
    initial_top_k: int = Field(default=5, ge=1, le=20)
    project_id: Optional[int] = None

class MultiHopResponse(BaseModel):
    """Multi-hop RAG 응답"""
    chunks: List[SearchResultItem]
    hop_trace: List[HopTrace] = Field(description="검색 경로 추적 (디버깅용)")
    total_hops_executed: int
```

### 6.5 통합 RAG 파이프라인 모델
```python
class EnhancedRAGRequest(BaseModel):
    """개선된 RAG 파이프라인 요청 (AI 라우터용)"""
    question: str
    project_id: Optional[int] = None
    label_ids: Optional[List[int]] = None
    search_mode: SearchMode = Field(default=SearchMode.HYBRID)
    use_reranking: bool = Field(default=True)
    use_multihop: bool = Field(default=False)
    max_context_tokens: Optional[int] = None

class EnhancedRAGResponse(BaseModel):
    """개선된 RAG 파이프라인 응답"""
    context: str
    context_chunks: List[ContextChunk]
    search_metadata: dict = Field(description="검색 과정 메타데이터")
```

---

## 7. 다음 Task 연계

### 완료 후 영향
- **9-3-1 (Reasoning 추천)**: HybridSearch, ContextManager 활용 가능
- **9-3-2 (지식구조 매칭)**: 유사 청크 검색에 개선된 검색 사용

### 전달 사항
- HybridSearchService 사용법 문서화
- Reranker 성능 벤치마크 결과
- Context 압축 로직 설명

---

## 7. 참고 자료

- 현재 SearchService: `backend/services/search/search_service.py`
- 현재 AI 라우터: `backend/routers/ai/ai.py`
- Qdrant 설정: `backend/config.py`
- 관계 모델: `backend/models/models.py` (KnowledgeRelation)
