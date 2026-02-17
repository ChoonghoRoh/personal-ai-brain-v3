# Phase 16-3 Plan — AI 자동화 Phase 3 (UX·인프라)

## 목표

파일별 완료 즉시 반영(Streaming Results)과 Virtual Scroll로 대량 문서 UX를 개선한다.

## Task 구성

| Task | 도메인 | 내용 | 의존성 |
|------|--------|------|--------|
| 16-3-1 | [BE+FE] | doc_result SSE 이벤트 + FE 문서 완료 표시 | 16-2 완료 |
| 16-3-2 | [FE] | Virtual Scroll 문서 리스트 (가시 영역 ~22노드) | 16-3-1 |
| 16-3-3 | [BE+INFRA] | (DEFERRED) Celery/Redis 큐 — 인프라 확장 시 별도 Phase | — |

## 실행 순서

16-3-1 → 16-3-2 (순차, 동일 FE 파일 수정)
16-3-3은 DEFERRED (마스터 플랜: "인프라 확장 시 별도 Phase로 분리 가능")

## 변경 파일

| 파일 | Task | 변경 내용 |
|------|------|----------|
| `backend/services/automation/ai_workflow_service.py` | 16-3-1 | 배치 완료 시 doc_result 상태 저장 |
| `backend/services/automation/ai_workflow_state.py` | 16-3-1 | doc_results 리스트 + add_doc_result() |
| `backend/routers/automation/automation.py` | 16-3-1 | doc_result SSE 이벤트 전송 |
| `web/public/js/admin/ai-automation.js` | 16-3-1, 16-3-2 | doc_result 핸들링 + Virtual Scroll |
| `web/src/pages/admin/ai-automation.html` | 16-3-1 | doc-result 관련 DOM 요소 |
| `web/public/css/admin/admin-ai-automation.css` | 16-3-1, 16-3-2 | 완료 표시 스타일 + Virtual Scroll 스타일 |

## 참조

- [Phase 16 Master Plan §6](../phase-16-master-plan.md)
- [리스크 분석 §3.3 방안 K, A](../../planning/260217-1600-AI자동화기능-리스크분석.md)
