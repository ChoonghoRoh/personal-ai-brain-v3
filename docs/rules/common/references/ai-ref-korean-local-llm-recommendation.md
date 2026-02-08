# 한국어 로컬 LLM 추천 (Docker·Backend·n8n 공유 환경)

**현재 구성**: 로컬 LLM은 **Ollama**로 통일되어 있으며, **기본 모델은 `qwen2.5:7b`** (다국어·한국어, 추론·키워드에 유리)입니다. Ollama는 **호스트(localhost)** 에서 실행하고, Backend(Docker)는 `OLLAMA_BASE_URL=http://host.docker.internal:11434`, `OLLAMA_MODEL=qwen2.5:7b`로 연결합니다. Docker Compose의 `ollama` 서비스는 주석 처리되어 있으며, 필요 시 해제 후 `OLLAMA_BASE_URL=http://ollama:11434`로 변경할 수 있습니다.

로컬 LLM 사용처:
1. **AI 라우터** (`backend/routers/ai/ai.py`): Ollama `/api/generate` 로 **답변 생성**
2. **라벨/키워드** (`scripts/backend/extract_keywords_and_labels.py`): `extract_keywords_with_ollama()` 로 **키워드 추출**

Docker 구성: Backend, n8n, Qdrant, PostgreSQL, **Ollama**, Web(FastAPI)가 동일 호스트에서 동작합니다.

---

## 1. 추천 모델 (한국어·성능·리소스 균형)

### 1) **Bllossom 3B (llama-3.2-Korean-Bllossom-3B)** — 기본 추천

| 항목 | 내용 |
|------|------|
| **용도** | 답변 생성 + 키워드 추출 모두 적합 |
| **한국어** | 150GB 한국어 추가 사전학습, DPO 기반 인스트럭션 튜닝 |
| **리소스** | 약 2~3GB RAM (Q4_K_M), Docker·n8n·Backend와 동시 실행에 유리 |
| **형식** | GGUF (HuggingFace: `Bllossom/llama-3.2-Korean-Bllossom-3B-gguf-Q4_K_M`) |
| **Ollama** | Modelfile로 GGUF 로드 후 사용 가능 |

- **답변 생성**: 짧은 문맥·일상 질의·요약에 적합.  
- **키워드 추출**: 짧은 텍스트에서 키워드/라벨 뽑기에 충분한 품질.

---

### 2) **EEVE-Korean 10.8B** — 품질 우선

| 항목 | 내용 |
|------|------|
| **용도** | 답변 생성(품질 우선), 키워드 추출(정확도 우선) |
| **한국어** | SOLAR-10.7B 기반 한국어 인스트럭션 튜닝 (야놀자 계열) |
| **리소스** | 약 6~7GB RAM (Q4_K_M), 8GB급이면 Backend와 분리해 Ollama 전용 권장 |
| **형식** | GGUF (HuggingFace: `teddylee777/EEVE-Korean-Instruct-10.8B-v1.0-gguf`) |
| **Ollama** | Modelfile 예제 있음, Q4_K_S / Q4_K_M / Q8_0 등 선택 가능 |

- **답변 생성**: Bllossom 3B보다 자연스럽고 세밀한 한국어.  
- **키워드 추출**: 복잡한 문장·도메인 용어가 많을 때 유리.

---

### 3) **EXAONE 3.5 (2.4B~32B)** — 선택지

| 항목 | 내용 |
|------|------|
| **용도** | LG AI Research, 한국어·영어 병행 |
| **리소스** | 2.4B는 경량, 32B는 전용 서버 권장 |
| **Ollama** | `ollama run exaone3.5:2.4b` 등으로 사용 가능 |

- Docker·n8n·Backend와 함께 돌릴 때는 **2.4B/3.5B** 크기 사용 권장. **추론·의미 기반 키워드 추천**에는 상대적으로 약하다는 피드백이 있음 → 8GB 대안은 [ai-ref-8gb-inference-and-keyword-alternatives.md](ai-ref-8gb-inference-and-keyword-alternatives.md) 참고.

