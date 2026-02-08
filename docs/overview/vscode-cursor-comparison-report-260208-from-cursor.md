# vscode-overview vs cursor-overview 세부 비교·분석 리포트

**작성일**: 2026-02-08  
**대상 문서**: `vscode-overview-260208.md`, `cursor-overview-260208.md`  
**목적**: 구조·엔드포인트 일치성, 메뉴 흐름, 설정값, 누락 기능·다음 단계 정리

---

## 1. 구조 및 엔드포인트 일치성 검토

### 1.1 Backend API: vscode (파일 경로) vs cursor (API Prefix) 대조

| vscode-overview (파일 경로) | cursor-overview (API Prefix) | 일치 | 비고 |
|-----------------------------|------------------------------|------|------|
| `backend/routers/auth/auth.py` | `/api/auth` | ✅ | - |
| `backend/routers/search/search.py`, `documents.py` | `/api/search`, `/api/documents` | ✅ | - |
| `backend/routers/ai/ai.py`, `conversations.py` | `/api/ask`, `/api/conversations` | ✅ | - |
| `backend/routers/reasoning/reason*.py`, `reason_store.py`, `reasoning_results.py`, `recommendations.py` | `/api/reason`, `/api/reasoning-results`, `/api/reason/recommendations` | ✅ | - |
| `backend/routers/knowledge/*.py` (knowledge, labels, relations, approval, suggestions, knowledge_integration) | `/api/knowledge`, `/api/labels`, `/api/relations`, `/api/approval/chunks`, `/api/knowledge-integration` | ✅ | - |
| `backend/routers/admin/*.py` (schema, template, preset, rag_profile, policy_set, audit_log) | `/api/admin/*` | ✅ | Phase 11 동일 반영 |
| `backend/routers/cognitive/*.py` | `/api/context`, `/api/memory`, `/api/learning`, `/api/personality`, `/api/metacognition` | ✅ | - |
| `backend/routers/system/*.py` (system, backup, logs, error_logs, statistics, integrity) | `/api/system`, `/api/logs`, `/api/error-logs`, `/api/integrity` | ✅ | - |
| `backend/routers/automation/*.py`, `workflow.py` | `/api/automation`, `/api/workflow` | ✅ | - |
| `backend/routers/ingest/file_parser.py` | `/api/file-parser` | ✅ | - |

### 1.2 Phase 11 (Admin 설정) 라우터 양쪽 문서 반영 여부

| Admin 기능 | vscode-overview | cursor-overview | 일치 |
|------------|-----------------|-----------------|------|
| Role 스키마 | `admin/schema_crud.py` + `/api/admin/schemas` | `/api/admin/*` (schemas, templates) | ✅ |
| 템플릿 | `admin/template_crud.py` + `/api/admin/templates` | `/api/admin/templates` | ✅ |
| 프리셋 | `admin/preset_crud.py` + `/api/admin/presets` | `/api/admin/presets` | ✅ |
| RAG 프로필 | `admin/rag_profile_crud.py` + `/api/admin/rag-profiles` | `/api/admin/rag-profiles` | ✅ |
| 정책 세트 | `admin/policy_set_crud.py` + `/api/admin/policy-sets` | `/api/admin/policy-sets` | ✅ |
| 감사 로그 | `admin/audit_log_crud.py` + `/api/admin/audit-logs` | `/api/admin/audit-logs` | ✅ |

**결론**: Phase 11 Admin 관련 라우터·엔드포인트는 두 문서에 **동일하게** 반영되어 있음.

### 1.3 불일치·주의 사항 (API·경로)

| 구분 | vscode-overview | cursor-overview | 주의 |
|------|-----------------|-----------------|------|
| 백업 API | `/api/system/backup`, `/api/system/backup/s`, `/api/system/backup/restore` (신규) | `curl /api/backup/create`, `/api/backup/list`, `/api/backup/restore/{backup_id}` (레거시만 기재) | **주의**: cursor는 레거시 경로만 예시로 사용. vscode 기준 신규는 `/api/system/backup` 계열. cursor 6.3에 신규 경로 보완 권장. |
| 통계 API | `/api/system/statistics` (루트; /documents, /knowledge 등) | `/api/system/statistics`, `/api/system/statistics/dashboard` (6.7 예시) | **주의**: vscode에는 `/dashboard` 경로 없음. 실제 코드는 `GET ""`, `GET /documents` 등. cursor의 `/dashboard`는 **존재하지 않을 수 있음** → 코드 확인 필요. |
| suggestions | vscode: `/api/suggestions/labels`, `/api/knowledge/integration/duplicate` | cursor: Prefix 표에 suggestions 미기재 | **주의**: cursor 3.1 테이블에 `/api/knowledge`만 있고 suggestions·knowledge-integration 하위 경로는 생략됨. 누락 아님(같은 knowledge 라우터). |

