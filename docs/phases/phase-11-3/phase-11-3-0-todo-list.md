# Phase 11-3: Admin UI — Todo List

**상태**: ✅ 완료
**우선순위**: Phase 11 내 3순위
**예상 작업량**: 9일
**시작일**: 2026-02-06
**완료일**: 2026-02-06

**기준 문서**: [phase-11-master-plan.md](../phase-11-master-plan.md)
**Plan**: [phase-11-3-0-plan.md](phase-11-3-0-plan.md)

---

## Phase 진행 정보

### 현재 Phase

- **Phase ID**: 11-3
- **Phase 명**: Admin UI
- **핵심 목표**: Admin 레이아웃·설정 편집·정책 대시보드·Audit Log 뷰어·API 연동 (기존 지식 Admin과 통합)

### 이전 Phase

- **Prev Phase ID**: 11-2
- **Prev Phase 명**: Admin 설정 Backend API
- **전환 조건**: 11-2 전체 Task 완료

### 다음 Phase

- **Next Phase ID**: 11-4
- **Next Phase 명**: 통합 테스트·운영 준비
- **전환 조건**: 11-3 전체 Task 완료

### Phase 11 내 우선순위

| 순위  | Phase ID | Phase 명               | 상태    |
| ----- | -------- | ---------------------- | ------- |
| 1     | 11-1     | DB 스키마·마이그레이션 | ✅ 완료 |
| 2     | 11-2     | Admin 설정 Backend API | ✅ 완료 |
| **3** | **11-3** | **Admin UI**           | ✅ 완료 |
| 4     | 11-4     | 통합 테스트·운영 준비  | ⏳ 대기 |

---

## Task 목록 (세부 단계 포함)

### 11-3-1: Admin 레이아웃·네비게이션·라우팅 ✅

**우선순위**: 11-3 내 1순위
**예상 작업량**: 2일
**의존성**: 11-2 완료
**상태**: ✅ 완료

#### 11-3-1a: 현황 감사

- [x] 현재 Admin 페이지 목록 정리 (labels, groups, approval, chunk-labels, chunk-create, statistics)
- [x] `backend/main.py` 내 Admin 관련 라우트 목록 정리
- [x] `header-component.js`의 ADMIN_MENU·USER_MENU 구조 확인
- [x] admin-common.js·admin-styles.css 사용처 정리
- [x] 현황 정리 문서화(plan 본문 또는 별도 MD)

#### 11-3-1b: 레이아웃 설계

- [x] 지식 관리 vs 설정 관리 메뉴 구분 방식 결정 (SETTINGS_MENU 별도 그룹)
- [x] 설정 관리 하위 메뉴 정의: templates, presets, RAG, policy, audit-logs
- [x] URL 규칙 결정: `/admin/settings/*`
- [x] 설계 요약 문서화

#### 11-3-1c: 공통 Admin shell·헤더 확장

- [x] `header-component.js`에 설정 관리 메뉴 그룹 추가 (SETTINGS_MENU + CSS)
- [x] Admin 전용 레이아웃 도입 (settings-common.css)
- [x] 기존 6개 Admin 페이지가 새 네비와 호환되는지 확인
- [x] 수정된 header-component.js 반영

#### 11-3-1d: Backend 라우팅 추가

- [x] `main.py`에 설정 관리 페이지 라우트 추가 (templates, presets, rag-profiles, policy-sets, audit-logs)
- [x] `web/src/pages/admin/settings/` 폴더 구조 결정
- [x] 각 라우트에 대응하는 HTML·템플릿 경로 연결

#### 11-3-1e: 설정 관리 진입점·네비 검증

- [x] 대시보드 또는 Admin 메뉴에서 설정 관리 진입 가능 확인
- [x] 통계 메뉴 노출 위치 통일(선택)
- [x] 동작 확인·문서화

---

### 11-3-2: 템플릿·프리셋·RAG 프로필 편집 화면 ✅

**우선순위**: 11-3 내 2순위
**예상 작업량**: 3.5일
**의존성**: 11-3-1 완료
**상태**: ✅ 완료

#### 11-3-2a: 템플릿 목록·상세·편집

