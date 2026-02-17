# Backend 작업지시 가이드

**버전**: 5.0-renewal-r3  
**대상**: backend-dev 팀원  
**용도**: Task 실행 프로세스 상세 지침

---

## Task 실행 프로세스

### 1. Task 할당 → 구현 → 보고

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

### 2. verifier가 FAIL 판정 시 수정

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

## 코드 작성 예시

### ORM 사용

```python
# ✅ 올바른 예시
from sqlalchemy.orm import Session
from backend.models.document_models import Document

def get_document_by_id(db: Session, doc_id: int) -> Document:
    return db.query(Document).filter(Document.id == doc_id).first()

# ❌ 잘못된 예시 (raw SQL)
def get_document_by_id(db: Session, doc_id: int):
    result = db.execute(f"SELECT * FROM documents WHERE id = {doc_id}")
    return result.fetchone()
```

### Pydantic 검증

```python
# ✅ 올바른 예시
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

class DocCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str

router = APIRouter()

@router.post("/api/doc")
async def create_document(req: DocCreate, db: Session = Depends(get_db)):
    try:
        doc = Document(title=req.title, content=req.content)
        db.add(doc)
        db.commit()
        return {"id": doc.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 타입 힌트

```python
# ✅ 올바른 예시
def process_documents(doc_ids: list[int]) -> dict[int, str]:
    result: dict[int, str] = {}
    for doc_id in doc_ids:
        result[doc_id] = "처리 완료"
    return result

# ❌ 잘못된 예시 (타입 힌트 없음)
def process_documents(doc_ids):
    result = {}
    for doc_id in doc_ids:
        result[doc_id] = "처리 완료"
    return result
```

---

**문서 관리**:
- 버전: 1.0 (3rd iteration)
- 최종 수정: 2026-02-17
- 기반: backend-dev.md § 4 (작업지시 분리)
