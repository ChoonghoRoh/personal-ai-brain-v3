# vscode · cursor 문서 비교 상세 리뷰 (vscode-cursor-match-detail-review-260208)

**비교 대상**: [docs/overview/vscode-overview-260208.md](docs/overview/vscode-overview-260208.md), [docs/overview/cursor-overview-260208.md](docs/overview/cursor-overview-260208.md)  
**기준 시점**: 2026-02-08  

---

## 1. Backend API 구조 및 엔드포인트 일치성 검토

### 1.1 공통 영역 비교 결과 (불일치/누락 중심)

| 구분 | vscode-overview (파일/엔드포인트) | cursor-overview (Prefix) | 차이/이슈 | 판정 |
|------|-----------------------------------|---------------------------|-----------|------|
| 지식 통합 | `backend/routers/knowledge/knowledge_integration.py` + `/api/knowledge/integration/duplicate` | `/api/knowledge-integration` | **경로 표기 불일치**: vscode 문서는 `/api/knowledge/integration/duplicate`로 서술, cursor는 `/api/knowledge-integration`로 서술 | ⚠️ 주의 |
| 시스템 백업 | `/api/system/backup`, `/api/backup/*` (레거시 포함) | `/api/system` (일반) | cursor 문서에 **백업·복원/검증 상세 엔드포인트 미기재** | ⚠️ 주의 |
| 무결성 검사 | `/api/integrity/check` | 미표기 | cursor 문서에 **무결성 검사 엔드포인트 미기재** | ⚠️ 주의 |
| 에러 로그 | `/api/error-logs` | 미표기 | cursor 문서에 **에러 로그 엔드포인트 미기재** | ⚠️ 주의 |
| Reasoning 스트리밍 | `/api/reason/stream`, `/api/reason/{task_id}/cancel` | `/api/reason` (stream, eta, share, decisions) | cursor는 개념 위주, vscode는 상세 경로 위주. **세부 경로 표기 레벨 차이** | 참고 |
| Admin 설정 | `/api/admin/schemas`, `/api/admin/templates`, `/api/admin/presets`, `/api/admin/rag-profiles`, `/api/admin/policy-sets`, `/api/admin/audit-logs` | `/api/admin/*` | **명칭 일치**. cursor는 Prefix 레벨, vscode는 상세 CRUD 레벨 | 정상 |

### 1.2 Phase 11(Admin 설정) 라우터 반영 점검

| 항목 | vscode-overview | cursor-overview | 판정 |
|------|-----------------|-----------------|------|
| schemas | `/api/admin/schemas` | `/api/admin/*` | 정상 |
| templates | `/api/admin/templates` | `/api/admin/*` | 정상 |
| presets | `/api/admin/presets` | `/api/admin/*` | 정상 |
| rag-profiles | `/api/admin/rag-profiles` | `/api/admin/*` | 정상 |
| policy-sets | `/api/admin/policy-sets` | `/api/admin/*` | 정상 |
| audit-logs | `/api/admin/audit-logs` | `/api/admin/*` | 정상 |

**결론**: Phase 11(Admin 설정) 관련 라우터는 양쪽 문서 모두 **일관적으로 반영됨**.  
단, **지식 통합(knowledge-integration)** 경로 표기는 양쪽 문서 간 **불일치**가 있으므로 정정 필요.

---

## 2. 사용자/관리자 메뉴 흐름(Flow) 분석

### 2.1 커서 문서 관리자 메뉴 ↔ 백엔드 기능 연결성

| 관리자 메뉴 (cursor 2.2) | UI 경로 | 연결되는 백엔드 기능 | 연결성 평가 | 판정 |
|---|---|---|---|---|
| 키워드 관리 | `/admin/groups` | `/api/labels` | 키워드 그룹을 labels로 관리하는 구조와 부합 | 정상 |
| 라벨 관리 | `/admin/labels` | `/api/labels` | 라벨 CRUD와 직접 연동 | 정상 |
| 청크 생성 | `/admin/chunk-create` | `/api/knowledge` + `/api/file-parser` | cursor 문서에 `ingest`로만 표기됨. 실제 API는 `/api/file-parser`로 명시 필요 | ⚠️ 주의 |
| 청크 승인 | `/admin/approval` | `/api/approval/chunks` | `backend/routers/knowledge/approval.py`와 논리적으로 일치 | 정상 |
| 청크 관리 | `/admin/chunk-labels` | `/api/knowledge`, `/api/labels` | 청크-라벨 매핑과 연동 | 정상 |
| 통계 | `/admin/statistics` | `/api/system/statistics` | 통계 대시보드와 연동 | 정상 |

### 2.2 관리자 체크리스트 ↔ 메뉴 누락 항목

