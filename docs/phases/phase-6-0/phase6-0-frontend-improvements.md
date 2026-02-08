# Phase 6.0: Frontend 개선 사항 정리

## 개요
프론트엔드의 공통 컴포넌트화, 보안 개선, 오류 수정 등을 진행했습니다.

## 개선 일자
2026-01-07

---

## 1. 공통 컴포넌트화

### 1.1 Header 컴포넌트 공통화
**파일**: `web/src/js/header-component.js`, `web/public/js/header-component.js`

**목적**: 모든 페이지에서 일관된 헤더와 네비게이션 제공

**주요 기능**:
- `renderHeader()` 함수로 동적 헤더 생성
- 현재 페이지 하이라이트 자동 처리
- 네비게이션 메뉴 통일 (대시보드, 검색, 지식 구조, Reasoning, AI 질의, 로그)
- 스타일 자동 주입

**적용 페이지**:
- `dashboard.html`
- `search.html`
- `knowledge.html`
- `reason.html`
- `document.html`
- `ask.html`
- `logs.html`

**사용 방법**:
```javascript
document.addEventListener('DOMContentLoaded', function() {
  renderHeader({
    title: '페이지 제목',
    subtitle: '페이지 부제목',
    currentPath: '/current-path'
  });
});
```

### 1.2 Layout 컴포넌트 공통화
**파일**: `web/src/js/layout-component.js`, `web/public/js/layout-component.js`

**목적**: Body와 Container 스타일 및 구조 공통화

**주요 기능**:
- `initLayout()` 함수로 공통 스타일 적용
- Body 기본 스타일 (폰트, 배경색, 색상)
- Container 스타일 (최대 너비 1200px, 중앙 정렬, 패딩)
- 반응형 디자인 지원 (모바일)

**공통화된 스타일**:
```css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, ...;
  background: #f5f5f5;
  color: #333;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}
```

**사용 방법**:
```javascript
document.addEventListener('DOMContentLoaded', function() {
  initLayout();
});
```

**효과**:
- 각 페이지에서 중복된 CSS 코드 제거
- 일관된 레이아웃 유지
- 유지보수성 향상

---

## 2. 스크립트 로드 최적화

### 2.1 중복 로드 문제 해결
**문제**: 
- `layout-component.js`와 `header-component.js`가 head와 body에 중복 로드됨
- `LAYOUT_STYLES`, `NAV_MENU` 등 상수 중복 선언 오류 발생

**해결 방법**:
1. **head에서 스크립트 제거**: 모든 페이지의 `<head>`에서 공통 스크립트 제거
2. **body 끝부분에만 로드**: 스크립트를 body 끝부분에만 배치
3. **중복 선언 방지**: window 객체에 이미 존재하면 재선언하지 않도록 수정

**수정된 파일**:
- `web/src/js/layout-component.js`: 중복 선언 방지 로직 추가
- `web/src/js/header-component.js`: 중복 선언 방지 로직 추가
- 모든 HTML 페이지: head에서 스크립트 제거

**코드 예시**:
```javascript
// layout-component.js
if (typeof window !== 'undefined') {
  if (!window.initLayout) {
    window.initLayout = initLayout;
    // ...
  }
}

// header-component.js
if (typeof window !== 'undefined') {
  if (!window.renderHeader) {
    window.renderHeader = renderHeader;
    // ...
  }
}
```

---

## 3. 문서 URL 인코딩 개선

### 3.1 이중 인코딩 방지
**파일**: `web/src/js/document-utils.js`

**문제**: 
- 문서 경로가 이중으로 인코딩되어 `brain%252Fprojects...` 형태로 변환됨
- 문서를 찾을 수 없는 오류 발생

**해결 방법**:
- `getDocumentUrl()` 함수에서 이미 인코딩된 경로 감지
- 디코딩 후 한 번만 재인코딩

**코드**:
```javascript
function getDocumentUrl(filePath) {
  if (!filePath) return '#';
  
  // 이미 인코딩된 경로인지 확인
  let decodedPath = filePath;
  try {
    decodedPath = decodeURIComponent(filePath);
    if (decodedPath !== filePath) {
      filePath = decodedPath; // 이미 인코딩된 경우 디코딩된 값 사용
    }
  } catch (e) {
    // 디코딩 실패 시 원본 사용
  }
  
  // 최종적으로 한 번만 인코딩
  return `/document/${encodeURIComponent(filePath)}`;
}
```

### 3.2 백엔드 경로 처리 개선
**파일**: `backend/routers/documents.py`

**문제**:
- `brain/brain%2Fprojects...` 형태로 이중 처리됨
- 경로 해석 오류

**해결 방법**:
1. `urllib.parse.unquote`로 추가 디코딩
2. `brain/`로 시작하는 경우: `PROJECT_ROOT / document_id`
3. 파일명만 있는 경우: `BRAIN_DIR / document_id`

**코드**:
```python
# 경로 정규화 및 디코딩
document_id = document_id.strip()
import urllib.parse
try:
    document_id = urllib.parse.unquote(document_id)
except:
    pass

# brain/로 시작하는 경우
if document_id.startswith("brain/"):
    doc_path = PROJECT_ROOT / document_id
# 파일명만 있는 경우
elif "/" not in document_id:
    doc_path = BRAIN_DIR / document_id
```

---

## 4. 보안 개선

### 4.1 마크다운 렌더링 보안 강화
**파일**: `web/src/pages/document.html`

**문제**:
- 마크다운 파일의 JavaScript 코드 블록이 실행될 수 있음
- `<script>` 태그가 그대로 실행되어 오류 발생

