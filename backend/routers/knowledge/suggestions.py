"""AI Suggestion API 라우터"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from pydantic import BaseModel

from backend.models.database import get_db
from backend.models.models import KnowledgeChunk, Label, KnowledgeLabel, KnowledgeRelation
from backend.services.search.search_service import get_search_service
from backend.services.ai.ollama_client import ollama_connection_check

router = APIRouter(prefix="/api/knowledge", tags=["Suggestions"])


class LabelSuggestion(BaseModel):
    label_id: int
    label_name: str
    label_type: str
    confidence: float


class RelationSuggestion(BaseModel):
    target_chunk_id: int
    target_content_preview: str
    relation_type: str
    score: float


@router.get("/labels/suggest")
async def suggest_labels(chunk_id: int = Query(..., description="청크 ID"), db: Session = Depends(get_db)):
    """청크 기반 자동 라벨 추천"""
    chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="청크를 찾을 수 없습니다.")
    
    # 간단한 키워드 기반 라벨 추천 (실제로는 더 정교한 AI 모델 사용 가능)
    suggestions = []
    
    # 기존 라벨 중에서 유사한 라벨 찾기
    all_labels = db.query(Label).all()
    chunk_text_lower = chunk.content.lower()
    
    for label in all_labels:
        # 간단한 키워드 매칭 (실제로는 임베딩 기반 유사도 계산)
        label_name_lower = label.name.lower()
        if label_name_lower in chunk_text_lower:
            confidence = 0.8
        elif any(word in chunk_text_lower for word in label_name_lower.split("_")):
            confidence = 0.6
        else:
            continue
        
        suggestions.append({
            "label_id": label.id,
            "label_name": label.name,
            "label_type": label.label_type,
            "confidence": confidence
        })
    
    # 신뢰도 순으로 정렬
    suggestions.sort(key=lambda x: x["confidence"], reverse=True)
    
    return {
        "chunk_id": chunk_id,
        "suggestions": suggestions[:10]  # 상위 10개만 반환
    }


@router.get("/labels/suggest-llm")
async def suggest_labels_llm(
    chunk_id: int = Query(..., description="청크 ID"),
    limit: int = Query(10, ge=1, le=15, description="추천 개수"),
    model: Optional[str] = Query(None, description="Ollama 모델명 (미지정 시 기본 모델)"),
    db: Session = Depends(get_db),
):
    """청크 내용 기반 LLM 키워드·라벨 추천 (Ollama 사용)."""
    chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="청크를 찾을 수 없습니다.")
    content = (chunk.content or "").strip()
    if not content:
        return {"chunk_id": chunk_id, "suggestions": [], "source": "llm", "message": "청크 내용이 없습니다."}
    existing_ids = [
        kl.label_id
        for kl in db.query(KnowledgeLabel).filter(KnowledgeLabel.chunk_id == chunk_id).all()
    ]
    from backend.services.reasoning.chunk_label_recommender import ChunkLabelRecommender
    from backend.services.search.hybrid_search import get_hybrid_search_service

    recommender = ChunkLabelRecommender(db, get_hybrid_search_service())
    result = recommender.recommend(
        chunk_id=chunk_id,
        content=content,
        existing_label_ids=existing_ids,
        limit=limit,
        model=model,
    )
    suggestions = result.get("suggestions", [])
    new_keywords = result.get("new_keywords", [])
    message = None
    if not suggestions and not new_keywords:
        message = "추천 결과가 없습니다. Ollama가 실행 중인지 확인해 주세요. (청크에서 추출한 단어도 없습니다.)"
    ollama_feedback = ollama_connection_check()
    return {
        "chunk_id": chunk_id,
        "suggestions": suggestions,
        "new_keywords": new_keywords,
        "source": "llm",
        "message": message,
        "ollama_feedback": ollama_feedback,
    }


@router.post("/labels/suggest/{chunk_id}/apply/{label_id}")
async def apply_label_suggestion(
    chunk_id: int,
    label_id: int,
    confidence: float = 0.8,
    db: Session = Depends(get_db)
):
    """AI 추천 라벨 적용 (suggested 상태로 생성)"""
    chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="청크를 찾을 수 없습니다.")
    
    label = db.query(Label).filter(Label.id == label_id).first()
    if not label:
        raise HTTPException(status_code=404, detail="라벨을 찾을 수 없습니다.")
    
    # 이미 존재하는지 확인
    existing = db.query(KnowledgeLabel).filter(
        KnowledgeLabel.chunk_id == chunk_id,
        KnowledgeLabel.label_id == label_id
    ).first()
    
    if existing:
        # 이미 존재하면 상태만 업데이트
        existing.status = "suggested"
        existing.source = "ai"
        existing.confidence = confidence
    else:
        # 새로 생성
        new_label = KnowledgeLabel(
            chunk_id=chunk_id,
            label_id=label_id,
            status="suggested",
            source="ai",
            confidence=confidence
        )
        db.add(new_label)
    
    db.commit()
    
    return {
        "chunk_id": chunk_id,
        "label_id": label_id,
        "status": "suggested",
        "confidence": confidence
    }


@router.get("/relations/suggest")
async def suggest_relations(
    chunk_id: int = Query(..., description="청크 ID"), 
    limit: int = Query(5, description="추천 개수"), 
    db: Session = Depends(get_db)
):
    """유사도 기반 관계 추천"""
    chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="청크를 찾을 수 없습니다.")
    
    if not chunk.qdrant_point_id:
        raise HTTPException(status_code=400, detail="청크에 임베딩이 없습니다.")
    
    # Qdrant에서 유사 청크 검색
    search_service = get_search_service()
    
    try:
        # 현재 청크의 임베딩을 가져와서 유사 청크 검색
        # 실제로는 Qdrant에서 유사도 검색을 수행해야 함
        # 여기서는 간단한 구현으로 대체
        
        # 같은 문서의 다른 청크들을 유사 청크로 제안 (실제로는 임베딩 기반)
        similar_chunks = db.query(KnowledgeChunk).filter(
            KnowledgeChunk.document_id == chunk.document_id,
            KnowledgeChunk.id != chunk_id,
            KnowledgeChunk.status == "approved"  # 승인된 청크만
        ).limit(limit).all()
        
        suggestions = []
        for similar_chunk in similar_chunks:
            # 간단한 유사도 점수 계산 (실제로는 임베딩 기반 코사인 유사도)
            score = 0.7  # 기본값
            
            suggestions.append({
                "target_chunk_id": similar_chunk.id,
                "target_content_preview": similar_chunk.content[:100] + "..." if len(similar_chunk.content) > 100 else similar_chunk.content,
                "relation_type": "similar",
                "score": score
            })
        
        return {
            "chunk_id": chunk_id,
            "suggestions": suggestions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"관계 추천 생성 실패: {str(e)}")


@router.post("/relations/suggest/{chunk_id}/apply")
async def apply_relation_suggestion(
    chunk_id: int,
    target_chunk_id: int,
    relation_type: str = "similar",
    score: float = 0.7,
    db: Session = Depends(get_db)
):
    """AI 추천 관계 적용 (확정되지 않은 상태로 생성)"""
    source_chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == chunk_id).first()
    if not source_chunk:
        raise HTTPException(status_code=404, detail="소스 청크를 찾을 수 없습니다.")
    
    target_chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == target_chunk_id).first()
    if not target_chunk:
        raise HTTPException(status_code=404, detail="타겟 청크를 찾을 수 없습니다.")
    
    # 이미 존재하는지 확인
    existing = db.query(KnowledgeRelation).filter(
        KnowledgeRelation.source_chunk_id == chunk_id,
        KnowledgeRelation.target_chunk_id == target_chunk_id
    ).first()
    
    if existing:
        # 이미 존재하면 업데이트
        existing.confirmed = "false"  # AI 제안 상태
        existing.source = "ai"
        existing.score = score
    else:
        # 새로 생성
        new_relation = KnowledgeRelation(
            source_chunk_id=chunk_id,
            target_chunk_id=target_chunk_id,
            relation_type=relation_type,
            confirmed="false",  # AI 제안 상태
            source="ai",
            score=score,
            confidence=score
        )
        db.add(new_relation)
    
    db.commit()
    
    return {
        "source_chunk_id": chunk_id,
        "target_chunk_id": target_chunk_id,
        "relation_type": relation_type,
        "confirmed": False,
        "score": score
    }

