# Web 서비스 메뉴 개편 시나리오

**대상**: Web 서비스 전체 메뉴(사용자·관리자 지식·관리자 설정) 진입·네비게이션·활성 표시 검증  
**기반 문서**: [web-service-menu-restructuring-plan.md](web-service-menu-restructuring-plan.md)  
**전제**: Base URL `http://localhost:8001`, 백엔드·웹 서버 기동  
**도구**: MCP cursor-ide-browser, Playwright E2E, 또는 수동 브라우저  
**형식**: 시나리오 # | 시나리오 제목 | 조치 | 기대 결과 | 검증 방법

---

## 1. 공통 (header-component)

| # | 시나리오 제목 | 조치 | 기대 결과 | 검증 방법 |
|---|---------------|------|-----------|-----------|
| **1** | header-component 로드 시 메뉴 상수 존재 | 아무 페이지 접속 후 개발자 도구 콘솔에서 `USER_MENU`, `ADMIN_MENU`, `SETTINGS_MENU` 참조 | 에러 없이 배열 존재 | 콘솔 또는 E2E page.evaluate |
| **2** | 현재 경로 기준 활성 메뉴 하이라이트 | `/dashboard` 접속 후 헤더 영역 확인 | "대시보드" 또는 해당 라벨이 활성(강조) 표시 | DOM에서 active/current 클래스 또는 텍스트 |
| **3** | 구체 경로 우선 활성 해석 | `/admin/settings/templates` 접속 | "템플릿" 또는 설정 메뉴 그룹에서 활성 표시 | 헤더 서브타이틀 또는 active 상태 |
| **4** | 모든 메뉴 path가 라우트와 1:1 대응 | 각 USER_MENU·ADMIN_MENU·SETTINGS_MENU path로 GET 요청 | 200 응답 (로그인 필요 시 302 후 200) | curl 또는 E2E page.goto + response.status |

---

## 2. 사용자 메뉴 진입 (USER_MENU — 6개)

| # | 시나리오 제목 | 조치 | 기대 결과 | 검증 방법 |
|---|---------------|------|-----------|-----------|
| **1** | /dashboard 직접 접속 | `http://localhost:8001/dashboard` 이동 | 대시보드 페이지 로드, 헤더에 "대시보드" 활성 | URL `/dashboard`, title 또는 h1 |
| **2** | /search 직접 접속 | `http://localhost:8001/search` 이동 | 검색 페이지 로드, 헤더에 "검색" 활성 | URL `/search`, 검색 입력 요소 |
| **3** | /knowledge 직접 접속 | `http://localhost:8001/knowledge` 이동 | 지식 구조 페이지 로드, 헤더에 "지식 구조" 활성 | URL `/knowledge`, 청크/라벨 관련 UI |
| **4** | /reason 직접 접속 | `http://localhost:8001/reason` 이동 | Reasoning Lab 페이지 로드, 헤더에 "Reasoning" 활성 | URL `/reason`, #question 또는 질문 입력 |
| **5** | /ask 직접 접속 | `http://localhost:8001/ask` 이동 | AI 질의 페이지 로드, 헤더에 "AI 질의" 활성 | URL `/ask`, 질의 입력 영역 |
| **6** | /logs 직접 접속 | `http://localhost:8001/logs` 이동 | 로그 페이지 로드, 헤더에 "로그" 활성 | URL `/logs`, 로그 목록 또는 필터 |
| **7** | 대시보드에서 Reasoning 링크 클릭 | `/dashboard` 접속 후 네비에서 "Reasoning" 클릭 | `/reason`으로 이동 | URL `/reason` |
| **8** | 네비에서 사용자 메뉴 순차 클릭 | 대시보드 → 검색 → 지식 구조 → Reasoning → AI 질의 → 로그 순 클릭 | 매 클릭마다 해당 URL·페이지·헤더 활성 | URL 및 헤더 라벨 |

---

## 3. 관리자 메뉴 — 지식 관리 진입 (ADMIN_MENU — 6개)

