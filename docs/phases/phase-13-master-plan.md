# Phase 13 Master Plan — Web 서비스 메뉴 개편 검증 및 보완

**작성일**: 2026-02-09  
**최종 수정**: 2026-02-10  
**상태**: 초안  
**선행 조건**: Phase 11-3 완료(Admin UI·메뉴 통합), Phase 12 완료 권장  
**기준 문서**: [web-service-menu-restructuring-scenarios.md](../planning/web-service-menu-restructuring-scenarios.md), [web-service-menu-restructuring-plan.md](../planning/web-service-menu-restructuring-plan.md), [260210-1430-local-llm-analysis-and-improvement.md](../overview/260210-1430-local-llm-analysis-and-improvement.md)  
**명명 규칙**: Phase ID **13-Y**, Task **13-Y-N**  
**산출물 규칙**: Task 당 report 작성, 저장 위치 `docs/phases/phase-13-Y/`

---

## Phase 13 목표 (1문장)

**Web 서비스 메뉴 개편 시나리오(36개)를 기준으로 Backend·Frontend·DB·Qdrant·E2E 전반의 수정·보완·개선을 수행하고, [Local LLM 분석·개선 보고서](../overview/260210-1430-local-llm-analysis-and-improvement.md)에서 도출한 Ollama·RAG 파이프라인 개선(True Streaming, 토큰 관리, System Prompt, 구조화 출력)을 반영하여 메뉴 구조 검증 완료 및 LLM UX·안정성을 확보한다.**

---

## 목차

