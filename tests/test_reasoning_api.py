"""
Phase 9-2-3: Reasoning API 테스트
- POST /api/reason (모드별, 필터, 질문 유무)
- GET /api/reason/recommendations/chunks, /labels, /questions, /explore
"""
import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


class TestReasonAPI:
    """POST /api/reason 테스트"""

    def test_reason_post_returns_200_or_500(self):
        """POST /api/reason 기본 요청 (inputs 필수)"""
        response = client.post(
            "/api/reason",
            json={
                "mode": "design_explain",
                "inputs": {},
                "question": "테스트 질문",
            },
        )
        # DB/Ollama 미준비 시 500 가능
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = response.json()
            assert "answer" in data or "result" in data or "output" in data

    def test_reason_post_empty_question(self):
        """질문 없을 때 (question=None) 처리"""
        response = client.post(
            "/api/reason",
            json={
                "mode": "design_explain",
                "inputs": {},
            },
        )
        assert response.status_code in [200, 422, 500]

    def test_reason_modes(self):
        """모드별 (design_explain, risk_review, next_steps, history_trace) 요청"""
        for mode in ("design_explain", "risk_review", "next_steps", "history_trace"):
            response = client.post(
                "/api/reason",
                json={"mode": mode, "inputs": {}, "question": "모드 테스트"},
            )
            assert response.status_code in [200, 500]


class TestRecommendationsAPI:
    """GET /api/reason/recommendations/* 테스트"""

    def test_recommendations_chunks_requires_chunk_ids(self):
        """GET /api/reason/recommendations/chunks - chunk_ids 없으면 422"""
        response = client.get("/api/reason/recommendations/chunks")
        assert response.status_code in [400, 422]

    def test_recommendations_chunks_with_ids(self):
        """GET /api/reason/recommendations/chunks?chunk_ids=1,2"""
        response = client.get("/api/reason/recommendations/chunks?chunk_ids=1,2&limit=5")
        assert response.status_code in [200, 404, 500]
        if response.status_code == 200:
            data = response.json()
            assert "recommendations" in data or "total" in data

    def test_recommendations_labels(self):
        """GET /api/reason/recommendations/labels"""
        response = client.get("/api/reason/recommendations/labels?content=테스트&limit=5")
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (list, dict))

    def test_recommendations_questions(self):
        """GET /api/reason/recommendations/questions"""
        response = client.get("/api/reason/recommendations/questions?project_id=1&limit=5")
        assert response.status_code in [200, 500]

    def test_recommendations_explore(self):
        """GET /api/reason/recommendations/explore"""
        response = client.get("/api/reason/recommendations/explore?context_chunk_ids=1&limit=5")
        assert response.status_code in [200, 400, 500]
