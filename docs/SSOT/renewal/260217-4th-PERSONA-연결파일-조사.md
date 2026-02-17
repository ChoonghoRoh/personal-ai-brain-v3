# 4th PERSONA 통합 — 연결된 파일 조사

**작성일**: 2026-02-17  
**목적**: 페르소나(Charter) 파일을 4th로 복사·통합한 뒤, 해당 Charter를 참조하는 프로젝트 내 모든 파일을 조사·정리.

---

## 1. 4th PERSONA 구성

| 파일 | 원본 | 비고 |
|------|------|------|
| `iterations/4th/PERSONA/LEADER.md` | docs/rules/role/LEADER.md | Team Lead |
| `iterations/4th/PERSONA/BACKEND.md` | docs/rules/role/BACKEND.md | backend-dev |
| `iterations/4th/PERSONA/FRONTEND.md` | docs/rules/role/FRONTEND.md | frontend-dev |
| `iterations/4th/PERSONA/QA.md` | docs/rules/role/QA.md | verifier, tester |
| `iterations/4th/PERSONA/PLANNER.md` | — | 4th 신규, planner |

4th **내부**에서는 위 PERSONA/*.md 만 참조하도록 링크를 변경 완료.

---

## 2. 4th 내부에서 PERSONA를 참조하는 파일 (변경 완료)

| 경로 | 참조 내용 |
|------|-----------|
| `iterations/4th/0-entrypoint.md` | 역할별 체크리스트 — Charter 링크 전부 PERSONA/*.md |
| `iterations/4th/1-project.md` | 역할별 상세 Charter, 참조 문서 테이블, Charter 장착 안내 |
| `iterations/4th/2-architecture.md` | 참조 문서 — Backend/Frontend Charter |
| `iterations/4th/ROLES/backend-dev.md` | 상단 Charter, 참조 문서 테이블 |
| `iterations/4th/ROLES/frontend-dev.md` | 상단 Charter, 참조 문서 테이블 |
| `iterations/4th/ROLES/verifier.md` | 상단 Charter, 참조 문서 테이블 |
| `iterations/4th/ROLES/tester.md` | 상단 Charter, 참조 문서 테이블 |
| `iterations/4th/ROLES/planner.md` | 상단 Charter (PLANNER.md) |
| `iterations/4th/VERSION.md` | 파일 목록·Breaking Changes·변경 이력 |
| `iterations/4th/PERSONA/README.md` | PERSONA 설명·연결 파일 요약 |

---

## 3. 프로젝트 전체 — Charter(rules/role) 참조 위치

아래는 **4th가 아닌** 경로에서 `docs/rules/role/` 또는 Charter 파일명을 참조하는 목록.  
4th 단독 사용 시에는 이 경로들을 수정하지 않아도 되며, 4th 진입 시에는 PERSONA/ 만 로딩하면 됨.

### 3.1 루트·설정

| 파일 | 참조 | 비고 |
|------|------|------|
| **AGENTS.md** | docs/rules/role/LEADER, BACKEND, FRONTEND, QA | 도구별 페르소나 매핑 (Cursor, Claude, Copilot, Gemini). 단일 소스 명시 |
| **.cursor/rules/leader-persona.mdc** | docs/rules/role/LEADER.md (링크) | Cursor alwaysApply. 전문 페르소나 문서 링크 |
| **.vscode/settings.json** | docs/rules/role/QA.md, docs/rules/testing/ | Copilot/QA 관련 프롬프트 텍스트 내 경로 |

### 3.2 SSOT renewal 루트 (4th 아님)

| 파일 | 참조 |
|------|------|
| docs/SSOT/renewal/0-entrypoint.md | ../../rules/role/*.md |
| docs/SSOT/renewal/1-project.md | docs/rules/role/LEADER, BACKEND, FRONTEND, QA |
| docs/SSOT/renewal/2-architecture.md | docs/rules/role/BACKEND, FRONTEND |
| docs/SSOT/renewal/3-workflow.md | docs/rules/role/LEADER |
| docs/SSOT/renewal/ROLES/*.md | ../../rules/role/*.md |
| docs/SSOT/renewal/RENEWAL-PLAN.md | Charter: BACKEND, QA, FRONTEND (이름만) |

### 3.3 iterations/1st, 2nd, 3rd (이전 iteration)

| 위치 | 참조 |
|------|------|
| iterations/1st/ROLES/backend-dev.md | ../../../rules/role/BACKEND.md |
| iterations/2nd/0-entrypoint, 1-project, 2-architecture, ROLES/* | docs/rules/role/* 또는 상대 경로 |
| iterations/3rd/0-entrypoint, 1-project, 2-architecture, ROLES/* | docs/rules/role/* 또는 상대 경로 |

---

## 4. 정리

- **4th 사용 시**: `iterations/4th/0-entrypoint.md` 진입 → 역할별 Charter는 **PERSONA/*.md** 만 사용. `docs/rules/role/` 은 읽지 않아도 동작.
- **AGENTS.md / .cursor / .vscode**: 도구별 페르소나는 계속 **docs/rules/role/** 를 가리킴. 4th PERSONA와 동기화하려면 필요 시 해당 설정에서 경로를 `docs/SSOT/renewal/iterations/4th/PERSONA/*.md` 로 바꿀 수 있음 (선택).
- **renewal 루트·1st·2nd·3rd**: 기존대로 docs/rules/role 참조 유지. 4th만 단독 SSOT로 쓸 때는 이 경로들은 건드리지 않아도 됨.

---

**문서 상태**: 4th PERSONA 통합 완료. 연결 파일 조사 완료.
