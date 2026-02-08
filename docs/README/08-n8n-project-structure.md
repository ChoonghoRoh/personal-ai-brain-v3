# n8n 프로젝트 구조 (전문 유지)

원문: `README.md.backup` Phase 8.1~8.3 섹션 중 n8n 관련 블록. n8n 디렉터리 구조·생성된 파일·규칙·마이그레이션 결과·관련 문서를 요약 없이 유지. 어떤 방식으로 n8n이 도입·진화했는지 추적용.

---

## docs/n8n/ 디렉터리 구조

```
docs/n8n/
├── n8n-backend-call-manual-settings.md   # Backend HTTP 호출 설정 (n8n → backend)
├── rules/
│   └── n8n node nameing Rules.md         # 노드 네이밍 규칙 (JS_/CMD_/DB_/GPT_ 등)
└── workflow/
    ├── Phase Auto Checker v1.json
    ├── Phase Auto Checker v1 Workflow.md
    ├── Task Execution v1.json
    ├── Task Execution v1 - Git 동기화 기록.md
    ├── Task Execution v1 - 변경 이력.md
    ├── Task Execution v1 - 실행 결과 확인 방법.md
    ├── Task Execution v1 Workflow Improvement Plan.md
    ├── Task Plan and Test Plan Generation v1 (test).json
    ├── Task Plan and Test Plan Generation v2 (phase-folder).json
    ├── Task Plan and Test Plan Generation v2 (phase-folder) - Workflow.md
    ├── Task Plan and Test Plan Generation vs Task Execution - 비교.md
    └── n8n-workflow-phase-task-convention.md
```

---

## 생성된 파일 (개발 코드 기준) — Phase 8.1~8.3

**Backend**

- `backend/models/workflow_common.py` — workflow 공통 컬럼명·테이블명·Phase/Plan/Task/TestResult 상태 Enum
- `backend/services/automation/workflow_task_service.py` — Task 실행 로직 (Claude CLI 호출, plan_md_path/plan_doc 처리)
- `backend/routers/automation/workflow.py` — `POST /api/workflow/run-task` API
- `backend/services/ai/ollama_client.py` — Ollama 연동 (8-3-0 gpt4all→Ollama 전환)
- `backend/services/automation/README-workflow_task_service.md` — Task 실행 서비스 설명 (8-2-7)

**DB 스크립트**

- `scripts/db/workflow_common_ddl.sql` — workflow 공통 DDL 조각
- `scripts/db/insert_workflow_phase_for_generation.sql` — phase 등록용
- `scripts/db/migrate_workflow_tasks_phase_slug.sql`, `migrate_workflow_tasks_task_num.sql`, `migrate_workflow_tasks_plan_md_path.sql` — workflow_tasks 컬럼 마이그레이션
- `scripts/db/migrate_postgres_volume.sh` — PostgreSQL 볼륨 마이그레이션

**n8n 워크플로우**

- `docs/n8n/workflow/Task Plan and Test Plan Generation v1 (test).json` — 8-2-6 테스트용
- `docs/n8n/workflow/Task Plan and Test Plan Generation v2 (phase-folder).json` — 8-2-6 phase-folder용
- `docs/n8n/workflow/Task Plan and Test Plan Generation v2 (phase-folder) - Workflow.md` — v2 동작 설명
- `docs/n8n/workflow/Task Execution v1.json` — 8-2-7 Task 실행 (Backend HTTP 호출)
- `docs/n8n/workflow/n8n-workflow-phase-task-convention.md`, `docs/n8n/n8n-backend-call-manual-settings.md`
- `docs/n8n/rules/n8n node nameing Rules.md` — n8n 노드 네이밍 규칙 (JS_/CMD_/DB_/GPT_ 등)
- `docs/n8n/workflow/Task Plan and Test Plan Generation vs Task Execution - 비교.md` — Task Plan v2 vs Task Execution 비교
- `docs/n8n/workflow/Task Execution v1 - Git 동기화 기록.md`, `docs/n8n/workflow/Task Execution v1 - 실행 결과 확인 방법.md`

**문서**

- `docs/phases/phase-8-1/phase8-1-plan.md`, `docs/phases/phase-8-1/tasks/phase8-1-1-database-schema-n8n-setting.md`, `docs/phases/phase-8-1/tasks/phase8-1-2-n8n-postgresql-migration.md`
- `docs/phases/phase-8-2/tasks/phase8-2-1-code-analysis-workflow-guide.md`, `docs/phases/phase-8-2/phase8-2-4-2-6-development-progress-check.md`, `docs/phases/phase-8-2/tasks/phase8-2-7-task-execution-workflow.md`, `docs/phases/phase-8-2/tasks/phase8-2-7-task-execution-git-sync-record.md`, `docs/phases/phase-8-2/tasks/phase8-2-8-task-test-and-store-workflow.md`
- `docs/phases/phase-8-3/tasks/phase8-3-0-dockerfile-ollama-folder-git-sync-record.md`, `docs/phases/phase-8-3/tasks/phase8-3-1-docker-compose-integration-guide.md`
- `docs/ai/korean-local-llm-recommendation.md`
- `docs/db/workflow-tables-common.md`, `docs/db/workflow_tasks-table-columns.md`
- `docs/phases/phase8-master-plan.md` — Phase 8 전체 실행 계획 (n8n 워크플로우·범위·일정)
- `docs/phase-document-taxonomy.md` — Phase 문서 분류 체계 (plan/todo-list/task/summary 등, ai-rule·자동화 판단 기준)

