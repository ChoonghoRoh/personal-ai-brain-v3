# Phase 11-3-0 Plan — Admin UI

**Phase ID**: 11-3  
**Phase 명**: Admin UI  
**Z**: 0 (초기 설계)  
**기준 문서**: [phase-11-master-plan.md](../phase-11-master-plan.md)  
**명명 규칙**: [ai-rule-phase-naming.md](../../ai/ai-rule-phase-naming.md)

---

## 1. Phase Goal

Phase 11-2에서 구축한 Admin **설정** API를 활용하여 **Admin 레이아웃·설정 편집 화면(템플릿·프리셋·RAG 프로필)·정책 대시보드·Audit Log 뷰어**를 구현하고, API 연동·권한·에러 처리를 완료한다.  
**기존 Admin(지식 관리: 라벨·그룹·청크·승인·통계)** 과 공존하며, **설정 관리** 영역을 추가·통합한다.

---

## 2. 현재 개발 상태 및 리팩토링 포인트

### 2.1 Backend

| 항목 | 현재 상태 | Phase 11-3 시 고려 사항 |
|------|-----------|--------------------------|
| **Admin 페이지 라우팅** | `main.py`에 `/admin/labels`, `/admin/groups`, `/admin/approval`, `/admin/chunk-labels`, `/admin/chunk-create`, `/admin/statistics` 개별 등록 | **설정 관리** 페이지용 라우트 추가 필요: `/admin/settings/templates`, `/admin/settings/presets`, `/admin/settings/rag-profiles`, `/admin/settings/policy`, `/admin/settings/audit-logs` (또는 `/admin/templates` 등 단순 경로). 라우트 일괄 등록/패턴 정리 검토 |
| **설정 API** | 없음 (Phase 11-2에서 `backend/routers/admin/` 추가 예정) | 11-3는 11-2 API 소비만 수행. Backend 변경은 라우팅·정적 페이지 서빙 위주 |
| **인증** | `middleware/auth.py`에서 `/admin/` 경로가 개발 환경에서 인증 제외 | 설정 관리 메뉴/페이지에 대한 권한 정책 결정 후, 필요 시 경로별 제외/포함 조정 |

### 2.2 Web

| 항목 | 현재 상태 | Phase 11-3 시 리팩토링·추가 |
|------|-----------|-----------------------------|
| **Admin 페이지 구조** | `web/src/pages/admin/` 하위에 HTML 6종(labels, groups, approval, chunk-labels, chunk-create, statistics). 페이지별로 `container` → `header-placeholder` → 콘텐츠. 헤더/네비는 `header-component.js` + `admin-common.js`의 `initializeAdminPage()`로 주입 | **설정 관리** HTML 5종 추가(또는 SPA형 1페이지만 라우팅). 기존 패턴 유지 시 각 설정 페이지에서 동일하게 shell 사용 |
| **Admin 네비게이션** | `header-component.js`의 `ADMIN_MENU`: 키워드 관리, 라벨 관리, 청크 생성, 청크 승인, 청크 관리. **통계(statistics)는 ADMIN_MENU에 없음** — 대시보드 등 다른 경로로 진입 | **지식 관리** vs **설정 관리** 구분 필요. ADMIN_MENU를 두 그룹으로 나누거나, 설정 관리 하위 메뉴(templates, presets, RAG, policy, audit) 추가. 통계 메뉴 노출 여부 통일 |
| **공통 자산** | `admin-styles.css`, `admin-common.js`(showError, showSuccess, initializeAdminPage). 페이지별 CSS/JS 존재 | 설정 관리 페이지용 공통 CSS/JS 추가. 에러/성공 메시지·로딩 UI는 기존 admin-common 확장 또는 공통 컴포넌트로 정리 |
| **지식 Admin** | 라벨·그룹·청크·승인·통계 각각 별도 API 사용(labels, knowledge, approval 등) | 기존 동작 유지. 설정 관리만 11-2 API 사용. 헤더/네비 확장 시 기존 링크 유지 |

### 2.3 DB

| 항목 | 현재 상태 | Phase 11-3 시 고려 |
|------|-----------|---------------------|
| **설정 테이블** | 없음. Phase 11-1에서 schemas, templates, prompt_presets, rag_profiles, context_rules, policy_sets, audit_logs 추가 예정 | 11-3는 DB 직접 접근 없음. 11-2 API를 통해서만 조회·변경 |
| **기존 테이블** | labels, knowledge_chunks, documents 등. 지식 Admin이 사용 | 변경 없음. 회귀 방지만 확인 |