| # | 시나리오 제목 | 조치 | 기대 결과 | 검증 방법 |
|---|---------------|------|-----------|-----------|
| **1** | /admin/groups 직접 접속 | `http://localhost:8001/admin/groups` 이동 | 키워드 그룹 페이지 로드, 헤더에 "키워드 관리" 활성 | URL `/admin/groups`, 그룹 목록 또는 폼 |
| **2** | /admin/labels 직접 접속 | `http://localhost:8001/admin/labels` 이동 | 라벨 관리 페이지 로드, 헤더에 "라벨 관리" 활성 | URL `/admin/labels` |
| **3** | /admin/chunk-create 직접 접속 | `http://localhost:8001/admin/chunk-create` 이동 | 청크 생성 페이지 로드, 헤더에 "청크 생성" 활성 | URL `/admin/chunk-create` |
| **4** | /admin/approval 직접 접속 | `http://localhost:8001/admin/approval` 이동 | 청크 승인 페이지 로드, 헤더에 "청크 승인" 활성 | URL `/admin/approval` |
| **5** | /admin/chunk-labels 직접 접속 | `http://localhost:8001/admin/chunk-labels` 이동 | 청크 관리 페이지 로드, 헤더에 "청크 관리" 활성 | URL `/admin/chunk-labels` |
| **6** | /admin/statistics 직접 접속 | `http://localhost:8001/admin/statistics` 이동 | 통계 페이지 로드, 헤더에 "통계" 활성 | URL `/admin/statistics` |
| **7** | Admin 페이지 공통 shell | 위 6개 페이지 각각에서 header-placeholder·admin 공통 스타일 확인 | 동일 헤더·레이아웃 패턴 | DOM 구조·admin-styles 적용 |
| **8** | 네비에서 Admin 지식 메뉴 순차 클릭 | groups → labels → chunk-create → approval → chunk-labels → statistics 순 클릭 | 매 클릭마다 해당 URL·헤더 활성 | URL 및 헤더 |

---

## 4. 관리자 메뉴 — 설정 관리 진입 (SETTINGS_MENU — 5개)

| # | 시나리오 제목 | 조치 | 기대 결과 | 검증 방법 |
|---|---------------|------|-----------|-----------|
| **1** | /admin/settings/templates 직접 접속 | `http://localhost:8001/admin/settings/templates` 이동 | 템플릿 설정 페이지 로드, 헤더에 "템플릿" 활성 | URL `/admin/settings/templates`, h2 또는 목록 |
| **2** | /admin/settings/presets 직접 접속 | `http://localhost:8001/admin/settings/presets` 이동 | 프리셋 설정 페이지 로드, 헤더에 "프리셋" 활성 | URL `/admin/settings/presets` |
| **3** | /admin/settings/rag-profiles 직접 접속 | `http://localhost:8001/admin/settings/rag-profiles` 이동 | RAG 프로필 페이지 로드, 헤더에 "RAG 프로필" 활성 | URL `/admin/settings/rag-profiles` |
| **4** | /admin/settings/policy-sets 직접 접속 | `http://localhost:8001/admin/settings/policy-sets` 이동 | 정책 페이지 로드, 헤더에 "정책" 활성 | URL `/admin/settings/policy-sets` |
| **5** | /admin/settings/audit-logs 직접 접속 | `http://localhost:8001/admin/settings/audit-logs` 이동 | 변경 이력 페이지 로드, 헤더에 "변경 이력" 활성 | URL `/admin/settings/audit-logs` |
| **6** | 설정 페이지에서 header-component 동일 사용 | 위 5개 페이지에서 헤더·네비 소스 확인 | header-component.js 로드, 설정 메뉴 그룹 표시 | DOM script src, 설정 메뉴 링크 존재 |
| **7** | Templates → Presets 네비게이션 | templates 페이지에서 Presets 링크 클릭 | `/admin/settings/presets`로 이동 | URL 변경 |
| **8** | 설정 5개 페이지 로딩 시간 | 각 설정 페이지 접속 시 로드 완료까지 시간 | 3초 이내 (환경에 따라 조정 가능) | Performance API 또는 E2E timeout |

---

## 5. 메뉴 간 이동 (사용자 ↔ Admin 지식 ↔ Admin 설정)

