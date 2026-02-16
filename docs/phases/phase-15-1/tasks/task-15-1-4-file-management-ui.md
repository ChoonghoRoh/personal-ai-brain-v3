# Task 15-1-4: 파일관리 UI 페이지

**우선순위**: 15-1 내 4순위
**의존성**: 15-1-1, 15-1-2, 15-1-3
**담당 팀원**: frontend-dev
**상태**: 대기

---

## §1. 개요

지식관리 Admin 메뉴에 "파일관리" 페이지를 추가한다. 지정 폴더 경로 표시/변경, 파일 목록 테이블, 업로드, 동기화 기능을 제공한다.

## §2. 파일 변경 계획

| 파일 | 유형 | 변경 내용 |
|------|------|----------|
| `web/src/pages/admin/knowledge-files.html` | 신규 | 파일관리 HTML 페이지 |
| `web/public/js/admin/knowledge-files.js` | 신규 | 파일관리 JS 모듈 |
| `web/public/css/admin/admin-knowledge-files.css` | 신규 | 파일관리 스타일 |
| `web/public/js/components/header-component.js` | 수정 | ADMIN_MENU에 "파일관리" 항목 추가 |
| `backend/main.py` | 수정 | `_HTML_ROUTES`에 파일관리 라우트 추가 |

## §3. 작업 체크리스트 (Done Definition)

### HTML 페이지
- [ ] layout-component, header-component 포함
- [ ] 폴더 경로 표시 영역 + 변경 버튼 (모달 또는 인라인 수정)
- [ ] 파일 목록 테이블 (파일명, 크기, 수정일, document_id, 청크 수, 상태)
- [ ] 업로드 버튼 + 드래그앤드롭 영역
- [ ] 동기화 버튼
- [ ] `<script type="module">` 사용

### JS 모듈
- [ ] ESM import/export 패턴
- [ ] GET `/api/knowledge/folder-config` 호출 → 폴더 경로 표시
- [ ] GET `/api/knowledge/folder-files` 호출 → 테이블 렌더링
- [ ] PUT `/api/knowledge/folder-config` → 경로 변경
- [ ] POST `/api/knowledge/upload` → 파일 업로드 (FormData)
- [ ] POST `/api/knowledge/sync` → 동기화 실행 + 결과 표시
- [ ] API 에러 핸들링 (try-catch + 사용자 메시지)
- [ ] innerHTML 사용 시 esc() 적용

### 통합
- [ ] `_HTML_ROUTES`에 `("/admin/knowledge-files", "admin/knowledge-files.html", "파일관리")` 등록
- [ ] ADMIN_MENU에 `{ path: '/admin/knowledge-files', label: '파일관리', icon: 'bi-folder2-open' }` 추가
- [ ] 페이지 로드 시 콘솔 에러 없음
- [ ] 기존 LNB·레이아웃 스타일과 일관성

## §4. 참조

- `web/src/pages/admin/labels.html` — 기존 Admin 페이지 구조 참조
- `web/public/js/admin/admin-labels.js` — Admin JS 패턴 참조
- `web/public/js/components/header-component.js` — ADMIN_MENU 배열 위치
- `backend/main.py` — `_HTML_ROUTES` 배열 위치
