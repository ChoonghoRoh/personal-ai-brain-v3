# Web (프론트엔드)

백엔드와 동일하게 **용도별 하위 폴더**로 정리되어 있습니다. 서빙 경로는 `backend/main.py`에서 `web/public`을 `/static`으로 마운트합니다.

## 구조

### public/ (정적 파일, URL prefix `/static`)

| 경로 | 역할 | 포함 |
|------|------|------|
| **css/** | 스타일 | 루트: dashboard, ask, document, logs, reason, search / **admin/** / **knowledge/** |
| **js/components/** | 공통 컴포넌트·유틸 | layout-component, header-component, utils, document-utils, pagination-component, text-formatter |
| **js/admin/** | 관리자·승인·키워드그룹·라벨 | admin-*, chunk-approval-manager, keyword-group-*, label-manager, knowledge-admin |
| **js/knowledge/** | 지식 스튜디오·상세·매칭 | knowledge, knowledge-detail, knowledge-label-matching, knowledge-relation-matching |
| **js/search/** | 검색 | search |
| **js/document/** | 문서 뷰어 | document |
| **js/reason/** | Reasoning Lab | reason |
| **js/ask/** | AI 질의 | ask |
| **js/logs/** | 로그 | logs |
| **js/dashboard/** | 대시보드 | dashboard |

### src/pages/ (HTML 템플릿)

- **admin/** — 라벨·그룹·승인 (`admin/labels.html`, `admin/groups.html`, `admin/approval.html`)
- **knowledge/** — 지식 스튜디오·상세·매칭·관리 (`knowledge.html`, `knowledge-detail.html`, …)
- 루트 — dashboard, search, document, ask, logs, reason

템플릿 이름은 `backend/main.py`에서 `templates_dir` 기준 상대 경로로 사용됩니다 (예: `knowledge/knowledge.html`).

### src/js/

공통 JS 소스(선택). 실제 서빙은 `public/js/` 기준입니다.

## HTML에서 참조 예

```html
<link rel="stylesheet" href="/static/css/knowledge/knowledge.css" />
<script src="/static/js/components/utils.js"></script>
<script src="/static/js/knowledge/knowledge.js"></script>
```

## backend와의 대응

- **admin** — 라벨·그룹·승인 API
- **knowledge** — 지식·청크·관계 API
- **search** — 검색 API
- **document** — 문서 API
- **reason** — 추론 API
- **ask** — AI 질의 API
- **logs** — 로그 API
- **dashboard** — 시스템/대시보드 API
