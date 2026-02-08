"""자동화 서비스"""
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.models.models import KnowledgeChunk, Label, KnowledgeLabel, KnowledgeRelation
from backend.services.search.search_service import get_search_service
from backend.services.cognitive.context_service import ContextService

logger = logging.getLogger(__name__)


class AutomationService:
    """자동화 서비스 클래스"""
    
    def __init__(self):
        self.search_service = get_search_service()
        self.context_service = ContextService()
    
    def auto_label_chunks(
        self,
        db: Session,
        chunk_ids: Optional[List[int]] = None,
        min_confidence: float = 0.7
    ) -> Dict:
        """청크 자동 라벨링"""
        labeled_count = 0
        
        # 대상 청크 조회
        query = db.query(KnowledgeChunk).filter(KnowledgeChunk.status == "approved")
        if chunk_ids:
            query = query.filter(KnowledgeChunk.id.in_(chunk_ids))
        
        chunks = query.all()
        all_labels = db.query(Label).all()
        
        for chunk in chunks:
            chunk_text_lower = chunk.content.lower()
            suggestions = []
            
            # 기존 라벨과 매칭
            for label in all_labels:
                label_name_lower = label.name.lower()
                
                # 키워드 매칭
                if label_name_lower in chunk_text_lower:
                    confidence = 0.8
                elif any(word in chunk_text_lower for word in label_name_lower.split("_")):
                    confidence = 0.6
                else:
                    continue
                
                if confidence >= min_confidence:
                    suggestions.append({
                        "label_id": label.id,
                        "confidence": confidence
                    })
            
            # 라벨 적용
            for suggestion in suggestions:
                existing = db.query(KnowledgeLabel).filter(
                    KnowledgeLabel.chunk_id == chunk.id,
                    KnowledgeLabel.label_id == suggestion["label_id"]
                ).first()
                
                if not existing:
                    knowledge_label = KnowledgeLabel(
                        chunk_id=chunk.id,
                        label_id=suggestion["label_id"],
                        confidence=suggestion["confidence"],
                        source="ai",
                        status="suggested"
                    )
                    db.add(knowledge_label)
                    labeled_count += 1
        
        db.commit()
        
        return {
            "labeled_count": labeled_count,
            "processed_chunks": len(chunks)
        }
    
    def auto_suggest_relations(
        self,
        db: Session,
        chunk_id: int,
        limit: int = 5
    ) -> List[Dict]:
        """자동 관계 추론"""
        chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == chunk_id).first()
        if not chunk:
            return []
        
        # 의미적 유사도 기반 관계 추천
        try:
            # 검색 서비스를 사용하여 유사 청크 찾기
            search_results = self.search_service.search_simple(
                chunk.content[:200],  # 청크 내용의 일부로 검색
                top_k=limit + 1  # 자기 자신 제외
            )
            
            suggestions = []
            for result in search_results:
                # 자기 자신 제외
                if result.get('document_id') == chunk.qdrant_point_id:
                    continue
                
                # 타겟 청크 찾기
                target_chunk = db.query(KnowledgeChunk).filter(
                    KnowledgeChunk.qdrant_point_id == str(result.get('document_id'))
                ).first()
                
                if target_chunk and target_chunk.id != chunk_id:
                    # 기존 관계 확인
                    existing = db.query(KnowledgeRelation).filter(
                        KnowledgeRelation.source_chunk_id == chunk_id,
                        KnowledgeRelation.target_chunk_id == target_chunk.id
                    ).first()
                    
                    if not existing:
                        suggestions.append({
                            "target_chunk_id": target_chunk.id,
                            "target_content_preview": target_chunk.content[:100],
                            "relation_type": "similar",
                            "score": result.get('score', 0.7)
                        })
            
            return suggestions[:limit]
        except Exception as e:
            logger.error(f"자동 관계 추론 실패: {e}")
            return []
    
    def batch_auto_label(
        self,
        db: Session,
        batch_size: int = 100,
        min_confidence: float = 0.7
    ) -> Dict:
        """배치 자동 라벨링"""
        total_labeled = 0
        processed = 0
        
        # 승인된 청크 중 라벨이 없는 청크 대상
        chunks = db.query(KnowledgeChunk).filter(
            KnowledgeChunk.status == "approved"
        ).limit(batch_size).all()
        
        for chunk in chunks:
            # 이미 라벨이 있는지 확인
            existing_labels = db.query(KnowledgeLabel).filter(
                KnowledgeLabel.chunk_id == chunk.id
            ).count()
            
            if existing_labels == 0:
                result = self.auto_label_chunks(db, [chunk.id], min_confidence)
                total_labeled += result["labeled_count"]
            
            processed += 1
        
        return {
            "processed": processed,
            "labeled": total_labeled
        }


def get_automation_service() -> AutomationService:
    """자동화 서비스 인스턴스 가져오기"""
    return AutomationService()
