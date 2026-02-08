"""Task Plan Generator 테스트 - Claude Code CLI 기반"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.automation.project_analyzer import (
    find_related_files,
    extract_keywords_from_task,
    get_project_structure,
    collect_file_context,
)
from backend.services.automation.task_plan_generator import (
    generate_task_plan,
    _check_claude_cli_available,
)

client = TestClient(app)


class TestProjectAnalyzer:
    """프로젝트 분석 유틸리티 테스트"""

    def test_extract_keywords_from_task(self):
        """Task 제목에서 키워드 추출"""
        keywords = extract_keywords_from_task(
            task_title="Backend API 인증 기능 추가",
            task_description="JWT 토큰 기반 인증 구현"
        )
        assert len(keywords) > 0
        assert "backend" in keywords or "api" in keywords or "인증" in keywords

    def test_extract_keywords_filters_stopwords(self):
        """불용어 필터링 확인"""
        keywords = extract_keywords_from_task("the task is to add a feature")
        assert "the" not in keywords
        assert "is" not in keywords
        assert "to" not in keywords

    def test_find_related_files(self):
        """관련 파일 검색"""
        files = find_related_files(
            keywords=["config", "backend"],
            max_files=5
        )
        assert isinstance(files, list)
        if files:
            assert "relevance_score" in files[0]
            assert "path" in files[0]

    def test_get_project_structure(self):
        """프로젝트 구조 조회"""
        structure = get_project_structure(max_depth=2)
        assert "directories" in structure
        assert "key_files" in structure
        assert isinstance(structure["directories"], list)
        assert isinstance(structure["key_files"], list)

    def test_collect_file_context(self):
        """파일 컨텍스트 수집"""
        context = collect_file_context(
            file_paths=["backend/config.py"],
            max_content_per_file=1000
        )
        assert "files" in context
        assert "total_chars" in context
        assert "file_count" in context


class TestClaudeCliCheck:
    """Claude Code CLI 확인 테스트"""

    def test_check_claude_cli_not_installed(self):
        """Claude CLI 미설치 시 오류 메시지"""
        with patch('backend.services.automation.task_plan_generator._resolve_claude_cli_js', return_value=None):
            with patch('os.environ.get', return_value="/nonexistent/path"):
                with patch('pathlib.Path.exists', return_value=False):
                    available, error = _check_claude_cli_available()
                    assert available is False
                    assert "설치" in error or "CLI" in error


class TestTaskPlanGenerator:
    """Task Plan 생성 테스트"""

    def test_generate_task_plan_returns_structure(self):
        """Task Plan 생성 결과 구조 확인"""
        result = generate_task_plan(
            task_num="test-1",
            task_title="테스트 Task",
            phase_slug="test-phase",
        )
        # 구조 확인 (성공 여부와 무관)
        assert "task_plan" in result
        assert "test_plan" in result
        assert "analyzed_files" in result
        assert "success" in result
        assert "error" in result

    def test_generate_task_plan_cli_not_available(self):
        """Claude CLI 미사용 시 에러 반환"""
        with patch('backend.services.automation.task_plan_generator._check_claude_cli_available') as mock_check:
            mock_check.return_value = (False, "Claude Code 인증 토큰이 없습니다.")
            result = generate_task_plan(
                task_num="test-2",
                task_title="테스트 Task",
                phase_slug="test-phase",
            )
            assert result["success"] is False
            assert "토큰" in result["error"]
            assert result["task_plan"] == ""
            assert result["test_plan"] == ""

    def test_generate_task_plan_with_mock_cli(self):
        """Claude CLI Mock으로 Task Plan 생성"""
        mock_task_plan = "# Task Plan: 테스트\n\n## 목표\n테스트 목표"
        mock_test_plan = "# Test Plan: 테스트\n\n## 테스트 범위\n테스트"

        with patch('backend.services.automation.task_plan_generator._check_claude_cli_available') as mock_check:
            mock_check.return_value = (True, "")
            with patch('backend.services.automation.task_plan_generator._run_claude_cli') as mock_run:
                mock_run.side_effect = [
                    (True, mock_task_plan),  # Task Plan
                    (True, mock_test_plan),  # Test Plan
                ]
                result = generate_task_plan(
                    task_num="test-3",
                    task_title="Mock 테스트",
                    phase_slug="test-phase",
                )
                assert result["success"] is True
                assert "Task Plan" in result["task_plan"]
                assert "Test Plan" in result["test_plan"]


class TestTaskPlanAPI:
    """Task Plan API 엔드포인트 테스트"""

    def test_generate_task_plan_endpoint_structure(self):
        """POST /api/workflow/generate-task-plan 응답 구조 테스트"""
        response = client.post(
            "/api/workflow/generate-task-plan",
            json={
                "task_num": "api-test-1",
                "task_title": "API 테스트 Task",
                "phase_slug": "test-phase",
            }
        )
        assert response.status_code == 200
        data = response.json()
        # 응답 구조 확인
        assert "success" in data
        assert "task_plan" in data
        assert "test_plan" in data
        assert "analyzed_files" in data
        assert "error" in data

    def test_generate_task_plan_endpoint_validation(self):
        """필수 필드 검증 테스트"""
        # task_num 누락
        response = client.post(
            "/api/workflow/generate-task-plan",
            json={
                "task_title": "Test Task",
                "phase_slug": "test-phase",
            }
        )
        assert response.status_code == 422  # Validation Error

    def test_generate_task_plan_endpoint_with_context(self):
        """컨텍스트 힌트를 포함한 API 테스트"""
        response = client.post(
            "/api/workflow/generate-task-plan",
            json={
                "task_num": "api-test-2",
                "task_title": "Backend 설정 기능",
                "phase_slug": "test-phase",
                "context_hint": "config backend settings"
            }
        )
        assert response.status_code == 200
        data = response.json()
        # error 필드에 메시지가 있거나 성공
        assert "error" in data
