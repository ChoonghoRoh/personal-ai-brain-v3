# Task 11-3-3: 정책 대시보드·Audit Log 뷰어

**우선순위**: 11-3 내 3순위  
**예상 작업량**: 2일  
**의존성**: 11-3-1 완료  
**상태**: ⏳ 대기

**기반 문서**: [phase-11-3-0-todo-list.md](../phase-11-3-0-todo-list.md)  
**Plan**: [phase-11-3-0-plan.md](../phase-11-3-0-plan.md)  
**작업 순서**: [phase-11-navigation.md](../../phase-11-navigation.md)

---

## 1. 개요

### 1.1 목표

**정책 대시보드**(정책 세트 목록·활성/비활성·우선순위·프로젝트/도메인 매핑·새 정책 추가·편집)와 **Audit Log 뷰어**(필터·테이블·상세 모달)를 구현한다. API 연동은 11-3-4에서 통합한다.

---

## 2. 파일 변경 계획

### 2.1 신규 생성

| 파일 경로 | 용도 |
|-----------|------|
| `web/src/pages/admin/` (또는 settings/) | 정책 대시보드·Audit Log 뷰어 HTML |
| `web/public/js/admin/` | 해당 페이지용 JS |
| `web/public/css/admin/` | 해당 페이지용 CSS |

### 2.2 수정

| 파일 경로 | 용도 |
|-----------|------|
| (없음) | 필요 시 admin-common 확장 |

---

## 3. 작업 체크리스트 (Done Definition)

### 3.1 11-3-3a: 정책 대시보드

- [ ] 정책 세트 목록 화면
- [ ] 활성/비활성·우선순위 표시(또는 드래그)
- [ ] 프로젝트/도메인별 정책 매핑 테이블
- [ ] 새 정책 추가·편집(모달 또는 별도 페이지)
- [ ] HTML/JS/CSS 작성

### 3.2 11-3-3b: Audit Log 뷰어

- [ ] 필터: 엔티티 타입, 액션, 날짜 범위
- [ ] 테이블: 시간, 변경자, 액션, 테이블, 레코드
- [ ] 상세 모달: old/new 값 diff 또는 JSON
- [ ] HTML/JS/CSS 작성

---

## 4. 참조

- [phase-11-3-0-plan.md](../phase-11-3-0-plan.md) §5.3
- [phase-11-master-plan-sample.md](../../phase-11-master-plan-sample.md) — Policy Set Dashboard·Audit Log Viewer 참고
