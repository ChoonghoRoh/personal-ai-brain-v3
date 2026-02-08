"""Knowledge Chunks API 라우터"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from backend.models.database import get_db
from backend.models.models import KnowledgeChunk, Label, KnowledgeLabel, Document, Project, KnowledgeRelation
from backend.config import AUTO_STRUCTURE_MATCHING_ENABLED
from backend.services.knowledge.structure_matcher import get_structure_matcher

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


class ChunkResponse(BaseModel):
    id: int
    content: str
    chunk_index: int
    document_id: int
    document_name: Optional[str] = None
    project_name: Optional[str] = None
    title: Optional[str] = None  # Phase 7.9.5: Chunk title
    title_source: Optional[str] = None  # Phase 7.9.5: Title source
    labels: List[dict] = []
    outgoing_relations_count: int = 0
    incoming_relations_count: int = 0

    class Config:
        from_attributes = True


class ChunkListResponse(BaseModel):
    """페이징 정보를 포함한 청크 목록 응답"""
    items: List[ChunkResponse]
    total_count: int
    limit: int
    offset: int
    total_pages: int
    current_page: int


class ChunkDetailResponse(BaseModel):
    id: int
    content: str
    chunk_index: int
    document_id: int
    document_name: Optional[str] = None
    project_name: Optional[str] = None
    title: Optional[str] = None  # Phase 7.9.5: Chunk title
    title_source: Optional[str] = None  # Phase 7.9.5: Title source
    labels: List[dict] = []
    outgoing_relations: List[dict] = []
    incoming_relations: List[dict] = []

    class Config:
        from_attributes = True


@router.get("/chunks", response_model=ChunkListResponse, 
            summary="청크 목록 조회",
            description="""
            지식 청크 목록을 조회합니다.
            
            **필터링 옵션**:
            - `label_id`: 특정 라벨이 붙은 청크만 조회
            - `document_id`: 특정 문서의 청크만 조회
            - `project_id`: 특정 프로젝트의 청크만 조회
            
            **페이징**:
            - `limit`: 반환할 최대 결과 수 (기본값: 100)
            - `offset`: 페이징 오프셋 (기본값: 0)
            
            **예제**:
            ```
            GET /api/knowledge/chunks?label_id=1&limit=20&offset=0
            ```
            """)
async def list_chunks(
    label_id: Optional[int] = Query(None, description="라벨 ID로 필터링"),
    document_id: Optional[int] = Query(None, description="문서 ID로 필터링"),
    project_id: Optional[int] = Query(None, description="프로젝트 ID로 필터링"),
    limit: int = Query(100, ge=1, le=1000, description="최대 결과 수"),
    offset: int = Query(0, ge=0, description="오프셋"),
    sort_by: str = Query("created_at", description="정렬 기준 (created_at, chunk_index, title)"),
    sort_order: str = Query("desc", description="정렬 방향 (asc, desc)"),
    db: Session = Depends(get_db)
):
    """지식 청크 목록 조회 (페이징 지원)"""
    # 기본 쿼리 생성
    base_query = db.query(KnowledgeChunk)
    
    # 라벨 필터
    if label_id:
        base_query = base_query.join(KnowledgeLabel).filter(KnowledgeLabel.label_id == label_id)
    
    # 문서 필터
    if document_id:
        base_query = base_query.filter(KnowledgeChunk.document_id == document_id)
    
    # 프로젝트 필터
    if project_id:
        base_query = base_query.join(Document).filter(Document.project_id == project_id)
    
    # 정렬 적용
    valid_sort_fields = ["created_at", "chunk_index", "title"]
    if sort_by not in valid_sort_fields:
        sort_by = "created_at"
    
    sort_field = getattr(KnowledgeChunk, sort_by, KnowledgeChunk.created_at)
    if sort_order.lower() == "asc":
        base_query = base_query.order_by(sort_field.asc())
    else:
        base_query = base_query.order_by(sort_field.desc())
    
    # 총 개수 계산 (필터 적용 후)
    total_count = base_query.count()
    
    # Eager loading으로 N+1 쿼리 문제 해결
    from sqlalchemy.orm import joinedload, selectinload
    
    # 정렬 및 페이징 (Eager loading 적용)
    chunks = base_query.options(
        joinedload(KnowledgeChunk.document).joinedload(Document.project),
        selectinload(KnowledgeChunk.labels).joinedload(KnowledgeLabel.label)
    ).order_by(KnowledgeChunk.id.desc()).offset(offset).limit(limit).all()
    
    # 결과 생성 (이미 로드된 관계 사용)
    result = []
    for chunk in chunks:
        # 문서 정보 (이미 로드됨)
        doc = chunk.document
        project = doc.project if doc else None
        
        # 라벨 정보 (이미 로드됨)
        label_list = [
            {"id": kl.label.id, "name": kl.label.name, "label_type": kl.label.label_type} 
            for kl in chunk.labels
        ]
        
        # 관계 개수 (별도 쿼리 필요, 하지만 인덱스로 최적화됨)
        outgoing_count = len([r for r in chunk.outgoing_relations if r.confirmed == "true"]) if hasattr(chunk, 'outgoing_relations') else 0
        incoming_count = len([r for r in chunk.incoming_relations if r.confirmed == "true"]) if hasattr(chunk, 'incoming_relations') else 0
        
        # 관계 개수를 정확히 계산하기 위해 별도 쿼리 (최적화: 인덱스 사용)
        if outgoing_count == 0 or incoming_count == 0:
            from backend.models.models import KnowledgeRelation
            if outgoing_count == 0:
                outgoing_count = db.query(KnowledgeRelation).filter(
                    KnowledgeRelation.source_chunk_id == chunk.id,
                    KnowledgeRelation.confirmed == "true"
                ).count()
            if incoming_count == 0:
                incoming_count = db.query(KnowledgeRelation).filter(
                    KnowledgeRelation.target_chunk_id == chunk.id,
                    KnowledgeRelation.confirmed == "true"
                ).count()
        
        result.append(ChunkResponse(
            id=chunk.id,
            content=chunk.content,
            chunk_index=chunk.chunk_index,
            document_id=chunk.document_id,
            document_name=doc.file_name if doc else None,
            project_name=project.name if project else None,
            title=chunk.title,
            title_source=chunk.title_source,
            labels=label_list,
            outgoing_relations_count=outgoing_count,
            incoming_relations_count=incoming_count
        ))
    
    # 페이징 메타데이터 계산
    total_pages = (total_count + limit - 1) // limit if limit > 0 else 0
    current_page = (offset // limit) + 1 if limit > 0 else 1
    
    return ChunkListResponse(
        items=result,
        total_count=total_count,
        limit=limit,
        offset=offset,
        total_pages=total_pages,
        current_page=current_page
    )


@router.get("/chunks/{chunk_id}", response_model=ChunkDetailResponse)
async def get_chunk(chunk_id: int, db: Session = Depends(get_db)):
    """지식 청크 상세 조회"""
    chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="청크를 찾을 수 없습니다")
    
    # 문서 정보
    doc = db.query(Document).filter(Document.id == chunk.document_id).first()
    project = None
    if doc and doc.project_id:
        project = db.query(Project).filter(Project.id == doc.project_id).first()
    
    # 라벨 정보
    labels = db.query(Label).join(KnowledgeLabel).filter(
        KnowledgeLabel.chunk_id == chunk.id
    ).all()
    label_list = [{"id": label.id, "name": label.name, "label_type": label.label_type} for label in labels]
    
    # 나가는 관계
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
                "description": rel.description
            })
    
    # 들어오는 관계
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
                "description": rel.description
            })
    
    return ChunkDetailResponse(
        id=chunk.id,
        content=chunk.content,
        chunk_index=chunk.chunk_index,
        document_id=chunk.document_id,
        document_name=doc.file_name if doc else None,
        project_name=project.name if project else None,
        title=chunk.title,
        title_source=chunk.title_source,
        labels=label_list,
        outgoing_relations=outgoing_list,
        incoming_relations=incoming_list
    )


# ========== Phase 9-3-2: 단일 청크 생성 API (structure_suggestions 반환) ==========


class ChunkCreateRequest(BaseModel):
    """단일 청크 생성 요청 (Phase 9-3-2)"""
    document_id: int
    content: str
    chunk_index: int
    title: Optional[str] = None
    title_source: Optional[str] = None  # "heading" | "ai_extracted" | "manual"


@router.post("/chunks", summary="단일 청크 생성 (Phase 9-3-2)")
async def create_chunk(
    request: ChunkCreateRequest,
    include_suggestions: bool = Query(True, description="구조 추천 포함 여부"),
    db: Session = Depends(get_db),
):
    """단일 청크를 생성하고, 옵션에 따라 structure_suggestions(라벨·유사 청크·카테고리 추천)를 반환합니다."""
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


# ========== Phase 7.7: 청크-라벨 연결 API 확장 ==========

class ChunkLabelsAdd(BaseModel):  # Phase 7.7
    label_ids: List[int]
    status: str = "confirmed"  # suggested, confirmed, rejected
    source: str = "human"  # ai, human


class ChunkLabelsRemove(BaseModel):  # Phase 7.7
    label_ids: List[int]


@router.post("/chunks/{chunk_id}/labels")
async def add_labels_to_chunk(
    chunk_id: int,
    request: ChunkLabelsAdd,
    db: Session = Depends(get_db)
):
    """청크에 다중 라벨 추가 (Phase 7.7)"""
    chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="청크를 찾을 수 없습니다")
    
    added_count = 0
    skipped_count = 0
    
    for label_id in request.label_ids:
        # 라벨 존재 확인
        label = db.query(Label).filter(Label.id == label_id).first()
        if not label:
            skipped_count += 1
            continue
        
        # 중복 체크
        existing = db.query(KnowledgeLabel).filter(
            KnowledgeLabel.chunk_id == chunk_id,
            KnowledgeLabel.label_id == label_id
        ).first()
        
        if existing:
            # 존재하면 상태/소스 업데이트
            existing.status = request.status
            existing.source = request.source
            skipped_count += 1
        else:
            # 새로 생성
            knowledge_label = KnowledgeLabel(
                chunk_id=chunk_id,
                label_id=label_id,
                status=request.status,
                source=request.source,
                confidence=1.0
            )
            db.add(knowledge_label)
            added_count += 1
    
    db.commit()
    
    return {
        "message": f"{added_count}개의 라벨이 추가되었습니다",
        "added_count": added_count,
        "skipped_count": skipped_count
    }


@router.post("/chunks/{chunk_id}/labels/apply")
async def apply_suggested_labels(
    chunk_id: int,
    request: ChunkLabelsAdd,
    auto_confirm: bool = Query(False, description="추천 라벨을 confirmed 상태로 적용 (Phase 9-3-2)"),
    db: Session = Depends(get_db),
):
    """추천 라벨 일괄 적용 (Phase 9-3-2)."""
    from backend.services.knowledge.auto_labeler import get_auto_labeler
    labeler = get_auto_labeler(db)
    result = labeler.apply_suggested_labels(
        chunk_id=chunk_id,
        label_ids=request.label_ids,
        auto_confirm=auto_confirm,
    )
    return result


@router.delete("/chunks/{chunk_id}/labels")
async def remove_labels_from_chunk(
    chunk_id: int,
    request: ChunkLabelsRemove,
    db: Session = Depends(get_db)
):
    """청크에서 다중 라벨 제거 (Phase 7.7)"""
    chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="청크를 찾을 수 없습니다")
    
    removed_count = 0
    
    for label_id in request.label_ids:
        knowledge_label = db.query(KnowledgeLabel).filter(
            KnowledgeLabel.chunk_id == chunk_id,
            KnowledgeLabel.label_id == label_id
        ).first()
        
        if knowledge_label:
            db.delete(knowledge_label)
            removed_count += 1
    
    db.commit()
    
    return {
        "message": f"{removed_count}개의 라벨이 제거되었습니다",
        "removed_count": removed_count
    }


@router.get("/chunks/{chunk_id}/labels")
async def get_chunk_labels_detailed(chunk_id: int, db: Session = Depends(get_db)):
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
                "confidence": kl.confidence
            })
    
    return {
        "chunk_id": chunk_id,
        "labels": result
    }


# ========== Phase 9-3-2: 청크 구조 추천 API ==========

@router.get("/chunks/{chunk_id}/suggestions")
async def get_chunk_structure_suggestions(
    chunk_id: int,
    db: Session = Depends(get_db),
):
    """청크에 대한 라벨·유사 청크·카테고리 추천 (Phase 9-3-2)."""
    if not AUTO_STRUCTURE_MATCHING_ENABLED:
        return {"suggested_labels": [], "similar_chunks": [], "suggested_category": None}
    chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="청크를 찾을 수 없습니다")
    matcher = get_structure_matcher(db)
    result = matcher.match_on_chunk_create(chunk)
    return result


@router.get("/documents/{document_id}/suggestions")
async def get_document_suggestions(
    document_id: int,
    db: Session = Depends(get_db),
):
    """문서에 대한 카테고리·유사 문서 추천 (Phase 9-3-2)."""
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


# ========== Phase 7.7: 문서 카테고리 설정 API ==========

class DocumentCategorySet(BaseModel):  # Phase 7.7
    label_id: int


@router.post("/documents/{document_id}/category")
async def set_document_category(
    document_id: int,
    request: DocumentCategorySet,
    db: Session = Depends(get_db)
):
    """문서 카테고리 설정 (Phase 7.7)"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다")
    
    # 라벨 존재 및 타입 확인
    label = db.query(Label).filter(Label.id == request.label_id).first()
    if not label:
        raise HTTPException(status_code=404, detail="라벨을 찾을 수 없습니다")
    
    # 카테고리/프로젝트/도메인 타입만 허용
    if label.label_type not in ["category", "project", "domain"]:
        raise HTTPException(
            status_code=400,
            detail=f"카테고리 라벨은 'category', 'project', 'domain' 타입만 허용됩니다. (현재: {label.label_type})"
        )
    
    document.category_label_id = request.label_id
    db.commit()
    db.refresh(document)
    
    return {
        "message": "문서 카테고리가 설정되었습니다",
        "document_id": document_id,
        "category_label_id": request.label_id,
        "category_label_name": label.name
    }


