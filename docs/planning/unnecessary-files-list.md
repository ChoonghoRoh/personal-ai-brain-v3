# 불필요한 폴더/파일 목록 (현재 프로젝트 기준)

**작성일**: 2026-02-08
**목적**: ver3 프로젝트에서 삭제·정리 후보 색출

---

## 1. 삭제 권장 (명확히 불필요)

| 경로                                                    | 사유                                                                           | 용량   |
| ------------------------------------------------------- | ------------------------------------------------------------------------------ | ------ |
| **test.md**                                             | 컨테이너 내부 `ls` 출력이 붙여 넣어진 임시 파일. 프로젝트 문서 아님.           | 4K     |
| **README.md.backup**                                    | README 이전 버전 백업. 버전 관리(Git)로 대체 가능.                             | 80K    |
| **docs/phase-document-taxonomy.md.backup**              | 동일 문서의 백업. Git으로 복구 가능.                                           | 소규모 |
| **web/src/pages/knowledge-admin.html.backup**           | 페이지 소스 백업. Git으로 복구 가능.                                           | 소규모 |
| **web/public/js/reason/reason_backup.js**               | Reasoning 페이지 JS 백업. Git으로 복구 가능.                                   | 소규모 |
| **docs/rules/\_backup/**                                | 규칙 문서 백업 폴더(내부 1개 .md). Git으로 복구 가능.                          | ~2K    |
| **project-start-plan-step1.md**                         | 예전 "Local Test Setup (Mac + M1)" 가이드. 현재는 Docker·ver3 기준이라 미사용. | 4K     |
| **backups/pre_restore_20260208_155025.tar.gz**          | 복원 전 자동 백업(restore.sh 생성). 복원 검증 후 삭제 가능.                    | ~427B  |
| **backups/pre_restore_metadata_20260208_155025.tar.gz** | 위와 동일, 메타데이터용. 복원 검증 후 삭제 가능.                               | ~27K   |

---

## 2. 검토 후 정리 (선택)

| 경로                                       | 사유                                                                                                | 용량  | 비고           |
| ------------------------------------------ | --------------------------------------------------------------------------------------------------- | ----- | -------------- |
| **.vscode/**                               | Cursor용 `.cursor/`와 역할 중복. VSCode에서도 이 프로젝트를 연다면 유지, Cursor 전용이면 제거 검토. | ~15K  | Ver3 갱신 완료 |
| **backups/full*20260111_000102*\*.tar.gz** | 예전 full 백업 형식(메타·qdrant만). 현재는 backup_YYYYMMDD_HHMMSS 형식 사용. 보관 필요 없으면 정리. | ~376K | 레거시         |
| **backups/full*20260204_094017*\*.tar.gz** | 위와 동일.                                                                                          | ~378K | 레거시         |
| **logs/**                                  | 런타임 로그 폴더. 비어있음. 필요시만 보관.                                                          | 0B    | 자동 생성됨    |
| **playwright-report/**                     | E2E 테스트 리포트. 테스트 실행 시마다 재생성.                                                       | ~524K | 자동 생성됨    |
| **test-results/**                          | pytest 결과 폴더. 비어있음.                                                                         | 4K    | 자동 생성됨    |

---

## 3. 유지 (삭제하지 않음)

| 경로                                                                              | 비고                                                  |
| --------------------------------------------------------------------------------- | ----------------------------------------------------- |
| **backups/backup_20260208_154209/**                                               | ver3 복원에 사용한 백업. 유지.                        |
| **backups/backup_20260206_022500/**                                               | 이전 백업본. 필요시 참조용으로 유지.                  |
| **backups/backup_metadata.json**                                                  | 백업 메타데이터. 유지.                                |
| **brain/**, **docs/**, **backend/**, **scripts/**, **e2e/**, **tests/**, **web/** | 프로젝트 소스·문서·테스트. 유지.                      |
| **.cursor/**, **.github/**                                                        | Cursor 설정·CI. 유지.                                 |
| **postgres-data/**                                                                | PostgreSQL 데이터베이스 저장소. 유지 (Docker volume). |
| **qdrant-data-ver3/**                                                             | Qdrant 벡터 DB 저장소. Ver3 갱신 완료.                |
| **node_modules/**                                                                 | Playwright 및 npm 의존성. 유지 (.gitignore 처리).     |

---

## 4. 삭제 시 참고

- **백업 파일(\*.backup, \_backup/)**
  - Git에 이전 버전이 있으면 `git checkout -- <path>` 등으로 복구 가능.
  - 삭제 전 `git status`로 추적 여부 확인 권장.

- **pre*restore*\***
  - `scripts/backup/restore.sh`가 복원 전에 만든 자동 백업.
  - ver3 복원(backup_20260208_154209)이 정상이면 삭제해도 됨.

- **.vscode/**
  - 삭제 시 VSCode에서 이 워크스페이스를 열 때 프로젝트 전용 설정만 없어짐.
  - 사용하지 않으면 제거해도 동작에는 영향 없음.

---

## 5. 요약

- **즉시 삭제 권장**: 9개 항목 (§1) - ~190K 용량
- **검토 후 정리**: 6개 항목 (§2) - 자동 생성 및 레거시 포함
- **유지**: §3 참고

### 우선순위

1. **높음**: test.md, README.md.backup, 백업 HTML/JS (§1 상단)
2. **중간**: project-start-plan-step1.md, pre*restore*\* (§1 하단)
3. **낮음**: 레거시 full\_\*.tar.gz 백업 (§2)

삭제 후 `git add` / `git status`로 변경 범위 확인 후 커밋하는 것을 권장합니다.

---

## 6. Ver3 프로젝트 구조 정리

### 루트 레벨 필수 파일

- ✅ **docker-compose.yml** - Docker 컴포즈 설정
- ✅ **Dockerfile.backend** - 백엔드 도커 이미지
- ✅ **requirements.txt** - Python 의존성
- ✅ **requirements-docker.txt** - Docker용 Python 의존성
- ✅ **package.json** - Node.js 의존성 (Playwright)
- ✅ **pytest.ini** - pytest 설정
- ✅ **pyproject.toml** - Python 프로젝트 설정
- ✅ **playwright.config.js** - Playwright E2E 테스트 설정
- ✅ **README.md** - 프로젝트 메인 가이드

### 데이터 & 설정 폴더

| 폴더                  | 용도                               | 크기 |
| --------------------- | ---------------------------------- | ---- |
| **backend/**          | FastAPI 백엔드 서버                | 3.4M |
| **web/**              | 프론트엔드 (HTML/JS)               | 996K |
| **tests/**            | pytest 단위/통합 테스트            | 460K |
| **e2e/**              | Playwright E2E 테스트              | 72K  |
| **docs/**             | 프로젝트 문서 (Phase별, 가이드 등) | 4.9M |
| **scripts/**          | 유틸리티 스크립트 (DB, 백업 등)    | 979M |
| **brain/**            | 로컬 지식 저장소                   | 156K |
| **backups/**          | 백업 파일 (DB/Qdrant)              | 1.0M |
| **postgres-data/**    | PostgreSQL 데이터                  | 46M  |
| **qdrant-data-ver3/** | Qdrant 벡터 DB (Ver3)              | 11M  |

### 에디터 & 설정

| 폴더         | 용도                                   |
| ------------ | -------------------------------------- |
| **.cursor/** | Cursor IDE 설정 (유지 권장)            |
| **.vscode/** | VSCode 설정 (Cursor 전용 시 제거 검토) |
| **.github/** | GitHub Actions 워크플로우              |
| **.git/**    | Git 저장소                             |
| **.env**     | 환경 변수 (공개 금지)                  |
