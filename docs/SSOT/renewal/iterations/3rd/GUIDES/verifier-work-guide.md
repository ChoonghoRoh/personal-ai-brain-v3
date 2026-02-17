# Verifier 작업지시 가이드

**버전**: 1.0 (3rd iteration)  
**대상**: verifier 팀원  
**용도**: 검증 프로세스 상세 지침

---

## 검증 프로세스

### 1. Team Lead로부터 검증 요청 수신

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

### 2. 재검증

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

## 검증 체크리스트 예시

### 백엔드 검증

```python
# ✅ Critical 통과 예시
from sqlalchemy.orm import Session
from backend.models.document_models import Document
from pydantic import BaseModel

class DocCreate(BaseModel):
    title: str
    content: str

async def create_document(req: DocCreate, db: Session) -> Document:
    try:
        doc = Document(title=req.title, content=req.content)
        db.add(doc)
        db.commit()
        return doc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 프론트엔드 검증

```javascript
// ✅ Critical 통과 예시
import { get } from '/static/js/utils/api.js';
import { esc } from '/static/js/utils/security.js';

async function init() {
  try {
    const data = await get('/api/documents');
    render(data);
  } catch (error) {
    alert('데이터 로드 실패');
  }
}

function render(data) {
  const container = document.getElementById('container');
  container.innerHTML = data.map(item => 
    `<div>${esc(item.title)}</div>`
  ).join('');
}
```

---

**문서 관리**:
- 버전: 1.0 (3rd iteration)
- 최종 수정: 2026-02-17
- 기반: verifier.md § 5 (검증 프로세스 분리)
