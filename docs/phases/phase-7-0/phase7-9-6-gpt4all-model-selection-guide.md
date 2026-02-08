# Phase 7.9.6: GPT4All 모델 선택 가이드

**작성일**: 2026-01-09  
**현재 사용 모델**: orca-mini-3b-gguf2-q4_0.gguf (3B)

---

## 📊 모델 비교표

### 현재 모델 vs 상위 모델

| 모델 이름                                  | 파일 크기 | 필요 RAM | 파라미터 | 개발사         | 라이선스        | 성능       |
| ------------------------------------------ | --------- | -------- | -------- | -------------- | --------------- | ---------- |
| **orca-mini-3b-gguf2-q4_0.gguf** (현재)    | 1.98 GB   | 4 GB     | 3B       | Microsoft      | CC-BY-NC-SA-4.0 | ⭐⭐⭐     |
| **Phi-3-mini-4k-instruct.Q4_0.gguf**       | 2.18 GB   | 4 GB     | 3.8B     | Microsoft      | MIT             | ⭐⭐⭐     |
| **Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf** | 4.11 GB   | 8 GB     | 7B       | Mistral & Nous | Apache 2.0      | ⭐⭐⭐⭐   |
| **Meta-Llama-3-8B-Instruct.Q4_0.gguf**     | 4.66 GB   | 8 GB     | 8B       | Meta           | Llama 3 License | ⭐⭐⭐⭐⭐ |
| **gpt4all-13b-snoozy-q4_0.gguf**           | 7.37 GB   | 16 GB    | 13B      | Nomic AI       | GPL             | ⭐⭐⭐⭐⭐ |

---

## 🎯 추천 모델 (상위 버전)

### 1. Meta-Llama-3-8B-Instruct.Q4_0.gguf (최고 추천)

**특징**:

- ✅ **파라미터**: 8B (현재 모델의 2.7배)
- ✅ **파일 크기**: 4.66 GB
- ✅ **필요 RAM**: 8 GB
- ✅ **성능**: 높은 품질의 응답 생성
- ✅ **라이선스**: Llama 3 License (상업적 사용 가능)

**장점**:

- Meta의 최신 기술 적용
- 다국어 지원 우수
- 추론 능력 뛰어남
- 코딩 작업에 적합

**단점**:

- 메모리 사용량이 2배 (4GB → 8GB)
- 파일 크기가 2배 이상 (1.98GB → 4.66GB)
- 다운로드 시간 증가

**사용 시나리오**:

- 제목 생성 품질 향상이 필요한 경우
- 더 복잡한 질의응답이 필요한 경우
- 다국어 지원이 중요한 경우

---

### 2. Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf (균형 추천)

**특징**:

- ✅ **파라미터**: 7B (현재 모델의 2.3배)
- ✅ **파일 크기**: 4.11 GB
- ✅ **필요 RAM**: 8 GB
- ✅ **성능**: 높은 품질의 응답 생성
- ✅ **라이선스**: Apache 2.0 (상업적 사용 가능)

**장점**:

- Mistral의 고성능 모델
- DPO (Direct Preference Optimization) 적용
- Apache 2.0 라이선스로 사용 제약 적음
- Llama 3보다 약간 작아서 빠름

**단점**:

- 메모리 사용량이 2배 (4GB → 8GB)
- 파일 크기가 2배 이상

**사용 시나리오**:

- 상업적 사용이 중요한 경우
- Llama 3보다 빠른 응답이 필요한 경우
- 균형잡힌 성능과 속도가 필요한 경우

---

### 3. Phi-3-mini-4k-instruct.Q4_0.gguf (경량 상위)

**특징**:

- ✅ **파라미터**: 3.8B (현재 모델의 1.3배)
- ✅ **파일 크기**: 2.18 GB
- ✅ **필요 RAM**: 4 GB
- ✅ **성능**: 현재 모델보다 약간 향상
- ✅ **라이선스**: MIT (매우 자유로운 사용)

**장점**:

- 현재 모델과 비슷한 리소스 사용
- MIT 라이선스로 가장 자유로운 사용
- 파일 크기 증가가 적음 (1.98GB → 2.18GB)
- 메모리 요구사항 동일 (4GB)

**단점**:

- 성능 향상이 크지 않음 (3B → 3.8B)
- 큰 모델만큼의 품질 향상은 기대하기 어려움

**사용 시나리오**:

- 리소스 제약이 있는 환경
- 약간의 성능 향상만 필요한 경우
- MIT 라이선스가 중요한 경우

---

### 4. gpt4all-13b-snoozy-q4_0.gguf (최고 성능)

**특징**:

- ✅ **파라미터**: 13B (현재 모델의 4.3배)
- ✅ **파일 크기**: 7.37 GB
- ✅ **필요 RAM**: 16 GB
- ✅ **성능**: 최고 품질의 응답 생성
- ✅ **라이선스**: GPL

**장점**:

- 가장 높은 성능
- 복잡한 작업에 적합
- 긴 컨텍스트 처리 가능

**단점**:

- 메모리 사용량이 4배 (4GB → 16GB)
- 파일 크기가 3.7배 (1.98GB → 7.37GB)
- 다운로드 시간이 매우 김
- GPL 라이선스 제약

**사용 시나리오**:

- 고성능이 절실히 필요한 경우
- 충분한 메모리가 있는 경우 (16GB+)
- 복잡한 추론 작업이 많은 경우

---

## 🔄 모델 변경 방법

### 1. 코드에서 모델 이름 변경

다음 파일들에서 모델 이름을 변경해야 합니다:

#### `backend/routers/ai.py`

