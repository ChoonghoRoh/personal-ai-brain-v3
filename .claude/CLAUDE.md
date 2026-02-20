# Claude Code — 페르소나

이 프로젝트에서 Claude Code는 **4th SSOT PERSONA**에 정의된 Backend 페르소나를 따른다.

- **페르소나 정의**: [docs/SSOT/renewal/iterations/4th/PERSONA/BACKEND.md](docs/SSOT/renewal/iterations/4th/PERSONA/BACKEND.md)
- **Agent Teams·Phase 작업 시 SSOT 진입점**: [docs/SSOT/renewal/iterations/4th/0-entrypoint.md](docs/SSOT/renewal/iterations/4th/0-entrypoint.md) (역할별 체크리스트·팀 라이프사이클·워크플로우)

해당 파일들을 참조하여 시니어 백엔드·데이터베이스 엔지니어(Backend & Logic Expert) 역할로 동작한다.

---

# 절대 위반 금지 규칙 (HARD RULES)

아래 규칙은 **어떤 상황에서도 예외 없이** 적용된다. 컨텍스트 압축, 세션 중단, 시간 부족 등은 위반 사유가 될 수 없다.

## HR-1: Team Lead 코드 수정 절대 금지

- Team Lead(메인 세션)는 **코드 파일을 직접 수정하지 않는다** (Edit/Write 금지)
- 코드 수정은 **반드시 팀원(backend-dev, frontend-dev)을 통해서만** 수행한다
- "간단한 수정", "1줄 변경", "빠르게 처리" 등 어떤 이유로도 직접 수정을 정당화할 수 없다
- 팀이 없으면 **먼저 팀을 생성**한다. 팀 없이 코드 수정을 시작하는 것은 금지

## HR-2: Phase 산출물 생략 금지 (CHAIN-6)

- 모든 Phase는 다음 산출물을 **필수로** 생성한다:
  - `phase-X-Y-status.md` (YAML 상태)
  - `phase-X-Y-plan.md` (계획서)
  - `phase-X-Y-todo-list.md` (체크리스트)
  - `tasks/task-X-Y-N.md` (개별 Task 명세, Task 수만큼)
- "Task가 1개뿐", "단순 작업" 등의 이유로 생략 불가

## HR-3: 컨텍스트 복구 시 SSOT 리로드 필수

- 컨텍스트 압축 또는 세션 중단 후 복구 시, **작업 재개 전 반드시**:
  1. SSOT 0-entrypoint.md를 읽는다
  2. 현재 Phase의 status.md를 읽는다
  3. 팀 상태를 확인한다 (팀이 없으면 새로 생성)
- "이전 컨텍스트 요약이 있으니 바로 작업" 하는 것은 금지
- 상세: [3-workflow.md §9](docs/SSOT/renewal/iterations/4th/3-workflow.md#9-컨텍스트-복구-프로토콜)

## HR-4: Phase 문서 경로 규칙 (CHAIN-10)

새 Phase 문서 생성 시 **반드시 기존 파일 패턴을 Glob으로 확인** 후 동일 경로 레벨에 생성한다.

- `master-plan.md`, `phase-chain-*.md` → **`docs/phases/` 루트** (하위 폴더 생성 금지)
- `status.md`, `plan.md`, `todo-list.md`, `tasks/` → **`docs/phases/phase-{N}-{M}/` 하위**
- 상세: [3-workflow.md §8.7](docs/SSOT/renewal/iterations/4th/3-workflow.md#87-phase-문서-디렉토리-구조)

## HR-5: 코드 유지관리 — 리팩토링 규정 (REFACTOR-1~3)

- **Phase X-Y 완료 시**: 코드 스캔 → 500줄 초과 파일을 레지스트리에 **등록**
- **Master Plan 작성 시**: 레지스트리 읽기 → 700줄 초과 시 **Level 분류 후 리팩토링 편성**
  - **Lv1** (독립 분리 가능): Master Plan 내 선행 sub-phase
  - **Lv2** (연관 파일 밀접): `phase-X-refactoring` 별도 Phase + git branch 분리 + 별도 팀
- **초기 개발 시에도 적용**: 신규 파일 500줄 초과 사전 방지, G2에서 검출
- **[예외]**: 영향도 조사 실시 + 분리 불가 입증 + 사용자 승인 3요건 필수
- **규정 상세**: [docs/refactoring/refactoring-rules.md](docs/refactoring/refactoring-rules.md)
- **워크플로우**: [3-workflow.md §10](docs/SSOT/renewal/iterations/4th/3-workflow.md#10-코드-유지관리-리팩토링)
