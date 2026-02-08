# Personal AI Brain Ver3 - 전체 프로젝트 구조 분석

**작성일**: 2026-02-08
**기준**: Ver3 리팩토링 완료 후
**목적**: 프로젝트 폴더 구조, 데이터, 설정의 완전한 이해

---

## 1. 루트 디렉터리 구성

### 1.1 프로젝트 설정 파일

```
📄 docker-compose.yml          # 전체 Docker 서비스 오케스트레이션
📄 Dockerfile.backend          # FastAPI 백엔드 Docker 이미지
📄 requirements.txt            # Python 의존성 (로컬 개발)
📄 requirements-docker.txt     # Python 의존성 (Docker 환경)
📄 package.json                # Node.js 의존성 (Playwright)
📄 package-lock.json           # 의존성 lock 파일
📄 pytest.ini                  # pytest 설정 및 마커
📄 pyproject.toml              # Python 프로젝트 메타데이터
📄 playwright.config.js        # E2E 테스트 설정
📄 README.md                   # 프로젝트 메인 가이드 (14KB)
📄 .env                        # 환경 변수 (공개 금지)
📄 .env.example                # 환경 변수 샘플
📄 .dockerignore               # Docker 빌드 제외 파일
📄 .gitignore                  # Git 추적 제외 설정
```

### 1.2 에디터 & CI/CD 설정

```
📁 .cursor/                    # Cursor IDE 설정
   ├── settings.json           # 편집기 설정
   ├── keybindings.json        # 키바인딩
   ├── extensions.json         # 추천 확장
   ├── .cursorignore           # Cursor 무시 파일
   └── rules/                  # Cursor AI 규칙

📁 .vscode/                    # VSCode 설정 (Ver3 갱신 완료)
   ├── settings.json           # postgres-data, qdrant-data-ver3 제외
   ├── extensions.json         # 추천 확장
   └── keybindings.json        # 키바인딩

📁 .github/                    # GitHub Actions
   └── workflows/              # CI/CD 자동화

📁 .git/                       # Git 저장소 정보
```

---

## 2. 핵심 프로젝트 폴더

### 2.1 Backend 구조 (3.4MB)

```
📁 backend/
├── 📄 main.py                 # FastAPI 진입점
├── 📄 config.py               # 환경 설정
│
├── 📁 routers/                # API 라우터 (기능별)
│   ├── admin/                 # Admin 설정 관리 (Phase 11)
│   ├── ai/                    # AI 대화 & 추천
│   ├── auth/                  # 인증 (JWT, 세션)
│   ├── automation/            # 자동화 워크플로우
│   ├── cognitive/             # 메모리, 학습, 개성
│   ├── ingest/                # 파일 업로드 & 파싱
│   ├── knowledge/             # 지식 CRUD & 관리
│   ├── reasoning/             # Reasoning Lab (Phase 10)
│   ├── search/                # 하이브리드 검색
│   └── system/                # 백업, 로그, 통계, 무결성
│
├── 📁 models/                 # 데이터 모델 & DB
│   ├── database.py            # SQLAlchemy 모델
│   ├── models.py              # 비즈니스 모델
│   ├── admin_models.py        # Admin 데이터 모델
│   └── workflow_common.py     # 워크플로우 공통 모델
│
├── 📁 services/               # 비즈니스 로직
│   ├── search_service.py
│   ├── knowledge_service.py
│   ├── reasoning_service.py
│   ├── backup_service.py
│   └── ...
│
├── 📁 middleware/             # 요청 처리 미들웨어
│   ├── auth.py                # 인증 (Phase 9-1)
│   ├── rate_limit.py          # 속도 제한
│   ├── security.py            # 보안 헤더
│   └── __init__.py
│
├── 📁 utils/                  # 유틸리티 함수
│
├── 📁 logs/                   # 런타임 로그 (자동 생성)
│
├── 📁 __pycache__/            # Python 바이트코드 (무시됨)
│
└── 📄 __init__.py
```

