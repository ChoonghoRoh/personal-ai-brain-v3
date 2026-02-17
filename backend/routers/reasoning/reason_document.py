"""Phase 15-3: 지정 문서 대상 Reasoning API

지정 문서(document_ids) 또는 폴더 경로(folder_path)에 대해
기존 Reasoning 엔진을 실행하고, 결과를 저장·조회하는 전용 API.
"""
import json
import uuid
import logging
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.models.database import get_db
from backend.models.models import Document, KnowledgeChunk, ReasoningResult
from backend.services.search.search_service import get_search_service
from backend.services.reasoning.dynamic_reasoning_service import get_dynamic_reasoning_service
from backend.routers.reasoning.reason import (
    collect_chunks_by_document_ids,
    collect_chunks_by_question_in_documents,
    expand_chunks_with_relations,
    build_context_chunks,
    collect_relations,
    generate_reasoning_answer,
)
from backend.routers.reasoning.reason_stream import format_sse_event
from backend.config import KNOWLEDGE_FOLDER_PATH

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reasoning", tags=["Document Reasoning"])


# ---------- 요청/응답 스키마 ----------

class RunOnDocumentsRequest(BaseModel):
    document_ids: Optional[List[int]] = None
    folder_path: Optional[str] = None
    mode: str = "design_explain"
    question: Optional[str] = None
    template_id: Optional[str] = None
    model: Optional[str] = None


class RunOnDocumentsResponse(BaseModel):
    session_id: str
    task_id: str
    message: str
    document_count: int
    chunk_count: int


class DocumentReasoningResult(BaseModel):
    document_id: int
    document_name: Optional[str] = None
    results: list


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: int
    current_document: Optional[str] = None
    message: Optional[str] = None


# ---------- 진행 상태 관리 ----------

_task_status = {}


# ---------- 헬퍼 ----------

def _resolve_document_ids(db: Session, req: RunOnDocumentsRequest) -> List[int]:
    """document_ids 또는 folder_path에서 문서 ID 목록 해석"""
    if req.document_ids:
        # 존재 여부 검증
        existing = db.query(Document.id).filter(Document.id.in_(req.document_ids)).all()
        existing_ids = [row[0] for row in existing]
        if not existing_ids:
            raise HTTPException(status_code=404, detail="지정된 문서가 존재하지 않습니다.")
        return existing_ids

    if req.folder_path:
        # folder_path 기반 문서 조회 (file_path LIKE 패턴)
        folder = req.folder_path.rstrip("/")
        docs = db.query(Document.id).filter(
            Document.file_path.like(f"{folder}/%")
        ).all()
        if not docs:
            raise HTTPException(
                status_code=404,
                detail=f"폴더 '{folder}'에 해당하는 문서가 없습니다.",
            )
        return [row[0] for row in docs]

    raise HTTPException(
        status_code=400,
        detail="document_ids 또는 folder_path 중 하나를 지정해야 합니다.",
    )


