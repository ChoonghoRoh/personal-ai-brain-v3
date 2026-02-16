# Task 15-2-3: LNB 메뉴 + HTML 라우트 추가

**우선순위**: 15-2 내 1순위 (병렬)
**의존성**: 없음
**담당 팀원**: frontend-dev
**상태**: 대기

---

## §1. 개요

LNB 메뉴에 "AI 자동화" 항목을 추가하고, HTML 라우트를 등록한다.

## §2. 파일 변경 계획

| 파일 | 유형 | 변경 내용 |
|------|------|----------|
| `web/public/js/components/header-component.js` | 수정 | ADMIN_MENU에 AI 자동화 항목 추가 |
| `backend/main.py` | 수정 | _HTML_ROUTES에 ai-automation 라우트 추가 |

## §3. 작업 체크리스트 (Done Definition)

- [ ] ADMIN_MENU에 `{ path: '/admin/ai-automation', label: 'AI 자동화', icon: '🤖' }` 추가
  - 파일관리 뒤, 통계 앞 위치
- [ ] _HTML_ROUTES에 `("/admin/ai-automation", "admin/ai-automation.html", "AI 자동화")` 추가
- [ ] 기존 메뉴 순서·구조 유지

## §4. 참조

- `web/public/js/components/header-component.js` — ADMIN_MENU 배열
- `backend/main.py` — _HTML_ROUTES 배열
