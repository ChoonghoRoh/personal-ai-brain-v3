# Task 13-2-1: [BE] HTML 라우트 목록 문서화·메뉴 path 1:1 대응 검증

**우선순위**: 13-2 내 1순위 (최우선)
**예상 작업량**: 소 (0.5일)
**의존성**: 없음
**상태**: TODO

**기반 문서**: `phase-13-2-todo-list.md`
**Plan**: `phase-13-2-plan.md`

---

## 1. 개요

### 1.1 목표

main.py에 정의된 HTML 라우트와 header-component의 메뉴 path 17개를 1:1 대응 표로 문서화하고, 누락된 라우트가 있으면 추가한다.

### 1.2 관련 시나리오

- 공통 시나리오 S-03: path와 라우트 1:1 대응
- 공통 시나리오 S-04: Base URL 일치

---

## 2. 산출물

| 파일 | 내용 |
|------|------|
| `docs/phases/phase-13-2/route-menu-mapping.md` | 라우트↔메뉴 대응 표 |
| `backend/main.py` (필요 시) | 누락 라우트 추가 |

---

## 3. 작업 체크리스트

- [ ] main.py HTML 라우트 전수 추출
- [ ] 메뉴 path 17개 대응 표 작성
- [ ] 누락 라우트 발견 시 추가
- [ ] curl 검증: 17개 path 200 OK
- [ ] Base URL(8001) 일치 확인

---

## 4. 참조

- Phase 13 Master Plan §B-1, B-3, B-4
