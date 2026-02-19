# Task 17-4-6: [FE] 대화 기록 그리드 + 페이지네이션 + 선택 삭제

**우선순위**: 17-4 내 6순위 (BE 완료 후)
**예상 작업량**: 중간
**의존성**: 17-4-4 (페이지네이션/삭제 API)
**담당 팀원**: frontend-dev
**상태**: 대기

---

## §1. 개요

모든 대화 세션을 그리드 카드뷰로 표시하는 "대화 기록" 영역을 추가한다. 페이지네이션과 다중 선택 삭제를 지원한다.

## §2. 파일 변경 계획

| 구분 | 파일 | 변경 내용 |
|------|------|----------|
| 수정 | `web/src/pages/reason.html` | 대화 기록 탭/영역 HTML |
| 수정 | `web/public/js/reason/reason-render.js` | 세션 목록 렌더링 + 페이지네이션 |
| 수정 | `web/public/js/reason/reason.js` | 기록 탭 이벤트 핸들러 |

## §3. 작업 체크리스트 (Done Definition)

- [ ] "대화 기록" 탭 또는 토글 영역 추가
- [ ] 세션 카드: 제목, 턴 수, 최근 질문, 생성일
- [ ] 페이지네이션 컨트롤 (이전/다음 + 페이지 번호)
- [ ] 체크박스 다중 선택 + "선택 삭제" 버튼
- [ ] 세션 클릭 → loadSession(session_id) → 해당 대화 로드
- [ ] 삭제 확인 모달 (confirm)

## §4. 참조

- API: GET /api/reason/sessions (page/size), DELETE /api/reason/sessions/bulk
