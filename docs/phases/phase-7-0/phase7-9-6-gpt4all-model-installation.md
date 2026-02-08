# Phase 7.9.6: GPT4All 모델 설치 정보 및 코드 연결 확인

**작성일**: 2026-01-09  
**모델**: orca-mini-3b-gguf2-q4_0.gguf

---

## 📋 모델 정보

### 기본 정보

- **모델 이름**: `orca-mini-3b-gguf2-q4_0.gguf`
- **모델 크기**: 약 1.98 GB
- **필요 RAM**: 약 4 GB
- **파라미터**: 3B (30억)
- **용도**: 제목 생성, 키워드 추출, 간단한 질의응답

### 모델 특징

- ✅ 작고 빠른 모델 (3B 파라미터)
- ✅ 자동 다운로드 지원
- ✅ 로컬 실행 (오프라인 가능)
- ✅ 무료 사용

---

## 📦 설치 방법

### 1. 패키지 설치

```bash
# 가상환경 활성화
cd /Users/map-rch/WORKS/personal-ai-brain-v2
source scripts/venv/bin/activate

# GPT4All 패키지 설치
pip install gpt4all
```

### 2. 모델 자동 다운로드

모델은 첫 실행 시 자동으로 다운로드됩니다:

```python
from gpt4all import GPT4All

# 첫 실행 시 자동 다운로드 (약 1.98GB)
model = GPT4All("orca-mini-3b-gguf2-q4_0.gguf")
```

### 3. 모델 저장 위치

기본 저장 위치: `~/.cache/gpt4all/`

- macOS/Linux: `~/.cache/gpt4all/`
- Windows: `C:\Users\<username>\.cache\gpt4all\`

---

## 🔗 코드에서 라이브러리 연결 확인

### 사용 위치

프로젝트에서 GPT4All 모델을 사용하는 파일들:

#### 1. 백엔드 API

**`backend/routers/ai.py`**
- 함수: `get_gpt4all_model()`
- 용도: AI 질의응답 API
- 모델: `orca-mini-3b-gguf2-q4_0.gguf`
- 싱글톤 패턴 사용

```python
_gpt4all_model_name = "orca-mini-3b-gguf2-q4_0.gguf"
_gpt4all_model = GPT4All(_gpt4all_model_name)
```

#### 2. 시스템 서비스

**`backend/services/system_service.py`**
- 함수: `_get_gpt4all_status()`
- 용도: GPT4All 상태 확인 및 테스트
- 모델: `orca-mini-3b-gguf2-q4_0.gguf`

#### 3. 문서 임베딩

**`scripts/embed_and_store.py`**
- 함수: `extract_title_with_ai()`
- 용도: 청크 제목 추출
- 모델: `orca-mini-3b-gguf2-q4_0.gguf`

```python
model = GPT4All("orca-mini-3b-gguf2-q4_0.gguf")
```

#### 4. 키워드 추출

**`scripts/extract_keywords_and_labels.py`**
- 함수: `extract_keywords_with_gpt4all()`
- 용도: 키워드 자동 추출
- 모델: `orca-mini-3b-gguf2-q4_0.gguf`

#### 5. 검색 및 쿼리

**`scripts/search_and_query.py`**
- 함수: `query_with_gpt4all()`
- 용도: 검색 결과 기반 응답 생성
- 모델: `orca-mini-3b-gguf2-q4_0.gguf`

#### 6. 제목 생성 스크립트

**`scripts/generate_chunk_titles.py`**
- 함수: `extract_title_with_ai()` (import)
- 용도: 제목 없는 청크에 제목 생성
- 모델: `orca-mini-3b-gguf2-q4_0.gguf` (embed_and_store.py에서 사용)

---

## ✅ 설치 확인 방법

### 방법 1: 확인 스크립트 실행

```bash
cd /Users/map-rch/WORKS/personal-ai-brain-v2
source scripts/venv/bin/activate
python scripts/check_gpt4all_model.py
```

이 스크립트는 다음을 확인합니다:
1. GPT4All 패키지 설치 여부
2. 모델 정보
3. 모델 저장 위치
4. 코드에서 라이브러리 연결 상태
5. 모델 로딩 테스트 (선택적)

### 방법 2: 대시보드에서 확인

1. 서버 실행:
   ```bash
   python scripts/start_server.py
   ```

2. 브라우저에서 접속:
   ```
   http://localhost:8000/dashboard
   ```

3. "GPT4All 상태" 섹션에서 확인:
   - 패키지 설치 여부
   - 모델 이름
   - 실행 테스트 결과

### 방법 3: 수동 확인

```python
# Python 인터프리터에서 확인
from gpt4all import GPT4All

# 모델 로딩 (첫 실행 시 다운로드)
model = GPT4All("orca-mini-3b-gguf2-q4_0.gguf")

# 간단한 테스트
response = model.generate("Hello", max_tokens=10)
print(response)
```

---

## 🔧 문제 해결

### 문제 1: 모델 다운로드 실패

**증상**: HTTP 404 오류 또는 다운로드 실패

**해결 방법**:
1. 인터넷 연결 확인
2. 디스크 공간 확인 (최소 3GB 필요)
3. 방화벽 설정 확인
4. 모델 이름 확인 (`orca-mini-3b-gguf2-q4_0.gguf`)

### 문제 2: 메모리 부족

**증상**: 모델 로딩 실패 또는 시스템 느려짐

**해결 방법**:
1. 최소 4GB RAM 필요
2. 다른 애플리케이션 종료
3. 더 작은 모델 사용 고려

### 문제 3: 패키지 설치 오류

**증상**: `ModuleNotFoundError: No module named 'gpt4all'`

**해결 방법**:
```bash
# 가상환경 활성화 확인
source scripts/venv/bin/activate

# 패키지 재설치
pip install --upgrade gpt4all
```

### 문제 4: 모델 파일 찾을 수 없음

**증상**: 모델 파일이 다운로드되었지만 찾을 수 없음

**해결 방법**:
1. 저장 위치 확인: `~/.cache/gpt4all/`
2. 파일 권한 확인
3. 모델 이름 확인 (대소문자 구분)

---

## 📊 사용 예시

### 제목 생성

```bash
# 제목 없는 청크에 제목 생성
python scripts/generate_chunk_titles.py --limit 10

# 전체 청크 처리
python scripts/generate_chunk_titles.py
```

### 키워드 추출

```python
from scripts.extract_keywords_and_labels import extract_keywords_with_gpt4all

keywords = extract_keywords_with_gpt4all("문서 내용", top_n=10)
```

### AI 질의응답

```bash
# API를 통한 질의응답
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "프로젝트 목적은 무엇인가요?"}'
```

---

## 📝 참고 자료

- [GPT4All 공식 문서](https://docs.gpt4all.io/)
- [GPT4All Python SDK](https://docs.gpt4all.io/gpt4all_python/home.html)
- [사용 가능한 모델 목록](https://gpt4all.io/models.html)

---

**최종 업데이트**: 2026-01-09
