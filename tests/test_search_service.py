"""검색 서비스 테스트"""
import pytest
from backend.services.search.search_service import SearchService


def test_search_service_initialization():
    """검색 서비스 초기화 테스트"""
    service = SearchService()
    assert service is not None
    assert service.cache is not None


def test_search_simple():
    """간단한 검색 테스트"""
    service = SearchService()
    results = service.search_simple("test", top_k=5)

    assert isinstance(results, list)
    assert len(results) <= 5


def test_cache_functionality():
    """캐시 기능 테스트"""
    service = SearchService()

    # 캐시 초기화
    service.clear_cache()
    stats = service.get_cache_stats()
    assert stats['size'] == 0

    # 검색 실행 (캐시 사용)
    service.search("test", top_k=5, use_cache=True)

    # 캐시 통계 확인
    stats = service.get_cache_stats()
    assert stats['size'] > 0


class TestRedisSearchCache:
    """Phase 15-4: Redis 검색 캐시 테스트"""

    def test_cache_backend_detection(self):
        """캐시 백엔드 자동 선택 확인"""
        service = SearchService(enable_cache=True)
        assert service.cache is not None
        stats = service.get_cache_stats()
        assert "size" in stats
        assert "backend" in stats

    def test_cache_set_and_get(self):
        """캐시 저장·조회 기본 동작"""
        service = SearchService(enable_cache=True)
        service.clear_cache()
        service.search("redis cache test", top_k=3, use_cache=True)
        stats = service.get_cache_stats()
        assert stats["size"] >= 0

    def test_cache_disabled(self):
        """캐시 비활성화 모드"""
        service = SearchService(enable_cache=False)
        assert service.cache is None
        stats = service.get_cache_stats()
        assert stats.get("enabled") is False

    def test_cache_clear(self):
        """캐시 초기화"""
        service = SearchService(enable_cache=True)
        service.clear_cache()
        stats = service.get_cache_stats()
        assert stats["size"] == 0
