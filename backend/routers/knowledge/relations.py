"""지식 관계 API 라우터"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from pydantic import BaseModel

from backend.models.database import get_db
from backend.models.models import KnowledgeRelation, KnowledgeChunk

router = APIRouter(prefix="/api/relations", tags=["Relations"])


class RelationCreate(BaseModel):
    source_chunk_id: int
    target_chunk_id: int
    relation_type: str
    confidence: float = 1.0
    description: str = None


class RelationApplyItem(BaseModel):
    """추천 관계 1건 (Phase 9-3-2 일괄 적용용)"""
    source_chunk_id: int
    target_chunk_id: int
    relation_type: str = "related_to"
    score: Optional[float] = 0.8


class RelationsApplyRequest(BaseModel):
    """추천 관계 일괄 적용 요청 (Phase 9-3-2)"""
    relations: List[RelationApplyItem]


class RelationResponse(BaseModel):
    id: int
    source_chunk_id: int
    target_chunk_id: int
    relation_type: str
    score: Optional[float] = None  # confidence 대신 score 사용
    description: Optional[str] = None
    confirmed: Optional[str] = None
    source: Optional[str] = None

    class Config:
        from_attributes = True


@router.post("", response_model=RelationResponse)
async def create_relation(relation: RelationCreate, db: Session = Depends(get_db)):
    """관계 생성"""
    # 소스 청크 확인
    source_chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == relation.source_chunk_id).first()
    if not source_chunk:
        raise HTTPException(status_code=404, detail="소스 청크를 찾을 수 없습니다")
    
    # 타겟 청크 확인
    target_chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == relation.target_chunk_id).first()
    if not target_chunk:
        raise HTTPException(status_code=404, detail="타겟 청크를 찾을 수 없습니다")
    
    # 자기 자신과의 관계 방지
    if relation.source_chunk_id == relation.target_chunk_id:
        raise HTTPException(status_code=400, detail="자기 자신과의 관계는 생성할 수 없습니다")
    
    # 중복 체크
    existing = db.query(KnowledgeRelation).filter(
        KnowledgeRelation.source_chunk_id == relation.source_chunk_id,
        KnowledgeRelation.target_chunk_id == relation.target_chunk_id,
        KnowledgeRelation.relation_type == relation.relation_type
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="이미 동일한 관계가 존재합니다")
    
    db_relation = KnowledgeRelation(**relation.dict())
    db.add(db_relation)
    db.commit()
    db.refresh(db_relation)
    return db_relation


@router.post("/apply", summary="추천 관계 일괄 적용 (Phase 9-3-2)")
async def apply_relations_batch(
    request: RelationsApplyRequest,
    db: Session = Depends(get_db),
):
    """추천 관계 목록을 일괄 적용합니다. AI 제안 상태(confirmed=false, source=ai)로 생성됩니다."""
    if not request.relations:
        return {"message": "적용할 관계가 없습니다", "applied_count": 0, "skipped_count": 0}

    applied = 0
    skipped = 0
    errors = []

    for item in request.relations:
        if item.source_chunk_id == item.target_chunk_id:
            errors.append(f"자기 자신과의 관계는 생성할 수 없습니다 (chunk_id={item.source_chunk_id})")
            skipped += 1
            continue

        source = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == item.source_chunk_id).first()
        if not source:
            errors.append(f"소스 청크를 찾을 수 없습니다: {item.source_chunk_id}")
            skipped += 1
            continue
        target = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == item.target_chunk_id).first()
        if not target:
            errors.append(f"타겟 청크를 찾을 수 없습니다: {item.target_chunk_id}")
            skipped += 1
            continue

        existing = db.query(KnowledgeRelation).filter(
            KnowledgeRelation.source_chunk_id == item.source_chunk_id,
            KnowledgeRelation.target_chunk_id == item.target_chunk_id,
            KnowledgeRelation.relation_type == item.relation_type,
        ).first()
        if existing:
            existing.confirmed = "false"
            existing.source = "ai"
            existing.score = item.score
            existing.confidence = item.score or 0.8
            applied += 1
            continue

        rel = KnowledgeRelation(
            source_chunk_id=item.source_chunk_id,
            target_chunk_id=item.target_chunk_id,
            relation_type=item.relation_type,
            confirmed="false",
            source="ai",
            score=item.score,
            confidence=item.score or 0.8,
        )
        db.add(rel)
        applied += 1

    db.commit()
    return {
        "message": f"{applied}건 적용, {skipped}건 스킵",
        "applied_count": applied,
        "skipped_count": skipped,
        "errors": errors[:20],
    }


@router.get("", response_model=List[RelationResponse])
async def list_relations(
    source_chunk_id: Optional[int] = Query(None, description="소스 청크 ID"),
    target_chunk_id: Optional[int] = Query(None, description="타겟 청크 ID"),
    relation_type: Optional[str] = Query(None, description="관계 타입"),
    db: Session = Depends(get_db)
):
    """관계 목록 조회"""
    query = db.query(KnowledgeRelation)
    
    if source_chunk_id:
        query = query.filter(KnowledgeRelation.source_chunk_id == source_chunk_id)
    if target_chunk_id:
        query = query.filter(KnowledgeRelation.target_chunk_id == target_chunk_id)
    if relation_type:
        query = query.filter(KnowledgeRelation.relation_type == relation_type)
    
    return query.all()


@router.get("/chunks/{chunk_id}/outgoing")
async def get_outgoing_relations(chunk_id: int, db: Session = Depends(get_db)):
    """청크의 나가는 관계 조회"""
    chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="청크를 찾을 수 없습니다")
    
    relations = db.query(KnowledgeRelation).filter(
        KnowledgeRelation.source_chunk_id == chunk_id
    ).all()
    
    result = []
    for rel in relations:
        target = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == rel.target_chunk_id).first()
        result.append({
            "id": rel.id,
            "target_chunk_id": rel.target_chunk_id,
            "target_content": target.content[:100] if target else "",
            "relation_type": rel.relation_type,
            "confidence": rel.confidence,
            "description": rel.description
        })
    
    return result


@router.get("/chunks/{chunk_id}/incoming")
async def get_incoming_relations(chunk_id: int, db: Session = Depends(get_db)):
    """청크의 들어오는 관계 조회"""
    chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="청크를 찾을 수 없습니다")
    
    relations = db.query(KnowledgeRelation).filter(
        KnowledgeRelation.target_chunk_id == chunk_id
    ).all()
    
    result = []
    for rel in relations:
        source = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == rel.source_chunk_id).first()
        result.append({
            "id": rel.id,
            "source_chunk_id": rel.source_chunk_id,
            "source_content": source.content[:100] if source else "",
            "relation_type": rel.relation_type,
            "confidence": rel.confidence,
            "description": rel.description
        })
    
    return result


@router.get("/{relation_id}", response_model=RelationResponse)
async def get_relation(
    relation_id: int,
    db: Session = Depends(get_db)
):
    """관계 상세 조회"""
    relation = db.query(KnowledgeRelation).filter(KnowledgeRelation.id == relation_id).first()
    if not relation:
        raise HTTPException(status_code=404, detail="관계를 찾을 수 없습니다")
    
    return RelationResponse(
        id=relation.id,
        source_chunk_id=relation.source_chunk_id,
        target_chunk_id=relation.target_chunk_id,
        relation_type=relation.relation_type,
        score=relation.score,
        description=relation.description,
        confirmed=relation.confirmed,
        source=relation.source
    )


@router.delete("/{relation_id}")
async def delete_relation(relation_id: int, db: Session = Depends(get_db)):
    """관계 삭제"""
    relation = db.query(KnowledgeRelation).filter(KnowledgeRelation.id == relation_id).first()
    if not relation:
        raise HTTPException(status_code=404, detail="관계를 찾을 수 없습니다")
    
    db.delete(relation)
    db.commit()
    return {"message": "관계가 삭제되었습니다"}

