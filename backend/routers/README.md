# Backend Routers (용도별 구조)

API 라우터는 **용도별 하위 패키지**로 구분되어 있습니다. URL prefix는 각 모듈 내 `APIRouter(prefix=...)` 에서 정의되며, 폴더 구조와 무관하게 기존과 동일하게 유지됩니다.

| 패키지 | 역할 | 포함 모듈 |
|--------|------|-----------|
| **search/** | 검색·문서 | search, documents |
| **system/** | 시스템·백업·무결성·로그 | system, backup, integrity, logs, error_logs |
| **ai/** | AI 질의·대화 | ai, conversations |
| **knowledge/** | 지식 그래프·청크·라벨·관계·승인 | knowledge, labels, relations, approval, knowledge_integration, suggestions |
| **reasoning/** | 추론 | reason, reasoning_chain, reasoning_results |
| **cognitive/** | 기억·맥락·학습·성격·메타인지 | memory, context, learning, personality, metacognition |
| **automation/** | 자동화·워크플로우 (n8n) | automation, workflow |
| **ingest/** | 수집·파싱 | file_parser |

## 사용 예 (main.py)

```python
from backend.routers.search import search, documents
from backend.routers.knowledge import knowledge, labels, relations, approval, suggestions, knowledge_integration
from backend.routers.automation import automation, workflow
# ...
app.include_router(search.router)
app.include_router(workflow.router)
```

## 새 라우터 추가 시

- 해당 도메인 패키지에 `.py` 파일 추가 후, 해당 패키지의 `__init__.py` 에 import·`__all__` 추가
- `backend/main.py` 에서 해당 패키지에서 import 후 `app.include_router(모듈.router)` 등록

## 대응 관계

라우터 도메인과 **backend/services** 하위 패키지가 동일한 이름으로 맞춰져 있음 (search, system, ai, knowledge, reasoning, cognitive, automation, ingest). 서비스 import 시 `backend.services.<도메인>.<모듈>` 사용.
