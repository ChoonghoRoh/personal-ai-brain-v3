# Phase 14 Master Plan Guide — 통합 메뉴·권한·와이드/LNB·API 문서·사용자/회원관리

**작성일**: 2026-02-10  
**역할**: PM(Project Manager) 분석·가이드  
**기준 문서**: [260216-0955-프론트엔드백엔드통합메뉴설계분석보고서.md](../planning/260216-0955-프론트엔드백엔드통합메뉴설계분석보고서.md), [phase-13-qc-report.md](phase-13-qc-report.md), [phase-13-final-summary-report.md](phase-13-final-summary-report.md), [260210-1400-db-sample-data-and-high-level-strategy.md](../planning/260210-1400-db-sample-data-and-high-level-strategy.md)  
**선행 조건**: Phase 13 완료 (메뉴 검증·E2E 69개 98.5%·페이지 접근 로그·Local LLM 개선)

---

## 1. 목적 및 범위

본 가이드는 다음을 목표로 한다.

1. **통합 메뉴 설계 보고서**(260216)의 추가·보완 사항을 PM 관점에서 정리하고, 파트별 연결 관계를 명시한다.
2. **API Swagger 서비스 도입(고도화) 방안**을 정의한다.
3. **Phase 13 QC 리포트**에서 보완이 필요한 항목을 Phase 14에 반영한다.
4. **세부 Phase 14 Plan** 초안을 제시한다.
5. **UI 전체 레이아웃**(설정관리 기준 와이드 화면)·**좌측 LNB** 네비게이션을 Phase 14 범위에 포함한다.
6. **사용자 검증·로그인·회원관리** 추가 방안 플랜을 마련한다.

**개발 소스 수정은 하지 않으며**, 분석·리포트·계획 수준으로만 작성한다.

---

## 2. 통합 메뉴 설계 보고서 기반 PM 분석

### 2.1 보고서 요약과 Phase 13 대비 갭

| 보고서 권장 사항 | Phase 13 완료 상태 | 갭 (Phase 14 반영 여부) |
|-----------------|-------------------|--------------------------|
| CDN → 로컬 라이브러리 | ✅ Phase 12-1-1 완료 | 없음 |
| 권한 기반 메뉴 분리 (user / admin:knowledge / admin:system) | ❌ 미적용 | **Phase 14 핵심** |
| 메뉴 UI: 사이드바 전환 | ❌ 현재 상단 가로 메뉴 | Phase 14 또는 백로그 |
| 설정 메뉴 5개 HTML/JS 완성 | ✅ Phase 11-3·13에서 구현 | 검증 강화만 |
| Backend 권한 검증 강화 (require_admin_*) | ❌ 미적용 | **Phase 14 핵심** |
| On-Premise/로컬 서버 운영 가이드 | 부분 (docker-compose 등 존재) | 문서화 보강 |
| E2E·통합 테스트 | ✅ Phase 13-3 완료 | 유지·확장 |

### 2.2 파트별 연결 관계 (PM 관점)

```
[Frontend]                    [Backend]                     [DB/Infra]
─────────────────────────────────────────────────────────────────────
header-component.js     ←→   main.py (HTML 라우트)    ←→   route-menu-mapping
  ├ 권한별 메뉴 노출     ←→   auth middleware (역할 검증)  ←→   (향후) user/role 테이블
  ├ "지식 관리" 레이블   ←→   (문구만 FE)                  ←→   —
  └ 사이드바(선택)       ←→   동일 라우트                  ←→   —

설정 5페이지 (HTML/JS)   ←→   /api/admin/settings/*   ←→   templates, presets, rag_profiles,
  └ 각 페이지 fetch      ←→   Pydantic·에러 표준화     ←→   policy_sets, audit_logs

E2E (Playwright)        ←→   /health/ready, /docs     ←→   PostgreSQL, Qdrant, Redis
  └ 메뉴·404 시나리오    ←→   OpenAPI 스펙               ←→   —
```

**연결 정리**:
- **FE ↔ BE**: 메뉴 path 17개는 이미 1:1 라우트·문서화 완료(Phase 13-2-1). Phase 14에서 추가되는 것은 **권한에 따른 메뉴 노출**과 **BE 권한 검증**의 짝 맞추기다.
- **BE ↔ DB**: 설정 메뉴 API는 이미 Admin 모델(schemas, templates, prompt_presets, rag_profiles, policy_sets, audit_logs)과 연동됨. Phase 14에서는 **역할(role) 정보**가 필요 시 확장(예: user_role 컬럼 또는 정책 테이블).
- **E2E ↔ API**: Phase 13 최종 요약 기준 **69개 E2E**(68 Pass, 1 Partial)·98.5% 합격. Phase 14에서는 **권한별 시나리오**(비인증/일반/관리자/시스템관리자) 추가·기존 69개 회귀 확인. 필요 시 Reasoning 저장 모달 등 애니메이션 대기 보완(최종 요약 §4.1).

### 2.3 추가·보완 사항 (보고서 §3·§5 기반)