**해결 방법**:
- `marked.parse()` 결과에서 `<script>` 태그 제거
- XSS 공격 방지

**코드**:
```javascript
// Markdown 렌더링
let html = marked.parse(data.content || "");

// <script> 태그 제거 (보안 및 실행 오류 방지)
const tempDiv = document.createElement("div");
tempDiv.innerHTML = html;
const scripts = tempDiv.querySelectorAll("script");
scripts.forEach((script) => script.remove());
html = tempDiv.innerHTML;
```

### 4.2 문서 접근 권한 검증
**파일**: `backend/routers/documents.py`

**개선 사항**:
- `brain/` 디렉토리 내의 파일만 접근 가능하도록 검증 강화
- 상세한 오류 메시지 제공 (디버깅 용이)
- 경로 정규화 및 검증 로직 개선

---

## 5. 오류 수정

### 5.1 Illegal return statement 오류
**파일**: `web/src/pages/document.html`

**문제**: 함수 밖에 `return` 문이 있어서 오류 발생

**해결**: `return` 문을 `loadDocument()` 함수 내부로 이동

### 5.2 JavaScript 변수 중복 선언 오류
**파일**: `web/src/pages/dashboard.html`

**문제**: `sizeKB`, `date`, `dateStr`, `timeStr` 변수가 중복 선언됨

**해결**: 중복 선언 제거

---

## 6. 디버깅 개선

### 6.1 프론트엔드 디버깅 로그
**파일**: `web/src/pages/document.html`

**추가된 로그**:
- 문서 로드 시 원본/인코딩된 경로 정보
- 실제 API URL
- 오류 발생 시 상세 정보

**코드**:
```javascript
console.log("Loading document:", {
  original: documentId,
  encoded: encodedId,
  apiUrl: apiUrl,
  pathname: window.location.pathname
});
```

### 6.2 백엔드 오류 메시지 개선
**파일**: `backend/routers/documents.py`

**개선 사항**:
- 오류 메시지에 경로 정보 포함
- 파일 존재 여부 확인 정보 제공
- 더 명확한 오류 메시지

---

## 7. 파일 구조

### 7.1 공통 컴포넌트 파일
```
web/
├── src/
│   └── js/
│       ├── header-component.js    # Header 컴포넌트
│       ├── layout-component.js    # Layout 컴포넌트
│       └── document-utils.js      # 문서 유틸리티
└── public/
    └── js/
        ├── header-component.js    # 정적 파일용
        ├── layout-component.js    # 정적 파일용
        └── document-utils.js      # 정적 파일용
```

### 7.2 적용된 페이지
- `web/src/pages/dashboard.html`
- `web/src/pages/search.html`
- `web/src/pages/knowledge.html`
- `web/src/pages/reason.html`
- `web/src/pages/document.html`
- `web/src/pages/ask.html`
- `web/src/pages/logs.html`

---

## 8. 사용 가이드

### 8.1 새 페이지 추가 시
1. **Layout 초기화**:
```javascript
<script src="/static/js/layout-component.js"></script>
<script>
  document.addEventListener('DOMContentLoaded', function() {
    initLayout();
  });
</script>
```

2. **Header 렌더링**:
```javascript
<script src="/static/js/header-component.js"></script>
<script>
  document.addEventListener('DOMContentLoaded', function() {
    renderHeader({
      title: '페이지 제목',
      subtitle: '페이지 부제목',
      currentPath: '/current-path'
    });
  });
</script>
```

3. **문서 링크 생성**:
```javascript
<script src="/static/js/document-utils.js"></script>
<script>
  // 문서 링크 생성
  const link = createDocumentLink('brain/projects/test.md', '테스트 문서');
  
  // 문서 카드 생성
  const card = createDocumentCard({
    file_path: 'brain/projects/test.md',
    name: '테스트 문서',
    size: 1024,
    modified: Date.now() / 1000
  });
</script>
```

---

## 9. 향후 개선 사항

### 9.1 예정된 작업
- [ ] CSS 파일 분리 (현재는 JavaScript에 인라인)
- [ ] 컴포넌트 빌드 시스템 도입 (선택사항)
- [ ] TypeScript 전환 (선택사항)
- [ ] 테스트 코드 작성

### 9.2 개선 가능 영역
- 에러 핸들링 통일
- 로딩 상태 표시 컴포넌트화
- 알림/토스트 메시지 컴포넌트
- 모달 컴포넌트

---

## 10. 참고 사항

### 10.1 스크립트 로드 순서
1. `layout-component.js` (스타일 초기화)
2. `header-component.js` (헤더 렌더링)
3. `document-utils.js` (문서 유틸리티, 필요한 경우)
4. 페이지별 스크립트

### 10.2 브라우저 호환성
- 최신 브라우저 지원 (Chrome, Firefox, Safari, Edge)
- ES6+ 문법 사용
- `querySelector`, `addEventListener` 등 표준 API 사용

### 10.3 성능 고려사항
- 스크립트는 body 끝부분에 배치하여 렌더링 차단 방지
- 중복 선언 방지로 메모리 효율성 향상
- 공통 스타일을 한 번만 주입하여 성능 최적화

---

## 변경 이력

- **2026-01-07**: 초기 문서 작성
  - Header 컴포넌트 공통화
  - Layout 컴포넌트 공통화
  - 스크립트 중복 로드 문제 해결
  - 문서 URL 인코딩 개선
  - 보안 개선
  - 오류 수정

