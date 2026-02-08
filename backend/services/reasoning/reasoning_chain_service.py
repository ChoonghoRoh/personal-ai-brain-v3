"""추론 체인 서비스"""
import logging
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from backend.models.models import KnowledgeChunk, KnowledgeRelation
from backend.services.search.search_service import get_search_service

logger = logging.getLogger(__name__)


class ReasoningChainService:
    """추론 체인 서비스 클래스"""
    
    def __init__(self):
        self.search_service = get_search_service()
    
    def build_reasoning_chain(
        self,
        db: Session,
        question: str,
        max_depth: int = 3,
        max_steps: int = 10
    ) -> Dict:
        """다단계 추론 체인 구축"""
        chain = {
            "question": question,
            "steps": [],
            "depth": 0,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # 1단계: 초기 검색
        try:
            search_results = self.search_service.search(
                query=question,
                top_k=5,
                offset=0,
                use_cache=False
            )
            initial_results = search_results.get("results", [])
        except Exception as e:
            logger.error(f"검색 오류: {e}")
            initial_results = []
        chain["steps"].append({
            "step": 1,
            "type": "initial_search",
            "results": [r.get("file") for r in initial_results],
            "count": len(initial_results)
        })
        
        # 2단계: 관계 추적
        if initial_results:
            first_result = initial_results[0]
            # Qdrant point ID로 청크 찾기
            chunk = db.query(KnowledgeChunk).filter(
                KnowledgeChunk.qdrant_point_id == str(first_result.get("document_id"))
            ).first()
            
            if chunk:
                # 관련 청크 찾기
                related_chunks = db.query(KnowledgeChunk).join(KnowledgeRelation).filter(
                    (KnowledgeRelation.source_chunk_id == chunk.id) |
                    (KnowledgeRelation.target_chunk_id == chunk.id)
                ).limit(5).all()
                
                chain["steps"].append({
                    "step": 2,
                    "type": "relation_tracking",
                    "related_chunks": [c.id for c in related_chunks],
                    "count": len(related_chunks)
                })
        
        # 3단계: 추가 검색 (관계 기반)
        if chain["steps"] and len(chain["steps"]) > 1:
            related_step = chain["steps"][1]
            if related_step.get("related_chunks"):
                # 관련 청크의 내용으로 추가 검색
                related_chunk = db.query(KnowledgeChunk).filter(
                    KnowledgeChunk.id == related_step["related_chunks"][0]
                ).first()
                
                if related_chunk:
                    try:
                        search_results = self.search_service.search(
                            query=related_chunk.content[:200],
                            top_k=3,
                            offset=0,
                            use_cache=False
                        )
                        follow_up_results = search_results.get("results", [])
                    except Exception as e:
                        logger.error(f"추가 검색 오류: {e}")
                        follow_up_results = []
                    
                    chain["steps"].append({
                        "step": 3,
                        "type": "follow_up_search",
                        "results": [r.get("file") for r in follow_up_results],
                        "count": len(follow_up_results)
                    })
        
        chain["depth"] = len(chain["steps"])
        return chain
    
    def visualize_reasoning_chain(
        self,
        chain: Dict
    ) -> Dict:
        """추론 체인 시각화 데이터"""
        nodes = []
        edges = []
        
        # 노드 생성
        question = chain.get("question", "Unknown question")
        nodes.append({
            "id": "question",
            "label": question[:50] if isinstance(question, str) else str(question)[:50],
            "type": "question"
        })
        
        steps = chain.get("steps", [])
        for i, step in enumerate(steps):
            step_num = step.get('step', i + 1)
            step_id = f"step_{step_num}"
            step_type = step.get('type', 'unknown')
            step_count = step.get('count', 0)
            
            nodes.append({
                "id": step_id,
                "label": f"{step_type} ({step_count})",
                "type": step_type
            })
            
            # 엣지 생성
            if i == 0:
                edges.append({
                    "from": "question",
                    "to": step_id
                })
            else:
                prev_step_num = steps[i-1].get('step', i)
                prev_step_id = f"step_{prev_step_num}"
                edges.append({
                    "from": prev_step_id,
                    "to": step_id
                })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "depth": chain.get("depth", len(steps)),
                "total_steps": len(steps)
            }
        }


def get_reasoning_chain_service() -> ReasoningChainService:
    """추론 체인 서비스 인스턴스 가져오기"""
    return ReasoningChainService()
