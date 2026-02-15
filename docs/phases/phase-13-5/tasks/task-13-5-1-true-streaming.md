# Task 13-5-1: [BE] True Streaming (ollama_generate_stream 기반 SSE)

**우선순위**: 13-5 내 1순위 (선행)
**예상 작업량**: 중대 (1.5일)
**의존성**: 없음 (ai.py 직접 수정)
**상태**: TODO

**기반 문서**: `phase-13-5-todo-list.md`
**Plan**: `phase-13-5-plan.md`
**참조**: [260210-1430-local-llm-analysis-and-improvement.md](../../../overview/260210-1430-local-llm-analysis-and-improvement.md)

---

## 1. 개요

### 1.1 현재 상태

`/api/ask/stream`이 Pseudo-streaming: Ollama에서 전체 응답을 받은 후 청크 단위로 분할 전송. TTFT(Time To First Token) 지연이 큼.

### 1.2 목표

Ollama `/api/generate` stream=true를 사용하여, 토큰이 생성되는 즉시 SSE(Server-Sent Events)로 클라이언트에 전달한다.

---

## 2. 파일 변경 계획

| 파일 | 변경 내용 |
|------|----------|
| `backend/services/ai/ollama_client.py` | `ollama_generate_stream` 함수 추가 (generator 반환) |
| `backend/routers/ai/ai.py` | `/api/ask/stream` 스트리밍 로직 전환 |

---

## 3. 작업 체크리스트

- [ ] ollama_client에 stream 함수 구현
- [ ] ai.py 스트리밍 엔드포인트 전환
- [ ] SSE 이벤트 형식 유지 (호환)
- [ ] TTFT 개선 측정
- [ ] 에러/중단 처리
- [ ] 프론트엔드 호환 확인

---

## 4. 참조

- Phase 13 Master Plan §L-1
- Ollama API 문서: stream=true
