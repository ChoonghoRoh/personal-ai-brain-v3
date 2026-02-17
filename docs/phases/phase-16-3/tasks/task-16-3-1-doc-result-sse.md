# Task 16-3-1: [BE+FE] 파일별 완료 즉시 반영

**우선순위**: 16-3 내 1순위
**예상 작업량**: 높음
**의존성**: Phase 16-2 완료
**담당 팀원**: backend-dev + frontend-dev
**상태**: 진행중

---

## §1. 개요

배치 단위로 문서 처리가 완료될 때마다 `doc_result` SSE 이벤트를 발행하여, 프론트엔드에서 문서별 완료 상태를 즉시 반영한다.

참조: [리스크 분석 §3.3 방안 K](../../../planning/260217-1600-AI자동화기능-리스크분석.md)

## §2. 파일 변경 계획

| 구분 | 파일 | 변경 내용 |
|------|------|----------|
| 수정 | `backend/services/automation/ai_workflow_state.py` | TaskState에 doc_results 리스트 + add_doc_result() |
| 수정 | `backend/services/automation/ai_workflow_service.py` | 배치 완료 시 add_doc_result() 호출 |
| 수정 | `backend/routers/automation/automation.py` | stream_progress에서 doc_result 이벤트 전송 |
| 수정 | `web/public/js/admin/ai-automation.js` | doc_result SSE 핸들러 + 문서 완료 표시 |
| 수정 | `web/src/pages/admin/ai-automation.html` | doc-result DOM 요소 |
| 수정 | `web/public/css/admin/admin-ai-automation.css` | 완료 문서 스타일 |

## §3. 작업 체크리스트 (Done Definition)

- [ ] TaskState에 doc_results: List[Dict] 필드 추가
- [ ] add_doc_result(task_id, doc_ids, batch_stats) 메서드
- [ ] execute_workflow에서 배치 완료 시 add_doc_result 호출
- [ ] stream_progress에서 doc_result 이벤트 감지·전송
- [ ] FE: doc_result 이벤트 수신 시 문서 체크마크 표시
- [ ] FE: 실시간 결과 패널에 배치별 결과 추가
- [ ] 80문서 4배치 시 doc_result 4회 발행

## §4. 참조

- [Phase 16 Master Plan §6 — 16-3-1](../../phase-16-master-plan.md)
