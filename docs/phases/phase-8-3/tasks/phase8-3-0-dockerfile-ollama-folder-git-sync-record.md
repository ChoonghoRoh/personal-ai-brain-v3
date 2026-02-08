# Phase 8-3-0 (1) Dockerfile.backend (2) gpt4all→Ollama (3) 폴더 정리 — Git 동기화 기록

Phase 8-3 관련 **Docker·Backend·requirements** 변경이 동일 커밋(cb2e7f6 등)에 포함되어 있으나, 기록은 8-3-0으로 별도 분기한다.  
n8n Task Execution v1만의 기록은 **Phase 8-2-7** → [phase8-2-7-task-execution-git-sync-record.md](./phase8-2-7-task-execution-git-sync-record.md)

**관련 문서:** `phase8-3-1-docker-compose-integration-guide.md`, `docs/ai/korean-local-llm-recommendation.md`

**기록 대상:**  
1. Dockerfile.backend 변경  
2. gpt4all → Ollama 전환  
3. backend·web·scripts 폴더 정리  

---

## 2026-01-27 동기화 (동일 커밋 내 8-3-0 항목)

### 브랜치·원격
- **브랜치:** `n8n` → **main** 병합 후 동기화
- **원격:** `origin` (https://github.com/ChoonghoRoh/personal-ai-brain.git)
- **커밋:** cb2e7f6, fca8a45 (8-2-7과 동일)

### 8-3-0 포함 변경 사항 (Docker·Backend·requirements)

| 구분 | 파일/경로 | 내용 |
|------|------------|------|
| 수정 | `Dockerfile.backend` | Backend 이미지 빌드 설정 (Node.js 추가 등) |
| 수정 | `docker-compose.yml` | 서비스·환경 변수 (ollama 서비스, OLLAMA_* 등) |
| 수정 | `backend/services/automation/workflow_task_service.py` | Task 실행·Claude CLI 연동 |
| 수정 | `requirements-docker.txt` | 의존성 |
| 수정 | `requirements.txt` | 의존성 |

---

## 변경 상세 (1 Dockerfile · 2 Ollama · 3 폴더 정리)

### 1. Dockerfile.backend

- **목적:** Backend 컨테이너에서 Claude Code CLI 실행 가능하도록.
- **변경 내용:**
  - **Node.js 설치 추가:** `apt-get install ... nodejs` — n8n 워크플로우에서 Backend가 `claude` CLI를 호출할 때 필요.
  - 기타: `build-essential`, `libpq-dev` 등 시스템 의존성 유지.
- **참고:** `docs/n8n/n8n-backend-call-manual-settings.md` 에서 “Dockerfile.backend에 nodejs” 안내함.

### 2. gpt4all → Ollama 전환

로컬 LLM을 **GPT4All**에서 **Ollama**로 통일한 변경 기록.

| 구분 | 파일/경로 | 내용 |
|------|------------|------|
| 추가 | `backend/config.py` | `OLLAMA_BASE_URL`, `OLLAMA_MODEL` 환경 변수 |
| 추가 | `backend/services/ai/ollama_client.py` | `ollama_generate()`, `ollama_available()` |
| 수정 | `backend/routers/ai/ai.py` | 답변 생성 시 `ollama_generate()` 사용 (기존 gpt4all 호출 제거) |
| 수정 | `backend/services/system/system_service.py` | `_get_gpt4all_status()` → `_get_ollama_status()`, 시스템 상태에 Ollama 반영 |
| 수정 | `backend/routers/system/system.py` | `POST /api/system/test/gpt4all` 경로 유지, 내부는 `_get_ollama_status(run_test=True)` 호출 |
| 수정 | `scripts/backend/extract_keywords_and_labels.py` | `extract_keywords_with_gpt4all` → `extract_keywords_with_ollama` 등 Ollama 연동 |
| 수정 | `docker-compose.yml` | `ollama` 서비스 추가, backend에 `OLLAMA_BASE_URL`, `OLLAMA_MODEL` 설정 |
| 수정 | `README.md` | Ollama 모델 실행 예시, 대시보드 “로컬 LLM (Ollama)” 안내 |
| 추가·수정 | `docs/ai/korean-local-llm-recommendation.md` | 현재 구성(Ollama), 추천 모델, Docker·Backend 연동 요약 |

- **API:** Ollama `POST /api/generate`, `GET /api/tags` 사용. 기본 모델 예: `bnksys/yanolja-eeve-korean-instruct-10.8b`.
- **대시보드:** `GET /api/system/status` 의 `gpt4all` 필드에 Ollama 상태가 담겨 나가며, 프론트는 “로컬 LLM (Ollama)”로 표시.

### 3. backend·web·scripts 폴더 정리

기존에 루트에 나열되어 있던 라우터·서비스·스크립트·웹 자원을 **용도별 하위 폴더**로 재구성한 기록.

#### backend

- **backend/routers** — 용도별 패키지로 분리. `backend/routers/README.md` 에 구조 정리.
  - **search/** — search, documents
  - **system/** — system, backup, integrity, logs, error_logs
  - **ai/** — ai, conversations
  - **knowledge/** — knowledge, labels, relations, approval, knowledge_integration, suggestions
  - **reasoning/** — reason, reasoning_chain, reasoning_results
  - **cognitive/** — memory, context, learning, personality, metacognition
  - **automation/** — automation, workflow
  - **ingest/** — file_parser
- **backend/services** — routers와 동일한 도메인별 하위 패키지. `backend/services/README.md` 에 정리.
  - **search/**, **system/**, **ai/**, **knowledge/**, **reasoning/**, **cognitive/**, **automation/**, **ingest/**  
  - 각 패키지에 해당 서비스 모듈 배치 (예: automation/workflow_task_service.py).

#### scripts

- **scripts/README.md** 에 용도별 분류 가이드 추가.
- **backend/** — API·서버·임베딩·검색·키워드 등: start_server.py, embed_and_store.py, search_and_query.py, extract_keywords_and_labels.py, generate_chunk_titles.py, check_gpt4all_model.py, check_model_download.py
- **db/** — DB 초기화·마이그레이션·스키마·분석: init_db.py, migrate_*.py, insert_test_tasks_to_db.py, insert_test_tasks.sql, analyze_slow_queries.py 등
- **n8n/** — n8n·Phase 8-2 연동: run_task_execution.py, run-claude-analysis.sh, run-gap-analysis.sh, generate-plan.sh, run-phase-8-2-all.sh, save_*_to_db.py
- **devtool/** — 백업·보안·동기화·감시·로그·테스트 등: backup_system.py, security_scan.py, watcher.py, work_logger.py 등
- **web/** — 웹/프론트 전용 (예정). README.md만 두고 스크립트는 추후 추가.

#### web

- **web/public/js** — 기능별 하위 폴더로 분리.
  - **admin/** — admin-approval, admin-common, admin-groups, admin-labels, chunk-approval-manager, keyword-group-*, knowledge-admin, label-manager
  - **ask/**, **dashboard/**, **document/**, **logs/**, **reason/**, **search/**
  - **knowledge/** — knowledge-detail, knowledge-label-matching, knowledge-relation-matching, knowledge
  - **components/** — document-utils, header-component, layout-component, pagination-component, text-formatter, utils
- **web/public/css** — **admin/** (admin-approval, admin-groups, admin-labels, admin-styles), **knowledge/** (knowledge-admin, knowledge-detail, knowledge), 그 외 루트에 ask, dashboard, document, logs, reason, search
- **web/src/pages** — **admin/** (approval, groups, labels), **knowledge/** (knowledge-admin, knowledge-detail, knowledge-label-matching, knowledge-relation-matching, knowledge), 그 외 루트에 ask, dashboard, document, logs, reason, search

**참고:** URL·API 경로는 기존과 동일하게 유지. `main.py` 및 각 라우터의 `APIRouter(prefix=...)` 로 기존 엔드포인트 유지.

---

### 요약

- Task Execution v1 테스트와 함께 반영된 Docker·Backend·requirements 변경을 Phase 8-3-0 관점에서 기록.
- **(1) Dockerfile.backend:** Node.js 추가(Claude Code CLI용).
- **(2) gpt4all → Ollama:** config·ollama_client·ai·system_service·extract_keywords·docker-compose·README·korean-local-llm-recommendation 에 기록·반영됨.
- **(3) backend·web·scripts 폴더 정리:** routers/services 용도별 패키지, scripts 용도별 하위 폴더(backend, db, n8n, devtool, web), web public js/css/pages 기능별 하위 폴더. README로 구조 문서화.
- main 병합·n8n 재분기 내용은 8-2-7 기록과 동일 (같은 커밋 범위).