### 2.4 리팩토링 요약

- **레이아웃·네비**: Admin 메뉴를 **지식 관리**(기존) | **설정 관리**(신규)로 구분하고, 설정 하위에 템플릿·프리셋·RAG·정책·Audit Log 메뉴 추가. 필요 시 공통 Admin shell(사이드바 또는 탭) 도입.
- **라우팅**: Backend에 설정 관리용 페이지 라우트 추가; Web에서 해당 경로에 맞는 HTML/JS 구성.
- **공통 처리**: 설정 API 호출·에러·로딩·권한을 admin-common 또는 전용 JS 모듈로 일원화하여 기존 showError/showSuccess와 동일한 UX 유지.

---

## 3. Scope

### 3.1 In Scope

| Task ID | 항목 | 예상 |
|---------|------|------|
| 11-3-1 | Admin 레이아웃·네비게이션·라우팅(현황 감사·설계·리팩토링·설정 라우트 추가) | 2일 |
| 11-3-2 | 템플릿·프리셋·RAG 프로필 편집 화면(목록·상세·편집·공통 폼) | 3.5일 |
| 11-3-3 | 정책 대시보드·Audit Log 뷰어 | 2일 |
| 11-3-4 | API 연동·권한 체크·에러 처리 | 1.5일 |

### 3.2 Out of Scope

- 통합 테스트·운영 매뉴얼(Phase 11-4), Admin **설정** Backend API 구현(Phase 11-2).
- 멀티 테넌시·A/B 테스트(마스터 플랜 Out of Scope).
- Next.js/React 전환(현재 스택은 Vanilla JS + HTML + CSS 유지).

---

## 4. Task 개요

| Task ID | Task 명 | 예상 작업량 | 의존성 |
|---------|---------|-------------|--------|
| 11-3-1 | Admin 레이아웃·네비게이션·라우팅 | 2일 | 11-2 완료 |
| 11-3-2 | 템플릿·프리셋·RAG 프로필 편집 화면 | 3.5일 | 11-3-1 완료 |
| 11-3-3 | 정책 대시보드·Audit Log 뷰어 | 2일 | 11-3-1 완료 |
| 11-3-4 | API 연동·권한·에러 처리 | 1.5일 | 11-3-2·11-3-3 연동 대상 |

**진행 순서**: 11-3-1 완료 후 11-3-2·11-3-3 병렬 가능; 11-3-4는 두 Task 결과에 대한 연동·통합.

---

## 5. Task별 상세 단계

### 5.1 Task 11-3-1: Admin 레이아웃·네비게이션·라우팅

| 단계 | 내용 | 산출물 |
|------|------|--------|
| **11-3-1a** | **현황 감사** — 현재 Admin 페이지 목록, Backend 라우트(`main.py`), `ADMIN_MENU`·헤더 구조(`header-component.js`), 공통 JS/CSS 사용처 정리 | 현황 정리 MD(또는 plan 본문) |
| **11-3-1b** | **레이아웃 설계** — 지식 관리 vs 설정 관리 구분 방식, 설정 관리 하위 메뉴(templates, presets, RAG, policy, audit-logs), URL 규칙(`/admin/settings/*` vs `/admin/templates` 등) 결정 | 설계 요약 |
| **11-3-1c** | **공통 Admin shell/헤더 확장** — `header-component.js`에 설정 관리 메뉴 그룹 추가. 필요 시 Admin 전용 레이아웃(사이드바/탭) 컴포넌트 도입. 기존 6개 Admin 페이지가 새 네비와 호환되는지 확인 | 수정된 `header-component.js`(및 필요 시 공통 HTML/JS) |
| **11-3-1d** | **Backend 라우팅 추가** — 설정 관리용 페이지 라우트 등록(`main.py`): 템플릿·프리셋·RAG·정책·Audit Log. 템플릿 디렉터리 `web/src/pages/admin/settings/` 또는 기존 `admin/` 하위 파일명 규칙 결정 | `main.py` 라우트, `web/src/pages/admin/` 구조 |
| **11-3-1e** | **설정 관리 진입점·네비 검증** — 대시보드 또는 Admin 메뉴에서 설정 관리 진입 가능 여부 확인. 통계 메뉴 노출 위치 통일(선택) | 동작 확인·문서화 |

### 5.2 Task 11-3-2: 템플릿·프리셋·RAG 프로필 편집 화면

