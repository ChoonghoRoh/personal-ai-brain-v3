# Phase 16-1 Todo List — AI 자동화 즉시 적용

**Phase**: 16-1
**기준**: [phase-16-1-plan.md](phase-16-1-plan.md)

---

- [ ] Task 16-1-1: [BE] 단계별 세부 진행률·청크 카운터·ETA (Owner: backend-dev)
  - `backend/services/automation/ai_workflow_service.py` progress 발행 로직 수정
  - SSE `progress` 이벤트에 `detail: { current, total, item_name }`, `eta_seconds` 필드 추가
  - 기존 `progress_pct` 호환 유지
  - 완료 기준: SSE 클라이언트에서 `d.detail.current/total`, `d.eta_seconds` 수신 가능

- [ ] Task 16-1-2: [FE] 파일 선택 시 사전 검증 UI (Owner: frontend-dev)
  - `web/public/js/admin/ai-automation.js` 선택 변경 이벤트 핸들러 추가
  - 예상 청크 ≈ selected.length * 12, 예상 소요 ≈ ceil(예상청크/10) 분
  - 50개 초과 시 "대량 처리 — 배치 분할 권장" 경고 표시
  - (선택) `web/public/css/admin/admin-ai-automation.css` warn 스타일 추가
  - 완료 기준: 체크박스 선택/해제 시 요약 영역 갱신, 50개 초과 시 warn 스타일

- [ ] Task 16-1-3: [BE] DB 트랜잭션 분할 (Owner: backend-dev)
  - `backend/services/automation/ai_workflow_service.py` execute_workflow 수정
  - 단계별 `SessionLocal()` 컨텍스트 분리: 텍스트추출→commit; 청크생성→commit; ...
  - 중간 실패 시 해당 단계 이전 커밋 유지
  - 완료 기준: 단계 경계마다 세션 종료·신규 세션. 기존 6단계 동작 결과 일치

- [ ] Task 16-1-4: [FS] SSE Heartbeat·재연결 (Owner: backend-dev + frontend-dev)
  - [BE] `ai_workflow_service.py` 또는 progress 스트리밍 라우터에서 0.5~5s 간격 `event: heartbeat` 발행
  - [FE] `ai-automation.js` EventSource 래핑: heartbeat 수신 시 lastEventTime 갱신, 30초 미수신 시 reconnect
  - 재연결 시 기존 task_id로 progress 재구독
  - 완료 기준: 장시간 실행 중 타임아웃 시에도 재연결 후 진행률 재개
