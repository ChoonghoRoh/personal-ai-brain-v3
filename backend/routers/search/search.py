"""검색 API 라우터"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict, Optional
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session

from backend.services.search.search_service import get_search_service
from backend.services.search.hybrid_search import get_hybrid_search_service, create_highlighted_snippet
from backend.models.database import get_db, SessionLocal
from backend.models.models import KnowledgeChunk, Document, Project

router = APIRouter(prefix="/api/search", tags=["Search"])


class AdvancedSearchRequest(BaseModel):
    """고급 검색 요청 모델"""
    query: str
    operator: str = "AND"  # AND, OR, NOT
    file_types: Optional[List[str]] = None
    project_ids: Optional[List[int]] = None
    label_ids: Optional[List[int]] = None
    date_from: Optional[str] = None  # YYYY-MM-DD
    date_to: Optional[str] = None  # YYYY-MM-DD
    limit: int = 20
    offset: int = 0


@router.get("")
async def search(
    q: str,
    limit: int = Query(5, ge=1, le=100, description="반환할 결과 수"),
    offset: int = Query(0, ge=0, description="페이징 오프셋"),
    file_path: Optional[str] = Query(None, description="파일 경로 필터"),
    use_cache: bool = Query(True, description="캐시 사용 여부"),
    sort_by: str = Query("score", description="정렬 기준 (score, created_at)"),
    sort_order: str = Query("desc", description="정렬 방향 (asc, desc)"),
    search_mode: str = Query(
        "semantic",
        description="검색 모드: semantic(의미만), keyword(키워드만), hybrid(키워드+의미 RRF)",
    ),
    project_id: Optional[int] = Query(None, description="프로젝트 필터 (hybrid/keyword 시 적용)"),
    label_ids: Optional[List[int]] = Query(None, description="라벨 필터 (hybrid/keyword 시 적용)"),
    status: Optional[str] = Query(None, description="청크 status 필터 (approved, draft, rejected)"),
    db: Session = Depends(get_db),
) -> Dict:
    """문서 검색 (최적화된 버전).

    - search_mode: semantic(기본) | keyword | hybrid (Phase 9-3-3)
    - 페이징 지원 (offset, limit)
    - 필터링 지원 (file_path 등)
    - 캐싱 지원
    """
    if not q or not q.strip():
        raise HTTPException(status_code=400, detail="검색어를 입력하세요")

    if search_mode in ("hybrid", "keyword"):
        hybrid_svc = get_hybrid_search_service()
        filters = {"file_path": file_path} if file_path else None
        if search_mode == "hybrid":
            rows = hybrid_svc.search_hybrid(
                db=db,
                query=q.strip(),
                top_k=limit + offset,
                filters=filters,
                project_id=project_id,
                label_ids=label_ids,
                status=status,
            )
        else:
            rows = hybrid_svc.keyword_search(
                db=db,
                query=q.strip(),
                top_k=limit + offset,
                project_id=project_id,
                label_ids=label_ids,
                status=status,
            )
        # API 응답 형식 통일 (document_id, file, score, content, snippet, chunk_index, highlighted_snippet)
        results = []
        for r in rows[offset : offset + limit]:
            content_preview = (r.get("content") or "")[:200]
            if len(r.get("content") or "") > 200:
                content_preview += "..."
            highlighted = create_highlighted_snippet(r.get("content", ""), q.strip())
            results.append({
                "document_id": r.get("document_id", ""),
                "file": r.get("file", ""),
                "score": r.get("score", 0.0),
                "content": r.get("content", ""),
                "snippet": r.get("snippet") or content_preview,
                "highlighted_snippet": highlighted,
                "chunk_index": r.get("chunk_index", 0),
            })
        return {
            "results": results,
            "total": len(rows),
            "offset": offset,
            "limit": limit,
        }

    service = get_search_service()
    filters = {}
    if file_path:
        filters["file_path"] = file_path
    if status:
        filters["status"] = status
    result = service.search(
        query=q.strip(),
        top_k=limit,
        offset=offset,
        filters=filters if filters else None,
        use_cache=use_cache,
        search_mode="semantic",
    )
    # highlighted_snippet 추가
    if "results" in result:
        for r in result["results"]:
            r["highlighted_snippet"] = create_highlighted_snippet(
                r.get("content", ""), q.strip()
            )
    if sort_by == "score" and "results" in result:
        if sort_order.lower() == "asc":
            result["results"].sort(key=lambda x: x.get("score", 0))
        else:
            result["results"].sort(key=lambda x: x.get("score", 0), reverse=True)
    return result


@router.get("/simple")
async def search_simple(q: str, limit: int = Query(5, ge=1, le=100)) -> List[Dict]:
    """간단한 검색 API (하위 호환성)"""
    if not q or not q.strip():
        raise HTTPException(status_code=400, detail="검색어를 입력하세요")
    
    service = get_search_service()
    results = service.search_simple(q.strip(), top_k=limit)
    
    return results


@router.post("/cache/clear")
async def clear_cache():
    """검색 캐시 초기화"""
    service = get_search_service()
    service.clear_cache()
    return {"message": "캐시가 초기화되었습니다."}


@router.get("/cache/stats")
async def get_cache_stats():
    """검색 캐시 통계"""
    service = get_search_service()
    stats = service.get_cache_stats()
    return stats


@router.post("/advanced")
async def advanced_search(request: AdvancedSearchRequest):
    """고급 검색 (복합 검색, 날짜 범위, 필터링)"""
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="검색어를 입력하세요")
    
    service = get_search_service()
    db = SessionLocal()
    
    try:
        # 기본 검색 실행
        search_result = service.search(
            query=request.query.strip(),
            top_k=100,  # 필터링 전에 더 많이 가져오기
            offset=0,
            use_cache=True
        )
        
        # 필터링 적용
        filtered_results = []
        
        for result in search_result['results']:
            # 파일 경로로 문서 조회
            doc = db.query(Document).filter(
                Document.file_path == result.get('file')
            ).first()
            
            if not doc:
                continue
            
            # 파일 형식 필터
            if request.file_types:
                if doc.file_type not in request.file_types:
                    continue
            
            # 프로젝트 필터
            if request.project_ids:
                if not doc.project_id or doc.project_id not in request.project_ids:
                    continue
            
            # 날짜 범위 필터
            if request.date_from or request.date_to:
                doc_date = doc.created_at.date() if doc.created_at else None
                if doc_date:
                    if request.date_from:
                        try:
                            date_from = datetime.strptime(request.date_from, "%Y-%m-%d").date()
                            if doc_date < date_from:
                                continue
                        except:
                            pass
                    if request.date_to:
                        try:
                            date_to = datetime.strptime(request.date_to, "%Y-%m-%d").date()
                            if doc_date > date_to:
                                continue
                        except:
                            pass
            
            # 라벨 필터 (청크 ID로 확인)
            if request.label_ids:
                chunk_id = None
                try:
                    # Qdrant point ID로 청크 찾기
                    chunk = db.query(KnowledgeChunk).filter(
                        KnowledgeChunk.qdrant_point_id == result.get('document_id')
                    ).first()
                    if chunk:
                        from backend.models.models import KnowledgeLabel
                        label_count = db.query(KnowledgeLabel).filter(
                            KnowledgeLabel.chunk_id == chunk.id,
                            KnowledgeLabel.label_id.in_(request.label_ids)
                        ).count()
                        if label_count == 0:
                            continue
                except:
                    pass
            
            filtered_results.append(result)
        
        # 페이징 적용
        total_count = len(filtered_results)
        paginated_results = filtered_results[request.offset:request.offset + request.limit]
        
        return {
            'results': paginated_results,
            'total': total_count,
            'offset': request.offset,
            'limit': request.limit
        }
    finally:
        db.close()


@router.get("/filters")
async def get_search_filters():
    """검색 필터 옵션 조회"""
    db = SessionLocal()
    
    try:
        # 파일 형식 목록
        file_types = db.query(Document.file_type).distinct().all()
        file_types_list = [ft[0] for ft in file_types if ft[0]]
        
        # 프로젝트 목록
        projects = db.query(Project).all()
        projects_list = [{"id": p.id, "name": p.name} for p in projects]
        
        return {
            'file_types': file_types_list,
            'projects': projects_list
        }
    finally:
        db.close()