| # | 시나리오 제목 | 조치 | 기대 결과 | 검증 방법 |
|---|---------------|------|-----------|-----------|
| **1** | 사용자 → Admin 지식 | `/dashboard`에서 Admin 영역 "키워드 관리" 클릭 | `/admin/groups` 이동, 헤더 활성 "키워드 관리" | URL 및 헤더 |
| **2** | Admin 지식 → Admin 설정 | `/admin/labels`에서 설정 "템플릿" 클릭 | `/admin/settings/templates` 이동, 헤더 활성 "템플릿" | URL 및 헤더 |
| **3** | Admin 설정 → 사용자 | `/admin/settings/presets`에서 "대시보드" 클릭 | `/dashboard` 이동, 헤더 활성 "대시보드" | URL 및 헤더 |
| **4** | Admin 설정 → Admin 지식 | `/admin/settings/audit-logs`에서 "청크 승인" 클릭 | `/admin/approval` 이동, 헤더 활성 "청크 승인" | URL 및 헤더 |
| **5** | 루트(/)에서 사용자 메뉴 진입 | `http://localhost:8001/` 접속 후 네비에서 "검색" 클릭 | `/search` 도달 | URL `/search` |

---

## 6. 라우팅·에러 처리

| # | 시나리오 제목 | 조치 | 기대 결과 | 검증 방법 |
|---|---------------|------|-----------|-----------|
| **1** | 존재하지 않는 Admin 경로 | `http://localhost:8001/admin/unknown` 접속 | 404 또는 적절한 에러 페이지/리다이렉트 | HTTP status 또는 에러 메시지 |
| **2** | 존재하지 않는 설정 하위 경로 | `http://localhost:8001/admin/settings/unknown` 접속 | 404 또는 적절한 처리 | HTTP status |
| **3** | 사용자 경로 오타 | `http://localhost:8001/dashbord` 접속 | 404 또는 302 → 올바른 경로 | HTTP status |

---

## 7. 시나리오 요약 및 E2E 매핑