---

### 4) **Qwen2.5 3B** — 8GB 환경에서 추론·키워드 품질 우선

| 항목 | 내용 |
|------|------|
| **용도** | 답변 생성 + **키워드 추출·추론** (exaone3.5:2.4b보다 추론·의미에 유리) |
| **한국어** | 다국어(한국어 포함), 인스트럭션·구조화·추론 강화 |
| **리소스** | 약 1.9~2.2GB, 8GB 공유 환경에 적합 |
| **Ollama** | `ollama run qwen2.5:3b` (Ollama 라이브러리 제공) |

- **추론·의미 추적**이 중요한 키워드/라벨 추천에는 **qwen2.5:3b**를 우선 시험해 볼 것을 권장. 상세·대안(외부 API, 하이브리드)은 [ai-ref-8gb-inference-and-keyword-alternatives.md](ai-ref-8gb-inference-and-keyword-alternatives.md) 참고.

---

## 2. 용도별 추천 요약

| 용도 | 8GB 공유 (Backend·n8n과 동시) | 리소스 여유 있음 (Ollama 전용) |
|------|--------------------------------------|--------------------------------|
| **답변 생성** | exaone3.5:2.4b / **qwen2.5:3b** | EEVE-Korean 10.8B (Q4_K_M) |
| **키워드·추론** | **qwen2.5:3b** (추천), exaone3.5:2.4b | EEVE-Korean 10.8B |

- **성능·결과물** 모두 한국어에 유리한 쪽은 **EEVE-Korean 10.8B**  
- **Docker·Backend·n8n·Qdrant·PostgreSQL·Web 공유**를 고려하면 **Bllossom 3B**가 메모리·속도 균형이 좋고, EEVE 10.8B는 Ollama를 별도 서비스로 두고 사용하는 구성을 권장합니다.

---

### 2.5 알려진 이슈 (특정 모델·환경)

| 모델 | 환경 | 이슈 | 권장 |
|------|------|------|------|
| **exaone3.5:2.4b** | Docker·8GB 공유 | 메모리 부족, 추론·키워드 품질 부족, 응답 비어있음 등 | **qwen2.5:7b** 또는 qwen2.5:3b 시험 |
| **bnksys/yanolja-eeve-korean-instruct-10.8b** | Docker·8GB 공유 | 메모리 부족, 모델 로드/추론 실패 | 12GB+ 단독 서버 또는 호스트에서 Ollama 실행 후 Backend만 Docker |
| **EEVE-Korean 10.8B** | 8GB RAM 단일 호스트 | OOM, 느린 추론 | 16GB+ 또는 Ollama를 별도 서버로 분리 |

- **Ollama Docker 분리**: Ollama를 **호스트에서 실행**하고 Backend(Docker)는 `OLLAMA_BASE_URL=http://host.docker.internal:11434`로 접속하면, 메모리·GPU를 호스트가 독점해 모델 안정성이 좋아집니다. 현재 `docker-compose.yml`은 이 구성을 기본으로 합니다.
- **백엔드 시작 전 Ollama·모델 확인**: `scripts/llm_server_check.py`를 사용하면 서버 연결·지정 모델 생성 테스트를 수행할 수 있습니다. 필요 시 `--start-if-missing`으로 호스트에서 `ollama serve` 자동 기동, `--no-check-model`로 서버만 확인 가능.

```bash
# 예: 호스트에서 Ollama 확인 후 qwen2.5:7b 테스트
python scripts/llm_server_check.py --url http://localhost:11434 --model qwen2.5:7b
# 서버 꺼져 있으면 기동 후 모델 테스트
python scripts/llm_server_check.py --start-if-missing --check-model
```

---

## 3. Docker·공유 환경 구성 권장

- **LLM 실행 위치**: Backend 컨테이너 내부가 아니라 **Ollama(LocalAI 등) 별도 서비스**로 두는 것을 권장.  
  - Backend, n8n, Qdrant, PostgreSQL, Web은 그대로 두고,  
  - Ollama만 추가 컨테이너 또는 호스트 서비스로 실행 → Backend는 `OPENAI_BASE_URL`(또는 `LOCAL_LLM_URL`)로 해당 API 호출.

