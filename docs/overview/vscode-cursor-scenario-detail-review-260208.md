# 프로젝트 소스 및 시나리오 디테일 리뷰 (vscode-cursor-scenario-detail-review-260208)

**비교 기준**: [docs/overview/vscode-overview-260208.md](docs/overview/vscode-overview-260208.md), [docs/overview/cursor-overview-260208.md](docs/overview/cursor-overview-260208.md)  
**소스 기준**: Backend/Frontend 실제 구현  
**작성일**: 2026-02-08

---

## 1. E2E 시나리오 추적 및 무결성 리뷰

### 1.1 관리자 메뉴(UI) → API 매핑 (시나리오 중심)

| 관리자 메뉴(UI) | Frontend 파일 | 호출 API (vscode-overview 기준) | 실제 호출 소스 | 결과 |
|---|---|---|---|---|
| 청크 승인 | [web/src/pages/admin/approval.html](web/src/pages/admin/approval.html) | `/api/approval/chunks/*` | [web/public/js/admin/admin-approval.js](web/public/js/admin/admin-approval.js) → `ChunkApprovalManager` in [web/public/js/admin/chunk-approval-manager.js](web/public/js/admin/chunk-approval-manager.js) | 정상 |
| 청크 승인 상세 | 동일 | `/api/approval/chunks/pending`, `/api/approval/chunks/{id}/approve`, `/api/approval/chunks/{id}/reject`, `/api/approval/chunks/batch/approve` | [web/public/js/admin/chunk-approval-manager.js](web/public/js/admin/chunk-approval-manager.js) | 정상 |
| 지식 통합(Integration) | **해당 UI 없음** | `/api/knowledge-integration/*` | Frontend 호출 소스 없음 | ⚠️ 주의 |

**요약**: 시나리오의 승인 단계는 UI→API→Backend 라우터 연결이 명확히 존재합니다. 다만 “통합(Integration)” 단계는 UI/JS에 호출 경로가 없어 E2E 시나리오로 연결되지 않습니다.

### 1.2 승인 → 통합 흐름의 백엔드 논리 순서

| 단계 | 기대 흐름(논리) | 실제 구현 상태 | 결과 |
|---|---|---|---|
| 1 | 승인 대기 청크 조회 | `GET /api/approval/chunks/pending` in [backend/routers/knowledge/approval.py](backend/routers/knowledge/approval.py) | 정상 |
| 2 | 청크 승인/거부 처리 | `POST /api/approval/chunks/{id}/approve` 및 배치 승인 | 정상 |
| 3 | 승인 후 지식 통합 수행 | `POST /api/knowledge-integration/integrate` in [backend/routers/knowledge/knowledge_integration.py](backend/routers/knowledge/knowledge_integration.py) | **승인 라우터에서 통합 호출 없음** | ⚠️ 주의 |
| 4 | 통합 결과 검증(모순 감지/해결) | `/api/knowledge-integration/contradictions/*` | **UI/승인 흐름과 연결 없음** | ⚠️ 주의 |

**해석**: 현재 승인 로직은 승인 처리까지만 수행하며, 지식 통합은 별도 API로 분리된 상태입니다. 승인 후 통합이 자동 실행되도록 설계된 호출 흐름은 소스에서 확인되지 않습니다.

### 1.3 경로 불일치가 통신 오류를 일으킬 가능성

| 항목 | 문서 표기 | 실제 라우터 | 영향 | 결과 |
|---|---|---|---|---|
| 지식 통합 API | vscode-overview: `/api/knowledge/integration/duplicate` | 실제: `/api/knowledge-integration/*` | **문서 기반 호출 시 404 가능** | ⚠️ 주의 |

**분석**: 프론트엔드에서 해당 경로를 직접 호출하는 코드가 현재는 없어 실제 장애로 이어지지는 않지만, 문서/개발자가 이를 참조해 구현할 경우 오류 가능성이 큽니다.

---

## 2. Admin 설정 데이터 흐름(Data Flow) 및 묶음 리뷰

### 2.1 단계별 Model → Router → UI 매핑

