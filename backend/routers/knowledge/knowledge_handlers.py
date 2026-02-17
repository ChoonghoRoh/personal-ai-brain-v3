"""Knowledge 엔드포인트 핸들러 — 청크 CRUD·라벨 연결·구조 추천 (knowledge.py에서 분리)

문서/프로젝트/키워드 관련 핸들러는 document_handlers.py 참조.
"""
from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload, selectinload
from typing import List, Optional

from backend.models.models import (
    KnowledgeChunk, Label, KnowledgeLabel, Document, Project, KnowledgeRelation,
)
from backend.config import AUTO_STRUCTURE_MATCHING_ENABLED
from backend.services.knowledge.structure_matcher import get_structure_matcher


# ---------------------------------------------------------------------------
# 청크 목록 조회
# ---------------------------------------------------------------------------

async def handle_list_chunks(
    label_id: Optional[int],
    document_id: Optional[int],
    project_id: Optional[int],
    limit: int,
    offset: int,
    sort_by: str,
    sort_order: str,
    db: Session,
):
    """지식 청크 목록 조회 (페이징 지원)"""
    base_query = db.query(KnowledgeChunk)

    if label_id:
        base_query = base_query.join(KnowledgeLabel).filter(KnowledgeLabel.label_id == label_id)

    if document_id:
        base_query = base_query.filter(KnowledgeChunk.document_id == document_id)

    if project_id:
        base_query = base_query.join(Document).filter(Document.project_id == project_id)

    valid_sort_fields = ["created_at", "chunk_index", "title"]
    if sort_by not in valid_sort_fields:
        sort_by = "created_at"

    sort_field = getattr(KnowledgeChunk, sort_by, KnowledgeChunk.created_at)
    if sort_order.lower() == "asc":
        base_query = base_query.order_by(sort_field.asc())
    else:
        base_query = base_query.order_by(sort_field.desc())

    total_count = base_query.count()

    chunks = base_query.options(
        joinedload(KnowledgeChunk.document).joinedload(Document.project),
        selectinload(KnowledgeChunk.labels).joinedload(KnowledgeLabel.label),
    ).order_by(KnowledgeChunk.id.desc()).offset(offset).limit(limit).all()

    result = []
    for chunk in chunks:
        doc = chunk.document
        project = doc.project if doc else None

        label_list = [
            {"id": kl.label.id, "name": kl.label.name, "label_type": kl.label.label_type}
            for kl in chunk.labels
        ]

        outgoing_count = len([r for r in chunk.outgoing_relations if r.confirmed == "true"]) if hasattr(chunk, 'outgoing_relations') else 0
        incoming_count = len([r for r in chunk.incoming_relations if r.confirmed == "true"]) if hasattr(chunk, 'incoming_relations') else 0

        if outgoing_count == 0 or incoming_count == 0:
            if outgoing_count == 0:
                outgoing_count = db.query(KnowledgeRelation).filter(
                    KnowledgeRelation.source_chunk_id == chunk.id,
                    KnowledgeRelation.confirmed == "true",
                ).count()
            if incoming_count == 0:
                incoming_count = db.query(KnowledgeRelation).filter(
                    KnowledgeRelation.target_chunk_id == chunk.id,
                    KnowledgeRelation.confirmed == "true",
                ).count()

        result.append({
            "id": chunk.id,
            "content": chunk.content,
            "chunk_index": chunk.chunk_index,
            "document_id": chunk.document_id,
            "document_name": doc.file_name if doc else None,
            "project_name": project.name if project else None,
            "title": chunk.title,
            "title_source": chunk.title_source,
            "labels": label_list,
            "outgoing_relations_count": outgoing_count,
            "incoming_relations_count": incoming_count,
        })

    total_pages = (total_count + limit - 1) // limit if limit > 0 else 0
    current_page = (offset // limit) + 1 if limit > 0 else 1

    return {
        "items": result,
        "total_count": total_count,
        "limit": limit,
        "offset": offset,
        "total_pages": total_pages,
        "current_page": current_page,
    }


# ---------------------------------------------------------------------------
# 청크 상세 조회
# ---------------------------------------------------------------------------

async def handle_get_chunk(chunk_id: int, db: Session):
    """지식 청크 상세 조회"""
    chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="청크를 찾을 수 없습니다")

    doc = db.query(Document).filter(Document.id == chunk.document_id).first()
    project = None
    if doc and doc.project_id:
        project = db.query(Project).filter(Project.id == doc.project_id).first()

    labels = db.query(Label).join(KnowledgeLabel).filter(
        KnowledgeLabel.chunk_id == chunk.id
    ).all()
    label_list = [{"id": label.id, "name": label.name, "label_type": label.label_type} for label in labels]

    outgoing_rels = db.query(KnowledgeRelation).filter(
        KnowledgeRelation.source_chunk_id == chunk.id
    ).all()
    outgoing_list = []
    for rel in outgoing_rels:
        target = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == rel.target_chunk_id).first()
        if target:
            outgoing_list.append({
                "id": rel.id,
                "target_chunk_id": rel.target_chunk_id,
                "target_content": target.content[:100] + "..." if len(target.content) > 100 else target.content,
                "relation_type": rel.relation_type,
                "confidence": rel.confidence,
                "description": rel.description,
            })

    incoming_rels = db.query(KnowledgeRelation).filter(
        KnowledgeRelation.target_chunk_id == chunk.id
    ).all()
    incoming_list = []
    for rel in incoming_rels:
        source = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == rel.source_chunk_id).first()
        if source:
            incoming_list.append({
                "id": rel.id,
                "source_chunk_id": rel.source_chunk_id,
                "source_content": source.content[:100] + "..." if len(source.content) > 100 else source.content,
                "relation_type": rel.relation_type,
                "confidence": rel.confidence,
                "description": rel.description,
            })

    return {
        "id": chunk.id,
        "content": chunk.content,
        "chunk_index": chunk.chunk_index,
        "document_id": chunk.document_id,
        "document_name": doc.file_name if doc else None,
        "project_name": project.name if project else None,
        "title": chunk.title,
        "title_source": chunk.title_source,
        "labels": label_list,
        "outgoing_relations": outgoing_list,
        "incoming_relations": incoming_list,
    }


