# Task 11-3-1: Admin 레이아웃·네비게이션·라우팅

**우선순위**: 11-3 내 1순위  
**예상 작업량**: 2일  
**의존성**: 11-2 완료  
**상태**: ⏳ 대기

**기반 문서**: [phase-11-3-0-todo-list.md](../phase-11-3-0-todo-list.md)  
**Plan**: [phase-11-3-0-plan.md](../phase-11-3-0-plan.md)  
**작업 순서**: [phase-11-navigation.md](../../phase-11-navigation.md)

---

## 1. 개요

### 1.1 목표

현재 Admin 페이지·라우팅·헤더/네비를 **현황 감사**한 뒤, **지식 관리 vs 설정 관리** 구분을 반영한 레이아웃 설계·공통 Admin shell/헤더 확장·Backend 설정 관리 페이지 라우트 추가를 수행하고, 설정 관리 진입점·네비를 검증한다.

---

## 2. 파일 변경 계획

### 2.1 신규 생성

| 파일 경로 | 용도 |
|-----------|------|
| `web/src/pages/admin/settings/` (또는 admin 하위) | 설정 관리 HTML·템플릿 (templates, presets, rag-profiles, policy, audit-logs) |
| 현황·설계 요약 MD (선택) | plan 본문 또는 별도 문서 |

### 2.2 수정

| 파일 경로 | 용도 |
|-----------|------|
| `web/public/js/components/header-component.js` | 설정 관리 메뉴 그룹 추가 |
| `backend/main.py` | 설정 관리 페이지 라우트 추가 |

---

## 3. 작업 체크리스트 (Done Definition)

### 3.1 11-3-1a: 현황 감사

- [ ] 현재 Admin 페이지 목록 정리 (labels, groups, approval, chunk-labels, chunk-create, statistics)
- [ ] `backend/main.py` 내 Admin 관련 라우트 목록 정리
- [ ] `header-component.js`의 ADMIN_MENU·USER_MENU 구조 확인
- [ ] admin-common.js·admin-styles.css 사용처 정리
- [ ] 현황 정리 문서화(plan 본문 또는 별도 MD)

### 3.2 11-3-1b: 레이아웃 설계

- [ ] 지식 관리 vs 설정 관리 메뉴 구분 방식 결정
- [ ] 설정 관리 하위 메뉴 정의: templates, presets, RAG, policy, audit-logs
- [ ] URL 규칙 결정: `/admin/settings/*` vs `/admin/templates` 등
- [ ] 설계 요약 문서화

### 3.3 11-3-1c: 공통 Admin shell·헤더 확장

- [ ] `header-component.js`에 설정 관리 메뉴 그룹 추가
- [ ] 필요 시 Admin 전용 레이아웃(사이드바/탭) 도입
- [ ] 기존 6개 Admin 페이지가 새 네비와 호환되는지 확인
- [ ] 수정된 header-component.js 반영

### 3.4 11-3-1d: Backend 라우팅 추가

- [ ] `main.py`에 설정 관리 페이지 라우트 추가 (templates, presets, rag-profiles, policy, audit-logs)
- [ ] `web/src/pages/admin/` 하위 구조 결정 (settings/ 폴더 또는 기존 admin/ 하위 파일명)
- [ ] 각 라우트에 대응하는 HTML·템플릿 경로 연결

### 3.5 11-3-1e: 설정 관리 진입점·네비 검증

- [ ] 대시보드 또는 Admin 메뉴에서 설정 관리 진입 가능 확인
- [ ] 통계 메뉴 노출 위치 통일(선택)
- [ ] 동작 확인·문서화

---

## 4. 참조

- [phase-11-3-0-plan.md](../phase-11-3-0-plan.md) §2·§5.1 — 현재 개발 상태·Task 11-3-1 상세 단계
- `backend/main.py`, `web/public/js/components/header-component.js` — 현재 Admin 라우팅·헤더
