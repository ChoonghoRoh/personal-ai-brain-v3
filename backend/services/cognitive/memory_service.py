"""기억 시스템 서비스"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from backend.models.models import Memory, KnowledgeChunk


class MemoryService:
    """기억 시스템 서비스 클래스"""
    
    MEMORY_TYPES = {
        'long_term': '장기 기억',
        'short_term': '단기 기억',
        'working': '작업 기억'
    }
    
    def __init__(self):
        pass
    
    def create_memory(
        self,
        db: Session,
        memory_type: str,
        content: str,
        importance_score: float = 0.5,
        category: Optional[str] = None,
        related_chunk_id: Optional[int] = None,
        metadata: Optional[Dict] = None,
        expires_in_hours: Optional[int] = None
    ) -> Memory:
        """기억 생성"""
        if memory_type not in self.MEMORY_TYPES:
            raise ValueError(f"Invalid memory type: {memory_type}")
        
        # 만료 시간 설정 (단기 기억의 경우)
        expires_at = None
        if memory_type == 'short_term' and expires_in_hours:
            expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
        elif memory_type == 'short_term':
            # 기본 24시간
            expires_at = datetime.utcnow() + timedelta(hours=24)
        
        # 메타데이터 JSON 변환
        metadata_str = None
        if metadata:
            import json
            metadata_str = json.dumps(metadata)
        
        memory = Memory(
            memory_type=memory_type,
            content=content,
            importance_score=importance_score,
            category=category,
            related_chunk_id=related_chunk_id,
            meta_data=metadata_str,
            expires_at=expires_at
        )
        
        db.add(memory)
        db.commit()
        db.refresh(memory)
        
        return memory
    
    def get_long_term_memories(
        self,
        db: Session,
        category: Optional[str] = None,
        limit: int = 50
    ) -> List[Memory]:
        """장기 기억 조회 (핵심 지식, 원칙, 가치관)"""
        query = db.query(Memory).filter(
            Memory.memory_type == 'long_term'
        )
        
        if category:
            query = query.filter(Memory.category == category)
        
        # 중요도 순으로 정렬
        memories = query.order_by(Memory.importance_score.desc()).limit(limit).all()
        
        # 접근 정보 업데이트
        for memory in memories:
            memory.access_count += 1
            memory.last_accessed_at = datetime.utcnow()
        
        db.commit()
        
        return memories
    
    def get_short_term_memories(
        self,
        db: Session,
        limit: int = 20
    ) -> List[Memory]:
        """단기 기억 조회 (최근 대화, 작업 컨텍스트)"""
        # 만료되지 않은 단기 기억만 조회
        now = datetime.utcnow()
        memories = db.query(Memory).filter(
            and_(
                Memory.memory_type == 'short_term',
                or_(
                    Memory.expires_at.is_(None),
                    Memory.expires_at > now
                )
            )
        ).order_by(Memory.created_at.desc()).limit(limit).all()
        
        # 접근 정보 업데이트
        for memory in memories:
            memory.access_count += 1
            memory.last_accessed_at = datetime.utcnow()
        
        db.commit()
        
        return memories
    
    def get_working_memories(
        self,
        db: Session,
        limit: int = 10
    ) -> List[Memory]:
        """작업 기억 조회 (현재 추론 중인 정보)"""
        # 작업 기억은 최신순으로 조회
        memories = db.query(Memory).filter(
            Memory.memory_type == 'working'
        ).order_by(Memory.created_at.desc()).limit(limit).all()
        
        return memories
    
    def search_memories(
        self,
        db: Session,
        query: str,
        memory_types: Optional[List[str]] = None,
        limit: int = 20
    ) -> List[Memory]:
        """기억 검색"""
        search_query = db.query(Memory).filter(
            Memory.content.ilike(f"%{query}%")
        )
        
        if memory_types:
            search_query = search_query.filter(Memory.memory_type.in_(memory_types))
        
        # 중요도 및 최근 접근 순으로 정렬
        memories = search_query.order_by(
            Memory.importance_score.desc(),
            Memory.last_accessed_at.desc()
        ).limit(limit).all()
        
        # 접근 정보 업데이트
        for memory in memories:
            memory.access_count += 1
            memory.last_accessed_at = datetime.utcnow()
        
        db.commit()
        
        return memories
    
    def update_importance(
        self,
        db: Session,
        memory_id: int,
        importance_score: float
    ) -> Memory:
        """기억 중요도 업데이트"""
        memory = db.query(Memory).filter(Memory.id == memory_id).first()
        if not memory:
            raise ValueError(f"Memory not found: {memory_id}")
        
        memory.importance_score = max(0.0, min(1.0, importance_score))
        memory.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(memory)
        
        return memory
    
    def delete_expired_memories(
        self,
        db: Session
    ) -> int:
        """만료된 단기 기억 삭제"""
        now = datetime.utcnow()
        expired = db.query(Memory).filter(
            and_(
                Memory.memory_type == 'short_term',
                Memory.expires_at.isnot(None),
                Memory.expires_at <= now
            )
        ).all()
        
        count = len(expired)
        for memory in expired:
            db.delete(memory)
        
        db.commit()
        
        return count
    
    def promote_to_long_term(
        self,
        db: Session,
        memory_id: int,
        importance_score: float = 0.7
    ) -> Memory:
        """단기 기억을 장기 기억으로 승격"""
        memory = db.query(Memory).filter(Memory.id == memory_id).first()
        if not memory:
            raise ValueError(f"Memory not found: {memory_id}")
        
        memory.memory_type = 'long_term'
        memory.importance_score = importance_score
        memory.expires_at = None  # 장기 기억은 만료 없음
        memory.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(memory)
        
        return memory


# 싱글톤 인스턴스
_memory_service = None

def get_memory_service() -> MemoryService:
    """기억 서비스 인스턴스 가져오기"""
    global _memory_service
    if _memory_service is None:
        _memory_service = MemoryService()
    return _memory_service
