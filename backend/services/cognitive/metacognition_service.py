"""메타 인지 서비스"""
import logging
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import math

from backend.models.models import KnowledgeChunk, KnowledgeLabel, KnowledgeRelation

logger = logging.getLogger(__name__)


class MetacognitionService:
    """메타 인지 서비스 클래스"""
    
    def __init__(self):
        pass
    
    def calculate_confidence_score(
        self,
        db: Session,
        chunk_id: int
    ) -> float:
        """청크 신뢰도 점수 계산"""
        chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == chunk_id).first()
        if not chunk:
            return 0.0
        
        confidence_factors = []
        
        # 1. 라벨 수 (더 많은 라벨 = 더 높은 신뢰도)
        label_count = db.query(KnowledgeLabel).filter(
            KnowledgeLabel.chunk_id == chunk_id,
            KnowledgeLabel.status == "confirmed"
        ).count()
        label_score = min(label_count / 5.0, 1.0)  # 최대 5개 라벨 기준
        confidence_factors.append(label_score * 0.3)
        
        # 2. 관계 수 (더 많은 관계 = 더 높은 신뢰도)
        relation_count = db.query(KnowledgeRelation).filter(
            (KnowledgeRelation.source_chunk_id == chunk_id) |
            (KnowledgeRelation.target_chunk_id == chunk_id),
            KnowledgeRelation.confirmed == "true"
        ).count()
        relation_score = min(relation_count / 10.0, 1.0)  # 최대 10개 관계 기준
        confidence_factors.append(relation_score * 0.3)
        
        # 3. 승인 상태
        if chunk.status == "approved":
            approval_score = 1.0
        elif chunk.status == "draft":
            approval_score = 0.5
        else:
            approval_score = 0.0
        confidence_factors.append(approval_score * 0.4)
        
        # 최종 신뢰도 점수 (0.0 - 1.0)
        total_confidence = sum(confidence_factors)
        return min(max(total_confidence, 0.0), 1.0)
    
    def indicate_uncertainty(
        self,
        db: Session,
        chunk_id: int,
        threshold: float = 0.5
    ) -> Dict:
        """지식 불확실성 표시"""
        confidence = self.calculate_confidence_score(db, chunk_id)
        
        uncertainty_level = "low"
        if confidence < threshold:
            if confidence < 0.3:
                uncertainty_level = "high"
            else:
                uncertainty_level = "medium"
        
        return {
            "chunk_id": chunk_id,
            "confidence_score": confidence,
            "uncertainty_level": uncertainty_level,
            "is_uncertain": confidence < threshold
        }
    
    def get_knowledge_uncertainty_map(
        self,
        db: Session,
        chunk_ids: Optional[List[int]] = None
    ) -> Dict:
        """지식 불확실성 맵"""
        query = db.query(KnowledgeChunk)
        if chunk_ids:
            query = query.filter(KnowledgeChunk.id.in_(chunk_ids))
        
        chunks = query.all()
        
        uncertainty_map = {}
        for chunk in chunks:
            uncertainty = self.indicate_uncertainty(db, chunk.id)
            uncertainty_map[chunk.id] = uncertainty
        
        return {
            "uncertainty_map": uncertainty_map,
            "total_chunks": len(chunks),
            "high_uncertainty_count": sum(
                1 for u in uncertainty_map.values() 
                if u["uncertainty_level"] == "high"
            )
        }


def get_metacognition_service() -> MetacognitionService:
    """메타 인지 서비스 인스턴스 가져오기"""
    return MetacognitionService()
