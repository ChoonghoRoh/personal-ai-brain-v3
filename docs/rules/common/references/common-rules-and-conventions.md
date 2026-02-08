# 룰 및 규약

**수정 시**: 규칙 추가·변경 시 이 파일과 링크 대상 문서를 갱신. AI 판단·자동 생성 시 이 문서와 링크된 규칙을 우선 참고.

---

## 문서 분류 (Phase Document Taxonomy)

- **경로**: [common-phase-document-taxonomy.md](./common-phase-document-taxonomy.md)
- **용도**: Phase 문서의 목적, 역할, 생성 주체, 자동화 가능 여부 정의. plan / todo-list / task / summary 등.
- **연동**: `docs/ai/ai-rule-decision.md`, `docs/ai/ai-rule-phase-naming.md` §7, phase 폴더·tasks 하위 규칙.

---

## n8n 규칙

- **노드 명명**: [../n8n/n8n-rule-node-naming.md](../../n8n/references/n8n-rule-node-naming.md) — Prefix(JS*, CMD*, DB*, GPT* 등), 동사+대상.
- **워크플로우·Phase-Task 규약**: [../n8n/n8n-workflow-phase-task-convention.md](../../n8n/references/n8n-workflow-phase-task-convention.md).
- **Backend 호출 설정**: [../n8n/n8n-backend-call-manual-settings.md](../../n8n/references/n8n-backend-call-manual-settings.md).
- **n8n 프로젝트 구조 전문**: [../n8n/n8n-project-structure.md](../../n8n/references/n8n-project-structure.md)

---

## AI 룰 (판단·자동 생성)

- **판단 기준**: [docs/ai/ai-rule-decision.md](../../ai/references/ai-rule-decision.md)
- **Phase 명명·폴더 규칙**: [docs/ai/ai-rule-phase-naming.md](../../ai/references/ai-rule-phase-naming.md)
- **Phase 자동 생성**: [docs/ai/ai-rule-phase-auto-generation.md](../../ai/references/ai-rule-phase-auto-generation.md)
- **Task 검사 규정**: [docs/ai/ai-rule-task-inspection.md](../../ai/references/ai-rule-task-inspection.md) — Task 완료 검사 시 확인 항목·판단 기준·산출물 규정
- **Phase Navigation 생성**: [docs/ai/ai-rule-phase-navigation-generation.md](../../ai/references/ai-rule-phase-navigation-generation.md) — **phase-X-master-plan** 존재 시 **[phase-x-navi:make]** 명령으로 `phase-X-navigation.md` 생성·갱신. 형식 참조: phase-10-navigation.md, phase-9-navigation.md.
- **Phase-X-Y Plan·Todo-List 생성**: [docs/ai/ai-rule-phase-plan-todo-generation.md](../../ai/references/ai-rule-phase-plan-todo-generation.md) — **phase-X-master-plan**·**phase-X-navigation** 기반 **[phase-x-plan-todo:make]** 명령으로 각 phase-X-Y에 대해 `phase-X-Y-0-plan.md`, `phase-X-Y-0-todo-list.md` 생성·갱신. 공통 규약·누락 방지 체크리스트 준수. 참조: phase-10-1~10-4, phase-9-1~9-5.
- **Task 생성 규칙**: [docs/ai/ai-rule-task-creation.md](../../ai/references/ai-rule-task-creation.md) — **phase-X-Y-0-todo-list** 기반 **[task-x-y:make]** 명령으로 `phase-X-Y/tasks/` 하위에 todo 항목별 `task-X-Y-N-<topic>.md` 생성·갱신. 파일명·공통 규약·참고 결과물: phase-10-1, phase-10-2.

---

## Phase 폴더 규칙

- **phase-X-Y** 폴더, **tasks/** 하위, 파일명 패턴(phaseX-Y-Z-plan.md, phaseX-Y-N-task.md 등): [ai-rule-phase-naming.md](../../ai/references/ai-rule-phase-naming.md) §7, [README-phase-folder-convention.md](../../../phases/phase-8-0/README-phase-folder-convention.md) 참고.
