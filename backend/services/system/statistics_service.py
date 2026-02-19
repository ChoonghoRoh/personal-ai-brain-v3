"""통계 서비스

Phase 9-4-2: 통계/분석 대시보드
- 문서, 청크, 라벨 통계
- 사용량 통계
- 시스템 상태
- 트렌드 데이터
"""

import logging
import math
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy import func, and_, distinct
from sqlalchemy.orm import Session

from backend.models.models import (
    Document, KnowledgeChunk, Label, KnowledgeLabel,
    KnowledgeRelation, Project, ReasoningResult
)
from backend.models.admin_models import PageAccessLog

logger = logging.getLogger(__name__)


class StatisticsService:
    """통계 수집 및 분석 서비스"""

    def __init__(self, db: Session):
        self.db = db

    def get_summary(self) -> Dict[str, Any]:
        """전체 통계 요약"""
        return {
            "total_documents": self._count_documents(),
            "total_chunks": self._count_chunks(),
            "total_labels": self._count_labels(),
            "total_projects": self._count_projects(),
            "total_relations": self._count_relations(),
            "approved_chunks": self._count_chunks_by_status("approved"),
            "pending_chunks": self._count_chunks_by_status("pending"),
        }

    def get_document_statistics(self) -> Dict[str, Any]:
        """문서 상세 통계"""
        return {
            "total": self._count_documents(),
            "by_type": self._documents_by_type(),
            "by_project": self._documents_by_project(),
            "recent": self._recent_documents(days=7),
        }

    def get_knowledge_statistics(self) -> Dict[str, Any]:
        """지식(청크/라벨) 상세 통계"""
        return {
            "chunks": {
                "total": self._count_chunks(),
                "by_status": self._chunks_by_status(),
                "by_project": self._chunks_by_project(),
                "average_per_document": self._average_chunks_per_document(),
            },
            "labels": {
                "total": self._count_labels(),
                "by_type": self._labels_by_type(),
                "top_used": self._top_used_labels(limit=10),
            },
            "relations": {
                "total": self._count_relations(),
                "by_type": self._relations_by_type(),
            }
        }

    def get_usage_statistics(self) -> Dict[str, Any]:
        """사용량 통계"""
        today = datetime.utcnow().date()
        week_ago = today - timedelta(days=7)

        return {
            "reasoning": {
                "total": self._count_reasoning_results(),
                "today": self._count_reasoning_by_date(today),
                "this_week": self._count_reasoning_since(week_ago),
                "by_mode": self._reasoning_by_mode(),
            },
            # 검색, AI 질의 등은 별도 로깅 테이블 필요 (현재는 미구현)
            "note": "Search and ask statistics require usage logging table"
        }

    def get_system_statistics(self) -> Dict[str, Any]:
        """시스템 상태 통계"""
        result = {
            "database": self._get_database_stats(),
            "qdrant": self._get_qdrant_stats(),
        }
        try:
            from backend.services.system.system_service import get_system_service
            sys_svc = get_system_service()
            ollama_info = sys_svc._get_ollama_status(run_test=False)
            result["ollama"] = {
                "status": ollama_info.get("status", "unknown"),
                "model_name": ollama_info.get("model_name"),
                "models": ollama_info.get("models", []),
            }
        except Exception as e:
            logger.error(f"Ollama 상태 확인 실패: {e}")
            result["ollama"] = {"status": "error"}
        return result

    def get_trends(self, days: int = 7) -> Dict[str, Any]:
        """트렌드 데이터 (일별)"""
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days - 1)

        trends = []
        current_date = start_date

        while current_date <= end_date:
            daily_stats = {
                "date": current_date.isoformat(),
                "documents": self._count_documents_by_date(current_date),
                "chunks": self._count_chunks_by_date(current_date),
                "reasoning": self._count_reasoning_by_date(current_date),
            }
            trends.append(daily_stats)
            current_date += timedelta(days=1)

        return {
            "period": f"{days}d",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "data": trends
        }

    def get_page_access_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """페이지 접근 로그 조회 (Phase 13-4-1)"""
        try:
            results = self.db.query(PageAccessLog).order_by(
                PageAccessLog.accessed_at.desc()
            ).limit(limit).all()

            return [
                {
                    "id": log.id,
                    "path": log.path,
                    "method": log.method,
                    "status_code": log.status_code,
                    "response_time_ms": log.response_time_ms,
                    "user_agent": log.user_agent,
                    "ip_address": log.ip_address,
                    "accessed_at": log.accessed_at.isoformat() if log.accessed_at else None
                }
                for log in results
            ]
        except Exception as e:
            logger.error(f"페이지 접근 로그 조회 실패: {e}")
            return []

    # ================== List Methods (Phase 17-5) ==================

    def list_documents(self, page: int = 1, size: int = 20, file_type: Optional[str] = None,
                       q: Optional[str] = None, sort_by: str = "created_at", sort_order: str = "desc") -> Dict[str, Any]:
        """문서 목록 (페이지네이션 + 필터)"""
        try:
            query = self.db.query(Document)
            if file_type:
                query = query.filter(Document.file_type == file_type)
            if q and q.strip():
                term = f"%{q.strip()}%"
                query = query.filter(Document.file_name.ilike(term))

            total = query.count()

            # 정렬
            sort_col = getattr(Document, sort_by, Document.created_at)
            if sort_order == "asc":
                query = query.order_by(sort_col.asc())
            else:
                query = query.order_by(sort_col.desc())

            offset = (page - 1) * size
            items = query.offset(offset).limit(size).all()

            return {
                "items": [
                    {
                        "id": d.id,
                        "file_name": d.file_name,
                        "file_type": d.file_type,
                        "file_path": d.file_path,
                        "project_id": d.project_id,
                        "created_at": d.created_at.isoformat() if d.created_at else None,
                    }
                    for d in items
                ],
                "total": total,
                "page": page,
                "size": size,
                "total_pages": math.ceil(total / size) if total > 0 else 1,
            }
        except Exception as e:
            logger.error("문서 목록 조회 실패: %s", e)
            return {"items": [], "total": 0, "page": page, "size": size, "total_pages": 1}

    def list_chunks(self, page: int = 1, size: int = 20, status: Optional[str] = None,
                    q: Optional[str] = None, sort_by: str = "created_at", sort_order: str = "desc") -> Dict[str, Any]:
        """청크 목록 (페이지네이션 + 필터)"""
        try:
            query = self.db.query(KnowledgeChunk)
            if status:
                query = query.filter(KnowledgeChunk.status == status)
            if q and q.strip():
                term = f"%{q.strip()}%"
                query = query.filter(KnowledgeChunk.content.ilike(term))

            total = query.count()

            sort_col = getattr(KnowledgeChunk, sort_by, KnowledgeChunk.created_at)
            if sort_order == "asc":
                query = query.order_by(sort_col.asc())
            else:
                query = query.order_by(sort_col.desc())

            offset = (page - 1) * size
            items = query.offset(offset).limit(size).all()

            return {
                "items": [
                    {
                        "id": c.id,
                        "content": (c.content[:100] + "...") if c.content and len(c.content) > 100 else c.content,
                        "status": c.status,
                        "document_id": c.document_id,
                        "created_at": c.created_at.isoformat() if c.created_at else None,
                    }
                    for c in items
                ],
                "total": total,
                "page": page,
                "size": size,
                "total_pages": math.ceil(total / size) if total > 0 else 1,
            }
        except Exception as e:
            logger.error("청크 목록 조회 실패: %s", e)
            return {"items": [], "total": 0, "page": page, "size": size, "total_pages": 1}

    def list_labels(self, page: int = 1, size: int = 20, label_type: Optional[str] = None,
                    q: Optional[str] = None, sort_by: str = "name", sort_order: str = "asc") -> Dict[str, Any]:
        """라벨 목록 (페이지네이션 + 필터)"""
        try:
            query = self.db.query(
                Label.id, Label.name, Label.label_type,
                func.count(KnowledgeLabel.chunk_id).label("usage_count")
            ).outerjoin(KnowledgeLabel, KnowledgeLabel.label_id == Label.id
            ).group_by(Label.id, Label.name, Label.label_type)

            if label_type:
                query = query.filter(Label.label_type == label_type)
            if q and q.strip():
                term = f"%{q.strip()}%"
                query = query.filter(Label.name.ilike(term))

            # Count before pagination (subquery)
            count_query = self.db.query(Label)
            if label_type:
                count_query = count_query.filter(Label.label_type == label_type)
            if q and q.strip():
                count_query = count_query.filter(Label.name.ilike(f"%{q.strip()}%"))
            total = count_query.count()

            # 정렬
            if sort_by == "usage_count":
                if sort_order == "asc":
                    query = query.order_by(func.count(KnowledgeLabel.chunk_id).asc())
                else:
                    query = query.order_by(func.count(KnowledgeLabel.chunk_id).desc())
            else:
                sort_col = getattr(Label, sort_by, Label.name)
                if sort_order == "asc":
                    query = query.order_by(sort_col.asc())
                else:
                    query = query.order_by(sort_col.desc())

            offset = (page - 1) * size
            items = query.offset(offset).limit(size).all()

            return {
                "items": [
                    {
                        "id": lid,
                        "name": name,
                        "label_type": ltype,
                        "usage_count": usage,
                    }
                    for lid, name, ltype, usage in items
                ],
                "total": total,
                "page": page,
                "size": size,
                "total_pages": math.ceil(total / size) if total > 0 else 1,
            }
        except Exception as e:
            logger.error("라벨 목록 조회 실패: %s", e)
            return {"items": [], "total": 0, "page": page, "size": size, "total_pages": 1}

    def list_reasoning_results(self, page: int = 1, size: int = 20, mode: Optional[str] = None,
                               from_date: Optional[str] = None, to_date: Optional[str] = None,
                               sort_by: str = "created_at", sort_order: str = "desc") -> Dict[str, Any]:
        """추론 결과 목록 (페이지네이션 + 필터)"""
        try:
            query = self.db.query(ReasoningResult).filter(
                ReasoningResult.question != "",
                ReasoningResult.question.isnot(None),
            )
            if mode:
                query = query.filter(ReasoningResult.mode == mode)
            if from_date:
                query = query.filter(ReasoningResult.created_at >= datetime.fromisoformat(from_date))
            if to_date:
                to_dt = datetime.fromisoformat(to_date) + timedelta(days=1)
                query = query.filter(ReasoningResult.created_at < to_dt)

            total = query.count()

            sort_col = getattr(ReasoningResult, sort_by, ReasoningResult.created_at)
            if sort_order == "asc":
                query = query.order_by(sort_col.asc())
            else:
                query = query.order_by(sort_col.desc())

            offset = (page - 1) * size
            items = query.offset(offset).limit(size).all()

            return {
                "items": [
                    {
                        "id": r.id,
                        "question": (r.question[:80] + "...") if r.question and len(r.question) > 80 else r.question,
                        "mode": r.mode,
                        "summary": r.summary,
                        "created_at": r.created_at.isoformat() if r.created_at else None,
                    }
                    for r in items
                ],
                "total": total,
                "page": page,
                "size": size,
                "total_pages": math.ceil(total / size) if total > 0 else 1,
            }
        except Exception as e:
            logger.error("추론 결과 목록 조회 실패: %s", e)
            return {"items": [], "total": 0, "page": page, "size": size, "total_pages": 1}

    # ================== Private Methods ==================

    def _count_documents(self) -> int:
        """총 문서 수"""
        try:
            return self.db.query(func.count(Document.id)).scalar() or 0
        except Exception as e:
            logger.error(f"문서 수 조회 실패: {e}")
            return 0

    def _count_chunks(self) -> int:
        """총 청크 수"""
        try:
            return self.db.query(func.count(KnowledgeChunk.id)).scalar() or 0
        except Exception as e:
            logger.error(f"청크 수 조회 실패: {e}")
            return 0

    def _count_chunks_by_status(self, status: str) -> int:
        """상태별 청크 수"""
        try:
            return self.db.query(func.count(KnowledgeChunk.id)).filter(
                KnowledgeChunk.status == status
            ).scalar() or 0
        except Exception as e:
            logger.error(f"상태별 청크 수 조회 실패: {e}")
            return 0

    def _count_labels(self) -> int:
        """총 라벨 수"""
        try:
            return self.db.query(func.count(Label.id)).scalar() or 0
        except Exception as e:
            logger.error(f"라벨 수 조회 실패: {e}")
            return 0

    def _count_projects(self) -> int:
        """총 프로젝트 수"""
        try:
            return self.db.query(func.count(Project.id)).scalar() or 0
        except Exception as e:
            logger.error(f"프로젝트 수 조회 실패: {e}")
            return 0

    def _count_relations(self) -> int:
        """총 관계 수"""
        try:
            return self.db.query(func.count(KnowledgeRelation.id)).scalar() or 0
        except Exception as e:
            logger.error(f"관계 수 조회 실패: {e}")
            return 0

    def _documents_by_type(self) -> Dict[str, int]:
        """파일 유형별 문서 수"""
        try:
            results = self.db.query(
                Document.file_type,
                func.count(Document.id)
            ).group_by(Document.file_type).all()

            return {
                (file_type or "unknown"): count
                for file_type, count in results
            }
        except Exception as e:
            logger.error(f"유형별 문서 수 조회 실패: {e}")
            return {}

    def _documents_by_project(self) -> List[Dict[str, Any]]:
        """프로젝트별 문서 수"""
        try:
            results = self.db.query(
                Project.id,
                Project.name,
                func.count(Document.id).label('count')
            ).outerjoin(Document, Document.project_id == Project.id
            ).group_by(Project.id, Project.name).all()

            return [
                {"project_id": pid, "project_name": name, "count": count}
                for pid, name, count in results
            ]
        except Exception as e:
            logger.error(f"프로젝트별 문서 수 조회 실패: {e}")
            return []

    def _recent_documents(self, days: int = 7) -> int:
        """최근 N일간 추가된 문서 수"""
        try:
            since = datetime.utcnow() - timedelta(days=days)
            return self.db.query(func.count(Document.id)).filter(
                Document.created_at >= since
            ).scalar() or 0
        except Exception as e:
            logger.error(f"최근 문서 수 조회 실패: {e}")
            return 0

    def _chunks_by_status(self) -> Dict[str, int]:
        """상태별 청크 수"""
        try:
            results = self.db.query(
                KnowledgeChunk.status,
                func.count(KnowledgeChunk.id)
            ).group_by(KnowledgeChunk.status).all()

            return {
                (status or "unknown"): count
                for status, count in results
            }
        except Exception as e:
            logger.error(f"상태별 청크 수 조회 실패: {e}")
            return {}

    def _chunks_by_project(self) -> List[Dict[str, Any]]:
        """프로젝트별 청크 수"""
        try:
            results = self.db.query(
                Project.id,
                Project.name,
                func.count(KnowledgeChunk.id).label('count')
            ).outerjoin(Document, Document.project_id == Project.id
            ).outerjoin(KnowledgeChunk, KnowledgeChunk.document_id == Document.id
            ).group_by(Project.id, Project.name).all()

            return [
                {"project_id": pid, "project_name": name, "count": count or 0}
                for pid, name, count in results
            ]
        except Exception as e:
            logger.error(f"프로젝트별 청크 수 조회 실패: {e}")
            return []

    def _average_chunks_per_document(self) -> float:
        """문서당 평균 청크 수"""
        try:
            doc_count = self._count_documents()
            chunk_count = self._count_chunks()

            if doc_count == 0:
                return 0.0

            return round(chunk_count / doc_count, 2)
        except Exception as e:
            logger.error(f"평균 청크 수 계산 실패: {e}")
            return 0.0

    def _labels_by_type(self) -> Dict[str, int]:
        """유형별 라벨 수"""
        try:
            results = self.db.query(
                Label.label_type,
                func.count(Label.id)
            ).group_by(Label.label_type).all()

            return {
                (label_type or "unknown"): count
                for label_type, count in results
            }
        except Exception as e:
            logger.error(f"유형별 라벨 수 조회 실패: {e}")
            return {}

    def _top_used_labels(self, limit: int = 10) -> List[Dict[str, Any]]:
        """가장 많이 사용된 라벨 TOP N"""
        try:
            results = self.db.query(
                Label.id,
                Label.name,
                Label.label_type,
                func.count(KnowledgeLabel.chunk_id).label('usage_count')
            ).join(KnowledgeLabel, KnowledgeLabel.label_id == Label.id
            ).group_by(Label.id, Label.name, Label.label_type
            ).order_by(func.count(KnowledgeLabel.chunk_id).desc()
            ).limit(limit).all()

            return [
                {
                    "label_id": lid,
                    "name": name,
                    "type": label_type,
                    "usage_count": count
                }
                for lid, name, label_type, count in results
            ]
        except Exception as e:
            logger.error(f"인기 라벨 조회 실패: {e}")
            return []

    def _relations_by_type(self) -> Dict[str, int]:
        """관계 유형별 수"""
        try:
            results = self.db.query(
                KnowledgeRelation.relation_type,
                func.count(KnowledgeRelation.id)
            ).group_by(KnowledgeRelation.relation_type).all()

            return {
                (rel_type or "unknown"): count
                for rel_type, count in results
            }
        except Exception as e:
            logger.error(f"관계 유형별 수 조회 실패: {e}")
            return {}

    def _count_reasoning_results(self) -> int:
        """총 추론 결과 수"""
        try:
            return self.db.query(func.count(ReasoningResult.id)).scalar() or 0
        except Exception as e:
            logger.error(f"추론 결과 수 조회 실패: {e}")
            return 0

    def _count_reasoning_by_date(self, date: datetime.date) -> int:
        """특정 날짜의 추론 수"""
        try:
            start = datetime.combine(date, datetime.min.time())
            end = datetime.combine(date, datetime.max.time())

            return self.db.query(func.count(ReasoningResult.id)).filter(
                and_(
                    ReasoningResult.created_at >= start,
                    ReasoningResult.created_at <= end
                )
            ).scalar() or 0
        except Exception as e:
            logger.error(f"날짜별 추론 수 조회 실패: {e}")
            return 0

    def _count_reasoning_since(self, date: datetime.date) -> int:
        """특정 날짜 이후 추론 수"""
        try:
            start = datetime.combine(date, datetime.min.time())

            return self.db.query(func.count(ReasoningResult.id)).filter(
                ReasoningResult.created_at >= start
            ).scalar() or 0
        except Exception as e:
            logger.error(f"기간 추론 수 조회 실패: {e}")
            return 0

    def _reasoning_by_mode(self) -> Dict[str, int]:
        """모드별 추론 수"""
        try:
            results = self.db.query(
                ReasoningResult.mode,
                func.count(ReasoningResult.id)
            ).group_by(ReasoningResult.mode).all()

            return {
                (mode or "unknown"): count
                for mode, count in results
            }
        except Exception as e:
            logger.error(f"모드별 추론 수 조회 실패: {e}")
            return {}

    def _count_documents_by_date(self, date: datetime.date) -> int:
        """특정 날짜에 추가된 문서 수"""
        try:
            start = datetime.combine(date, datetime.min.time())
            end = datetime.combine(date, datetime.max.time())

            return self.db.query(func.count(Document.id)).filter(
                and_(
                    Document.created_at >= start,
                    Document.created_at <= end
                )
            ).scalar() or 0
        except Exception as e:
            logger.error(f"날짜별 문서 수 조회 실패: {e}")
            return 0

    def _count_chunks_by_date(self, date: datetime.date) -> int:
        """특정 날짜에 추가된 청크 수"""
        try:
            start = datetime.combine(date, datetime.min.time())
            end = datetime.combine(date, datetime.max.time())

            return self.db.query(func.count(KnowledgeChunk.id)).filter(
                and_(
                    KnowledgeChunk.created_at >= start,
                    KnowledgeChunk.created_at <= end
                )
            ).scalar() or 0
        except Exception as e:
            logger.error(f"날짜별 청크 수 조회 실패: {e}")
            return 0

    def _get_database_stats(self) -> Dict[str, Any]:
        """데이터베이스 통계"""
        try:
            # 테이블별 레코드 수
            tables = {
                "documents": self._count_documents(),
                "chunks": self._count_chunks(),
                "labels": self._count_labels(),
                "projects": self._count_projects(),
                "relations": self._count_relations(),
                "reasoning_results": self._count_reasoning_results(),
            }

            return {
                "tables": tables,
                "total_records": sum(tables.values())
            }
        except Exception as e:
            logger.error(f"데이터베이스 통계 조회 실패: {e}")
            return {}

    def _get_qdrant_stats(self) -> Dict[str, Any]:
        """Qdrant 벡터 DB 통계"""
        try:
            from qdrant_client import QdrantClient
            from backend.config import QDRANT_HOST, QDRANT_PORT, COLLECTION_NAME

            client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

            # 컬렉션 정보 조회
            collection_info = client.get_collection(COLLECTION_NAME)

            # Qdrant 버전 호환성 처리 (vectors_count → points_count)
            points_count = None
            try:
                points_count = collection_info.points_count
            except AttributeError:
                try:
                    points_count = collection_info.vectors_count
                except AttributeError:
                    points_count = 0

            return {
                "collection_name": COLLECTION_NAME,
                "vectors_count": points_count or 0,
                "points_count": points_count or 0,
                "status": collection_info.status.value if collection_info.status else "unknown"
            }
        except Exception as e:
            logger.warning(f"Qdrant 통계 조회 실패: {e}")
            return {
                "error": str(e),
                "note": "Qdrant connection failed"
            }


def get_statistics_service(db: Session) -> StatisticsService:
    """통계 서비스 인스턴스 생성"""
    return StatisticsService(db)