1. [관련 문서](#관련-문서)
2. [기준 시나리오 및 Phase 12 대비](#1-기준-시나리오-및-phase-12-대비)
3. [목표 및 범위 (In / Out Scope)](#2-목표-및-범위-in--out-scope)
4. [영역별 수정·보완·개선 상세](#3-영역별-수정보완개선-상세)
5. [단계 번호 체계 및 Phase 13 구조](#4-단계-번호-체계-및-phase-13-구조)
6. [상세 Task 목록·산출물](#5-상세-task-목록산출물)
7. [의존성 및 진행 순서](#6-의존성-및-진행-순서)
8. [성공 기준 (체크리스트)](#7-성공-기준-체크리스트)
9. [예상 총 작업량](#8-예상-총-작업량)
10. [리스크 관리](#9-리스크-관리)

---

## 관련 문서

| 문서 | 용도 |
|------|------|
| [web-service-menu-restructuring-scenarios.md](../planning/web-service-menu-restructuring-scenarios.md) | 36개 시나리오(공통·사용자·Admin 지식·Admin 설정·메뉴 간 이동·라우팅·에러) |
| [web-service-menu-restructuring-plan.md](../planning/web-service-menu-restructuring-plan.md) | 메뉴 구조 매핑·검증 체크리스트·개편 이슈 목록 |
| [Phase 11-3 Plan](phase-11-3/phase-11-3-0-plan.md) | Admin UI·지식/설정 구분·header-component |
| [Phase 12 Master Plan](phase-12-master-plan.md) | 선행 Phase, Base URL·보안·API 구조 |
| [Phase 13 Navigation](phase-13-navigation.md) | 작업 순서·진행 현황 (생성 예정) |
| [260210-1430-local-llm-analysis-and-improvement.md](../overview/260210-1430-local-llm-analysis-and-improvement.md) | Local LLM·Ollama 현황·기능 개선·모델 개선 방향, Next Steps |

---

## 1. 기준 시나리오 및 Phase 12 대비

### 1.1 기준 시나리오 요약

| 카테고리 | 시나리오 수 | 검증 관점 |
|----------|:-----------:|-----------|
| 공통 (header-component) | 4 | 메뉴 상수 존재, 활성 하이라이트, path·라우트 1:1 |
| 사용자 메뉴 진입 | 8 | dashboard/search/knowledge/reason/ask/logs 진입·헤더 활성 |
| Admin 지식 메뉴 진입 | 8 | groups, labels, chunk-create, approval, chunk-labels, statistics·공통 shell |
| Admin 설정 메뉴 진입 | 8 | templates, presets, rag-profiles, policy-sets, audit-logs·네비·로딩 |
| 메뉴 간 이동 | 5 | 사용자 ↔ Admin 지식 ↔ Admin 설정 전환 |
| 라우팅·에러 | 3 | /admin/unknown, /admin/settings/unknown, 사용자 경로 오타 → 404 등 |
| **합계** | **36** | — |

### 1.2 Phase 12 대비 Phase 13 위치

Phase 12는 프로덕션 안정화(P0~P2). Phase 13은 **메뉴 구조 검증·보완**에 집중한다.

| Phase 12 산출물 (전제) | Phase 13에서 활용 |
|----------------------|------------------|
| Base URL 8001 통일 | 메뉴 시나리오 Base URL 전제 |
| API 에러 표준화 | 404 HTML 응답 시 일관된 에러 페이지 연동 가능 |
| E2E·테스트 인프라 | 메뉴 E2E 스펙 확장 기반 |

---

## 2. 목표 및 범위 (In / Out Scope)

### 2.1 In Scope (포함)

| 영역 | 항목 |
|------|------|
| **Frontend** | header-component 활성 해석 순서 명시·검증, NAV_MENU deprecated 제거, 지식 vs 설정 그룹핑 UI 보완, 공통 Admin shell 검증, 404 전용 페이지(선택) |
| **Backend** | HTML 라우트 404 처리 명시, 라우트 목록 문서화·일괄 등록 패턴 검토, 메뉴 path와 라우트 1:1 대응 검증 |
| **DB** | 메뉴 개편에 따른 스키마 변경 없음(기존 audit_logs 등 활용). 선택: 메뉴/페이지 접근 로그 테이블 도입 |
| **Qdrant** | 메뉴 개편에 따른 컬렉션·인덱스 변경 없음. 메뉴로 진입하는 페이지(search, knowledge, reason)에서 사용하는 API·Qdrant 연동 회귀 검증 |
| **E2E·테스트** | 사용자 메뉴 6개 전용 E2E, Admin 지식 6개 전용 E2E, 메뉴 간 이동 시나리오, 404 시나리오, 36개 시나리오와 E2E 매핑 문서화 |
| **Backend·Local LLM** | [Local LLM 분석 보고서](../overview/260210-1430-local-llm-analysis-and-improvement.md) 기반: True Streaming(ollama_generate_stream), 토큰 관리(한국어 친화·tiktoken/transformers), System Prompt(role: system), 구조화 출력(format=json), 프롬프트 주입 방어 검토 |

### 2.2 Out of Scope (제외)

| 항목 | 사유 |
|------|------|
| 메뉴 항목 추가/삭제(기능 확장) | 메뉴 개편 검증·보완 범위. 신규 메뉴는 별도 Phase |
| SPA 전환·프론트 프레임워크 도입 | Phase 12 Out of Scope 유지 |
| Qdrant 스키마·컬렉션 변경 | 메뉴와 무관 |
| DB 대규모 스키마 변경 | 메뉴와 무관. 선택 Task만 해당 |
| 모델 교체·임베딩 고도화 | DeepSeek-R1, Llama-3.1, BGE-M3 등은 Local LLM 보고서 권장사항으로 별도 Phase·백로그 |
| LLM 프롬프트 주입 대응 | Phase 13에서는 검토·문서화 수준. 전면 방어는 별도 Phase |

---

## 3. 영역별 수정·보완·개선 상세

### 3.1 Backend

| # | 구분 | 현재 상태 | 수정·보완·개선 내용 |
|---|------|-----------|----------------------|
| B-1 | **HTML 라우트** | `main.py`에 `/`, `/dashboard`, `/search`, `/knowledge`, `/reason`, `/ask`, `/logs`, `/document/*`, `/admin/*`, `/admin/settings/*` 개별 등록 | 라우트 목록을 문서화(경로·템플릿 매핑 표). 일괄 등록 패턴(루프·설정 테이블) 검토 시 가독성·유지보수성 개선 |
| B-2 | **404 처리** | 미정의 경로 GET 시 FastAPI 기본 404 JSON 응답 | HTML 요청(Accept: text/html)인 경우 404 전용 HTML 페이지 반환 검토. 또는 기존 404 유지하고 문서화만 |
| B-3 | **라우트 1:1 대응** | 시나리오의 USER_MENU·ADMIN_MENU·SETTINGS_MENU path 17개 모두 라우트 존재 | 각 path별 라우트 존재 여부 체크리스트·스크립트화. 누락 시 라우트 추가 |
| B-4 | **Base URL** | Phase 12-1-2에서 8001 통일·환경변수화 완료 가정 | 메뉴 시나리오 Base URL(`http://localhost:8001`)과 설정 일치 확인 |
| B-5 | **인증·미들웨어** | `/admin/` 경로 개발 환경에서 인증 제외 가능 | 메뉴 진입 시 리다이렉트(302) 발생 여부 문서화. 프로덕션 시 메뉴별 권한 정책 정리 |

### 3.2 Frontend

| # | 구분 | 현재 상태 | 수정·보완·개선 내용 |
|---|------|-----------|----------------------|
| F-1 | **header-component.js** | USER_MENU, ADMIN_MENU, SETTINGS_MENU 정의. 활성 해석: user → settings → admin 순 | 활성 해석 순서를 코드 주석·문서에 명시. 구체 경로 우선 규칙 유지 |
| F-2 | **NAV_MENU deprecated** | `NAV_MENU = USER_MENU` 존재. 기존 호환용 | NAV_MENU 참조처 grep 후 제거. NAV_MENU 변수 삭제 또는 deprecated 주석 유지 |
| F-3 | **지식 vs 설정 그룹핑** | ADMIN_MENU 6개 + SETTINGS_MENU 5개 별도 렌더링 | UI에서 "지식 관리" / "설정 관리" 그룹 레이블 또는 구분선 도입 여부 검토·구현 |
| F-4 | **공통 Admin shell** | admin-common.js, admin-styles.css, header-placeholder | Admin 지식 6페이지·설정 5페이지에서 동일 shell 사용 여부 검증. 불일치 시 통일 |
| F-5 | **활성 메뉴 하이라이트** | currentPath 기준 라벨 표시 | DOM에서 active/current 클래스 또는 aria-current 적용 여부 확인. 접근성·스타일 일관성 보완 |
| F-6 | **404 페이지** | 없음(백엔드 404 시 브라우저 기본 페이지) | 선택: 404.html 생성 후 백엔드에서 HTML 404 시 해당 템플릿 반환 |
| F-7 | **로딩 시간** | 설정 5페이지 로딩 3초 이내 시나리오 | 불필요한 스크립트/스타일 순서·지연 로딩 검토. 성능 이슈 시 개선 Task |

### 3.3 DB

| # | 구분 | 현재 상태 | 수정·보완·개선 내용 |
|---|------|-----------|----------------------|
| D-1 | **스키마** | 메뉴 구조는 코드(header-component)에만 존재. DB 테이블 없음 | **변경 없음** 권장. 메뉴 항목을 DB로 관리할 경우만 별도 Phase에서 도입 |
| D-2 | **audit_logs** | 설정 메뉴 "변경 이력"에서 사용 | Phase 11 연동 유지. 메뉴 개편으로 인한 스키마 변경 없음 |
| D-3 | **선택: 접근 로그** | 없음 | 메뉴/페이지별 접근 로그 수집 시 `page_access_log` 등 테이블 추가. Phase 13에서는 **선택 Task** |

### 3.4 Qdrant

| # | 구분 | 현재 상태 | 수정·보완·개선 내용 |
|---|------|-----------|----------------------|
| Q-1 | **컬렉션·인덱스** | brain_documents 등 기존 구조 | **변경 없음**. 메뉴 개편은 Qdrant와 무관 |
| Q-2 | **API 연동** | /search, /knowledge, /reason 등에서 Qdrant 사용 | 메뉴 진입 후 해당 페이지에서 호출하는 API·Qdrant 연동이 정상 동작하는지 **회귀 검증**만 수행. 버그 수정 시 해당 Phase(Task)에 기록 |

### 3.5 E2E·테스트

| # | 구분 | 현재 상태 | 수정·보완·개선 내용 |
|---|------|-----------|----------------------|
| E-1 | **사용자 메뉴 6개** | smoke.spec.js(dashboard), phase-10-1(reason) 등 일부만 전용 스펙 | search, knowledge, ask, logs 전용 E2E 스펙 추가. 진입·헤더 활성 검증 |
| E-2 | **Admin 지식 6개** | phase-11-3은 설정 5개 위주 | groups, labels, chunk-create, approval, chunk-labels, statistics 각각 진입 E2E 추가 |
| E-3 | **메뉴 간 이동** | phase-11-3 7.1 (Templates→Presets) 일부 | 사용자→Admin 지식→Admin 설정→사용자 순 이동 시나리오 E2E 추가 |
| E-4 | **404 시나리오** | phase-11-3 9.1 (없는 Admin 경로) | /admin/unknown, /admin/settings/unknown, /dashbord 등 404·에러 응답 E2E 추가 |
| E-5 | **시나리오↔E2E 매핑** | 시나리오 문서 §7에 표로 요약 | 36개 시나리오와 E2E 스펙·테스트 케이스 ID 매핑 문서 갱신. 미커버 시나리오는 수동/MCP로 실행·기록 |

### 3.6 Local LLM·Ollama (개선 부문)

**참조**: [260210-1430-local-llm-analysis-and-improvement.md](../overview/260210-1430-local-llm-analysis-and-improvement.md)

| # | 구분 | 현재 상태 | 수정·보완·개선 내용 |
|---|------|-----------|----------------------|
| L-1 | **True Streaming** | `/api/ask/stream`이 Pseudo-streaming(전체 응답 대기 후 청크 전송). TTFT 지연 큼 | `ollama_generate_stream` 사용하여 Ollama 토큰 생성 즉시 SSE 전달. `backend/routers/ai/ai.py` 스트리밍 로직 전환 |
| L-2 | **토큰 관리** | `chars // 4` 근사치. 한글 환경 오차·Context Window 초과(400) 위험 | `tiktoken` 또는 `transformers` Tokenizer로 정확한 토큰 수 계산. 모델별 최대 컨텍스트(4k~32k)에 맞춰 RAG 범위 동적 조정. `ContextManager` 한국어 친화 수정 |
| L-3 | **System Prompt** | "한국어로만 답변" 등을 User Prompt 앞에 매번 삽입. 프롬프트 지저분·코드블록/영문 삭제 위험 | Ollama `/api/chat`의 `role: system` 활용. 페르소나·제약사항 분리 정의. 과도한 후처리 정규식 축소 |
| L-4 | **구조화 출력** | 텍스트 추출 시 정규식 의존. 불안정 | Ollama `format="json"` 옵션 활용. 지식 추출·요약 시 JSON 형태 안정적 데이터 확보 |
| L-5 | **연결성·폴백** | Ollama 미실행 시 에러 메시지·폴백 답변 확인됨 | `ollama_connection_check` 유지. 문서화·테스트 유지 |
| L-6 | **보안** | LLM 프롬프트 주입 방어가 프롬프트 지시 수준에 머무름 | Phase 13에서는 방어 로직 검토·문서화. 전면 주입 방어는 별도 Phase |

**Out of Scope (Phase 13)**: 최신 모델 교체(DeepSeek-R1, Llama-3.1), 양자화 최적화(GGUF Q4_K_M 등), 임베딩 모델 고도화(BGE-M3, multilingual-e5-large) — 보고서 권장사항으로 별도 Phase·백로그.

---

## 4. 단계 번호 체계 및 Phase 13 구조

### 4.1 단계 번호 체계

| 구분 | 형식 | 의미 | 예시 |
|------|------|------|------|
| **Phase** | **13-Y** | Y = 영역·우선순위 단위 | 13-1, 13-2, 13-3 |
| **Task** | **13-Y-N** | N = 해당 Phase 내 순번 | 13-1-1, 13-2-2 |
| **폴더** | `phase-13-Y/` | Phase 단위 문서 | `docs/phases/phase-13-1/` |

### 4.2 Phase 13 구조

```
Phase 13 (X=13, Y=영역·우선순위별 phase-13-Y)

1순위  Phase 13-1   Frontend 메뉴·헤더 보완
       ├── Task 13-1-1   [FE] header-component 활성 해석 순서 문서화·NAV_MENU 제거
       ├── Task 13-1-2   [FE] 지식 vs 설정 그룹핑 UI 보완
       ├── Task 13-1-3   [FE] Admin 공통 shell 검증·불일치 시 통일
       └── Task 13-1-4   [FE] (선택) 404 전용 HTML 페이지·활성 메뉴 접근성 보완

2순위  Phase 13-2   Backend 라우팅·에러 처리 보완
       ├── Task 13-2-1   [BE] HTML 라우트 목록 문서화·메뉴 path 1:1 대응 검증
       ├── Task 13-2-2   [BE] (선택) HTML 404 전용 응답
       └── Task 13-2-3   [BE] 라우트 일괄 등록 패턴 검토·리팩터링(선택)

3순위  Phase 13-3   E2E·검증 확대
       ├── Task 13-3-1   [E2E] 사용자 메뉴 6개 진입 E2E 스펙
       ├── Task 13-3-2   [E2E] Admin 지식 6개 진입 E2E 스펙
       ├── Task 13-3-3   [E2E] 메뉴 간 이동·404 시나리오 E2E
       └── Task 13-3-4   [DOC] 36개 시나리오↔E2E 매핑 문서 갱신

4순위  Phase 13-5   Backend Local LLM·Ollama 개선
       ├── Task 13-5-1   [BE] True Streaming (ollama_generate_stream 기반 SSE)
       ├── Task 13-5-2   [BE] 토큰 관리 정밀화 (tiktoken/transformers, ContextManager 한국어 친화)
       ├── Task 13-5-3   [BE] System Prompt 활용 (role: system, 후처리 정규식 축소)
       └── Task 13-5-4   [BE] (선택) 구조화 출력 (format=json)·프롬프트 주입 방어 검토

선택   Phase 13-4   DB·운영 (선택)
       └── Task 13-4-1   [DB] (선택) 메뉴/페이지 접근 로그 테이블 도입
```

---

## 5. 상세 Task 목록·산출물

### Phase 13-1 Frontend 메뉴·헤더 보완 (1순위)

| Task | 도메인 | 목표 | 예상 | 산출물 |
|------|--------|------|------|--------|
| 13-1-1 | [FE] | header-component 활성 해석 순서( user → settings → admin ) 코드·문서 반영. NAV_MENU 참조처 제거·변수 삭제 또는 deprecated 유지 | 0.5일 | header-component.js 수정, plan 또는 docs 갱신 |
| 13-1-2 | [FE] | Admin 영역에서 "지식 관리" / "설정 관리" 그룹 레이블 또는 구분 UI 추가 | 0.5일 | header-component.js 또는 admin 레이아웃 수정 |
| 13-1-3 | [FE] | Admin 지식 6페이지·설정 5페이지 공통 shell(header-placeholder, admin-common, admin-styles) 검증. 불일치 시 통일 | 0.5일 | 검증 체크리스트·수정 패치 |
| 13-1-4 | [FE] | (선택) 404.html 생성·백엔드 연동. 활성 메뉴 aria-current 등 접근성 보완 | 0.5일 | 404.html, header 스크립트 수정 |

### Phase 13-2 Backend 라우팅·에러 처리 보완 (2순위)

| Task | 도메인 | 목표 | 예상 | 산출물 |
|------|--------|------|------|--------|
| 13-2-1 | [BE] | 메뉴 path 17개와 main.py 라우트 1:1 대응 표 문서화. 누락 시 라우트 추가 | 0.5일 | docs/phases/phase-13-2/route-menu-mapping.md 또는 동등 문서 |
| 13-2-2 | [BE] | (선택) Accept: text/html 인 404 요청 시 404.html 템플릿 반환 | 0.5일 | main.py 예외 핸들러·404 템플릿 |
| 13-2-3 | [BE] | (선택) HTML 라우트 일괄 등록 패턴(리스트+루프) 검토·리팩터링 | 1일 | main.py 리팩터링 |

### Phase 13-3 E2E·검증 확대 (3순위)

| Task | 도메인 | 목표 | 예상 | 산출물 |
|------|--------|------|------|--------|
| 13-3-1 | [E2E] | 사용자 메뉴 6개(dashboard, search, knowledge, reason, ask, logs) 진입·헤더 활성 E2E 스펙 | 1일 | e2e/phase-13-menu-user.spec.js 또는 기존 스펙 확장 |
| 13-3-2 | [E2E] | Admin 지식 6개(groups, labels, chunk-create, approval, chunk-labels, statistics) 진입 E2E 스펙 | 1일 | e2e/phase-13-menu-admin-knowledge.spec.js 또는 확장 |
| 13-3-3 | [E2E] | 메뉴 간 이동(사용자→Admin→설정→사용자)·404(/admin/unknown 등) E2E | 0.5일 | phase-13-menu-cross.spec.js 또는 phase-11-3 확장 |
| 13-3-4 | [DOC] | 36개 시나리오와 E2E 테스트 케이스 ID 매핑 갱신. 미커버 시나리오 명시 | 0.5일 | web-service-menu-restructuring-scenarios.md §7 갱신 |

### Phase 13-5 Backend Local LLM·Ollama 개선 (4순위)

| Task | 도메인 | 목표 | 예상 | 산출물 |
|------|--------|------|------|--------|
| 13-5-1 | [BE] | True Streaming: `ollama_generate_stream` 기반으로 Ollama 토큰 생성 즉시 SSE 전달. `backend/routers/ai/ai.py` 스트리밍 로직 전환 | 1.5일 | ai.py 수정, ollama_client stream 연동 |
| 13-5-2 | [BE] | 토큰 관리: tiktoken 또는 transformers Tokenizer 도입, ContextManager 한국어 친화 수정. 모델별 최대 컨텍스트에 맞춰 RAG 범위 동적 조정 | 1.5일 | ContextManager·토큰 계산 로직 수정, 의존성 추가 |
| 13-5-3 | [BE] | System Prompt: Ollama `/api/chat`의 `role: system` 활용. "한국어로만 답변" 등 페르소나·제약 분리. 과도한 후처리 정규식 축소 | 1일 | ai.py·ollama_client 수정, 프롬프트 구조 문서화 |
| 13-5-4 | [BE] | (선택) 구조화 출력: Ollama `format="json"` 활용(지식 추출·요약). LLM 프롬프트 주입 방어 검토·문서화 | 0.5일 | JSON 출력 경로 추가, 보안 검토 문서 |

### Phase 13-4 DB·운영 (선택)

| Task | 도메인 | 목표 | 예상 | 산출물 |
|------|--------|------|------|--------|
| 13-4-1 | [DB] | (선택) 메뉴/페이지 접근 로그 테이블 설계·마이그레이션·기록 로직 | 1일 | 마이그레이션, 로깅 서비스 |

---

## 6. 의존성 및 진행 순서

### 6.1 의존성

```
Phase 13-1 (FE) — 13-1-1 완료 후 13-1-2·13-1-3
  13-1-1 [FE] header-component·NAV_MENU   ← 선행
  13-1-2 [FE] 그룹핑 UI                    ← 13-1-1 이후
  13-1-3 [FE] 공통 shell 검증              ← 독립 (13-1-1과 병렬 가능)
  13-1-4 [FE] 404·접근성(선택)             ← 13-2-2(선택)와 연동 시 13-2 후

Phase 13-2 (BE) — 13-1과 병렬 가능
  13-2-1 [BE] 라우트 문서화·1:1 검증       ← 최우선
  13-2-2 [BE] HTML 404(선택)               ← 13-1-4와 연동 시 조율
  13-2-3 [BE] 라우트 리팩터(선택)          ← 13-2-1 이후

Phase 13-3 (E2E) — 13-1·13-2 완료 후 권장
  13-3-1~13-3-4                            ← 메뉴·라우트 안정화 후 E2E 확대

Phase 13-4 (DB 선택) — 독립
  13-4-1 [DB] 접근 로그(선택)               ← 필요 시만

Phase 13-5 (Local LLM) — 13-2 완료 후 또는 병렬
  13-5-1 [BE] True Streaming                ← 선행 (ai.py 의존)
  13-5-2 [BE] 토큰 관리 정밀화               ← 독립 (ContextManager)
  13-5-3 [BE] System Prompt                 ← 13-5-1과 연동 시 13-5-1 이후
  13-5-4 [BE] 구조화 출력·주입 방어(선택)   ← 13-5-3 이후 권장
```

### 6.2 의존성 그래프

```
Phase 11-3·12 완료
     │
     ├──────────────────────────────┐
     ▼                              ▼
13-1 Frontend 보완              13-2 Backend 보완
  ├── 13-1-1 header·NAV_MENU      ├── 13-2-1 라우트 문서화
  ├── 13-1-2 그룹핑 UI             ├── 13-2-2 HTML 404(선택)
  ├── 13-1-3 공통 shell            └── 13-2-3 리팩터(선택)
  └── 13-1-4 404·접근성(선택)
     │ (13-1·13-2 완료)
     ▼
13-3 E2E·검증 확대
  ├── 13-3-1 사용자 6개 E2E
  ├── 13-3-2 Admin 지식 6개 E2E
  ├── 13-3-3 메뉴 간 이동·404 E2E
  └── 13-3-4 시나리오↔E2E 매핑 문서
     │
     ├──────────────────────────────┐
     ▼                              ▼
13-5 Local LLM 개선             13-4 DB 선택
  ├── 13-5-1 True Streaming        └── 13-4-1 접근 로그(선택)
  ├── 13-5-2 토큰 관리
  ├── 13-5-3 System Prompt
  └── 13-5-4 구조화 출력·주입(선택)
     │
     ▼
Phase 13 완료
```

---

## 7. 성공 기준 (체크리스트)

### 7.1 Phase 13 완료 조건 체크리스트

#### Frontend (13-1)

- [ ] **13-1-1** header-component 활성 해석 순서 문서화. NAV_MENU 참조처 0건 또는 deprecated 명시
- [ ] **13-1-2** Admin 영역에 지식 관리/설정 관리 그룹 구분 표시
- [ ] **13-1-3** Admin 지식 6페이지·설정 5페이지 공통 shell 검증 완료·불일치 수정
- [ ] **13-1-4** (선택) 404 페이지·접근성 보완 적용

#### Backend (13-2)

- [ ] **13-2-1** 메뉴 path 17개 ↔ 라우트 1:1 대응 문서 존재·검증 완료
- [ ] **13-2-2** (선택) HTML 404 응답 시 404 템플릿 반환
- [ ] **13-2-3** (선택) 라우트 일괄 등록 리팩터링 완료

#### E2E·검증 (13-3)

- [ ] **13-3-1** 사용자 메뉴 6개 진입 E2E 통과
- [ ] **13-3-2** Admin 지식 6개 진입 E2E 통과
- [ ] **13-3-3** 메뉴 간 이동·404 시나리오 E2E 통과
- [ ] **13-3-4** 36개 시나리오↔E2E 매핑 문서 갱신

#### Backend Local LLM (13-5)

- [ ] **13-5-1** `/api/ask/stream`이 Ollama 토큰 생성 즉시 SSE 전달(True Streaming). TTFT 개선 확인
- [ ] **13-5-2** 토큰 계산이 tiktoken/transformers 기반으로 동작. ContextManager 한국어 친화·Context Window 초과 방어
- [ ] **13-5-3** Ollama `/api/chat`에서 `role: system` 활용. 후처리 정규식 축소·프롬프트 구조 문서화
- [ ] **13-5-4** (선택) 구조화 출력(format=json) 적용·프롬프트 주입 방어 검토 문서화

#### DB (13-4 선택)

- [ ] **13-4-1** (선택) 접근 로그 테이블·기록 로직 구현

### 7.2 KPI (참고)

| 지표 | 목표 |
|------|------|
| 메뉴 시나리오 36개 | E2E 또는 수동 검증 완료·결과 기록 |
| 라우트 1:1 대응 | 17개 path 200 OK (또는 인증 시 302 후 200) |
| NAV_MENU 참조 | 0건(제거) 또는 deprecated 1곳만 |
| Admin 공통 shell | 11페이지 동일 패턴 적용 |
| LLM True Streaming | TTFT 개선·SSE 즉시 전달 |
| LLM 토큰 관리 | 한글 환경 Context Window 초과 0건(목표) |

---

## 8. 예상 총 작업량

| 단계 | 예상 일수 |
|------|----------|
| Phase 13-1 Frontend 보완 | 1.5~2일 |
| Phase 13-2 Backend 보완 | 1~2일 |
| Phase 13-3 E2E·검증 확대 | 2.5~3일 |
| Phase 13-4 DB 선택 | 0~1일 |
| Phase 13-5 Local LLM 개선 | 3.5~4.5일 |
| **합계** | **약 8.5~12.5일** (13-4·13-5-4 선택 제외 시 약 8~11일) |

---

## 9. 리스크 관리

| ID | 리스크 | 영향도 | 대응 |
|----|--------|--------|------|
| R-001 | NAV_MENU 제거 시 외부 참조처 미발견 | 낮 | grep·빌드 후 회귀 테스트 |
| R-002 | 라우트 리팩터 시 경로 누락 | 중 | 13-2-1 문서·체크리스트로 사전 검증 |
| R-003 | E2E 확대로 인한 CI 시간 증가 | 낮 | 병렬·태그로 메뉴 E2E 분리 실행 |
| R-004 | 404 HTML 응답 시 API 404와 충돌 | 낮 | Accept 헤더 또는 경로로 HTML/API 구분 |
| R-005 | True Streaming 전환 시 기존 클라이언트 호환 | 중 | SSE 이벤트 형식 유지·프론트 ask/stream 소비부 검증 |
| R-006 | tiktoken/transformers 도입 시 의존성·메모리 증가 | 중 | 경량 옵션(tiktoken) 우선. 모델별 토크나이저 캐시 정책 |
| R-007 | System Prompt·후처리 축소 시 기존 답변 품질 변화 | 중 | A/B 비교 또는 회귀 테스트. 롤백 가능하도록 플래그 |

---

## 10. DB·Qdrant 요약

| 영역 | Phase 13 기본 범위 | 선택·비고 |
|------|---------------------|------------|
| **DB** | 스키마 변경 없음. audit_logs 등 기존 활용 | 13-4-1: 메뉴/페이지 접근 로그 테이블 도입(선택) |
| **Qdrant** | 컬렉션·인덱스 변경 없음 | 메뉴로 진입하는 페이지(search, knowledge, reason)의 API·Qdrant 연동 회귀 검증만 수행 |

---

**문서 상태**: 초안 (v1.1 — Local LLM 개선 부문 반영)  
**다음 단계**: Phase 13-1 착수 → `phase-13-1/` 폴더·status·plan·todo-list 생성. Phase 13-5는 메뉴(13-1~13-3) 완료 후 또는 병렬 착수 가능.  
**문서 위치**: `docs/phases/phase-13-master-plan.md`