# ---------------------------------------------------------------------------
# 청크 생성
# ---------------------------------------------------------------------------

async def handle_create_chunk(request, include_suggestions: bool, db: Session):
    """단일 청크를 생성하고 structure_suggestions를 반환."""
    document = db.query(Document).filter(Document.id == request.document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다")

    chunk = KnowledgeChunk(
        document_id=request.document_id,
        content=request.content.strip(),
        chunk_index=request.chunk_index,
        title=request.title,
        title_source=request.title_source,
        status="draft",
        source="human_created",
        qdrant_point_id=None,
    )
    db.add(chunk)
    db.commit()
    db.refresh(chunk)

    structure_suggestions = {}
    if include_suggestions and AUTO_STRUCTURE_MATCHING_ENABLED:
        try:
            matcher = get_structure_matcher(db)
            structure_suggestions = matcher.match_on_chunk_create(chunk)
        except Exception:
            structure_suggestions = {
                "suggested_labels": [],
                "similar_chunks": [],
                "suggested_category": None,
            }

    return {
        "chunk": {
            "id": chunk.id,
            "document_id": chunk.document_id,
            "content": chunk.content,
            "chunk_index": chunk.chunk_index,
            "title": chunk.title,
            "title_source": chunk.title_source,
            "status": chunk.status,
        },
        "structure_suggestions": structure_suggestions,
    }


# ---------------------------------------------------------------------------
# 청크-라벨 연결
# ---------------------------------------------------------------------------

async def handle_add_labels_to_chunk(chunk_id: int, request, db: Session):
    """청크에 다중 라벨 추가 (Phase 7.7)"""
    chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="청크를 찾을 수 없습니다")

    added_count = 0
    skipped_count = 0

    for label_id in request.label_ids:
        label = db.query(Label).filter(Label.id == label_id).first()
        if not label:
            skipped_count += 1
            continue

        existing = db.query(KnowledgeLabel).filter(
            KnowledgeLabel.chunk_id == chunk_id,
            KnowledgeLabel.label_id == label_id,
        ).first()

        if existing:
            existing.status = request.status
            existing.source = request.source
            skipped_count += 1
        else:
            knowledge_label = KnowledgeLabel(
                chunk_id=chunk_id,
                label_id=label_id,
                status=request.status,
                source=request.source,
                confidence=1.0,
            )
            db.add(knowledge_label)
            added_count += 1

    db.commit()

    return {
        "message": f"{added_count}개의 라벨이 추가되었습니다",
        "added_count": added_count,
        "skipped_count": skipped_count,
    }


