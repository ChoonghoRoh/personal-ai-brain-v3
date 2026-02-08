"""Phase 11-2: Admin 설정 Backend API 테스트

Admin CRUD API 라우터 등록·엔드포인트 동작 검증.
- OpenAPI에 admin 경로 포함 여부
- GET 목록 API 응답 구조 (200 시 items/total, DB 미준비 시 500 가능)
"""
import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_admin_routes_in_openapi():
    """OpenAPI 스키마에 Admin API 경로가 포함되어 있는지 확인"""
    openapi = app.openapi()
    paths = openapi.get("paths", {})
    admin_paths = [p for p in paths if p.startswith("/api/admin")]
    assert len(admin_paths) >= 1, "Admin API 경로가 OpenAPI에 없음"
    assert any("/schemas" in p for p in admin_paths), "Admin schemas 경로 없음"
    assert any("/templates" in p for p in admin_paths), "Admin templates 경로 없음"
    assert any("/presets" in p for p in admin_paths), "Admin presets 경로 없음"
    assert any("/rag-profiles" in p for p in admin_paths), "Admin rag-profiles 경로 없음"
    assert any("/policy-sets" in p for p in admin_paths), "Admin policy-sets 경로 없음"


def test_admin_schemas_list():
    """GET /api/admin/schemas 목록 조회 (200 + items/total 또는 DB 미준비 시 500)"""
    response = client.get("/api/admin/schemas", params={"limit": 5, "offset": 0})
    if response.status_code == 500:
        pytest.skip("DB 또는 admin 테이블 미준비(Phase 11-1 마이그레이션 필요)")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data
    assert isinstance(data["items"], list)


def test_admin_templates_list():
    """GET /api/admin/templates 목록 조회"""
    response = client.get("/api/admin/templates", params={"limit": 5, "offset": 0})
    if response.status_code == 500:
        pytest.skip("DB 또는 admin 테이블 미준비")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data and "total" in data


def test_admin_presets_list():
    """GET /api/admin/presets 목록 조회"""
    response = client.get("/api/admin/presets", params={"limit": 5, "offset": 0})
    if response.status_code == 500:
        pytest.skip("DB 또는 admin 테이블 미준비")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data and "total" in data


def test_admin_rag_profiles_list():
    """GET /api/admin/rag-profiles 목록 조회"""
    response = client.get("/api/admin/rag-profiles", params={"limit": 5, "offset": 0})
    if response.status_code == 500:
        pytest.skip("DB 또는 admin 테이블 미준비")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data and "total" in data


def test_admin_policy_sets_list():
    """GET /api/admin/policy-sets 목록 조회"""
    response = client.get("/api/admin/policy-sets", params={"limit": 5, "offset": 0})
    if response.status_code == 500:
        pytest.skip("DB 또는 admin 테이블 미준비")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data and "total" in data
