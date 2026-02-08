# Reasoning Lab (/reason) 기능 종합 보고서

**작성일**: 2026-02-04
**대상**: Personal AI Brain - Reasoning Lab 기능
**용도**: 시스템 구조 및 구현 상세 문서

---

## 1. 구현 목표

### 1.1 핵심 목적

지식 베이스에 저장된 문서와 청크를 기반으로 **다중 모드 추론(Reasoning)**을 수행하여 사용자 질문에 맥락 기반 답변을 제공

### 1.2 세부 목표

| 목표 | 설명 |
|------|------|
| **지식 기반 추론** | 승인된(approved) 청크들을 활용한 근거 있는 답변 생성 |
| **다중 모드 지원** | 4가지 추론 모드로 다양한 분석 관점 제공 |
| **하이브리드 검색** | 시맨틱 검색(Qdrant) + 필터링 검색(PostgreSQL) 결합 |
| **지식 그래프 활용** | 청크 간 관계(Relations)를 추적하여 연관 컨텍스트 확장 |
| **LLM 통합** | Ollama 기반 로컬 LLM으로 답변 생성 |
| **추천 시스템** | 관련 청크, 라벨, 탐색 방향 제안 |

---

## 2. 추론 모드 (4가지)

| 모드 | 역할 | 설명 |
|------|------|------|
| `design_explain` | Software Architect | 설계 의도, 구조, 아키텍처 설명 |
| `risk_review` | Risk Analyst | 위험 요소, 잠재적 문제점 분석 |
| `next_steps` | Project Manager | 다음 단계, 후속 작업 제안 |
| `history_trace` | Tech Documentation Expert | 히스토리 추적, 변경 이력 분석 |

---

## 3. 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Frontend (reason.html)                       │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────────────┐ │
│  │ Question    │  │ Mode Select  │  │ Filters (Projects/Labels)   │ │
│  │ Textarea    │  │ (4 modes)    │  │ Multi-select dropdowns      │ │
│  └─────────────┘  └──────────────┘  └─────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────────┘
                             │ POST /api/reason
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Backend Router (reason.py)                        │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ 1. collect_chunks_by_question() → Qdrant 시맨틱 검색          │  │
│  │ 2. collect_knowledge_chunks()   → PostgreSQL 필터 검색        │  │
│  │ 3. expand_chunks_with_relations() → 지식그래프 2-depth 확장   │  │
│  │ 4. add_semantic_search_results() → 추가 시맨틱 보강           │  │
│  │ 5. DynamicReasoningService.generate_reasoning() → LLM 답변    │  │
│  └───────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
   │   Qdrant    │    │ PostgreSQL  │    │   Ollama    │
   │ (Vector DB) │    │ (Relational)│    │ (Local LLM) │
   └─────────────┘    └─────────────┘    └─────────────┘
```

---

## 4. Backend 구현

### 4.1 라우터 구조

```
backend/routers/reasoning/
├── __init__.py
├── reason.py              # 핵심 추론 API (557줄)
├── reasoning_chain.py     # 다단계 추론 체인 (53줄)
├── reasoning_results.py   # 결과 저장/조회 (163줄)
└── recommendations.py     # 추천 시스템 (129줄)
```

### 4.2 핵심 API 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/reason` | **메인 추론 실행** |
| POST | `/api/reasoning-chain/build` | 다단계 추론 체인 생성 |
| POST | `/api/reasoning-chain/visualize` | 추론 체인 시각화 |
| POST | `/api/reasoning-results` | 결과 저장 |
| GET | `/api/reasoning-results` | 결과 목록 조회 |
| GET | `/api/reasoning-results/{id}` | 특정 결과 조회 |
| DELETE | `/api/reasoning-results/{id}` | 결과 삭제 |
| GET | `/api/reason/recommendations/chunks` | 관련 청크 추천 |
| GET | `/api/reason/recommendations/labels` | 라벨 추천 |
| GET | `/api/reason/recommendations/questions` | 샘플 질문 생성 |
| GET | `/api/reason/recommendations/explore` | 탐색 방향 제안 |

### 4.3 메인 추론 요청/응답 스키마