| # | 보완 항목 | 파트 | 상세 | 우선순위 |
|---|-----------|------|------|:--------:|
| 1 | 권한 기반 메뉴 표시 | FE | MENU_PERMISSIONS, userRole 기반 ADMIN/SETTINGS 메뉴 표시/숨김 | P0 |
| 2 | Backend 권한 검증 | BE | require_admin_knowledge, require_admin_system 의존성 적용 | P0 |
| 3 | "지식 관리" 그룹 레이블 | FE | header-component.js menu-group-title "관리자 메뉴" → "지식 관리" (Phase 13 QC 권장) | P1 |
| 4 | 전체 레이아웃 와이드화 | FE | 설정관리 페이지 기준 전체 화면 와이드 레이아웃 통일 | P1 |
| 5 | 좌측 LNB 네비게이션 | FE | 사용자/지식/설정 메뉴를 좌측 LNB로 이전·네비게이션 구조 정리 | P1 |
| 6 | 사이드바 레이아웃 | FE | 선택: layout-base.html, sidebar CSS (보고서 §3.2) — LNB와 통합 | P2 |
| 7 | 로컬 서버 운영 가이드 | DOC | docker-compose·Nginx·체크리스트 문서화 | P1 |
| 8 | API 문서 고도화 | BE | Swagger/OpenAPI 태그·설명·인증 연동 (아래 §4) | P1 |

### 2.4 Phase 14 실행 전 현황 검토 (Backend·API·DB·Frontend)

Plan 실행 전 각 레이어 현황을 정리하고, 추가 개선 포인트를 체크한다.

#### 2.4.1 Backend 현황

| 항목 | 현재 상태 | 갭·추가 개선 |
|------|-----------|--------------|
| **인증** | `middleware/auth.py`: `get_current_user`, `require_auth`, `UserInfo(username, auth_type)`. JWT payload `sub`만 사용. **role 없음**. | Phase 14: UserInfo에 `role` 추가 또는 JWT claim 확장. `require_admin_knowledge`, `require_admin_system` 미구현 → **신규 의존성 함수 추가** |
| **Admin 라우터** | `routers/admin/*`: 모든 엔드포인트 `Depends(get_db)` 만 사용. **require_auth/권한 검증 없음**. | 14-1-3: `/api/admin/*`(지식), `/api/admin/settings/*`(설정)에 권한 의존성 적용. `deps.py`에 `require_admin_*` 추가 |
| **인증 제외** | `AUTH_EXCLUDE_PREFIXES`에 `/admin/` 포함 → 개발 편의상 Admin HTML/API 인증 제외. | 프로덕션 시 `/admin/` 제외 제거 또는 역할 기반으로 API만 보호(HTML은 401 시 로그인 페이지 리다이렉트 정책 결정) |
| **라우터 수** | main.py에 라우터 30개 이상 등록. Admin은 `prefix=/api/admin`, 하위 tags 분산(admin-schemas 등). | Swagger 태그를 메뉴 구조(user/knowledge/settings)와 통일(§4). 권한 적용 시 라우터별 Depends 일괄 추가 |

#### 2.4.2 API 현황

| 항목 | 현재 상태 | 갭·추가 개선 |
|------|-----------|--------------|
| **인증 API** | `/api/auth/login`, `/api/auth/token`, `/api/auth/status`, `/api/auth/logout`. login은 "미구현" 반환, token은 API Key로 JWT 발급. | 14-5: 로그인 플로우 구현 여부 결정. 토큰 갱신(refresh) API 없음 → 플랜에 반영 |
| **Admin API** | `/api/admin/schemas`, `/templates`, `/presets`, `/rag-profiles`, `/policy-sets`, `/audit-logs`, `/page-access-logs`. CRUD 완비. **인증/역할 검증 없음**. | 14-1-3 적용 시 401/403 표준 응답. OpenAPI에 security 적용 경로 명시(14-2-2) |
| **OpenAPI** | main.py에 title, description, version, servers 설정. 라우터별 `tags=` 일부 사용. **securitySchemes 미설정**. | 14-2-1: tags 그룹화(사용자/지식/설정). 14-2-2: securitySchemes(JWT Bearer, X-API-Key) 및 경로별 security 명시 |
| **에러 응답** | admin CRUD: 404/409/422 deps에서 처리. 인증 401은 middleware. **403 Forbidden(권한 없음) 미사용**. | 역할 검증 실패 시 403 응답 및 `detail` 메시지 규격 정리 |

#### 2.4.3 DB 현황

| 항목 | 현재 상태 | 갭·추가 개선 |
|------|-----------|--------------|
| **사용자/역할** | **users 테이블 없음**. `admin_models.AdminSchema.role_key`는 스키마 정의용 키(display_order 등)로, **RBAC용 user role 아님**. | 14-5 플랜: user/role 테이블 설계 또는 JWT claim만으로 역할 부여(최소 스키마). Phase 14에서 **역할 소비처**(BE 의존성·FE 메뉴) 확정 후 저장소 결정 |
| **Admin 테이블** | schemas, templates, prompt_presets, rag_profiles, context_rules, policy_sets, audit_logs, page_access_logs. init_db()로 생성. | 권한 적용 시 audit_logs.changed_by 등과 사용자 식별자 연동 방안 검토. 회원관리 도입 시 users 테이블·마이그레이션 |
| **세션/토큰** | 세션 DB 없음. JWT stateless. | 토큰 블랙리스트(로그아웃) 필요 시 Redis 등 검토(14-5 플랜) |

#### 2.4.4 Frontend 현황