- **네트워크**: 동일 `docker-compose`라면 `ollama` 서비스 추가 후 Backend에서 `http://ollama:11434`로 접근하면 되고,  
  - 호스트에서 Ollama를 띄웠다면 `http://host.docker.internal:11434` 등으로 접근.

- **n8n**: 워크플로에서 “OpenAI 호환” 노드로 같은 Ollama URL을 지정하면 Backend와 동일한 한국어 모델을 공유할 수 있습니다.

---

## 4. 8GB 환경에서 추론·키워드 품질이 부족할 때

- **exaone3.5:2.4b**는 추론·의미 기반 키워드 추천에 약하다는 판단이 있는 경우:  
  → [ai-ref-8gb-inference-and-keyword-alternatives.md](ai-ref-8gb-inference-and-keyword-alternatives.md) 참고.  
  - Ollama: **qwen2.5:3b** 시험 (`OLLAMA_MODEL=qwen2.5:3b`).  
  - 대안: 키워드만 외부 API(OpenAI/Claude) 사용, 정규식 폴백 유지, Ollama를 12GB+ 서버로 분리 등.

---

## 5. 외부 단독 서버(16GB/32GB) 모델 추천

Ollama를 **12GB+ 전용 서버**로 분리할 때, Backend는 `OLLAMA_BASE_URL=http://원격서버IP:11434`, `OLLAMA_MODEL=모델명`으로 연결합니다. **특정 하드웨어(i5-8400, 32GB RAM, M.2 256GB, GPU Radeon R7 270X 2GB)에 맞춘 OS·서버·Ollama·모델 설계**(CPU 위주, GPU 미사용 권장)는 [ai-ref-llm-dedicated-server-design.md](ai-ref-llm-dedicated-server-design.md) 참고.

| 서버 RAM | 용도 우선순위 | 추천 모델 (Ollama) |
|----------|----------------|---------------------|
| **16GB** | 한국어 + 안정 | EEVE-Korean 7B, Qwen2.5 7B |
| **16GB** | 한국어 최대(여유 적음) | EEVE-Korean 10.8B |
| **32GB** | 한국어 + 여유 | EEVE-Korean 10.8B, Qwen2.5 14B |
| **32GB** | 한국어 최대 품질 | exaone3.5:32b |

- 16GB 단독: 7B~10B 권장. EEVE 10.8B는 가능하나 OS·KV 캐시 고려 시 여유가 적음.
- 32GB 단독: 13B~32B 가능. exaone3.5:32b는 Q4 기준 약 19GB.

---

## 6. gpt4all 추천 (로컬·비-Docker)

Backend API·키워드 추천은 Ollama로 통일되어 있으나, **로컬 스크립트**(`search_and_query.py`, `embed_and_store.py`)에서는 gpt4all(GGUF)을 직접 사용할 수 있습니다. Docker 환경에는 gpt4all이 부적합해 Ollama로 대체한 상태입니다. **i5-8400 / 32GB RAM / R7 270X 2GB** 같은 스펙에서는 [ai-ref-llm-dedicated-server-design.md](ai-ref-llm-dedicated-server-design.md)의 Ollama·qwen2.5:7b / EEVE-Korean 10.8B 구성을 우선 권장하고, gpt4all은 호스트에서 별도 실험용으로 사용할 수 있습니다.

| 환경 | 용도 | 추천 모델 (gpt4all / GGUF) |
|------|------|-----------------------------|
| **8GB** | 한국어 + 키워드·추론 | Llama-3.1-Korean-8B-Instruct-Q4_K_M (Parkoz), Meta-Llama-3-8B-Instruct.Q4_0.gguf |
| **8GB** | 경량·빠름 | Phi-3-mini-4k-instruct.Q4_0.gguf, SmolLM2-1.7B-Instruct |
| **16GB** | 13B 품질 | gpt4all-13b-snoozy-q4_0.gguf, Meta-Llama-3.1-8B-Instruct-128k |