**Request (`ReasonRequest`)**
```python
{
    "mode": "design_explain",           # 추론 모드
    "inputs": {
        "project_ids": [1, 2],          # 선택: 프로젝트 필터
        "label_ids": [3, 4]             # 선택: 라벨 필터
    },
    "question": "시스템 아키텍처는?",     # 사용자 질문
    "filters": {},                       # 추가 필터
    "model": "qwen2.5:7b"               # Ollama 모델
}
```

**Response (`ReasonResponse`)**
```python
{
    "answer": "분석 결과...",            # LLM 생성 답변
    "context_chunks": [...],            # 사용된 컨텍스트 청크들
    "relations": [...],                 # 청크 간 관계 정보
    "reasoning_steps": [...],           # 추론 단계 로그
    "recommendations": {
        "related_chunks": [...],        # 관련 청크
        "sample_questions": [...],      # 추천 질문
        "labels": [...],                # 추천 라벨
        "explore": [...]                # 탐색 제안
    }
}
```

### 4.4 핵심 서비스

**파일: `backend/services/reasoning/dynamic_reasoning_service.py`**

```python
class DynamicReasoningService:
    async def generate_reasoning(
        self,
        question: str,
        context_chunks: List[dict],
        mode: str,
        max_tokens: int = 2000,
        model: str = None
    ) -> Optional[str]:
        # 1. 모드별 프롬프트 선택
        # 2. 컨텍스트 구성
        # 3. Ollama API 호출
        # 4. 답변 반환 (실패 시 템플릿 폴백)
```

**모드별 프롬프트 역할:**
- `design_explain`: "당신은 소프트웨어 아키텍트입니다..."
- `risk_review`: "당신은 위험 분석가입니다..."
- `next_steps`: "당신은 프로젝트 매니저입니다..."
- `history_trace`: "당신은 기술 문서 전문가입니다..."

---

## 5. Frontend 구현

### 5.1 파일 구조

```
web/
├── src/pages/reason.html           # 메인 HTML 템플릿 (157줄)
├── public/css/reason.css           # 스타일시트
└── public/js/reason/reason.js      # JavaScript 로직 (150+줄)
```

### 5.2 UI 구성요소

| 섹션 | 설명 |
|------|------|
| **Reasoning Form** | 질문 입력, 모드 선택, 모델 선택 |
| **Filters** | 프로젝트/라벨 다중 선택 드롭다운 |
| **Loading** | 실행 중 경과 시간 표시 |
| **Results Summary** | 문서/청크/관계 개수 요약 |
| **Final Conclusion** | LLM 생성 답변 표시 |
| **Used Context** | 청크/문서 탭 뷰 |
| **Reasoning Steps** | 단계별 프로세스 로그 |
| **Recommendations** | 4개 패널 (청크, 질문, 라벨, 탐색) |

### 5.3 주요 JavaScript 함수

```javascript
// reason.js
async function runReasoning()           // 추론 API 호출
function showReasoningLoadingWithElapsed() // 로딩 UI + 타이머
async function loadReasoningOptions()   // 프로젝트/라벨 로드
async function loadSeedChunk()          // URL 파라미터로 시드 청크 로드
```

---

## 6. Database (PostgreSQL) 구현

### 6.1 관련 테이블

**`reasoning_results` - 추론 결과 저장**

```sql
CREATE TABLE reasoning_results (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    reasoning_steps TEXT,      -- JSON 문자열
    context_chunks TEXT,       -- JSON 문자열
    relations TEXT,            -- JSON 문자열
    mode VARCHAR,
    session_id VARCHAR,        -- 인덱스
    meta_data TEXT,            -- JSON 문자열
    created_at TIMESTAMP DEFAULT NOW()
);
```

**`knowledge_chunks` - 지식 청크**

| 컬럼 | 용도 |
|------|------|
| `id` | PK, 청크 식별자 |
| `content` | 청크 텍스트 내용 |
| `title` | 청크 제목 |
| `status` | 상태 (approved/pending) |
| `qdrant_point_id` | Qdrant 벡터 ID 매핑 |
| `document_id` | 소속 문서 FK |

**`knowledge_relations` - 청크 간 관계**

| 컬럼 | 용도 |
|------|------|
| `source_chunk_id` | 출발 청크 |
| `target_chunk_id` | 도착 청크 |
| `relation_type` | 관계 유형 |
| `confirmed` | 확인 여부 |

**`knowledge_labels` - 청크-라벨 연결**

