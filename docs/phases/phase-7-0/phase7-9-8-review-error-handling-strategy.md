# Phase 7.9.8: 오류 처리 전략 및 분기 로직

**작성일**: 2026-01-10

---

## 📋 개요

이 문서는 프로젝트에서 발견된 오류들을 처리하기 위한 전략과 분기 로직을 정의합니다. 특히 같은 오류가 3회 이상 발생하는 경우 다음 로직으로 이동하는 처리 방안을 포함합니다.

---

## 🔄 오류 처리 분기 로직

### 기본 원칙

1. **같은 오류가 3회 이상 발생 시**: 다음 로직으로 이동
2. **임계값 도달 시**: 대체 로직 또는 우회 방법 사용
3. **복구 불가능 시**: 사용자에게 명확한 오류 메시지 표시

---

## 🔴 우선순위 높음: 즉시 처리

### 1. XSS 취약점 수정

**오류 발생 횟수**: 5회 이상  
**처리 전략**: 모든 페이지에서 즉시 수정

#### 처리 방법

**1단계: 이스케이프 함수 생성**

```javascript
// web/public/js/utils.js (새 파일)
function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}
```

**2단계: 각 페이지 수정**

- `knowledge.js`: 청크 내용 이스케이프
- `admin-approval.js`: 청크 상세 내용 이스케이프
- `search.js`: 검색 결과 스니펫 이스케이프
- `admin-labels.js`: 청크 검색 결과 이스케이프
- `admin-groups.js`: 키워드 목록 이스케이프

**3단계: 검증**

- 모든 사용자 입력 데이터 이스케이프 확인
- XSS 공격 시뮬레이션 테스트

**예상 소요 시간**: 2-3일  
**담당자**: 개발팀 전체

---

### 2. 컨텍스트 윈도우 초과 처리

**오류 발생 횟수**: 3회 이상  
**처리 전략**: 프롬프트 길이 제한 강화

#### 처리 방법

**1단계: 토큰 계산 함수 추가**

```python
# backend/utils/token_counter.py (새 파일)
def estimate_tokens(text: str) -> int:
    """텍스트의 대략적인 토큰 수 추정"""
    # 간단한 추정: 공백 포함 평균 4자 = 1 토큰
    return len(text) // 4
```

**2단계: 프롬프트 길이 제한 강화**

```python
# 기존: max_length = 2000
# 변경: max_length = 1500 (토큰 수 고려)
MAX_PROMPT_LENGTH = 1500
MAX_TOKENS = 1800  # 안전 마진 포함
```

**3단계: 각 위치 수정**

- `backend/routers/reason.py`: Reasoning 프롬프트
- `scripts/embed_and_store.py`: 제목 생성 프롬프트
- `backend/routers/suggestions.py`: 키워드 추천 프롬프트

**4단계: 오류 발생 시 처리**

```python
# 3회 이상 오류 발생 시
if error_count >= 3:
    # 더 짧은 프롬프트로 재시도
    content = content[:1000]
    # 또는 청크를 여러 부분으로 나누어 처리
    chunks = split_content(content, max_length=1000)
```

**예상 소요 시간**: 1일  
**담당자**: 백엔드 개발자

---

## 🟡 우선순위 중간: 단기 처리

### 3. Qdrant 속성 오류 처리

**오류 발생 횟수**: 3회 이상  
**처리 전략**: 버전별 호환성 처리

#### 처리 방법

**1단계: Qdrant 버전 확인**

```python
# backend/services/system_service.py
def get_qdrant_version():
    try:
        client = QdrantClient(host="localhost", port=6333)
        # 버전 확인 로직
        return client.get_version()
    except Exception as e:
        return None
```

**2단계: 버전별 속성 처리**

```python
def get_points_count(collection_info):
    """Qdrant 버전별 포인트 수 가져오기"""
    # 3회 이상 오류 발생 시 대체 로직
    error_count = get_error_count('qdrant_points_count')

    if error_count >= 3:
        # 대체 방법: 다른 API 사용
        try:
            # points_count 속성 시도
            return collection_info.points_count
        except AttributeError:
            try:
                # vectors_count 속성 시도 (구버전)
                return collection_info.vectors_count
            except AttributeError:
                # 최종 대체: API 호출
                return get_points_count_via_api(collection_info.name)
    else:
        # 정상 로직
        return collection_info.points_count
```

**3단계: 오류 카운터 관리**

```python
# 오류 발생 시 카운터 증가
def handle_qdrant_error(error):
    error_count = increment_error_count('qdrant_points_count')
    if error_count >= 3:
        # 다음 로직으로 이동
        return use_alternative_method()
    else:
        # 재시도
        raise error
```

**예상 소요 시간**: 0.5일  
**담당자**: 백엔드 개발자

---

## 🟢 우선순위 낮음: 중기 개선

### 4. 네트워크 오류 처리 개선

**오류 발생 횟수**: 모든 페이지  
**처리 전략**: 통합 오류 처리 유틸리티

#### 처리 방법

