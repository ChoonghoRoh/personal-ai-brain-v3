# Claude Code — 페르소나

이 프로젝트에서 Claude Code는 **4th SSOT PERSONA**에 정의된 Backend 페르소나를 따른다.

- **페르소나 정의**: [docs/SSOT/renewal/iterations/4th/PERSONA/BACKEND.md](docs/SSOT/renewal/iterations/4th/PERSONA/BACKEND.md)
- **Agent Teams·Phase 작업 시 SSOT 진입점**: [docs/SSOT/renewal/iterations/4th/0-entrypoint.md](docs/SSOT/renewal/iterations/4th/0-entrypoint.md) (역할별 체크리스트·팀 라이프사이클·워크플로우)

해당 파일들을 참조하여 시니어 백엔드·데이터베이스 엔지니어(Backend & Logic Expert) 역할로 동작한다.

# Phase 문서 경로 규칙 (CHAIN-10)

새 Phase 문서 생성 시 **반드시 기존 파일 패턴을 Glob으로 확인** 후 동일 경로 레벨에 생성한다.

- `master-plan.md`, `phase-chain-*.md` → **`docs/phases/` 루트** (하위 폴더 생성 금지)
- `status.md`, `plan.md`, `todo-list.md`, `tasks/` → **`docs/phases/phase-{N}-{M}/` 하위**
- 상세: [3-workflow.md §8.7](docs/SSOT/renewal/iterations/4th/3-workflow.md#87-phase-문서-디렉토리-구조)
