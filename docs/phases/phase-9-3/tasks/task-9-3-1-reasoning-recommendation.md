# Task 9-3-1: Reasoning AI 추천/샘플 기능 업그레이드

**우선순위**: 2 (Phase 9-3 내 두 번째)
**예상 작업량**: 3일
**의존성**: Task 9-3-3 (RAG 기능 강화) 완료 후 진행
**상태**: ⏳ 대기

---

## 1. 개요

### 1.1 목표
템플릿 기반 Reasoning을 LLM 기반 동적 추론으로 업그레이드하고, 관련 청크/라벨/질문 추천 기능 추가

### 1.2 현재 상태 분석
| 항목 | 현재 | 목표 |
|------|------|------|
| 추론 방식 | 템플릿 기반 고정 응답 | LLM 기반 동적 추론 |
| 관련 청크 추천 | 없음 | 유사도/관계 기반 추천 |
| 라벨 추천 | 없음 | 컨텍스트 기반 추천 |
| 샘플 질문 | 없음 | 지식 기반 자동 생성 |
| 추가 탐색 제안 | 없음 | 추론 결과 기반 제안 |

### 1.3 현재 Reasoning 구조 분석
```
현재 파일:
- backend/routers/reasoning/reason.py (메인 API)
- backend/routers/reasoning/reasoning_chain.py (추론 체인)
- backend/routers/reasoning/reasoning_results.py (결과 저장)
- backend/services/reasoning/reasoning_chain_service.py (체인 서비스)

현재 generate_reasoning_answer() 문제점:
- 모드별 고정 템플릿 사용
- 실제 LLM 추론 없음
- 통계 정보만 제공
```

---

## 2. 파일 변경 계획

### 2.1 신규 생성 파일

| 파일 경로 | 용도 | 우선순위 |
|----------|------|----------|
| `backend/services/reasoning/recommendation_service.py` | 추천 로직 서비스 | 1 |
| `backend/routers/reasoning/recommendations.py` | 추천 API 라우터 | 2 |
| `backend/services/reasoning/dynamic_reasoning_service.py` | LLM 기반 동적 추론 | 3 |
| `tests/test_reasoning_recommendations.py` | 추천 기능 테스트 | 4 |

### 2.2 수정 파일

| 파일 경로 | 수정 내용 | 영향도 |
|----------|----------|--------|
| `backend/routers/reasoning/reason.py` | LLM 기반 추론, recommendations 필드 추가 | 높음 |
| `backend/routers/reasoning/__init__.py` | 새 라우터 등록 | 낮음 |
| `backend/services/reasoning/__init__.py` | 새 서비스 export | 낮음 |
| `backend/main.py` | recommendations 라우터 등록 | 낮음 |
| `web/src/pages/reason.html` | 추천 UI 추가 | 중간 |
| `web/public/js/reason.js` | 추천 표시 로직 | 중간 |

### 2.3 삭제 파일
- 없음

---

## 3. 개발 순서 (우선순위별)

### Step 1: RecommendationService 구현 (1일)

#### 1-1. recommendation_service.py 기본 구조
```
구현할 클래스/함수:
- class RecommendationService
  - __init__(db: Session, search_service: SearchService)

핵심 메서드:
- recommend_related_chunks(chunk_ids, limit) -> List[ChunkRecommendation]
- recommend_labels(content, existing_labels) -> List[LabelRecommendation]
- generate_sample_questions(project_id, label_ids, limit) -> List[SampleQuestion]
- suggest_exploration(reasoning_result) -> List[ExplorationSuggestion]
```

#### 1-2. recommend_related_chunks 구현
```
로직:
1. 입력 청크들의 qdrant_point_id 조회
2. KnowledgeRelation에서 관련 청크 조회 (confirmed=true)
3. HybridSearchService로 의미 유사 청크 검색
4. 동일 라벨 가진 청크 조회
5. 중복 제거 및 점수 기반 정렬
6. 상위 N개 반환

반환 형식:
{
    "chunk_id": int,
    "title": str,
    "content_preview": str ([:100]),
    "similarity_score": float,
    "source": "relation" | "semantic" | "label",
    "document_name": str
}
```

#### 1-3. recommend_labels 구현
```
로직:
1. 입력 content에서 키워드 추출
2. 기존 Label 테이블에서 키워드 매칭
3. 유사 청크들의 라벨 수집 (HybridSearch 활용)
4. 라벨 빈도 및 관련도 점수 계산
5. existing_labels 제외
6. 상위 N개 반환

반환 형식:
{
    "label_id": int,
    "name": str,
    "label_type": str,
    "confidence": float,
    "source": "keyword" | "similar_chunk" | "inference"
}
```

