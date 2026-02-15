# Task 13-1-4: [FE] (선택) 404 전용 HTML·활성 메뉴 접근성 보완

**우선순위**: 13-1 내 4순위 (선택)
**예상 작업량**: 소 (0.5일)
**의존성**: Task 13-2-2 (Backend HTML 404 응답)와 연동
**상태**: TODO (선택)

**기반 문서**: `phase-13-1-todo-list.md`
**Plan**: `phase-13-1-plan.md`

---

## 1. 개요

### 1.1 목표

404 전용 HTML 페이지를 생성하고, 활성 메뉴에 aria-current 등 접근성 속성을 보완한다.

---

## 2. 파일 변경 계획

| 파일 | 변경 내용 |
|------|----------|
| `web/src/pages/404.html` | 404 전용 페이지 신규 생성 |
| header-component 스크립트 | aria-current="page" 추가 |

---

## 3. 작업 체크리스트

- [ ] 404.html 페이지 생성 (메뉴 구조 포함·홈 링크)
- [ ] 활성 메뉴에 aria-current="page" 적용
- [ ] active/current CSS 클래스 일관성 확인
- [ ] 백엔드 404 HTML 응답 연동 확인 (13-2-2)

---

## 4. 참조

- Phase 13 Master Plan §13-1-4
- 라우팅·에러 시나리오 S-34~S-36
