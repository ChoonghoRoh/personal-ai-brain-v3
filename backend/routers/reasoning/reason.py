"""Reasoning API 라우터"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from pydantic import BaseModel

from backend.models.database import get_db
from backend.services.reasoning.dynamic_reasoning_service import get_dynamic_reasoning_service
from backend.services.reasoning.recommendation_service import get_recommendation_service

# --- 헬퍼 함수 import (reason_helpers.py) ---
from backend.routers.reasoning.reason_helpers import (
    collect_knowledge_from_projects,
    collect_knowledge_from_labels,
    collect_knowledge_from_label_ids,
    collect_knowledge_from_category,
    collect_chunks_by_document_ids,
    collect_chunks_by_question_in_documents,
    trace_relations,
    parse_reasoning_inputs,
    collect_knowledge_chunks,
    expand_chunks_with_relations,
    collect_chunks_by_question,
    add_semantic_search_results,
    build_context_chunks,
    collect_relations,
    generate_reasoning_answer,
)

router = APIRouter(prefix="/api/reason", tags=["Reasoning"])


# --- Pydantic 모델 ---

class ReasonFilters(BaseModel):  # Phase 7.7, 15-3
    project_ids: Optional[List[int]] = None
    category_label_ids: Optional[List[int]] = None
    keyword_group_ids: Optional[List[int]] = None
    keyword_ids: Optional[List[int]] = None
    document_ids: Optional[List[int]] = None  # Phase 15-3


class ReasonRequest(BaseModel):
    mode: str = "design_explain"  # design_explain, risk_review, next_steps, history_trace
    inputs: Dict
    question: Optional[str] = None
    filters: Optional[ReasonFilters] = None  # Phase 7.7: 필터 확장
    model: Optional[str] = None  # Reasoning용 Ollama 모델. 없으면 OLLAMA_MODEL 사용


class ReasonResponse(BaseModel):
    answer: str
    context_chunks: List[Dict]
    relations: List[Dict]
    reasoning_steps: List[str]
    recommendations: Optional[Dict] = None  # Phase 9-3-1


# --- 엔드포인트 ---

@router.post("", response_model=ReasonResponse)
async def reason(request: ReasonRequest, db: Session = Depends(get_db)):
    """Reasoning 실행. 질문이 있으면 질문 기반 의미 검색 우선, 프로젝트/라벨은 보조 조회."""
    reasoning_steps = []

    # 1. 입력 파싱
    reasoning_steps.append("입력 파싱 중...")
    project_ids, label_names, filter_label_ids, document_ids = parse_reasoning_inputs(request)
    question = (request.question or "").strip()

    # 2. 지식 수집
    chunks = []

    # Phase 15-3: 문서 기반 수집 우선
    if document_ids:
        if question:
            chunks = collect_chunks_by_question_in_documents(
                db, question, document_ids, top_k=20, reasoning_steps=reasoning_steps
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
    elif question:
        # 기본: 질문 기반 의미 검색 (use_cache=False 로 매 요청마다 질문에 맞는 결과)
        chunks = collect_chunks_by_question(
            db, question, top_k=20, reasoning_steps=reasoning_steps, use_cache=False
        )
        # 보조: 프로젝트/라벨로 추가 수집 후 병합(중복 제거)
        if project_ids or label_names or (request.filters and (request.filters.category_label_ids or request.filters.keyword_group_ids or request.filters.keyword_ids)):
            secondary = collect_knowledge_chunks(
                db, project_ids, label_names, filter_label_ids, request, reasoning_steps
            )
            seen = {c.id for c in chunks}
            for c in secondary:
                if c.id not in seen:
                    seen.add(c.id)
                    chunks.append(c)
            if secondary:
                reasoning_steps.append("보조 필터(프로젝트/라벨) 청크 병합 완료")
        # 질문에 대한 관련 지식이 없을 때: 전체 폴백 없이 0건 유지
        if not chunks:
            reasoning_steps.append("질문과 관련된 지식이 수집되지 않았습니다. 질문에 맞는 안내를 생성합니다.")
    if not chunks and not question and not document_ids:
        # 질문 없을 때만: 프로젝트/라벨 기반 수집(또는 전체 폴백)
        chunks = collect_knowledge_chunks(
            db, project_ids, label_names, filter_label_ids, request, reasoning_steps
        )

    # 3. 관계 추적
    all_chunks = expand_chunks_with_relations(db, chunks, reasoning_steps)

    # 4. 질문이 있을 때만 의미 검색으로 추가 보강
    if question and len(chunks) > 0:
        all_chunks = add_semantic_search_results(db, all_chunks, question, reasoning_steps, top_k=5)
    else:
        all_chunks = add_semantic_search_results(db, all_chunks, request.question, reasoning_steps)

    # 5. 컨텍스트 구성 (project_id, labels 포함)
    context_chunks = build_context_chunks(db, all_chunks, reasoning_steps)

    # 6. 관계 정보 수집
    relations = collect_relations(db, chunks)

    # 7. Reasoning 실행 (LLM 우선, 실패 시 템플릿 폴백)
    reasoning_steps.append("Reasoning 실행 중...")
    dynamic_svc = get_dynamic_reasoning_service()
    answer = dynamic_svc.generate_reasoning(
        request.question, context_chunks, request.mode, max_tokens=500, model=request.model
    )
    if answer is None:
        answer = generate_reasoning_answer(
            request.mode, request.question, all_chunks, context_chunks, relations
        )
    reasoning_steps.append("Reasoning 완료")

    # 8. 추천 생성 (Phase 9-3-1)
    recommendations = None
    try:
        rec_svc = get_recommendation_service(db)
        context_chunk_ids = [c.get("id") for c in context_chunks if c.get("id")]
        related_chunks = rec_svc.recommend_related_chunks(context_chunk_ids, limit=5) if context_chunk_ids else []
        combined_content = " ".join([(c.get("content") or "")[:300] for c in context_chunks])
        suggested_labels = rec_svc.recommend_labels(combined_content, limit=5) if combined_content.strip() else []
        sample_questions = rec_svc.generate_sample_questions(limit=3, model=request.model)
        explore_more = rec_svc.suggest_exploration(context_chunk_ids=context_chunk_ids, limit=5)
        recommendations = {
            "related_chunks": related_chunks,
            "suggested_labels": suggested_labels,
            "sample_questions": sample_questions,
            "explore_more": explore_more,
        }
    except Exception as e:
        import logging
        logging.getLogger(__name__).debug("recommendations build failed: %s", e)

    return ReasonResponse(
        answer=answer,
        context_chunks=context_chunks,
        relations=relations,
        reasoning_steps=reasoning_steps,
        recommendations=recommendations,
    )
