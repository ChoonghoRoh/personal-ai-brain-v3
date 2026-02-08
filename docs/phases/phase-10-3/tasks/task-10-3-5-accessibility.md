# Task 10-3-5: 접근성 (WCAG 2.1 AA)

**우선순위**: 10-3 내 5순위  
**예상 작업량**: 1일  
**의존성**: 10-3-1 완료 후 병렬 가능  
**상태**: ✅ 완료

**기반 문서**: [phase-10-3-0-todo-list.md](../phase-10-3-0-todo-list.md)  
**작업 순서**: [phase-10-navigation.md](../../phase-10-navigation.md)

---

## 1. 개요

### 1.1 목표

Reasoning 페이지 및 결과 영역이 **WCAG 2.1 AA** 수준의 접근성을 갖도록 키보드 조작, 포커스, aria/role 등을 점검·적용한다.

### 1.2 대상

| 항목        | 내용                                                 |
| ----------- | ---------------------------------------------------- |
| 키보드 조작 | 모든 기능 키보드로 접근 가능                         |
| 포커스 표시 | 포커스 링·가시성                                     |
| aria/role   | 탭·필터·버튼 등에 aria-selected, role, aria-label 등 |

---

## 2. 파일 변경 계획

### 2.1 수정

| 파일 경로                 | 용도                             |
| ------------------------- | -------------------------------- |
| Reasoning 페이지·컴포넌트 | aria, role, tabindex 등 추가     |
| CSS                       | 포커스 스타일 (focus-visible 등) |

---

## 3. 작업 체크리스트

### 3.1 점검

- [ ] 키보드 조작 가능 여부 점검 (탭 순서, Enter/Space 동작)
- [ ] 포커스 표시 가시성 점검
- [ ] 탭·필터·버튼 등에 aria-selected, role 등 적용

### 3.2 충족

- [ ] WCAG 2.1 AA 수준 목표 항목 충족 (또는 체크리스트 작성·진행)
- [ ] 스크린 리더·축소 확대 등 기본 시나리오 검증

---

## 4. 참고 문서

- [Phase 10-3 Plan](../phase-10-3-0-plan.md)
- [Phase 10-3 Todo List](../phase-10-3-0-todo-list.md)
- [Phase 10 Master Plan](../../phase-10-master-plan.md) §6.1 — 접근성 WCAG 2.1 AA
- WCAG 2.1: https://www.w3.org/WAI/WCAG21/quickref/
