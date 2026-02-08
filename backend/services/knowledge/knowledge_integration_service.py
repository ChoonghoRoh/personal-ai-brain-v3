"""지식 통합 및 세계관 구성 서비스"""
import logging
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from collections import defaultdict

from backend.models.models import KnowledgeChunk, KnowledgeRelation, Document
from backend.services.search.search_service import get_search_service
from backend.services.cognitive.context_service import ContextService

logger = logging.getLogger(__name__)


class KnowledgeIntegrationService:
    """지식 통합 및 세계관 구성 서비스 클래스"""
    
    def __init__(self):
        self.search_service = get_search_service()
        self.context_service = ContextService()
    
    def integrate_knowledge(
        self,
        db: Session,
        chunk_ids: List[int],
        strategy: str = "merge"  # merge, prioritize, resolve
    ) -> Dict:
        """지식 통합 알고리즘"""
        chunks = db.query(KnowledgeChunk).filter(
            KnowledgeChunk.id.in_(chunk_ids)
        ).all()
        
        if not chunks:
            return {"error": "청크를 찾을 수 없습니다"}
        
        # 청크 내용 통합
        integrated_content = []
        sources = []
        
        for chunk in chunks:
            integrated_content.append({
                "chunk_id": chunk.id,
                "content": chunk.content,
                "title": chunk.title,
                "document_id": chunk.document_id
            })
            
            # 문서 정보 추가
            doc = db.query(Document).filter(Document.id == chunk.document_id).first()
            if doc:
                sources.append({
                    "document_id": doc.id,
                    "file_path": doc.file_path
                })
        
        # 통합 전략 적용
        if strategy == "prioritize":
            # 승인된 청크 우선
            integrated_content.sort(
                key=lambda x: 1 if db.query(KnowledgeChunk).filter(
                    KnowledgeChunk.id == x["chunk_id"]
                ).first().status == "approved" else 0,
                reverse=True
            )
        elif strategy == "resolve":
            # 모순 해결 (간단한 버전)
            # 실제로는 더 정교한 모순 감지 필요
            pass
        
        return {
            "integrated_content": integrated_content,
            "sources": sources,
            "strategy": strategy,
            "total_chunks": len(chunks)
        }
    
    def detect_contradictions(
        self,
        db: Session,
        chunk_ids: List[int]
    ) -> List[Dict]:
        """모순 감지"""
        chunks = db.query(KnowledgeChunk).filter(
            KnowledgeChunk.id.in_(chunk_ids)
        ).all()
        
        contradictions = []
        
        # 간단한 키워드 기반 모순 감지
        for i, chunk1 in enumerate(chunks):
            for chunk2 in chunks[i+1:]:
                # 반대 키워드 체크
                content1_lower = chunk1.content.lower()
                content2_lower = chunk2.content.lower()
                
                opposite_pairs = [
                    ("중요", "불필요"),
                    ("필수", "선택"),
                    ("항상", "절대 안"),
                    ("맞다", "틀리다")
                ]
                
                for word1, word2 in opposite_pairs:
                    if word1 in content1_lower and word2 in content2_lower:
                        contradictions.append({
                            "chunk1_id": chunk1.id,
                            "chunk2_id": chunk2.id,
                            "type": "contradiction",
                            "severity": "medium",
                            "description": f"'{word1}'와 '{word2}' 키워드 모순"
                        })
        
        return contradictions
    
    def resolve_contradictions(
        self,
        contradictions: List[Dict],
        resolution_strategy: str = "prioritize_new"  # prioritize_new, prioritize_old, merge
    ) -> Dict:
        """모순 해결 전략"""
        resolved = []
        
        for contradiction in contradictions:
            if resolution_strategy == "prioritize_new":
                # 새로운 청크 우선
                resolved.append({
                    "contradiction": contradiction,
                    "resolution": "new_chunk_prioritized",
                    "kept_chunk_id": contradiction["chunk2_id"]
                })
            elif resolution_strategy == "prioritize_old":
                # 기존 청크 우선
                resolved.append({
                    "contradiction": contradiction,
                    "resolution": "old_chunk_prioritized",
                    "kept_chunk_id": contradiction["chunk1_id"]
                })
            elif resolution_strategy == "merge":
                # 병합 (간단한 버전)
                resolved.append({
                    "contradiction": contradiction,
                    "resolution": "merged",
                    "merged_chunk_ids": [contradiction["chunk1_id"], contradiction["chunk2_id"]]
                })
        
        return {
            "resolved_contradictions": resolved,
            "strategy": resolution_strategy,
            "total_resolved": len(resolved)
        }
    
    def build_worldview(
        self,
        db: Session,
        project_ids: Optional[List[int]] = None
    ) -> Dict:
        """세계관 구성"""
        query = db.query(KnowledgeChunk).filter(
            KnowledgeChunk.status == "approved"
        )
        
        if project_ids:
            query = query.join(Document).filter(Document.project_id.in_(project_ids))
        
        chunks = query.all()
        
        # 주제별 그룹화
        topics = defaultdict(list)
        for chunk in chunks:
            # 간단한 키워드 기반 주제 추출
            content_lower = chunk.content.lower()
            if "프로그래밍" in content_lower or "코드" in content_lower:
                topics["프로그래밍"].append(chunk.id)
            elif "데이터" in content_lower or "데이터베이스" in content_lower:
                topics["데이터"].append(chunk.id)
            elif "AI" in content_lower or "인공지능" in content_lower:
                topics["AI"].append(chunk.id)
            else:
                topics["기타"].append(chunk.id)
        
        return {
            "total_chunks": len(chunks),
            "topics": dict(topics),
            "created_at": datetime.utcnow().isoformat()
        }


def get_knowledge_integration_service() -> KnowledgeIntegrationService:
    """지식 통합 서비스 인스턴스 가져오기"""
    return KnowledgeIntegrationService()
