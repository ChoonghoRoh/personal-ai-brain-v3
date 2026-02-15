# 개요 및 빠른 시작 (전문 유지)

**출처**
원문: `README.md.backup` 1~1913라인.
기존 내용 최대한 유지.
프로젝트 개요·주요 기능·프로젝트 구조·아키텍처·시작하기·사용 예시·기술 스택·완료/향후 계획.

- phase1 ~ phase7까지 완료
- phase8-1 ~ phase8-3 까지 기록

---

# Personal AI Brain

로컬 환경에서 실행하는 개인 AI 브레인 시스템입니다. Markdown, PDF, DOCX 문서를 벡터 데이터베이스에 저장하고, 의미 기반 검색과 AI 응답을 제공합니다. 웹 인터페이스를 통해 브라우저에서 모든 기능을 사용할 수 있습니다.

## 🎯 주요 기능

### 핵심 기능

- **문서 임베딩**: Markdown, PDF, DOCX 파일을 자동으로 임베딩하여 Qdrant에 저장
- **의미 기반 검색**: 자연어 쿼리로 관련 문서 검색
- **AI 응답 생성**: Ollama를 사용한 컨텍스트 기반 응답 생성 (로컬 LLM, EEVE-Korean 등)

### 자동화 기능

- **자동 변경 감지**: 파일 변경 시 자동으로 임베딩 갱신
- **Git 자동 커밋**: 변경사항 자동 커밋 및 기록
- **작업 로그 관리**: 모든 작업 이력을 중앙에서 통합 관리
- **시스템 상태 관리**: 시스템 상태, 컨텍스트, TODO 자동 생성
- **키워드 자동 추출**: 문서에서 키워드를 자동 추출하여 라벨 생성 및 청크 자동 라벨링

## 📁 프로젝트 구조

현행 구조(2026 기준). `brain/reference/`, 루트 `collector/`는 collector.py 실행 시 생성·사용됩니다.

```
personal-ai-brain/
├── brain/
│   ├── projects/       # 프로젝트별 문서
│   └── system/         # 시스템 관리 파일
│       ├── work_log.md      # 통합 작업 로그
│       ├── work_log.json    # 작업 로그 데이터
│       ├── status.md        # 시스템 상태
│       ├── context.md       # 시스템 컨텍스트
│       └── todo.md          # TODO 목록
├── scripts/
│   ├── backend/        # 임베딩·검색·서버
│   │   ├── embed_and_store.py   # 문서 임베딩 및 저장
│   │   ├── search_and_query.py  # 검색 및 질의
│   │   ├── start_server.py      # 웹 서버 실행
│   │   └── ...
│   ├── devtool/        # 자동화·유틸
│   │   ├── watcher.py           # 파일 변경 감지
│   │   ├── auto_commit.py      # Git 자동 커밋
│   │   ├── collector.py        # PDF/DOCX 수집 (→ brain/reference/ 출력)
│   │   ├── system_agent.py     # 시스템 상태 관리
│   │   ├── work_logger.py      # 작업 로그 관리
│   │   ├── check_data_sync.py  # 데이터 일관성 확인
│   │   ├── sync_data.py        # 데이터 동기화
│   │   ├── verify_and_sync.sh  # 통합 동기화 스크립트
│   │   └── ...
│   ├── db/             # DB 초기화·마이그레이션
│   │   ├── init_db.py
│   │   └── ...
│   └── n8n/            # n8n 연동 스크립트
├── backend/            # FastAPI 백엔드
│   ├── main.py
│   ├── routers/        # 용도별 하위 패키지 (search, system, ai, knowledge, reasoning, cognitive, automation, ingest)
│   ├── services/
│   └── config.py
├── web/                # 웹 프론트엔드 (정적·템플릿)
│   ├── src/
│   │   ├── pages/      # admin/, knowledge/, dashboard·search·document·ask·logs·reason 등
│   │   └── js/         # 공통 컴포넌트 (header-component, layout-component, document-utils)
│   └── public/
│       ├── css/        # 기능별 (admin/, knowledge/ 등)
│       └── js/         # 기능별 (components/, admin/, knowledge/, search/ 등)
├── docs/               # 프로젝트 문서
│   ├── phases/         # Phase별 계획·작업 (phase-2-0, phase-3-0, ... phase-8-3)
│   ├── manual/         # 사용자 매뉴얼 (access-guide, manual-knowledge-admin, manual-knowledge-studio, manual-reasoning-lab)
│   ├── README/         # 개요·아키텍처·진행 등 (이 문서 포함)
│   ├── n8n/, db/, ai/, overview/, prompts/, scripts/ 등
│   └── ...
├── backups/            # 백업 데이터 (선택)
└── qdrant-data/        # Qdrant 데이터 저장소
```