| 항목 | 현재 상태 | 갭·추가 개선 |
|------|-----------|--------------|
| **메뉴** | `header-component.js`: USER_MENU(6), ADMIN_MENU(6), SETTINGS_MENU(5). **전체 노출**, 권한 필터 없음. 그룹 타이틀 "사용자 메뉴", "**관리자 메뉴**", "설정 관리". | 14-1-1: MENU_PERMISSIONS·userRole 기반 표시/숨김. 14-1-2: "관리자 메뉴" → "지식 관리" 1곳 수정 |
| **레이아웃** | `layout-component.js`: container **max-width 1200px** 기본. `createContainer(options.maxWidth)` 지원. | 14-3-1: 설정관리와 동일한 **와이드** 기준(예: max-width none 또는 100%)으로 통일. 페이지별 CSS에 1200/1400 혼재( knowledge 1400, logs 1400, admin 일부 none) → **공통 레이아웃 한 곳에서 제어** |
| **설정 페이지** | admin/settings/*.html: settings-common.css, settings-layout, admin-container. **와이드 스타일** 적용됨. | 사용자·지식 페이지에 동일 레이아웃 적용. LNB 도입 시 header 내 메뉴를 LNB로 이전(14-3-2) |
| **인증 소비** | FE에서 `/api/auth/status` 호출·로그인 유도 패턴 **미확인**. 토큰 저장·헤더 첨부 등 클라이언트 플로우 정리 필요. | 14-5-1 플랜에 FE 인증 플로우(로그인 페이지, 401 시 리다이렉트, LNB에 로그아웃 노출) 포함 |

#### 2.4.5 추가 개선 체크리스트 (꼼꼼 점검)

| # | 영역 | 체크 항목 | Phase 14 반영 |
|---|------|-----------|---------------|
| 1 | BE | require_admin_knowledge, require_admin_system 의존성 정의 및 Admin 라우터 적용 | 14-1-3 |
| 2 | BE | UserInfo 또는 JWT claim에 role 추가, AUTH_ENABLED=false 시 테스트용 role 처리 | 14-1-1·14-1-3 |
| 3 | BE | 403 Forbidden 응답 규격(역할 부족) | 14-1-3 |
| 4 | API | OpenAPI securitySchemes·경로별 security 문서화 | 14-2-2 |
| 5 | API | 태그를 사용자/지식/설정 그룹으로 통일 | 14-2-1 |
| 6 | DB | 역할 저장소 결정(JWT vs user 테이블), 필요 시 마이그레이션 | 14-5-1 |
| 7 | FE | MENU_PERMISSIONS 상수·userRole 기반 메뉴 렌더링 | 14-1-1 |
| 8 | FE | "지식 관리" 그룹 레이블, 와이드 레이아웃 통일, LNB 도입 | 14-1-2, 14-3-1, 14-3-2 |
| 9 | FE | 공통 레이아웃 컴포넌트(또는 CSS 변수)로 max-width·구조 일원화 | 14-3-1 |
| 10 | E2E | 권한별 시나리오(비인증/일반/관리자) 추가 검토 | 14-1 이후 |

---

## 3. Phase 13 QC·최종 요약 반영

### 3.1 Phase 13 QC 리포트 보완 반영

[phase-13-qc-report.md](phase-13-qc-report.md) §8 권장 사항을 Phase 14에 반영한다.

| QC 항목 | Phase 13 상태 | Phase 14 반영 방안 |
|---------|----------------|-------------------|
| **13-1-2 그룹 레이블** | "관리자 메뉴" 사용, "지식 관리" 미적용 | Task 14-1-x: header-component.js에서 `menu-group-title` "관리자 메뉴" → "지식 관리" 1곳 수정 |
| **13-5-4 (선택) 구조화 출력** | format=json 미구현, SKIP | Phase 14에서 선택 Task로 유지. ollama_client에 `format` 파라미터 추가·지식 추출/요약 경로 JSON 출력 검토 |
| **13-4-1 (선택) 접근 로그** | Phase 13-4에서 **완료** (최종 요약 확인) | page_access_logs 테이블·미들웨어·조회 API 구현 완료. Phase 14 백로그: **접근 로그 분석 UI**(§3.2 참조) |

이외 Phase 13 성공 기준은 만족한 것으로 두고, **Phase 14 성공 기준**에 위 보완 항목을 선택 Task로 명시한다.

### 3.2 Phase 13 최종 요약(Final Summary) 반영

[phase-13-final-summary-report.md](phase-13-final-summary-report.md) 결과를 Phase 14에서 이어받는다.

| 항목 | Phase 13 최종 결과 | Phase 14 반영 |
|------|-------------------|---------------|
| **E2E** | 69개 시나리오 (68 Pass, 1 Partial). 13-1(12), 13-2(10), 13-3(36), 13-4(3), 13-5(8). **98.5% 합격 (PASSED)** | Phase 14에서 **69개 E2E 유지·회귀 확인**. 권한 적용 후 **권한별 시나리오**(비인증/일반/관리자) 추가. |
| **페이지 접근 로그(13-4)** | page_access_logs 테이블, PageAccessLogMiddleware, `/api/system/statistics/access-logs` E2E 검증 완료 | 유지. Phase 14 백로그: **접근 로그 분석 UI**(Admin 통계 페이지에 "가장 많이 방문한 메뉴 TOP 5" 등 시각화). |
| **LLM/Reasoning(13-5)** | True Streaming·TTFT 개선 확인. **1건 Partial**: 저장 모달 닫힘 감지 시 타임아웃(UI 애니메이션 vs 테스트 대기) | E2E 안정화 시 **모달/애니메이션 대기 보완** 권장: Playwright `waitForFunction` 타임아웃 조정 또는 모달 페이드 아웃 반영한 상태 체크. |

**Phase 14 백로그(최종 요약 §4 반영)**:
- **접근 로그 분석 UI**: 현재 로그는 DB·API로만 확인 가능. 향후 Admin 통계 페이지에 방문 TOP 5 등 차트 추가.
- **E2E 모달 대기**: Reasoning 의사결정 문서 저장 모달 닫힘 검증 시 타임아웃 방지(테스트 코드 또는 UI 대기 시간 조정).

---

## 4. API Swagger 서비스 도입(고도화) 방안

### 4.1 현재 상태

- **FastAPI 기본 제공**: `/docs` (Swagger UI), `/redoc` (ReDoc), `/openapi.json` (OpenAPI 3.0 스펙).
- **설정**: `main.py`에서 `title`, `description`, `version`, `servers`, `contact` 등 메타데이터 설정됨. EXTERNAL_PORT(8001) 반영(Phase 12-1-2).
- **인증**: Swagger UI "Authorize"로 Bearer/API Key 입력 가능. Phase 9-1 인증과 연동.

### 4.2 도입(고도화) 방안

| # | 항목 | 내용 | 비고 |
|---|------|------|------|
| 1 | **태그 그룹화** | 라우터별 `tags=["admin"]`, `tags=["search"]` 등으로 Swagger UI에서 그룹 표시. 메뉴 구조(사용자/지식/설정)와 맞춤 | BE |
| 2 | **엔드포인트 설명 보강** | `summary`, `description`, `response_description` 일관 작성. 404/422/500 응답 스키마 명시 | BE |
| 3 | **인증 스키마 명시** | OpenAPI `securitySchemes`에 JWT Bearer·API Key 명시. `security` 적용 경로 문서화 | BE |
| 4 | **버전 정보 노출** | `openapi_url` 또는 커스텀 `/api/openapi.json`에서 버전·빌드 정보 쿼리 파라미터 옵션 | BE |
| 5 | **CI에서 스펙 검증** | `openapi.json` 아티팩트 저장·스펙 변경 시 리뷰 또는 회귀 테스트 트리거 | CI |
| 6 | **문서 전용 경로 (선택)** | 프로덕션에서 `/docs` 비활성화 시 대체 URL(예: `/api/docs`) 또는 정적 OpenAPI HTML 제공 | INFRA |

**구현 범위 제안**: (1)~(3)을 Phase 14 Task로, (4)~(6)은 선택·백로그로 둔다.

### 4.3 Phase 14 Task 제안 (Swagger)

| Task ID | 내용 | 산출물 |
|---------|------|--------|
| 14-2-x | API 문서(Swagger) 태그 그룹화·엔드포인트 설명 보강 | 라우터 tags·summary/description 정리, OpenAPI securitySchemes 문서화 |
| (선택) | OpenAPI 스펙 CI 아티팩트 저장 | .github/workflows 또는 스크립트에서 openapi.json 저장 |

---

## 5. Phase 14 세부 Plan (초안)

### 5.1 Phase 14 목표 (1문장)

**통합 메뉴 설계 보고서의 권한 분리·UI 보완과 Phase 13 QC 보완 항목을 반영하고, 설정관리 기준 전체 와이드 레이아웃·좌측 LNB 네비게이션을 도입하며, API Swagger(OpenAPI) 문서를 고도화하고 사용자 검증·로그인·회원관리 추가 방안을 수립하여 권한 기반 메뉴·API 접근과 운영 가시성을 확보한다.**

### 5.2 Phase 14 구조 (가이드 초안)

```
Phase 14 (가이드 초안)

14-1   권한·메뉴 보완 (통합 메뉴 보고서 + QC 반영)
       ├── 14-1-0   [BE] 역할 스키마·의존성 설계 (role, require_admin_knowledge/system)
       ├── 14-1-1   [FE] 권한 기반 메뉴 표시 (MENU_PERMISSIONS, userRole) · [BE] Admin API 권한 적용
       ├── 14-1-2   [FE] "지식 관리" 그룹 레이블 적용 (Phase 13 QC)
       ├── 14-1-3   [BE] 403 응답·에러 메시지 규격
       └── 14-1-4   [DOC] (선택) 로컬 서버 운영 가이드

14-2   API 문서(Swagger) 고도화
       ├── 14-2-1   [BE] OpenAPI 태그 그룹화·엔드포인트 설명 보강
       ├── 14-2-2   [BE] OpenAPI securitySchemes·인증 경로 문서화
       └── 14-2-3   (선택) CI OpenAPI 스펙 아티팩트

14-3   UI 전체 레이아웃·좌측 LNB
       ├── 14-3-1   [FE] 설정관리 기준 전체 와이드 레이아웃 통일 (사용자·Admin·설정 공통)
       ├── 14-3-2   [FE] 좌측 LNB(Left Navigation Bar) 도입·네비게이션 이전 (사용자/지식 관리/설정 관리)
       └── 14-3-3   [FE] (선택) LNB 접기/펼치기·반응형(모바일 시 드로어)

14-4   (선택) UI·운영
       ├── 14-4-1   [FE] (선택) 사이드바·LNB 스타일 통일 (보고서 §3.2)
       ├── 14-4-2   [DOC] 배포 전 체크리스트 최종화 (보고서 §7 기반)
       └── (백로그) [FE] 접근 로그 분석 UI — Admin 통계 페이지에 방문 TOP 5 등 시각화 (Phase 13 최종 요약 §4.2)

14-5   사용자 검증·로그인·회원관리 (방안 플랜)
       ├── 14-5-1   [DOC] 사용자 검증·로그인·회원관리 요구사항 및 단계별 플랜 문서
       ├── 14-5-2   [BE] (플랜 후) 로그인/로그아웃·토큰 갱신 API 보강
       └── 14-5-3   [BE] (플랜 후) 회원(사용자) CRUD·목록·역할 관리 API 설계

14-6   DB 샘플 데이터·고도화·검증 (Phase 14 연동)
       ├── 14-6-1   [DOC] DB 샘플·고도화 전략 문서 확정·Phase 14 호환성 점검
       ├── 14-6-2   [BE/SCRIPT] 백업 후 시드 실행 (projects→labels→documents→chunks→cognitive→admin→audit/relations)
       ├── 14-6-3   [BE/SCRIPT] 1차 검증 (건수·FK·무결성·Qdrant 동기화)
       ├── 14-6-4   [BE/SCRIPT] (선택) Qdrant 임베딩 시드
       └── 14-6-5   [QA] 개발 완료 후 데이터 2차 검증 (재검증 스크립트·리포트·성공 기준)
```

### 5.3 의존성 및 순서

- **14-1-1(권한 메뉴)** 과 **14-1-3(권한 검증)** 은 짝으로 진행. BE 권한 스키마 확정 후 FE에서 role 소비.
- **14-1-2** "지식 관리" 레이블은 독립, 14-1-1 이전/이후 모두 가능.
- **14-2** Swagger 고도화는 14-1과 병렬 가능.
- **14-3** 레이아웃·LNB: 14-3-1(와이드 통일)을 먼저 적용한 뒤 14-3-2(LNB 도입). 기존 상단 header와 공존 또는 단계적 대체.
- **14-5** 사용자 검증·로그인·회원관리: 14-5-1 플랜 문서 선행 후 14-5-2·14-5-3 구현 여부 결정.
- **14-6** DB 샘플·검증: 14-6-1 문서 확정 후 14-6-2(시드)·14-6-3(1차 검증) 실행. **14-6-5(2차 검증)** 은 개발 완료(또는 시드·권한·API 변경 후) 시점에 재실행하여 데이터 정합성·품질 재확인.

### 5.4 성공 기준 (체크리스트 초안)

- [ ] **14-1-1** 비인증/일반 사용자에게 Admin·설정 메뉴 미노출(또는 역할에 따라 노출).
- [ ] **14-1-2** header-component "지식 관리" 그룹 레이블 적용.
- [ ] **14-1-3** /api/admin/* (지식), /api/admin/settings/* (설정) 경로에 권한 의존성 적용.
- [ ] **14-2-1** Swagger UI에서 태그별 그룹·엔드포인트 설명 확인.
- [ ] **14-2-2** OpenAPI 스펙에 securitySchemes·security 반영.
- [ ] **14-3-1** 사용자·Admin·설정 모든 페이지가 설정관리와 동일한 와이드 레이아웃 적용.
- [ ] **14-3-2** 좌측 LNB에 사용자 메뉴 6개·지식 관리 6개·설정 관리 5개 네비게이션 표시, 활성 메뉴 하이라이트.
- [ ] **14-5-1** 사용자 검증·로그인·회원관리 요구사항 및 단계별 플랜 문서 완성.
- [ ] **14-6** DB 샘플 시드·1차 검증 완료. **14-6-5** 개발 완료 후 데이터 2차 검증 완료(재검증 스크립트·리포트·성공 기준 충족).

### 5.5 UI 전체 레이아웃·좌측 LNB 상세

| 항목 | 내용 |
|------|------|
| **와이드 레이아웃 기준** | 설정관리 5페이지(템플릿·프리셋·RAG·정책·감사)와 동일한 전체 너비 레이아웃을 **사용자 메뉴 6페이지·지식 관리 6페이지**에 적용. 컨테이너 max-width 제거 또는 넓힘, 일관된 그리드/여백 적용. |
| **적용 범위** | 사용자: 대시보드·검색·채팅·문서·로그·도움말 / 지식: 소스·문서·추출·요약·LLM·정책 / 설정: 위 5개. **공통 레이아웃 템플릿**(예: layout-base.html 또는 layout-component) 한 곳에서 제어. |
| **좌측 LNB 역할** | 기존 상단 가로 메뉴(header-component)를 **좌측 세로 네비게이션**으로 이전 또는 병행. 그룹: "사용자", "지식 관리", "설정 관리". 권한에 따라 그룹·항목 표시/숨김(14-1-1과 연동). |
| **header vs LNB** | 상단 header는 로고·사용자 정보·로그아웃 등 유지; **주 메뉴 네비게이션은 LNB**로 이동. 모바일/좁은 화면에서는 LNB를 드로어(접기·오버레이)로 전환 검토(14-3-3). |

---

## 6. 사용자 검증·로그인·회원관리 추가 방안 (플랜)

Phase 14에서는 **구현 범위 확정 전** 요구사항 정리와 단계별 플랜 수립을 목표로 한다.

### 6.1 범위 정의

| 영역 | 포함 내용 | Phase 14에서 할 일 |
|------|-----------|---------------------|
| **사용자 검증** | 요청 단위 인증(토큰 검증)·역할(role) 기반 접근 제어 | 14-1-3 BE 권한 검증과 연동. 검증 실패 시 401/403·에러 메시지 표준화 |
| **로그인** | 로그인 폼·로그아웃·세션/토큰 갱신·비밀번호 정책 | 플랜 문서에 요구사항·플로우 정리. 구현은 14-5-1 문서 확정 후 14-5-2 |
| **회원관리** | 사용자 CRUD·목록·역할 할당·비활성화·감사 로그 | 플랜 문서에 Admin 전용 메뉴·API 스키마 초안. 구현은 14-5-3 또는 Phase 15 |

### 6.2 단계별 플랜 (안)

| 단계 | 내용 | 산출물 |
|------|------|--------|
| **1. 요구사항·플로우** | 로그인/로그아웃 시나리오, 역할 종류(예: user / admin:knowledge / admin:system), 회원 목록·편집 화면 요구사항 | 14-5-1 요구사항·플로우 문서 |
| **2. API·DB 스키마** | 로그인/로그아웃/토큰 갱신 API, 사용자 목록·상세·수정·역할 변경 API, user/role 테이블 확장안 | API 명세 초안·스키마 변경 제안 |
| **3. FE 연동** | 로그인 페이지·LNB에 사용자/로그아웃 노출, (선택) 회원관리 Admin 페이지 | 14-5-2·14-5-3 완료 후 또는 Phase 15 |
| **4. 보안·테스트** | 비밀번호 저장·토큰 만료·역할 검증 E2E 시나리오 | QA 체크리스트·E2E 시나리오 추가 |

### 6.3 전제 조건·리스크

- **기존 인증(Phase 9-1)** 과의 정합성: JWT·API Key 등 기존 방식 유지 여부 결정.
- **회원관리 메뉴 위치**: 설정 관리 하위 vs 별도 "시스템 관리" 그룹 — 통합 메뉴 보고서·LNB 구조와 맞춤.
- **On-Premise·단일 사용자**: 인증 비활성(AUTH_ENABLED=false) 또는 단일 계정 모드 유지 옵션 명시.

---

## 7. 리스크 및 전제 조건

| ID | 리스크 | 대응 |
|----|--------|------|
| R-01 | 권한 도입 시 기존 개발 환경(인증 비활성) 호환 | AUTH_ENABLED=false 시 메뉴 전부 노출 또는 테스트용 role 고정 |
| R-02 | 역할(role) 저장소 미정의 | JWT claim 또는 DB user 테이블 확장. Phase 14에서 최소 스키마 결정 |
| R-03 | Swagger 고도화 시 라우터 수정량 증가 | 태그·설명만 추가하는 범위로 제한, 대규모 리팩터 배제 |
| R-04 | 와이드·LNB 전환 시 기존 상단 메뉴 의존 페이지 이슈 | 공통 레이아웃 컴포넌트로 마이그레이션, E2E로 회귀 확인 |
| R-05 | 로그인·회원관리 도입 시 범위 확대 | 14-5-1 플랜으로 범위 고정, 구현은 Phase 14 내 선택 또는 Phase 15로 이관 |

**전제 조건**: Phase 13 완료, 통합 메뉴 설계 보고서(260216) 검토 완료.

---

## 8. 개발 테스크 세분화 및 고도화 전략

Phase 14 실행 전 현황(§2.4)을 반영하여 테스크를 세분화하고, 고도화 순서와 산출물을 명시한다.

### 8.1 고도화 전략 원칙

| 원칙 | 내용 |
|------|------|
| **BE 우선** | 권한 스키마(role)·의존성(require_admin_*) 확정 후 FE에서 role 소비. API 계약 변경 최소화. |
| **레이아웃 후 LNB** | 와이드 레이아웃 통일(14-3-1) 완료 후 LNB 도입(14-3-2). 기존 header와 공존·단계적 대체. |
| **문서·플랜 선행** | Swagger 고도화(14-2)는 14-1과 병렬 가능. 사용자·회원관리(14-5)는 14-5-1 플랜 문서 확정 후 구현. |
| **E2E 연동** | 권한·메뉴·레이아웃 변경 시 E2E 시나리오 추가·회귀 확인. |

### 8.2 Phase 14-1 권한·메뉴 — 테스크 세분화

| Task ID | 세부 내용 | 산출물 | 선행 |
|---------|-----------|--------|------|
| **14-1-0** | **[BE] 역할 스키마·의존성 설계** | role 값 정의(user/admin:knowledge/admin:system), require_admin_knowledge/system 구현, UserInfo 또는 JWT claim에 role 반영 | — |
| **14-1-1a** | **[BE] Admin API 권한 적용** | /api/admin/* (지식: groups, labels, chunk-create, approval, chunk-labels, statistics)에 require_admin_knowledge 적용 | 14-1-0 |
| **14-1-1b** | **[BE] Admin Settings API 권한 적용** | /api/admin/settings/* (schemas, templates, presets, rag-profiles, policy-sets, audit-logs, page-access-logs)에 require_admin_system 적용 | 14-1-0 |
| **14-1-1c** | **[FE] 권한 기반 메뉴 표시** | MENU_PERMISSIONS 상수, /api/auth/status 또는 토큰에서 userRole 획득, ADMIN_MENU·SETTINGS_MENU 표시/숨김 | 14-1-0 |
| **14-1-2** | **[FE] "지식 관리" 그룹 레이블** | header-component.js menu-group-title "관리자 메뉴" → "지식 관리" 1곳 수정 | — |
| **14-1-3** | **[BE] 403 응답·에러 메시지** | 권한 부족 시 403 Forbidden, detail 규격 정리 | 14-1-1a·14-1-1b |
| **14-1-4** | **[DOC] (선택) 로컬 서버 운영 가이드** | docker-compose·Nginx·체크리스트 문서화 | — |

### 8.3 Phase 14-2 API 문서(Swagger) — 테스크 세분화

| Task ID | 세부 내용 | 산출물 | 선행 |
|---------|-----------|--------|------|
| **14-2-1a** | **[BE] OpenAPI 태그 그룹화** | 라우터별 tags=["user"] / ["knowledge"] / ["settings"] 등 메뉴 구조와 맞춤 | — |
| **14-2-1b** | **[BE] 엔드포인트 설명 보강** | summary, description, response_description, 404/422/500 스키마 명시 | — |
| **14-2-2a** | **[BE] securitySchemes 정의** | OpenAPI에 JWT Bearer·X-API-Key 스키마 명시 | — |
| **14-2-2b** | **[BE] 경로별 security 적용** | 보호 경로에 security=[...] 적용·문서 반영 | 14-1-1a·14-1-1b |
| **14-2-3** | **(선택) CI OpenAPI 스펙** | openapi.json 아티팩트 저장·변경 시 리뷰 | — |

### 8.4 Phase 14-3 UI 레이아웃·LNB — 테스크 세분화

| Task ID | 세부 내용 | 산출물 | 선행 |
|---------|-----------|--------|------|
| **14-3-1a** | **[FE] 공통 레이아웃·와이드 기준 정의** | layout-component 또는 공통 CSS에서 container max-width 와이드(예: none/100%) 옵션, 설정 페이지와 동일 스타일 | — |
| **14-3-1b** | **[FE] 사용자 페이지 와이드 적용** | dashboard, search, ask, logs, knowledge, reason 6페이지 레이아웃 통일 | 14-3-1a |
| **14-3-1c** | **[FE] 지식(Admin) 페이지 와이드 적용** | admin/groups, labels, chunk-create, approval, chunk-labels, statistics 6페이지 레이아웃 통일 | 14-3-1a |
| **14-3-2a** | **[FE] LNB 컴포넌트 신규** | 좌측 세로 네비게이션 HTML/CSS/JS, 그룹(사용자/지식 관리/설정 관리), 활성 하이라이트, 권한별 노출(14-1-1c 연동) | 14-1-1c |
| **14-3-2b** | **[FE] LNB 적용·header 정리** | 공통 레이아웃에 LNB 삽입, header는 로고·사용자 정보·로그아웃만 유지, 기존 상단 메뉴 제거 또는 LNB로 이전 | 14-3-2a |
| **14-3-3** | **[FE] (선택) LNB 접기·반응형** | LNB 접기/펼치기, 모바일 시 드로어(오버레이) 전환 | 14-3-2b |

### 8.5 Phase 14-6 DB 샘플·고도화·검증 — 테스크 세분화

**상세 전략·백업·검증**: [260210-1400-db-sample-data-and-high-level-strategy.md](../planning/260210-1400-db-sample-data-and-high-level-strategy.md) 참조. 아래 Task는 해당 문서와 동기화한다.

| Task ID | 세부 내용 | 산출물 | 선행 |
|---------|-----------|--------|------|
| **14-6-1** | **[DOC] Phase 14 호환성 점검** | DB 샘플 전략 문서와 Phase 14(역할·audit_logs.changed_by·page_access_logs·users 테이블) 호환성 검토·보완 | — |
| **14-6-2a** | **[SCRIPT] 백업** | `backup_system.py backup --type full` 실행·검증 | — |
| **14-6-2b** | **[SCRIPT] .md 인벤토리** | docs/ 등 .md 목록·카테고리 분류 (분석만) | — |
| **14-6-2c** | **[SCRIPT] projects·labels 시드** | 5~10 projects, 100+ labels | 14-6-2a |
| **14-6-2d** | **[SCRIPT] documents 시드** | 100+ documents (.md 1:1) | 14-6-2c |
| **14-6-2e** | **[SCRIPT] knowledge_chunks·knowledge_labels** | 300+ chunks, 500+ knowledge_labels | 14-6-2d |
| **14-6-2f** | **[SCRIPT] memories·conversations·reasoning_results** | 각 100+ | 14-6-2e |
| **14-6-2g** | **[SCRIPT] Admin 설정 시드** | schemas, templates, prompt_presets, rag_profiles, context_rules, policy_sets (templates·presets 100+) | 14-6-2f |
| **14-6-2h** | **[SCRIPT] audit_logs·knowledge_relations** | 100+ audit_logs, 50~200 relations | 14-6-2g |
| **14-6-3** | **[SCRIPT] 1차 검증** | 건수·FK·무결성·Qdrant 동기화 (`validate_sample_data.py` 또는 `/api/integrity/*`) | 14-6-2h |
| **14-6-4** | **[SCRIPT] (선택) Qdrant 임베딩** | 300+ 청크 임베딩·upsert, qdrant_point_id 역저장 | 14-6-3 |
| **14-6-5** | **[QA] 개발 완료 후 데이터 2차 검증** | 시드·권한·API 변경 등 개발 완료 시점에 **재검증 스크립트 실행**·리포트 생성·성공 기준 충족 확인. 1차와 동일 검증 항목 + 회귀(건수·정합성·품질) | 14-6-3 또는 14-6-4 완료 후, Phase 14 개발 완료 시점 |

### 8.6 Phase 14-4·14-5 — 테스크 요약

| 블록 | 세분화 요약 | 비고 |
|------|-------------|------|
| **14-4** | 14-4-1 LNB 스타일 통일(선택), 14-4-2 배포 체크리스트 최종화 | 14-3 완료 후 또는 백로그 |
| **14-5** | 14-5-1 요구사항·플로우 문서 → 14-5-2 로그인/토큰 API 보강, 14-5-3 회원 CRUD API 설계 | 플랜 문서 선행, 구현은 Phase 14 내 선택 또는 Phase 15 |

### 8.7 실행 순서 권장

```
1) 14-1-0 (역할 스키마·의존성)
2) 14-1-2 ("지식 관리" 레이블) — 14-1-0와 병렬 가능
3) 14-1-1a, 14-1-1b (BE 권한 적용) → 14-1-3 (403)
4) 14-1-1c (FE 권한 메뉴)
5) 14-2-1a, 14-2-1b, 14-2-2a (Swagger 태그·설명·securitySchemes) — 14-1과 병렬 가능
6) 14-2-2b (경로별 security) — 14-1-1 완료 후
7) 14-3-1a → 14-3-1b, 14-3-1c (와이드 레이아웃)
8) 14-3-2a → 14-3-2b (LNB 도입)
9) 14-5-1 (사용자·로그인·회원관리 플랜 문서) — 필요 시 14-5-2·14-5-3 착수
10) E2E 권한별 시나리오·회귀 테스트 (기존 69개 유지·권한 시나리오 추가. 필요 시 Reasoning 모달 대기 보완 — Phase 13 최종 요약 §4.1)
11) 14-6-1 (DB 샘플 문서 Phase 14 호환성) → 14-6-2a~2h (백업·시드) → 14-6-3 (1차 검증) → (선택) 14-6-4 (Qdrant)
12) 14-6-5 개발 완료 후 데이터 2차 검증 (재검증 스크립트·리포트·성공 기준)
```

### 8.8 성공 기준 보강 (체크리스트)

- [ ] **14-1-0** UserInfo 또는 JWT에 role 반영, require_admin_knowledge/system 동작, AUTH_ENABLED=false 시 테스트용 role.
- [ ] **14-1-1** 비인증/일반 사용자에게 Admin·설정 메뉴 및 API 401/403.
- [ ] **14-1-2** header 또는 LNB에 "지식 관리" 그룹 레이블 적용.
- [ ] **14-2** Swagger UI 태그 그룹·엔드포인트 설명·securitySchemes·security 확인.
- [ ] **14-3-1** 사용자·Admin·설정 모든 페이지 와이드 레이아웃 통일.
- [ ] **14-3-2** 좌측 LNB에 17개 메뉴 그룹별 표시, 활성 하이라이트, 권한별 숨김.
- [ ] **14-5-1** 사용자 검증·로그인·회원관리 요구사항·단계별 플랜 문서 완성.
- [ ] **E2E** 기존 69개 시나리오 회귀·권한별 접근 시나리오 통과. (선택) Reasoning 저장 모달 대기 보완.
- [ ] **14-6** DB 샘플 시드·1차 검증 완료. **14-6-5** 개발 완료 후 데이터 2차 검증 완료(재검증 스크립트·리포트·성공 기준 충족).

---

## 9. 참고 문서

| 문서 | 용도 |
|------|------|
| [260216-0955-프론트엔드백엔드통합메뉴설계분석보고서.md](../planning/260216-0955-프론트엔드백엔드통합메뉴설계분석보고서.md) | 권한 분리·UI·사이드바/LNB·운영 가이드 원본 |
| [phase-13-qc-report.md](phase-13-qc-report.md) | 13-1-2·13-5-4·13-4-1 보완 반영 |
| [phase-13-final-summary-report.md](phase-13-final-summary-report.md) | **Phase 13 최종 QC**(69 E2E·98.5%·13-4 완료)·Phase 14 이어받을 항목·백로그(접근 로그 분석 UI)·E2E 모달 대기 보완 권장 |
| [phase-13-master-plan.md](phase-13-master-plan.md) | 선행 Phase 범위·메뉴 17개 path |
| [phase-13-2/route-menu-mapping.md](phase-13-2/route-menu-mapping.md) | 메뉴 path ↔ 라우트 대응 |
| [260210-1400-db-sample-data-and-high-level-strategy.md](../planning/260210-1400-db-sample-data-and-high-level-strategy.md) | **DB 샘플 데이터·고도화·백업/복구·검증 전략** (14-6 Task 상세·2차 검증 지침) |
| [AGENTS.md](../AGENTS.md) | 에이전트 역할 (Cursor=리더, Claude=BE, Gemini=FE, Copilot=QA) |

---

**문서 상태**: 가이드 초안 (분석·리포트만, 소스 수정 없음). 실행 전 Backend·API·DB·Frontend 현황 검토(§2.4) 및 개발 테스크 세분화·고도화 전략(§8) 반영.  
**다음 단계**: Phase 14 착수 시 14-1-0부터 순서대로 Task 세부 문서 생성·착수. §8.6 실행 순서 권장 참고.
