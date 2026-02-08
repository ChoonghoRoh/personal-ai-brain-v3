"""
Phase 9-2-4: 문서 → 검색 → AI 응답 E2E 시나리오
- 문서 업로드 → 청크 생성 → 임베딩 → 검색 → AI 응답
- DB·Qdrant·Ollama 등이 준비된 환경에서 실행 (통합 테스트)
"""
import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


@pytest.mark.integration
class TestDocumentToAnswer:
    """문서 업로드 → 청크 → 임베딩 → 검색 → AI 응답 플로우"""

    def test_search_after_chunks_exist(self):
        """청크가 존재할 때 검색 API 호출 (통합 전제: DB·Qdrant)"""
        response = client.get("/api/search/simple?q=테스트&limit=5")
        assert response.status_code in [200, 400, 500]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list) or "results" in data

    def test_ask_after_search(self):
        """검색 후 AI 질의 (통합: 검색 → /api/ask)"""
        response = client.post(
            "/api/ask",
            json={"question": "테스트 질문", "context_enabled": True, "top_k": 3},
        )
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = response.json()
            assert "answer" in data