### 2.2 Frontend 구조 (996KB)

```
📁 web/
├── 📄 README.md              # 웹 개발 가이드
│
└── 📁 src/
    │
    ├── 📁 pages/             # HTML 페이지
    │   ├── admin/            # Admin 페이지 그룹
    │   │   ├── settings/     # 설정 관리 (Phase 11-3)
    │   │   │   ├── schema-settings.html
    │   │   │   ├── template-settings.html
    │   │   │   ├── preset-settings.html
    │   │   │   ├── rag-profile-settings.html
    │   │   │   └── policy-settings.html
    │   │   ├── approval.html
    │   │   ├── statistics.html
    │   │   ├── groups.html
    │   │   ├── labels.html
    │   │   └── knowledge-admin.html (.backup 파일 제거 권장)
    │   │
    │   ├── knowledge/        # 지식 관리 페이지
    │   │
    │   ├── dashboard.html    # 메인 대시보드
    │   ├── reason.html       # Reasoning Lab UI (Phase 10)
    │   ├── search.html       # 검색 페이지
    │   ├── ask.html          # AI 대화 페이지
    │   └── ...
    │
    ├── 📁 public/            # 정적 자산
    │   └── 📁 js/            # JavaScript 모듈
    │       ├── 📁 admin/     # Admin UI 컴포넌트
    │       ├── 📁 knowledge/ # 지식 관리 컴포넌트
    │       ├── 📁 reason/    # Reasoning Lab
    │       │   ├── reason.js
    │       │   ├── reason_backup.js (.backup 파일 제거 권장)
    │       │   └── ...
    │       ├── 📁 search/    # 검색 컴포넌트
    │       ├── 📁 common/    # 공통 유틸리티
    │       ├── api-client.js # API 호출 모듈
    │       └── ...
    │
    └── 📁 node_modules/      # npm 의존성 (.gitignore 처리)
```

### 2.3 테스트 구조 (460KB)

```
📁 tests/
├── 📄 conftest.py            # pytest 픽스처 & 설정
├── 📄 __init__.py
│
├── 📄 test_admin_api.py       # Admin API 테스트
├── 📄 test_ai_api.py          # AI API 테스트
├── 📄 test_api_routers.py     # 라우터 테스트
├── 📄 test_hybrid_search.py   # 하이브리드 검색 테스트
├── 📄 test_knowledge_api.py   # 지식 API 테스트
├── 📄 test_models.py          # 데이터 모델 테스트
├── 📄 test_reasoning_api.py   # Reasoning API 테스트
├── 📄 test_reasoning_recommendations.py  # 추천 테스트
├── 📄 test_search_service.py  # 검색 서비스 테스트
├── 📄 test_structure_matching.py
├── 📄 test_task_plan_generator.py
│
├── 📁 integration/            # 통합 테스트
│
└── 📁 __pycache__/            # 바이트코드 (무시됨)
```

### 2.4 E2E 테스트 (Playwright, 72KB)

```
📁 e2e/
├── 📄 smoke.spec.js           # 기본 동작 테스트
├── 📄 phase-9-1.spec.js       # Phase 9-1 (보안, 인증)
├── 📄 phase-9-3.spec.js       # Phase 9-3
├── 📄 phase-10-1.spec.js      # Phase 10-1 (Reasoning 기본)
├── 📄 phase-10-1-mcp-scenarios.spec.js  # MCP 시나리오
├── 📄 phase-10-2.spec.js
├── 📄 phase-10-3.spec.js
├── 📄 phase-10-4.spec.js      # Phase 10-4 (공유 기능)
├── 📄 phase-11-2.spec.js
└── 📄 phase-11-3.spec.js      # Phase 11-3 (Admin 설정)
```

### 2.5 문서 구조 (4.9MB)

