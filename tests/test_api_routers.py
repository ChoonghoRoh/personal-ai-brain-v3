"""API 라우터 테스트"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_search_api():
    """검색 API 테스트"""
    response = client.get("/api/search?q=test&limit=5")
    assert response.status_code in [200, 400]  # 검색어가 없을 수도 있음


def test_search_simple_api():
    """간단한 검색 API 테스트"""
    response = client.get("/api/search/simple?q=test&limit=5")
    assert response.status_code in [200, 400]


def test_cache_stats_api():
    """캐시 통계 API 테스트"""
    response = client.get("/api/search/cache/stats")
    assert response.status_code == 200
    assert "size" in response.json()


def test_health_check():
    """헬스 체크 테스트"""
    response = client.get("/health")
    assert response.status_code == 200
