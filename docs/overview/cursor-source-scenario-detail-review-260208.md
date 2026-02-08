# 프로젝트 소스 및 시나리오 디테일 리뷰

**작성일**: 2026-02-08  
**대상**: E2E 시나리오 추적, Admin 데이터 흐름, 운영 시나리오, 통합 테스트 가이드 vs 소스 정합성  
**참조 문서**: cursor-overview-260208.md, vscode-overview-260208.md, vscode-cursor-comparison-report-260208.md

---

## 1. E2E(End-to-End) 시나리오 추적 및 무결성 리뷰

**검토 시나리오:** "관리자가 지식 승인(Approval)을 진행하고 이를 지식 베이스에 통합(Integration)하는 과정"

### 1.1 cursor 2.2 관리자 메뉴 UI → vscode 명시 API 매핑

| cursor 2.2 메뉴 | Frontend (HTML) | Frontend JS (실제 호출) | 호출 API (vscode 명시) | Backend 라우터 | 일치 |
|-----------------|-----------------|-------------------------|-------------------------|----------------|------|
| 청크 승인 | `admin/approval.html` | `chunk-approval-manager.js` | `/api/approval/chunks/pending`, `/api/approval/chunks/{id}/approve`, `/api/approval/chunks/batch/approve`, `/api/approval/chunks/{id}/reject` | `backend/routers/knowledge/approval.py` | ✅ |
| 청크 승인 상세 | 동일 | 동일 | `/api/knowledge/chunks/{id}`, `/api/knowledge/relations/suggest`, `/api/knowledge/labels/suggest-llm`, `/api/knowledge/labels/suggest/{id}/apply/{labelId}` | `knowledge/knowledge.py`, `relations.py`, `suggestions.py` | ✅ |
| 지식 관리(승인 연계) | `knowledge/knowledge-admin.html` | `knowledge-admin.js` → `ChunkApprovalManager`, `LabelManager` | `/api/approval/chunks`, `/api/knowledge/chunks`, `/api/labels` | 동일 | ✅ |
| 키워드/라벨/청크 생성/청크 라벨 | `admin/groups.html`, `labels.html`, `chunk-create.html`, `chunk-labels.html` | 각 admin/*.js | `/api/labels`, `/api/knowledge/*`, ingest | `labels.py`, `knowledge.py`, `file_parser` | ✅ |

**요약**: 관리자 메뉴에서 사용하는 UI 파일들이 호출하는 API는 vscode-overview에 명시된 엔드포인트와 **일치**하며, 모두 `backend/routers/knowledge/` 및 `approval.py`로 연결됨.

### 1.2 approval.py ↔ knowledge_integration.py 시나리오 내 순서·역할

| 단계 | 라우터/소스 | 역할 | 시나리오 상 순서 |
|------|-------------|------|-------------------|
| 1 | `approval.py` | 승인 대기 목록 조회 `GET /api/approval/chunks/pending` | 1 |
| 2 | `approval.py` | 단일/일괄 승인 `POST .../approve`, 거절 `POST .../reject` | 2 |
| 3 | `approval.py` (내부) | 청크 `status = "approved"`, `approved_at`, `approved_by` 갱신, DB commit | 3 |
| 4 | (선택) `approval.py` | `suggest_relations=True` 시 `structure_matcher.suggest_relations_on_approve(chunks[0])` 호출 → 관계 추천 반환 | 4 |
| 5 | **지식 통합** | `knowledge_integration.py`: `POST /api/knowledge-integration/integrate` (chunk_ids, strategy) — **현재 프론트엔드에서 호출 없음** | 5 (설계상; UI 연동 없음) |

**논리적 흐름 정리**:
1. **승인(approval.py)**: 관리자가 청크를 승인하면 DB에서 해당 청크의 `status`가 `approved`로 바뀜. 이미 “지식 베이스에 포함 가능한 상태”로 전환됨.
2. **통합(knowledge_integration.py)**: 여러 청크를 전략(merge/prioritize/resolve)에 따라 “통합”하는 별도 API. 모순 감지(`/contradictions/detect`), 세계관 구성(`/worldview`) 등 고급 기능 제공.
3. **현재 구현**: 승인만으로도 청크는 검색/지식 그래프에 활용 가능. **통합(Integration) API는 백엔드만 존재하고, Admin/지식 UI에서 호출하는 코드가 없음.** 따라서 “승인 → (선택) 통합” 중 “통합” 단계는 **자동으로 이어지지 않음**.

### 1.3 경로 불일치(⚠️ /api/knowledge-integration)와 통신 오류 가능성

| 항목 | 비교 리포트 지적 | 소스 관점 분석 |
|------|------------------|----------------|
| **Prefix** | cursor 3.1에 `/api/knowledge-integration` 기재, vscode 5.4에 knowledge_integration 파일 경로만 있음 | `knowledge_integration.py`는 `prefix="/api/knowledge-integration"` 사용. **경로 자체는 일치.** |
| **프론트엔드 호출** | - | `web/` 전체에서 `knowledge-integration`, `integrate`, `contradictions`, `worldview` **검색 결과 0건**. 즉, **어떤 UI도 `/api/knowledge-integration`을 호출하지 않음.** |
| **통신 오류 가능성** | “경로 불일치로 인한 오류” | **경로 불일치로 인한 4xx/5xx는 없음.** 다만 “지식 통합” 시나리오를 **UI에서 실행하려면** 프론트엔드에 `/api/knowledge-integration/integrate` (및 필요 시 detect/resolve) 호출을 **추가**해야 함. 현재는 해당 시나리오가 **UI에 없어서** “실행 자체가 안 됨”에 가깝다. |

**결론**: `/api/knowledge-integration` 경로는 백엔드와 문서 간 **일치**한다. 다만 **승인 → 통합** E2E를 “관리자 UI에서 끝까지” 수행하려면, 승인 완료 후 “통합” 버튼/플로우에서 `POST /api/knowledge-integration/integrate`를 호출하는 프론트엔드 수정이 필요하다.

---

## 2. Admin 설정 데이터 흐름(Data Flow) 및 묶음 리뷰

### 2.1 단계별 [백엔드 모델 - 라우터 - 프론트엔드 HTML] 묶음

| 단계 | 백엔드 모델 (admin_models.py) | 라우터 (backend/routers/admin/) | API Prefix | 프론트엔드 HTML | 비고 |
|------|-------------------------------|-----------------------------------|------------|-----------------|------|
| schemas | `AdminSchema` | `schema_crud.py` | `/api/admin/schemas` | `admin/settings/templates.html` (스키마·템플릿 동시 편집) | ✅ |
| templates | `AdminTemplate` | `template_crud.py` | `/api/admin/templates` | `admin/settings/templates.html` | ✅ |
| presets | `AdminPromptPreset` | `preset_crud.py` | `/api/admin/presets` | `admin/settings/presets.html` | ✅ |
| rag_profiles | `AdminRagProfile` | `rag_profile_crud.py` | `/api/admin/rag-profiles` | `admin/settings/rag-profiles.html` | ✅ |
| policy_sets | `AdminPolicySet` | `policy_set_crud.py` | `/api/admin/policy-sets` | `admin/settings/policy-sets.html` | ✅ |
| audit_logs | `AdminAuditLog` | `audit_log_crud.py` | `/api/admin/audit-logs` | `admin/settings/audit-logs.html` | ✅ (조회 전용) |

**참고**: DB 테이블명은 `prompt_presets`(모델은 AdminPromptPreset), API는 `presets`로 노출됨. cursor 6.1의 “presets”와 vscode 5.2의 “preset_crud”와 **일치**.

### 2.2 cursor 6.1 데이터 순서 vs vscode 5.2 소스 구조·UI 메뉴

| cursor 6.1 순서 | vscode 5.2 파일 나열 | UI 메뉴 (cursor 2.3) | 소스상만 있고 UI에 없는 항목 |
|-----------------|----------------------|------------------------|------------------------------|
| schemas → templates → presets → rag_profiles → policy_sets → audit_logs | schema_crud, template_crud, preset_crud, rag_profile_crud, policy_set_crud, audit_log_crud | 템플릿(스키마 포함), 프리셋, RAG 프로필, 정책, 변경 이력 | **없음** — 6종 모두 UI에 있음. |

**결론**: cursor 6.1의 데이터 순서와 vscode 5.2 소스 구조·cursor 2.3 설정 메뉴는 **100% 일치**하며, 소스에만 있고 UI에 누락된 설정 항목은 **없음**.

### 2.3 policy_sets(또는 기타 설정) 수정 시 AI 응답 반영 구조

| 질문 | 소스 분석 결과 |
|------|----------------|
| policy_sets 수정 시 `backend/routers/ai/ai.py`에 즉시 반영되는가? | **아니오.** `ai/ai.py` 내에서 `policy_set`, `policy_sets`, `rag_profile`, `template`, `preset` 등 **Admin 설정 테이블을 조회하는 코드가 없음.** (grep 결과 0건) |
| AI 응답 생성 경로 | `ai.py` → `get_multi_hop_rag()` 등 검색·RAG 서비스 사용. **프롬프트/정책은 코드 내 상수·하드코딩 또는 요청 파라미터로만 사용**되는 구조로 보임. |
| 참조 관계 | Admin CRUD는 `admin_models.py`의 `AdminPolicySet`, `AdminTemplate` 등을 사용하나, **ai 라우터나 AI 서비스가 이 모델들을 import하거나 읽지 않음.** |

**결론**: 현재 소스 기준으로 **특정 설정(policy_sets, templates, rag_profiles 등)을 Admin에서 수정해도, AI 응답 기능(ai.py)에는 자동 반영되지 않는다.** 즉시 반영하려면 ai 라우터/서비스에서 해당 설정을 DB 또는 캐시에서 읽어 오도록 **추가 연동**이 필요하다.

---

## 3. 운영(Ops) 시나리오 및 예외 처리 리뷰

### 3.1 헬스체크·로그 API와 main.py·미들웨어 연결

| vscode 9.4 항목 | 실제 소스 위치 | 연결 관계 |
|-----------------|----------------|-----------|
| **헬스체크** | `main.py`: `@app.get("/health")` → `{"status": "ok"}` | **주의**: vscode에는 `/api/system/health`로 기재되어 있으나, **실제 구현은 루트 `/health`**. `backend/routers/system/system.py`에는 `/status`, `/info`만 있고 `/health` 없음. LB/배포 검사 시 **`/health`** 사용해야 함. |
| **로그** | `backend/routers/system/logs.py` → prefix `/api/logs` | `main.py`에서 `app.include_router(logs.router)` 등록. ✅ |
| **에러 로그** | `backend/routers/system/error_logs.py` → prefix `/api/error-logs` | `main.py`에서 `app.include_router(error_logs.router)` 등록. ✅ |

**요약**: 헬스체크는 **문서를 `/health`로 수정**하거나, `/api/system/health`를 system 라우터에 추가하는 것이 좋음. 로그/에러 로그 API는 main과 **정상 연결**됨.

### 3.2 사용자 메뉴 에러 발생 시 감사 로그·에러 로그 UI 전달 여부

| 경로 | 소스 존재 여부 | 비고 |
|------|----------------|------|
| **감사 로그 (Admin 설정 변경 이력)** | `GET /api/admin/audit-logs` → `audit_log_crud.py` (조회 전용). `admin/settings/audit-logs.html`에서 호출 | Admin **설정 CRUD** 시 이력을 **DB에 기록**하는 코드는 **별도로 검색되지 않음.** `deps.log_crud_action()`은 **Python logger.info()만 수행**하며, `audit_logs` 테이블에 insert하지 않음. 따라서 **현재 구조로는 “사용자 메뉴에서 발생한 일반 에러”가 감사 로그로 자동 전달되지 않음.** |
| **에러 로그 UI** | `backend/routers/system/error_logs.py` → 파일(`errors.jsonl`) 기반 조회. **에러 로그 전용 UI 페이지**는 `web/src/pages/`에 **없음.** `logs.html`은 `/api/logs`(작업 로그)만 사용 | **주의**: “에러 로그 UI”는 **문서/메뉴에는 있을 수 있으나**, 현재 **전용 페이지는 없음.** 에러는 `logging_service` 등에서 `errors.jsonl`에 기록되며, API로만 조회 가능. |

**결론**: 사용자 메뉴에서 에러가 나도, 그 자체가 **감사 로그(Audit Log)나 에러 로그 UI로 자동 전달되는 로직은 없음.** 감사 로그는 “Admin 설정 변경” 이력을 담는 용도로 설계되어 있으며, 그 **기록(insert) 경로**도 코드상 명확히 보이지 않음(트리거 또는 미구현 가능성). 에러 로그는 **API만 있고**, 이를 보여주는 **전용 UI 페이지는 없음.**

### 3.3 백업/복원 UI 누락 — 프론트엔드 수정 추천

| 항목 | 내용 |
|------|------|
| **현재 상태** | 백업/복원 API는 `backend/routers/system/backup.py`에만 존재. `web/src/pages/` 아래에 **backup.html, admin/backup.html 등 백업·복원 전용 페이지 없음.** |
| **추가할 프론트엔드 위치** | 1) **`web/src/pages/admin/backup.html`** (관리자 메뉴 하위에 백업/복원 배치) 또는 2) **`web/src/pages/logs.html`** 확장(로그·에러·백업을 한 “시스템” 페이지로 통합) |
| **수정 방향** | 1) **신규 페이지 권장**: `admin/backup.html` 생성 후, `web/public/js/admin/backup.js`에서 **`POST /api/system/backup`**(백업 생성), **`GET /api/system/backup/s`**(목록; 코드 오타로 `"s"`일 수 있음 → 실제 경로 확인 필요), **`POST /api/system/backup/restore`**(body: `backup_name`, `confirm`) 호출. 2) **라우팅**: `main.py`의 HTML 라우팅에 `/admin/backup` → `admin/backup.html` 추가. 3) **메뉴**: `header-component.js` 등에서 관리자 메뉴에 “백업/복원” 항목 추가. 4) **레거시**: 문서화된 `/api/backup/create`, `/api/backup/list` 등은 레거시이므로, 신규 API(`/api/system/backup`) 기준으로 UI 구현 권장. |

---

## 4. 통합 테스트 가이드와 소스 정합성 리뷰

### 4.1 devtest README·시나리오 vs vscode 소스 트리 구조

| 테스트 가이드 (docs/devtest/) | vscode-overview 소스 트리 | 일관성 |
|-------------------------------|---------------------------|--------|
| Phase 11-1(DB), 11-2(API), 11-3(Admin UI) Task 단위 시나리오 | `backend/routers/admin/*_crud.py`, `web/src/pages/admin/settings/*.html` | ✅ 기능 단위와 Task가 대응됨. |
| Task당 최대 20가지 시나리오, 시나리오 ID (11-1-1-S01 등) | 소스는 “기능별”로만 나뉨. 테스트 단위와 소스 단위가 **동일하지는 않으나**, Phase 11-1~11-3 범위와 소스 구조는 **일관**됨. | ✅ |
| integration-test-guide §6 Phase 11 Task 목록 | vscode 5.2 Admin 파일 목록(schema, template, preset, rag_profile, policy_set, audit_log) | ✅ 1:1 대응. |

**결론**: 테스트 가이드에서 정의한 **기능 단위(Task)**와 vscode-overview의 **소스 트리 구조**는 **일관되게 분리**되어 있음.

### 4.2 Phase 10 Reasoning ↔ 데이터 무결성 검사(api/integrity/check) 연계

| 질문 | 소스 수준 연계 |
|------|----------------|
| Reasoning 결과 조회 시 `api/integrity/check`를 거치도록 설계되어 있는가? | **아니오.** `backend/routers/reasoning/reasoning_results.py` 및 관련 서비스에서 **integrity 라우터나 integrity_service를 호출하지 않음.** `backend/routers/system/integrity.py`는 **별도** 무결성 검사용 API(`GET /api/integrity/check`, `/sync`, `/consistency` 등)만 제공. |
| 설계 의도 | Reasoning “결과” 조회는 **무결성 검사 없이** DB/캐시에서 바로 조회. 무결성 검사는 **운영/점검 시** 수동 또는 스케줄로 호출하는 용도로 보임. |

**결론**: Phase 10 Reasoning 소스가 **추론 결과 조회 시** `api/integrity/check`를 **자동으로 거치도록 설계되어 있지 않음.** 테스트 문서에서 “무결성 검사를 거치도록 설계”라고 되어 있다면, **현재 구현과 불일치**하거나 “운영 절차” 수준의 권장사항으로 보는 것이 맞음.

### 4.3 테스트 문서에는 있으나 개요 문서(vscode/cursor)에 없는 숨겨진 기능·파일

| 구분 | 항목 | 비고 |
|------|------|------|
| **devtest** | `integration-test-guide.md` §7 Phase 10 회귀·Phase 11 연동, `phase-10-regression-scenarios.md`, `phase-11-5/regression-e2e-phase11-scenarios.md` | 개요 문서에는 “Phase 10 회귀·11-5-7” 요약만 있고, **시나리오 파일 경로·이름**은 cursor 7.2(webtest) 등에 일부만 등장. |
| **숨겨진/미언급 기능** | 1) **`/api/knowledge-integration`** 전체 (integrate, contradictions/detect·resolve, worldview) — vscode 5.4에 파일 경로만 있고, cursor 3.1에는 prefix만 있음. **어떤 UI에서 쓰는지 개요에 없음.** 2) **`/api/integrity/*`** 하위 경로 (`/sync`, `/consistency`, `fix/orphan-*`) — vscode에는 `/api/integrity/check`만 나옴. 3) **`/health`** — 실제는 루트 `/health`인데 vscode 9.4는 `/api/system/health`로 기재. |
| **파일** | `web/src/pages/knowledge-admin.html.backup` — 백업 파일이므로 “기능”은 아니나, 목록에 없음. `e2e/phase-*.spec.js` 존재 여부는 개요에 없음. | 테스트 가이드 4.1에서는 E2E spec 파일 위치(`e2e/phase-{X-Y}.spec.js`)를 명시. |

**요약**: 테스트 문서에만 정의되어 있고 두 개요 문서에는 **언급이 없거나 짧은** 항목 — **knowledge-integration API 용도**, **integrity 하위 경로**, **실제 헬스체크 경로(/health)**. 이들을 개요 문서에 반영하면 정합성이 높아짐.

---

## 5. 종합 표 (요약)

| 영역 | 일치/구현됨 | 주의/보완 필요 |
|------|-------------|----------------|
| **1. 승인→통합 E2E** | UI→API→approval.py 매핑 일치; approval.py 내부 흐름 명확 | 통합 단계: UI에서 `/api/knowledge-integration` 호출 없음 → 프론트 추가 필요 |
| **2. Admin 데이터 흐름** | schemas~audit_logs 6종 모델-라우터-HTML 일치; UI 누락 없음 | policy_sets 등 설정 변경이 ai.py에 반영되지 않음 → 연동 설계 필요 |
| **3. 운영** | 로그/에러 로그 API는 main과 연결됨 | 헬스체크: 실제 `/health` vs 문서 `/api/system/health` 불일치; 감사 로그 insert 경로 불명; 에러 로그 전용 UI 없음; 백업/복원 UI 없음 → admin/backup.html 등 추가 권장 |
| **4. 통합 테스트** | Phase 11 Task와 소스 구조 일관됨 | Reasoning 결과 조회 시 integrity/check 자동 경유 아님; knowledge-integration·integrity 하위·/health 등 “숨겨진” 기능은 개요에 보강 권장 |

---

**작성일**: 2026-02-08
