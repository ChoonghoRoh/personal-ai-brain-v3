# Phase 9-3 개발 진행 가이드

**Phase**: 9-3 AI 기능 고도화
**전체 예상 작업량**: 8.5일
**Task 수**: 3개

---

## 개발 시작 전 필수 확인

### 1. 프로젝트 구조 파악
```
backend/
├── services/
│   ├── search/          # 검색 서비스 (9-3-3 주요 작업 위치)
│   ├── ai/              # AI 서비스 (context_manager 추가)
│   ├── reasoning/       # 추론 서비스 (9-3-1 작업 위치)
│   └── knowledge/       # 지식 서비스 (9-3-2 작업 위치)
├── routers/
│   ├── ai/              # AI API
│   ├── search/          # 검색 API
│   ├── reasoning/       # 추론 API
│   └── knowledge/       # 지식 API
└── models/
    └── models.py        # SQLAlchemy 모델 정의
```

### 2. 핵심 기존 코드 확인
개발 전 반드시 아래 파일들의 현재 구조를 확인:

| 파일 | 확인할 내용 |
|------|------------|
| `backend/services/search/search_service.py` | SearchService 클래스, search() 메서드 시그니처 |
| `backend/routers/ai/ai.py` | prepare_question_context() 함수, ask 엔드포인트 |
| `backend/routers/reasoning/reason.py` | generate_reasoning_answer() 함수 |
| `backend/models/models.py` | KnowledgeChunk, KnowledgeRelation, Label 모델 |

### 3. 환경 확인
```bash
# Docker 서비스 실행 확인
docker-compose ps

# 필요 서비스: backend, postgres, qdrant, ollama
```

---

## Task 개발 순서

