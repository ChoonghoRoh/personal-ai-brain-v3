# 참조 문서 인덱스

**수정 시**: 문서 추가·이동 시 이 목록만 갱신. AI가 "어디에 뭐가 있는지" 검색할 때 사용.

---

## 문서 루트별

| 디렉터리/파일 | 용도 |
|---------------|------|
| **docs/ai/** | AI 룰(판단, Phase 명명, 자동 생성), 한국어 LLM 추천 |
| **docs/db/** | DB 스키마, workflow 테이블 규약, 연결 가이드 |
| **docs/n8n/** | n8n 규칙(rules/), 워크플로우(workflow/), Backend 연동 설정. 구조 전문: [08-n8n-project-structure.md](./08-n8n-project-structure.md) |
| **docs/phases/** | Phase별 계획·작업·테스트(phase-8-0, phase-8-1, phase-8-2, phase-8-3, phase8-master-plan 등) |
| **docs/manual/** | 사용자 매뉴얼(Knowledge Admin, Knowledge Studio, Reasoning Lab 등) |
| **docs/overview/** | 프로젝트 개요(project-overview-*.md) |
| **docs/prompts/** | 프롬프트·가이드 |
| **docs/scripts/** | 문서/Phase 관련 스크립트 설명 |
| **phase-document-taxonomy.md** | Phase 문서 분류 체계(루트는 docs/) |

---

## Backend·스크립트

| 경로 | 용도 |
|------|------|
| **backend/routers/README.md** | 라우터 패키지 구조 |
| **backend/services/README.md** | 서비스 패키지 구조 |
| **backend/services/automation/README-workflow_task_service.md** | Task 실행 서비스(8-2-7) |
| **scripts/README.md** | 스크립트 목록·용도 |
| **web/README.md** | 웹 구조 |

---

## Phase 8·n8n 관련

- 계획: `docs/phases/phase8-master-plan.md`
- 8-1: `docs/phases/phase-8-1/phase8-1-plan.md`, tasks/phase8-1-1-*, phase8-1-2-*
- 8-2: `docs/phases/phase-8-2/tasks/` (phase8-2-1~8-2-8), phase8-2-4-2-6-development-progress-check.md
- 8-3: `docs/phases/phase-8-3/tasks/phase8-3-0-*`, phase8-3-1-*
- 8.0.0: `docs/phases/phase-8-0/phase8-0-plan.md`, phase8-0-todo-list.md, tasks/
- n8n 구조 전문: [08-n8n-project-structure.md](./08-n8n-project-structure.md)
