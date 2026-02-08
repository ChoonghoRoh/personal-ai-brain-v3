# Personal AI Brain

로컬에서 실행하는 개인 AI 브레인: Markdown/PDF/DOCX를 벡터 DB에 저장하고, 의미 검색·AI 응답·지식 구조화·Reasoning을 제공합니다. (n8n 워크플로우는 Phase 8 보류로 Docker에서 주석 처리됨.)

---

## 현재까지 내용 요약 (2026-02-07)

| 구분              | 내용                                                                                                                                                                                                                                                                                                                                                                            |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Phase 9**       | 9-1~9-5 Task 반영·검증 완료. 보안(인증/CORS/Rate Limit), 테스트(API·통합·CI), AI 고도화(RAG·Reasoning 추천·지식 매칭), 기능 확장(HWP·통계·백업), 코드 품질(mypy·문서화). [phase-9-final-summary-report.md](docs/phases/phase-9-final-summary-report.md)                                                                                                                         |
| **Phase 10**      | Reasoning 페이지 고도화 계획 확정. 10-1 UX/UI → 10-2 모드별 시각화 → 10-3 결과물 형식 → 10-4 고급 기능(선택). Plan·Todo·Task 문서 및 [phase-10-navigation.md](docs/phases/phase-10-navigation.md) 작업 순서 정의. [phase-10-master-plan.md](docs/phases/phase-10-master-plan.md)                                                                                                |
| **Phase 10 완료** | 10-1~10-4 구현·검증 완료. E2E 통과. [phase-10-final-summary-report.md](docs/phases/phase-10-final-summary-report.md) — 다음 권장: Phase 11 계획 시 회귀 테스트 범위 확장.                                                                                                                                                                                                       |
| **Phase 11**      | Admin 설정 관리 시스템 구축. 11-1 DB 스키마·마이그레이션 → 11-2 Admin 설정 Backend API → 11-3 Admin UI → 11-4 통합 테스트·운영 준비 → 11-5 Phase 10 고도화. [phase-11-master-plan.md](docs/phases/phase-11-master-plan.md), [phase-11-navigation.md](docs/phases/phase-11-navigation.md)                                                                                        |
| **Phase 11-5**    | Phase 10 고도화(§2.1~§2.5) 완료. 11-5-1·2 검토·계획, 11-5-3~6 선택 항목(성능·시각화·접근성·공유·저장), 11-5-7 회귀·E2E·Phase 11 연동. [phase-11-5-plan.md](docs/phases/phase-11-5/phase-11-5-plan.md), [phase-10-improvement-plan.md](docs/phases/phase-11-5/phase-10-improvement-plan.md)                                                                                      |
| **Phase 11-5 webtest 요약** | E2E 29/29 통과, 2차 webtest·MCP-Cursor 시나리오. [phase-11-5-webtest-execution-report.md](docs/webtest/phase-11-5/phase-11-5-webtest-execution-report.md) |
| **통합 테스트**   | [docs/devtest](docs/devtest) — 통합 테스트 가이드·시나리오·리포트 규정 (Phase 11-4 연계).                                                                                                                                                                                                                                                                                       |
| **작업 로그**     | [brain/system/work_log.md](brain/system/work_log.md), 일자별: [work_log_260207.md](brain/system/work_log_260207.md), [work_log_260204.md](brain/system/work_log_260204.md)                                                                                                                                                                                                     |

---

## 이슈·개발 과정 (요약)

| 구분                   | 내용                                                                                                                                 |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| **Phase 8 워크플로우** | 보류. n8n 워크플로우 개발은 별도 프로젝트 권장. [docs/phases/phase-8-wrap-up.md](docs/phases/phase-8-wrap-up.md)                     |
| **n8n Docker**         | 기본 실행 시 n8n 컨테이너는 기동하지 않음 (`docker-compose.yml`에서 주석 처리). 재활성화 시 해당 블록 주석 해제.                     |
| **리팩토링 시**        | n8n 관련 부분(n8n 서비스, docs/n8n, Phase 8-2 워크플로우 전용)은 제외하고 진행. [phase-8-wrap-up.md](docs/phases/phase-8-wrap-up.md) |

상세: [docs/README/07-issues-and-future.md](docs/README/07-issues-and-future.md), [docs/README/03-development-progress.md](docs/README/03-development-progress.md).

---

## AI/개발자용 네비게이션

**수정·판단·작성 시**: 아래 링크를 우선 참고. 상세는 각 문서에 있으며, 이 README는 진입점만 유지.

