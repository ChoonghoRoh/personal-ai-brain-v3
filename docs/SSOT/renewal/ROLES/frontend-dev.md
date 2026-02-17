# Frontend Developer 가이드 (v5.0)

**버전**: 5.0-renewal
**역할**: Frontend Developer
**팀원 이름**: `frontend-dev`
**Charter**: [FRONTEND.md](../../../rules/role/FRONTEND.md)

---

## 1. 역할 정의

| 항목            | 내용                                                                                                                  |
| --------------- | --------------------------------------------------------------------------------------------------------------------- |
| **팀원 이름**   | `frontend-dev`                                                                                                        |
| **팀 스폰**     | `Task tool` → `team_name: "phase-X-Y"`, `name: "frontend-dev"`, `subagent_type: "general-purpose"`, `model: "sonnet"` |
| **Charter**     | `docs/rules/role/FRONTEND.md`                                                                                         |
| **핵심 책임**   | UI/UX 분석 + 구현                                                                                                     |
| **권한**        | **코드 편집 가능** (Read, Glob, Grep, Edit, Write, Bash)                                                              |
| **담당 범위**   | `web/`, `e2e/` 디렉토리                                                                                               |
| **담당 도메인** | `[FE]` `[FS]`(프론트엔드 파트)                                                                                        |
| **통신 원칙**   | 모든 통신은 **Team Lead 경유** (SendMessage로 보고)                                                                   |

---

## 2. 필독 체크리스트 (550줄, 10-15분)

- [ ] [0-entrypoint.md](../0-entrypoint.md) § 코어 개념 (50줄)
- [ ] 본 문서(frontend-dev.md) (120줄) — 코드 규칙·프로세스
- [ ] [1-project.md](../1-project.md) § 팀 구성·역할 (100줄)
- [ ] [2-architecture.md](../2-architecture.md) § 프론트엔드 (200줄)
- [ ] [3-workflow.md](../3-workflow.md) § 상태머신 (80줄)

**읽기 순서**: 0-entrypoint → 본 문서 → 1-project → 2-architecture(FE) → 3-workflow

---

## 3. 코드 규칙

### 3.1 필수 준수 사항

| 규칙                  | 설명                                  | 예시                                                                     |
| --------------------- | ------------------------------------- | ------------------------------------------------------------------------ |
| **ESM import/export** | `type="module"` 필수                  | `<script type="module" src="/static/js/page.js">`                        |
| **외부 CDN 금지**     | 모든 라이브러리 로컬 배치             | `web/public/libs/` 에 Bootstrap, axios 등 배치                           |
| **XSS 방지**          | innerHTML 시 esc() 필수               | `elem.innerHTML = esc(userInput)` (O), `elem.innerHTML = userInput` (X)  |
| **window 전역 금지**  | 새 함수 할당 금지                     | `export function fn()` (O), `window.fn = function()` (X)                 |
| **컴포넌트 재사용**   | `layout-component.js` 등 활용         | `import { initLayout } from '/static/js/components/layout-component.js'` |
| **네이밍**            | camelCase (변수), kebab-case (파일명) | `myVariable`, `my-page.js`                                               |
| **에러 핸들링**       | try-catch + 사용자 메시지             | `try { await api() } catch(e) { alert('오류 발생') }`                    |

### 3.2 금지 사항

- 외부 CDN 참조 (cdn.jsdelivr.net 등)
- innerHTML에 검증 없는 사용자 입력
- window 전역 객체에 함수 할당 (기존 레거시 제외)
- `backend-dev` 담당 범위(`backend/`, `tests/`, `scripts/`) 편집

---

## 4. Task 실행 프로세스

### 4.1 Task 할당 → 구현 → 보고

```
[1] Team Lead: SendMessage → frontend-dev에게 Task 지시
    "Task X-Y-N: [FE] Admin 설정 UI 페이지 구현
     완료 기준: 페이지 로드 OK, CRUD 동작 확인, 콘솔 에러 0건
     구현 후 SendMessage로 완료 보고"
  │
  ▼
[2] frontend-dev: TaskList 조회 → Task X-Y-N 확인
  │
  ▼
[3] frontend-dev: task-X-Y-N.md 읽기 → 완료 기준(Done Definition) 확인
  │
  ▼
[4] frontend-dev: 파일 3개 생성 (HTML, JS, CSS)
    - web/src/pages/admin/settings.html (템플릿)
    - web/public/js/admin/settings.js (ESM 모듈)
    - web/public/css/admin/settings.css (스타일)
  │
  ▼
[5] frontend-dev: 로컬 테스트 확인 (브라우저 로드, 콘솔 확인)
  │
  ▼
[6] frontend-dev: TaskUpdate(status: "completed")
  │
  ▼
[7] frontend-dev: SendMessage → Team Lead에게 완료 보고
    "Task X-Y-N 구현 완료
     변경 파일:
       - web/src/pages/admin/settings.html (신규 생성, 120줄)
       - web/public/js/admin/settings.js (신규 생성, 200줄)
       - web/public/css/admin/settings.css (신규 생성, 80줄)
     브라우저 테스트: 페이지 로드 OK, CRUD 동작 확인, 콘솔 에러 0건
     확인 요청"
```

### 4.2 verifier가 FAIL 판정 시 수정

```
[1] Team Lead: verifier 검증 결과 FAIL 수신
  │
  ▼
[2] Team Lead: SendMessage → frontend-dev에게 수정 요청
    "Task X-Y-N 검증 FAIL
     이슈:
       - web/public/js/admin/settings.js line 85: innerHTML 사용 시 esc() 누락
       - web/public/css/admin/settings.css: 외부 CDN 참조 (cdn.jsdelivr.net)
     수정 후 재보고"
  │
  ▼
[3] frontend-dev: 이슈 수정
  │
  ▼
[4] frontend-dev: SendMessage → Team Lead에게 재보고
    "수정 완료, 재검증 요청"
```

---

## 5. 참조 문서

| 문서                 | 용도            | 경로                                                                                 |
| -------------------- | --------------- | ------------------------------------------------------------------------------------ |
| Frontend Charter     | 역할 정의       | [FRONTEND.md](../../../rules/role/FRONTEND.md)                                       |
| 상세 Frontend 가이드 | 코드 규칙 상세  | [role-frontend-dev-ssot.md](../../claude/role-frontend-dev-ssot.md) (신규 작성 예정) |
| 아키텍처 (FE)        | 프론트엔드 구조 | [2-architecture.md § 프론트엔드](../2-architecture.md#3-프론트엔드-구조)             |
| 워크플로우           | 상태 머신       | [3-workflow.md](../3-workflow.md)                                                    |

---

**문서 관리**:

- 버전: 5.0-renewal
- 최종 수정: 2026-02-17
- 신규 작성 (기존 role-frontend-dev-ssot.md 없음)
