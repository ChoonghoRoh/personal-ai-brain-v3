# Phase 9 Master Plan - 보안 강화, 테스트 확대, AI 기능 고도화

**작성일**: 2026-02-01
**상태**: ✅ 확정 (Confirmed)
**확정일**: 2026-02-01
**기준 문서**: `docs/review/2026-02-01-full-project-analysis-report.md`

### 관련 문서
| 문서 | 용도 |
|------|------|
| [phase-9-navigation.md](./phase-9-navigation.md) | 전체 진행 현황 추적 |
| [phase-9-work-instructions.md](./phase-9-work-instructions.md) | 작업 지시사항/규칙 |
| [phase-9-prompt-templates.md](./phase-9-prompt-templates.md) | 프롬프트 템플릿 |
| [phase-9-3-todo-list.md](./phase-9-3/phase-9-3-todo-list.md) | 현재 Phase Todo |

---

## 목차

1. [Phase 9 개요](#1-phase-9-개요)
2. [목표 및 범위](#2-목표-및-범위)
3. [단계별 계획](#3-단계별-계획)
4. [상세 Task 목록](#4-상세-task-목록)
5. [우선순위 및 의존성](#5-우선순위-및-의존성)
6. [완료 기준](#6-완료-기준)
7. [제외 항목](#7-제외-항목)

---

## 1. Phase 9 개요

### 1.1 배경

Phase 8까지 핵심 기능(문서 임베딩, 의미 검색, AI 응답, 지식 구조화, Reasoning)이 구현되었으나, 프로젝트 분석 결과 다음 영역에서 개선이 필요함:

| 영역 | 현재 점수 | 목표 점수 |
|------|-----------|-----------|
| 보안 | 60/100 | 85/100 |
| 테스트 | 40/100 | 75/100 |
| AI 기능 | 70/100 | 90/100 |
| 기능 완성도 | 90/100 | 95/100 |

### 1.2 Phase 9 핵심 테마

```
┌─────────────────────────────────────────────────────────────┐
│                      Phase 9 핵심 테마                       │
├─────────────────────────────────────────────────────────────┤
│  1. 보안 강화        → 인증, 비밀번호 보안, CORS, Rate Limit │
│  2. 테스트 확대      → API 테스트, 통합 테스트, CI/CD        │
│  3. AI 기능 고도화   → Reasoning 추천, RAG 강화, 지식 매칭   │
│  4. 기능 확장        → HWP 지원, 통계 대시보드, 백업/복원    │
│  5. 코드 품질        → 리팩토링, 문서화, 타입 힌트 강화      │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. 목표 및 범위

### 2.1 In Scope (포함)

| 분류 | 항목 |
|------|------|
| **보안** | API 인증 시스템, 환경변수 비밀번호 관리, CORS 설정, Rate Limiting |
| **테스트** | AI/Knowledge/Reasoning API 테스트, 통합 테스트, 테스트 커버리지 70% |
| **AI 기능** | Reasoning 추천/샘플 기능, Import 시 지식구조 매칭, RAG 고도화 |
| **기능** | HWP 파일 지원, 통계/분석 대시보드, 백업/복원 시스템 |
| **품질** | 코드 리팩토링, 타입 힌트 보강, API 문서화 개선 |

### 2.2 Out of Scope (제외)

| 항목 | 사유 |
|------|------|
| n8n 워크플로우 | Phase 8 보류, 별도 프로젝트 권장 |
| Discord 연동 | n8n 의존 기능 |
| 외부 클라우드 연동 | 로컬 우선 프로젝트 방침 |

---

## 3. 단계별 계획

### Phase 9 구조

```
Phase 9
├── 9-1   보안 강화 (Security Enhancement)
│   ├── 9-1-1  API 인증 시스템 구축
│   ├── 9-1-2  환경변수 비밀번호 관리
│   ├── 9-1-3  CORS 설정
│   └── 9-1-4  Rate Limiting
│
├── 9-2   테스트 확대 (Test Expansion)
│   ├── 9-2-1  AI API 테스트
│   ├── 9-2-2  Knowledge API 테스트
│   ├── 9-2-3  Reasoning API 테스트
│   ├── 9-2-4  통합 테스트
│   └── 9-2-5  CI/CD 파이프라인
│
├── 9-3   AI 기능 고도화 (AI Enhancement) ★ 핵심
│   ├── 9-3-1  Reasoning AI 추천/샘플 기능 업그레이드
│   ├── 9-3-2  Data Import/CRUD 지식구조 자동 매칭
│   └── 9-3-3  RAG 기능 강화
│
├── 9-4   기능 확장 (Feature Extension)
│   ├── 9-4-1  HWP 파일 지원
│   ├── 9-4-2  통계/분석 대시보드
│   └── 9-4-3  백업/복원 시스템
│
└── 9-5   코드 품질 (Code Quality)
    ├── 9-5-1  코드 리팩토링
    ├── 9-5-2  타입 힌트 강화
    └── 9-5-3  API 문서화 개선
```

---

## 4. 상세 Task 목록

### 9-1 보안 강화

#### 9-1-1: API 인증 시스템 구축

| 항목 | 내용 |
|------|------|
| **목표** | API Key 또는 JWT 기반 인증 추가 |
| **산출물** | `backend/middleware/auth.py`, `backend/routers/auth/` |
| **예상 작업량** | 2일 |

#### 9-1-2: 환경변수 비밀번호 관리

| 항목 | 내용 |
|------|------|
| **목표** | 하드코딩된 비밀번호를 환경변수로 이동 |
| **산출물** | `.env.example` 업데이트, `backend/config.py` 수정 |
| **예상 작업량** | 0.5일 |

#### 9-1-3: CORS 설정

| 항목 | 내용 |
|------|------|
| **목표** | 프로덕션 배포를 위한 CORS 정책 설정 |
| **산출물** | `backend/middleware/cors.py` |
| **예상 작업량** | 0.5일 |

#### 9-1-4: Rate Limiting

| 항목 | 내용 |
|------|------|
| **목표** | API 남용 방지를 위한 요청 제한 |
| **산출물** | `backend/middleware/rate_limit.py` |
| **예상 작업량** | 1일 |

---

### 9-2 테스트 확대

#### 9-2-1 ~ 9-2-5: 테스트 확대

| Task | 산출물 | 예상 작업량 |
|------|--------|-------------|
| 9-2-1 AI API 테스트 | `tests/test_ai_api.py` | 1일 |
| 9-2-2 Knowledge API 테스트 | `tests/test_knowledge_api.py` | 1일 |
| 9-2-3 Reasoning API 테스트 | `tests/test_reasoning_api.py` | 0.5일 |
| 9-2-4 통합 테스트 | `tests/integration/` | 1.5일 |
| 9-2-5 CI/CD 파이프라인 | `.github/workflows/test.yml` | 0.5일 |

---

### 9-3 AI 기능 고도화 ★ 핵심

#### 9-3-1: Reasoning AI 추천/샘플 기능 업그레이드

| 항목 | 내용 |
|------|------|
| **목표** | 템플릿 기반 → LLM 기반 동적 추론, 추천 기능 추가 |
| **산출물** | |
| | - `backend/services/reasoning/recommendation_service.py` |
| | - `backend/routers/reasoning/recommendations.py` |
| | - Web UI 업데이트 (`web/src/pages/reason.html`) |

**현재 상태 분석:**
```
현재 Reasoning 시스템의 한계:
1. generate_reasoning_answer()가 템플릿 기반 (모드별 고정 포맷)
2. 관련 청크/라벨 추천 기능 없음
3. 샘플 질문 제안 기능 없음
4. 추론 결과 기반 추가 탐색 제안 없음
```

**세부 기능:**

| 기능 | 설명 | API |
|------|------|-----|
| **LLM 기반 동적 추론** | Ollama/Claude로 컨텍스트 기반 실제 추론 | `POST /api/reason` 개선 |
| **관련 청크 추천** | 현재 청크와 유사한 청크 자동 추천 | `GET /api/reason/recommendations/chunks` |
| **관련 라벨 추천** | 현재 컨텍스트에 맞는 라벨 추천 | `GET /api/reason/recommendations/labels` |
| **샘플 질문 추천** | 수집된 지식 기반 추천 질문 생성 | `GET /api/reason/recommendations/questions` |
| **추가 탐색 제안** | 추론 결과 기반 "더 알아보기" 제안 | `GET /api/reason/recommendations/explore` |

**구현 설계:**

```python
# recommendation_service.py

class RecommendationService:
    def recommend_related_chunks(
        self,
        chunk_ids: List[int],
        limit: int = 5
    ) -> List[ChunkRecommendation]:
        """
        현재 청크와 관련된 청크 추천
        - 관계 그래프 탐색 (KnowledgeRelation)
        - 의미 유사도 검색 (Qdrant)
        - 동일 라벨 청크 우선
        """
        pass

    def recommend_labels(
        self,
        content: str,
        existing_labels: List[int]
    ) -> List[LabelRecommendation]:
        """
        컨텐츠 기반 라벨 추천
        - 키워드 추출 → 기존 라벨 매칭
        - 유사 청크의 라벨 참조
        - LLM 기반 라벨 제안
        """
        pass

    def generate_sample_questions(
        self,
        project_id: int = None,
        label_ids: List[int] = None,
        limit: int = 5
    ) -> List[SampleQuestion]:
        """
        지식 기반 샘플 질문 생성
        - 청크 내용 분석
        - LLM으로 질문 생성
        - 다양성 확보 (모드별 질문)
        """
        pass

    def suggest_exploration(
        self,
        reasoning_result: ReasoningResult
    ) -> List[ExplorationSuggestion]:
        """
        추론 결과 기반 추가 탐색 제안
        - 관련 프로젝트 제안
        - 관련 라벨 카테고리 제안
        - 연관 질문 제안
        """
        pass
```

**예상 작업량:** 3일

---

#### 9-3-2: Data Import/CRUD 지식구조 자동 매칭

| 항목 | 내용 |
|------|------|
| **목표** | 데이터 생성/수정 시 자동으로 지식 구조와 연결 |
| **산출물** | |
| | - `backend/services/knowledge/structure_matcher.py` |
| | - `backend/services/knowledge/auto_labeler.py` |
| | - 기존 라우터 확장 |

**현재 상태 분석:**
```
현재 Import/CRUD 흐름:
1. 문서 업로드 → 청크 생성 → 수동 라벨링
2. 자동 키워드 추출은 있으나 구조 매칭 없음
3. 관계 자동 생성 없음
4. 유사 문서 그룹핑 없음
```

**세부 기능:**

| 기능 | 설명 | 트리거 |
|------|------|--------|
| **자동 라벨 추천** | Import 시 컨텐츠 분석 → 라벨 추천 | 청크 생성 시 |
| **유사 청크 연결 추천** | 새 청크와 유사한 기존 청크 관계 제안 | 청크 생성 시 |
| **카테고리 자동 분류** | 문서 내용 기반 카테고리 라벨 추천 | 문서 생성 시 |
| **유사 문서 그룹핑** | 유사한 문서끼리 자동 그룹 제안 | 문서 생성 시 |
| **관계 자동 제안** | 의미적 연관성 기반 관계 자동 생성 | 청크 승인 시 |

**구현 설계:**

```python
# structure_matcher.py

class StructureMatcher:
    def match_on_chunk_create(
        self,
        chunk: KnowledgeChunk
    ) -> StructureMatchResult:
        """
        청크 생성 시 자동 매칭

        Returns:
            suggested_labels: 추천 라벨 목록
            similar_chunks: 유사 청크 목록 (관계 후보)
            suggested_category: 추천 카테고리
        """
        # 1. 키워드 추출
        keywords = extract_keywords(chunk.content)

        # 2. 기존 라벨과 매칭
        suggested_labels = match_keywords_to_labels(keywords)

        # 3. Qdrant에서 유사 청크 검색
        similar_chunks = search_similar_chunks(chunk.content, top_k=10)

        # 4. 유사 청크의 라벨 참조하여 추가 추천
        suggested_labels += infer_labels_from_similar(similar_chunks)

        # 5. 카테고리 추론
        suggested_category = infer_category(chunk, similar_chunks)

        return StructureMatchResult(...)

    def suggest_relations_on_approve(
        self,
        chunk: KnowledgeChunk
    ) -> List[RelationSuggestion]:
        """
        청크 승인 시 관계 자동 제안

        - 동일 문서 내 청크와의 순서 관계
        - 유사 청크와의 의미 관계
        - 동일 라벨 청크와의 관계
        """
        pass


# auto_labeler.py

class AutoLabeler:
    def label_on_import(
        self,
        document: Document,
        chunks: List[KnowledgeChunk]
    ) -> AutoLabelResult:
        """
        Import 시 자동 라벨링

        1. 문서 전체 분석 → 문서 레벨 라벨
        2. 각 청크 분석 → 청크 레벨 라벨
        3. 기존 지식과 교차 분석 → 추가 라벨
        """
        pass

    def suggest_category(
        self,
        document: Document
    ) -> CategorySuggestion:
        """
        문서 카테고리 자동 제안

        - 파일 경로 분석 (docs/phases/, brain/ 등)
        - 컨텐츠 분석
        - 유사 문서 카테고리 참조
        """
        pass
```

**API 확장:**

| 기존 API | 추가 기능 |
|----------|-----------|
| `POST /api/documents` | 응답에 `suggested_category`, `suggested_labels` 추가 |
| `POST /api/knowledge/chunks` | 응답에 `suggested_labels`, `similar_chunks` 추가 |
| `POST /api/knowledge/approval` | 응답에 `suggested_relations` 추가 |

**예상 작업량:** 2.5일

---

#### 9-3-3: RAG 기능 강화

| 항목 | 내용 |
|------|------|
| **목표** | RAG 파이프라인 품질 및 성능 향상 |
| **산출물** | |
| | - `backend/services/search/hybrid_search.py` |
| | - `backend/services/search/reranker.py` |
| | - `backend/services/ai/context_manager.py` |
| | - 기존 AI 라우터 개선 |

**현재 상태 분석:**
```
현재 RAG 파이프라인의 한계:
1. 단순 벡터 검색만 사용 (키워드 검색 없음)
2. Reranking 없음 (초기 검색 결과 그대로 사용)
3. 컨텍스트 윈도우 고정 (1000자)
4. Single-hop 검색만 (관계 추적 없음)
5. 컨텍스트 압축 없음
```

**세부 기능:**

| 기능 | 설명 | 효과 |
|------|------|------|
| **Hybrid Search** | 키워드 + 의미 검색 결합 | 검색 정확도 향상 |
| **Reranking** | Cross-encoder로 재정렬 | 관련성 높은 문서 상위 배치 |
| **Multi-hop RAG** | 관계 추적하며 다단계 검색 | 복잡한 질문 대응 |
| **Context Compression** | 중요 문장만 추출 | 컨텍스트 효율화 |
| **동적 컨텍스트** | 질문 복잡도에 따른 크기 조절 | 품질/비용 최적화 |

**구현 설계:**

```python
# hybrid_search.py

class HybridSearchService:
    def search(
        self,
        query: str,
        top_k: int = 10,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3
    ) -> List[SearchResult]:
        """
        Hybrid Search: 의미 검색 + 키워드 검색 결합

        1. Qdrant 벡터 검색 (semantic)
        2. PostgreSQL full-text 검색 (keyword)
        3. RRF(Reciprocal Rank Fusion) 또는 가중 합산
        """
        semantic_results = self.semantic_search(query, top_k * 2)
        keyword_results = self.keyword_search(query, top_k * 2)

        return self.fuse_results(
            semantic_results,
            keyword_results,
            semantic_weight,
            keyword_weight
        )


# reranker.py

class Reranker:
    def rerank(
        self,
        query: str,
        candidates: List[SearchResult],
        top_k: int = 5
    ) -> List[SearchResult]:
        """
        Cross-encoder 기반 Reranking

        - 가벼운 모델: ms-marco-MiniLM-L-6-v2
        - 또는 LLM 기반 관련성 점수 (비용 주의)
        """
        pass


# context_manager.py

class ContextManager:
    def build_context(
        self,
        question: str,
        search_results: List[SearchResult],
        max_tokens: int = 2000
    ) -> ContextResult:
        """
        지능형 컨텍스트 구성

        1. 질문 복잡도 분석 → 필요 컨텍스트 크기 결정
        2. 문서 중요도 순 정렬
        3. 각 문서에서 관련 문장만 추출 (compression)
        4. 토큰 제한 내에서 최대 정보 포함
        """
        pass

    def compress_context(
        self,
        content: str,
        question: str,
        max_length: int = 500
    ) -> str:
        """
        컨텍스트 압축

        - 질문과 관련 높은 문장만 추출
        - 중복 제거
        - 요약 (필요시 LLM 사용)
        """
        pass


# multi_hop_rag.py

class MultiHopRAG:
    def search(
        self,
        question: str,
        max_hops: int = 2
    ) -> MultiHopResult:
        """
        Multi-hop RAG: 관계 추적하며 다단계 검색

        Hop 1: 질문 → 초기 검색 결과
        Hop 2: 초기 결과의 관계 → 연관 청크
        Hop 3: 연관 청크 기반 추가 검색

        Returns:
            chunks: 최종 청크 목록
            hop_trace: 각 hop별 검색 경로
        """
        pass
```

**개선된 RAG 파이프라인:**

```
기존:
  Question → Qdrant Search → Top 5 → Context (1000자) → LLM → Answer

개선 후:
  Question
      ↓
  [복잡도 분석] → 단순/복잡 판단
      ↓
  [Hybrid Search] → 의미 + 키워드 검색
      ↓
  [Reranking] → Cross-encoder 재정렬
      ↓
  [Multi-hop] (복잡 질문만) → 관계 추적
      ↓
  [Context Compression] → 중요 문장 추출
      ↓
  [동적 컨텍스트] → 적정 크기 결정
      ↓
  LLM → Answer
```

**예상 작업량:** 3일

---

### 9-4 기능 확장

#### 9-4-1: HWP 파일 지원

| 항목 | 내용 |
|------|------|
| **목표** | HWP 파일 파싱 및 임베딩 지원 |
| **산출물** | `backend/services/ingest/hwp_parser.py` |
| **예상 작업량** | 2일 |

#### 9-4-2: 통계/분석 대시보드

| 항목 | 내용 |
|------|------|
| **목표** | 시스템 사용 현황 및 지식 통계 시각화 |
| **산출물** | `web/src/pages/admin/statistics.html`, `backend/routers/system/statistics.py` |
| **기능** | 문서/청크/라벨 통계, 검색/질의 횟수, 인기 검색어/라벨 |
| **예상 작업량** | 2일 |

#### 9-4-3: 백업/복원 시스템

| 항목 | 내용 |
|------|------|
| **목표** | PostgreSQL + Qdrant 데이터 백업/복원 |
| **산출물** | `backend/routers/system/backup.py`, `scripts/backup/` |
| **예상 작업량** | 2일 |

---

### 9-5 코드 품질

| Task | 목표 | 예상 작업량 |
|------|------|-------------|
| 9-5-1 코드 리팩토링 | 중복 제거, 구조 개선 | 1.5일 |
| 9-5-2 타입 힌트 강화 | mypy 100% 통과 | 1일 |
| 9-5-3 API 문서화 개선 | OpenAPI 품질 향상 | 1일 |

---

## 5. 우선순위 및 의존성

### 5.1 우선순위

| 순위 | 단계 | 사유 |
|------|------|------|
| **1** | 9-3 AI 기능 고도화 | 핵심 가치 제공, 사용자 경험 향상 |
| **2** | 9-1 보안 강화 | 기반 인프라, 필수 요소 |
| **3** | 9-2 테스트 확대 | 안정성 확보 |
| **4** | 9-4 기능 확장 | 사용자 편의 기능 |
| **5** | 9-5 코드 품질 | 지속적 개선 |

### 5.2 의존성 그래프

```
9-1-2 (환경변수) → 9-1-1 (인증) → 9-1-3 (CORS) / 9-1-4 (Rate Limit)

9-3-3 (RAG 강화) → 9-3-1 (Reasoning 추천)
                 ↘
                   9-3-2 (지식구조 매칭)

9-2-1~3 (단위 테스트) → 9-2-4 (통합 테스트) → 9-2-5 (CI/CD)

9-4-1~3 → 독립적 진행 가능

9-5-1~3 → 독립적 진행 가능 (다른 작업과 병행)
```

### 5.3 추천 진행 순서

```
Week 1: 9-3-3 (RAG 강화) - 기반 작업
Week 2: 9-3-1 (Reasoning 추천) + 9-3-2 (지식구조 매칭)
Week 3: 9-1 (보안 강화 전체)
Week 4: 9-2-1~3 (단위 테스트)
Week 5: 9-2-4~5 (통합 테스트, CI/CD) + 9-4-1 (HWP)
Week 6: 9-4-2~3 (통계, 백업) + 9-5 (코드 품질)
```

---

## 6. 완료 기준

### 6.1 Phase 9 완료 조건

| 영역 | 완료 기준 |
|------|-----------|
| **AI 기능** | Reasoning 추천 API 동작, RAG Hybrid Search 적용, Import 시 자동 매칭 |
| **보안** | API 인증 동작, 환경변수 비밀번호, CORS/Rate Limit 설정 |
| **테스트** | 테스트 커버리지 70% 이상, CI/CD 파이프라인 동작 |
| **기능** | HWP 지원, 통계 대시보드, 백업/복원 동작 |
| **품질** | mypy 검사 통과, API 문서 완성 |

### 6.2 KPI

| 지표 | 현재 | 목표 |
|------|------|------|
| RAG 검색 정확도 | ~70% | 85% |
| Reasoning 추천 활용률 | 0% | 50% |
| Import 자동 라벨링률 | 30% | 80% |
| 보안 점수 | 60/100 | 85/100 |
| 테스트 커버리지 | ~20% | 70% |

---

## 7. 제외 항목

### 7.1 n8n 관련 (Phase 8 보류)

| 항목 | 사유 |
|------|------|
| n8n 워크플로우 개발 | 별도 프로젝트 권장 |
| Discord 승인 루프 | n8n 의존 |
| Todo-List 자동 생성 (n8n) | n8n 의존 |

### 7.2 기타 제외

| 항목 | 사유 |
|------|------|
| 외부 클라우드 연동 | 로컬 우선 방침 |
| 모바일 앱 | 웹 UI 우선 |
| 다국어 지원 | 한국어 전용 프로젝트 |

---

## 부록

### A. 예상 총 작업량

| 단계 | 예상 일수 |
|------|-----------|
| 9-1 보안 강화 | 4일 |
| 9-2 테스트 확대 | 4.5일 |
| 9-3 AI 기능 고도화 | **8.5일** |
| 9-4 기능 확장 | 6일 |
| 9-5 코드 품질 | 3.5일 |
| **합계** | **26.5일** |

### B. 필요 라이브러리 (예상)

| 용도 | 라이브러리 |
|------|------------|
| 인증 | python-jose, passlib |
| Rate Limiting | slowapi |
| HWP 파싱 | pyhwp, olefile |
| Reranking | sentence-transformers (cross-encoder) |
| 키워드 검색 | PostgreSQL full-text search |
| 테스트 커버리지 | pytest-cov |
| 타입 검사 | mypy |

### C. 9-3 AI 기능 고도화 상세 설계

#### C.1 Reasoning 추천 응답 예시

```json
{
  "answer": "이 프로젝트는...",
  "context_chunks": [...],
  "recommendations": {
    "related_chunks": [
      {"id": 42, "title": "Phase 8 설계", "similarity": 0.89},
      {"id": 56, "title": "API 구조", "similarity": 0.85}
    ],
    "suggested_labels": [
      {"id": 5, "name": "architecture", "confidence": 0.92},
      {"id": 12, "name": "design-pattern", "confidence": 0.78}
    ],
    "sample_questions": [
      "이 설계의 장단점은?",
      "향후 확장 계획은?"
    ],
    "explore_more": [
      {"type": "project", "id": 2, "name": "Phase 9"},
      {"type": "label", "id": 8, "name": "security"}
    ]
  }
}
```

#### C.2 Import 시 지식구조 매칭 응답 예시

```json
{
  "document": {...},
  "chunks": [...],
  "structure_matching": {
    "suggested_category": {
      "label_id": 15,
      "name": "development-docs",
      "confidence": 0.88
    },
    "suggested_labels": [
      {"label_id": 3, "name": "python", "source": "keyword_extraction"},
      {"label_id": 7, "name": "api", "source": "similar_document"}
    ],
    "similar_documents": [
      {"id": 24, "title": "API Guide", "similarity": 0.82}
    ],
    "relation_candidates": [
      {"target_chunk_id": 156, "relation_type": "related_to", "confidence": 0.75}
    ]
  }
}
```

---

**문서 상태**: ✅ 확정 (Confirmed)
**확정일**: 2026-02-01
**현재 진행**: Phase 9-3 (AI 기능 고도화)
**다음 Phase**: Phase 9-1 (보안 강화)