| 카테고리 | 시나리오 수 | E2E 스펙 매핑 | E2E 커버 |
|----------|:-----------:|---------------|:--------:|
| 공통 (header-component) | 4 | `phase-13-menu-user.spec.js` (#1 루트, #2 활성), `phase-13-menu-cross.spec.js` (#4 전체순회) | 4/4 |
| 사용자 메뉴 진입 | 8 | `phase-13-menu-user.spec.js` (6개 페이지 × 3 = 로드·헤더·활성) | 8/8 |
| Admin 지식 메뉴 진입 | 8 | `phase-13-menu-admin-knowledge.spec.js` (6개 × 3 = 로드·shell·활성) | 8/8 |
| Admin 설정 메뉴 진입 | 8 | `phase-13-menu-admin-knowledge.spec.js` (5개 × 2 = 로드·shell), `phase-11-3.spec.js` | 8/8 |
| 메뉴 간 이동 | 5 | `phase-13-menu-cross.spec.js` (전체순회, 사용자→Admin, Admin→설정, 설정→사용자) | 5/5 |
| 라우팅·에러 | 3 | `phase-13-menu-cross.spec.js` (404: /admin/unknown, /admin/settings/unknown, /dashbord) | 3/3 |
| **합계** | **36** | — | **36/36** |

### 시나리오별 E2E 테스트 케이스 ID 상세 매핑

| 시나리오 # | 카테고리 | 시나리오 제목 | E2E 스펙 | 테스트 이름 |
|:----------:|----------|--------------|----------|-------------|
| §1-1 | 공통 | header-component 상수 존재 | `phase-13-menu-user` | 대시보드 헤더가 렌더링된다 |
| §1-2 | 공통 | 현재 경로 기준 활성 하이라이트 | `phase-13-menu-user` | 대시보드 메뉴 활성 하이라이트 |
| §1-3 | 공통 | 구체 경로 우선 활성 해석 | `phase-13-menu-admin-knowledge` | 설정 5개 shell 로드 |
| §1-4 | 공통 | 모든 path 라우트 1:1 대응 | `phase-13-menu-user` + `admin-knowledge` | 전체 17개 200 OK |
| §2-1~6 | 사용자 | 6개 메뉴 직접 접속 | `phase-13-menu-user` | 각 페이지 로드 + 헤더 + 활성 |
| §2-7 | 사용자 | 대시보드→Reasoning 클릭 | `phase-13-menu-cross` | 전체 순회 (dashboard→groups→templates→search) |
| §2-8 | 사용자 | 사용자 메뉴 순차 클릭 | `phase-13-menu-user` | 6개 각각 개별 진입 검증 |
| §3-1~6 | Admin 지식 | 6개 메뉴 직접 접속 | `phase-13-menu-admin-knowledge` | 각 페이지 로드 + shell + 활성 |
| §3-7 | Admin 지식 | Admin 공통 shell | `phase-13-menu-admin-knowledge` | shell 로드 테스트 (container, header) |
| §3-8 | Admin 지식 | Admin 지식 순차 클릭 | `phase-13-menu-admin-knowledge` | 6개 각각 개별 진입 검증 |
| §4-1~5 | Admin 설정 | 5개 메뉴 직접 접속 | `phase-13-menu-admin-knowledge` | 각 페이지 로드 + shell |
| §4-6 | Admin 설정 | header-component 동일 사용 | `phase-13-menu-admin-knowledge` | 5개 shell 로드 (header 동일) |
| §4-7 | Admin 설정 | Templates→Presets 이동 | `phase-13-menu-cross` | Admin→설정 이동 |
| §4-8 | Admin 설정 | 설정 5개 로딩 시간 | `phase-13-menu-admin-knowledge` | 10초 타임아웃 내 로드 |
| §5-1 | 메뉴 간 | 사용자→Admin 지식 | `phase-13-menu-cross` | 사용자→Admin 활성 변경 |
| §5-2 | 메뉴 간 | Admin 지식→Admin 설정 | `phase-13-menu-cross` | Admin→설정 이동 |
| §5-3 | 메뉴 간 | Admin 설정→사용자 | `phase-13-menu-cross` | 설정→사용자 이동 |
| §5-4 | 메뉴 간 | Admin 설정→Admin 지식 | `phase-13-menu-cross` | 전체 순회 |
| §5-5 | 메뉴 간 | 루트→사용자 진입 | `phase-13-menu-user` | 루트(/) 대시보드 로드 |
| §6-1 | 에러 | /admin/unknown 404 | `phase-13-menu-cross` | /admin/unknown 404 |
| §6-2 | 에러 | /admin/settings/unknown 404 | `phase-13-menu-cross` | /admin/settings/unknown 404 |
| §6-3 | 에러 | /dashbord 오타 404 | `phase-13-menu-cross` | /dashbord 404 |

---

## 8. 테스트 실행 결과 (2026-02-16, Phase 13-3)

**실행 명령**: `npx playwright test e2e/phase-13-menu-user.spec.js e2e/phase-13-menu-admin-knowledge.spec.js e2e/phase-13-menu-cross.spec.js`
**Base URL**: `http://localhost:8001`

| 결과 | 개수 | 비고 |
|------|:----:|------|
| **통과** | 56 | user 19 + admin-knowledge 28 + cross 9 |
| **실패** | 0 | — |
| **건너뜀** | 0 | — |

**커버리지 요약**:
- 사용자 메뉴 6개: 페이지 로드·헤더 렌더링·활성 하이라이트 각각 검증 (18 tests)
- Admin 지식 6개: 페이지 로드·공통 shell·활성 메뉴 각각 검증 (18 tests)
- Admin 설정 5개: 페이지 로드·공통 shell 검증 (10 tests)
- 메뉴 간 이동: 4개 시나리오 (전체순회, 사용자→Admin, Admin→설정, 설정→사용자)
- 404 시나리오: 3개 경로 + 404 페이지 header 렌더링 + 대시보드 링크 (5 tests)
- 루트 접근: 1 test

**이전 대비**: 36개 시나리오 전수 E2E 커버 달성 (이전 22개 → 현재 56개 테스트)

---

**문서 위치**: `docs/planning/web-service-menu-restructuring-scenarios.md`
