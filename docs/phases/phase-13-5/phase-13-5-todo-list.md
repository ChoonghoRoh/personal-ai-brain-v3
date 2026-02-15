# Phase 13-5 Todo List — Backend Local LLM·Ollama 개선

**Phase**: 13-5
**작성일**: 2026-02-16

---

## Task 13-5-1 [BE] True Streaming (ollama_generate_stream 기반 SSE) ✅

- [x] ollama_client.py `ollama_generate_stream` 함수 확인 (기존 구현 활용)
- [x] Ollama `/api/generate` stream=true 연동
- [x] `backend/routers/ai/ai.py` `/api/ask/stream` 엔드포인트 전환:
  - [x] 기존 Pseudo-streaming (전체 응답 대기 후 10자 청크 전송) 제거
  - [x] Ollama 토큰 생성 즉시 SSE 이벤트로 전달
- [x] SSE 이벤트 형식 유지 (기존 클라이언트 호환)
- [x] TTFT(Time To First Token) 개선 확인 — 토큰 즉시 전달
- [x] 에러 처리: Ollama 스트림 중단 시 SSE 에러 이벤트
- [x] 프론트엔드 ask/stream 소비부 호환 확인

## Task 13-5-2 [BE] 토큰 관리 정밀화 ✅

- [x] tiktoken 선택 (cl100k_base 인코딩)
- [x] requirements.txt 의존성 추가: `tiktoken>=0.5.0`
- [x] 토큰 계산 유틸리티 함수 구현:
  - [x] tiktoken 로드 (미설치 시 graceful fallback)
  - [x] 정확한 토큰 수 계산 (`_approx_tokens()`)
- [x] ContextManager 한국어 친화 수정:
  - [x] `CHARS_PER_TOKEN_APPROX` 4→2로 변경 (한국어 1.5~2 토큰/문자)
  - [x] tiktoken 사용 가능 시 정확 계산, 아니면 근사치 폴백
- [x] 기존 답변 품질 회귀 확인 — /api/ask 정상 응답

## Task 13-5-3 [BE] System Prompt 활용 ✅

- [x] Ollama `/api/generate` system 파라미터 + `/api/chat` role:system 메시지 지원
- [x] `system_prompt` 파라미터를 ollama_client.py 전 함수에 추가
- [x] `AI_SYSTEM_PROMPT` 상수 생성 (한국어 전용, 중국어 금지 등)
- [x] User Prompt에서 시스템 지시 제거 — `build_prompt()` 간소화
- [x] 과도한 후처리 정규식 축소:
  - [x] `postprocess_answer()` ~50줄 → ~10줄로 축소
  - [x] 이모지 제거 + 영문 문장 제거만 최소 유지
- [x] generate_ai_answer() + generate_streaming_answer() 모두 system_prompt 전달

## Task 13-5-4 [BE] (선택) 구조화 출력·프롬프트 주입 방어 — SKIP

- [ ] Ollama `format="json"` 옵션 활용 경로 식별
- [ ] LLM 프롬프트 주입 방어 현황 검토
- 사유: 13-5-1/2/3으로 핵심 개선 완료, 별도 Phase에서 진행 가능