**1단계: 통합 오류 처리 함수 생성**

```javascript
// web/public/js/error-handler.js (새 파일)
class ErrorHandler {
  constructor() {
    this.errorCounts = new Map();
  }

  async handleApiCall(url, options, retries = 3) {
    for (let i = 0; i < retries; i++) {
      try {
        const response = await fetch(url, options);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return await response.json();
      } catch (error) {
        const errorKey = `${url}_${error.message}`;
        const count = this.getErrorCount(errorKey);

        if (count >= 3) {
          // 3회 이상 오류 발생 시 다음 로직으로 이동
          return this.useAlternativeLogic(url, error);
        }

        this.incrementErrorCount(errorKey);

        if (i === retries - 1) {
          throw error;
        }

        // 재시도 전 대기
        await this.delay(1000 * (i + 1));
      }
    }
  }

  useAlternativeLogic(url, error) {
    // 대체 로직: 캐시된 데이터 사용 또는 오프라인 모드
    console.warn("Using alternative logic due to repeated errors");
    return this.getCachedData(url) || this.getOfflineData(url);
  }
}
```

**2단계: 각 페이지에 적용**

- 모든 API 호출을 `ErrorHandler`를 통해 처리
- 사용자 친화적인 오류 메시지 표시

**예상 소요 시간**: 1-2일  
**담당자**: 프론트엔드 개발자

---

## 📊 오류 카운터 관리

### 구현 방법

**1단계: 오류 카운터 저장소**

```javascript
// 로컬 스토리지 또는 메모리
const errorCounts = {
  xss_vulnerability: 0,
  context_window_exceeded: 0,
  qdrant_attribute_error: 0,
  // ...
};
```

**2단계: 오류 카운터 증가**

```javascript
function incrementErrorCount(errorType) {
  const key = `error_count_${errorType}`;
  const count = parseInt(localStorage.getItem(key) || "0") + 1;
  localStorage.setItem(key, count.toString());
  return count;
}
```

**3단계: 임계값 확인**

```javascript
function shouldUseAlternativeLogic(errorType) {
  const count = getErrorCount(errorType);
  return count >= 3;
}
```

---

## 🔄 분기 로직 플로우차트

```
오류 발생
    ↓
오류 타입 확인
    ↓
오류 카운터 증가
    ↓
카운터 >= 3?
    ├─ Yes → 다음 로직으로 이동
    │         ├─ 대체 방법 사용
    │         ├─ 우회 로직 실행
    │         └─ 사용자에게 알림
    │
    └─ No → 재시도
            ├─ 성공 → 카운터 리셋
            └─ 실패 → 카운터 증가 후 재시도
```

---

## 🎯 처리 우선순위

### 즉시 처리 (보안)

1. **XSS 취약점 수정**: 2-3일
2. **컨텍스트 윈도우 초과**: 1일

### 단기 처리 (기능)

3. **Qdrant 속성 오류**: 0.5일
4. **네트워크 오류 처리**: 1-2일

### 중기 개선 (UX)

5. **HTML 문자열 조작 개선**: 3-5일

---

## 📝 구현 체크리스트

### XSS 취약점 수정

- [ ] 이스케이프 함수 생성
- [ ] `knowledge.js` 수정
- [ ] `admin-approval.js` 수정
- [ ] `search.js` 수정
- [ ] `admin-labels.js` 수정
- [ ] `admin-groups.js` 수정
- [ ] XSS 공격 테스트

### 컨텍스트 윈도우 초과 처리

- [ ] 토큰 계산 함수 추가
- [ ] 프롬프트 길이 제한 강화
- [ ] `reason.py` 수정
- [ ] `embed_and_store.py` 수정
- [ ] `suggestions.py` 수정
- [ ] 오류 발생 시 대체 로직 추가

### Qdrant 속성 오류 처리

- [ ] Qdrant 버전 확인 함수 추가
- [ ] 버전별 속성 처리 로직 추가
- [ ] 오류 카운터 관리
- [ ] 대체 방법 구현

### 네트워크 오류 처리

- [ ] 통합 오류 처리 함수 생성
- [ ] 각 페이지에 적용
- [ ] 사용자 친화적인 메시지 추가
- [ ] 재시도 로직 구현

---

## 🔍 모니터링

### 오류 로깅

```javascript
function logError(errorType, error, context) {
  console.error(`[${errorType}]`, error, context);

  // 서버에 오류 로그 전송 (선택적)
  fetch("/api/errors", {
    method: "POST",
    body: JSON.stringify({
      type: errorType,
      message: error.message,
      context: context,
      timestamp: new Date().toISOString(),
    }),
  }).catch(() => {
    // 오류 로그 전송 실패는 무시
  });
}
```

### 오류 통계

- 오류 발생 빈도 추적
- 오류 타입별 통계
- 대체 로직 사용 빈도

---

## 📚 참고 자료

- [OWASP XSS Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [FastAPI Error Handling](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [Qdrant Python Client](https://qdrant.github.io/qdrant-client/)
