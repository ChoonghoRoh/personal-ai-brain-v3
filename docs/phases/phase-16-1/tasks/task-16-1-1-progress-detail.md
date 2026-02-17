# Task 16-1-1: [BE] 단계별 세부 진행률·청크 카운터·ETA

**우선순위**: 16-1 내 1순위
**예상 작업량**: 중간
**의존성**: 없음 (Phase 15-2 완료 전제)
**담당 팀원**: backend-dev
**상태**: 대기

---

## §1. 개요

AI 자동화 SSE `progress` 이벤트에 세부 진행률(현재/전체 청크, 항목명)과 예상 잔여 시간(ETA)을 추가하여, 대량 파일 처리 시 사용자가 진행 상황을 정확히 인지할 수 있게 한다.

참조: [리스크 분석 §3.1 방안 B](../../../planning/260217-1600-AI자동화기능-리스크분석.md)

## §2. 파일 변경 계획

| 구분 | 파일 | 변경 내용 |
|------|------|----------|
| 수정 | `backend/services/automation/ai_workflow_service.py` | progress 발행 로직에 `detail`, `eta_seconds` 추가 |
| 수정 | (해당 시) SSE 응답 라우터 | progress 이벤트 스키마 확장 |

## §3. 작업 체크리스트 (Done Definition)

- [ ] `progress` SSE 이벤트 payload에 `detail: { current: int, total: int, item_name: str }` 포함
- [ ] `eta_seconds: float | null` 필드 추가 (선택적, 계산 불가 시 null)
- [ ] 단계 내 청크/문서 인덱스로 세부 진행률 계산 로직 구현
- [ ] 기존 `progress_pct` 필드 호환 유지 (기존 FE 동작 깨지지 않음)
- [ ] 기존 자동화 테스트 통과 (`tests/test_automation*.py` 또는 관련 테스트)

## §4. 참조

- [Phase 16 Master Plan §4.2 — 16-1-1](../../phase-16-master-plan.md)
- [AI 자동화 리스크 분석 §3.1 방안 B](../../../planning/260217-1600-AI자동화기능-리스크분석.md)