def _save_reasoning_result(
    db: Session,
    *,
    session_id: str,
    question: str,
    answer: str,
    mode: str,
    reasoning_steps: list,
    context_chunks: list,
    relations: list,
    document_ids: List[int],
) -> ReasoningResult:
    """Reasoning 결과를 DB에 저장"""
    result = ReasoningResult(
        question=question or f"[문서 Reasoning] mode={mode}, docs={document_ids}",
        answer=answer,
        mode=mode,
        reasoning_steps=json.dumps(reasoning_steps, ensure_ascii=False),
        context_chunks=json.dumps(context_chunks, ensure_ascii=False),
        relations=json.dumps(relations, ensure_ascii=False),
        recommendations=json.dumps({"document_ids": document_ids}, ensure_ascii=False),
        share_id=session_id,
        view_count=0,
        is_private=0,
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


# ---------- API 엔드포인트 ----------

@router.post("/run-on-documents", response_model=RunOnDocumentsResponse)
async def run_on_documents(req: RunOnDocumentsRequest, db: Session = Depends(get_db)):
    """지정 문서(들)에 대해 Reasoning 실행 (동기).

    document_ids 또는 folder_path로 대상 문서를 지정하고,
    mode와 question으로 Reasoning을 실행합니다.
    """
    # 1. 문서 ID 해석
    document_ids = _resolve_document_ids(db, req)

    # 2. 청크 수집
    reasoning_steps = [f"대상 문서 {len(document_ids)}건 확인"]
    if req.question and req.question.strip():
        chunks = collect_chunks_by_question_in_documents(
            db, req.question, document_ids, top_k=20, reasoning_steps=reasoning_steps,
        )
        if len(chunks) < 5:
            doc_chunks = collect_chunks_by_document_ids(db, document_ids)
            seen = {c.id for c in chunks}
            for c in doc_chunks:
                if c.id not in seen:
                    seen.add(c.id)
                    chunks.append(c)
            reasoning_steps.append(f"문서 전체 청크 보강: 총 {len(chunks)}개")
    else:
        chunks = collect_chunks_by_document_ids(db, document_ids)
        reasoning_steps.append(f"문서에서 {len(chunks)}개 청크 수집")

    if not chunks:
        raise HTTPException(status_code=400, detail="선택한 문서에 승인된 청크가 없습니다.")

    # 3. 관계 확장 + 컨텍스트 구성
    all_chunks = expand_chunks_with_relations(db, chunks, reasoning_steps)
    context_chunks = build_context_chunks(db, all_chunks, reasoning_steps)
    relations = collect_relations(db, chunks)

    # 4. LLM Reasoning 실행
    reasoning_steps.append("Reasoning 실행 중...")
    dynamic_svc = get_dynamic_reasoning_service()
    answer = dynamic_svc.generate_reasoning(
        req.question, context_chunks, req.mode, max_tokens=500, model=req.model,
    )
    if answer is None:
        answer = generate_reasoning_answer(
            req.mode, req.question, all_chunks, context_chunks, relations,
        )
    reasoning_steps.append("Reasoning 완료")

    # 5. 결과 저장
    session_id = uuid.uuid4().hex[:12]
    task_id = uuid.uuid4().hex[:8]
    _save_reasoning_result(
        db,
        session_id=session_id,
        question=req.question or "",
        answer=answer,
        mode=req.mode,
        reasoning_steps=reasoning_steps,
        context_chunks=context_chunks,
        relations=relations,
        document_ids=document_ids,
    )

    return RunOnDocumentsResponse(
        session_id=session_id,
        task_id=task_id,
        message=f"{len(document_ids)}개 문서에 대한 Reasoning 완료",
        document_count=len(document_ids),
        chunk_count=len(chunks),
    )


@router.get("/run-on-documents/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """실행 중인 Reasoning 진행 상황 조회 (폴링용).

    현재는 동기 실행이므로 항상 completed를 반환합니다.
    비동기 실행 도입 시 실제 진행 상태를 반환합니다.
    """
    status = _task_status.get(task_id)
    if status:
        return TaskStatusResponse(**status)
    # 동기 실행 시 task_id로 조회 → 완료 처리
    return TaskStatusResponse(
        task_id=task_id,
        status="completed",
        progress=100,
        message="Reasoning 완료",
    )


@router.get("/results-by-documents")
async def get_results_by_documents(
    document_ids: str = Query(..., description="콤마 구분 문서 ID (예: 1,2,3)"),
    db: Session = Depends(get_db),
):
    """문서별 Reasoning 결과 목록 조회.

    document_ids 파라미터로 지정된 문서에 대한 기존 Reasoning 결과를 반환합니다.
    """
    try:
        doc_id_list = [int(x.strip()) for x in document_ids.split(",") if x.strip()]
    except ValueError:
        raise HTTPException(status_code=400, detail="document_ids는 콤마 구분 정수여야 합니다.")

    if not doc_id_list:
        raise HTTPException(status_code=400, detail="document_ids가 비어 있습니다.")

    # ReasoningResult에서 recommendations JSON에 document_ids가 포함된 결과 조회
    results = db.query(ReasoningResult).order_by(ReasoningResult.id.desc()).limit(200).all()

    # 문서 이름 캐시
    doc_names = {}
    docs = db.query(Document.id, Document.file_name).filter(Document.id.in_(doc_id_list)).all()
    for doc_id, fname in docs:
        doc_names[doc_id] = fname

    # 문서별 결과 매핑
    doc_results = {did: [] for did in doc_id_list}
    for r in results:
        try:
            rec = json.loads(r.recommendations) if r.recommendations else {}
        except (json.JSONDecodeError, TypeError):
            rec = {}
        saved_doc_ids = rec.get("document_ids", [])
        if not saved_doc_ids:
            continue
        for did in doc_id_list:
            if did in saved_doc_ids:
                doc_results[did].append({
                    "id": r.id,
                    "question": r.question,
                    "answer": (r.answer or "")[:300],
                    "mode": r.mode,
                    "share_id": r.share_id,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                })

    return [
        DocumentReasoningResult(
            document_id=did,
            document_name=doc_names.get(did),
            results=doc_results.get(did, []),
        )
        for did in doc_id_list
    ]
