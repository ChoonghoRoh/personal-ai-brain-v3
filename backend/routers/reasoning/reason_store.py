"""Reasoning 결과 공유·의사결정 문서 저장 API (Phase 10-4-2, 10-4-3, 11-5-6, 17-4)"""
import json
import math
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

# Phase 17-4-1: 세션 관리 스키마
class SessionCreateRequest(BaseModel):
    title: Optional[str] = None


class SessionResponse(BaseModel):
    session_id: str
    title: Optional[str] = None


class SessionListItem(BaseModel):
    session_id: str
    title: Optional[str] = None
    turn_count: int
    last_question: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# Phase 17-4-4: 다중 삭제 스키마
class BulkDeleteRequest(BaseModel):
    session_ids: List[str]


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


# ---------- Phase 17-4-1: 세션 관리 ----------

@router.post("/sessions", response_model=SessionResponse)
async def create_session(req: SessionCreateRequest, db: Session = Depends(get_db)):
    """새 세션 생성. placeholder ReasoningResult 레코드로 세션을 초기화합니다."""
    session_id = str(uuid.uuid4())
    now = datetime.utcnow()
    title = req.title if req.title else f"새 대화 {now.strftime('%Y-%m-%d %H:%M')}"

    placeholder = ReasoningResult(
        session_id=session_id,
        question="",
        answer="",
        title=title,
        mode=None,
    )
    db.add(placeholder)
    db.commit()
    db.refresh(placeholder)

    return SessionResponse(session_id=session_id, title=title)


@router.get("/sessions")
async def list_sessions(page: int = 1, size: int = 10, db: Session = Depends(get_db)):
    """세션 목록 조회 (페이지네이션). session_id가 있는 레코드를 그룹핑합니다."""
    try:
        # session_id가 있는 레코드 전체 조회
        all_records = (
            db.query(ReasoningResult)
            .filter(ReasoningResult.session_id.isnot(None))
            .order_by(ReasoningResult.created_at.asc())
            .all()
        )

        # session_id별 그룹핑
        session_map: dict = {}
        for rec in all_records:
            sid = rec.session_id
            if sid not in session_map:
                session_map[sid] = {
                    "session_id": sid,
                    "title": rec.title,
                    "records": [],
                    "created_at": rec.created_at,
                    "updated_at": rec.created_at,
                }
            session_map[sid]["records"].append(rec)
            if rec.created_at and rec.created_at > session_map[sid]["updated_at"]:
                session_map[sid]["updated_at"] = rec.created_at

        # 세션 목록 구성 (최신 updated_at 기준 내림차순)
        sessions_sorted = sorted(
            session_map.values(),
            key=lambda s: s["updated_at"],
            reverse=True,
        )

        total = len(sessions_sorted)
        total_pages = math.ceil(total / size) if total > 0 else 1
        offset = (page - 1) * size
        page_sessions = sessions_sorted[offset: offset + size]

        result_list = []
        for s in page_sessions:
            records = s["records"]
            # placeholder 제외 실제 Q&A 턴
            real_turns = [r for r in records if r.question and r.question.strip()]
            turn_count = len(real_turns)
            last_question = real_turns[-1].question[:100] if real_turns else None
            # title: 세션 title이 없으면 첫 질문 사용
            title = s["title"]
            if not title and real_turns:
                title = real_turns[0].question[:50]

            result_list.append(SessionListItem(
                session_id=s["session_id"],
                title=title,
                turn_count=turn_count,
                last_question=last_question,
                created_at=s["created_at"].isoformat() if s["created_at"] else None,
                updated_at=s["updated_at"].isoformat() if s["updated_at"] else None,
            ))

        return {
            "sessions": [item.dict() for item in result_list],
            "total": total,
            "page": page,
            "size": size,
            "total_pages": total_pages,
        }
    except Exception as e:
        logger.error("세션 목록 조회 오류: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}")
async def get_session(session_id: str, db: Session = Depends(get_db)):
    """세션 상세 조회. 해당 session_id의 모든 ReasoningResult를 시간순으로 반환합니다."""
    try:
        records = (
            db.query(ReasoningResult)
            .filter(ReasoningResult.session_id == session_id)
            .order_by(ReasoningResult.created_at.asc())
            .all()
        )
        if not records:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")

        # title: 첫 레코드 기준
        title = records[0].title
        if not title:
            real = [r for r in records if r.question and r.question.strip()]
            title = real[0].question[:50] if real else None

        turns = []
        for r in records:
            # placeholder 제외
            if not r.question or not r.question.strip():
                continue
            turns.append({
                "id": r.id,
                "question": r.question,
                "answer": r.answer,
                "mode": r.mode,
                "summary": r.summary,
                "reasoning_steps": json.loads(r.reasoning_steps or "[]"),
                "context_chunks": json.loads(r.context_chunks or "[]"),
                "relations": json.loads(r.relations or "[]"),
                "recommendations": json.loads(r.recommendations or "{}"),
                "created_at": r.created_at.isoformat() if r.created_at else None,
            })

        return {
            "session_id": session_id,
            "title": title,
            "turns": turns,
            "turn_count": len(turns),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("세션 상세 조회 오류: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sessions/bulk")
async def bulk_delete_sessions(req: BulkDeleteRequest, db: Session = Depends(get_db)):
    """다중 세션 일괄 삭제."""
    try:
        deleted_count = 0
        for sid in req.session_ids:
            count = db.query(ReasoningResult).filter(
                ReasoningResult.session_id == sid
            ).delete()
            deleted_count += count
        db.commit()
        return {
            "message": "일괄 삭제 완료",
            "deleted_count": deleted_count,
            "session_count": len(req.session_ids),
        }
    except Exception as e:
        logger.error("세션 일괄 삭제 오류: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, db: Session = Depends(get_db)):
    """세션 삭제. 해당 session_id의 모든 ReasoningResult를 삭제합니다."""
    try:
        deleted_count = (
            db.query(ReasoningResult)
            .filter(ReasoningResult.session_id == session_id)
            .delete()
        )
        if deleted_count == 0:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
        db.commit()
        return {"message": "삭제 완료", "deleted_count": deleted_count}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("세션 삭제 오류: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