```
📁 docs/
├── 📄 README.md
│
├── 📁 overview/               # 프로젝트 개요
│   ├── vscode-overview-260208.md
│   ├── cursor-overview-260208.md
│   ├── project-overview-2026-01-11.md
│   └── ...
│
├── 📁 phases/                 # Phase별 계획 & 요약
│   ├── phase-09-summary.md
│   ├── phase-10-summary.md
│   ├── phase-11-summary.md
│   └── ...
│
├── 📁 rules/                  # 개발 규칙 (Phase 11 개선)
│   ├── ai/                    # AI 프롬프트 & 규칙
│   ├── backend/               # Backend 컨벤션
│   ├── common/                # 공통 규칙
│   ├── prompts/               # Agent 프롬프트
│   ├── templates/             # 검증 템플릿
│   ├── testing/               # 테스트 가이드
│   ├── rules-and-conventions.md
│   └── _backup/               # 이전 버전 (.backup 제거 권장)
│
├── 📁 planning/               # 계획 & 정리
│   ├── unnecessary-files-list.md (본 문서 참고)
│   ├── project-structure-v3-comprehensive.md (본 파일)
│   └── ...
│
├── 📁 ai/                     # AI 관련 문서
│   ├── prompts/               # LLM 프롬프트
│   └── ...
│
├── 📁 db/                     # 데이터베이스
│   ├── schema-design.md       # 스키마 설계
│   ├── migration-guide.md     # 마이그레이션
│   └── ...
│
├── 📁 devtest/                # 개발 테스트 가이드
├── 📁 webtest/                # 웹 테스트 가이드
├── 📁 execution/              # 실행 가이드
├── 📁 features/               # 기능 문서
├── 📁 manual/                 # 수동 작업 가이드
├── 📁 n8n/                    # N8N 워크플로우 문서
├── 📁 prompts/                # 프롬프트 모음
├── 📁 README/                 # README 모음
├── 📁 review/                 # 검토 & 개선 기록
├── 📁 scripts/                # 스크립트 문서
│
└── 📁 webtest/                # 웹 테스트 문서
```

### 2.6 스크립트 유틸리티 (979MB - 용량 큼)

```
📁 scripts/
├── 📄 __init__.py
├── 📄 README.md               # 스크립트 사용 가이드
│
├── 📄 docker-compose-up.sh    # Docker 시작 스크립트
├── 📄 llm_server_check.py     # LLM 서버 상태 확인
├── 📄 webtest.py              # 웹 테스트 실행
│
├── 📁 db/                     # DB 마이그레이션 & 시딩
│   ├── init_db.py
│   ├── seed_data.py
│   └── migration/
│
├── 📁 backup/                 # 백업 스크립트
│   ├── backup.sh
│   └── restore.sh             # 복원 시 pre_restore_* 자동 생성
│
├── 📁 devtool/                # 개발 도구
│   ├── quick_test.py
│   └── ...
│
├── 📁 n8n/                    # N8N 워크플로우 초기화
│
└── 📁 web/                    # 웹 테스트 & 초기화
```

---

## 3. 데이터 & 저장소

### 3.1 지식 저장소 (156KB)

```
📁 brain/
├── 📁 projects/               # 프로젝트별 지식
├── 📁 system/                 # 시스템 메타데이터
└── [실제 마크다운 문서들]
```

### 3.2 백업 (1.0MB)

```
📁 backups/
├── 📁 backup_20260208_154209/  # ✅ Ver3 복원에 사용한 최신 백업 (유지)
│   ├── metadata/
│   ├── qdrant/
│   └── postgres/
│
├── 📁 backup_20260206_022500/  # 이전 백업 (참조용)
│
├── 📄 backup_metadata.json      # 백업 메타데이터
│
├── 📄 full_20260111_000102_metadata.tar.gz     # ⚠️ 레거시 (삭제 검토)
├── 📄 full_20260111_000102_qdrant.tar.gz       # ⚠️ 레거시 (삭제 검토)
│
├── 📄 full_20260204_094017_metadata.tar.gz     # ⚠️ 레거시 (삭제 검토)
├── 📄 full_20260204_094017_qdrant.tar.gz       # ⚠️ 레거시 (삭제 검토)
│
├── 📄 pre_restore_20260208_155025.tar.gz       # ⚠️ 자동 백업 (삭제 가능)
└── 📄 pre_restore_metadata_20260208_155025.tar.gz  # ⚠️ 자동 백업 (삭제 가능)
```