# ========== Phase 9-3-2: 문서 생성 API (suggested_category, similar_documents 반환) ==========


class DocumentCreateRequest(BaseModel):
    """문서 생성 요청 (Phase 9-3-2)"""
    file_path: str
    file_name: str
    file_type: str = "md"  # md, pdf, docx
    size: int = 0
    project_id: Optional[int] = None


@router.post("/documents", summary="문서 생성 (Phase 9-3-2)")
async def create_document(
    request: DocumentCreateRequest,
    include_suggestions: bool = Query(True, description="카테고리·유사 문서 추천 포함 여부"),
    db: Session = Depends(get_db),
):
    """문서를 생성하고, 옵션에 따라 suggested_category 및 similar_documents를 반환합니다."""
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


@router.get("/documents")
async def list_documents_with_category(
    category_label_id: Optional[int] = Query(None, description="카테고리 라벨 ID로 필터링"),
    label_type: Optional[str] = Query(None, description="라벨 타입 필터링"),
    db: Session = Depends(get_db)
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
        
        # 라벨 타입 필터링
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
            "created_at": doc.created_at.isoformat() if doc.created_at else None
        })
    
    return result


@router.get("/documents/{document_id}")
async def get_document(document_id: int, db: Session = Depends(get_db)):
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
    
    # 청크 개수
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
        "updated_at": document.updated_at.isoformat() if document.updated_at else None
    }


