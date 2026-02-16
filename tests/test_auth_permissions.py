"""Phase 14-1: 역할 기반 권한 검증 테스트

역할 계층(admin_system > admin_knowledge > user) 및
Admin API 접근 제어(401/403) 검증.
"""
import os
import pytest
from unittest.mock import patch
from datetime import timedelta

from fastapi.testclient import TestClient


# AUTH_ENABLED=true로 강제 설정 (모듈 로드 전)
@pytest.fixture(autouse=True)
def _enable_auth(monkeypatch):
    monkeypatch.setattr("backend.config.AUTH_ENABLED", True)
    monkeypatch.setattr("backend.middleware.auth.AUTH_ENABLED", True)
    monkeypatch.setattr("backend.routers.auth.auth.AUTH_ENABLED", True)


@pytest.fixture
def client():
    from backend.main import app
    return TestClient(app)


@pytest.fixture
def _tokens():
    """역할별 JWT 토큰 생성"""
    from backend.middleware.auth import create_access_token, ROLE_USER, ROLE_ADMIN_KNOWLEDGE, ROLE_ADMIN_SYSTEM

    def _make(role: str) -> str:
        return create_access_token(
            data={"sub": f"test_{role}", "role": role},
            expires_delta=timedelta(minutes=30),
        )

    return {
        "user": _make(ROLE_USER),
        "admin_knowledge": _make(ROLE_ADMIN_KNOWLEDGE),
        "admin_system": _make(ROLE_ADMIN_SYSTEM),
    }


# ============================================
# /api/auth/status 역할 반환 테스트
# ============================================

class TestAuthStatusRole:
    """인증 상태 API에서 role 필드 반환 검증"""

    def test_status_returns_role_when_auth_disabled(self, monkeypatch):
        """AUTH_ENABLED=false 시 role=admin_system 반환"""
        monkeypatch.setattr("backend.config.AUTH_ENABLED", False)
        monkeypatch.setattr("backend.middleware.auth.AUTH_ENABLED", False)
        monkeypatch.setattr("backend.routers.auth.auth.AUTH_ENABLED", False)
        from backend.main import app
        c = TestClient(app)
        resp = c.get("/api/auth/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["role"] == "admin_system"

    def test_status_returns_no_role_when_auth_enabled(self, client):
        """AUTH_ENABLED=true, 미인증 시 role=None"""
        resp = client.get("/api/auth/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["role"] is None

    def test_me_returns_role_with_jwt(self, client, _tokens):
        """JWT 인증 시 /api/auth/me에서 role 반환"""
        resp = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {_tokens['admin_system']}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["role"] == "admin_system"
        assert data["authenticated"] is True


# ============================================
# Admin API 권한 검증 (401/403)
# ============================================

class TestAdminApiPermissions:
    """Admin API 엔드포인트 접근 제어 검증"""

    ADMIN_ENDPOINTS = [
        "/api/admin/schemas",
        "/api/admin/templates",
        "/api/admin/presets",
        "/api/admin/rag-profiles",
        "/api/admin/policy-sets",
        "/api/admin/audit-logs",
    ]

    def test_admin_api_401_without_auth(self, client):
        """인증 없이 Admin API 접근 시 401"""
        for endpoint in self.ADMIN_ENDPOINTS:
            resp = client.get(endpoint)
            assert resp.status_code == 401, f"{endpoint} → {resp.status_code} (expected 401)"

    def test_admin_api_403_with_user_role(self, client, _tokens):
        """user 역할로 Admin API 접근 시 403"""
        headers = {"Authorization": f"Bearer {_tokens['user']}"}
        for endpoint in self.ADMIN_ENDPOINTS:
            resp = client.get(endpoint, headers=headers)
            assert resp.status_code == 403, f"{endpoint} → {resp.status_code} (expected 403)"

    def test_admin_api_403_with_admin_knowledge_role(self, client, _tokens):
        """admin_knowledge 역할로 Admin API(설정 관리) 접근 시 403"""
        headers = {"Authorization": f"Bearer {_tokens['admin_knowledge']}"}
        for endpoint in self.ADMIN_ENDPOINTS:
            resp = client.get(endpoint, headers=headers)
            assert resp.status_code == 403, f"{endpoint} → {resp.status_code} (expected 403)"

    def test_admin_api_accessible_with_admin_system(self, client, _tokens):
        """admin_system 역할로 Admin API 접근 시 200 또는 500(DB 미준비)"""
        headers = {"Authorization": f"Bearer {_tokens['admin_system']}"}
        for endpoint in self.ADMIN_ENDPOINTS:
            resp = client.get(endpoint, headers=headers)
            assert resp.status_code in (200, 500), (
                f"{endpoint} → {resp.status_code} (expected 200 or 500)"
            )


# ============================================
# 역할 계층 단위 테스트
# ============================================

class TestRoleHierarchy:
    """역할 계층 및 의존성 함수 검증"""

    def test_role_hierarchy_order(self):
        """역할 계층 순서: admin_system > admin_knowledge > user"""
        from backend.middleware.auth import ROLE_HIERARCHY, ROLE_USER, ROLE_ADMIN_KNOWLEDGE, ROLE_ADMIN_SYSTEM
        assert ROLE_HIERARCHY[ROLE_USER] < ROLE_HIERARCHY[ROLE_ADMIN_KNOWLEDGE]
        assert ROLE_HIERARCHY[ROLE_ADMIN_KNOWLEDGE] < ROLE_HIERARCHY[ROLE_ADMIN_SYSTEM]

    def test_jwt_token_contains_role(self):
        """JWT 토큰에 role claim 포함"""
        from backend.middleware.auth import create_access_token, verify_jwt_token
        token = create_access_token(data={"sub": "test", "role": "admin_knowledge"})
        decoded = verify_jwt_token(token)
        assert decoded is not None
        assert decoded.role == "admin_knowledge"

    def test_jwt_token_default_role(self):
        """JWT 토큰에 role 없으면 기본 user"""
        from backend.middleware.auth import create_access_token, verify_jwt_token
        token = create_access_token(data={"sub": "test"})
        decoded = verify_jwt_token(token)
        assert decoded is not None
        assert decoded.role == "user"


# ============================================
# 403 응답 규격 검증
# ============================================

class TestForbiddenResponse:
    """403 Forbidden 응답 detail 메시지 검증"""

    def test_403_detail_message(self, client, _tokens):
        """403 응답에 적절한 detail 메시지 포함"""
        headers = {"Authorization": f"Bearer {_tokens['user']}"}
        resp = client.get("/api/admin/schemas", headers=headers)
        assert resp.status_code == 403
        data = resp.json()
        assert "detail" in data
        assert "admin_system" in data["detail"].lower() or "permission" in data["detail"].lower()