| 단계 | 내용 | 산출물 |
|------|------|--------|
| **11-3-2a** | **템플릿 목록·상세·편집** — 템플릿 목록(테이블/카드), status 필터, 상세 뷰, 편집 폼(name, template_type, content, output_format, citation_rule 등). Draft 저장·Publish 버튼(11-2 API 연동은 11-3-4에서 통합) | HTML/JS/CSS, `phase-11-3/` task 문서 |
| **11-3-2b** | **프리셋 목록·상세·편집** — 프리셋 목록, task_type 필터, 편집 폼(system_prompt, model_name, temperature, top_p, max_tokens, constraints 등) | HTML/JS/CSS |
| **11-3-2c** | **RAG 프로필 목록·상세·편집** — RAG 프로필 목록, 편집 폼(chunk_size, chunk_overlap, top_k, score_threshold, use_rerank 등) | HTML/JS/CSS |
| **11-3-2d** | **공통 폼·유효성·에러 표시** — 입력 유효성, 필수 필드, API 에러 메시지 표시(showError 등 재사용). 로딩 상태 표시(선택) | 공통 스크립트 또는 admin-common 확장 |

### 5.3 Task 11-3-3: 정책 대시보드·Audit Log 뷰어

| 단계 | 내용 | 산출물 |
|------|------|--------|
| **11-3-3a** | **정책 대시보드** — 정책 세트 목록, 활성/비활성, 우선순위 표시(또는 드래그). 프로젝트/도메인별 매핑 테이블. 새 정책 추가·편집(모달 또는 별도 페이지) | HTML/JS/CSS |
| **11-3-3b** | **Audit Log 뷰어** — 필터(엔티티 타입, 액션, 날짜 범위), 테이블(시간, 변경자, 액션, 테이블, 레코드). 상세 모달(old/new 값 diff 또는 JSON) | HTML/JS/CSS |

### 5.4 Task 11-3-4: API 연동·권한·에러 처리

| 단계 | 내용 | 산출물 |
|------|------|--------|
| **11-3-4a** | **설정 API 클라이언트·연동** — 11-2 엔드포인트 호출 래퍼(fetch 또는 공통 함수). 템플릿·프리셋·RAG·정책·Audit Log 각 화면에서 CRUD 호출 연결 | JS 모듈, 각 페이지 연동 |
| **11-3-4b** | **권한 체크** — 설정 관리 메뉴/페이지 접근 시 인증·역할 확인(또는 API 403 시 메시지 처리). 개발 환경 예외 정책 유지 | JS·필요 시 Backend 경로 조정 |
| **11-3-4c** | **공통 에러·로딩 처리** — API 실패 시 showError, 로딩 중 표시, 낙관적 업데이트 정책(선택). 기존 admin-common과 동일 UX | admin-common 또는 전용 모듈 |
| **11-3-4d** | **기존 Admin과 통합 검증** — 지식 관리(라벨·그룹·청크·승인·통계) 회귀 없음 확인. 설정 관리와 지식 관리 메뉴 전환·헤더 일관성 확인 | 체크리스트·문서화 |

---

## 6. Validation / Exit Criteria

- [ ] **11-3-1** Admin 레이아웃·라우팅·네비에 지식 관리/설정 관리 구분 반영, 설정 관리 페이지 라우트 동작
- [ ] **11-3-2** 템플릿·프리셋·RAG 프로필 목록·상세·편집 화면 구현(11-2 API와 연동 후 11-3-4에서 검증)
- [ ] **11-3-3** 정책 대시보드·Audit Log 뷰어 구현
- [ ] **11-3-4** 설정 API 연동·권한·에러 처리 완료, 기존 지식 Admin 회귀 없음
- [ ] Task 테스트 결과는 `docs/phases/phase-11-3/`에 저장.

---

## 7. 참고 문서

| 문서 | 용도 |
|------|------|
| [phase-11-master-plan.md](../phase-11-master-plan.md) | Phase 11 전체 계획 |
| [phase-11-3-0-todo-list.md](phase-11-3-0-todo-list.md) | 본 Phase 할 일 목록 |
| [phase-11-master-plan-sample.md](../phase-11-master-plan-sample.md) | Admin UI 구조·화면 설계 참고 |
| `backend/main.py` | 현재 Admin 페이지 라우팅 |
| `web/public/js/components/header-component.js` | ADMIN_MENU·헤더 구조 |
| `web/public/js/admin/admin-common.js` | showError, showSuccess, initializeAdminPage |
