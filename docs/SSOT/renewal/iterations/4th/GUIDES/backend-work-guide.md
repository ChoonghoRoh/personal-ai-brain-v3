# Backend 작업지시 가이드

**버전**: 6.0-renewal-4th  
**대상**: backend-dev 팀원  
**용도**: Task 실행 프로세스 상세 지침

---

## Task 실행 프로세스

### 1. Task 할당 → 구현 → 보고

```
[1] Team Lead: SendMessage → backend-dev에게 Task 지시
[2] backend-dev: TaskList 조회 → Task X-Y-N 확인
[3] backend-dev: task-X-Y-N.md 읽기 → 완료 기준(Done Definition) 확인
[4] backend-dev: 코드 작성 (backend/, tests/)
[5] backend-dev: 로컬 테스트 확인 (pytest)
[6] backend-dev: TaskUpdate(status: "completed")
[7] backend-dev: SendMessage → Team Lead에게 완료 보고
```

### 2. verifier가 FAIL 판정 시 수정

Team Lead가 수정 요청 전달 → backend-dev 이슈 수정 → SendMessage로 재보고.

---

## 코드 작성 예시

- **ORM 사용**: SQLAlchemy ORM만 사용, raw SQL 금지.
- **Pydantic 검증**: 모든 API 입력은 Pydantic 스키마로 검증.
- **타입 힌트**: 함수 파라미터 + 반환 타입 필수.

➜ 상세: [ROLES/backend-dev.md](../ROLES/backend-dev.md), [2-architecture.md](../2-architecture.md)

---

**문서 관리**: 버전 6.0-renewal-4th, 단독 사용(4th 세트만 참조)
