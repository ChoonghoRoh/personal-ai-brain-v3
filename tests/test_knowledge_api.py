"""
Phase 9-2-2: Knowledge API 테스트
- GET/POST /api/knowledge/chunks, GET /api/knowledge/chunks/{id}
- GET/POST /api/labels, 청크-라벨 연결
- GET/POST /api/relations
"""
import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


class TestKnowledgeChunks:
    """청크 CRUD 테스트 (prefix=/api/knowledge)"""

    def test_list_chunks_returns_200(self):
        """GET /api/knowledge/chunks 목록 조회"""
        response = client.get("/api/knowledge/chunks?limit=10&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total_count" in data
        assert isinstance(data["items"], list)

    def test_get_chunk_by_id(self):
        """GET /api/knowledge/chunks/{chunk_id} 단건 조회 (없으면 404)"""
        response = client.get("/api/knowledge/chunks/1")
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "id" in data
            assert "content" in data
            assert "document_id" in data


class TestLabelsAPI:
    """라벨 API 테스트 (prefix=/api/labels)"""

    def test_list_labels_returns_200(self):
        """GET /api/labels 라벨 목록"""
        response = client.get("/api/labels")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_label_validation(self):
        """POST /api/labels 필수 필드 검증 (name, label_type 없으면 422)"""
        response = client.post("/api/labels", json={})
        assert response.status_code == 422


class TestRelationsAPI:
    """관계 API 테스트 (prefix=/api/relations)"""

    def test_list_relations_returns_200(self):
        """GET /api/relations 관계 목록"""
        response = client.get("/api/relations")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_relation_validation(self):
        """POST /api/relations 필수 필드 검증 (source_chunk_id, target_chunk_id, relation_type 없으면 422)"""
        response = client.post("/api/relations", json={})
        assert response.status_code == 422