| 구분                   | 문서                                                                                                       | 용도                                                                               |
| ---------------------- | ---------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| **개요·시작**          | [docs/README/01-overview-and-quickstart.md](docs/README/01-overview-and-quickstart.md)                     | 한 줄 설명, 빠른 시작, 기능 요약                                                   |
| **아키텍처**           | [docs/README/02-architecture.md](docs/README/02-architecture.md)                                           | 디렉터리 구조, Backend/Web/실행환경, 기술 스택                                     |
| **개발 진행**          | [docs/README/03-development-progress.md](docs/README/03-development-progress.md)                           | 진행 단계 표 + Phase별 **전문** 문서 링크 (03-phase-1-4, 03-phase-5-7, 03-phase-8) |
| **n8n 구조**           | [docs/README/08-n8n-project-structure.md](docs/README/08-n8n-project-structure.md)                         | n8n 프로젝트 구조·생성된 파일·규칙·마이그레이션 결과 **전문**                      |
| **룰·규약**            | [docs/README/04-rules-and-conventions.md](docs/README/04-rules-and-conventions.md)                         | 문서 분류(Taxonomy), n8n 규칙, AI 룰, Phase 폴더 규칙                              |
| **DB 구조**            | [docs/README/05-database.md](docs/README/05-database.md)                                                   | PostgreSQL/Qdrant, 스키마 문서 링크, 마이그레이션                                  |
| **참조 문서**          | [docs/README/06-reference-docs-index.md](docs/README/06-reference-docs-index.md)                           | docs/·Backend·스크립트 문서 인덱스                                                 |
| **이슈·향후**          | [docs/README/07-issues-and-future.md](docs/README/07-issues-and-future.md)                                 | 알려진 이슈, 향후 계획, 완료 기능 체크                                             |
| **Phase 9 요약**       | [docs/phases/phase-9-final-summary-report.md](docs/phases/phase-9-final-summary-report.md)                 | Phase 9-1~9-5 Task 개발 내역·API 통합·회귀 테스트 요약                             |
| **Phase 10 계획**      | [docs/phases/phase-10-master-plan.md](docs/phases/phase-10-master-plan.md)                                 | Reasoning 페이지 고도화 (10-1~10-4)                                                |
| **Phase 10 완료 요약** | [docs/phases/phase-10-final-summary-report.md](docs/phases/phase-10-final-summary-report.md)               | Phase 10-1~10-4 완료·E2E 결과·다음 권장(회귀 확장)                                 |
| **Phase 10 순서**      | [docs/phases/phase-10-navigation.md](docs/phases/phase-10-navigation.md)                                   | 10-1→10-2→10-3→10-4 작업 순서·Task 문서 링크                                       |
| **Phase 11 계획**      | [docs/phases/phase-11-master-plan.md](docs/phases/phase-11-master-plan.md)                                 | Admin 설정 관리 시스템 (11-1~11-5)                                                 |
| **Phase 11 순서**      | [docs/phases/phase-11-navigation.md](docs/phases/phase-11-navigation.md)                                   | 11-1→11-2→11-3→11-4→11-5 작업 순서·Task 문서 링크                                  |
| **Phase 11-5 고도화**  | [docs/phases/phase-11-5/phase-10-improvement-plan.md](docs/phases/phase-11-5/phase-10-improvement-plan.md) | Phase 10 고도화 §2.1~§2.5·11-5-1~7 완료·선택 Task·회귀·E2E 연동                    |
| **Phase 11-5 webtest 요약** | [docs/webtest/phase-11-5/phase-11-5-webtest-execution-report.md](docs/webtest/phase-11-5/phase-11-5-webtest-execution-report.md) | E2E·2차 webtest·MCP-Cursor 시나리오 요약 |
| **통합 테스트**        | [docs/devtest/README.md](docs/devtest/README.md)                                                           | 통합 테스트 가이드·시나리오·리포트 (Phase 11-4 연계)                               |

- **Phase별 작업 기록**: [03-phase-1-4](docs/README/03-phase-1-4.md), [03-phase-5-7](docs/README/03-phase-5-7.md), [03-phase-8](docs/README/03-phase-8.md) — **요약 없이 전문 유지**. 어떤 방식으로 진화했는지 추적용.
- **n8n 프로젝트 구조**: [08-n8n-project-structure](docs/README/08-n8n-project-structure.md) — 디렉터리·워크플로우·규칙·생성된 파일·마이그레이션 **전문**.
- **전체 과거 기록(원문)**: [README.md.backup](README.md.backup) — 리팩토링 전 본문 보존.

---

## 빠른 시작

```bash
docker-compose up -d
```

