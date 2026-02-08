"""Phase 9-3-3: Hybrid Search 단위 테스트"""
import pytest
from backend.services.search.hybrid_search import (
    HybridSearchService,
    get_hybrid_search_service,
)


class TestHybridSearchService:
    """HybridSearchService 테스트."""

    def test_fuse_results_empty(self):
        """빈 결과 RRF 결합."""
        svc = HybridSearchService(semantic_weight=0.7, keyword_weight=0.3)
        fused = svc.fuse_results([], [])
        assert fused == []

    def test_fuse_results_semantic_only(self):
        """의미 검색 결과만 있을 때."""
        svc = HybridSearchService(semantic_weight=0.7, keyword_weight=0.3)
        semantic = [
            {"document_id": "1", "content": "a", "score": 0.9},
            {"document_id": "2", "content": "b", "score": 0.8},
        ]
        fused = svc.fuse_results(semantic, [])
        assert len(fused) == 2
        assert fused[0]["document_id"] == "1"
        assert fused[0]["source"] == "hybrid"
        assert 0 <= fused[0]["score"] <= 1

    def test_fuse_results_keyword_only(self):
        """키워드 검색 결과만 있을 때."""
        svc = HybridSearchService(semantic_weight=0.7, keyword_weight=0.3)
        keyword = [
            {"document_id": "1", "content": "x", "score": 0.7},
        ]
        fused = svc.fuse_results([], keyword)
        assert len(fused) == 1
        assert fused[0]["document_id"] == "1"
        assert fused[0]["source"] == "hybrid"

    def test_fuse_results_overlap(self):
        """의미·키워드 겹치는 document_id는 RRF로 결합."""
        svc = HybridSearchService(semantic_weight=0.7, keyword_weight=0.3)
        semantic = [
            {"document_id": "1", "content": "a", "score": 0.9},
            {"document_id": "2", "content": "b", "score": 0.8},
        ]
        keyword = [
            {"document_id": "1", "content": "a", "score": 0.8},
            {"document_id": "3", "content": "c", "score": 0.6},
        ]
        fused = svc.fuse_results(semantic, keyword)
        assert len(fused) == 3
        # 1이 양쪽에 있으면 RRF 점수가 가장 높아야 함
        ids = [f["document_id"] for f in fused]
        assert "1" in ids
        assert "2" in ids
        assert "3" in ids
        top_id = fused[0]["document_id"]
        assert top_id == "1"
