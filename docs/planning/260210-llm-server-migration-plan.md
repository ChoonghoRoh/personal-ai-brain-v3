# 🏗️ 독립형 로컬 LLM 서버 이전 및 운용 계획

**작성일:** 2026-02-10  
**검증일:** 2026-02-10 (§6 검증 및 교차 검증 추가)  
**목표:** 개인용 AI 두뇌(Personal AI Brain v3)의 추론 엔진을 고사양 독립 서버로 분리하여 성능, 응답 속도, 안정성을 극대화한다.

**관련 문서:** [Phase 13 Master Plan](../phases/phase-13-master-plan.md) (Local LLM 개선 13-5), [Local LLM 분석·개선 보고서](../overview/260210-1430-local-llm-analysis-and-improvement.md)

---

## 1. 서버 사양 분석 및 한계점

### 🖥️ Hardware Spec
- **CPU:** AMD Ryzen 7 3800X (8 Core / 16 Thread) - *데이터 전처리 및 벡터 DB 연산에 충분*
- **RAM:** 32GB (DDR4 3200MHz, 16GB x 2) - *시스템 메모리 여유 있음 (모델 Offloading 가능)*
- **GPU:** NVIDIA RTX 5070 Ti (16GB VRAM) - *핵심 자원*
- **Storage:** NVMe M.2 SSD 1TB - *모델 가중치 및 벡터 데이터 저장에 충분*

### ⚠️ 자원 운용 제약 사항 (Critical Constraints)
- **VRAM 16GB 한계:**
    - LLM 추론 속도는 VRAM에 모델이 전적으로 올라갔을 때 가장 빠름.
    - **14B 모델 (Q4 양자화)** 기준 약 9~10GB VRAM 소모 → **여유 공간 6GB**.
    - **32B 모델 (Q4 양자화)** 기준 약 18~20GB 소모 → **VRAM 초과 (시스템 RAM 사용 시 속도 급감)**.
    - **결론:** 주력 모델은 **7B ~ 14B 사이즈**로 선정하고, 양자화(Quantization)를 적극 활용해야 함.

---

## 2. 모델 선정 및 운용 계획 (Model Portfolio)

Ollama 기반으로 운용하며, **단일 범용 모델**보다는 **작업별 특화 모델(Expert Models)**을 스위칭하거나 라우팅하는 전략을 추천합니다.

### 2.1 추천 모델 라인업 (Ollama Library)

| 역할 (Role) | 추천 모델 (Model ID) | 파라미터 | 양자화 (Rec.) | VRAM 점유(est.) | 선정 이유 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **메인 두뇌 (General/Reasoning)** | **DeepSeek-R1-Distill-Qwen-14B** | 14B | Q4_K_M | ~9.5 GB | 현존 최강의 추론 능력 + 한국어 성능 우수. 16GB VRAM에 최적. |
| **코딩/엔지니어링 (Developer)** | **Qwen2.5-Coder-14B-Instruct** | 14B | Q4_K_M | ~9.0 GB | 코드 생성, 리팩토링, 버그 분석에 특화. |
| **빠른 응답/검색 (Speed/RAG)** | **EEVE-Korean-10.8B** | 10.8B | Q5_K_M | ~8.0 GB | 한국어 자연스러움 최상. RAG 요약용으로 적합. |
| **초경량 라우터 (Router)** | **Llama-3.2-3B** | 3B | Q8_0 | ~4.0 GB | 단순 분류, 의도 파악, JSON 포맷팅용. |

### 2.2 양자화(Quantization) 전략
- **Q4_K_M (4-bit Medium):** 성능 손실은 거의 없으면서 메모리 사용량을 절반으로 줄이는 **Golden Standard**. 14B 모델 구동 시 필수.
- **Q5_K_M / Q6_K:** 7B~10B 이하 모델 사용 시 여유가 있다면 선택하여 정밀도 향상.

---

## 3. 프로젝트 기능별 모델 활용 방안

Personal AI Brain v3의 기존 메뉴와 기능에 맞춰 모델을 할당합니다.

### A. 🧠 Brain/Reasoning (심층 추론 및 의사결정)
- **대상 기능:** 복잡한 질문, 계획 수립(Planning), 페르소나 기반 대화.
- **할당 모델:** `DeepSeek-R1-Distill-Qwen-14B`
- **활용:** 
    - 사용자의 불명확한 지시를 구체적인 Task로 변환.
    - "생각하는 과정(Chain of Thought)"을 포함하여 논리적 답변 제공.