**Docker Compose 아키텍처**: `postgres`, `qdrant`, **ollama**(로컬 LLM·별도 컨테이너), `backend` 서비스. **n8n은 Phase 8 보류로 주석 처리되어 기본 실행 시 기동하지 않음.** 상세: [docs/README/02-architecture.md](docs/README/02-architecture.md).

- Backend: http://localhost:**8001** (ver3 전용. ver2는 8000) — 대시보드: /dashboard, API: /docs
- PostgreSQL: 호스트 **5433** (ver3), Qdrant: 호스트 **6343** (ver3). 상세: [docs/planning/ver3-refactor-backup-plan.md](docs/planning/ver3-refactor-backup-plan.md)
- Ollama: http://localhost:11434 (별도 컨테이너, 로컬 LLM)
- n8n: 사용 시 `docker-compose.yml`에서 n8n 서비스·n8n_data 볼륨 주석 해제 후 `docker compose up -d n8n`

로컬 LLM 사용 시 모델 로드 (한 번 실행):

```bash
# 기본: exaone3.5:2.4b (한국어/영어, ~1.6GB, Ollama 라이브러리)
docker exec -it ollama ollama run exaone3.5:2.4b
```

**추론·키워드 품질 우선(8GB)**: `qwen2.5:3b` — exaone3.5:2.4b보다 추론·의미 기반 키워드 추천에 유리. `OLLAMA_MODEL=qwen2.5:3b` 후 `docker exec -it ollama ollama pull qwen2.5:3b`

**10.8B 모델(EEVE-Korean) 사용 시** — 약 11.3 GiB RAM 필요. 메모리 부족 시 위 2.4B 사용.

```bash
# 12GB+ RAM 있을 때만
docker exec -it ollama ollama run bnksys/yanolja-eeve-korean-instruct-10.8b
```

8GB에서 추론·키워드 대안(외부 API 등): [docs/ai/8gb-inference-and-keyword-alternatives.md](docs/ai/8gb-inference-and-keyword-alternatives.md). 상세: [docs/README/01-overview-and-quickstart.md](docs/README/01-overview-and-quickstart.md).

---

## 키워드 (검색·판단용)

- **ARCHITECTURE**: [docs/README/02-architecture.md](docs/README/02-architecture.md)
- **DEVELOPMENT_PROGRESS**: [docs/README/03-development-progress.md](docs/README/03-development-progress.md) (Phase 전문: 03-phase-1-4, 03-phase-5-7, 03-phase-8)
- **PHASE_10_COMPLETE**: [docs/phases/phase-10-final-summary-report.md](docs/phases/phase-10-final-summary-report.md)
- **PHASE_11**: [docs/phases/phase-11-master-plan.md](docs/phases/phase-11-master-plan.md), [docs/phases/phase-11-navigation.md](docs/phases/phase-11-navigation.md)
- **PHASE_11_5**: [docs/phases/phase-11-5/phase-10-improvement-plan.md](docs/phases/phase-11-5/phase-10-improvement-plan.md) (Phase 10 고도화 §2.1~§2.5)
- **DEVTEST**: [docs/devtest/README.md](docs/devtest/README.md)
- **N8N_PROJECT_STRUCTURE**: [docs/README/08-n8n-project-structure.md](docs/README/08-n8n-project-structure.md)
- **RULES**: [docs/README/04-rules-and-conventions.md](docs/README/04-rules-and-conventions.md)
- **DB_SCHEMA**: [docs/README/05-database.md](docs/README/05-database.md)
- **REFERENCE_DOCS**: [docs/README/06-reference-docs-index.md](docs/README/06-reference-docs-index.md)
- **ISSUES_FUTURE**: [docs/README/07-issues-and-future.md](docs/README/07-issues-and-future.md)

---

## 수정 시 안내

- **프로젝트 개요·시작 방법**: `docs/README/01-overview-and-quickstart.md`
- **아키텍처·구조**: `docs/README/02-architecture.md`
- **진행 현황**: `docs/README/03-development-progress.md` (Phase 전문: 03-phase-1-4, 03-phase-5-7, 03-phase-8)
- **n8n 프로젝트 구조**: `docs/README/08-n8n-project-structure.md`
- **룰·규약**: `docs/README/04-rules-and-conventions.md` (실제 규칙은 링크된 docs/ai, docs/n8n 등에서 수정)
- **DB**: `docs/README/05-database.md` (스키마·마이그레이션은 docs/db, scripts/db에서 수정)
- **참조 문서 목록**: `docs/README/06-reference-docs-index.md`
- **이슈·향후 계획**: `docs/README/07-issues-and-future.md`

이 README는 진입점과 링크만 유지하고, 본문은 위 문서에 두는 것을 권장합니다.
