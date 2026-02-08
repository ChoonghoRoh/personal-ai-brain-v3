# 아키텍처 및 구조 (전문 유지)

원문: `README.md.backup` 71~111라인. Backend/Web/실행환경·n8n·backend·web 파일 공유.

---

## 🏗 아키텍처 및 구조 변경

Docker Compose로 `postgres`, `qdrant`, `ollama`, `backend`, `n8n` 서비스가 **pab-network** 브리지 네트워크에서 동작합니다. 각 컴포넌트별 세부는 아래와 같습니다.

| 컴포넌트 | 이미지/베이스 | 버전 |
|----------|----------------|------|
| Backend | Dockerfile.backend | Python 3.12-slim, uvicorn |
| PostgreSQL | postgres | 15 |
| Qdrant | qdrant/qdrant | latest |
| n8n | n8nio/n8n | latest |
| Ollama | ollama/ollama | latest |

---

### Backend (FastAPI)

- **역할**: API·정적 파일(web)·임베딩·검색·AI 질의·지식·Reasoning·워크플로우 Task 실행 등 통합 서버.
- **이미지·버전**: `Dockerfile.backend` → 베이스 `python:3.12-slim`, uvicorn. Node.js 포함(Claude Code CLI 호출용).
- **컨테이너명**: `pab-backend`. **포트**: `8000` (호스트 8000 노출).
- **환경 변수** (`backend/config.py`에서 읽음, docker-compose로 오버라이드):
  - `PROJECT_ROOT`, `WORKSPACE_ROOT`: `/app` (컨테이너 내 프로젝트 루트).
  - `DATABASE_URL`: `postgresql://brain:brain_password@postgres:5432/knowledge` (PostgreSQL 연결).
  - `QDRANT_HOST`, `QDRANT_PORT`: `qdrant`, `6333` (Qdrant 연결).
  - `OLLAMA_BASE_URL`, `OLLAMA_MODEL`: `http://ollama:11434`, `bnksys/yanolja-eeve-korean-instruct-10.8b` (Ollama 연동).
  - `API_HOST`, `API_PORT`: `0.0.0.0`, `8000`. `ANTHROPIC_API_KEY`: Task 실행(Claude) 시 선택.
- **볼륨**: `${PAB_PROJECT_ROOT:-.}:/app` (backend·web·brain·scripts 등 공유). Claude CLI용 `/host-npm-global`, `~/.claude` 마운트 가능.
- **의존성**: `depends_on` → `postgres` (healthy), `qdrant` (started). Ollama는 의존에 포함하지 않음(선택 연동).
- **코드 구조**: `routers/`·`services/` 용도별 하위 패키지 (`search`, `system`, `ai`, `knowledge`, `reasoning`, `cognitive`, `automation`, `ingest`). 상세: `backend/routers/README.md`, `backend/services/README.md`.

---

### PostgreSQL

- **역할**: 지식 메타데이터·워크플로우(phases, plans, tasks 등)·n8n 메타 저장.
- **이미지·버전**: `postgres:15`. **컨테이너명**: `pab-postgres`. **포트**: `5432`.
- **환경**: `POSTGRES_USER=brain`, `POSTGRES_PASSWORD=brain_password`, `POSTGRES_DB=knowledge`. Backend는 DB `knowledge`, n8n은 DB `n8n` 사용(동일 유저/비밀번호).
- **볼륨**: `postgres_data:/var/lib/postgresql/data` (영구 저장).
- **헬스체크**: `pg_isready -U brain -d knowledge`. Backend·n8n이 `depends_on`(condition: service_healthy)으로 기동 순서 보장.

---

### Qdrant

- **역할**: 벡터 DB. 문서 임베딩 저장·의미 검색(컬렉션 예: `brain_documents`).
- **이미지·버전**: `qdrant/qdrant:latest`. **컨테이너명**: `qdrant`. **포트**: `6333`, `6334` (API·gRPC).
- **볼륨**: `./qdrant-data:/qdrant/storage` (프로젝트 디렉터리, 영구 저장).
- **헬스체크**: `wget --spider http://localhost:6333/`. Backend가 `depends_on`(condition: service_started)으로 연결 대기.
- **Backend 연동**: `backend/config.py`의 `QDRANT_HOST`, `QDRANT_PORT`, `COLLECTION_NAME`으로 접속.

---

### n8n

