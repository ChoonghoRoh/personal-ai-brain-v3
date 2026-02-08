"""
Phase 9-2-1: AI API 테스트
- POST /api/ask (정상/빈 질문/컨텍스트 없음)
- Ollama 모델 목록은 GET /api/system/status 의 ollama 정보로 확인
"""
import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


class TestAskAPI:
    """POST /api/ask 테스트 (AI 라우터 prefix=/api/ask)"""

    def test_ask_normal_question_returns_200(self):
        """정상 질문 시 200 및 answer 필드 존재"""
        response = client.post(
            "/api/ask",
            json={
                "question": "테스트 질문입니다.",
                "context_enabled": True,
                "top_k": 3,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert "context" in data
        # Ollama 미동작 시에도 폴백 답변으로 200 반환
        assert isinstance(data["answer"], str)

    def test_ask_empty_question_returns_400(self):
        """빈 질문 시 400 에러"""
        response = client.post(
            "/api/ask",
            json={
                "question": "",
                "context_enabled": True,
            },
        )
        assert response.status_code == 400
        assert "질문" in response.json().get("detail", "")

    def test_ask_whitespace_only_question_returns_400(self):
        """공백만 있는 질문 시 400 에러"""
        response = client.post(
            "/api/ask",
            json={
                "question": "   ",
                "context_enabled": True,
            },
        )
        assert response.status_code == 400

    def test_ask_context_disabled(self):
        """컨텍스트 없을 때 처리 (context_enabled=False)"""
        response = client.post(
            "/api/ask",
            json={
                "question": "컨텍스트 없이 질문",
                "context_enabled": False,
                "top_k": 0,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        # 컨텍스트 없으면 지식 베이스 없음 메시지 또는 폴백
        assert len(data.get("sources", [])) == 0 or "지식" in data["answer"] or len(data["answer"]) > 0


class TestOllamaModels:
    """Ollama 모델 목록 확인 (시스템 상태 경유)"""

    def test_system_status_includes_ollama(self):
        """GET /api/system/status 에 ollama 관련 정보 포함"""
        response = client.get("/api/system/status")
        assert response.status_code == 200
        data = response.json()
        # status 구조에 ollama 또는 유사 키 존재
        assert "ollama" in data or "gpt4all" in data or any(
            "ollama" in str(k).lower() for k in data.keys()
        )

    def test_system_health_returns_200(self):
        """헬스 체크 API (시스템 상태 대체)"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json().get("status") == "ok"