#### 1-4. generate_sample_questions 구현
```
로직:
1. 필터 조건으로 청크 수집 (project_id, label_ids)
2. 청크 내용 분석 (키워드, 주제)
3. LLM으로 질문 생성 (Ollama 활용)
4. 모드별 질문 다양성 확보 (design, risk, next_steps)
5. 중복/유사 질문 필터링

반환 형식:
{
    "question": str,
    "suggested_mode": str,
    "related_chunk_ids": List[int],
    "topic": str
}

LLM 프롬프트:
"다음 지식을 바탕으로 사용자가 물어볼 수 있는 질문 3개를 생성하세요.
지식: {chunk_contents}
형식: JSON 배열 [{question, mode}]"
```

#### 1-5. suggest_exploration 구현
```
로직:
1. 추론 결과의 context_chunks 분석
2. 관련된 다른 프로젝트 찾기
3. 관련된 라벨 카테고리 찾기
4. 연관 질문 생성 (LLM)
5. 탐색 제안 구성

반환 형식:
{
    "type": "project" | "label" | "question",
    "id": int (해당시),
    "name": str,
    "description": str,
    "relevance": float
}
```

---

### Step 2: Recommendations API 구현 (0.5일)

#### 2-1. recommendations.py 라우터 생성
```
엔드포인트:
- GET /api/reason/recommendations/chunks
  - Query params: chunk_ids (comma separated), limit

- GET /api/reason/recommendations/labels
  - Query params: content, existing_label_ids, limit

- GET /api/reason/recommendations/questions
  - Query params: project_id, label_ids, limit

- GET /api/reason/recommendations/explore
  - Query params: reasoning_result_id

응답 형식:
{
    "recommendations": [...],
    "total": int,
    "source": str
}
```

---

### Step 3: LLM 기반 동적 추론 (1일)

#### 3-1. dynamic_reasoning_service.py 구현
```
구현할 클래스/함수:
- class DynamicReasoningService
  - __init__(ollama_client, context_manager)

- generate_reasoning(question, context_chunks, mode) -> str
- _build_reasoning_prompt(question, context, mode) -> str
- _postprocess_reasoning(raw_answer) -> str
```

#### 3-2. reason.py 수정 (generate_reasoning_answer 개선)
```
현재:
- 템플릿 기반 고정 응답

변경 후:
- DynamicReasoningService.generate_reasoning() 호출
- 실패 시 기존 템플릿으로 폴백
- recommendations 필드 추가

응답 구조 변경:
{
    "answer": str,
    "context_chunks": [...],
    "relations": [...],
    "reasoning_steps": [...],
    "recommendations": {  # 새로 추가
        "related_chunks": [...],
        "suggested_labels": [...],
        "sample_questions": [...],
        "explore_more": [...]
    }
}
```

#### 3-3. 모드별 프롬프트 설계
```
design_explain 모드:
"당신은 소프트웨어 아키텍트입니다.
다음 컨텍스트를 바탕으로 설계 의도와 배경을 설명하세요.
컨텍스트: {context}
질문: {question}
한국어로 답변하세요."

risk_review 모드:
"당신은 리스크 분석가입니다.
다음 컨텍스트에서 잠재적 위험과 고려사항을 분석하세요.
컨텍스트: {context}
질문: {question}
한국어로 답변하세요."

next_steps 모드:
"당신은 프로젝트 매니저입니다.
다음 컨텍스트를 바탕으로 다음 단계를 제안하세요.
컨텍스트: {context}
질문: {question}
한국어로 답변하세요."

history_trace 모드:
"당신은 기술 문서 전문가입니다.
다음 컨텍스트에서 히스토리와 맥락을 추적하여 설명하세요.
컨텍스트: {context}
질문: {question}
한국어로 답변하세요."
```

---

### Step 4: Web UI 업데이트 (0.5일)

#### 4-1. reason.html 수정
```
추가할 UI 요소:
- 관련 청크 추천 섹션 (카드 형태)
- 샘플 질문 버튼 그룹
- 추가 탐색 제안 링크
- 라벨 추천 태그

배치:
- 추론 결과 아래에 "관련 정보" 섹션 추가
- 사이드바 또는 하단에 샘플 질문 표시
```

#### 4-2. reason.js 수정
```
추가할 함수:
- fetchRecommendations(chunkIds)
- displayRelatedChunks(chunks)
- displaySampleQuestions(questions)
- displayExploreMore(suggestions)
- handleSampleQuestionClick(question)
```

---