---

## 2. 사용자/관리자 메뉴 흐름(Flow) 분석

### 2.1 cursor "2.2 관리자 메뉴" vs vscode "9. 관리자 프로그램 리뷰 체크리스트" 대조

| cursor (메뉴·경로·API) | vscode 체크리스트 항목 | UI↔Backend 연결 | 비고 |
|------------------------|------------------------|------------------|------|
| 키워드 관리 `/admin/groups` → `/api/labels` | - | ✅ `backend/routers/knowledge/labels.py` | 체크리스트에는 "Admin UI 진입점"만 있고 메뉴별 매핑은 없음. |
| 라벨 관리 `/admin/labels` → `/api/labels` | - | ✅ 동일 | - |
| 청크 생성 `/admin/chunk-create` → `/api/knowledge`, ingest | - | ✅ knowledge + file-parser | - |
| 청크 승인 `/admin/approval` → `/api/approval/chunks` | 접근 제어·감사 | ✅ `backend/routers/knowledge/approval.py` | **일치** |
| 청크 관리 `/admin/chunk-labels` → `/api/knowledge`, `/api/labels` | - | ✅ | - |
| 통계 `/admin/statistics` → `/api/system/statistics` | 운영·모니터링: `admin/statistics.html` | ✅ `backend/routers/system/statistics.py` | **일치** |
| 설정: templates, presets, rag-profiles, policy-sets, audit-logs | 9.1~9.5 전반 (접근 제어, 감사, 백업, 모니터링, 보안) | ✅ `/api/admin/*` | **일치** |

### 2.2 체크리스트에 있으나 메뉴 목차에서 별도 노출이 약한 항목

| vscode 체크리스트 항목 | cursor 메뉴/문서 반영 | 주의 |
|------------------------|------------------------|------|
| Admin API 전용 보호(인증/역할) | 6.6 권한 관리: "Admin 접근: 인증된 사용자 모두 접근 가능" | **주의**: "Admin 전용 역할 분리"는 Phase 12 계획. 현재는 미구현. |
| 감사 로그 보존 기간·용량 정책 | 6.2 "무기한 보존 (DB 용량 모니터링 필요)" | ✅ cursor에만 상세 정책 기술. vscode에는 "보존 기간·용량 정책" 체크만 있음. |
| 백업 스케줄·보관 장소·복원 절차 | 6.3 수동 백업/API 백업/복원 절차 | **주의**: cursor는 레거시 `/api/backup/*` 예시. vscode 기준 신규 `/api/system/backup`과 혼용 시 혼란 가능. |
| 롤백/버전 (Phase 11-2-3) | 6.2 "롤백 기능: Phase 11-2-3에서 구현 예정", 6.5 수동 롤백 | ✅ 양쪽 모두 "구현 예정·수동 롤백"으로 일치. |

### 2.3 UI 경로 ↔ Backend 라우터 매핑 요약

| UI 경로 (cursor 기준) | Backend (vscode 파일 경로) | 일치 |
|-----------------------|----------------------------|------|
| `/admin/approval` | `backend/routers/knowledge/approval.py` | ✅ (승인은 knowledge 도메인) |
| `/admin/settings/templates` | `backend/routers/admin/template_crud.py`, `schema_crud.py` | ✅ |
| `/admin/settings/audit-logs` | `backend/routers/admin/audit_log_crud.py` | ✅ |
| `/admin/statistics` | `backend/routers/system/statistics.py` | ✅ |

**결론**: 관리자 메뉴 경로와 백엔드 기능은 **논리적으로 잘 연결**되어 있음. 체크리스트에 있는 "Admin 전용 역할", "백업 경로 통일"은 문서 간 정리·보완 필요.

---

## 3. 기술 스택·환경 변수(Config) 상세 비교

### 3.1 기술 스택 비교

| 항목 | vscode-overview | cursor-overview | 일치 | 비고 |
|------|-----------------|-----------------|------|------|
| Backend | FastAPI (Python 3.11+) | FastAPI, PostgreSQL, Qdrant, Ollama | ✅ | vscode가 Python 버전 명시 |
| Frontend | Vanilla JavaScript + HTML | Vanilla JS + HTML + CSS (SPA 아님) | ✅ | cursor가 구조 설명 보강 |
| DB / Vector / LLM | PostgreSQL, Qdrant, Ollama (exaone3.5, qwen2.5) | 동일 + **기본 모델 qwen2.5:7b** | ⚠️ | **주의**: LLM 기본값만 상이 (아래 3.2 참고) |
| 테스트 | Playwright (E2E), pytest | 동일 + webtest.py, Phase별 spec | ✅ | - |

