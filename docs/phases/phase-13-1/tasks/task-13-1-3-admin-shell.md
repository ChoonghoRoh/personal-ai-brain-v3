# Task 13-1-3: [FE] Admin 공통 shell 검증·불일치 시 통일

**우선순위**: 13-1 내 3순위 (13-1-1과 병렬 가능)
**예상 작업량**: 소 (0.5일)
**의존성**: 없음 (독립)
**상태**: TODO

**기반 문서**: `phase-13-1-todo-list.md`
**Plan**: `phase-13-1-plan.md`

---

## 1. 개요

### 1.1 목표

Admin 지식 6페이지와 설정 5페이지에서 공통 shell(header-placeholder, admin-common.js, admin-styles.css)이 동일하게 적용되는지 검증하고, 불일치가 있으면 통일한다.

### 1.2 검증 대상 (11페이지)

**Admin 지식 (6)**:
groups, labels, chunk-create, approval, chunk-labels, statistics

**Admin 설정 (5)**:
templates, presets, rag-profiles, policy-sets, audit-logs

---

## 2. 작업 체크리스트

- [ ] 11개 Admin 페이지 HTML 구조 비교
- [ ] header-placeholder 존재 여부 전수 확인
- [ ] admin-common.js 로드 여부 확인
- [ ] admin-styles.css 로드 여부 확인
- [ ] 불일치 발견 시 통일 패치 적용
- [ ] 검증 체크리스트 문서화

---

## 3. 참조

- Phase 13 Master Plan §13-1-3
- Phase 11-3 Plan (Admin UI 통합)