| 단계 | Backend 모델 | Backend 라우터 | Frontend HTML | Frontend JS | 결과 |
|---|---|---|---|---|---|
| schemas | `AdminSchema` in [backend/models/admin_models.py](backend/models/admin_models.py) | [backend/routers/admin/schema_crud.py](backend/routers/admin/schema_crud.py) | [web/src/pages/admin/settings/templates.html](web/src/pages/admin/settings/templates.html) | [web/public/js/admin/settings/templates.js](web/public/js/admin/settings/templates.js) | 정상 |
| templates | `AdminTemplate` in [backend/models/admin_models.py](backend/models/admin_models.py) | [backend/routers/admin/template_crud.py](backend/routers/admin/template_crud.py) | [web/src/pages/admin/settings/templates.html](web/src/pages/admin/settings/templates.html) | [web/public/js/admin/settings/templates.js](web/public/js/admin/settings/templates.js) | 정상 |
| presets | `AdminPromptPreset` in [backend/models/admin_models.py](backend/models/admin_models.py) | [backend/routers/admin/preset_crud.py](backend/routers/admin/preset_crud.py) | [web/src/pages/admin/settings/presets.html](web/src/pages/admin/settings/presets.html) | [web/public/js/admin/settings/presets.js](web/public/js/admin/settings/presets.js) | 정상 |
| rag_profiles | `AdminRagProfile` in [backend/models/admin_models.py](backend/models/admin_models.py) | [backend/routers/admin/rag_profile_crud.py](backend/routers/admin/rag_profile_crud.py) | [web/src/pages/admin/settings/rag-profiles.html](web/src/pages/admin/settings/rag-profiles.html) | [web/public/js/admin/settings/rag-profiles.js](web/public/js/admin/settings/rag-profiles.js) | 정상 |
| policy_sets | `AdminPolicySet` in [backend/models/admin_models.py](backend/models/admin_models.py) | [backend/routers/admin/policy_set_crud.py](backend/routers/admin/policy_set_crud.py) | [web/src/pages/admin/settings/policy-sets.html](web/src/pages/admin/settings/policy-sets.html) | [web/public/js/admin/settings/policy-sets.js](web/public/js/admin/settings/policy-sets.js) | 정상 |
| audit_logs | `AdminAuditLog` in [backend/models/admin_models.py](backend/models/admin_models.py) | [backend/routers/admin/audit_log_crud.py](backend/routers/admin/audit_log_crud.py) | [web/src/pages/admin/settings/audit-logs.html](web/src/pages/admin/settings/audit-logs.html) | [web/public/js/admin/settings/audit-logs.js](web/public/js/admin/settings/audit-logs.js) | 정상 |

### 2.2 데이터 흐름 문서 일치성 검토

| 항목 | cursor-overview 6.1 | vscode-overview 5.2 | 소스 상태 | 결과 |
|---|---|---|---|---|
| schemas → templates → presets → rag_profiles → policy_sets | 있음 | 있음(구성 파일 목록) | 라우터/JS 모두 존재 | 정상 |
| context_rules | 없음 | 없음 | 모델만 존재 (router/UI 없음) | ⚠️ 주의 |

**해석**: Admin 설정의 핵심 5단계는 문서와 소스 모두 일치합니다. 다만 `context_rules`는 DB 모델만 존재하며 라우터·UI가 없어 문서에도 누락된 상태입니다.

### 2.3 policy_sets 변경이 AI 응답에 즉시 반영되는가?

| 점검 항목 | 확인 결과 | 근거 | 결과 |
|---|---|---|---|
| `policy_sets`가 AI 응답 로직에 참조되는가 | 참조 코드 없음 | [backend/routers/ai/ai.py](backend/routers/ai/ai.py) 및 services에서 `AdminPolicySet` 참조 미확인 | ⚠️ 주의 |

**결론**: 현재 `policy_sets` 변경이 AI 응답에 즉시 반영되는 구조는 확인되지 않습니다. Admin 설정은 CRUD 기능 중심으로 구성되어 있으며, AI 응답 파이프라인과의 연결은 별도 구현이 필요합니다.

---

## 3. 운영(Ops) 시나리오 및 예외 처리 리뷰

### 3.1 헬스체크/로그 API 연결성

| 항목 | 문서 표기 | 실제 라우터/소스 | 결과 |
|---|---|---|---|
| 헬스체크 | `/api/system/health` | 실제는 `/health` in [backend/main.py](backend/main.py) | ⚠️ 주의 |
| 시스템 상태 | `/api/system/*` | `/api/system/status`, `/api/system/info` in [backend/routers/system/system.py](backend/routers/system/system.py) | 정상 |
| 로그 조회 | `/api/logs` | [backend/routers/system/logs.py](backend/routers/system/logs.py) | 정상 |
| 에러 로그 | `/api/error-logs` | [backend/routers/system/error_logs.py](backend/routers/system/error_logs.py) | 정상 |

**해석**: 헬스체크 경로가 문서와 실제 소스가 다릅니다. 운영 문서에서 `/health`로 수정 필요합니다.

### 3.2 사용자 메뉴 에러 발생 시 감사 로그/에러 로그 연계

| 항목 | 기대 흐름 | 소스 확인 | 결과 |
|---|---|---|---|
| 사용자 오류 → 감사 로그 | UI 이벤트가 `/api/admin/audit-logs`로 연결 | 감사 로그는 Admin 설정 CRUD에 의해 기록됨. 사용자 메뉴 오류와 자동 연계 없음 | ⚠️ 주의 |
| 사용자 오류 → 에러 로그 UI 노출 | 에러 로그 UI/페이지 존재 | 에러 로그 API는 존재하나 UI 페이지 없음 | ⚠️ 주의 |