### B. 🔍 Search & RAG (지식 검색 및 요약)
- **대상 기능:** `/api/ask` (지식베이스 질의), 문서 요약, 검색 결과 재랭킹.
- **할당 모델:** `EEVE-Korean-10.8B` 또는 `Qwen2.5-14B`
- **활용:**
    - 한국어 문맥 이해도가 높은 모델을 사용하여 검색된 청크(Chunk)를 매끄럽게 요약.
    - 8k~16k 컨텍스트 윈도우를 활용해 다량의 문서를 한 번에 처리.

### C. 💻 Dev/Coding (코드 생성 및 리뷰)
- **대상 기능:** 자동화 스크립트 작성, 코드 리팩토링 제안, 버그 원인 분석.
- **할당 모델:** `Qwen2.5-Coder-14B`
- **활용:**
    - Python(FastAPI), JS(React/Vanilla) 코드 생성 시 문법 정확도 보장.
    - FIM(Fill-In-the-Middle) 기능을 활용한 코드 자동 완성 지원.

---

## 4. 모델 튜닝 및 고도화 계획 (Tuning Roadmap)

단순 프롬프트 엔지니어링을 넘어, 프로젝트 데이터를 모델에 학습시키는 계획입니다.

### 1단계: System Prompt Optimization (즉시 적용)
- **목표:** 모델 교체 없이 페르소나 및 응답 형식을 제어.
- **방법:** `backend/services/ai/ollama_client.py` 수정.
    - `DeepSeek-R1`용 시스템 프롬프트: "Think step-by-step before answering..."
    - JSON 출력 강제: Ollama의 `format='json'` 옵션 활용.

### 2단계: RAG 파이프라인 최적화 (데이터 튜닝)
- **목표:** 모델이 프로젝트의 문맥(SSOT, 문서 구조)을 더 잘 이해하도록 함.
- **방법:**
    - 임베딩 모델 교체: `multilingual-e5-large` (한국어 검색 성능 향상).
    - 메타데이터 필터링 강화: 파일 경로, 태그 등을 활용해 LLM에 주입되는 컨텍스트의 '순도'를 높임.

### 3단계: LoRA Fine-tuning (장기 목표)
- **목표:** 프로젝트 특화 말투, 코딩 스타일(Vanilla JS 모듈화 등), 도메인 지식 주입.
- **대상:** `Qwen2.5-14B` 또는 `Llama-3.1-8B`.
- **방법 (Unsloth 활용):**
    1.  **데이터셋 구축:**
        - `docs/**/*.md` (프로젝트 규칙 및 설계 철학)
        - `backend/**/*.py`, `web/**/*.js` (선호하는 코딩 스타일)
        - 기존 QA 로그 (질문-답변 쌍)
    2.  **학습 환경:**
        - 독립 서버의 **5070 Ti (16GB)**를 활용하여 학습 진행.
        - **LoRA (Low-Rank Adaptation)** 방식을 사용하여 가중치 일부만 학습 (VRAM 10GB 내외로 가능).
    3.  **적용:**
        - 학습된 LoRA 어댑터(`.gguf` 변환)를 Ollama 모드파일(`Modelfile`)에 적용하여 서빙.

---

## 5. 서버 구축 및 네트워크 연결 방안

### 5.1 인프라 구축 단계 (Implementation Checklist)

1.  **OS 설치:** Ubuntu 22.04 LTS 또는 24.04 LTS 권장 (드라이버 안정성 및 Docker 호환성).
2.  **GPU 드라이버 및 툴킷:**
    - NVIDIA Driver (550+ 버전 권장) 설치.
    - `nvidia-smi`로 5070 Ti 인식 확인.
3.  **Docker 및 NVIDIA Container Toolkit:**
    - Docker Engine 설치.
    - GPU 가속을 위해 `nvidia-container-toolkit` 설정 (Ollama 컨테이너 사용 시 필수).
4.  **Ollama 서비스 구성:**
    - Docker Compose를 통한 Ollama 서빙 (GPU 자원 할당 설정).
    - `OLLAMA_HOST=0.0.0.0` 설정을 통해 외부(메인 서버) 접근 허용.
    - 모델 사전 다운로드 (`ollama pull deepseek-r1:14b` 등).

### 5.2 네트워크 연결 및 보안 방안 (Network Topology)