### Step 5: 테스트 (0.5일)

#### 5-1. 단위 테스트
```
테스트 파일: tests/test_reasoning_recommendations.py

테스트 케이스:
- test_recommend_related_chunks_returns_results
- test_recommend_labels_excludes_existing
- test_generate_sample_questions_format
- test_suggest_exploration_types
- test_dynamic_reasoning_uses_llm
- test_dynamic_reasoning_fallback_on_error
```

#### 5-2. API 테스트
```
테스트 케이스:
- test_recommendations_chunks_api
- test_recommendations_labels_api
- test_recommendations_questions_api
- test_reason_api_includes_recommendations
```

---

## 4. 개발 주의사항

### 4.1 코드 품질 기준

| 항목 | 기준 |
|------|------|
| 타입 힌트 | 모든 함수/메서드에 적용 |
| Docstring | 모든 클래스/함수에 작성 |
| 에러 처리 | LLM 실패 시 폴백 로직 필수 |
| 로깅 | 추천 생성 과정 로깅 |
| 캐싱 | 반복 요청에 대한 캐싱 고려 |

### 4.2 성능 기준

| 항목 | 기준 |
|------|------|
| 추천 API 응답 시간 | < 1초 (캐시 미적용) |
| 샘플 질문 생성 | < 3초 (LLM 호출 포함) |
| 동적 추론 응답 | < 5초 (LLM 호출 포함) |

### 4.3 품질 통과 기준

| 항목 | 통과 기준 |
|------|----------|
| 단위 테스트 | 100% 통과 |
| API 테스트 | 100% 통과 |
| 기존 Reasoning API | 하위 호환 (기존 응답 형식 유지) |
| 추천 품질 | 관련성 있는 추천 70% 이상 |
| UI 정상 동작 | 모든 추천 요소 표시 |

### 4.4 주의사항 체크리스트

- [ ] LLM 호출 실패 시 기존 템플릿으로 폴백
- [ ] 추천 결과가 없을 때 빈 배열 반환 (에러 아님)
- [ ] 기존 ReasonResponse 필드 유지 (recommendations는 추가)
- [ ] 샘플 질문 생성 시 중복 방지
- [ ] UI에서 추천 섹션 토글 가능하게 (사용자 선택)
- [ ] 대량 데이터 시 페이징 고려

---

## 5. API 엔드포인트 상세 스펙

### 5.1 GET /api/reason/recommendations/chunks
**용도**: 관련 청크 추천

**Request**
```
Query Parameters:
- chunk_ids: string (required) - 쉼표로 구분된 청크 ID 목록
  예: "1,2,3"
- limit: int (optional, default=5, max=20) - 반환할 추천 수
```

**Response 200**
```json
{
    "recommendations": [
        {
            "chunk_id": 10,
            "title": "Phase 8 설계 문서",
            "content_preview": "Phase 8에서는 n8n 워크플로우...",
            "similarity_score": 0.85,
            "source": "semantic",
            "document_name": "phase-8-design.md"
        }
    ],
    "total": 5,
    "source": "hybrid_search"
}
```

**Response 400**
```json
{
    "detail": "chunk_ids parameter is required"
}
```

---

### 5.2 GET /api/reason/recommendations/labels
**용도**: 라벨 추천

**Request**
```
Query Parameters:
- content: string (required) - 라벨을 추천받을 텍스트 내용
- existing_label_ids: string (optional) - 제외할 기존 라벨 ID 목록
  예: "1,5,10"
- limit: int (optional, default=5, max=15) - 반환할 추천 수
```

**Response 200**
```json
{
    "recommendations": [
        {
            "label_id": 3,
            "name": "architecture",
            "label_type": "topic",
            "confidence": 0.92,
            "source": "keyword"
        },
        {
            "label_id": 7,
            "name": "backend",
            "label_type": "category",
            "confidence": 0.78,
            "source": "similar_chunk"
        }
    ],
    "total": 2,
    "source": "combined"
}
```

---

### 5.3 GET /api/reason/recommendations/questions
**용도**: 샘플 질문 생성

**Request**
```
Query Parameters:
- project_id: int (optional) - 프로젝트 필터
- label_ids: string (optional) - 라벨 필터 (쉼표 구분)
- limit: int (optional, default=3, max=10) - 생성할 질문 수
```

**Response 200**
```json
{
    "recommendations": [
        {
            "question": "Phase 8의 설계 결정 배경은 무엇인가요?",
            "suggested_mode": "design_explain",
            "related_chunk_ids": [1, 5, 12],
            "topic": "architecture"
        },
        {
            "question": "현재 구현에서 잠재적 위험 요소는?",
            "suggested_mode": "risk_review",
            "related_chunk_ids": [3, 8],
            "topic": "risk"
        }
    ],
    "total": 2,
    "source": "llm_generated"
}
```

