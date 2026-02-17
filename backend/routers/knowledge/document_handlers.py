"""문서/프로젝트/키워드 추출 핸들러 (knowledge_handlers.py에서 분리)

문서 카테고리 설정, 문서 CRUD, 프로젝트 목록, 키워드 추출 등의 비즈니스 로직.
"""
from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from backend.models.models import (
    KnowledgeChunk, Label, KnowledgeLabel, Document, Project,
)
from backend.config import AUTO_STRUCTURE_MATCHING_ENABLED
from backend.services.knowledge.structure_matcher import get_structure_matcher


# ---------------------------------------------------------------------------
# 문서 카테고리 설정
# ---------------------------------------------------------------------------

async def handle_set_document_category(document_id: int, request, db: Session):
    """문서 카테고리 설정 (Phase 7.7)"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다")

    label = db.query(Label).filter(Label.id == request.label_id).first()
    if not label:
        raise HTTPException(status_code=404, detail="라벨을 찾을 수 없습니다")

    if label.label_type not in ["category", "project", "domain"]:
        raise HTTPException(
            status_code=400,
            detail=f"카테고리 라벨은 'category', 'project', 'domain' 타입만 허용됩니다. (현재: {label.label_type})",
        )

    document.category_label_id = request.label_id
    db.commit()
    db.refresh(document)

    return {
        "message": "문서 카테고리가 설정되었습니다",
        "document_id": document_id,
        "category_label_id": request.label_id,
        "category_label_name": label.name,
    }


# ---------------------------------------------------------------------------
# 문서 CRUD
# ---------------------------------------------------------------------------

async def handle_create_document(request, include_suggestions: bool, db: Session):
    """문서를 생성하고 suggested_category/similar_documents를 반환."""
    existing = db.query(Document).filter(Document.file_path == request.file_path).first()
    if existing:
        raise HTTPException(status_code=400, detail="동일한 file_path를 가진 문서가 이미 존재합니다")

    if request.project_id:
        proj = db.query(Project).filter(Project.id == request.project_id).first()
        if not proj:
            raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다")

    document = Document(
        file_path=request.file_path,
        file_name=request.file_name,
        file_type=request.file_type,
        size=request.size,
        project_id=request.project_id,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    suggested_category = None
    similar_documents = []
    if include_suggestions and AUTO_STRUCTURE_MATCHING_ENABLED:
        try:
            matcher = get_structure_matcher(db)
            suggested_category = matcher._infer_category_from_path(document.file_path or "")
            if not suggested_category:
                from backend.services.knowledge.auto_labeler import get_auto_labeler
                labeler = get_auto_labeler(db)
                suggested_category = labeler.suggest_category(document)
            similar_documents = matcher.find_similar_documents(document)
        except Exception:
            pass

    return {
        "document": {
            "id": document.id,
            "file_path": document.file_path,
            "file_name": document.file_name,
            "file_type": document.file_type,
            "size": document.size,
            "project_id": document.project_id,
        },
        "suggested_category": suggested_category,
        "similar_documents": similar_documents,
    }


async def handle_list_documents_with_category(
    category_label_id: Optional[int],
    label_type: Optional[str],
    db: Session,
):
    """카테고리별 문서 목록 조회 (Phase 7.7)"""
    query = db.query(Document)

    if category_label_id:
        query = query.filter(Document.category_label_id == category_label_id)

    documents = query.all()

    result = []
    for doc in documents:
        category_label = None
        if doc.category_label_id:
            category_label = db.query(Label).filter(Label.id == doc.category_label_id).first()

        if label_type and category_label and category_label.label_type != label_type:
            continue

        project = None
        if doc.project_id:
            project = db.query(Project).filter(Project.id == doc.project_id).first()

        result.append({
            "id": doc.id,
            "file_path": doc.file_path,
            "file_name": doc.file_name,
            "file_type": doc.file_type,
            "project_id": doc.project_id,
            "project_name": project.name if project else None,
            "category_label_id": doc.category_label_id,
            "category_label_name": category_label.name if category_label else None,
            "category_label_type": category_label.label_type if category_label else None,
            "created_at": doc.created_at.isoformat() if doc.created_at else None,
        })

    return result


async def handle_get_document(document_id: int, db: Session):
    """문서 상세 조회"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다")

    project = None
    if document.project_id:
        project = db.query(Project).filter(Project.id == document.project_id).first()

    category_label = None
    if document.category_label_id:
        category_label = db.query(Label).filter(Label.id == document.category_label_id).first()

    chunks_count = db.query(KnowledgeChunk).filter(KnowledgeChunk.document_id == document_id).count()

    return {
        "id": document.id,
        "file_path": document.file_path,
        "file_name": document.file_name,
        "file_type": document.file_type,
        "size": document.size,
        "project_id": document.project_id,
        "project_name": project.name if project else None,
        "category_label_id": document.category_label_id,
        "category_label_name": category_label.name if category_label else None,
        "category_label_type": category_label.label_type if category_label else None,
        "qdrant_collection": document.qdrant_collection,
        "chunks_count": chunks_count,
        "created_at": document.created_at.isoformat() if document.created_at else None,
        "updated_at": document.updated_at.isoformat() if document.updated_at else None,
    }


