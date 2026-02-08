# 8GB 환경 추론·키워드 추천 모델 및 대안

**배경**: 기본 모델 `exaone3.5:2.4b`는 Ollama 라이브러리에 있으나 **추론·의미 추적**이 약해, gpt4all 시절처럼 “키워드 추론·의미 분석으로 새 단어 추천” 수준의 품질을 기대하기 어렵다. 8GB 메모리 환경에서 추론에 쓸 수 있는 Ollama 모델이 없을 경우의 **대안**을 정리한다.

---

## 1. Ollama 모델 (8GB 이내)

| 모델 | Ollama 이름 | 메모리(대략) | 추론·의미 | 한국어 | 비고 |
|------|-------------|--------------|-----------|--------|------|
| **Qwen2.5 3B** | `qwen2.5:3b` | ~1.9–2.2GB | ◎ | 다국어(한국어 포함) | 인스트럭션·구조화·추론 강화, 128K 컨텍스트 |
| **exaone3.5 2.4B** | `exaone3.5:2.4b` | ~1.6GB | △ | ◎ | 현재 기본값, 추론·의미는 상대적으로 약함 |
| **Phi-3 Mini** | `phi3:mini` | ~2GB대 | ○ | △ | 경량, 키워드 추출용 프롬프트에 활용 가능 |
| **Gemma3 4B** | `gemma3:4b` | ~2.5GB대 | ○ | △ | 요약·추론 태스크에 적합 |

- **8GB 전용 머신**이면 7B급(예: `qwen2.5:7b`)도 가능하나, Docker·Backend·Postgres·Qdrant 등과 **공유**하면 8GB에서는 3B~4B 권장.
- **추론·의미 기반 키워드 추천**을 우선하면 **`qwen2.5:3b`**를 첫 번째 후보로 권장 (Ollama 라이브러리 제공, 8GB에서 여유 있음).

### 1.1 기본 모델을 Qwen2.5 3B로 바꾸는 방법

```bash
# Ollama에서 모델 로드
docker exec -it ollama ollama pull qwen2.5:3b
```

환경 변수로 지정:

```bash
# .env 또는 docker-compose 오버라이드
OLLAMA_MODEL=qwen2.5:3b
```

`backend/config.py`의 기본값을 바꾸지 않아도 `OLLAMA_MODEL`만 설정하면 전체(키워드 추천·RAG·Reasoning)가 해당 모델을 사용한다.

---

## 2. Ollama만으로 부족할 때의 대안

8GB에서 돌릴 수 있는 Ollama 모델으로도 **추론·의미 기반 키워드 품질**이 부족하다고 판단되면 아래를 검토할 수 있다.

### 2.1 키워드 추출만 외부 API 사용 (하이브리드)

- **구성**: RAG·일반 답변은 계속 로컬 Ollama, **키워드/라벨 추천만** OpenAI 또는 Claude 등 외부 API 사용.
- **장점**: 키워드 품질만 선택적으로 올릴 수 있음.
- **구현 포인트**:
  - `scripts/backend/extract_keywords_and_labels.py`에서 이미 `extract_keywords_with_openai()` 폴백이 있음.
  - 환경 변수(예: `KEYWORD_EXTRACTION_PROVIDER=openai`)로 “키워드만 외부 API”를 선택하도록 분기 추가 가능.
- **비용**: 키워드 추출 호출 횟수만큼만 과금 (짧은 텍스트 위주라 비용은 제한적).

### 2.2 정규식 폴백 유지 (현재 동작)

- Ollama 실패 또는 미사용 시 **정규식 기반** `extract_keywords_with_regex()`로 동작 중.
- 품질은 LLM보다 낮지만, **추론 없이** 안정적으로 동작하며 8GB 부담이 없다.

### 2.3 외부 LLM API를 전면 사용

- 모든 생성(답변·키워드·Reasoning)을 OpenAI/Claude 등으로 통일.
- 8GB 제약은 없어지지만, 비용·프라이버시·네트워크 의존이 커진다.

### 2.4 더 큰 Ollama 모델은 별도 서버에

- 12GB+ RAM이 있는 **별도 서버**에 Ollama만 두고, EEVE-Korean 10.8B 등 큰 모델 실행.
- Backend는 `OLLAMA_BASE_URL`로 해당 서버를 바라보게 설정.
- 8GB 호스트에서는 Backend·DB·Qdrant만 두고, LLM은 원격 Ollama에 위임하는 구성.

---

## 3. 요약 및 권장 순서

| 우선순위 | 내용 |
|----------|------|
| 1 | **8GB 공유 환경**: Ollama 모델을 **`qwen2.5:3b`**로 시험. (추론·의미가 exaone3.5:2.4b보다 나은 편.) |
| 2 | **키워드 품질만** 더 필요하면: 키워드 추출만 **OpenAI/Claude** 등 외부 API로 옮기는 하이브리드 검토. |
| 3 | **로컬만** 유지해야 하면: 정규식 폴백 유지 + 가능하면 `qwen2.5:3b` 사용. |
| 4 | **리소스 여유**가 있으면: Ollama를 12GB+ 서버로 분리하고 EEVE-Korean 10.8B 등으로 품질 향상. |

이 문서는 “exaone3.5:2.4b는 추론·의미에 약하므로, 8GB에서는 qwen2.5:3b 시도 → 부족하면 키워드만 외부 API”라는 선택지를 정리한 것이다.