@router.get("/projects")
async def list_projects(db: Session = Depends(get_db)):
    """프로젝트 목록 조회"""
    projects = db.query(Project).all()
    
    result = []
    for project in projects:
        # 문서 개수
        documents_count = db.query(Document).filter(Document.project_id == project.id).count()
        
        result.append({
            "id": project.id,
            "name": project.name,
            "path": project.path,
            "description": project.description,
            "documents_count": documents_count,
            "created_at": project.created_at.isoformat() if project.created_at else None,
            "updated_at": project.updated_at.isoformat() if project.updated_at else None
        })
    
    return result


@router.post("/documents/{document_id}/extract-keywords")
async def extract_keywords_from_document(
    document_id: int,
    top_n: int = 10,
    use_llm: bool = False,
    db: Session = Depends(get_db)
):
    """문서에서 키워드를 추출하고 라벨을 자동 생성"""
    from scripts.backend.extract_keywords_and_labels import (
        extract_keywords_from_markdown,
        create_labels_from_keywords,
        auto_label_chunks
    )
    
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다")
    
    # 문서 내용 가져오기
    chunks = db.query(KnowledgeChunk).filter(
        KnowledgeChunk.document_id == document_id
    ).all()
    
    if not chunks:
        raise HTTPException(status_code=400, detail="문서에 청크가 없습니다")
    
    # 모든 청크 내용 합치기
    full_content = "\n".join([chunk.content for chunk in chunks])
    
    # 키워드 추출
    keywords = extract_keywords_from_markdown(full_content, top_n=top_n, use_llm=use_llm)
    
    if not keywords:
        return {
            "document_id": document_id,
            "keywords": [],
            "labels_created": 0,
            "chunks_labeled": 0,
            "message": "키워드를 추출할 수 없습니다"
        }
    
    # 라벨 생성
    keyword_set = set(keywords)
    keyword_to_label_id = create_labels_from_keywords(keyword_set, label_type="keyword", db=db)
    
    # 청크에 자동 라벨링
    labeled_count = 0
    for chunk in chunks:
        chunk_content_lower = chunk.content.lower()
        for keyword in keywords:
            if keyword.lower() in chunk_content_lower:
                label_id = keyword_to_label_id[keyword]
                existing = db.query(KnowledgeLabel).filter(
                    KnowledgeLabel.chunk_id == chunk.id,
                    KnowledgeLabel.label_id == label_id
                ).first()
                
                if not existing:
                    knowledge_label = KnowledgeLabel(
                        chunk_id=chunk.id,
                        label_id=label_id,
                        confidence=0.7,
                        source="ai",
                        status="suggested"
                    )
                    db.add(knowledge_label)
                    labeled_count += 1
    
    db.commit()
    
    return {
        "document_id": document_id,
        "keywords": keywords,
        "labels_created": len(keyword_to_label_id),
        "chunks_labeled": labeled_count
    }

