"""학습 및 적응 서비스"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from collections import defaultdict

from backend.models.models import KnowledgeChunk, KnowledgeLabel, Label, Conversation, Memory

logger = logging.getLogger(__name__)


class LearningService:
    """학습 및 적응 서비스 클래스"""
    
    def __init__(self):
        self.user_patterns = {}
        self.feedback_history = []
    
    def learn_user_patterns(
        self,
        db: Session,
        days: int = 30
    ) -> Dict:
        """사용자 패턴 학습"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # 최근 대화 기록 분석
        conversations = db.query(Conversation).filter(
            Conversation.created_at >= cutoff_date
        ).all()
        
        # 질문 패턴 분석
        question_patterns = defaultdict(int)
        for conv in conversations:
            # 질문의 첫 단어나 키워드 추출
            words = conv.question.split()[:3]  # 처음 3개 단어
            pattern = " ".join(words)
            question_patterns[pattern] += 1
        
        # 라벨 사용 패턴 분석
        label_usage = defaultdict(int)
        recent_labels = db.query(KnowledgeLabel).join(KnowledgeChunk).filter(
            KnowledgeChunk.created_at >= cutoff_date
        ).all()
        
        for kl in recent_labels:
            label_usage[kl.label_id] += 1
        
        # 패턴 저장
        patterns = {
            "question_patterns": dict(question_patterns),
            "label_usage": dict(label_usage),
            "total_conversations": len(conversations),
            "analysis_date": datetime.utcnow().isoformat()
        }
        
        self.user_patterns = patterns
        return patterns
    
    def record_feedback(
        self,
        feedback_type: str,
        item_id: int,
        rating: float,
        comment: Optional[str] = None
    ):
        """피드백 기록"""
        feedback = {
            "type": feedback_type,  # label, relation, answer, etc.
            "item_id": item_id,
            "rating": rating,  # 0.0 - 1.0
            "comment": comment,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.feedback_history.append(feedback)
        
        # 최근 1000개만 유지
        if len(self.feedback_history) > 1000:
            self.feedback_history = self.feedback_history[-1000:]
        
        return feedback
    
    def get_feedback_stats(self) -> Dict:
        """피드백 통계"""
        if not self.feedback_history:
            return {
                "total_feedback": 0,
                "average_rating": 0.0,
                "by_type": {}
            }
        
        total = len(self.feedback_history)
        total_rating = sum(f["rating"] for f in self.feedback_history)
        avg_rating = total_rating / total if total > 0 else 0.0
        
        # 타입별 통계
        by_type = defaultdict(lambda: {"count": 0, "total_rating": 0.0})
        for feedback in self.feedback_history:
            ftype = feedback["type"]
            by_type[ftype]["count"] += 1
            by_type[ftype]["total_rating"] += feedback["rating"]
        
        for ftype in by_type:
            count = by_type[ftype]["count"]
            by_type[ftype]["average_rating"] = by_type[ftype]["total_rating"] / count if count > 0 else 0.0
            del by_type[ftype]["total_rating"]
        
        return {
            "total_feedback": total,
            "average_rating": avg_rating,
            "by_type": dict(by_type)
        }
    
    def improve_based_on_feedback(
        self,
        db: Session
    ) -> Dict:
        """피드백 기반 개선"""
        improvements = []
        
        # 낮은 평점 피드백 분석
        low_rating_feedback = [f for f in self.feedback_history if f["rating"] < 0.5]
        
        for feedback in low_rating_feedback:
            if feedback["type"] == "label":
                # 라벨 관련 피드백 처리
                improvements.append({
                    "type": "label_improvement",
                    "item_id": feedback["item_id"],
                    "suggestion": "라벨 신뢰도 조정 필요"
                })
            elif feedback["type"] == "answer":
                # 답변 관련 피드백 처리
                improvements.append({
                    "type": "answer_improvement",
                    "item_id": feedback["item_id"],
                    "suggestion": "답변 품질 개선 필요"
                })
        
        return {
            "improvements": improvements,
            "total_low_rating": len(low_rating_feedback)
        }


def get_learning_service() -> LearningService:
    """학습 서비스 인스턴스 가져오기"""
    return LearningService()