**Response 503** (LLM 실패 시)
```json
{
    "recommendations": [],
    "total": 0,
    "source": "llm_unavailable",
    "message": "LLM 서비스를 사용할 수 없습니다. 나중에 다시 시도해주세요."
}
```

---

### 5.4 GET /api/reason/recommendations/explore
**용도**: 추가 탐색 제안

**Request**
```
Query Parameters:
- reasoning_result_id: int (required) - 추론 결과 ID
```

**Response 200**
```json
{
    "recommendations": [
        {
            "type": "project",
            "id": 2,
            "name": "Phase 9 계획",
            "description": "관련된 다음 단계 프로젝트",
            "relevance": 0.75
        },
        {
            "type": "label",
            "id": 5,
            "name": "security",
            "description": "보안 관련 지식 탐색",
            "relevance": 0.68
        },
        {
            "type": "question",
            "id": null,
            "name": "보안 고려사항은 무엇인가요?",
            "description": "추론 결과와 관련된 후속 질문",
            "relevance": 0.82
        }
    ],
    "total": 3,
    "source": "context_analysis"
}
```

**Response 404**
```json
{
    "detail": "Reasoning result not found"
}
```

---

### 5.5 POST /api/reason (기존 API 확장)
**용도**: 추론 실행 (recommendations 필드 추가)

**Request Body** (기존과 동일)
```json
{
    "question": "Phase 8의 설계 의도는?",
    "mode": "design_explain",
    "project_id": 1,
    "label_ids": [1, 2]
}
```

**Response 200** (확장된 응답)
```json
{
    "answer": "Phase 8은 n8n 워크플로우 자동화를 통해...",
    "context_chunks": [...],
    "relations": [...],
    "reasoning_steps": [...],
    "recommendations": {
        "related_chunks": [
            {
                "chunk_id": 15,
                "title": "워크플로우 설계",
                "content_preview": "...",
                "similarity_score": 0.88,
                "source": "semantic",
                "document_name": "workflow-design.md"
            }
        ],
        "suggested_labels": [
            {
                "label_id": 3,
                "name": "automation",
                "label_type": "topic",
                "confidence": 0.85,
                "source": "inference"
            }
        ],
        "sample_questions": [
            {
                "question": "워크플로우 성능 최적화 방법은?",
                "suggested_mode": "design_explain",
                "related_chunk_ids": [15, 20],
                "topic": "performance"
            }
        ],
        "explore_more": [
            {
                "type": "project",
                "id": 3,
                "name": "Phase 9",
                "description": "다음 개발 단계",
                "relevance": 0.72
            }
        ]
    }
}
```

---

### 5.6 공통 에러 응답

**401 Unauthorized**
```json
{
    "detail": "Not authenticated"
}
```

**500 Internal Server Error**
```json
{
    "detail": "Internal server error",
    "error_code": "RECOMMENDATION_FAILED"
}
```

---

## 6. 의존성 활용

### 5.1 Task 9-3-3에서 가져올 것
- `HybridSearchService`: 유사 청크 검색에 활용
- `ContextManager`: 질문 생성 시 컨텍스트 구성
- `Reranker`: 추천 결과 재정렬에 활용 (선택적)

### 5.2 활용 코드 예시
```python
# recommendation_service.py에서
from backend.services.search.hybrid_search import HybridSearchService
from backend.services.ai.context_manager import ContextManager

class RecommendationService:
    def __init__(self, db, hybrid_search: HybridSearchService):
        self.hybrid_search = hybrid_search

    def recommend_related_chunks(self, chunk_ids, limit):
        # 9-3-3의 HybridSearch 활용
        results = self.hybrid_search.search_hybrid(
            query=chunk_content,
            search_mode="hybrid"
        )
```

---

## 6. 다음 Task 연계

### 완료 후 영향
- **9-3-2 (지식구조 매칭)**: recommend_labels 로직 재사용 가능

### 전달 사항
- RecommendationService API 문서
- 추천 점수 계산 로직 설명
- LLM 프롬프트 템플릿

---

## 7. 참고 자료

- 현재 Reasoning API: `backend/routers/reasoning/reason.py`
- 현재 추론 체인: `backend/services/reasoning/reasoning_chain_service.py`
- Ollama 클라이언트: `backend/services/ai/ollama_client.py`
- 지식 모델: `backend/models/models.py`