**설정**

- `docker-compose.yml` — backend, PostgreSQL, Qdrant, n8n, ollama 통합

---

## n8n 규칙·문서 분류 및 관련 작업

Phase 8 워크플로우·자동화와 연동되는 **규칙·규약·문서 분류** 작업 기록.

| 구분 | 경로 | 용도 |
|------|------|------|
| **n8n 규칙** | `docs/n8n/rules/` | n8n 워크플로우 노드 명명 규칙 (Prefix·동사+대상, JS_/CMD_/DB_/GPT_ 등). Task Plan v2·Task Execution 워크플로우 노드 이름 기준. |
| | `docs/n8n/rules/n8n node nameing Rules.md` | 노드 네이밍 규칙 상세 (목적, 기본 형식, Prefix 규칙, 예시). |
| **문서 분류** | `docs/phase-document-taxonomy.md` | Phase 문서 분류 체계(Taxonomy). plan/todo-list/task/summary 등 문서 종류·역할·생성 주체·자동화 가능 여부 정의. ai-rule·phase-auto-generation 판단 기준. |
| **n8n 문서** | `docs/n8n/` | n8n 워크플로우·Backend 연동·규약 문서. `workflow/`(JSON·Workflow.md·convention), `n8n-backend-call-manual-settings.md` 등. |

- **규칙 반영**: Task Plan and Test Plan Generation v2 (phase-folder), Task Execution v1 워크플로우는 `docs/n8n/rules/` 노드 네이밍 규칙과 `docs/n8n/workflow/n8n-workflow-phase-task-convention.md` phase-task 규약을 따름.
- **Taxonomy 연동**: `docs/phase-document-taxonomy.md`는 `docs/ai/ai-rule-decision.md`, `docs/ai/ai-rule-phase-naming.md` §7 및 phase 폴더·tasks 하위 규칙과 함께 문서 구조 판단에 사용됨.

---

## 핵심 개선사항

- ✅ n8n 데이터베이스 통합 관리 (PostgreSQL), Docker Compose로 모든 서비스 통합
- ✅ Backend `POST /api/workflow/run-task`로 Task 실행 (n8n → HTTP 호출, plan_md_path 기반 실행)
- ✅ Task Plan v2: phase todo-list 파싱 → task_num/phase_slug · plan_md_path 저장 → workflow_tasks INSERT
- ✅ workflow_common 모델·DDL 조각으로 스키마·코드 일관성 유지
- ✅ 프로젝트 폴더 마운트로 n8n에서 직접 프로젝트 파일 접근 가능
- ✅ 로컬 LLM gpt4all → Ollama 전환 (8-3-0): `ollama_client`, 시스템 상태·키워드 추출 Ollama 연동

---

## 마이그레이션 결과 (n8n)

- **워크플로우**: 4개 성공적으로 마이그레이션 + Task Plan v1/v2, Task Execution v1 (문서/JSON 보관)
- **Credentials**: 6개 성공적으로 마이그레이션 (OpenAI, Discord Bot, Webhook, ChatGPT, Anthropic 등)

---

## 관련 문서

- `docs/phases/phase-8-1/phase8-1-plan.md` — Phase 8-1 계획
- `docs/phases/phase-8-1/tasks/phase8-1-1-database-schema-n8n-setting.md` — PostgreSQL 스키마
- `docs/phases/phase-8-1/tasks/phase8-1-2-n8n-postgresql-migration.md` — 마이그레이션 가이드
- `docs/phases/phase-8-2/tasks/phase8-2-1-code-analysis-workflow-guide.md` — 코드 분석 워크플로우
- `docs/phases/phase-8-2/tasks/phase8-2-7-task-execution-workflow.md` — Task 실행 (8-2-7)
- `docs/phases/phase-8-2/tasks/phase8-2-7-task-execution-git-sync-record.md` — 8-2-7 Git 동기화 기록
- `docs/phases/phase-8-2/tasks/phase8-2-8-task-test-and-store-workflow.md` — 8-2-8 Task 테스트·결과 저장 (미구현)
- `docs/phases/phase-8-2/phase8-2-4-2-6-development-progress-check.md` — 8-2-4~8-2-6 진행 현황
- `docs/phases/phase8-master-plan.md` — Phase 8 전체 실행 계획
- `docs/phases/phase-8-3/tasks/phase8-3-0-dockerfile-ollama-folder-git-sync-record.md` — 8-3-0 Dockerfile·gpt4all→Ollama·폴더 정리
- `docs/phases/phase-8-3/tasks/phase8-3-1-docker-compose-integration-guide.md` — Docker Compose 통합
- `docs/ai/korean-local-llm-recommendation.md` — Ollama 한국어 모델 추천
- `docs/db/workflow-tables-common.md`, `docs/db/workflow_tasks-table-columns.md` — workflow 테이블 규약
- `docs/n8n/rules/n8n node nameing Rules.md` — n8n 노드 네이밍 규칙
- `docs/phase-document-taxonomy.md` — Phase 문서 분류 체계 (Taxonomy)
