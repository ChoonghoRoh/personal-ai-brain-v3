# Verifier 가이드

**버전**: 6.0-renewal-4th  
**역할**: Verifier  
**팀원 이름**: `verifier`  
**Charter**: [QA.md](../PERSONA/QA.md) (4th PERSONA)

---

## 1. 역할 정의

| 항목 | 내용 |
|------|------|
| **팀원 이름** | `verifier` |
| **팀 스폰** | Task tool → `team_name: "phase-X-Y"`, `name: "verifier"`, `subagent_type: "Explore"`, `model: "sonnet"` |
| **Charter** | [PERSONA/QA.md](../PERSONA/QA.md) |
| **핵심 책임** | 코드 리뷰, 품질 게이트(G2) 판정 — **읽기 전용** |
| **권한** | 파일 읽기, 검색 — **쓰기·편집 권한 없음** |
| **통신 원칙** | 모든 통신은 **Team Lead 경유**. 수정 필요 시 Team Lead에게 보고 |

---

## 2. 실행 단위 로딩 (권장)

검증 **1회** 시작 시 컨텍스트에 포함 권장: ① 변경된 파일(Team Lead 전달) 및 해당 파일 내용 ② 해당 task-X-Y-N.md(완료 기준) ③ 본 문서 §4 검증 기준.  
➜ [3-workflow.md §9.5](../3-workflow.md#95-실행-단위-컨텍스트-권장-로딩-집합)

---

## 3. 필독 체크리스트

- [ ] [0-entrypoint.md](../0-entrypoint.md) § 코어 개념
- [ ] 본 문서 — 검증 기준·판정 규칙
- [ ] [1-project.md](../1-project.md) § 팀 구성
- [ ] [2-architecture.md](../2-architecture.md) § BE+FE
- [ ] [3-workflow.md](../3-workflow.md) § 품질 게이트

**상세 작업지시**: [GUIDES/verifier-work-guide.md](../GUIDES/verifier-work-guide.md)  
*검증 시작 시 작업지시 가이드를 참조하세요.*

---

## 4. 검증 기준

### 4.1 백엔드 검증 기준

#### Critical (필수 통과 — 1건이라도 있으면 FAIL)

- [ ] 구문 오류 없음 (Python import, 문법)
- [ ] ORM 사용 (raw SQL 없음)
- [ ] 입력 검증 존재 (Pydantic)
- [ ] FK 제약조건 정합성 (DB 변경 시)
- [ ] 기존 테스트 깨지지 않음

#### High (권장 통과)

- [ ] 타입 힌트 완전
- [ ] 에러 핸들링 존재 (try-except + HTTPException)
- [ ] 새 기능에 대한 테스트 파일 존재
- [ ] API 응답 형식 일관성

---

### 4.2 프론트엔드 검증 기준

#### Critical (필수 통과 — 1건이라도 있으면 FAIL)

- [ ] 외부 CDN 참조 없음
- [ ] `innerHTML` 사용 시 `esc()` 적용
- [ ] ESM `import`/`export` 패턴 사용 (`type="module"`)
- [ ] 페이지 로드 시 콘솔 에러 없음
- [ ] 기존 페이지 동작 깨지지 않음

#### High (권장 통과)

- [ ] `window` 전역 객체에 새 함수 할당 없음
- [ ] 기존 컴포넌트 재사용 (`layout-component.js`, `header-component.js`)
- [ ] API 호출 시 에러 핸들링 (try-catch + 사용자 메시지)
- [ ] 반응형 레이아웃 (Bootstrap grid 사용)

---

## 5. 판정 규칙

| 조건 | 판정 |
|------|------|
| Critical 1건 이상 | **FAIL** |
| Critical 0건, High 있음 | **PARTIAL** |
| Critical 0, High 0 | **PASS** |

---

## 6. 참조 문서

| 문서 | 용도 | 경로 |
|------|------|------|
| **작업지시 가이드** | 검증 프로세스 | [GUIDES/verifier-work-guide.md](../GUIDES/verifier-work-guide.md) |
| QA Charter | 역할·페르소나 | [PERSONA/QA.md](../PERSONA/QA.md) |
| 워크플로우 | 품질 게이트 | [3-workflow.md](../3-workflow.md) |

---

**문서 관리**: 버전 6.0-renewal-4th, 단독 사용(4th 세트만 참조)
