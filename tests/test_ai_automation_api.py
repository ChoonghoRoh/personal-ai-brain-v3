"""AI 자동화 API 테스트 (Phase 15-2-1)"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from backend.main import app
from backend.services.automation import ai_workflow_state


@pytest.fixture
def client():
    """테스트 클라이언트"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def cleanup_tasks():
    """각 테스트 후 태스크 정리"""
    yield
    ai_workflow_state.active_tasks.clear()


def test_create_task():
    """태스크 생성 테스트"""
    task_id = ai_workflow_state.create_task(
        document_ids=[1, 2, 3],
        auto_approve=True,
    )

    assert task_id is not None
    assert task_id in ai_workflow_state.active_tasks

    task = ai_workflow_state.get_task(task_id)
    assert task is not None
    assert task.document_ids == [1, 2, 3]
    assert task.auto_approve is True
    assert task.status == "running"
    assert task.progress_pct == 0


def test_update_progress():
    """진행 상황 업데이트 테스트"""
    task_id = ai_workflow_state.create_task([1], False)

    ai_workflow_state.update_progress(
        task_id=task_id,
        stage_name="테스트 단계",
        progress_pct=50,
        message="진행 중",
    )

    task = ai_workflow_state.get_task(task_id)
    assert task.current_stage == "테스트 단계"
    assert task.progress_pct == 50
    assert len(task.stages) == 1
    assert task.stages[0]["name"] == "테스트 단계"
    assert task.stages[0]["progress"] == 50


def test_complete_task():
    """태스크 완료 테스트"""
    task_id = ai_workflow_state.create_task([1], False)

    results = {"chunks_created": 5, "keywords_extracted": 10}
    ai_workflow_state.complete_task(task_id, results)

    task = ai_workflow_state.get_task(task_id)
    assert task.status == "completed"
    assert task.progress_pct == 100
    assert task.results == results
    assert task.completed_at is not None


def test_fail_task():
    """태스크 실패 테스트"""
    task_id = ai_workflow_state.create_task([1], False)

    ai_workflow_state.fail_task(
        task_id=task_id,
        error="테스트 에러",
        failed_stage="단계2",
    )

    task = ai_workflow_state.get_task(task_id)
    assert task.status == "failed"
    assert task.error == "테스트 에러"
    assert "실패" in task.current_stage


def test_cancel_task():
    """태스크 취소 테스트"""
    task_id = ai_workflow_state.create_task([1], False)

    success = ai_workflow_state.cancel_task(task_id)
    assert success is True

    task = ai_workflow_state.get_task(task_id)
    assert task.status == "cancelled"
    assert task.cancelled is True


def test_cancel_completed_task():
    """완료된 태스크 취소 시도 테스트"""
    task_id = ai_workflow_state.create_task([1], False)
    ai_workflow_state.complete_task(task_id, {})

    success = ai_workflow_state.cancel_task(task_id)
    assert success is False


def test_list_tasks():
    """태스크 목록 조회 테스트"""
    task_id1 = ai_workflow_state.create_task([1], False)
    task_id2 = ai_workflow_state.create_task([2], True)

    tasks = ai_workflow_state.list_tasks(limit=10)

    assert len(tasks) == 2
    assert tasks[0]["task_id"] == task_id2  # 최근 생성 순
    assert tasks[1]["task_id"] == task_id1


def test_format_sse_event():
    """SSE 이벤트 포맷 테스트"""
    event = ai_workflow_state.format_sse_event(
        "progress",
        {"stage": "단계1", "percent": 30},
    )

    assert "event: progress" in event
    assert "data:" in event
    assert "단계1" in event
    assert "30" in event


def test_run_full_workflow_api(client):
    """전체 워크플로우 실행 API 테스트"""
    with patch("backend.routers.automation.automation.require_admin_knowledge") as mock_auth:
        mock_user = MagicMock()
        mock_user.username = "test_user"
        mock_auth.return_value = mock_user

        response = client.post(
            "/api/automation/run-full",
            json={
                "document_ids": [1, 2, 3],
                "auto_approve": True,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert "message" in data
        assert "3개" in data["message"]


def test_run_full_workflow_empty_documents(client):
    """빈 문서 목록으로 워크플로우 실행 시도 테스트"""
    with patch("backend.routers.automation.automation.require_admin_knowledge") as mock_auth:
        mock_user = MagicMock()
        mock_user.username = "test_user"
        mock_auth.return_value = mock_user

        response = client.post(
            "/api/automation/run-full",
            json={
                "document_ids": [],
                "auto_approve": False,
            },
        )

        assert response.status_code == 400
        assert "비어 있습니다" in response.json()["detail"]


def test_cancel_workflow_api(client):
    """워크플로우 취소 API 테스트"""
    task_id = ai_workflow_state.create_task([1], False)

    with patch("backend.routers.automation.automation.require_admin_knowledge") as mock_auth:
        mock_user = MagicMock()
        mock_user.username = "test_user"
        mock_auth.return_value = mock_user

        response = client.post(f"/api/automation/cancel/{task_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"
        assert "취소 요청됨" in data["message"]


def test_cancel_nonexistent_task(client):
    """존재하지 않는 태스크 취소 시도 테스트"""
    with patch("backend.routers.automation.automation.require_admin_knowledge") as mock_auth:
        mock_user = MagicMock()
        mock_user.username = "test_user"
        mock_auth.return_value = mock_user

        response = client.post("/api/automation/cancel/nonexistent-task-id")

        assert response.status_code == 404


def test_list_tasks_api(client):
    """태스크 목록 조회 API 테스트"""
    ai_workflow_state.create_task([1], False)
    ai_workflow_state.create_task([2], True)

    with patch("backend.routers.automation.automation.require_admin_knowledge") as mock_auth:
        mock_user = MagicMock()
        mock_user.username = "test_user"
        mock_auth.return_value = mock_user

        response = client.get("/api/automation/tasks")

        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert "count" in data
        assert data["count"] == 2


def test_cleanup_old_tasks():
    """오래된 태스크 정리 테스트"""
    task_id1 = ai_workflow_state.create_task([1], False)
    task_id2 = ai_workflow_state.create_task([2], False)

    # 태스크 완료 처리
    ai_workflow_state.complete_task(task_id1, {})
    ai_workflow_state.complete_task(task_id2, {})

    # 즉시 정리 (max_age_seconds=0)
    removed = ai_workflow_state.cleanup_old_tasks(max_age_seconds=0)

    assert removed == 2
    assert len(ai_workflow_state.active_tasks) == 0


def test_is_cancelled():
    """취소 상태 확인 테스트"""
    task_id = ai_workflow_state.create_task([1], False)

    assert ai_workflow_state.is_cancelled(task_id) is False

    ai_workflow_state.cancel_task(task_id)

    assert ai_workflow_state.is_cancelled(task_id) is True


def test_is_cancelled_nonexistent_task():
    """존재하지 않는 태스크 취소 상태 확인 테스트"""
    assert ai_workflow_state.is_cancelled("nonexistent") is False
