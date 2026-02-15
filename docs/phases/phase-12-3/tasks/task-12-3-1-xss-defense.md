# Task 12-3-1: [FE] innerHTML XSS 방어

**우선순위**: 12-3 내 5순위
**예상 작업량**: 소 (layout-component.js 2파일 수정)
**의존성**: 없음
**상태**: ✅ 완료

**기반 문서**: `phase-12-3-todo-list.md`
**Plan**: `phase-12-3-plan.md`
**작업 순서**: `phase-12-navigation.md`

---

## 1. 개요

### 1.1 목표

layout-component.js의 innerHTML 사용처에 XSS 방어 패턴을 적용한다. HTMLElement/DocumentFragment 타입 체크를 통해 안전한 DOM 조작을 보장하고, 개발자 의도를 `@trusted` 주석으로 명시한다.

---

## 2. 파일 변경 계획

### 2.2 수정

| 파일 | 변경 내용 |
|------|----------|
| `web/public/js/components/layout-component.js` | replaceChildren, @trusted 주석, DocumentFragment 분기 |
| `web/src/js/layout-component.js` | 동일 변경 (소스 동기화) |

---

## 3. 작업 체크리스트

- [x] `escapeHtml()` 유틸 함수 존재 확인 (utils.js)
- [x] layout-component.js createContainer(): DocumentFragment/HTMLElement 타입 체크 추가
- [x] layout-component.js renderContainer(): replaceChildren() 패턴 적용
- [x] innerHTML 사용처에 `@trusted` 주석 마킹
- [x] web/src/js/ 버전과 web/public/js/ 버전 동기화

---

## 4. 참조

- Phase 12 Master Plan §12-3-1
- FRONTEND.md Charter: "innerHTML 사용 시 반드시 esc() 이스케이프 적용"
