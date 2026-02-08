# Phase 7.9.8: 반복 오류 정리 (3회 이상 발생)

**작성일**: 2026-01-10

---

## 🔴 반복 오류 목록

### 1. XSS 취약점 (5회 이상 발견)

**발생 위치**:

1. `/knowledge` - 청크 내용 HTML 직접 삽입
2. `/admin/approval` - 청크 상세 내용 HTML 직접 삽입
3. `/search` - 검색 결과 스니펫 HTML 직접 삽입
4. `/admin/labels` - 청크 검색 결과 HTML 직접 삽입
5. `/admin/groups` - 키워드 목록 HTML 직접 삽입

**오류 패턴**:

```javascript
// 문제 코드 패턴
element.innerHTML = userData; // XSS 위험
element.innerHTML = `<div>${userInput}</div>`; // XSS 위험
```

**해결 방안**:

```javascript
// 안전한 코드
element.textContent = userData; // 텍스트만 표시
// 또는
element.innerHTML = escapeHtml(userData); // 이스케이프 처리
```

**우선순위**: 🔴 높음 (보안 취약점)

---

### 2. 컨텍스트 윈도우 초과 (3회 이상 발견)

**발생 위치**:

1. `/reason` - Reasoning 실행 시
2. AI 제목 생성 스크립트
3. 키워드 추천 스크립트

**오류 메시지**:

```
ERROR: The prompt size exceeds the context window
LLaMA ERROR: The prompt is 2119 tokens and the context window is 2048!
```

**원인**:

- 프롬프트 길이가 모델의 컨텍스트 윈도우(2048 토큰)를 초과
- `max_length = 2000`으로 제한했지만 토큰화 후 실제 토큰 수가 더 많음

**해결 방안**:

1. 프롬프트 길이를 1500자로 제한
2. 토큰 수를 직접 계산하여 제한
3. 긴 청크는 여러 부분으로 나누어 처리

**우선순위**: 🟡 중간 (기능 동작 불가)

---

### 3. Qdrant 속성 오류 (3회 이상 발견)

**발생 위치**:

1. `/dashboard` - 시스템 상태 조회
2. `backend/services/system_service.py` - Qdrant 상태 확인
3. 시스템 상태 파일 생성

**오류 메시지**:

```
'CollectionInfo' object has no attribute 'vectors_count'
```

**원인**:

- Qdrant 버전 차이로 인한 속성명 불일치
- 구버전: `vectors_count`
- 신버전: `points_count` 또는 다른 속성명

**해결 방안**:

1. Qdrant 버전 확인
2. 버전별 호환성 처리
3. try-except로 안전하게 처리

**우선순위**: 🟡 중간 (간헐적 오류)

---

### 4. 네트워크 오류 처리 패턴 (모든 페이지)

**발생 위치**:

- 모든 API 호출 페이지

**오류 패턴**:

```javascript
try {
  const response = await fetch(url);
  // ...
} catch (error) {
  console.error("오류:", error);
  // 사용자에게 친화적인 메시지 표시 필요
}
```

**문제점**:

- 네트워크 오류와 API 오류를 구분하지 않음
- 사용자에게 명확한 오류 메시지 제공 부족
- 재시도 로직 없음

**해결 방안**:

1. 네트워크 오류와 API 오류 구분
2. 사용자 친화적인 오류 메시지
3. 재시도 로직 추가 (선택적)

**우선순위**: 🟢 낮음 (기능은 작동하나 UX 개선)

---

### 5. HTML 문자열 직접 조작 (모든 페이지)

**발생 위치**:

- 모든 페이지의 JavaScript 파일

**오류 패턴**:

```javascript
// 문제 코드
element.innerHTML = `
  <div>${data.name}</div>
  <div>${data.content}</div>
`;
```

**문제점**:

- XSS 취약점
- 유지보수 어려움
- 템플릿 엔진 없음

**해결 방안**:

1. 템플릿 엔진 도입 (Handlebars, Mustache 등)
2. 또는 `textContent` 사용
3. 또는 이스케이프 함수 사용

**우선순위**: 🟡 중간 (보안 및 유지보수성)

---

## 📊 오류 통계

### 오류 유형별 발생 횟수

| 오류 유형            | 발생 횟수   | 우선순위 | 상태      |
| -------------------- | ----------- | -------- | --------- |
| XSS 취약점           | 5+          | 높음     | ✅ 완료   |
| 컨텍스트 윈도우 초과 | 3+          | 중간     | ✅ 완료   |
| Qdrant 속성 오류     | 3+          | 중간     | ✅ 완료   |
| 네트워크 오류 처리   | 모든 페이지 | 낮음     | ⏸️ 보류   |
| HTML 문자열 조작     | 모든 페이지 | 중간     | ⏸️ 보류   |

---

## 🎯 처리 계획

### 즉시 처리 (보안)

1. **XSS 취약점 수정**: 모든 페이지의 사용자 입력 데이터 이스케이프 처리
   - 예상 소요 시간: 2-3일
   - 영향 범위: 모든 페이지
   - **상태**: ✅ 완료

### 단기 처리 (기능)

2. **컨텍스트 윈도우 초과 처리**: 프롬프트 길이 제한 강화

   - 예상 소요 시간: 1일
   - 영향 범위: Reasoning, AI 제목 생성, 키워드 추천
   - **상태**: ✅ 완료

3. **Qdrant 호환성 처리**: 버전별 속성명 처리
   - 예상 소요 시간: 0.5일
   - 영향 범위: 시스템 상태 조회
   - **상태**: ✅ 완료

### 중기 개선 (UX)

4. **네트워크 오류 처리 개선**: 사용자 친화적인 오류 메시지

   - 예상 소요 시간: 1-2일
   - 영향 범위: 모든 페이지
   - **상태**: ⏸️ 보류 (사용성 개선, 나중에 처리)

5. **템플릿 엔진 도입**: HTML 문자열 조작 개선
   - 예상 소요 시간: 3-5일
   - 영향 범위: 모든 페이지
   - **상태**: ⏸️ 보류 (사용성 개선, 나중에 처리)

---

## 📝 관련 파일

### XSS 취약점

- `web/public/js/knowledge.js`
- `web/public/js/admin-approval.js`
- `web/public/js/search.js`
- `web/public/js/admin-labels.js`
- `web/public/js/admin-groups.js`

### 컨텍스트 윈도우 초과

- `backend/routers/reason.py`
- `scripts/embed_and_store.py` (제목 생성)
- `backend/routers/suggestions.py` (키워드 추천)

### Qdrant 속성 오류

- `backend/services/system_service.py`
- `web/public/js/dashboard.js`
