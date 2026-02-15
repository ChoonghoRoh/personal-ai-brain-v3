# Task 13-2-2: [BE] (선택) HTML 404 전용 응답

**우선순위**: 13-2 내 2순위 (선택)
**예상 작업량**: 소 (0.5일)
**의존성**: Task 13-1-4 (FE 404 페이지)와 연동
**상태**: TODO (선택)

**기반 문서**: `phase-13-2-todo-list.md`
**Plan**: `phase-13-2-plan.md`

---

## 1. 개요

### 1.1 목표

미정의 경로 GET 요청 시, Accept 헤더가 text/html이면 404.html 전용 페이지를 반환하고, application/json이면 기존 JSON 404를 유지한다.

---

## 2. 작업 체크리스트

- [ ] FastAPI 예외 핸들러에서 Accept 헤더 판별 로직 구현
- [ ] HTML 요청 시 404.html 템플릿 반환
- [ ] API 요청 시 기존 JSON 404 유지
- [ ] /admin/unknown, /admin/settings/unknown, /dashbord 테스트

---

## 3. 참조

- Phase 13 Master Plan §B-2
- 라우팅·에러 시나리오 S-34~S-36