- **IP 할당:** 독립 LLM 서버에 내부망 고정 IP 할당 (예: `192.168.0.100`).
- **연결 프로토콜:** REST API (Port 11434).
- **보안 강화 (Nginx Reverse Proxy):**
    - Ollama 앞단에 Nginx 설치.
    - **API Key 인증:** `proxy_set_header Authorization` 등을 활용해 허용된 서버(메인 프로젝트 서버)만 접근 가능하도록 설정.
    - **IP 화이트리스트:** 메인 서버의 IP만 11434(또는 80/443) 포트로 접근 가능하도록 `ufw` 방화벽 설정.
- **메인 서버 설정 업데이트:**
    - `backend/.env` 파일의 `OLLAMA_BASE_URL`을 독립 서버의 IP로 수정.
    - 로컬 DNS 사용 시 `/etc/hosts`에 `llm-server 192.168.0.100` 등록 후 도메인으로 접근.

---

## 6. 검증 및 교차 검증 (Verification & Cross-Check)

**검증일:** 2026-02-10  
**대상:** 본 계획서 §1~§5 vs 현재 프로젝트 코드·Phase 13 Master Plan·Local LLM 분석 보고서.

### 6.1 현재 프로젝트 파일 검증

| 계획서 항목 | 프로젝트 현황 | 일치 여부 | 비고 |
|-------------|---------------|:---------:|------|
| `OLLAMA_BASE_URL` | `backend/config.py` + `.env` 에서 로드, 기본값 `http://localhost:11434` | ✅ | 독립 서버 이전 시 .env만 수정하면 됨 |
| `ollama_client.py` 수정 (System Prompt, format=json) | `backend/services/ai/ollama_client.py`: `/api/chat` 사용 시 `messages`에 `role: user`만 존재. `role: system`·`format` 옵션 없음 | ❌ | **기능 업그레이드 필요** (Phase 13-5-3, 13-5-4) |
| 스트리밍 API | `backend/routers/ai/ai.py` `/api/ask/stream` → `generate_streaming_answer()` 내부에서 `ollama_generate()`(비스트리밍) 호출 후 응답을 10자 청크로 분할 전송 (Pseudo-streaming) | ❌ | **True Streaming 미적용**. `ollama_generate_stream`은 `ollama_client.py`에 이미 구현됨. ai.py만 전환 필요 (Phase 13-5-1) |
| 토큰 계산 | `backend/services/ai/context_manager.py`: `CHARS_PER_TOKEN_APPROX = 4`, `len(text)//4` 근사. `CONTEXT_MAX_TOKENS_SIMPLE=800`, `COMPLEX=2000` (config) | ⚠️ | 한글 오차·Context Window 초과 위험. **정밀 토큰 관리 업그레이드 필요** (Phase 13-5-2) |
| RAG 컨텍스트 길이 | `ai.py` `prepare_question_context`: `MAX_CONTEXT_LENGTH = 1000`(문자). enhanced 경로는 `ContextManager.build_context` 사용 | ⚠️ | 단순 경로는 문자 기준 1000자 고정. Phase 13-5-2와 연동 시 토큰 기준 통일 권장 |
| 모델 단일/다중 | 현재 `OLLAMA_MODEL`, `OLLAMA_MODEL_LIGHT`(라벨·키워드 등)만 사용. 기능별 모델(Brain/Search/Dev) 스위칭 없음 | ❌ | **§3 기능별 모델 활용** 반영 시 라우팅 로직 추가 필요 (본 계획서 범위 내 구현 항목으로 명시 권장) |

### 6.2 기능 업그레이드 필요 부문 교차 검증

아래는 **기능 업그레이드가 필요한 부분**을 Phase 13 Master Plan·Local LLM 분석 보고서와 교차 검증한 결과이다.

