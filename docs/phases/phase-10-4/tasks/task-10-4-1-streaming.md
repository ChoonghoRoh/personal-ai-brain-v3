# Task 10-4-1: LLM 스트리밍 응답 표시

**우선순위**: 10-4 내 1순위  
**예상 작업량**: 3일  
**의존성**: Phase 10-1·10-2 완료 후 권장  
**상태**: ✅ 완료

**기반 문서**: [phase-10-4-0-todo-list.md](../phase-10-4-0-todo-list.md)  
**작업 순서**: [phase-10-navigation.md](../../phase-10-navigation.md)

---

## 1. 개요

### 1.1 목표

Reasoning 실행 시 **LLM 응답을 스트리밍**으로 수신하여 **실시간으로 표시**한다. 사용자가 답변이 생성되는 과정을 단계적으로 볼 수 있도록 한다.

### 1.2 대상

| 대상        | 내용                                        |
| ----------- | ------------------------------------------- |
| 백엔드      | Reasoning API 스트리밍 응답 (SSE 또는 동등) |
| 프론트엔드  | 스트리밍 청크 수신 및 실시간 표시           |
| 10-1-2 취소 | 로딩·취소와 스트리밍 동작 정합성            |

---

## 2. 파일 변경 계획

### 2.1 신규/수정

| 파일 경로                                                    | 용도                                    |
| ------------------------------------------------------------ | --------------------------------------- |
| `backend/routers/reasoning/reason.py` (또는 별도 엔드포인트) | SSE/스트리밍 응답 지원                  |
| 백엔드 서비스 레이어                                         | Ollama/LLM 스트리밍 호출                |
| 프론트엔드: Reasoning 페이지                                 | EventSource 또는 fetch 스트림 수신·표시 |

---

## 3. 작업 체크리스트

### 3.1 백엔드

- [x] Reasoning API 스트리밍 응답 지원 (SSE `answer_token` 이벤트)
  - [x] `ollama_client.py`: `ollama_generate_stream()`, `_ollama_chat_stream()` 추가
  - [x] `dynamic_reasoning_service.py`: `generate_reasoning_stream()` 메서드 추가
  - [x] `reason_stream.py`: Stage 4에서 `_async_stream_tokens()` + `answer_token` SSE yield
- [x] 취소(10-1-2) 시 스트리밍 중단 처리 (토큰 루프 내 cancelled 확인)

### 3.2 프론트엔드

- [x] 스트리밍 청크 수신 (fetch stream + answer_token 이벤트 핸들링)
- [x] 실시간 표시 UI (`showStreamingAnswer()` → answer div에 토큰 추가)
- [x] 로딩·취소(10-1-2)와 스트리밍 동작 정합성 확인

---

## 4. 참고 문서

- [Phase 10-4 Plan](../phase-10-4-0-plan.md)
- [Phase 10-4 Todo List](../phase-10-4-0-todo-list.md)
- [Task 10-1-2 취소](../../phase-10-1/tasks/task-10-1-2-cancel.md)
- Reasoning API: `backend/routers/reasoning/reason.py`
