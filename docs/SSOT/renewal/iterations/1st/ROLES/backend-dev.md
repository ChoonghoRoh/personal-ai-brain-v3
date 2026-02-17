# Backend Developer 가이드 (v5.0)

**버전**: 5.0-renewal  
**역할**: Backend Developer  
**팀원 이름**: `backend-dev`  
**Charter**: [BACKEND.md](../../../rules/role/BACKEND.md)  
**기반**: role-backend-dev-ssot.md (v1.1, 154줄)

---

## 1. 역할 정의

| 항목 | 내용 |
|------|------|
| **팀원 이름** | `backend-dev` |
| **팀 스폰** | `Task tool` → `team_name: "phase-X-Y"`, `name: "backend-dev"`, `subagent_type: "general-purpose"`, `model: "sonnet"` |
| **Charter** | `docs/rules/role/BACKEND.md` |
| **핵심 책임** | API, DB 스키마, 서비스 로직 구현 |
| **권한** | **코드 편집 가능** (Read, Glob, Grep, Edit, Write, Bash) |
| **담당 범위** | `backend/`, `tests/`, `scripts/` 디렉토리 |
| **담당 도메인** | `[BE]` `[DB]` `[FS]`(백엔드 파트) |
| **통신 원칙** | 모든 통신은 **Team Lead 경유** (SendMessage로 보고) |

---

## 2. 필독 체크리스트 (550줄, 10-15분)

- [ ] [0-entrypoint.md](../0-entrypoint.md) § 코어 개념 (50줄)
- [ ] 본 문서(backend-dev.md) (120줄) — 코드 규칙·프로세스
- [ ] [1-project.md](../1-project.md) § 팀 구성·역할 (100줄)
- [ ] [2-architecture.md](../2-architecture.md) § 백엔드 (200줄)
- [ ] [3-workflow.md](../3-workflow.md) § 상태머신 (80줄)

**읽기 순서**: 0-entrypoint → 본 문서 → 1-project → 2-architecture(BE) → 3-workflow

---

## 3. 코드 규칙

### 3.1 필수 준수 사항

| 규칙 | 설명 | 예시 |
|------|------|------|
| **ORM 필수** | raw SQL 절대 금지, SQLAlchemy ORM만 사용 | `session.query(Document).filter(...)` (O), `session.execute("SELECT ...")` (X) |
| **Pydantic 검증** | 모든 API 입력은 Pydantic 스키마로 검증 | `@app.post("/api/doc") def create(req: DocCreate):` |
| **타입 힌트** | 함수 파라미터 + 반환 타입 힌트 필수 | `def get_doc(doc_id: int) -> Document:` |
| **에러 핸들링** | try-except + HTTPException 패턴 | `try: ... except Exception as e: raise HTTPException(404, str(e))` |
| **비동기** | async/await 활용 | `async def get_doc(): await db.execute(...)` |
| **네이밍** | snake_case | `document_service.py`, `def get_document_by_id():` |

### 3.2 금지 사항

- raw SQL 쿼리
- 타입 힌트 생략
- 입력 검증 없이 사용자 입력 처리
- 에러 처리 없이 예외 방치
- `frontend-dev` 담당 범위(`web/`, `e2e/`) 편집

---

## 4. Task 실행 프로세스

### 4.1 Task 할당 → 구현 → 보고

```
[1] Team Lead: SendMessage → backend-dev에게 Task 지시
    "Task X-Y-N: [BE] Admin API CRUD 구현
     완료 기준: POST/GET/PUT/DELETE 엔드포인트 4개, Pydantic 스키마 정의, 테스트 파일 동반
     구현 후 SendMessage로 완료 보고"
  │
  ▼
[2] backend-dev: TaskList 조회 → Task X-Y-N 확인
  │
  ▼
[3] backend-dev: task-X-Y-N.md 읽기 → 완료 기준(Done Definition) 확인
  │
  ▼
[4] backend-dev: 코드 작성 (backend/, tests/)
    - backend/routers/admin/admin_crud.py (API 라우터)
    - backend/schemas/admin_schemas.py (Pydantic 스키마)
    - backend/models/admin_models.py (ORM 모델, 필요 시)
    - tests/test_admin_crud.py (테스트 파일)
  │
  ▼
[5] backend-dev: 로컬 테스트 확인 (pytest tests/test_admin_crud.py)
  │
  ▼
[6] backend-dev: TaskUpdate(status: "completed")
  │
  ▼
[7] backend-dev: SendMessage → Team Lead에게 완료 보고
    "Task X-Y-N 구현 완료
     변경 파일:
       - backend/routers/admin/admin_crud.py (신규 생성, 150줄)
       - backend/schemas/admin_schemas.py (신규 생성, 50줄)
       - tests/test_admin_crud.py (신규 생성, 80줄)
     로컬 테스트: PASS (pytest 3개, 100%)
     확인 요청"
```

### 4.2 verifier가 FAIL 판정 시 수정

```
[1] Team Lead: verifier 검증 결과 FAIL 수신
  │
  ▼
[2] Team Lead: SendMessage → backend-dev에게 수정 요청
    "Task X-Y-N 검증 FAIL
     이슈:
       - backend/routers/admin/admin_crud.py line 45: 타입 힌트 누락
       - tests/test_admin_crud.py: DELETE 엔드포인트 테스트 누락
     수정 후 재보고"
  │
  ▼
[3] backend-dev: 이슈 수정
  │
  ▼
[4] backend-dev: SendMessage → Team Lead에게 재보고
    "수정 완료, 재검증 요청"
```

---

## 5. 참조 문서

| 문서 | 용도 | 경로 |
|------|------|------|
| Backend Charter | 역할 정의 | [BACKEND.md](../../../rules/role/BACKEND.md) |
| 상세 Backend 가이드 | 코드 규칙 상세 | [role-backend-dev-ssot.md](../../claude/role-backend-dev-ssot.md) |
| 아키텍처 (BE) | 백엔드 구조 | [2-architecture.md § 백엔드](../2-architecture.md#2-백엔드-구조) |
| 워크플로우 | 상태 머신 | [3-workflow.md](../3-workflow.md) |

---

**문서 관리**:
- 버전: 5.0-renewal
- 최종 수정: 2026-02-17
- 기반: role-backend-dev-ssot.md (v1.1, 154줄 → 120줄 요약)
