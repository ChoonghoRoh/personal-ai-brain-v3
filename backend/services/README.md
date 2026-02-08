# Backend Services (용도별 구조)

서비스는 **routers와 동일한 도메인**으로 하위 패키지에 나뉘어 있습니다. 라우터가 `backend.services.<도메인>.<모듈>` 형태로 import합니다.

| 패키지 | 역할 | 포함 모듈 |
|--------|------|-----------|
| **search/** | 검색·문서 동기화 | search_service, document_sync_service |
| **system/** | 시스템·로그·무결성 | system_service, logging_service, integrity_service |
| **knowledge/** | 지식 통합 | knowledge_integration_service |
| **reasoning/** | 추론 체인 | reasoning_chain_service |
| **cognitive/** | 기억·맥락·학습·성격·메타인지 | memory_service, context_service, learning_service, personality_service, metacognition_service |
| **automation/** | 자동화·워크플로우 | automation_service, workflow_task_service |
| **ingest/** | 수집·파싱 | file_parser_service |

## Import 예

```python
# 라우터에서
from backend.services.search.search_service import get_search_service
from backend.services.automation.workflow_task_service import run_task

# 서비스 간 참조
from backend.services.search.search_service import get_search_service
from backend.services.cognitive.context_service import ContextService
```

## 서비스 간 의존성

- **search**: 다른 서비스에 의존하지 않음 (기반)
- **cognitive/context_service**: search.search_service 사용
- **reasoning/reasoning_chain_service**: search.search_service 사용
- **knowledge/knowledge_integration_service**: search, cognitive.context 사용
- **automation/automation_service**: search, cognitive.context 사용