| 컬럼 | 용도 |
|------|------|
| `chunk_id` | 청크 FK |
| `label_id` | 라벨 FK |
| `status` | 상태 (confirmed/pending) |

### 6.2 주요 쿼리 패턴

**승인된 청크만 조회:**
```python
chunks = db.query(KnowledgeChunk).filter(
    KnowledgeChunk.status == "approved"
).all()
```

**프로젝트/라벨 필터링:**
```python
# 프로젝트로 필터
chunks = db.query(KnowledgeChunk).join(Document).filter(
    Document.project_id.in_(project_ids)
).all()

# 라벨로 필터
chunks = db.query(KnowledgeChunk).join(KnowledgeLabel).filter(
    KnowledgeLabel.label_id.in_(label_ids),
    KnowledgeLabel.status == "confirmed"
).all()
```

**관계 확장 (2-depth):**
```python
for depth in range(MULTIHOP_MAX_DEPTH):  # default: 2
    relations = db.query(KnowledgeRelation).filter(
        KnowledgeRelation.source_chunk_id.in_(current_ids),
        KnowledgeRelation.confirmed == "true"
    ).all()
    # target_chunk_id들을 다음 탐색 대상에 추가
```

---

## 7. Qdrant (Vector DB) 구현

### 7.1 구성 설정

```python
# backend/config.py
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
QDRANT_API_KEY = None                    # 선택
COLLECTION_NAME = "brain_documents"
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
```

### 7.2 사용 패턴

**1. 질문 기반 시맨틱 검색**
```python
# reason.py: collect_chunks_by_question()
results = await search_service.search_simple(
    question,
    top_k=20,
    use_cache=False
)
# Qdrant point_id → PostgreSQL chunk 매핑
```

**2. 추가 시맨틱 보강**
```python
# reason.py: add_semantic_search_results()
results = await search_service.search_simple(
    question,
    top_k=5
)
# 기존 결과와 중복 제거 후 추가
```

**3. 관련 청크 추천**
```python
# recommendation_service.py
results = await search_service.hybrid_search(
    chunk_content,
    top_k=5
)
# 유사 청크 추천
```

### 7.3 검색 흐름

```
사용자 질문
    │
    ▼
┌─────────────────────────────────┐
│ SentenceTransformer 임베딩      │
│ (multilingual-MiniLM-L12-v2)   │
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│ Qdrant Vector Search            │
│ Collection: brain_documents     │
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│ PostgreSQL 매핑                 │
│ qdrant_point_id → chunk.id     │
│ status="approved" 필터         │
└─────────────────────────────────┘
```

---

## 8. 핵심 구현 사항

### 8.1 하이브리드 검색 전략

| 순서 | 검색 방법 | 우선순위 | 설명 |
|------|-----------|----------|------|
| 1 | 질문 시맨틱 검색 | **최우선** | Qdrant로 질문과 유사한 청크 검색 |
| 2 | 프로젝트/라벨 필터 | 보조 | PostgreSQL에서 조건 필터링 |
| 3 | 관계 확장 | 보조 | 지식그래프 2-depth 탐색 |
| 4 | 추가 시맨틱 | 보강 | 부족 시 추가 검색 |

### 8.2 컨텍스트 구성

```python
def build_context_chunks(chunks):
    return [{
        "chunk_id": chunk.id,
        "content": chunk.content,
        "title": chunk.title,
        "document_name": chunk.document.file_name,
        "project_id": chunk.document.project_id,
        "labels": [label.name for label in chunk.labels],
        "source": "semantic" | "filter" | "relation"
    } for chunk in chunks]
```

### 8.3 LLM 통합

**Ollama 호출:**
```python
async with httpx.AsyncClient() as client:
    response = await client.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json={
            "model": model or OLLAMA_MODEL,
            "prompt": full_prompt,
            "stream": False
        },
        timeout=60.0
    )
```

**폴백 전략:**
- LLM 실패 시 → 템플릿 기반 답변 생성
- 컨텍스트 없음 시 → "관련 지식이 없습니다" + 안내 메시지

### 8.4 추천 시스템 알고리즘

**관련 청크 점수:**
| 소스 | 점수 |
|------|------|
| 직접 관계 (relation) | 0.9 |
| 시맨틱 유사도 | 실제 점수 |
| 동일 라벨 | 0.7 |

