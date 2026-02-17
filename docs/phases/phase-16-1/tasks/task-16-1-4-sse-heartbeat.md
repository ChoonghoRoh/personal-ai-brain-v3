# Task 16-1-4: [FS] SSE Heartbeat·재연결

**우선순위**: 16-1 내 4순위
**예상 작업량**: 중간
**의존성**: 16-1-1·16-1-3 이후 (동일 서비스 파일 BE 파트)
**담당 팀원**: backend-dev + frontend-dev
**상태**: 대기

---

## §1. 개요

장시간 AI 자동화 실행 중 SSE 연결이 프록시/브라우저 타임아웃으로 끊기는 문제를 방지하기 위해, 백엔드에서 주기적 heartbeat 이벤트를 발행하고 프론트엔드에서 heartbeat 미수신 시 자동 재연결하는 메커니즘을 구현한다.

참조: [리스크 분석 §3.1 방안 D](../../../planning/260217-1600-AI자동화기능-리스크분석.md)

## §2. 파일 변경 계획

| 구분 | 파일 | 변경 내용 |
|------|------|----------|
| 수정 | `backend/services/automation/ai_workflow_service.py` 또는 progress 라우터 | heartbeat 이벤트 발행 (0.5~5s 간격) |
| 수정 | `web/public/js/admin/ai-automation.js` | EventSource 래핑, heartbeat 감시, 30s 타임아웃 재연결 |

## §3. 작업 체크리스트 (Done Definition)

- [ ] [BE] progress 스트림에서 `event: heartbeat` 주기적 발행 (0.5~5s 간격)
- [ ] [FE] heartbeat 수신 시 `lastEventTime` 갱신
- [ ] [FE] 30초 heartbeat 미수신 시 EventSource 종료 + 3초 후 재연결
- [ ] [FE] 재연결 시 기존 task_id로 progress 재구독
- [ ] 장시간 실행 중 네트워크 차단 후 복구 시 진행률 재개 확인
- [ ] 기존 AI 자동화 동작에 영향 없음

## §4. 참조

- [Phase 16 Master Plan §4.2 — 16-1-4](../../phase-16-master-plan.md)
