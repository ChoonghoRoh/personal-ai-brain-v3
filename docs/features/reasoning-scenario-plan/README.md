# Reasoning Scenario Plan — Index

**폴더 목적**: Reasoning Lab(/reason) 검증·시나리오·webtest MCP 시나리오 문서 모음.
원본 파일(reasoning-lab-feature-report.md, reason-lab-refactoring-design.md)은 **수정하지 않음**.
인용 시 `references/` 복사본 또는 원본 경로만 사용.

---

## 파일 목록

| 파일명                                     | 용도                                                 | 의존 문서                                 |
| ------------------------------------------ | ---------------------------------------------------- | ----------------------------------------- |
| **00-reasoning-scenario-master-plan.md**   | 본 계획 통합: 목표·전제·Step 1~5 요약                | —                                         |
| **00-08-feature-availability-check.md**   | 00~08·references 구현 기능 점검 보고서               | 01~08, references                        |
| **development-gaps-extract.md**            | 문서 vs 현재 소스 비교·추가 개발 필요 항목 발췌     | 00~08, references, 00-08-feature-availability-check |
| **01-verification-data-index.md**          | 검증/테스트 가능한 데이터·코드 위치 매핑             | feature report §1~§11                     |
| **02-reasoning-stories-and-scenarios.md**  | 스토리/시나리오 (모드별·플로우별)                    | 01, feature report                        |
| **03-scenario-document-creation-guide.md** | references 사용 규칙, 복사·시나리오 문서 작성 가이드 | —                                         |
| **04-verification-database.md**            | DB(PostgreSQL) 기능 작동 검증                        | 01, feature report §6                     |
| **05-verification-qdrant.md**              | Qdrant 기능 작동 검증                                | 01, feature report §7                     |
| **06-verification-backend.md**             | Backend API·pytest 검증                              | 01, feature report §4                     |
| **07-verification-frontend.md**            | Frontend(reason.html, reason JS) 검증                | 01, feature report §5, refactoring design |
| **08-webtest-mcp-reasoning-scenarios.md**  | MCP Cursor webtest 시나리오 (6항목, 69개)            | 04~07, webtest phase-10-1 형식            |

---

## 권장 읽기/작업 순서

1. **00** — Master Plan (목표·전제·단계 개요)
2. **01** — Verification Data Index (경로·테스트 매핑)
3. **02** — Stories and Scenarios (스토리/시나리오)
4. **03** — Scenario Document Creation Guide (복사·시나리오 작성 절차)
5. **04~07** — DB / Qdrant / Backend / Frontend 검증
6. **08** — Webtest MCP Reasoning 시나리오 (진입·입력·실행·결과·추천·저장·에러)
7. **README.md** (본 인덱스)

---

## references 폴더

- **위치**: `docs/features/reasoning-scenario-plan/references/`
- **역할**: 원본 문서의 **복사본** 보관. 원본은 수정하지 않음.
- **복사본 목록**:
  - `reasoning-lab-feature-report-ref.md` ← [reasoning-lab-feature-report.md](../reasoning-lab-feature-report.md)
  - `reason-lab-refactoring-design-ref.md` ← [reason-lab-refactoring-design.md](../reason-lab-refactoring-design.md)
- **가이드**: [03-scenario-document-creation-guide.md](03-scenario-document-creation-guide.md)에서 references 사용 규칙·파일명 규칙·시나리오 템플릿 확인.
