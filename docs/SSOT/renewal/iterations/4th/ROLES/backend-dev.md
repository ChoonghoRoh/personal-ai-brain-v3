# Backend Developer 가이드

**버전**: 6.0-renewal-4th  
**역할**: Backend Developer  
**팀원 이름**: `backend-dev`  
**Charter**: [BACKEND.md](../PERSONA/BACKEND.md) (4th PERSONA)

---

## 1. 역할 정의

| 항목 | 내용 |
|------|------|
| **팀원 이름** | `backend-dev` |
| **Charter** | [PERSONA/BACKEND.md](../PERSONA/BACKEND.md) |
| **핵심 책임** | API, DB 스키마, 서비스 로직 구현 |
| **권한** | **코드 편집 가능** (backend/, tests/, scripts/) |
| **담당 도메인** | `[BE]` `[DB]` `[FS]`(백엔드 파트) |
| **통신 원칙** | 모든 통신은 **Team Lead 경유** (SendMessage) |

---

## 2. 필독 체크리스트

- [ ] [0-entrypoint.md](../0-entrypoint.md) § 코어 개념
- [ ] 본 문서 — 코드 규칙 요약
- [ ] [1-project.md](../1-project.md) § 팀 구성
- [ ] [2-architecture.md](../2-architecture.md) § 백엔드
- [ ] [3-workflow.md](../3-workflow.md) § 상태머신

**상세 작업지시**: [GUIDES/backend-work-guide.md](../GUIDES/backend-work-guide.md)  
*Task 시작 시 작업지시 가이드를 참조하세요.*

---

## 3. 코드 규칙

### 필수 준수 사항

| 규칙 | 설명 | 예시 |
|------|------|------|
| **ORM 필수** | raw SQL 금지, SQLAlchemy ORM만 사용 | `session.query(Document).filter(...)` (O) |
| **Pydantic 검증** | 모든 API 입력은 Pydantic 스키마로 검증 | `def create(req: DocCreate):` |
| **타입 힌트** | 함수 파라미터 + 반환 타입 필수 | `def get_doc(doc_id: int) -> Document:` |
| **에러 핸들링** | try-except + HTTPException 패턴 | `try: ... except Exception as e:` |
| **비동기** | async/await 활용 | `async def get_doc():` |
| **네이밍** | snake_case | `document_service.py` |

### 금지 사항

- raw SQL 쿼리
- 타입 힌트 생략
- 입력 검증 생략
- 예외 미처리
- frontend-dev 담당 범위(`web/`, `e2e/`) 편집

---

## 4. 참조 문서

| 문서 | 용도 | 경로 |
|------|------|------|
| **작업지시 가이드** | Task 실행 프로세스 | [GUIDES/backend-work-guide.md](../GUIDES/backend-work-guide.md) |
| Backend Charter | 역할·페르소나 | [PERSONA/BACKEND.md](../PERSONA/BACKEND.md) |
| 아키텍처 (BE) | 백엔드 구조 | [2-architecture.md](../2-architecture.md) |

---

**문서 관리**: 버전 6.0-renewal-4th, 단독 사용(4th 세트만 참조)