### 3.2 환경 변수·설정값 비교

| 변수/항목 | vscode-overview | cursor-overview | 주의 |
|-----------|-----------------|-----------------|------|
| **POSTGRES_PASSWORD** | `password` | `brain_password` | **주의**: 값 상이. 실제 배포 시 하나로 통일 필요 (docker-compose / .env 기준 권장). |
| **OLLAMA_BASE_URL** | `http://ollama:11434` | `http://host.docker.internal:11434` | **주의**: 호스트 차이. Docker 내부(ollama) vs 호스트(host.docker.internal). 환경별로 다름. |
| **OLLAMA_MODEL** | `exaone3.5:2.4b` | `qwen2.5:7b` | **주의**: 문서별 기본 모델 명칭 다름. **Phase 11 완료 시점 기준**은 프로젝트 기본값(docker-compose.yml 또는 .env.example)으로 하나 정해 두는 것이 좋음. |
| **Auth** | `SECRET_KEY=your-secret-key` | `JWT_SECRET_KEY=your-secret-key-change-in-production` | **주의**: 실제 코드(`backend/config.py`)는 **JWT_SECRET_KEY** 사용. vscode의 SECRET_KEY는 오기 → vscode 수정 권장. |
| **Web 포트** | 3000 (Frontend 선택) | 미기재 | vscode만 명시. |

### 3.3 Phase 11 완료 시점 "최종 기준" 권장

| 설정 항목 | 권장 | 근거 |
|-----------|------|------|
| **기본 LLM 모델** | **`qwen2.5:7b`** (docker-compose.yml 기본값) | `docker-compose.yml`: `OLLAMA_MODEL=${OLLAMA_MODEL:-qwen2.5:7b}`. cursor와 일치; vscode의 exaone3.5:2.4b는 예시로만 사용 시 명시. |
| **DB 비밀번호** | **`brain_password`** (docker-compose 기본값) | `docker-compose.yml`: `POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-brain_password}`. cursor와 일치; vscode의 `password`는 오기 가능성. |
| **Auth 환경 변수** | 코드에서 사용하는 이름 (예: `JWT_SECRET_KEY` vs `SECRET_KEY`) | backend/config.py 등에서 실제 읽는 변수명에 맞춰 문서 통일. |
| **OLLAMA_BASE_URL** | 로컬: `http://ollama:11434` (컨테이너 간), 호스트에서 접근: `http://localhost:11434` 등 | 문서에 "개발 환경(컨테이너 내부)" vs "호스트에서 Docker 접근" 두 예시를 나누어 기재 권장. |

---

## 4. 누락된 기능 및 향후 과제(Next Step) 추출

### 4.1 vscode "8. 다음 단계" + "9. 체크리스트" vs cursor 메뉴 구조

| vscode (다음 단계·체크리스트) | cursor 메뉴·문서 반영 | 구현/보완 상태 |
|-------------------------------|------------------------|----------------|
| Phase 12: 멀티 테넌시, 고급 Admin(A/B 테스트, 품질 리포트), 외부 연동 | cursor 6.6 Phase 12: RBAC, Admin 역할 분리, 승인 워크플로우 | 🔲 미구현 (향후) |
| 기술 부채: E2E spec 파일 미존재 | cursor 7.2 E2E 예시: `e2e/phase-11-3.spec.js` | ⚠️ **주의**: 파일 존재 여부 확인 필요. "미존재"면 cursor 예시는 가상일 수 있음. |
| 기술 부채: 운영 매뉴얼 미완료 (11-4-2) | cursor §6 운영 가이드 (백업, 롤백, 권한, 모니터링) | 🔲 일부만 문서화, "운영 매뉴얼"로 정식화는 미완료 |
| 체크리스트: Admin API 관리자 전용 인증/역할 | cursor 6.6 "Admin 접근: 인증된 사용자 모두" | 🔲 Admin 전용 역할 미구현 |
| 체크리스트: 감사 로그 보존 기간·용량 정책 | cursor 6.2 "무기한 보존" | ✅ 정책 기술됨 (cursor) |
| 체크리스트: 백업 스케줄·보관 장소·복원 절차 문서화 | cursor 6.3 수동/API 백업·복원 | ⚠️ API 경로를 신규(`/api/system/backup`)로 보완 필요 |

