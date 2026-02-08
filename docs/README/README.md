# README 분리 문서 (AI/개발자용)

이 폴더는 루트 `README.md`를 **기존 내용 최대한 유지**한 채 링크 기반으로 분리한 문서입니다. Phase별 작업 기록은 **요약 없이 전문**으로 넣어 두었으며, 나중에 어떤 AI가 읽어도 **어떤 방식으로 진화했는지** 알 수 있도록 했습니다.

---

## 파일 목록

| 파일                              | 용도                                                                                                                                                 |
| --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| **01-overview-and-quickstart.md** | 프로젝트 개요·주요 기능·프로젝트 구조·시작하기·사용 예시·기술 스택·완료/향후 (원문 1~330라인 유지)                                                   |
| **02-architecture.md**            | 아키텍처 및 구조 변경, Docker Compose(ollama 별도 컨테이너), n8n·backend·web 파일 공유                                                               |
| **03-development-progress.md**    | 개발 진행 **인덱스**: 진행 단계 표 + Phase별 전문 문서 링크                                                                                          |
| **03-phase-1-4.md**               | Phase 1~4 작업 기록 **전문** (원문 331~568라인)                                                                                                      |
| **03-phase-5-7.md**               | Phase 5~7 작업 기록 **전문** (원문 570~1609라인)                                                                                                     |
| **03-phase-8.md**                 | Phase 8.0.0·8.1~8.3 작업 기록 **전문** (원문 1610~1913라인)                                                                                          |
| **04-rules-and-conventions.md**   | 룰·규약(문서 분류, n8n, AI 룰, Phase 폴더) — 링크 위주                                                                                               |
| **05-database.md**                | DB 구조 요약, docs/db·스크립트 링크                                                                                                                  |
| **06-reference-docs-index.md**    | 참조 문서 인덱스(docs/, Backend, 스크립트)                                                                                                           |
| **07-issues-and-future.md**       | 알려진 이슈, 향후 계획, 완료 기능 체크                                                                                                               |
| **08-n8n-project-structure.md**   | **n8n 프로젝트 구조 전문**: docs/n8n/ 디렉터리, 생성된 파일, 규칙·문서 분류, 마이그레이션 결과, 관련 문서                                            |
| **09-phase-9.md**                 | **Phase 9 작업 내용 요약**: 9-1~9-5 Task 개발 내역 요약. 원문: [phase-9-final-summary-report.md](../phases/phase-9-final-summary-report.md)          |
| **10-phase-10.md**                | **Phase 10 작업 내용 요약**: 10-1~10-4 Task 개발·E2E 결과 요약. 원문: [phase-10-final-summary-report.md](../phases/phase-10-final-summary-report.md) |

---

## Phase·통합 테스트 문서 (docs/phases, docs/devtest)

루트 README와 동기화. 최신 Phase 상태·작업 순서는 아래 문서를 참고합니다.

| 구분                   | 문서                                                                                         | 용도                                                            |
| ---------------------- | -------------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| **Phase 9 요약**       | [phase-9-final-summary-report.md](../phases/phase-9-final-summary-report.md)                 | Phase 9-1~9-5 Task 개발 내역·API 통합·회귀 테스트 요약          |
| **Phase 10 계획**      | [phase-10-master-plan.md](../phases/phase-10-master-plan.md)                                 | Reasoning 페이지 고도화 (10-1~10-4)                             |
| **Phase 10 완료 요약** | [phase-10-final-summary-report.md](../phases/phase-10-final-summary-report.md)               | Phase 10-1~10-4 완료·E2E 결과·다음 권장                         |
| **Phase 10 순서**      | [phase-10-navigation.md](../phases/phase-10-navigation.md)                                   | 10-1→10-2→10-3→10-4 작업 순서·Task 문서                         |
| **Phase 11 계획**      | [phase-11-master-plan.md](../phases/phase-11-master-plan.md)                                 | Admin 설정 관리 시스템 (11-1~11-5)                              |
| **Phase 11 순서**      | [phase-11-navigation.md](../phases/phase-11-navigation.md)                                   | 11-1→11-2→11-3→11-4→11-5 작업 순서·Task 문서                    |
| **Phase 11-5 고도화**  | [phase-11-5/phase-10-improvement-plan.md](../phases/phase-11-5/phase-10-improvement-plan.md) | Phase 10 고도화 §2.1~§2.5·11-5-1~11-5-7 완료(선택·회귀·E2E 연동) |
| **Phase 11-5 webtest 요약** | [phase-11-5-webtest-execution-report.md](../webtest/phase-11-5/phase-11-5-webtest-execution-report.md) | Phase 11-5 E2E·2차 webtest·MCP-Cursor 시나리오 요약 |
| **통합 테스트**        | [devtest/README.md](../devtest/README.md)                                                    | 통합 테스트 가이드·시나리오·리포트 (Phase 11-4 연계)            |

---

## 사용 원칙

- **Phase별 작업 기록**: 03-phase-1-4, 03-phase-5-7, 03-phase-8 은 **요약 없이 원문 유지**. 09-phase-9, 10-phase-10 은 Phase 9·10 **요약** (원문은 docs/phases/ phase-9-final-summary-report, phase-10-final-summary-report).
- **n8n 구조**: 08-n8n-project-structure.md 에 n8n 디렉터리·워크플로우·규칙·생성된 파일·마이그레이션 결과를 **전문**으로 둠.
- **단일 소스**: 상세 규칙·스키마는 해당 주제 문서(docs/ai, docs/db, docs/n8n 등)에 두고, 여기서는 **요약·링크** 또는 **전문 복사**만 유지.
- **과거 전체 기록**: 루트 `README.md.backup` 참고.
