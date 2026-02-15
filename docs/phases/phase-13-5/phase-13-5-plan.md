# Phase 13-5 Plan — Backend Local LLM·Ollama 개선

**작성일**: 2026-02-16
**Phase**: 13-5 (4순위)
**목표**: True Streaming, 토큰 관리 정밀화, System Prompt 활용, 구조화 출력·주입 방어
**기준 문서**: [phase-13-master-plan.md](../phase-13-master-plan.md), [260210-1430-local-llm-analysis-and-improvement.md](../../overview/260210-1430-local-llm-analysis-and-improvement.md)

---

## 목표

Local LLM 분석 보고서 기반 Ollama·RAG 파이프라인 개선 4건:
1. True Streaming: `ollama_generate_stream` 기반으로 Ollama 토큰 생성 즉시 SSE 전달. TTFT 개선
2. 토큰 관리: tiktoken 또는 transformers Tokenizer 도입, ContextManager 한국어 친화, Context Window 초과 방어
3. System Prompt: Ollama `/api/chat`의 `role: system` 활용, 페르소나·제약 분리, 후처리 정규식 축소
4. (선택) 구조화 출력: Ollama `format="json"` 활용, LLM 프롬프트 주입 방어 검토·문서화

## Task 구성

| Task | 도메인 | 목표 | 변경 파일 | 예상 |
|------|--------|------|----------|------|
| 13-5-1 | [BE] | True Streaming (ollama_generate_stream 기반 SSE) | ai.py, ollama_client.py | 1.5일 |
| 13-5-2 | [BE] | 토큰 관리 정밀화 (tiktoken/transformers, ContextManager) | ContextManager, requirements.txt | 1.5일 |
| 13-5-3 | [BE] | System Prompt (role: system, 후처리 축소) | ai.py, ollama_client.py, 프롬프트 문서 | 1일 |
| 13-5-4 | [BE] | (선택) 구조화 출력·프롬프트 주입 방어 | ollama_client.py, 보안 문서 | 0.5일 |

## 구현 순서

1. 13-5-1 (선행 — ai.py 스트리밍 로직 전환)
2. 13-5-2 (독립 — ContextManager 수정)
3. 13-5-3 (13-5-1과 연동 시 이후)
4. 13-5-4 (선택, 13-5-3 이후 권장)

## 의존성

- Phase 13-2 완료 후 또는 병렬 가능
- 13-5-1 → 13-5-3 (ai.py 스트리밍·System Prompt 연동)
- 13-5-3 → 13-5-4 (프롬프트 구조 확립 후 주입 방어)

## 검증 방법

- `/api/ask/stream` SSE 즉시 토큰 전달 확인 (TTFT 측정)
- 토큰 계산 정밀도: 한국어 텍스트 chars//4 vs tiktoken 비교
- System Prompt 적용 후 LLM 응답 품질·한국어 전용 확인
- (선택) JSON 출력 파싱 성공률 확인

## Out of Scope

- 최신 모델 교체 (DeepSeek-R1, Llama-3.1)
- 양자화 최적화 (GGUF Q4_K_M)
- 임베딩 모델 고도화 (BGE-M3, multilingual-e5-large)
→ 별도 Phase·백로그
