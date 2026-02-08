"""Reasoning 추천 API — 관련 청크/라벨/샘플 질문/탐색 제안 (Phase 9-3-1)"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.models.database import get_db
from backend.services.reasoning.recommendation_service import get_recommendation_service

router = APIRouter(prefix="/api/reason/recommendations", tags=["reason-recommendations"])


@router.get("/chunks")
async def get_recommendations_chunks(
    chunk_ids: str = Query(..., description="쉼표로 구분된 청크 ID 목록 (예: 1,2,3)"),
    limit: int = Query(5, ge=1, le=20, description="반환할 추천 수"),
    db: Session = Depends(get_db),
):
    """관련 청크 추천."""
    try:
        ids = [int(x.strip()) for x in chunk_ids.split(",") if x.strip()]
    except ValueError:
        raise HTTPException(status_code=400, detail="chunk_ids must be comma-separated integers")
    if not ids:
        raise HTTPException(status_code=400, detail="chunk_ids parameter is required")
    svc = get_recommendation_service(db)
    recommendations = svc.recommend_related_chunks(chunk_ids=ids, limit=limit)
    return {
        "recommendations": recommendations,
        "total": len(recommendations),
        "source": "hybrid_search",
    }


@router.get("/labels")
async def get_recommendations_labels(
    content: str = Query(..., description="라벨을 추천받을 텍스트 내용"),
    existing_label_ids: Optional[str] = Query(None, description="제외할 라벨 ID (쉼표 구분)"),
    limit: int = Query(5, ge=1, le=15, description="반환할 추천 수"),
    db: Session = Depends(get_db),
):
    """라벨 추천."""
    if not content or not content.strip():
        raise HTTPException(status_code=400, detail="content parameter is required")
    existing = []
    if existing_label_ids:
        try:
            existing = [int(x.strip()) for x in existing_label_ids.split(",") if x.strip()]
        except ValueError:
            pass
    svc = get_recommendation_service(db)
    recommendations = svc.recommend_labels(
        content=content.strip(),
        existing_label_ids=existing if existing else None,
        limit=limit,
    )
    return {
        "recommendations": recommendations,
        "total": len(recommendations),
        "source": "combined",
    }


@router.get("/questions")
async def get_recommendations_questions(
    project_id: Optional[int] = Query(None, description="프로젝트 필터"),
    label_ids: Optional[str] = Query(None, description="라벨 필터 (쉼표 구분)"),
    limit: int = Query(3, ge=1, le=10, description="생성할 질문 수"),
    db: Session = Depends(get_db),
):
    """샘플 질문 생성 (LLM 사용, 실패 시 빈 목록)."""
    label_id_list = None
    if label_ids:
        try:
            label_id_list = [int(x.strip()) for x in label_ids.split(",") if x.strip()]
        except ValueError:
            pass
    svc = get_recommendation_service(db)
    recommendations = svc.generate_sample_questions(
        project_id=project_id,
        label_ids=label_id_list,
        limit=limit,
    )
    if not recommendations:
        return {
            "recommendations": [],
            "total": 0,
            "source": "llm_unavailable",
            "message": "LLM 서비스를 사용할 수 없거나 질문을 생성하지 못했습니다. 나중에 다시 시도해주세요.",
        }
    return {
        "recommendations": recommendations,
        "total": len(recommendations),
        "source": "llm_generated",
    }


@router.get("/explore")
async def get_recommendations_explore(
    reasoning_result_id: Optional[int] = Query(None, description="추론 결과 ID"),
    context_chunk_ids: Optional[str] = Query(None, description="컨텍스트 청크 ID (쉼표 구분)"),
    limit: int = Query(5, ge=1, le=10),
    db: Session = Depends(get_db),
):
    """추가 탐색 제안 (프로젝트/라벨/질문)."""
    from backend.models.models import ReasoningResult
    if reasoning_result_id is not None:
        res = db.query(ReasoningResult).filter(ReasoningResult.id == reasoning_result_id).first()
        if not res:
            raise HTTPException(status_code=404, detail="Reasoning result not found")
    chunk_id_list = None
    if context_chunk_ids:
        try:
            chunk_id_list = [int(x.strip()) for x in context_chunk_ids.split(",") if x.strip()]
        except ValueError:
            pass
    if not chunk_id_list and reasoning_result_id is None:
        chunk_id_list = []
    svc = get_recommendation_service(db)
    recommendations = svc.suggest_exploration(
        context_chunk_ids=chunk_id_list,
        reasoning_result_id=reasoning_result_id,
        limit=limit,
    )
    return {
        "recommendations": recommendations,
        "total": len(recommendations),
        "source": "context_analysis",
    }
