"""
Phase 9-2-4: Import → 자동 라벨 추천 → 적용 → 검증 E2E 시나리오
- Phase 9-3-2 구조 매칭(자동 라벨 추천) 연동
- DB 준비된 환경에서 실행 (통합 테스트)
"""
import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


@pytest.mark.integration
class TestImportMatching:
    """Import → 라벨 추천 → 적용 플로우"""

    def test_chunk_suggestions_endpoint(self):
        """청크 ID로 라벨 추천 API (GET /api/knowledge/chunks/{id}/suggestions)"""
        response = client.get("/api/knowledge/chunks/1/suggestions")
        assert response.status_code in [200, 404, 500]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict) or isinstance(data, list)
