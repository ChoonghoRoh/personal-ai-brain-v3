"""Reasoning API 라우터"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from pydantic import BaseModel

from backend.models.database import get_db
from backend.models.models import Project, Document, KnowledgeChunk, Label, KnowledgeLabel, KnowledgeRelation
from backend.services.search.search_service import get_search_service
from backend.services.reasoning.dynamic_reasoning_service import get_dynamic_reasoning_service
from backend.services.reasoning.recommendation_service import get_recommendation_service

router = APIRouter(prefix="/api/reason", tags=["reason"])


class ReasonFilters(BaseModel):  # Phase 7.7
    project_ids: Optional[List[int]] = None
    category_label_ids: Optional[List[int]] = None
    keyword_group_ids: Optional[List[int]] = None
    keyword_ids: Optional[List[int]] = None


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
    recommendations: Optional[Dict] = None  # Phase 9-3-1: related_chunks, suggested_labels, sample_questions, explore_more


def collect_knowledge_from_projects(db: Session, project_ids: List[int]) -> List[KnowledgeChunk]:
    """프로젝트에서 지식 청크 수집 (승인된 청크만)"""
    chunks = []
    for project_id in project_ids:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            continue
        
        documents = db.query(Document).filter(Document.project_id == project_id).all()
        for doc in documents:
            doc_chunks = db.query(KnowledgeChunk).filter(
                KnowledgeChunk.document_id == doc.id,
                KnowledgeChunk.status == "approved"  # 승인된 청크만
            ).all()
            chunks.extend(doc_chunks)
    
    return chunks


def collect_knowledge_from_labels(db: Session, label_names: List[str]) -> List[KnowledgeChunk]:
    """라벨에서 지식 수집 (승인된 청크만)"""
    chunks = []
    labels = db.query(Label).filter(Label.name.in_(label_names)).all()
    for label in labels:
        knowledge_labels = db.query(KnowledgeLabel).filter(KnowledgeLabel.label_id == label.id).all()
        for kl in knowledge_labels:
            chunk = db.query(KnowledgeChunk).filter(
                KnowledgeChunk.id == kl.chunk_id,
                KnowledgeChunk.status == "approved"  # 승인된 청크만
            ).first()
            if chunk:
                chunks.append(chunk)
    
    return chunks


def collect_knowledge_from_label_ids(db: Session, label_ids: List[int]) -> List[KnowledgeChunk]:
    """라벨 ID로 지식 수집 (승인된 청크만, Phase 7.7)"""
    chunks = []
    knowledge_labels = db.query(KnowledgeLabel).filter(
        KnowledgeLabel.label_id.in_(label_ids),
        KnowledgeLabel.status == "confirmed"  # 확정된 라벨만
    ).all()
    
    chunk_ids = {kl.chunk_id for kl in knowledge_labels}
    if chunk_ids:
        chunks = db.query(KnowledgeChunk).filter(
            KnowledgeChunk.id.in_(chunk_ids),
            KnowledgeChunk.status == "approved"  # 승인된 청크만
        ).all()
    
    return chunks


def collect_knowledge_from_category(db: Session, category_label_ids: List[int]) -> List[KnowledgeChunk]:
    """카테고리 라벨로 지식 수집 (승인된 청크만, Phase 7.7)"""
    chunks = []
    # 카테고리 라벨이 연결된 문서 찾기
    documents = db.query(Document).filter(
        Document.category_label_id.in_(category_label_ids)
    ).all()
    
    doc_ids = [doc.id for doc in documents]
    if doc_ids:
        chunks = db.query(KnowledgeChunk).filter(
            KnowledgeChunk.document_id.in_(doc_ids),
            KnowledgeChunk.status == "approved"  # 승인된 청크만
        ).all()
    
    return chunks


def trace_relations(db: Session, chunks: List[KnowledgeChunk], depth: int = 2) -> List[KnowledgeChunk]:
    """관계를 따라 지식 청크 추적 (승인된 청크만, 최적화된 버전)"""
    all_chunks = {chunk.id: chunk for chunk in chunks}
    current_chunk_ids = [chunk.id for chunk in chunks]
    
    for _ in range(depth):
        if not current_chunk_ids:
            break
        
        # 배치로 관계 조회 (N+1 쿼리 문제 해결)
        relations = db.query(KnowledgeRelation).filter(
            (
                (KnowledgeRelation.source_chunk_id.in_(current_chunk_ids)) |
                (KnowledgeRelation.target_chunk_id.in_(current_chunk_ids))
            ),
            KnowledgeRelation.confirmed == "true"
        ).all()
        
        # 관련 청크 ID 수집
        related_chunk_ids = set()
        for rel in relations:
            if rel.source_chunk_id in current_chunk_ids:
                related_chunk_ids.add(rel.target_chunk_id)
            if rel.target_chunk_id in current_chunk_ids:
                related_chunk_ids.add(rel.source_chunk_id)
        
        # 이미 포함된 청크 제외
        related_chunk_ids = related_chunk_ids - set(all_chunks.keys())
        
        if not related_chunk_ids:
            break
        
        # 배치로 청크 조회 (승인된 청크만)
        next_chunks = db.query(KnowledgeChunk).filter(
            KnowledgeChunk.id.in_(related_chunk_ids),
            KnowledgeChunk.status == "approved"
        ).all()
        
        # 결과에 추가
        for chunk in next_chunks:
            all_chunks[chunk.id] = chunk
        
        current_chunk_ids = [chunk.id for chunk in next_chunks]
    
    return list(all_chunks.values())


def parse_reasoning_inputs(request: ReasonRequest) -> tuple:
    """입력 파싱"""
    project_ids = request.inputs.get("projects", [])
    label_names = request.inputs.get("labels", [])
    
    # Phase 7.7: 필터 파싱
    filter_label_ids = []
    if request.filters:
        if request.filters.category_label_ids:
            filter_label_ids.extend(request.filters.category_label_ids)
        if request.filters.keyword_group_ids:
            filter_label_ids.extend(request.filters.keyword_group_ids)
        if request.filters.keyword_ids:
            filter_label_ids.extend(request.filters.keyword_ids)
        if request.filters.project_ids:
            project_ids = list(set(project_ids + request.filters.project_ids))
    
    return project_ids, label_names, filter_label_ids


def collect_knowledge_chunks(
    db: Session, 
    project_ids: List[int], 
    label_names: List[str], 
    filter_label_ids: List[int],
    request: ReasonRequest,
    reasoning_steps: List[str]
) -> List[KnowledgeChunk]:
    """PostgreSQL에서 지식 청크 수집"""
    reasoning_steps.append("PostgreSQL에서 지식 수집 중...")
    chunks = []
    
    # Phase 7.7: 카테고리 필터 적용
    if request.filters and request.filters.category_label_ids:
        category_chunks = collect_knowledge_from_category(db, request.filters.category_label_ids)
        chunks.extend(category_chunks)
        reasoning_steps.append(f"카테고리에서 {len(category_chunks)}개 청크 수집")
    
    if project_ids:
        project_chunks = collect_knowledge_from_projects(db, project_ids)
        chunks.extend(project_chunks)
        reasoning_steps.append(f"프로젝트에서 {len(project_chunks)}개 청크 수집")
    
    if label_names:
        label_chunks = collect_knowledge_from_labels(db, label_names)
        chunks.extend(label_chunks)
        reasoning_steps.append(f"라벨에서 {len(label_chunks)}개 청크 수집")
    
    # Phase 7.7: 키워드 그룹/키워드 필터 적용
    if filter_label_ids:
        filter_chunks = collect_knowledge_from_label_ids(db, filter_label_ids)
        chunks.extend(filter_chunks)
        reasoning_steps.append(f"키워드/그룹 필터에서 {len(filter_chunks)}개 청크 수집")
    
    # 중복 제거
    chunks = list({chunk.id: chunk for chunk in chunks}.values())
    approved_chunks = [chunk for chunk in chunks if chunk.status == "approved"]

    # 조건에 맞는 승인 청크가 없을 때: DB에 승인 청크가 있으면 전체로 폴백 (기능 테스트·일반 사용 지원)
    no_filter = (
        not project_ids
        and not label_names
        and not filter_label_ids
        and not (request.filters and request.filters.category_label_ids)
    )
    if not approved_chunks:
        fallback = (
            db.query(KnowledgeChunk)
            .filter(KnowledgeChunk.status == "approved")
            .order_by(KnowledgeChunk.id.desc())
            .limit(100)
            .all()
        )
        if fallback:
            if no_filter:
                reasoning_steps.append(f"필터 없음 → 승인된 전체 청크 {len(fallback)}개 사용")
            else:
                reasoning_steps.append("선택한 프로젝트/라벨에 해당하는 승인 청크가 없어, 승인된 전체 청크로 실행합니다.")
            return fallback
        raise HTTPException(
            status_code=400,
            detail="승인된 지식이 없습니다. 관리자 승인이 필요한 청크가 있습니다.",
        )

    return approved_chunks


def expand_chunks_with_relations(
    db: Session,
    chunks: List[KnowledgeChunk],
    reasoning_steps: List[str]
) -> List[KnowledgeChunk]:
    """관계를 통해 청크 확장"""
    reasoning_steps.append("관계 추적 중...")
    related_chunks = trace_relations(db, chunks, depth=2)
    reasoning_steps.append(f"관계를 통해 {len(related_chunks)}개 추가 청크 발견")
    
    all_chunks = chunks + related_chunks
    all_chunks = list({chunk.id: chunk for chunk in all_chunks}.values())
    return all_chunks


def collect_chunks_by_question(
    db: Session,
    question: str,
    top_k: int = 20,
    reasoning_steps: Optional[List[str]] = None,
    use_cache: bool = False,
) -> List[KnowledgeChunk]:
    """질문 기반 의미 검색으로 승인 청크 수집 (주요 조회). use_cache=False 권장으로 매 요청마다 질문에 맞는 결과 반영."""
    if not question or not question.strip():
        return []
    steps = reasoning_steps or []
    steps.append("질문 기반 의미 검색 중...")
    search_service = get_search_service()
    search_results = search_service.search_simple(
        question.strip(), top_k=top_k, use_cache=use_cache
    )
    chunks = []
    seen = set()
    for result in search_results:
        qdrant_id = result.get("document_id")
        chunk = db.query(KnowledgeChunk).filter(
            KnowledgeChunk.qdrant_point_id == str(qdrant_id),
            KnowledgeChunk.status == "approved",
        ).first()
        if chunk and chunk.id not in seen:
            seen.add(chunk.id)
            chunks.append(chunk)
    steps.append(f"의미 검색으로 {len(chunks)}개 청크 수집")
    return chunks


def add_semantic_search_results(
    db: Session,
    all_chunks: List[KnowledgeChunk],
    question: Optional[str],
    reasoning_steps: List[str],
    top_k: int = 5,
) -> List[KnowledgeChunk]:
    """Qdrant 의미 검색 결과 추가 (기존 청크에 병합)."""
    if not question:
        return all_chunks
    reasoning_steps.append("Qdrant에서 의미 검색 중...")
    search_service = get_search_service()
    search_results = search_service.search_simple(question.strip(), top_k=top_k)
    semantic_chunks = []
    seen = {c.id for c in all_chunks}
    for result in search_results:
        qdrant_id = result.get("document_id")
        chunk = db.query(KnowledgeChunk).filter(
            KnowledgeChunk.qdrant_point_id == str(qdrant_id),
            KnowledgeChunk.status == "approved",
        ).first()
        if chunk and chunk.id not in seen:
            seen.add(chunk.id)
            all_chunks.append(chunk)
            semantic_chunks.append(chunk)
    reasoning_steps.append(f"의미 검색으로 {len(semantic_chunks)}개 추가 청크 발견")
    return all_chunks


def build_context_chunks(
    db: Session,
    all_chunks: List[KnowledgeChunk],
    reasoning_steps: List[str]
) -> List[Dict]:
    """컨텍스트 청크 구성 (project_id, labels 포함)"""
    reasoning_steps.append("컨텍스트 구성 중...")
    
    # 최대 20개로 제한
    chunks_to_process = all_chunks[:20]
    chunk_ids = [c.id for c in chunks_to_process]
    
    # 배치로 문서 및 프로젝트 조회 (N+1 쿼리 문제 해결)
    document_ids = list(set([chunk.document_id for chunk in chunks_to_process]))
    documents = {doc.id: doc for doc in db.query(Document).filter(Document.id.in_(document_ids)).all()}
    
    project_ids = list(set([doc.project_id for doc in documents.values() if doc.project_id]))
    projects = {proj.id: proj for proj in db.query(Project).filter(Project.id.in_(project_ids)).all()} if project_ids else {}
    
    # 청크별 라벨 이름 배치 조회 (확정된 KnowledgeLabel만)
    chunk_labels: Dict[int, List[str]] = {cid: [] for cid in chunk_ids}
    if chunk_ids:
        knowledge_labels = (
            db.query(KnowledgeLabel.chunk_id, Label.name)
            .join(Label, KnowledgeLabel.label_id == Label.id)
            .filter(
                KnowledgeLabel.chunk_id.in_(chunk_ids),
                KnowledgeLabel.status == "confirmed",
            )
            .all()
        )
        for cid, name in knowledge_labels:
            if name and cid in chunk_labels:
                chunk_labels[cid].append(name)
    
    # 컨텍스트 구성 (document, project, project_id, labels 표기)
    context_chunks = []
    for chunk in chunks_to_process:
        doc = documents.get(chunk.document_id)
        project = projects.get(doc.project_id) if doc and doc.project_id else None
        context_chunks.append({
            "id": chunk.id,
            "content": chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content,
            "document": doc.file_name if doc else None,
            "project": project.name if project else None,
            "project_id": doc.project_id if doc else None,
            "labels": chunk_labels.get(chunk.id) or [],
        })
    
    return context_chunks


def collect_relations(
    db: Session,
    chunks: List[KnowledgeChunk]
) -> List[Dict]:
    """관계 정보 수집 (최적화된 버전)"""
    if not chunks:
        return []
    
    # 초기 청크들의 관계만 (최대 10개)
    chunk_ids = [chunk.id for chunk in chunks[:10]]
    
    # 배치로 관계 조회 (N+1 쿼리 문제 해결)
    all_relations = db.query(KnowledgeRelation).filter(
        KnowledgeRelation.source_chunk_id.in_(chunk_ids)
    ).all()
    
    # 타겟 청크 ID 수집
    target_chunk_ids = list(set([rel.target_chunk_id for rel in all_relations]))
    
    # 배치로 타겟 청크 조회
    target_chunks = {
        chunk.id: chunk 
        for chunk in db.query(KnowledgeChunk).filter(KnowledgeChunk.id.in_(target_chunk_ids)).all()
    }
    
    # 청크 딕셔너리 생성 (빠른 조회)
    chunk_dict = {chunk.id: chunk for chunk in chunks[:10]}
    
    # 관계 정보 구성
    relations = []
    for rel in all_relations:
        source_chunk = chunk_dict.get(rel.source_chunk_id)
        target_chunk = target_chunks.get(rel.target_chunk_id)
        
        if source_chunk and target_chunk:
            relations.append({
                "type": rel.relation_type,
                "source": source_chunk.content[:50],
                "target": target_chunk.content[:50],
                "description": rel.description
            })
    
    return relations


def generate_reasoning_answer(
    mode: str,
    question: Optional[str],
    all_chunks: List[KnowledgeChunk],
    context_chunks: List[Dict],
    relations: List[Dict]
) -> str:
    """Reasoning 답변 생성"""
    if mode == "design_explain":
        answer = f"📐 설계/배경 설명\n\n"
        answer += f"수집된 {len(all_chunks)}개 지식 조각을 기반으로 설계 배경과 맥락을 설명합니다:\n\n"
        answer += f"• {len(context_chunks)}개 주요 컨텍스트 청크\n"
        answer += f"• {len(relations)}개 발견된 관계\n\n"
        if question:
            answer += f"질문: '{question}'\n\n"
        answer += "이 지식들을 종합하여 설계 의도와 배경을 명확히 설명할 수 있습니다."
    elif mode == "risk_review":
        answer = f"⚠️ 리스크 분석\n\n"
        answer += f"{len(all_chunks)}개 관련 지식을 분석하여 잠재적 리스크와 문제점을 식별합니다:\n\n"
        answer += f"• {len(context_chunks)}개 분석 대상 청크\n"
        answer += f"• {len(relations)}개 관계를 통한 영향도 추적\n\n"
        if question:
            answer += f"분석 대상: '{question}'\n\n"
        answer += "관계 그래프를 통해 리스크 전파 경로와 영향을 파악할 수 있습니다."
    elif mode == "next_steps":
        answer = f"🚀 다음 단계 제안\n\n"
        answer += f"{len(all_chunks)}개 관련 지식을 기반으로 다음 단계를 제안합니다:\n\n"
        answer += f"• {len(context_chunks)}개 참고 지식\n"
        if relations:
            answer += f"• {len(relations)}개 관계를 고려한 연속성\n\n"
        else:
            answer += "\n"
        if question:
            answer += f"제안 요청: '{question}'\n\n"
        answer += "현재 상태와 관계를 분석하여 논리적인 다음 단계를 제안합니다."
    else:  # history_trace
        answer = f"📜 히스토리/맥락 추적\n\n"
        answer += f"{len(all_chunks)}개 지식을 시간적/논리적 순서로 추적합니다:\n\n"
        answer += f"• {len(context_chunks)}개 추적 대상 청크\n"
        answer += f"• {len(relations)}개 관계를 통한 맥락 연결\n\n"
        if question:
            answer += f"추적 대상: '{question}'\n\n"
        answer += "관계 그래프를 따라 지식의 진화와 맥락을 추적할 수 있습니다."
    
    return answer


@router.post("", response_model=ReasonResponse)
async def reason(request: ReasonRequest, db: Session = Depends(get_db)):
    """Reasoning 실행. 질문이 있으면 질문 기반 의미 검색 우선, 프로젝트/라벨은 보조 조회."""
    reasoning_steps = []
    
    # 1. 입력 파싱
    reasoning_steps.append("입력 파싱 중...")
    project_ids, label_names, filter_label_ids = parse_reasoning_inputs(request)
    question = (request.question or "").strip()
    
    # 2. 지식 수집: 질문 우선 → 보조로 프로젝트/라벨 병합 (캐시 미사용으로 질문별 결과 반영)
    chunks = []
    if question:
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
        # 질문에 대한 관련 지식이 없을 때: 전체 폴백 없이 0건 유지 → LLM이 질문에 맞게 "관련 지식 없음" 안내
        if not chunks:
            reasoning_steps.append("질문과 관련된 지식이 수집되지 않았습니다. 질문에 맞는 안내를 생성합니다.")
    if not chunks and not question:
        # 질문 없을 때만: 프로젝트/라벨 기반 수집(또는 전체 폴백)
        chunks = collect_knowledge_chunks(
            db, project_ids, label_names, filter_label_ids, request, reasoning_steps
        )
    
    # 3. 관계 추적
    all_chunks = expand_chunks_with_relations(db, chunks, reasoning_steps)
    
    # 4. 질문이 있을 때만 의미 검색으로 추가 보강(이미 질문 기반 수집했으면 소량만 추가)
    if question and len(chunks) > 0:
        # 이미 질문으로 수집했으므로 추가 검색은 최소화(선택적)
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