- **exaone3.5 32B**와 동일 모델을 gpt4all에서 쓰려면: HuggingFace `LGAI-EXAONE/EXAONE-3.5-32B-Instruct-GGUF`의 `EXAONE-3.5-32B-Instruct-Q4_K_M.gguf` (약 19.3GB) 로드. 32GB+ RAM 권장.

---

## 7. 기타 로컬 모델·런타임

Ollama·gpt4all 외에 **로컬 런타임**(LocalAI, llama.cpp, LM Studio, vLLM)에서 사용할 수 있는 모델 예시입니다. GGUF 또는 각 런타임 지원 형식으로 제공되는 경우가 많습니다.

### 7.1 한국어·다국어

| 모델 | 크기 | 특징 | 비고 |
|------|------|------|------|
| **SOLAR / SOLAR-KO** | 10.7B | Upstage, 한국어·영어. SOLAR-KO는 한국어 어휘 확장 | Ollama: `solar`. GGUF: beomi/OPEN-SOLAR-KO-10.7B 등 |
| **DeepSeek-R1-Bllossom** | 8B / 70B | DeepSeek-R1 기반 한국어 튜닝, 추론 강함 | 8B는 16GB, 70B는 고사양 |
| **Llama 3.1 Korean 8B** | 8B | 한국어 인스트럭션 | GGUF(Parkoz 등) → LM Studio, llama.cpp, gpt4all |

### 7.2 추론·의미 (키워드/라벨 품질에 유리)

| 모델 | 크기 | 특징 | 비고 |
|------|------|------|------|
| **DeepSeek-R1** | 1.5B~671B | 추론·수학·코드, 128K 컨텍스트 | Ollama: `deepseek-r1` (7B 등) |
| **Mistral / Mistral 3** | 7B~22B | 대화·요약·추론 균형 | Ollama: `mistral`, `mistral3` |
| **Phi-3 / Phi-4** | 3.8B~14B | 경량·추론. Phi-4 14B는 더 강함 | Ollama: `phi3`, `phi4` |

### 7.3 경량(8GB)·중대형(16GB~32GB)

| 모델 | 크기 | 비고 |
|------|------|------|
| **SmolLM2** | 1.7B~3B | GGUF → LM Studio, llama.cpp, gpt4all |
| **Gemma 3** | 1B~27B | Ollama: `gemma3:1b`, `gemma3:4b`, `gemma3:12b` |
| **SOLAR 10.7B** | 10.7B | Ollama: `solar`. 단일 턴·벤치 상위 |
| **Command R / Yi** | 35B~104B / 6B~34B | Ollama 등. 35B는 32GB급 |

---

## 8. 참고 링크

- Bllossom 3B GGUF: https://huggingface.co/Bllossom/llama-3.2-Korean-Bllossom-3B-gguf-Q4_K_M  
- EEVE-Korean 10.8B GGUF: https://huggingface.co/teddylee777/EEVE-Korean-Instruct-10.8B-v1.0-gguf  
- EXAONE 3.5 32B GGUF: https://huggingface.co/LGAI-EXAONE/EXAONE-3.5-32B-Instruct-GGUF  
- Ollama Docker: https://docs.ollama.com/docker  
- Ollama 모델 검색: https://ollama.com/search (한국어: q=korean)  
- 8GB 추론·키워드 대안: [ai-ref-8gb-inference-and-keyword-alternatives.md](ai-ref-8gb-inference-and-keyword-alternatives.md)
- LLM 단독 서버 설계 (OS·서버·모델): [ai-ref-llm-dedicated-server-design.md](ai-ref-llm-dedicated-server-design.md)

이 문서는 “한국어에 유리한 모델”과 “Docker·Backend·n8n·Qdrant·PostgreSQL·Web 공유”를 모두 고려한 추천입니다. Backend는 Ollama API(`OLLAMA_BASE_URL`, `OLLAMA_MODEL`)로 연동됩니다.
