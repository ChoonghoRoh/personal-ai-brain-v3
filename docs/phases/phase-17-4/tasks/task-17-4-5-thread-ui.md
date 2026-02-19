# Task 17-4-5: [FE] 대화 스레드 UI + "이어서 질문하기" 버튼

**우선순위**: 17-4 내 5순위 (BE 완료 후)
**예상 작업량**: 큰
**의존성**: 17-4-1, 17-4-2 (BE API)
**담당 팀원**: frontend-dev
**상태**: 대기

---

## §1. 개요

현재 세션의 이전 대화 턴을 표시하는 스레드 패널을 추가한다. "이어서 질문하기" 버튼으로 같은 세션에서 연속 질의가 가능하고, "새 대화 시작" 버튼으로 새 세션을 시작한다.

## §2. 파일 변경 계획

| 구분 | 파일 | 변경 내용 |
|------|------|----------|
| 수정 | `web/src/pages/reason.html` | 대화 스레드 패널 HTML |
| 수정 | `web/public/js/reason/reason-control.js` | session_id 관리 + API 호출 |
| 수정 | `web/public/js/reason/reason.js` | 세션 초기화 + 이벤트 핸들러 |

## §3. 작업 체크리스트 (Done Definition)

- [ ] localStorage에 currentSessionId 저장/복원
- [ ] 대화 스레드 패널: 현재 세션의 이전 턴 카드 (질문 요약 + 시간)
- [ ] prepareReasoningRequest()에 session_id 포함
- [ ] "이어서 질문하기" 버튼 (결과 영역 하단)
- [ ] "새 대화 시작" 버튼 (새 session_id 생성 + UI 초기화)
- [ ] 턴 클릭 시 해당 결과 표시

## §4. 참조

- reason-control.js: prepareReasoningRequest() 함수
- reason.js: DOMContentLoaded 초기화
