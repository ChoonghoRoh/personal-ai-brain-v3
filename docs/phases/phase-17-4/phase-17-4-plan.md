# Phase 17-4 Plan — AI 질의 고도화: 멀티턴 대화 + 기록 관리

**Phase**: 17-4
**목표**: 멀티턴 대화(session_id) + 이전 대화 컨텍스트 주입 + 자동 요약 + 대화 기록 그리드 관리
**선행**: Phase 17-3 완료
**기준 문서**: [Phase 17 개발 요구사항 §7](../../planning/260218-0830-phase17-개발-요구사항.md)

---

## 1. 배경

현재 AI Reasoning 시스템은 각 질의가 독립적으로 처리되어, 이전 대화 맥락을 활용한 연속 질의가 불가능하다. session_id 필드와 Conversation/ReasoningResult 모델이 이미 존재하지만, 세션 라이프사이클 관리와 컨텍스트 주입 로직이 없다.

### 1.1 기존 인프라 현황

| 항목 | 현재 상태 | 비고 |
|------|----------|------|
| session_id 필드 | ✅ ReasoningResult + Conversation 모델에 존재 | 미활용 |
| /api/conversations | ✅ CRUD + session_id 필터링 존재 | offset/limit 지원 |
| /api/reasoning-results | ✅ CRUD + session_id 필터링 존재 | session_id 인덱스 |
| ReasoningResult.summary | ✅ 필드 존재 | 미활용 |
| SSE 스트리밍 | ✅ 5단계 파이프라인 구현 완료 | reason_stream.py |
| 컨텍스트 주입 | ❌ 이전 대화 참조 없음 | 신규 |
| 세션 라이프사이클 | ❌ 생성/목록/삭제 없음 | 신규 |
| 자동 요약 | ❌ 답변 후 요약 생성 없음 | 신규 |

## 2. 범위

| Task | 도메인 | 내용 | 담당 | 변경 파일 |
|------|--------|------|------|----------|
| 17-4-1 | [BE] | 세션 관리 API | backend-dev | reason_store.py |
| 17-4-2 | [BE] | 이어서 질문 API (session_id + 컨텍스트 주입) | backend-dev | reason_stream.py, stream_executor.py |
| 17-4-3 | [BE] | 자동 요약 생성 | backend-dev | stream_executor.py |
| 17-4-4 | [BE] | 페이지네이션 + 다중 삭제 API | backend-dev | reason_store.py |
| 17-4-5 | [FE] | 대화 스레드 UI + "이어서 질문하기" 버튼 | frontend-dev | reason.html, reason-control.js |
| 17-4-6 | [FE] | 대화 기록 그리드 + 페이지네이션 + 선택 삭제 | frontend-dev | reason-render.js, reason.html |

## 3. 완료 기준

- [ ] POST /api/reason/sessions → 새 세션 생성 (UUID 반환)
- [ ] GET /api/reason/sessions → 세션 목록 (page/size)
- [ ] GET /api/reason/sessions/{session_id} → 세션 상세 (대화 이력 포함)
- [ ] DELETE /api/reason/sessions/{session_id} → 세션 삭제
- [ ] POST /api/reason/stream에 session_id 파라미터 추가
- [ ] 이전 대화 요약을 LLM 프롬프트에 자동 주입
- [ ] 답변 완료 후 자동 요약 생성 → ReasoningResult.summary 저장
- [ ] DELETE /api/reason/sessions/bulk → 다중 세션 삭제
- [ ] 대화 스레드 패널: 현재 세션의 이전 턴 표시
- [ ] "이어서 질문하기" 버튼 → session_id 유지하며 새 질의
- [ ] "새 대화 시작" 버튼 → 새 session_id 생성
- [ ] 대화 기록 그리드: 세션 목록 카드뷰 + 페이지네이션
- [ ] 체크박스 다중 선택 + 일괄 삭제

## 4. 의존성

- 17-4-1 (세션 API) → 17-4-2 (이어서 질문), 17-4-4 (페이지네이션/삭제)
- 17-4-2 (이어서 질문) → 17-4-3 (자동 요약)
- 17-4-1~4 (BE) → 17-4-5, 17-4-6 (FE)
- 권장 순서: 17-4-1 → 17-4-2 → 17-4-3 → 17-4-4 → 17-4-5 + 17-4-6 병렬

## 5. 리스크

| 리스크 | 대응 |
|--------|------|
| 이전 대화 컨텍스트가 너무 길어 LLM 토큰 초과 | 최근 3턴만 요약 주입, 요약 길이 제한 (200자) |
| 자동 요약 LLM 호출로 응답 지연 | 비동기 요약 (답변 완료 후 백그라운드 처리) |
| 세션 데이터 누적으로 DB 부하 | 90일 초과 세션 자동 정리 (향후 배치) |