- **역할**: 워크플로우 자동화(Task Plan/Test Plan 생성, Execute Command, HTTP Request로 Backend 호출 등).
- **이미지·버전**: `n8nio/n8n:latest`. **컨테이너명**: `n8n`. **포트**: `5678`.
- **환경 변수**:
  - `N8N_HOST`, `N8N_PORT`, `N8N_PROTOCOL`: `localhost`, `5678`, `http`.
  - `WORKSPACE_ROOT=/workspace`: 프로젝트 루트(호스트 `PAB_PROJECT_ROOT`와 동일 경로 마운트).
  - `BACKEND_URL=http://backend:8000`: HTTP Request 노드에서 Backend API 호출.
  - `DB_TYPE=postgresdb`, `DB_POSTGRESDB_*`: PostgreSQL에 n8n 메타 저장 (`postgres`, DB `n8n`, 유저 `brain`).
  - `NODES_EXCLUDE='[]'`: Execute Command 노드 활성화.
- **볼륨**: `n8n_data:/home/node/.n8n` (워크플로우·크리덴셜). `${PAB_PROJECT_ROOT:-.}:/workspace` (프로젝트 공유). `.npm-global`, `docker.sock` 마운트(Execute Command·Claude CLI 등).
- **의존성**: `depends_on` → `postgres` (healthy).
- **파일 공유**: n8n은 `/workspace`, Backend는 `/app`으로 같은 호스트 디렉터리 참조. `docs/n8n/n8n-backend-call-manual-settings.md` 참고.

---

### Ollama (로컬 LLM)

- **역할**: 로컬 LLM 서버. AI 질의·키워드 추출 등 Backend에서 HTTP API로 호출.
- **이미지·버전**: `ollama/ollama:latest`. **컨테이너명**: `ollama`. **포트**: `11434`.
- **볼륨**: `ollama_data:/root/.ollama` (모델·캐시 영구 저장).
- **Backend 연동**: Backend 환경 변수 `OLLAMA_BASE_URL=http://ollama:11434`, `OLLAMA_MODEL=bnksys/yanolja-eeve-korean-instruct-10.8b`. Ollama `POST /api/generate`, `GET /api/tags` 사용.
- **의존성**: Backend `depends_on`에 포함하지 않음. 백엔드는 ollama 미기동 시에도 기동하며, AI 질의 시 폴백 메시지 반환. **모델은 컨테이너 기동 후 수동 로드**: `docker exec -it ollama ollama run bnksys/yanolja-eeve-korean-instruct-10.8b` (또는 `llama3.2-korean-bllossom:3b` 등).
- **개발 기록**: Phase 8-3-0 gpt4all→Ollama 전환. `docs/phases/phase-8-3/tasks/phase8-3-0-dockerfile-ollama-folder-git-sync-record.md`, `docker-compose.yml`.

---

### Web (정적·템플릿)

- **역할**: Backend가 `/app`(PROJECT_ROOT)에서 정적 파일 제공. 별도 컨테이너 없음.
- **경로**: `web/public/css`, `web/public/js` (기능별 하위: `js/components/`, `js/admin/`, `js/knowledge/`, `js/search/` 등). `web/src/pages/`에 `admin/`, `knowledge/` 그룹 및 dashboard·search·document·ask·logs·reason 페이지.
- **상세**: `web/README.md`.

---

### 의존성

- Backend 패키지: 루트 `requirements.txt` (실행·설정·아키텍처 요약이 파일 상단 주석에 있음).

---

### n8n · backend · web 파일 공유 (공통 변수)

Docker Compose 사용 시, 같은 호스트 디렉터리를 n8n과 backend가 각각 다른 경로로 참조합니다.

| 구분                   | 공통 변수                         | 컨테이너 내 경로      | 용도                                        |
| ---------------------- | --------------------------------- | --------------------- | ------------------------------------------- |
| **호스트**             | `PAB_PROJECT_ROOT` (.env)         | —                     | 프로젝트 루트 (상대 `.` 또는 절대 경로)     |
| **n8n**                | `WORKSPACE_ROOT`                  | `/workspace`          | 워크플로우·스크립트가 읽/쓰는 프로젝트 루트 |
| **backend**            | `PROJECT_ROOT` / `WORKSPACE_ROOT` | `/app`                | API·정적 파일(web) 기준 경로                |
| **n8n → backend 호출** | `BACKEND_URL`                     | `http://backend:8000` | n8n HTTP Request 노드에서 사용              |

- **설정**: `cp .env.example .env` 후 `PAB_PROJECT_ROOT=.` (또는 절대 경로). docker-compose는 `.env`를 자동으로 읽습니다.
- **파일 공유**: n8n이 `/workspace/brain/foo.md`에 쓰면 backend는 `/app/brain/foo.md`로 같은 파일을 참조합니다 (동일 호스트 디렉터리 마운트).
