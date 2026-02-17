# Task 15-3-3: [FE] "이 폴더로 Reasoning" 진입점

**우선순위**: 15-3 내 3순위
**의존성**: 15-3-1 (API 완성)
**담당 팀원**: frontend-dev
**상태**: DONE

---

## §1. 개요

파일관리 화면(knowledge-files)에서 사용자가 여러 문서를 선택하고 벌크 Reasoning을 실행할 수 있는 진입점을 구현한다. 테이블에 체크박스 열을 추가하고, 선택된 문서 수에 따라 "선택 문서 Reasoning" 버튼이 동적으로 활성화된다.

## §2. 파일 변경 계획

| 파일 | 유형 | 변경 내용 |
|------|------|----------|
| `web/src/pages/admin/knowledge-files.html` | 수정 | 체크박스 th 추가, 벌크 Reasoning 버튼, colspan 8 |
| `web/public/js/admin/knowledge-files.js` | 수정 | 체크박스 td 생성, 전체 선택, 벌크 버튼 이벤트 |

## §3. 작업 체크리스트 (Done Definition)

- [x] HTML 테이블 헤더에 전체 선택 체크박스 (`#select-all-files`) 추가
- [x] `renderFileList()` — 각 행에 `.file-select-cb` 체크박스 추가 (인덱싱된 문서만)
- [x] "선택 문서 Reasoning" 버튼 (`#bulk-reasoning-btn`) — disabled 기본, 선택 시 활성화
- [x] `getSelectedDocumentIds()` — 선택된 document_id 목록 반환
- [x] `updateBulkReasoningBtn()` — 선택 개수 반영 동적 업데이트
- [x] 전체 선택/해제 체크박스 연동
- [x] 이벤트 위임으로 개별 체크박스 변경 감지

## §4. 참조

- `web/src/pages/admin/knowledge-files.html` — HTML 템플릿
- `web/public/js/admin/knowledge-files.js` — JS 로직
- `web/public/css/admin/admin-knowledge-files.css` — 체크박스/벌크 스타일
