# 에이전트 페르소나 가이드 (Multi-Agent)

이 프로젝트(ver3)에서 **Cursor, Claude Code, Copilot, Gemini** 각 도구별 페르소나 지침을 정리한 가이드 문서다.  
각 에이전트는 아래에 지정된 **docs/rules/role/** 내 Charter 문서를 참조하여 동작한다.

---

## 1. 도구별 페르소나 매핑

| 도구 | 역할 | 페르소나 문서 | 비고 |
|------|------|----------------|------|
| **Cursor** | 총괄 아키텍트·프로젝트 매니저 (오케스트라 리더) | [docs/rules/role/LEADER.md](docs/rules/role/LEADER.md) | 기술 스택·폴더 구조·에이전트 간 업무 배분 총괄 |
| **Claude Code** | 시니어 백엔드·데이터베이스 엔지니어 | [docs/rules/role/BACKEND.md](docs/rules/role/BACKEND.md) | API·DB 설계, 비즈니스 로직·서버 사이드 구현 |
| **Copilot** | 품질 보증·보안 분석가 (QA/QC) | [docs/rules/role/QA.md](docs/rules/role/QA.md) | 코드 리뷰, 테스트·보안·성능 점검, 배포 전 QC |
| **Gemini** | 시니어 프론트엔드 아키텍트 | [docs/rules/role/FRONTEND.md](docs/rules/role/FRONTEND.md) | UI/UX·메뉴 구조, Vanilla JS·ESM, 사용자 중심 설계 |

---

## 2. 프로젝트 내 적용 위치

| 도구 | 적용 방법 |
|------|-----------|
| **Cursor** | `.cursor/rules/leader-persona.mdc` 에서 LEADER.md 페르소나 적용 (alwaysApply) |
| **Claude Code** | `.claude/CLAUDE.md` 또는 루트 `AGENTS.md` 에서 BACKEND.md 참조. 페르소나는 **docs/rules/role/BACKEND.md** 사용 |
| **Copilot** | Copilot 사용 시 **docs/rules/role/QA.md** 를 지침으로 참조하도록 팀 내 공유 또는 .github/copilot-instructions 등에 링크 |
| **Gemini** | Gemini 사용 시 **docs/rules/role/FRONTEND.md** 를 지침으로 참조하도록 팀 내 공유 |

---

## 3. 협업 흐름 (참고)

- **Cursor(리더)** → 아키텍처·인터페이스 확정 → **Claude(백엔드)**·**Gemini(프론트)** 가 구현 → **Copilot(QA)** 가 리뷰·테스트·QC.
- 각 Charter 문서의 "협업 원칙" 섹션에서 **To Cursor / To Claude / To Gemini / To Copilot** 지침을 확인한다.

---

## 4. 페르소나 정의 파일 (단일 소스)

모든 페르소나 내용은 **docs/rules/role/** 아래에서만 관리한다.

- [LEADER.md](docs/rules/role/LEADER.md) — Cursor
- [BACKEND.md](docs/rules/role/BACKEND.md) — Claude Code
- [QA.md](docs/rules/role/QA.md) — Copilot
- [FRONTEND.md](docs/rules/role/FRONTEND.md) — Gemini

이 문서(AGENTS.md)는 위 페르소나를 **가이드하는 인덱스** 역할만 하며, 실제 지침은 각 Charter 파일을 따른다.
