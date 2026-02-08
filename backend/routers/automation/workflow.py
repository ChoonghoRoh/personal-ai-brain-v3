"""n8n 워크플로우 연동 API (Phase 8-2-7 Task 실행 등)"""
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.models.database import get_db
from backend.services.automation.workflow_task_service import run_task
from backend.services.automation.task_plan_generator import generate_task_plan

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/workflow", tags=["workflow"])


class RunTaskRequest(BaseModel):
    task_id: int


class RunTaskResponse(BaseModel):
    success: bool
    message: str
    task_id: int


class GenerateTaskPlanRequest(BaseModel):
    """Task Plan 생성 요청"""
    task_num: str  # 예: "8-2-7"
    task_title: str  # 예: "Claude CLI Task 실행 기능"
    phase_slug: str  # 예: "phase-8-2"
    context_hint: Optional[str] = None  # 예: "backend API, automation"


class GenerateTaskPlanResponse(BaseModel):
    """Task Plan 생성 응답 (todo-list 기반 Task Plan만 생성, test-report 없음)"""
    success: bool
    task_plan: str
    analyzed_files: List[str]
    error: Optional[str] = None


@router.post("/run-task", response_model=RunTaskResponse)
def run_task_execution(
    body: RunTaskRequest,
    db: Session = Depends(get_db),
):
    """
    workflow_tasks 1건 실행 (n8n HTTP Request 호출용).
    로컬 Backend(Python)에서 실행되므로 n8n 컨테이너에 Python 불필요.
    """
    success, message = run_task(db, body.task_id)
    if not success and "not found" in message.lower():
        raise HTTPException(status_code=404, detail=message)
    return RunTaskResponse(success=success, message=message, task_id=body.task_id)


@router.post("/generate-task-plan", response_model=GenerateTaskPlanResponse)
def generate_task_plan_endpoint(body: GenerateTaskPlanRequest):
    """
    todo-list 기반 Task Plan만 생성. n8n 워크플로우에서 HTTP Request로 호출.

    - task_num: Task 번호 (예: "8-2-7")
    - task_title: Task 제목
    - phase_slug: Phase 식별자 (예: "phase-8-2")
    - context_hint: 추가 컨텍스트 힌트 (선택)

    Returns:
        task_plan: 생성된 Task Plan (마크다운, todo용 산출물)
        analyzed_files: 분석된 파일 목록
    """
    logger.info(f"Task Plan 생성 요청: {body.task_num} - {body.task_title}")

    result = generate_task_plan(
        task_num=body.task_num,
        task_title=body.task_title,
        phase_slug=body.phase_slug,
        context_hint=body.context_hint,
    )

    return GenerateTaskPlanResponse(
        success=result["success"],
        task_plan=result["task_plan"],
        analyzed_files=result["analyzed_files"],
        error=result.get("error"),
    )