**해석**: 감사 로그는 Admin 설정 변경 기록용이며, 사용자 오류와 자동 연계되는 구조는 확인되지 않습니다. 에러 로그 UI는 문서에도 없고 실제 페이지도 없습니다.

### 3.3 백업/복원 UI 누락에 대한 개선 방향

| 항목 | 현재 상태 | 권장 추가 위치 | 수정 방향 | 결과 |
|---|---|---|---|---|
| 백업/복원 UI | API만 존재 (`/api/system/backup*`) | 신규 페이지: web/src/pages/admin/backup.html | 백업 목록/생성/복원 버튼 UI + JS에서 `/api/system/backup`, `/api/system/backup{s}`, `/api/system/restore` 호출 | ⚠️ 주의 |
| 백업 검증 UI | API만 존재(문서 기준) | 신규 페이지: web/src/pages/admin/backup.html 또는 admin/statistics 확장 | 검증 버튼 추가 + 결과 표시 패널 | ⚠️ 주의 |
| 에러 로그 UI | API만 존재 (`/api/error-logs`) | 신규 페이지: web/src/pages/admin/error-logs.html | `/api/error-logs` 호출 리스트/필터 UI | ⚠️ 주의 |

---

## 4. 통합 테스트 가이드와 소스 정합성 리뷰

### 4.1 테스트 가이드 기능 단위 vs 소스 구조

| devtest 가이드 단위 | 실제 소스 구조 | 일치 여부 | 결과 |
|---|---|---|---|
| 11-1(DB) | admin 모델(스키마/템플릿/프리셋/RAG/정책/감사 로그) | 일치 | 정상 |
| 11-2(API) | admin CRUD 라우터 5종 + audit 로그 | 일치 | 정상 |
| 11-3(UI) | admin/settings 5페이지 + audit-logs | 일치 | 정상 |
| 11-2-4 정책 해석 resolve | 문서에는 설계/구현 언급, 소스에서 확인 어려움 | 구현 흔적 부족 | ⚠️ 주의 |

### 4.2 Reasoning 결과 조회 → 무결성 검사 연계

| 점검 항목 | 기대 | 실제 | 결과 |
|---|---|---|---|
| Reasoning 결과 조회 시 무결성 검사 호출 | `/api/integrity/check` 연계 | Reasoning 라우터/프론트엔드에서 무결성 호출 없음 | ⚠️ 주의 |

### 4.3 테스트 문서에는 있으나 개요 문서에 없는 기능(숨겨진 기능)

| 기능/엔드포인트 | 위치 | 문서 누락 | 결과 |
|---|---|---|---|
| `/api/system/status`, `/api/system/info`, `/api/system/work-log` | [backend/routers/system/system.py](backend/routers/system/system.py) | cursor/vscode 개요에 없음 | ⚠️ 주의 |
| `/api/system/test/gpt4all`, `/api/system/test/venv-packages` | [backend/routers/system/system.py](backend/routers/system/system.py) | 개요 문서에 없음 | ⚠️ 주의 |
| `/api/logs/stats` | [backend/routers/system/logs.py](backend/routers/system/logs.py) | 개요 문서에 없음 | ⚠️ 주의 |
| `/api/error-logs/stats` | [backend/routers/system/error_logs.py](backend/routers/system/error_logs.py) | 개요 문서에 없음 | ⚠️ 주의 |
| `/api/integrity/sync`, `/api/integrity/consistency`, `/api/integrity/fix/*` | [backend/routers/system/integrity.py](backend/routers/system/integrity.py) | 개요 문서에 없음 | ⚠️ 주의 |
| `/api/reason/eta`, `/api/reason/eta/feedback`, `/api/reason/tasks` | [backend/routers/reasoning/reason_stream.py](backend/routers/reasoning/reason_stream.py) | 개요 문서에 없음 | ⚠️ 주의 |

---

## 5. 종합 결론 및 우선 조치

| 우선순위 | 항목 | 조치 요약 | 결과 |
|---|---|---|---|
| 높음 | 지식 통합 경로 불일치 | vscode-overview의 `/api/knowledge/integration/duplicate`를 `/api/knowledge-integration/*`로 정정 | ⚠️ 주의 |
| 높음 | 승인→통합 흐름 단절 | 승인 처리 이후 통합 API 호출 연계(서비스/프론트) 설계 필요 | ⚠️ 주의 |
| 중간 | 헬스체크 경로 불일치 | `/api/system/health` → `/health`로 문서 수정 | ⚠️ 주의 |
| 중간 | 운영 UI 미존재 | 백업/에러로그/무결성 UI 신규 추가 또는 기존 페이지 확장 | ⚠️ 주의 |
| 낮음 | 숨겨진 API 문서화 | system/integrity/logs/reasoning 추가 엔드포인트 문서 보완 | ⚠️ 주의 |

---

**작성일**: 2026-02-08
