# 🧠 Local LLM Inspection & Improvement Report

**Date:** 2026-02-10 14:30
**Project:** Personal AI Brain v3
**Scope:** Local LLM Inference (Ollama) & RAG Pipeline

---

## 1. 현황 분석 (Inspection Summary)

### 1.1 기술 스택
- **Inference Engine:** Ollama (Local API)
- **Primary Model:** `qwen2.5:7b` (Config default), `EEVE-Korean-10.8B` (Implementation reference)
- **Framework:** FastAPI + Python 3.11
- **Integration:** `ollama_client.py`를 통한 REST API 통신 (urllib 사용)

### 1.2 주요 기능 및 검증 결과
- **[성공] Ollama 클라이언트 구현:** `generate` 및 `chat` API를 유연하게 지원하며, 모델 특성(instruct/eeve)에 따른 자동 폴백 로직이 견고함.
- **[성공] RAG 파이프라인:** 단순 검색뿐만 아니라 Hybrid Search, Reranking, Multi-hop RAG를 지원하여 컨텍스트 품질을 높임.
- **[부분 성공] 스트리밍:** SSE(/api/ask/stream)를 지원하지만, 실제로는 LLM 전체 응답을 기다린 후 청크로 나누어 전송하는 'Pseudo-streaming' 방식임.
- **[주의] 프롬프트 제어:** "한국어로만 답변"을 강제하기 위해 프롬프트 지시와 후처리(post-processing) 정규식을 과도하게 사용함. 이는 코드 블록이나 유용한 영문 전문 용어까지 삭제할 위험이 있음.

---

## 2. 기능 및 검증 결과 (Verification)

| 항목 | 검증 결과 | 비고 |
| :--- | :--- | :--- |
| **연결성** | Ollama 서비스 미실행 시 적절한 에러 메시지 및 폴백 답변 제공 확인. | `ollama_connection_check` 활용 |
| **컨텍스트 제한** | 프롬프트가 길어질 경우 자동으로 컨텍스트를 축소(1600자 제한)하는 방어 로직 작동. | `generate_ai_answer` 내 로직 |
| **토큰 계산** | `chars // 4` 방식의 근사치를 사용 중. 한글 환경에서는 오차가 큼. | `ContextManager` 내 구현 |
| **보안** | LLM 프롬프트 주입(Injection)에 대한 방어 로직은 프롬프트 지시사항 수준에 머물러 있음. | - |

---

## 3. 기능 개선 방향 (Functional Improvements)

### 3.1 True Streaming 도입
- **문제:** 현재 방식은 첫 토큰이 나오기까지 사용자 대기 시간이 긺 (TTFT 지연).
- **개선:** `ollama_generate_stream`을 사용하여 Ollama가 토큰을 생성하는 즉시 SSE로 클라이언트에 전달하도록 수정.

### 3.2 정밀한 토큰 관리
- **문제:** 현재 `chars // 4` 방식은 한국어 토큰을 과소평가하여 런타임 시 Context Window 초과 에러(400 Bad Request)를 유발할 수 있음.
- **개선:** `tiktoken` 또는 `transformers` 라이브러리의 Tokenizer를 사용하여 정확한 토큰 수를 계산하고, 모델별 최대 컨텍스트(4k~32k)에 맞춰 동적으로 RAG 범위를 확장.

### 3.3 System Prompt 활용
- **문제:** User Prompt 맨 앞에 "한국어로만 답변하세요" 등의 지시사항을 매번 붙여 프롬프트가 지저분함.
- **개선:** Ollama의 `/api/chat` 인터페이스에서 `role: system`을 활용하여 페르소나와 제약사항을 분리 정의.

### 3.4 구조화된 출력 (Structured Output)
- **문제:** 텍스트에서 정보를 추출할 때 정규식에 의존함.
- **개선:** Ollama의 `format="json"` 옵션을 활용하여 지식 추출이나 요약 시 JSON 형태의 안정적인 데이터를 확보.

---

## 4. 모델 개선 방향 (Model Improvements)

### 4.1 최신 모델 교체 제안
- **DeepSeek-R1-Distill-Qwen-7B:** 현재 Qwen 2.5보다 추론(Reasoning) 능력이 월등히 뛰어나며 한국어 지원이 우수함.
- **Llama-3.1-8B-Instruct (Korean Finetuned):** 더 긴 컨텍스트 윈도우(128k)와 높은 안정성을 제공.

### 4.2 양자화(Quantization) 최적화
- **GGUF Q4_K_M / Q5_K_M:** 8GB~16GB RAM 환경에서 성능 저하를 최소화하면서 추론 속도를 최적화할 수 있는 최적의 양자화 비트수 권장.

### 4.3 임베딩 모델 고도화
- 현재 `paraphrase-multilingual-MiniLM-L12-v2` 사용 중.
- **개선:** `BAAI/bge-m3` 또는 `intfloat/multilingual-e5-large`와 같이 한국어 의미 파악 능력이 더 뛰어난 모델로 교체하여 RAG의 정확도 향상.

---

## 5. 결론 및 다음 작업 (Next Steps)

1. **[구현]** `backend/routers/ai/ai.py`의 스트리밍 로직을 `ollama_generate_stream` 기반의 진정한 스트리밍으로 전환.
2. **[테스트]** DeepSeek-R1 모델을 로컬에 로드하여 현재 RAG 파이프라인과의 정합성 테스트.
3. **[최적화]** `ContextManager`의 토큰 계산 로직을 한국어 친화적으로 수정.