```python
# 현재
_gpt4all_model_name = "orca-mini-3b-gguf2-q4_0.gguf"

# 변경 예시 (Llama 3 사용 시)
_gpt4all_model_name = "Meta-Llama-3-8B-Instruct.Q4_0.gguf"
```

#### `backend/services/system_service.py`

```python
# 현재
model_name = "orca-mini-3b-gguf2-q4_0.gguf"

# 변경 예시
model_name = "Meta-Llama-3-8B-Instruct.Q4_0.gguf"
```

#### `scripts/embed_and_store.py`

```python
# 현재
model = GPT4All("orca-mini-3b-gguf2-q4_0.gguf")

# 변경 예시
model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf")
```

#### `scripts/extract_keywords_and_labels.py`

```python
# 현재
model = GPT4All("orca-mini-3b-gguf2-q4_0.gguf")

# 변경 예시
model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf")
```

#### `scripts/search_and_query.py`

```python
# 현재
GPT4ALL_MODEL = "orca-mini-3b-gguf2-q4_0.gguf"

# 변경 예시
GPT4ALL_MODEL = "Meta-Llama-3-8B-Instruct.Q4_0.gguf"
```

### 2. 모델 다운로드

모델은 첫 실행 시 자동으로 다운로드됩니다:

```python
from gpt4all import GPT4All

# 첫 실행 시 자동 다운로드
model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf")
```

### 3. 저장 위치

모든 모델은 `~/.cache/gpt4all/` 디렉토리에 저장됩니다.

---

## 📋 모델 선택 기준

### 리소스 기반 선택

| 시스템 RAM | 추천 모델                                     | 이유                    |
| ---------- | --------------------------------------------- | ----------------------- |
| 4 GB       | orca-mini-3b (현재) 또는 Phi-3-mini           | 메모리 제약             |
| 8 GB       | Meta-Llama-3-8B 또는 Nous-Hermes-2-Mistral-7B | 최적의 성능/리소스 비율 |
| 16 GB+     | gpt4all-13b-snoozy                            | 최고 성능               |

### 용도 기반 선택

| 용도        | 추천 모델                | 이유                  |
| ----------- | ------------------------ | --------------------- |
| 제목 생성   | Meta-Llama-3-8B          | 높은 품질의 제목 생성 |
| 키워드 추출 | Nous-Hermes-2-Mistral-7B | 빠른 응답과 좋은 품질 |
| 질의응답    | Meta-Llama-3-8B          | 추론 능력 우수        |
| 경량 사용   | Phi-3-mini               | 리소스 효율적         |

### 라이선스 기반 선택

| 라이선스 요구사항  | 추천 모델                                 |
| ------------------ | ----------------------------------------- |
| 상업적 사용        | Meta-Llama-3-8B, Nous-Hermes-2-Mistral-7B |
| 가장 자유로운 사용 | Phi-3-mini (MIT)                          |
| 오픈소스 프로젝트  | gpt4all-13b-snoozy (GPL)                  |

---

## ⚠️ 주의사항

### 1. 메모리 확인

모델 변경 전 시스템 메모리를 확인하세요:

```bash
# macOS/Linux
free -h  # 또는
vm_stat  # macOS

# Windows
wmic OS get TotalVisibleMemorySize,FreePhysicalMemory
```

### 2. 디스크 공간 확인

큰 모델은 더 많은 디스크 공간이 필요합니다:

- orca-mini-3b: 1.98 GB
- Llama-3-8B: 4.66 GB (추가 2.68 GB 필요)
- 13b-snoozy: 7.37 GB (추가 5.39 GB 필요)

### 3. 성능 테스트

모델 변경 후 반드시 테스트하세요:

```bash
# 제목 생성 테스트
python scripts/generate_chunk_titles.py --limit 5

# 모델 확인
python scripts/check_gpt4all_model.py
```

---

## 🎯 추천 시나리오

### 시나리오 1: 성능 향상이 필요한 경우

**추천**: `Meta-Llama-3-8B-Instruct.Q4_0.gguf`

- 제목 생성 품질 향상
- 더 나은 질의응답
- 다국어 지원

**요구사항**: 8GB RAM, 4.66GB 디스크 공간

### 시나리오 2: 균형잡힌 선택

**추천**: `Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf`

- 좋은 성능과 속도 균형
- Apache 2.0 라이선스
- 상업적 사용 가능

**요구사항**: 8GB RAM, 4.11GB 디스크 공간

### 시나리오 3: 리소스 제약이 있는 경우

**추천**: `Phi-3-mini-4k-instruct.Q4_0.gguf`

- 현재 모델과 비슷한 리소스
- 약간의 성능 향상
- MIT 라이선스

**요구사항**: 4GB RAM, 2.18GB 디스크 공간

---

## 📝 모델 이름 정확한 형식

GPT4All에서 사용하는 정확한 모델 이름:

1. `Meta-Llama-3-8B-Instruct.Q4_0.gguf`
2. `Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf`
3. `Phi-3-mini-4k-instruct.Q4_0.gguf`
4. `orca-mini-3b-gguf2-q4_0.gguf` (현재)
5. `gpt4all-13b-snoozy-q4_0.gguf`

**주의**: 모델 이름은 대소문자를 구분하며, 정확히 일치해야 합니다.

---

## 🔗 참고 자료

- [GPT4All 공식 모델 목록](https://docs.gpt4all.io/gpt4all_desktop/models.html)
- [GPT4All Python SDK 문서](https://docs.gpt4all.io/gpt4all_python/home.html)
- [모델 비교 및 벤치마크](https://gpt4all.io/models.html)

---

**최종 업데이트**: 2026-01-09
