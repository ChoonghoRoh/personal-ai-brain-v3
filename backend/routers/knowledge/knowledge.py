"""Knowledge Chunks API 라우터"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from backend.models.database import get_db

# --- 핸들러 import ---
from backend.routers.knowledge.knowledge_handlers import (
    handle_list_chunks,
    handle_get_chunk,
    handle_create_chunk,
    handle_add_labels_to_chunk,
    handle_apply_suggested_labels,
    handle_remove_labels_from_chunk,
    handle_get_chunk_labels_detailed,
    handle_get_chunk_structure_suggestions,
    handle_get_document_suggestions,
)
from backend.routers.knowledge.document_handlers import (
    handle_set_document_category,
    handle_create_document,
    handle_list_documents_with_category,
    handle_get_document,
    handle_list_projects,
    handle_extract_keywords,
    handle_get_folder_tree,
    handle_get_knowledge_tree,
)

router = APIRouter(prefix="/api/knowledge", tags=["Knowledge"])


# --- Pydantic 모델 ---

class ChunkResponse(BaseModel):
    id: int
    content: str
    chunk_index: int
    document_id: int
    document_name: Optional[str] = None
    project_name: Optional[str] = None
    title: Optional[str] = None
    title_source: Optional[str] = None
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
    title: Optional[str] = None
    title_source: Optional[str] = None
    labels: List[dict] = []
    outgoing_relations: List[dict] = []
    incoming_relations: List[dict] = []

    class Config:
        from_attributes = True


class ChunkCreateRequest(BaseModel):
    """단일 청크 생성 요청 (Phase 9-3-2)"""
    document_id: int
    content: str
    chunk_index: int
    title: Optional[str] = None
    title_source: Optional[str] = None


class ChunkLabelsAdd(BaseModel):  # Phase 7.7
    label_ids: List[int]
    status: str = "confirmed"
    source: str = "human"


class ChunkLabelsRemove(BaseModel):  # Phase 7.7
    label_ids: List[int]


class DocumentCategorySet(BaseModel):  # Phase 7.7
    label_id: int


class DocumentCreateRequest(BaseModel):
    """문서 생성 요청 (Phase 9-3-2)"""
    file_path: str
    file_name: str
    file_type: str = "md"
    size: int = 0
    project_id: Optional[int] = None


# --- 엔드포인트 ---

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
    db: Session = Depends(get_db),
):
    return await handle_list_chunks(label_id, document_id, project_id, limit, offset, sort_by, sort_order, db)


@router.get("/chunks/{chunk_id}", response_model=ChunkDetailResponse)
async def get_chunk(chunk_id: int, db: Session = Depends(get_db)):
    """지식 청크 상세 조회"""
    return await handle_get_chunk(chunk_id, db)


@router.post("/chunks", summary="단일 청크 생성 (Phase 9-3-2)")
async def create_chunk(
    request: ChunkCreateRequest,
    include_suggestions: bool = Query(True, description="구조 추천 포함 여부"),
    db: Session = Depends(get_db),
):
    """단일 청크를 생성하고, 옵션에 따라 structure_suggestions를 반환합니다."""
    return await handle_create_chunk(request, include_suggestions, db)


# ========== Phase 7.7: 청크-라벨 연결 API 확장 ==========

@router.post("/chunks/{chunk_id}/labels")
async def add_labels_to_chunk(
    chunk_id: int,
    request: ChunkLabelsAdd,
    db: Session = Depends(get_db),
):
    """청크에 다중 라벨 추가 (Phase 7.7)"""
    return await handle_add_labels_to_chunk(chunk_id, request, db)


@router.post("/chunks/{chunk_id}/labels/apply")
async def apply_suggested_labels(
    chunk_id: int,
    request: ChunkLabelsAdd,
    auto_confirm: bool = Query(False, description="추천 라벨을 confirmed 상태로 적용 (Phase 9-3-2)"),
    db: Session = Depends(get_db),
):
    """추천 라벨 일괄 적용 (Phase 9-3-2)."""
    return await handle_apply_suggested_labels(chunk_id, request, auto_confirm, db)


@router.delete("/chunks/{chunk_id}/labels")
async def remove_labels_from_chunk(
    chunk_id: int,
    request: ChunkLabelsRemove,
    db: Session = Depends(get_db),
):
    """청크에서 다중 라벨 제거 (Phase 7.7)"""
    return await handle_remove_labels_from_chunk(chunk_id, request, db)


@router.get("/chunks/{chunk_id}/labels")
async def get_chunk_labels_detailed(chunk_id: int, db: Session = Depends(get_db)):
    """청크의 라벨 목록 조회 (상세 정보 포함, Phase 7.7)"""
    return await handle_get_chunk_labels_detailed(chunk_id, db)


# ========== Phase 9-3-2: 청크 구조 추천 API ==========

@router.get("/chunks/{chunk_id}/suggestions")
async def get_chunk_structure_suggestions(
    chunk_id: int,
    db: Session = Depends(get_db),
):
    """청크에 대한 라벨/유사 청크/카테고리 추천 (Phase 9-3-2)."""
    return await handle_get_chunk_structure_suggestions(chunk_id, db)


@router.get("/documents/{document_id}/suggestions")
async def get_document_suggestions(
    document_id: int,
    db: Session = Depends(get_db),
):
    """문서에 대한 카테고리/유사 문서 추천 (Phase 9-3-2)."""
    return await handle_get_document_suggestions(document_id, db)


# ========== Phase 18-2: 폴더 계층 트리 API ==========

@router.get("/folder-tree", summary="폴더 계층 트리 조회 (Phase 18-2)")
async def get_folder_tree(
    project_id: Optional[int] = Query(None, description="프로젝트 ID (None이면 전체)"),
    db: Session = Depends(get_db),
):
    """프로젝트의 문서를 file_path 기반 폴더 계층 트리로 반환합니다."""
    return await handle_get_folder_tree(project_id, db)


@router.get("/tree", summary="통합 지식 트리 조회 (Phase 18-2)")
async def get_knowledge_tree(
    project_id: Optional[int] = Query(None, description="프로젝트 ID (None이면 전체)"),
    include_chunks: bool = Query(True, description="Chunk 레벨 포함 여부"),
    max_depth: int = Query(4, ge=1, le=10, description="트리 최대 깊이"),
    db: Session = Depends(get_db),
):
    """폴더 > 문서 > 청크 계층을 포함한 통합 지식 트리를 반환합니다."""
    return await handle_get_knowledge_tree(project_id, include_chunks, max_depth, db)


# ========== Phase 7.7: 문서 카테고리 설정 API ==========

@router.post("/documents/{document_id}/category")
async def set_document_category(
    document_id: int,
    request: DocumentCategorySet,
    db: Session = Depends(get_db),
):
    """문서 카테고리 설정 (Phase 7.7)"""
    return await handle_set_document_category(document_id, request, db)


# ========== Phase 9-3-2: 문서 생성 API ==========

@router.post("/documents", summary="문서 생성 (Phase 9-3-2)")
async def create_document(
    request: DocumentCreateRequest,
    include_suggestions: bool = Query(True, description="카테고리/유사 문서 추천 포함 여부"),
    db: Session = Depends(get_db),
):
    """문서를 생성하고 suggested_category 및 similar_documents를 반환합니다."""
    return await handle_create_document(request, include_suggestions, db)


@router.get("/documents")
async def list_documents_with_category(
    category_label_id: Optional[int] = Query(None, description="카테고리 라벨 ID로 필터링"),
    label_type: Optional[str] = Query(None, description="라벨 타입 필터링"),
    db: Session = Depends(get_db),
):
    """카테고리별 문서 목록 조회 (Phase 7.7)"""
    return await handle_list_documents_with_category(category_label_id, label_type, db)


@router.get("/documents/{document_id}")
async def get_document(document_id: int, db: Session = Depends(get_db)):
    """문서 상세 조회"""
    return await handle_get_document(document_id, db)


@router.get("/projects")
async def list_projects(db: Session = Depends(get_db)):
    """프로젝트 목록 조회"""
    return await handle_list_projects(db)


@router.post("/documents/{document_id}/extract-keywords")
async def extract_keywords_from_document(
    document_id: int,
    top_n: int = 10,
    use_llm: bool = False,
    db: Session = Depends(get_db),
):
    """문서에서 키워드를 추출하고 라벨을 자동 생성"""
    return await handle_extract_keywords(document_id, top_n, use_llm, db)