## 🏗 아키텍처 및 구조 변경

- **Backend (FastAPI)**

  - **routers/** · **services/** 는 **용도별 하위 패키지**로 구분됩니다.
  - 패키지: `search`, `system`, `ai`, `knowledge`, `reasoning`, `cognitive`, `automation`, `ingest`.
  - 상세: `backend/routers/README.md`, `backend/services/README.md`.

- **Web (정적·템플릿)**

  - **public/css**, **public/js** 는 용도별 하위 폴더 사용 (예: `js/components/`, `js/admin/`, `js/knowledge/`, `js/search/` 등).
  - **src/pages/** 에는 `admin/`, `knowledge/` 그룹이 있으며, 루트에 dashboard·search·document·ask·logs·reason 페이지가 있습니다.
  - 상세: `web/README.md`.

- **실행 환경**

  - **Docker Compose**: `postgres`, `qdrant`, **ollama(로컬 LLM, 별도 컨테이너)**, **backend(Python 컨테이너)**, `n8n` 서비스.
  - **Ollama**: 별도 컨테이너로 분리 (`ollama/ollama:latest`, 포트 11434). Backend는 `OLLAMA_BASE_URL=http://ollama:11434`, `OLLAMA_MODEL`로 연동. 모델은 컨테이너 기동 후 수동 로드. 상세: [02-architecture.md](02-architecture.md).
  - Backend 설정은 **환경 변수**로 오버라이드 (`backend/config.py`: `DATABASE_URL`, `QDRANT_HOST`, `QDRANT_PORT`, `PROJECT_ROOT` 등).
  - 이미지: `Dockerfile.backend` (Python 3.12, uvicorn).

- **의존성**
  - Backend 패키지 목록: 루트 `requirements.txt` (실행·설정·아키텍처 요약이 파일 상단 주석에 있음).

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

## 🚀 시작하기

### 0. Docker Compose로 한 번에 실행 (권장)

PostgreSQL, Qdrant, **Ollama(로컬 LLM)**, **FastAPI 백엔드(Python 컨테이너)**, n8n을 한 번에 띄웁니다.

```bash
# 프로젝트 루트에서
docker-compose up -d

# 백엔드만 빌드·실행 (이미지 최초 빌드 시 시간 소요)
docker-compose up -d backend
```

- **Backend API**: http://localhost:8001 (대시보드: /dashboard, API 문서: /docs)
- **n8n**: http://localhost:5678
- **Ollama**: http://localhost:11434 (로컬 LLM, EEVE-Korean 등)
- **PostgreSQL**: localhost:5432
- **Qdrant**: http://localhost:6333

로컬에서 코드 수정 시 백엔드 컨테이너는 `backend`, `web`, `brain`, `scripts` 볼륨 마운트로 반영됩니다. 재시작은 `docker-compose restart backend`로 할 수 있습니다.

**로컬 LLM (Ollama)**: AI 질의·키워드 추출은 **Ollama** 서비스로 연결됩니다. 컨테이너 기동 후 **모델을 한 번 로드**해야 합니다.

- **기본 모델(저메모리)**: `exaone3.5:2.4b` — Ollama 라이브러리 제공, 한국어/영어, 약 1.6GB, **7GB 이하 환경에서 동작**. (추론·의미 기반 키워드 품질은 상대적으로 약함.)
- **추론·키워드 품질 우선(8GB)**: `qwen2.5:3b` — 다국어(한국어 포함), ~2GB, 키워드 추론·의미 분석에 유리. [docs/ai/8gb-inference-and-keyword-alternatives.md](../../ai/8gb-inference-and-keyword-alternatives.md) 참고.
- **고품질(고메모리)**: `bnksys/yanolja-eeve-korean-instruct-10.8b` — **약 11.3 GiB 필요**. 시스템 메모리 부족(7.3 GiB 등) 시 2.4B 또는 qwen2.5:3b 사용.

```bash
# 기본: exaone3.5:2.4b (Ollama 라이브러리)
docker exec -it ollama ollama run exaone3.5:2.4b

# 추론·키워드 품질 우선: qwen2.5:3b (OLLAMA_MODEL=qwen2.5:3b 설정 후)
docker exec -it ollama ollama pull qwen2.5:3b

# 12GB+ RAM 있을 때: 10.8B
docker exec -it ollama ollama run bnksys/yanolja-eeve-korean-instruct-10.8b
```

모델이 없으면 대시보드에서 "로컬 LLM (Ollama): 미설치"로 표시되며, AI 질의 시 폴백 메시지가 반환됩니다. `OLLAMA_MODEL` 환경 변수로 사용할 모델을 변경할 수 있습니다. 8GB에서 추론 품질이 부족하면 [8gb-inference-and-keyword-alternatives.md](../../ai/8gb-inference-and-keyword-alternatives.md)에서 외부 API·하이브리드 등 대안을 참고하세요.

### 1. 환경 설정 (로컬 실행 시)

```bash
# 가상환경 활성화
cd scripts
source venv/bin/activate
```

### 2. Qdrant 실행

```bash
# Docker로 Qdrant 실행 (프로젝트 루트에서)
docker run -d -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant-data:/qdrant/storage \
  --name qdrant qdrant/qdrant
```

### 3. 문서 임베딩 및 저장

```bash
# brain 디렉토리의 모든 .md 파일을 임베딩하여 저장
python scripts/backend/embed_and_store.py

# Qdrant 컬렉션 재생성 (기존 데이터 삭제 후 재생성)
python scripts/backend/embed_and_store.py --recreate

# 데이터 일관성 확인
python scripts/devtool/check_data_sync.py

# 데이터 동기화 (불일치 시 자동 동기화)
python scripts/devtool/sync_data.py
```

### 4. 검색 및 질의

```bash
# 간단한 검색
python scripts/backend/search_and_query.py "프로젝트 목적"

# 대화형 검색 모드
python scripts/backend/search_and_query.py

# 로컬 LLM 사용: 웹 대시보드의 AI 질의 또는 Backend API 권장 (Ollama 연동)
# CLI에서 로컬 LLM 사용 시 (레거시: --gpt4all 옵션 지원)
python scripts/backend/search_and_query.py "프로젝트 목적" --gpt4all
```

### 5. 자동 변경 감지 (옵션)

```bash
# 파일 변경 시 자동으로 임베딩 갱신
python scripts/devtool/watcher.py
```

### 6. Git 자동 커밋 및 푸시

```bash
# 변경사항 자동 커밋 (원격 저장소가 있으면 자동으로 GitHub에 푸시)
python scripts/devtool/auto_commit.py

# 강제로 푸시 (원격 저장소가 없어도 시도)
python scripts/devtool/auto_commit.py --push

# 푸시하지 않음 (원격 저장소가 있어도 푸시 안함)
python scripts/devtool/auto_commit.py --no-push

# 커밋 메시지 직접 지정
python scripts/devtool/auto_commit.py -m "커밋 메시지"
```

**참고**: 원격 저장소(`origin`)가 설정되어 있으면 기본적으로 자동으로 GitHub에 푸시합니다.
원격 저장소를 설정하려면:

```bash
git remote add origin https://github.com/username/repository.git
```

### 7. 문서 수집 (PDF/DOCX)

```bash
# 루트 collector/ 디렉터리(없으면 스크립트가 생성)의 PDF/DOCX를 Markdown으로 변환하여 brain/reference/에 저장
python scripts/devtool/collector.py
```

### 8. 시스템 상태 관리

```bash
# 시스템 상태, 컨텍스트, TODO 자동 생성
python scripts/devtool/system_agent.py
```

### 9. 작업 로그 관리

```bash
# 작업 로그 확인 (Markdown)
cat brain/system/work_log.md

# 최근 작업 보기
python scripts/devtool/work_logger.py recent 10

# 오래된 항목 정리 (90일 이전)
python scripts/devtool/work_logger.py cleanup 90

# Markdown 재생성
python scripts/devtool/work_logger.py regenerate
```

### 10. 웹 서버 실행 (로컬)

Docker Compose를 쓰지 않을 때는 아래처럼 로컬에서 실행합니다.

```bash
# FastAPI 웹 서버 실행 (PostgreSQL·Qdrant는 docker-compose 또는 개별 컨테이너로 먼저 실행)
cd scripts
source venv/bin/activate
python backend/start_server.py
```

서버 실행 후:

- 대시보드: http://localhost:8001/dashboard
- 검색: http://localhost:8001/search
- API 문서: http://localhost:8001/docs

## 📝 사용 예시

### 문서 추가

`brain/projects/`에 Markdown 파일을 추가한 후 (collector.py 실행 후에는 `brain/reference/`에도 변환된 문서가 있음):

```bash
python scripts/backend/embed_and_store.py
```

### 검색

```bash
# 명령줄에서 검색
python scripts/backend/search_and_query.py "임베딩 테스트"

# 대화형 모드
python scripts/backend/search_and_query.py
# 질문을 입력하세요: 프로젝트 목적은?
```

## 🔧 기술 스택

- **벡터 DB**: Qdrant (Docker)
- **지식 DB**: PostgreSQL (Docker)
- **임베딩 모델**: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
- **LLM**: Ollama (로컬, EEVE-Korean 10.8B / Bllossom 3B 등, Phase 8-3에서 gpt4all→Ollama 전환)
- **파일 감시**: watchdog
- **문서 처리**: pypdf, python-docx
- **웹 프레임워크**: FastAPI, Uvicorn
- **ORM**: SQLAlchemy
- **Python**: 3.12+

## 📚 다음 단계

### 완료된 기능 ✅

- [x] 자동 기록 업데이트 설계 및 구현
- [x] Git 자동 커밋 자동화
- [x] PDF/DOCX 파일 지원 확장
- [x] 시스템 관리 AI 구축
- [x] 통합 작업 로그 시스템
- [x] 웹 인터페이스 추가 (Phase 4.1 완료)
- [x] 웹 UI 확장 (Phase 4.2 - Document Viewer, AI Ask Panel 완료)
- [x] 웹 UI 고도화 (Phase 4.3 - Log Viewer, 검색 UX 개선, 대시보드 고도화 완료)
- [x] 대시보드 문서 목록 기능 추가
- [x] 문서 뷰어 오류 수정 및 이중 인코딩 문제 해결
- [x] PostgreSQL 지식 DB 도입 (Phase 5.1 완료)
- [x] 지식 라벨링 시스템 (Phase 5.2 완료)
- [x] 지식 관계 그래프 구축 (Phase 5.3 완료)
- [x] Reasoning Pipeline 구축 (Phase 5.4 완료)
- [x] 통합 검증 및 회귀 테스트 (Phase 5.5 완료)
- [x] 지식 구조 및 Reasoning 웹 UI 구축 (Phase 6 완료)
- [x] 검증 시나리오 작성
- [x] 데이터 동기화 패턴 생성
- [x] 프론트엔드 공통 컴포넌트화 (Header, Layout)
- [x] 프론트엔드 보안 개선 및 오류 수정
- [x] 키워드 추출 및 자동 라벨링 기능 (Phase 7.6 완료)
- [x] 프론트엔드 코드 리팩토링 - 스크립트 및 CSS 분리 (Phase 7.9.7-8 완료)
- [x] AI 질의 기능 개선 - 한국어 답변 강제 및 컨텍스트 윈도우 최적화 (Phase 7.9.9 완료)
- [x] 코드 개선 작업 - 보안 취약점 수정, 리팩토링, 중복 코드 제거, 에러 처리 개선, 주석 추가 (Phase 7.9.9 코드 리뷰 완료)