### 4.2 cursor 메뉴 기준 "아직 구현/보완 필요"로 보이는 항목

| 메뉴/기능 | 현재 반영 | 보완 필요 |
|-----------|-----------|-----------|
| Admin 설정 데이터 흐름 (schemas → templates → … → audit_logs) | cursor §6.1, vscode에는 동일 흐름 없음 | vscode에 "Admin 설정 데이터 흐름" 단락 추가 시 두 문서 **일관** |
| `/admin/settings/templates`에서 스키마(schemas) 연동 | cursor: "스키마·템플릿 CRUD", API `/api/admin/schemas`, `/api/admin/templates` | ✅ 구현·문서 반영됨 |
| 롤백 기능 (audit-logs에서 이전 값 복원) | vscode 9.2 "Phase 11-2-3 설계", cursor 6.2 "구현 예정" | 🔲 UI 롤백 미구현, 수동/SQL만 문서화 |
| 통계: `/api/system/statistics/dashboard` | cursor 6.7에서 curl 예시로 사용 | ⚠️ **주의**: 실제 엔드포인트는 루트 `/api/system/statistics` 등일 수 있음. 코드 확인 후 문서 수정 권장. |

### 4.3 Admin 설정 데이터 흐름 — 두 문서 일관성

| 항목 | vscode-overview | cursor-overview | 일치 |
|------|-----------------|-----------------|------|
| 흐름 순서 (schemas → templates → presets → rag_profiles → policy_sets → audit_logs) | §5.2 Admin 파일 나열만 있음, **흐름 다이어그램/설명 없음** | §6.1 "Admin 설정 데이터 흐름"에 순서·설명 있음 | ⚠️ **주의**: vscode에는 "데이터 흐름" 설명이 없음. cursor §6.1 내용을 vscode에 요약 추가하면 **일관**됨. |
| 각 단계별 역할 설명 | 개별 CRUD·UI 기능만 | 6.1 "데이터 흐름 설명" 1~6번 | cursor만 상세. |

**권장**: vscode-overview §5.2 또는 §9 앞에 "Admin 설정 데이터 흐름(schemas → templates → … → audit_logs)" 요약을 cursor 6.1과 동일하게 추가.

### 4.4 요약 표: 누락·보완 필요 항목

| 구분 | 항목 | 조치 |
|------|------|------|
| **문서 불일치** | 백업 API 경로 (레거시 vs 신규) | cursor 6.3에 `/api/system/backup` 예시 추가, 레거시와 구분 표기 |
| **문서 불일치** | 통계 API `/dashboard` | 실제 코드 확인 후 cursor 6.7 수정 또는 vscode에 "루트만 사용" 명시 |
| **문서 보완** | vscode에 Admin 데이터 흐름(schemas→…→audit_logs) | cursor §6.1 요약을 vscode에 추가 |
| **설정 통일** | LLM 기본 모델, DB 비밀번호, Auth 변수명 | 프로젝트 기준값 1곳(.env.example 또는 docker-compose) 정한 뒤 두 문서가 이를 참조하도록 수정 |
| **미구현** | Admin 전용 역할, audit 로그 기반 롤백 UI | Phase 12 또는 11-2-3 범위로 유지, 문서에는 "미구현" 명시 유지 |

---

## 5. 종합 요약

| 검토 영역 | 결과 요약 |
|-----------|-----------|
| **1. 구조·엔드포인트** | Phase 11 포함 Backend 라우터·파일 경로는 **대체로 일치**. 백업/통계 API 경로만 cursor 쪽 보완 필요. |
| **2. 메뉴 흐름** | 관리자 메뉴(경로)·Backend API **연결 일치**. 체크리스트와 cursor 6.6 권한 설명 정합성 있음. |
| **3. 기술 스택·Config** | LLM 기본 모델, DB 비밀번호, Ollama URL, Auth 변수명 등 **차이 있음** → 단일 기준 정한 뒤 문서 통일 권장. |
| **4. 누락·다음 단계** | Admin **데이터 흐름**은 vscode에 없음 → cursor 6.1 기준 추가. 백업/통계 API·롤백 UI는 문서/구현 보완 필요. |

**주의**로 표시한 항목은 두 문서 또는 문서와 코드 간 불일치·보완이 필요한 부분입니다. 위 표와 권장 조치를 반영해 수정하면 두 개요 문서의 일관성과 운영 가이드 활용도가 높아집니다.