```
┌─────────────────────────────────────────────────────────────┐
│                    Phase 9-3 개발 순서                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [1] Task 9-3-3: RAG 기능 강화 (3일) ★ 최우선               │
│      ├── Step 1: Hybrid Search 구현                        │
│      ├── Step 2: Reranking 구현                            │
│      ├── Step 3: Context Manager 구현                      │
│      ├── Step 4: Multi-hop RAG 구현                        │
│      ├── Step 5: AI 라우터 통합                            │
│      └── Step 6: 테스트                                    │
│           │                                                 │
│           ▼ (완료 후 병렬 진행 가능)                        │
│  ┌────────┴────────┐                                        │
│  │                 │                                        │
│  ▼                 ▼                                        │
│  [2] Task 9-3-1   [3] Task 9-3-2                           │
│  Reasoning 추천   지식구조 매칭                             │
│  (3일)           (2.5일)                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Task 목록 및 상세 문서

| 순서 | Task ID | 이름 | 작업량 | 의존성 | 상세 문서 |
|------|---------|------|--------|--------|-----------|
| 1 | 9-3-3 | RAG 기능 강화 | 3일 | 없음 | [task-9-3-3-rag-enhancement.md](./task-9-3-3-rag-enhancement.md) |
| 2 | 9-3-1 | Reasoning AI 추천 | 3일 | 9-3-3 | [task-9-3-1-reasoning-recommendation.md](./task-9-3-1-reasoning-recommendation.md) |
| 3 | 9-3-2 | 지식구조 자동 매칭 | 2.5일 | 9-3-3 | [task-9-3-2-knowledge-structure-matching.md](./task-9-3-2-knowledge-structure-matching.md) |

---

## 파일 변경 총괄

### 신규 생성 파일 (총 10개)

| Task | 파일 경로 | 용도 |
|------|----------|------|
| 9-3-3 | `backend/services/search/hybrid_search.py` | Hybrid Search 서비스 |
| 9-3-3 | `backend/services/search/reranker.py` | Reranking 서비스 |
| 9-3-3 | `backend/services/ai/context_manager.py` | Context 관리 서비스 |
| 9-3-3 | `backend/services/search/multi_hop_rag.py` | Multi-hop RAG 서비스 |
| 9-3-1 | `backend/services/reasoning/recommendation_service.py` | 추천 로직 서비스 |
| 9-3-1 | `backend/services/reasoning/dynamic_reasoning_service.py` | LLM 동적 추론 |
| 9-3-1 | `backend/routers/reasoning/recommendations.py` | 추천 API 라우터 |
| 9-3-2 | `backend/services/knowledge/structure_matcher.py` | 구조 매칭 서비스 |
| 9-3-2 | `backend/services/knowledge/auto_labeler.py` | 자동 라벨링 서비스 |
| 공통 | `tests/test_*.py` (4개) | 테스트 파일 |

### 수정 파일 (총 12개)

| Task | 파일 경로 | 수정 내용 |
|------|----------|----------|
| 9-3-3 | `backend/services/search/search_service.py` | Hybrid Search 통합 |
| 9-3-3 | `backend/routers/ai/ai.py` | RAG 파이프라인 개선 |
| 9-3-3 | `backend/routers/search/search.py` | Hybrid 옵션 추가 |
| 9-3-3 | `backend/config.py` | RAG 설정 상수 추가 |
| 9-3-1 | `backend/routers/reasoning/reason.py` | LLM 추론, recommendations 필드 |
| 9-3-1 | `web/src/pages/reason.html` | 추천 UI 추가 |
| 9-3-1 | `web/public/js/reason.js` | 추천 표시 로직 |
| 9-3-2 | `backend/routers/knowledge/knowledge.py` | 청크 생성 시 추천 |
| 9-3-2 | `backend/routers/knowledge/approval.py` | 승인 시 관계 추천 |
| 9-3-2 | `backend/routers/search/documents.py` | 문서 카테고리 추천 |
| 공통 | `backend/services/*/__init__.py` | 모듈 export |
| 공통 | `backend/main.py` | 라우터 등록 |

---

## 개발 규칙

### 코드 품질 필수 사항
- [ ] 모든 함수/메서드에 타입 힌트 적용
- [ ] 모든 클래스/함수에 Docstring 작성
- [ ] 에러 발생 시 graceful 처리 (폴백 로직)
- [ ] 주요 동작에 로깅 적용 (`logger.info`, `logger.error`)

### 하위 호환성 필수 사항
- [ ] 기존 API 응답 필드 절대 삭제 금지 (추가만 허용)
- [ ] 기존 함수 시그니처 변경 시 기본값으로 호환성 유지
- [ ] 새 기능은 옵션 파라미터로 제공 (기본값 = 기존 동작)

### 테스트 필수 사항
- [ ] 신규 기능 단위 테스트 작성
- [ ] 기존 테스트 전체 통과 확인
- [ ] API 통합 테스트 작성

---

## 개발 시작 프롬프트

### Task 9-3-3 시작 시
```
Phase 9-3의 Task 9-3-3 (RAG 기능 강화) 개발을 시작합니다.

참조 문서:
- docs/phases/phase-9-3/tasks/task-9-3-3-rag-enhancement.md

Step 1 (Hybrid Search)부터 순차적으로 진행해주세요.
각 Step 완료 후 테스트를 실행하고, 완료되면 todo-list를 업데이트해주세요.
```

### Task 9-3-1 시작 시 (9-3-3 완료 후)
```
Phase 9-3의 Task 9-3-1 (Reasoning 추천) 개발을 시작합니다.

선행 완료: Task 9-3-3
참조 문서:
- docs/phases/phase-9-3/tasks/task-9-3-1-reasoning-recommendation.md

9-3-3에서 구현한 HybridSearchService, ContextManager를 활용해주세요.
```

### Task 9-3-2 시작 시 (9-3-3 완료 후)
```
Phase 9-3의 Task 9-3-2 (지식구조 매칭) 개발을 시작합니다.

선행 완료: Task 9-3-3
참조 문서:
- docs/phases/phase-9-3/tasks/task-9-3-2-knowledge-structure-matching.md

9-3-3에서 구현한 HybridSearchService를 활용해주세요.
```

---

## Task 완료 체크리스트

### 각 Task 완료 시 확인
- [ ] 모든 Step 구현 완료
- [ ] 단위 테스트 100% 통과
- [ ] 기존 테스트 영향 없음
- [ ] API 통합 테스트 통과
- [ ] todo-list 체크박스 업데이트
- [ ] 작업 로그 기록

### Phase 9-3 전체 완료 시 확인
- [ ] Task 9-3-3 완료
- [ ] Task 9-3-1 완료
- [ ] Task 9-3-2 완료
- [ ] 전체 테스트 통과
- [ ] Phase 9-3 todo-list 완료 표시
- [ ] 다음 Phase (9-1) 시작 준비

---

## 문제 해결 가이드

### Reranker 모델 로딩 느림
```python
# 싱글톤 패턴으로 한 번만 로딩
# reranker.py에서 모듈 레벨 인스턴스 생성
```

### Hybrid Search 성능 저하
```python
# PostgreSQL GIN 인덱스 확인
# keyword_weight 조정 (기본 0.3)
```

### LLM 호출 실패
```python
# 기존 템플릿으로 폴백 필수
# try-except로 graceful 처리
```