### 3.3 데이터베이스 (46MB + 11MB)

```
📁 postgres-data/              # PostgreSQL 저장소 (Docker volume)
│   ├── pg_wal/                # Write-Ahead Log
│   ├── base/                  # DB 데이터 파일
│   ├── global/                # 글로벌 객체
│   └── ...
│
📁 qdrant-data-ver3/           # ✅ Qdrant 벡터 DB (Ver3 갱신 완료)
│   ├── collections/           # 벡터 컬렉션
│   ├── qdrant.conf
│   ├── raft_state.json
│   └── ...
```

---

## 4. 테스트 & 리포트

```
📁 test-results/               # pytest 결과 (자동 생성, 비어있음)

📁 playwright-report/          # E2E 테스트 리포트 (524MB, 자동 생성)
└── index.html                 # 시각화 리포트
```

---

## 5. 불필요한 파일 (삭제 후보)

| 파일                                          | 사유                     | 대체                            |
| --------------------------------------------- | ------------------------ | ------------------------------- |
| **test.md**                                   | 임시 파일                | 삭제                            |
| **README.md.backup**                          | 버전 관리 대체           | Git `git checkout -- README.md` |
| **docs/phase-document-taxonomy.md.backup**    | 버전 관리 대체           | Git                             |
| **web/src/pages/knowledge-admin.html.backup** | 버전 관리 대체           | Git                             |
| **web/public/js/reason/reason_backup.js**     | 버전 관리 대체           | Git                             |
| **docs/rules/\_backup/**                      | 버전 관리 대체           | Git                             |
| **project-start-plan-step1.md**               | 레거시 가이드            | README.md 참고                  |
| **backups/pre*restore*\*.tar.gz**             | 자동 백업 (복원 검증 후) | 삭제 가능                       |
| **backups/full_20260\*.tar.gz**               | 레거시 형식              | 삭제 검토                       |

---

## 6. 설정 요약

### .vscode (Ver3 갱신 완료)

```json
{
  "search.exclude": {
    "qdrant-data-ver3": true, // ✅ Ver3로 갱신
    "postgres-data": true,
    "**/__pycache__": true,
    "**/.pytest_cache": true,
    "**/node_modules": true,
    "**/.venv": true,
    ".git": true
  },
  "python.defaultInterpreterPath": "/usr/local/bin/python3",
  "python.testing.pytestEnabled": true
}
```

### .cursor (유지)

```json
{
  "rules/": "AI 규칙 디렉터리",
  "settings.json": "Cursor 편집기 설정",
  ".cursorignore": "Cursor 무시 파일"
}
```

### .gitignore 주요 항목

```
.env
node_modules/
__pycache__/
.pytest_cache/
.mypy_cache/
postgres-data/
qdrant-data-ver3/
playwright-report/
logs/
test-results/
```

---

## 7. 다음 단계

1. **불필요한 파일 정리**
   - 백업 파일 제거 (§5 참고)
   - 용량 효율성 개선

2. **Git 커밋**

   ```bash
   git add .
   git status  # 변경 확인
   git commit -m "Clean up: Remove legacy backups and temporary files (Ver3)"
   ```

3. **문서 동기화**
   - `.vscode/` 및 `.cursor/` 설정 정기적 검토
   - 프로젝트 구조 변경 시 본 문서 업데이트

4. **CI/CD 자동화**
   - `.github/workflows/` 확인 및 유지
   - E2E 테스트 추가 개선

---

## 8. 참고

- **프로젝트 개요**: [docs/overview/vscode-overview-260208.md](../overview/vscode-overview-260208.md)
- **불필요한 파일 목록**: [unnecessary-files-list.md](unnecessary-files-list.md)
- **Backend API 가이드**: [docs/README/](../README/)
