"""인격 유지 서비스"""
import logging
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import json

from backend.models.models import Memory

logger = logging.getLogger(__name__)


class PersonalityService:
    """인격 유지 서비스 클래스"""
    
    def __init__(self):
        self.personality_profile = {
            "principles": [],
            "values": [],
            "preferences": [],
            "communication_style": "professional"
        }
        self.contradictions = []
    
    def define_personality_profile(
        self,
        principles: List[str],
        values: List[str],
        preferences: List[str],
        communication_style: str = "professional"
    ) -> Dict:
        """인격 프로필 정의"""
        self.personality_profile = {
            "principles": principles,
            "values": values,
            "preferences": preferences,
            "communication_style": communication_style,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        return self.personality_profile
    
    def get_personality_profile(self) -> Dict:
        """인격 프로필 조회"""
        return self.personality_profile
    
    def detect_contradictions(
        self,
        db: Session,
        new_content: str
    ) -> List[Dict]:
        """모순 감지"""
        contradictions = []
        
        # 장기 기억에서 원칙과 가치관 조회
        principles = db.query(Memory).filter(
            Memory.memory_type == "long_term",
            Memory.category == "principle"
        ).all()
        
        values = db.query(Memory).filter(
            Memory.memory_type == "long_term",
            Memory.category == "value"
        ).all()
        
        # 새 내용과 기존 원칙/가치관 비교
        for principle in principles:
            # 간단한 키워드 기반 모순 감지
            principle_content = principle.content.lower()
            new_content_lower = new_content.lower()
            
            # 반대 키워드 체크 (간단한 예시)
            opposite_keywords = {
                "중요": ["무시", "경시"],
                "필수": ["선택", "불필요"],
                "항상": ["절대 안", "금지"]
            }
            
            for key, opposites in opposite_keywords.items():
                if key in principle_content:
                    for opposite in opposites:
                        if opposite in new_content_lower:
                            contradictions.append({
                                "type": "principle_contradiction",
                                "principle_id": principle.id,
                                "principle_content": principle.content,
                                "contradicting_content": new_content,
                                "severity": "high"
                            })
        
        self.contradictions = contradictions
        return contradictions
    
    def resolve_contradiction(
        self,
        contradiction_id: int,
        resolution: str,
        priority: str = "new"  # new, existing
    ) -> Dict:
        """모순 해결"""
        if contradiction_id < len(self.contradictions):
            contradiction = self.contradictions[contradiction_id]
            contradiction["resolved"] = True
            contradiction["resolution"] = resolution
            contradiction["priority"] = priority
            contradiction["resolved_at"] = datetime.utcnow().isoformat()
            
            return contradiction
        
        return {"error": "모순을 찾을 수 없습니다"}


def get_personality_service() -> PersonalityService:
    """인격 서비스 인스턴스 가져오기"""
    return PersonalityService()
