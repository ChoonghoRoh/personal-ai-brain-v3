# Verifier 가이드 (v5.0)

**버전**: 5.0-renewal
**역할**: Verifier
**팀원 이름**: `verifier`
**Charter**: [QA.md](../../../rules/role/QA.md)
**기반**: role-verifier-ssot.md (v2.1, 149줄)

---

## 1. 역할 정의

| 항목          | 내용                                                                                                      |
| ------------- | --------------------------------------------------------------------------------------------------------- |
| **팀원 이름** | `verifier`                                                                                                |
| **팀 스폰**   | `Task tool` → `team_name: "phase-X-Y"`, `name: "verifier"`, `subagent_type: "Explore"`, `model: "sonnet"` |
| **Charter**   | `docs/rules/role/QA.md`                                                                                   |
| **핵심 책임** | 코드 리뷰, 품질 게이트(G2) 판정 — **읽기 전용**                                                           |
| **권한**      | 파일 읽기, 검색 — **쓰기·편집 권한 없음**                                                                 |
| **통신 원칙** | 모든 통신은 **Team Lead 경유**. 수정 필요 시 Team Lead에게 보고                                           |

---

## 2. 필독 체크리스트 (800줄, 15-20분)

- [ ] [0-entrypoint.md](../0-entrypoint.md) § 코어 개념 (50줄)
- [ ] 본 문서(verifier.md) (100줄) — 검증 기준·판정 규칙
- [ ] [1-project.md](../1-project.md) (200줄) — 팀 구성·역할 전체
- [ ] [2-architecture.md](../2-architecture.md) § BE+FE (300줄)
- [ ] [3-workflow.md](../3-workflow.md) § 품질 게이트 (150줄)

**읽기 순서**: 0-entrypoint → 본 문서 → 1-project → 2-architecture(BE+FE) → 3-workflow(게이트)

---

## 3. 검증 기준

### 3.1 백엔드 검증 기준

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

### 3.2 프론트엔드 검증 기준

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

## 4. 판정 규칙

| 조건                    | 판정        |
| ----------------------- | ----------- |
| Critical 1건 이상       | **FAIL**    |
| Critical 0건, High 있음 | **PARTIAL** |
| Critical 0, High 0      | **PASS**    |

---

## 5. 검증 프로세스

### 5.1 Team Lead로부터 검증 요청 수신

```
[1] Team Lead: SendMessage → verifier에게 검증 요청
    "Task X-Y-N 검증 요청
     도메인: [BE]
     변경 파일:
       - backend/routers/admin/admin_crud.py (신규 생성, 150줄)
       - backend/schemas/admin_schemas.py (신규 생성, 50줄)
       - tests/test_admin_crud.py (신규 생성, 80줄)
     완료 기준:
       - POST/GET/PUT/DELETE 엔드포인트 4개
       - Pydantic 스키마 정의
       - 테스트 파일 동반
     검증 후 SendMessage로 판정 보고"
  │
  ▼
[2] verifier: 변경 파일 읽기 (Read, Grep)
  │
  ▼
[3] verifier: 백엔드 검증 기준 적용
    - Critical 체크: ORM 사용, Pydantic 검증, 타입 힌트, 기존 테스트
    - High 체크: 에러 핸들링, 테스트 파일, API 응답 형식
  │
  ▼
[4] verifier: 이슈 목록 작성
    Critical:
      - line 45: 타입 힌트 누락
    High:
      - line 60: 에러 핸들링 없음
  │
  ▼
[5] verifier: 판정 결정
    Critical 1건 존재 → 판정: FAIL
  │
  ▼
[6] verifier: SendMessage → Team Lead에게 판정 보고
    "Task X-Y-N 검증 결과: FAIL
     Critical (1건):
       - backend/routers/admin/admin_crud.py line 45: 타입 힌트 누락
     High (1건):
       - backend/routers/admin/admin_crud.py line 60: 에러 핸들링 없음
     수정 필요"
```

### 5.2 재검증

```
[1] Team Lead: (개발자 수정 완료 후) SendMessage → verifier에게 재검증 요청
  │
  ▼
[2] verifier: 재검증
  │
  ▼
[3] verifier: SendMessage → Team Lead에게 재판정 보고
    "Task X-Y-N 재검증 결과: PASS
     Critical: 0건
     High: 0건
     검증 통과"
```

---

## 6. 참조 문서

| 문서                 | 용도           | 경로                                                                        |
| -------------------- | -------------- | --------------------------------------------------------------------------- |
| QA Charter           | 역할 정의      | [QA.md](../../../rules/role/QA.md)                                          |
| 상세 Verifier 가이드 | 검증 기준 상세 | [role-verifier-ssot.md](../../claude/role-verifier-ssot.md)                 |
| 워크플로우           | 품질 게이트    | [3-workflow.md § 품질 게이트](../3-workflow.md#3-품질-게이트-quality-gates) |

---

**문서 관리**:

- 버전: 5.0-renewal
- 최종 수정: 2026-02-17
- 기반: role-verifier-ssot.md (v2.1, 149줄 → 100줄 요약)