async def handle_list_projects(db: Session):
    """프로젝트 목록 조회"""
    projects = db.query(Project).all()

    result = []
    for project in projects:
        documents_count = db.query(Document).filter(Document.project_id == project.id).count()

        result.append({
            "id": project.id,
            "name": project.name,
            "path": project.path,
            "description": project.description,
            "documents_count": documents_count,
            "created_at": project.created_at.isoformat() if project.created_at else None,
            "updated_at": project.updated_at.isoformat() if project.updated_at else None,
        })

    return result


# ---------------------------------------------------------------------------
# 키워드 추출
# ---------------------------------------------------------------------------

async def handle_extract_keywords(document_id: int, top_n: int, use_llm: bool, db: Session):
    """문서에서 키워드를 추출하고 라벨을 자동 생성"""
    from scripts.backend.extract_keywords_and_labels import (
        extract_keywords_from_markdown,
        create_labels_from_keywords,
    )

    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다")

    chunks = db.query(KnowledgeChunk).filter(
        KnowledgeChunk.document_id == document_id
    ).all()

    if not chunks:
        raise HTTPException(status_code=400, detail="문서에 청크가 없습니다")

    full_content = "\n".join([chunk.content for chunk in chunks])

    keywords = extract_keywords_from_markdown(full_content, top_n=top_n, use_llm=use_llm)

    if not keywords:
        return {
            "document_id": document_id,
            "keywords": [],
            "labels_created": 0,
            "chunks_labeled": 0,
            "message": "키워드를 추출할 수 없습니다",
        }

    keyword_set = set(keywords)
    keyword_to_label_id = create_labels_from_keywords(keyword_set, label_type="keyword", db=db)

    labeled_count = 0
    for chunk in chunks:
        chunk_content_lower = chunk.content.lower()
        for keyword in keywords:
            if keyword.lower() in chunk_content_lower:
                label_id = keyword_to_label_id[keyword]
                existing = db.query(KnowledgeLabel).filter(
                    KnowledgeLabel.chunk_id == chunk.id,
                    KnowledgeLabel.label_id == label_id,
                ).first()

                if not existing:
                    knowledge_label = KnowledgeLabel(
                        chunk_id=chunk.id,
                        label_id=label_id,
                        confidence=0.7,
                        source="ai",
                        status="suggested",
                    )
                    db.add(knowledge_label)
                    labeled_count += 1

    db.commit()

    return {
        "document_id": document_id,
        "keywords": keywords,
        "labels_created": len(keyword_to_label_id),
        "chunks_labeled": labeled_count,
    }