| # | 기능 업그레이드 항목 | 본 계획서(§) | Phase 13 Master Plan | Local LLM 분석 보고서 | 현재 코드 상태 |
|---|----------------------|-------------|----------------------|------------------------|----------------|
| 1 | **True Streaming** | §6 Next Steps "스트리밍 API 동작 여부" | 13-5-1: `ollama_generate_stream` 기반 SSE | §3.1 True Streaming 도입 | ai.py: `ollama_generate` 후 청크 분할. **ollama_client에는 `ollama_generate_stream` 이미 존재** → ai.py만 전환 |
| 2 | **System Prompt** | §4 1단계: `ollama_client.py` 수정, DeepSeek-R1용 시스템 프롬프트 | 13-5-3: `role: system`, 후처리 축소 | §3.3 System Prompt 활용 | ollama_client: `role: user`만 사용. ai.py: "한국어로만 답변" 등 User Prompt에 포함 → **role: system 분리 필요** |
| 3 | **format=json** | §4 1단계: Ollama `format='json'` 옵션 | 13-5-4 (선택): 구조화 출력 | §3.4 구조화된 출력 | ollama_client에 `format` 파라미터 없음 → **옵션 추가 필요** |
| 4 | **토큰 관리 정밀화** | §3 B "8k~16k 컨텍스트 윈도우" 언급만 | 13-5-2: tiktoken/transformers, ContextManager 한국어 친화 | §3.2 정밀한 토큰 관리 | context_manager: chars//4. **tiktoken/transformers 도입 필요** |
| 5 | **기능별 모델 라우팅** | §3 A/B/C: Brain=DeepSeek-R1, Search=EEVE, Dev=Qwen2.5-Coder | Phase 13 Out of Scope (모델 교체·백로그) | §4 모델 개선 (별도) | 단일 OLLAMA_MODEL. **라우팅은 독립 서버 구축 후 2단계로 설계 권장** |
| 6 | **OLLAMA_BASE_URL + 인증** | §5.2 Nginx API Key, IP 화이트리스트 | — | — | 현재 클라이언트는 인증 헤더 미전송. **Nginx API Key 도입 시 backend에서 Authorization 헤더 전달 필요** |

### 6.3 리스크 검증 및 보완

Phase 13 Master Plan §9 리스크와 본 계획서(독립 서버 이전)를 함께 고려한 리스크 정리.

| ID | 리스크 | Phase 13 대응 | 본 계획서(독립 서버) 시 추가 리스크·대응 |
|----|--------|--------------|------------------------------------------|
| R-005 | True Streaming 전환 시 기존 클라이언트 호환 | SSE 이벤트 형식 유지·프론트 ask/stream 소비부 검증 | 독립 서버 이전 후에도 동일. **스트리밍 지연 시간(Latency) 측정** (§6 Next Steps 2번)으로 네트워크 구간 영향 확인 |
| R-006 | tiktoken/transformers 도입 시 의존성·메모리 | 경량(tiktoken) 우선, 토크나이저 캐시 정책 | **메인 서버(앱) 부하는 동일.** 독립 LLM 서버는 별도이므로 VRAM/메모리 이슈는 LLM 서버만 해당 |
| R-007 | System Prompt·후처리 축소 시 답변 품질 변화 | A/B 비교·회귀 테스트, 롤백 플래그 | 모델 교체(DeepSeek-R1 등)와 동시에 적용 시 **변수 분리** 권장: System Prompt만 먼저 적용 후 모델 교체 |
| — | **독립 서버 네트워크 지연** | — | 메인↔LLM 서버 구간 RTT·TTFT 증가 가능. **§6 Next Steps 2번 Latency 측정** 및 필요 시 로컬 캐시·타임아웃 조정 |
| — | **Nginx API Key 도입 시 backend 미지원** | — | 현재 `ollama_client`는 `Authorization` 미전송. **Nginx 인증 도입 시 `urllib.request`에 헤더 추가 또는 환경변수 `OLLAMA_AUTH_HEADER` 등 설계** |
| — | **Docker Ollama GPU 미할당 시** | — | GPU 없이 CPU 폴백 시 응답 지연 급증. **nvidia-container-toolkit·Ollama GPU 할당 검증**을 구축 체크리스트에 포함 권장 |

---

## 7. 결론 및 다음 작업 (Conclusion & Next Steps)

1.  **하드웨어 조립 및 OS 최적화:** 5070 Ti의 성능을 100% 활용하기 위한 전원 관리 및 쿨링 최적화.
2.  **독립 서버 서빙 테스트:** `curl`을 통해 외부망에서의 Ollama 응답 지연 시간(Latency) 측정.
3.  **메인 프로젝트 연동:** 스트리밍 API 동작 여부 및 RAG 컨텍스트 전달 안정성 검증.
4.  **기능 업그레이드 순서 권장:** 독립 서버 구축·연동 검증 후, Phase 13-5(True Streaming → 토큰 관리 → System Prompt → 구조화 출력) 순으로 적용 시 변수 분리·회귀 테스트에 유리함.
