"""
Phase 9-2-4: 지식 워크플로우 E2E 시나리오
- 청크 생성 → 라벨 추가 → 관계 생성 → 승인 → Reasoning
- DB 준비된 환경에서 실행 (통합 테스트)
"""
import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


@pytest.mark.integration
class TestKnowledgeWorkflow:
    """청크 → 라벨 → 관계 → 승인 → Reasoning 플로우"""

    def test_list_chunks_then_labels(self):
        """청크 목록 → 라벨 목록 (API 연속 호출)"""
        r1 = client.get("/api/knowledge/chunks?limit=5&offset=0")
        assert r1.status_code == 200
        r2 = client.get("/api/labels")
        assert r2.status_code == 200

    def test_list_relations(self):
        """관계 목록 조회"""
        response = client.get("/api/relations")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
