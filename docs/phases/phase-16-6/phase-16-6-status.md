---
phase: "16-6"
title: "Web CSS 리팩토링"
status: "done"
started_at: "2026-02-17"
completed_at: "2026-02-17"
---

# Phase 16-6: Web CSS 리팩토링

## 목표

CSS 500줄 초과 5개 파일(settings-common.css 제외)을 페이지/기능 단위로 분할하여 유지보수성 개선.

## 완료 내역

### Task 16-6-1: reason.css + knowledge CSS 분할

| 원본 파일 | 줄 수 | 분할 결과 | 줄 수 |
|-----------|:-----:|-----------|:-----:|
| reason.css (1,586줄) | 1,586 | reason.css | 502 |
| | | reason-sections.css | 597 |
| | | reason-advanced.css | 485 |
| knowledge-detail.css (746줄) | 746 | knowledge-detail.css | 407 |
| | | knowledge-detail-relations.css | 339 |
| knowledge-admin.css (603줄) | 603 | knowledge-admin.css | 379 |
| | | knowledge-admin-approval.css | 224 |

### Task 16-6-2: admin CSS 분할

| 원본 파일 | 줄 수 | 분할 결과 | 줄 수 |
|-----------|:-----:|-----------|:-----:|
| admin-knowledge-files.css (704줄) | 704 | admin-knowledge-files.css | 409 |
| | | admin-knowledge-files-upload.css | 295 |
| admin-ai-automation.css (595줄) | 595 | admin-ai-automation.css | 379 |
| | | admin-ai-automation-results.css | 216 |

### settings-common.css (534줄) — 현행 유지

5개 설정 페이지 공유 스타일. 분할 시 5곳 HTML 수정 필요하므로 유지.

## 수정 파일 목록

### CSS (수정 5 + 신규 7 = 12개)
- `web/public/css/reason.css` — 축소 (502줄)
- `web/public/css/reason-sections.css` — 신규 (597줄)
- `web/public/css/reason-advanced.css` — 신규 (485줄)
- `web/public/css/knowledge/knowledge-detail.css` — 축소 (407줄)
- `web/public/css/knowledge/knowledge-detail-relations.css` — 신규 (339줄)
- `web/public/css/knowledge/knowledge-admin.css` — 축소 (379줄)
- `web/public/css/knowledge/knowledge-admin-approval.css` — 신규 (224줄)
- `web/public/css/admin/admin-knowledge-files.css` — 축소 (409줄)
- `web/public/css/admin/admin-knowledge-files-upload.css` — 신규 (295줄)
- `web/public/css/admin/admin-ai-automation.css` — 축소 (379줄)
- `web/public/css/admin/admin-ai-automation-results.css` — 신규 (216줄)

### HTML (5개 수정)
- `web/src/pages/reason.html` — link 2개 추가
- `web/src/pages/knowledge/knowledge-detail.html` — link 1개 추가
- `web/src/pages/knowledge/knowledge-admin.html` — link 1개 추가
- `web/src/pages/admin/knowledge-files.html` — link 1개 추가
- `web/src/pages/admin/ai-automation.html` — link 1개 추가
