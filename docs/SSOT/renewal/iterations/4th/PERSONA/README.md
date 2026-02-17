# 4th PERSONA (페르소나·Charter 통합)

**버전**: 6.0-renewal-4th  
**역할**: `docs/rules/role/` Charter 내용을 4th SSOT 내로 복사·통합. 단독 사용 시 외부 Charter 참조 불필요.

---

## 파일 목록

| 파일 | 원본 | 적용 팀원 |
|------|------|----------|
| [LEADER.md](LEADER.md) | docs/rules/role/LEADER.md | Team Lead (메인 세션) |
| [BACKEND.md](BACKEND.md) | docs/rules/role/BACKEND.md | backend-dev |
| [FRONTEND.md](FRONTEND.md) | docs/rules/role/FRONTEND.md | frontend-dev |
| [QA.md](QA.md) | docs/rules/role/QA.md | verifier, tester |
| [PLANNER.md](PLANNER.md) | — (4th 신규) | planner |

---

## 연결된 파일 (4th 내부)

4th에서 PERSONA를 참조하는 문서:

| 문서 | 참조 내용 |
|------|-----------|
| [0-entrypoint.md](../0-entrypoint.md) | 역할별 체크리스트 Charter 링크 (PERSONA/*.md) |
| [1-project.md](../1-project.md) | 역할별 상세 Charter, 참조 문서 테이블, Charter 장착 안내 |
| [2-architecture.md](../2-architecture.md) | 참조 문서 — Backend/Frontend Charter |
| [ROLES/backend-dev.md](../ROLES/backend-dev.md) | 상단 Charter, 참조 문서 테이블 |
| [ROLES/frontend-dev.md](../ROLES/frontend-dev.md) | 상단 Charter, 참조 문서 테이블 |
| [ROLES/verifier.md](../ROLES/verifier.md) | 상단 Charter, 참조 문서 테이블 |
| [ROLES/tester.md](../ROLES/tester.md) | 상단 Charter, 참조 문서 테이블 |
| [ROLES/planner.md](../ROLES/planner.md) | 상단 Charter (PLANNER.md) |

---

## 프로젝트 전체에서 Charter를 참조하는 다른 위치

4th가 아닌 **다른 경로**에서는 여전히 `docs/rules/role/` 를 참조함. 4th 단독 사용 시에는 이 PERSONA/ 만 사용.

| 위치 | 참조 경로 | 비고 |
|------|-----------|------|
| **AGENTS.md** (루트) | docs/rules/role/LEADER, BACKEND, FRONTEND, QA | 도구별 페르소나 매핑 (Cursor, Claude, Copilot, Gemini) |
| **.cursor/rules/leader-persona.mdc** | LEADER.md | Cursor alwaysApply |
| **renewal/0-entrypoint.md** (4th 아님) | ../../rules/role/*.md | renewal 루트 진입점 |
| **renewal/1-project.md, 2-architecture.md, 3-workflow.md** | docs/rules/role/*.md | renewal 루트 |
| **iterations/1st, 2nd, 3rd** | ../../rules/role/*.md 등 | 이전 iteration |

4th를 기본 진입점으로 사용할 때는 **PERSONA/** 만 로딩하면 되며, `docs/rules/role/` 은 수정하지 않아도 동작함.