- [x] 템플릿 목록 화면 (테이블/카드, status 필터)
- [x] 템플릿 상세 뷰
- [x] 템플릿 편집 폼 (name, template_type, content, output_format, citation_rule 등)
- [x] Draft 저장·Publish 버튼 UI
- [x] HTML/JS/CSS 작성 (`templates.html`, `templates.js`)

#### 11-3-2b: 프리셋 목록·상세·편집

- [x] 프리셋 목록 화면 (task_type 필터)
- [x] 프리셋 상세 뷰
- [x] 프리셋 편집 폼 (system_prompt, model_name, temperature, top_p, max_tokens, constraints 등)
- [x] HTML/JS/CSS 작성 (`presets.html`, `presets.js`)

#### 11-3-2c: RAG 프로필 목록·상세·편집

- [x] RAG 프로필 목록 화면
- [x] RAG 프로필 상세 뷰
- [x] RAG 프로필 편집 폼 (chunk_size, chunk_overlap, top_k, score_threshold, use_rerank 등)
- [x] HTML/JS/CSS 작성 (`rag-profiles.html`, `rag-profiles.js`)

#### 11-3-2d: 공통 폼·유효성·에러 표시

- [x] 입력 유효성·필수 필드 처리
- [x] API 에러 메시지 표시(showError 등 재사용)
- [x] 로딩 상태 표시(선택)
- [x] settings-common.js·settings-common.css 작성

---

### 11-3-3: 정책 대시보드·Audit Log 뷰어 ✅

**우선순위**: 11-3 내 3순위
**예상 작업량**: 2일
**의존성**: 11-3-1 완료
**상태**: ✅ 완료

#### 11-3-3a: 정책 대시보드

- [x] 정책 세트 목록 화면
- [x] 활성/비활성·우선순위 표시
- [x] 프로젝트/도메인별 정책 매핑 (Template/Preset/RAG Profile 드롭다운)
- [x] 새 정책 추가·편집 (같은 페이지에서 편집)
- [x] HTML/JS/CSS 작성 (`policy-sets.html`, `policy-sets.js`)

#### 11-3-3b: Audit Log 뷰어

- [x] 필터: 엔티티 타입, 액션, 날짜 범위
- [x] 테이블: 시간, 변경자, 액션, 테이블, 레코드
- [x] 상세 모달: old/new 값 JSON 표시
- [x] HTML/JS/CSS 작성 (`audit-logs.html`, `audit-logs.js`)
- [x] Backend API: `audit_log_crud.py` 엔드포인트 구현

---

### 11-3-4: API 연동·권한·에러 처리 ✅

**우선순위**: 11-3 내 4순위
**예상 작업량**: 1.5일
**의존성**: 11-3-2·11-3-3 연동 대상
**상태**: ✅ 완료

#### 11-3-4a: 설정 API 클라이언트·연동

- [x] 11-2 엔드포인트 호출 래퍼 (`adminApiCall`) 구현 (`settings-common.js`)
- [x] 템플릿·프리셋·RAG·정책·Audit Log 각 화면에서 CRUD 호출 연결
- [x] JS 모듈 정리 (`settings-common.js`, 개별 페이지 JS 파일)

#### 11-3-4b: 권한 체크

- [x] 설정 관리 메뉴/페이지 접근 시 API 에러 메시지 처리
- [x] 개발 환경 예외 정책 유지 (AUTH_ENABLED=false)
- [x] Backend 경로 조정 완료

#### 11-3-4c: 공통 에러·로딩 처리

- [x] API 실패 시 showError 등 기존 UX 유지
- [x] 로딩 중 표시 ("Loading..." 상태)
- [x] settings-common.js에 공통 유틸 반영

#### 11-3-4d: 기존 Admin과 통합 검증

- [x] 지식 관리(라벨·그룹·청크·승인·통계) - header-component.js 호환성 유지
- [x] 설정 관리 ↔ 지식 관리 메뉴 전환·헤더 일관성 확인 (SETTINGS_MENU 별도 그룹)
- [x] Docker 재시작 후 최종 동작 확인 완료 (2026-02-07)
