"""Reasoning 결과 공유·의사결정 문서 저장 API (Phase 10-4-2, 10-4-3, 11-5-6)"""
import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.models.database import get_db
from backend.models.models import ReasoningResult

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reason", tags=["Reasoning Store"])


# ---------- 요청 스키마 ----------

class ShareRequest(BaseModel):
    question: str
    answer: str
    mode: Optional[str] = None
    reasoning_steps: Optional[list] = None
    context_chunks: Optional[list] = None
    relations: Optional[list] = None
    recommendations: Optional[dict] = None
    # 11-5-6: 공유 URL 고도화
    expires_in_days: Optional[int] = None  # None이면 무제한
    is_private: Optional[bool] = False


class DecisionSaveRequest(BaseModel):
    title: str
    summary: Optional[str] = None
    question: str
    answer: str
    mode: Optional[str] = None
    reasoning_steps: Optional[list] = None
    context_chunks: Optional[list] = None
    relations: Optional[list] = None
    recommendations: Optional[dict] = None


# ---------- Phase 10-4-2: 결과 공유 ----------

@router.post("/share")
async def create_share(req: ShareRequest, db: Session = Depends(get_db)):
    """결과 스냅샷을 저장하고 공유 ID 반환. 11-5-6: 만료·비공개 옵션 지원."""
    share_id = uuid.uuid4().hex[:8]
    now = datetime.utcnow()
    expires_at = (now + timedelta(days=req.expires_in_days)) if req.expires_in_days else None
    result = ReasoningResult(
        question=req.question,
        answer=req.answer,
        mode=req.mode,
        reasoning_steps=json.dumps(req.reasoning_steps or [], ensure_ascii=False),
        context_chunks=json.dumps(req.context_chunks or [], ensure_ascii=False),
        relations=json.dumps(req.relations or [], ensure_ascii=False),
        recommendations=json.dumps(req.recommendations or {}, ensure_ascii=False),
        share_id=share_id,
        expires_at=expires_at,
        view_count=0,
        is_private=1 if req.is_private else 0,
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return {
        "share_id": share_id,
        "url": f"/reason?share={share_id}",
        "expires_at": expires_at.isoformat() if expires_at else None,
        "is_private": req.is_private,
    }


@router.get("/share/{share_id}")
async def get_shared_result(share_id: str, db: Session = Depends(get_db)):
    """공유 ID로 결과 조회. 11-5-6: 만료·조회 횟수 적용."""
    result = db.query(ReasoningResult).filter(ReasoningResult.share_id == share_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="공유 결과를 찾을 수 없습니다.")
    if result.expires_at and result.expires_at < datetime.utcnow():
        raise HTTPException(status_code=410, detail="공유 링크가 만료되었습니다.")
    result.view_count = (result.view_count or 0) + 1
    db.commit()
    return {
        "id": result.id,
        "share_id": result.share_id,
        "question": result.question,
        "answer": result.answer,
        "mode": result.mode,
        "reasoning_steps": json.loads(result.reasoning_steps or "[]"),
        "context_chunks": json.loads(result.context_chunks or "[]"),
        "relations": json.loads(result.relations or "[]"),
        "recommendations": json.loads(result.recommendations or "{}"),
        "created_at": result.created_at.isoformat() if result.created_at else None,
        "view_count": result.view_count,
        "expires_at": result.expires_at.isoformat() if result.expires_at else None,
    }


# ---------- Phase 10-4-3: 의사결정 문서 저장 ----------

@router.post("/decisions")
async def save_decision(req: DecisionSaveRequest, db: Session = Depends(get_db)):
    """의사결정 문서 저장."""
    result = ReasoningResult(
        title=req.title,
        summary=req.summary,
        question=req.question,
        answer=req.answer,
        mode=req.mode,
        reasoning_steps=json.dumps(req.reasoning_steps or [], ensure_ascii=False),
        context_chunks=json.dumps(req.context_chunks or [], ensure_ascii=False),
        relations=json.dumps(req.relations or [], ensure_ascii=False),
        recommendations=json.dumps(req.recommendations or {}, ensure_ascii=False),
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return {
        "id": result.id,
        "title": result.title,
        "created_at": result.created_at.isoformat() if result.created_at else None,
    }


@router.get("/decisions")
async def list_decisions(q: Optional[str] = None, db: Session = Depends(get_db)):
    """의사결정 문서 목록 조회. 11-5-6: 검색(q) — title/summary 필터."""
    qry = db.query(ReasoningResult).filter(ReasoningResult.title.isnot(None))
    if q and q.strip():
        term = f"%{q.strip()}%"
        qry = qry.filter(
            (ReasoningResult.title.ilike(term)) | (ReasoningResult.summary.ilike(term))
        )
    results = qry.order_by(ReasoningResult.created_at.desc()).limit(50).all()
    return {
        "decisions": [
            {
                "id": r.id,
                "title": r.title,
                "summary": r.summary,
                "question": r.question,
                "mode": r.mode,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in results
        ],
        "count": len(results),
    }


@router.get("/decisions/{decision_id}")
async def get_decision(decision_id: int, db: Session = Depends(get_db)):
    """의사결정 문서 상세 조회."""
    result = db.query(ReasoningResult).filter(ReasoningResult.id == decision_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="의사결정 문서를 찾을 수 없습니다.")
    return {
        "id": result.id,
        "title": result.title,
        "summary": result.summary,
        "question": result.question,
        "answer": result.answer,
        "mode": result.mode,
        "reasoning_steps": json.loads(result.reasoning_steps or "[]"),
        "context_chunks": json.loads(result.context_chunks or "[]"),
        "relations": json.loads(result.relations or "[]"),
        "recommendations": json.loads(result.recommendations or "{}"),
        "share_id": result.share_id,
        "created_at": result.created_at.isoformat() if result.created_at else None,
    }


@router.delete("/decisions/{decision_id}")
async def delete_decision(decision_id: int, db: Session = Depends(get_db)):
    """의사결정 문서 삭제."""
    result = db.query(ReasoningResult).filter(ReasoningResult.id == decision_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="의사결정 문서를 찾을 수 없습니다.")
    db.delete(result)
    db.commit()
    return {"message": "삭제 완료", "id": decision_id}
