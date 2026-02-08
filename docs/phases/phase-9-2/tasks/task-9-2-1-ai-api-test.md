# Task 9-2-1: AI API 테스트

**우선순위**: 9-2 내 1순위
**예상 작업량**: 1일
**의존성**: 없음
**상태**: ✅ 구현 완료 (tests/test_ai_api.py 생성)

**기반 문서**: [phase-9-2-todo-list.md](../phase-9-2-todo-list.md)

---

## 1. 개요

### 1.1 목표

AI 라우터 및 RAG 파이프라인(Phase 9-3 구현물)에 대한 API 테스트를 작성하여 동작·엣지 케이스를 검증한다.

### 1.2 테스트 대상

| 대상           | 엔드포인트/기능                                          | 비고             |
| -------------- | -------------------------------------------------------- | ---------------- |
| AI 라우터      | `POST /api/ai/ask`, `GET /api/ai/models`                 | Ollama 연동      |
| RAG 파이프라인 | Hybrid Search, Reranking, Context Manager, Multi-hop RAG | Phase 9-3 구현물 |
| 엣지 케이스    | LLM 타임아웃, Qdrant 연결 실패                           | 폴백·에러 처리   |

---

## 2. 파일 변경 계획

### 2.1 신규 생성

| 파일 경로              | 용도               |
| ---------------------- | ------------------ |
| `tests/test_ai_api.py` | AI API 단위 테스트 |

### 2.2 수정

- 없음 (기존 AI 라우터는 그대로 두고 테스트만 추가)

---

## 3. 작업 체크리스트

### 3.1 AI 라우터 테스트

- [ ] `tests/test_ai_api.py` 생성
- [ ] `POST /api/ai/ask` 테스트
  - [ ] 정상 질문 응답
  - [ ] 빈 질문 에러
  - [ ] 컨텍스트 없을 때 처리
- [ ] `GET /api/ai/models` 테스트 (Ollama 모델 목록)

### 3.2 RAG 파이프라인 테스트 (Phase 9-3 구현물)

- [ ] Hybrid Search 테스트
- [ ] Reranking 테스트
- [ ] Context Manager 테스트
- [ ] Multi-hop RAG 테스트

### 3.3 엣지 케이스 테스트

- [ ] LLM 타임아웃 시 폴백
- [ ] Qdrant 연결 실패 시 처리

---

## 4. 참고 문서

- [Phase 9-2 Todo List](../phase-9-2-todo-list.md)
- [Phase 9-3 RAG 강화](../phase-9-3/tasks/task-9-3-3-rag-enhancement.md)
- 기존 테스트: `tests/test_hybrid_search.py`
