"""통계 API 라우터

Phase 9-4-2: 통계/분석 대시보드
- GET /api/system/statistics - 전체 통계 요약
- GET /api/system/statistics/documents - 문서 통계
- GET /api/system/statistics/knowledge - 지식(청크/라벨) 통계
- GET /api/system/statistics/usage - 사용량 통계
- GET /api/system/statistics/system - 시스템 상태
- GET /api/system/statistics/trends - 트렌드 데이터
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.models.database import get_db
from backend.services.system.statistics_service import get_statistics_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/system/statistics", tags=["Statistics"])


@router.get("")
async def get_statistics_summary(db: Session = Depends(get_db)):
    """
    전체 통계 요약

    Returns:
        - summary: 주요 지표 (문서, 청크, 라벨, 프로젝트 수)
        - documents: 문서 유형별 분포
        - chunks: 청크 상태별 분포
        - usage: 오늘 사용량
    """
    service = get_statistics_service(db)

    summary = service.get_summary()
    doc_stats = service.get_document_statistics()
    knowledge_stats = service.get_knowledge_statistics()
    usage_stats = service.get_usage_statistics()

    return {
        "summary": summary,
        "documents": {
            "by_type": doc_stats.get("by_type", {}),
            "recent_7d": doc_stats.get("recent", 0),
        },
        "chunks": {
            "by_status": knowledge_stats.get("chunks", {}).get("by_status", {}),
        },
        "labels": {
            "by_type": knowledge_stats.get("labels", {}).get("by_type", {}),
            "top_used": knowledge_stats.get("labels", {}).get("top_used", [])[:5],
        },
        "usage": {
            "reasoning_today": usage_stats.get("reasoning", {}).get("today", 0),
            "reasoning_total": usage_stats.get("reasoning", {}).get("total", 0),
        }
    }


@router.get("/documents")
async def get_document_statistics(db: Session = Depends(get_db)):
    """
    문서 상세 통계

    Returns:
        - total: 총 문서 수
        - by_type: 파일 유형별 분포
        - by_project: 프로젝트별 분포
        - recent: 최근 7일간 추가된 문서 수
    """
    service = get_statistics_service(db)
    return service.get_document_statistics()


@router.get("/knowledge")
async def get_knowledge_statistics(db: Session = Depends(get_db)):
    """
    지식(청크/라벨/관계) 상세 통계

    Returns:
        - chunks: 청크 통계 (총수, 상태별, 프로젝트별, 문서당 평균)
        - labels: 라벨 통계 (총수, 유형별, TOP 10)
        - relations: 관계 통계 (총수, 유형별)
    """
    service = get_statistics_service(db)
    return service.get_knowledge_statistics()


@router.get("/usage")
async def get_usage_statistics(db: Session = Depends(get_db)):
    """
    사용량 통계

    Returns:
        - reasoning: 추론 사용량 (오늘, 이번 주, 모드별)
    """
    service = get_statistics_service(db)
    return service.get_usage_statistics()


@router.get("/system")
async def get_system_statistics(db: Session = Depends(get_db)):
    """
    시스템 상태 통계

    Returns:
        - database: 데이터베이스 테이블별 레코드 수
        - qdrant: Qdrant 벡터 DB 상태
    """
    service = get_statistics_service(db)
    return service.get_system_statistics()


@router.get("/trends")
async def get_trends(
    days: int = Query(default=7, ge=1, le=90, description="조회할 일수 (1-90)"),
    db: Session = Depends(get_db)
):
    """
    트렌드 데이터 (일별)

    Args:
        days: 조회할 일수 (기본 7일, 최대 90일)

    Returns:
        - period: 조회 기간
        - data: 일별 데이터 (문서, 청크, 추론 수)
    """
    service = get_statistics_service(db)
    return service.get_trends(days=days)
