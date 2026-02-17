# Task 15-3-4: [FE] Reasoning 실행·진행·결과 표시

**우선순위**: 15-3 내 4순위
**의존성**: 15-3-3 (진입점)
**담당 팀원**: frontend-dev
**상태**: DONE

---

## §1. 개요

"선택 문서 Reasoning" 버튼 클릭 시 모드 선택 모달을 표시하고, 사용자가 모드와 질문을 입력한 후 실행하면 `POST /api/reasoning/run-on-documents` API를 호출하여 Reasoning을 실행한다. 완료 후 결과 페이지로 이동한다.

## §2. 파일 변경 계획

| 파일 | 유형 | 변경 내용 |
|------|------|----------|
| `web/public/js/admin/knowledge-files.js` | 수정 | 모달 생성·이벤트·API 호출·결과 이동 |
| `web/public/css/admin/admin-knowledge-files.css` | 수정 | 모달 오버레이·카드·모드 옵션 스타일 |

## §3. 작업 체크리스트 (Done Definition)

- [x] `showReasoningModeModal()` — 모달 동적 생성
  - 4대 모드 라디오 버튼 (design_explain 기본 선택)
  - 질문 입력 필드 (선택)
  - 실행/취소 버튼
  - 오버레이 클릭으로 닫기
- [x] `executeBulkReasoning(documentIds, mode, question)` — API 호출
  - `POST /api/reasoning/run-on-documents` fetch 호출
  - 성공 시 showSuccess 토스트 + `/reason?share={session_id}` 이동
  - 실패 시 showError 토스트
- [x] CSS 스타일 추가
  - `.modal-overlay` — 배경 오버레이 (fixed, z-index 1000)
  - `.reasoning-modal` — 모달 카드 (480px, 둥근 모서리, 그림자)
  - `.mode-option` — 모드 선택 카드 (호버 효과, 보라색 테마)
  - `.modal-field` — 입력 필드 스타일
  - `.modal-actions` — 버튼 정렬

## §4. 참조

- `web/public/js/admin/knowledge-files.js` — 모달 로직
- `web/public/css/admin/admin-knowledge-files.css` — 모달 스타일
- `backend/routers/reasoning/reason_document.py` — API 엔드포인트
