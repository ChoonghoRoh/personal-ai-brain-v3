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