| 체크리스트 항목 (vscode 9) | 관련 API/기능 | cursor 메뉴 목차 존재 여부 | 비고 | 판정 |
|---|---|---|---|---|
| 감사 로그 UI | `/api/admin/audit-logs`, `admin/settings/audit-logs.html` | **설정 메뉴(2.3)**에 있음 | 2.2에는 없으나 2.3에 존재 | 정상 |
| 백업·복원 | `/api/system/backup`, `/api/backup/*` | 없음 | Admin 메뉴에 전용 UI 없음 | ⚠️ 주의 |
| 백업 검증 | `/api/system/backup/{name}/verify` | 없음 | 메뉴/페이지 미존재 | ⚠️ 주의 |
| 무결성 검사 | `/api/integrity/check` | 없음 | 메뉴/페이지 미존재 | ⚠️ 주의 |
| 에러 로그 | `/api/error-logs` | 없음 | 메뉴/페이지 미존재 | ⚠️ 주의 |
| 헬스체크 | `/api/system/health` | 없음 | 운영 점검용 API만 존재 | 참고 |
| 보안 헤더/Rate Limit/CORS | 미들웨어 설정 | 없음 | UI 노출 대상 아님 | 참고 |

**결론**: cursor 문서의 관리자 메뉴는 **운영/보안 점검 기능(백업·무결성·에러 로그)**이 누락되어 있어, 운영자 관점에서 추가 메뉴 또는 별도 운영 페이지 기획이 필요.

---

## 3. 데이터 및 설정값(Config) 비교

| 항목 | vscode-overview | cursor-overview | 차이/이슈 | 판정 |
|------|------------------|-----------------|-----------|------|
| LLM 모델 표기 | Ollama: exaone3.5, qwen2.5 (일반 모델군) + `.env`에 `exaone3.5:2.4b` | 기본 모델 `qwen2.5:7b` | **모델 명칭 불일치**. vscode는 exaone3.5:2.4b, cursor는 qwen2.5:7b | ⚠️ 주의 |
| OLLAMA_BASE_URL | `.env`: `http://ollama:11434` | 미표기 | docker-compose 기본은 `http://host.docker.internal:11434`로 설정됨 | ⚠️ 주의 |
| DB 계정/비밀번호 | `.env`에 `POSTGRES_PASSWORD=password` | 미표기 | docker-compose는 `brain_password` 기본값 사용 | ⚠️ 주의 |
| AUTH_ENABLED | `.env`에 설명 있음 | 미표기 | 운영 기준 상태 명확화 필요 | 참고 |

### 3.1 최종 기준 권고 (Phase 11 완료 기준)

- **LLM 기본값**: `qwen2.5:7b` (docker-compose.yml 기본값 기준)  
- **OLLAMA_BASE_URL**: `http://host.docker.internal:11434` (Docker 분리 실행 기준)  
- **DB 기본 비밀번호**: `brain_password` (docker-compose.yml 기본값)  

**권고**: [docs/overview/vscode-overview-260208.md](docs/overview/vscode-overview-260208.md)의 `.env` 예시를 docker-compose 기본값과 일치하도록 조정 필요.

---

## 4. 누락된 기능 및 향후 과제(Next Step) 추출

### 4.1 다음 단계 vs 메뉴 구조 간 갭

| vscode-overview 다음 단계(8) | cursor 메뉴 반영 여부 | 보완 필요 사항 | 판정 |
|---|---|---|---|
| 멀티 테넌시 확장 | 없음 | Admin UI 및 DB 구조 확장 필요 | ⚠️ 주의 |
| 고급 Admin 기능(A/B 테스트, 품질 리포트) | 없음 | 통계/리포트 전용 페이지 필요 | ⚠️ 주의 |
| 외부 연동(Notion/Confluence) | 없음 | 연동 설정 UI/API 필요 | ⚠️ 주의 |

### 4.2 관리자 프로그램 리뷰 체크리스트 ↔ 메뉴 갭

| 체크리스트 항목 | cursor 메뉴에 반영 여부 | 보완 방향 | 판정 |
|---|---|---|---|
| 백업/복원 UI | 없음 | `/admin/backup` 등 운영 메뉴 추가 고려 | ⚠️ 주의 |
| 무결성 검사 UI | 없음 | `/admin/integrity` 등 운영 메뉴 추가 고려 | ⚠️ 주의 |
| 에러 로그 UI | 없음 | `/admin/error-logs` 혹은 통합 로그 페이지 확장 | ⚠️ 주의 |
| 감사 로그 UI | 있음 (설정 메뉴 2.3) | 2.2 메뉴와의 링크 연계 강화 | 참고 |

### 4.3 Admin 설정 데이터 흐름 일관성

| 항목 | vscode-overview | cursor-overview | 판정 |
|---|---|---|---|
| Admin 설정 데이터 흐름 (schemas → templates → presets → rag_profiles → policy_sets → audit_logs) | 상세 설명 존재 | **설명 없음** | ⚠️ 주의 |

**결론**: Admin 설정 데이터 흐름은 vscode 문서에만 상세 기재되어 있어, cursor 문서에도 동일 흐름을 추가해야 운영 문서 간 일관성이 유지됨.

---

## 5. 종합 결론 및 개선 제안

1. **지식 통합 API 경로 표기 불일치** → cursor 기준(`/api/knowledge-integration`)에 맞춰 vscode 문서 수정 권장.  
2. **운영자 기능(백업/무결성/에러로그) 메뉴 부재** → Admin 운영 메뉴 신설 또는 기존 메뉴 확장 필요.  
3. **환경 변수 및 기본 설정값 불일치** → docker-compose 기본값 기준으로 통일 필요.  
4. **Admin 설정 데이터 흐름 문서화 편차** → cursor 문서에도 동일 흐름 추가 권장.

---

**작성일**: 2026-02-08
