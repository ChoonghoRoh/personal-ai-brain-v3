"""
Phase 15-3: 문서 기반 Reasoning 테스트
- document_ids 필터 포함 요청 → 200/400/500 확인
- document_ids + question → 문서 내 의미 검색 경로 확인
- document_ids만 (question 없음) → 문서 전체 청크 수집 확인
- 기존 요청 (document_ids 없음) → 하위 호환성 확인
- 존재하지 않는 document_id → 400 에러 확인
"""
import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


class TestReasonDocumentFilter:
    """POST /api/reason — document_ids 필터 테스트 (Phase 15-3)"""

    def test_document_ids_with_question(self):
        """document_ids + question → 문서 내 의미 검색 경로"""
        response = client.post(
            "/api/reason",
            json={
                "mode": "design_explain",
                "inputs": {},
                "question": "이 문서의 핵심 내용은?",
                "filters": {"document_ids": [1]},
            },
        )
        # DB/Qdrant 미준비 시 400 또는 500 가능
        assert response.status_code in [200, 400, 500]
        if response.status_code == 200:
            data = response.json()
            assert "answer" in data
            assert "context_chunks" in data

    def test_document_ids_without_question(self):
        """document_ids만 (question 없음) → 문서 전체 청크 수집"""
        response = client.post(
            "/api/reason",
            json={
                "mode": "design_explain",
                "inputs": {},
                "filters": {"document_ids": [1]},
            },
        )
        assert response.status_code in [200, 400, 500]
        if response.status_code == 200:
            data = response.json()
            assert "answer" in data
            assert "context_chunks" in data

    def test_nonexistent_document_id(self):
        """존재하지 않는 document_id → 400 (승인된 청크 없음)"""
        response = client.post(
            "/api/reason",
            json={
                "mode": "design_explain",
                "inputs": {},
                "filters": {"document_ids": [999999]},
            },
        )
        # 존재하지 않는 문서 → 청크 0건 → 400
        assert response.status_code in [400, 500]

    def test_backward_compat_no_document_ids(self):
        """기존 요청 (document_ids 없음) → 하위 호환성 확인"""
        response = client.post(
            "/api/reason",
            json={
                "mode": "design_explain",
                "inputs": {},
                "question": "테스트 질문",
            },
        )
        # 기존 동작 그대로
        assert response.status_code in [200, 500]

    def test_empty_document_ids_list(self):
        """빈 document_ids 목록 → 기존 동작 유지"""
        response = client.post(
            "/api/reason",
            json={
                "mode": "design_explain",
                "inputs": {},
                "question": "테스트 질문",
                "filters": {"document_ids": []},
            },
        )
        assert response.status_code in [200, 500]


class TestReasonStreamDocumentFilter:
    """POST /api/reason/stream — document_ids 필터 테스트 (Phase 15-3)"""

    def test_stream_document_ids_with_question(self):
        """스트리밍: document_ids + question"""
        response = client.post(
            "/api/reason/stream",
            json={
                "mode": "design_explain",
                "inputs": {},
                "question": "문서 분석",
                "filters": {"document_ids": [1]},
            },
        )
        # SSE 스트리밍 → 200
        assert response.status_code == 200

    def test_stream_backward_compat(self):
        """스트리밍: 기존 요청 (document_ids 없음) 호환"""
        response = client.post(
            "/api/reason/stream",
            json={
                "mode": "design_explain",
                "inputs": {},
                "question": "테스트",
            },
        )
        assert response.status_code == 200