**라벨 추천:**
1. 키워드 매칭 (content ↔ label.name)
2. 하이브리드 검색으로 유사 청크의 라벨
3. LLM 키워드 추출 → 기존 라벨 매칭

---

## 9. 설정 옵션

### 9.1 환경 변수

```bash
# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333
COLLECTION_NAME=brain_documents

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b

# RAG 설정
HYBRID_SEARCH_SEMANTIC_WEIGHT=0.7
HYBRID_SEARCH_KEYWORD_WEIGHT=0.3
RERANKER_ENABLED=true
CONTEXT_MAX_TOKENS_SIMPLE=800
CONTEXT_MAX_TOKENS_COMPLEX=2000
MULTIHOP_MAX_DEPTH=2

# Rate Limiting
RATE_LIMIT_LLM_PER_MINUTE=10
```

### 9.2 조정 가능 파라미터

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| `top_k` (질문 검색) | 20 | 시맨틱 검색 최대 결과 |
| `top_k` (보강) | 5 | 추가 검색 결과 |
| `MULTIHOP_MAX_DEPTH` | 2 | 관계 탐색 깊이 |
| `max_tokens` (LLM) | 2000 | 답변 최대 토큰 |

---

## 10. 데이터 흐름 요약

```
[사용자 질문 + 모드 + 필터]
         │
         ▼
┌────────────────────────────────────────────────────────┐
│ 1. 시맨틱 검색 (Qdrant)                                │
│    question → embedding → vector search → chunk IDs   │
└────────────────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────┐
│ 2. DB 필터 검색 (PostgreSQL)                           │
│    project_ids + label_ids → approved chunks          │
└────────────────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────┐
│ 3. 관계 확장 (PostgreSQL)                              │
│    chunk_ids → relations → related_chunk_ids (depth 2)│
└────────────────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────┐
│ 4. 컨텍스트 구성                                       │
│    chunks → content + metadata + labels               │
└────────────────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────┐
│ 5. LLM 답변 생성 (Ollama)                              │
│    mode_prompt + context + question → answer          │
└────────────────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────┐
│ 6. 추천 생성                                           │
│    related_chunks, sample_questions, labels, explore  │
└────────────────────────────────────────────────────────┘
         │
         ▼
[ReasonResponse: answer + context + relations + steps + recommendations]
```

---

## 11. 파일 위치 요약

### Backend

| 파일 | 용도 | 줄 수 |
|------|------|-------|
| `backend/routers/reasoning/reason.py` | 메인 추론 API | 557 |
| `backend/routers/reasoning/reasoning_chain.py` | 추론 체인 | 53 |
| `backend/routers/reasoning/reasoning_results.py` | 결과 CRUD | 163 |
| `backend/routers/reasoning/recommendations.py` | 추천 API | 129 |
| `backend/services/reasoning/dynamic_reasoning_service.py` | LLM 서비스 | 126 |
| `backend/services/reasoning/reasoning_chain_service.py` | 체인 서비스 | 163 |
| `backend/services/reasoning/recommendation_service.py` | 추천 서비스 | 556 |
| `backend/services/search/search_service.py` | Qdrant 검색 | - |
| `backend/models/models.py` | DB 모델 | - |

### Frontend

| 파일 | 용도 |
|------|------|
| `web/src/pages/reason.html` | 페이지 템플릿 |
| `web/public/css/reason.css` | 스타일시트 |
| `web/public/js/reason/reason.js` | JavaScript 로직 |

### Config

| 파일 | 용도 |
|------|------|
| `backend/config.py` | 전체 설정 |
| `.env` / `.env.example` | 환경 변수 |

---

## 12. 확장 포인트

### 12.1 새 추론 모드 추가

1. `dynamic_reasoning_service.py`의 `MODE_PROMPTS`에 새 모드 추가
2. `reason.html`의 모드 선택 UI 업데이트
3. `reason.js`의 `modeDescriptions` 맵 업데이트

### 12.2 검색 알고리즘 개선

- `HYBRID_SEARCH_SEMANTIC_WEIGHT` 조정
- `RERANKER_MODEL` 변경
- `MULTIHOP_MAX_DEPTH` 증가

### 12.3 새 추천 유형 추가

1. `recommendation_service.py`에 새 메서드 추가
2. `recommendations.py`에 새 엔드포인트 추가
3. Frontend에 새 추천 패널 추가

---

**문서 끝**