async def handle_apply_suggested_labels(chunk_id: int, request, auto_confirm: bool, db: Session):
    """추천 라벨 일괄 적용 (Phase 9-3-2)."""
    from backend.services.knowledge.auto_labeler import get_auto_labeler
    labeler = get_auto_labeler(db)
    result = labeler.apply_suggested_labels(
        chunk_id=chunk_id,
        label_ids=request.label_ids,
        auto_confirm=auto_confirm,
    )
    return result


async def handle_remove_labels_from_chunk(chunk_id: int, request, db: Session):
    """청크에서 다중 라벨 제거 (Phase 7.7)"""
    chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="청크를 찾을 수 없습니다")

    removed_count = 0

    for label_id in request.label_ids:
        knowledge_label = db.query(KnowledgeLabel).filter(
            KnowledgeLabel.chunk_id == chunk_id,
            KnowledgeLabel.label_id == label_id,
        ).first()

        if knowledge_label:
            db.delete(knowledge_label)
            removed_count += 1

    db.commit()

    return {
        "message": f"{removed_count}개의 라벨이 제거되었습니다",
        "removed_count": removed_count,
    }


async def handle_get_chunk_labels_detailed(chunk_id: int, db: Session):
    """청크의 라벨 목록 조회 (상세 정보 포함, Phase 7.7)"""
    chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="청크를 찾을 수 없습니다")

    knowledge_labels = db.query(KnowledgeLabel).filter(
        KnowledgeLabel.chunk_id == chunk_id
    ).all()

    result = []
    for kl in knowledge_labels:
        label = db.query(Label).filter(Label.id == kl.label_id).first()
        if label:
            result.append({
                "id": label.id,
                "name": label.name,
                "label_type": label.label_type,
                "parent_label_id": label.parent_label_id,
                "color": label.color,
                "status": kl.status,
                "source": kl.source,
                "confidence": kl.confidence,
            })

    return {
        "chunk_id": chunk_id,
        "labels": result,
    }


# ---------------------------------------------------------------------------
# 구조 추천
# ---------------------------------------------------------------------------

async def handle_get_chunk_structure_suggestions(chunk_id: int, db: Session):
    """청크에 대한 라벨/유사 청크/카테고리 추천 (Phase 9-3-2)."""
    if not AUTO_STRUCTURE_MATCHING_ENABLED:
        return {"suggested_labels": [], "similar_chunks": [], "suggested_category": None}
    chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="청크를 찾을 수 없습니다")
    matcher = get_structure_matcher(db)
    result = matcher.match_on_chunk_create(chunk)
    return result


async def handle_get_document_suggestions(document_id: int, db: Session):
    """문서에 대한 카테고리/유사 문서 추천 (Phase 9-3-2)."""
    if not AUTO_STRUCTURE_MATCHING_ENABLED:
        return {"category": None, "similar_documents": []}
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다")
    matcher = get_structure_matcher(db)
    cat = matcher._infer_category_from_path(document.file_path or "")
    if not cat and document.id:
        from backend.services.knowledge.auto_labeler import get_auto_labeler
        labeler = get_auto_labeler(db)
        cat = labeler.suggest_category(document)
    similar = matcher.find_similar_documents(document)
    return {
        "category": cat,
        "similar_documents": similar,
    }


