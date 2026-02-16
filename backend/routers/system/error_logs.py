"""에러 로그 API 라우터"""
from fastapi import APIRouter, Depends, Query
from typing import List, Dict
from pathlib import Path
import json

from backend.services.system.logging_service import get_error_tracker

router = APIRouter(prefix="/api/error-logs", tags=["Error Logs"])


@router.get("/stats")
async def get_error_stats():
    """에러 통계 조회"""
    tracker = get_error_tracker()
    stats = tracker.get_error_stats()
    return stats


@router.get("")
async def list_error_logs(
    limit: int = Query(50, ge=1, le=1000, description="최대 결과 수"),
    offset: int = Query(0, ge=0, description="오프셋"),
    error_type: str = Query(None, description="에러 타입 필터")
):
    """에러 로그 목록 조회"""
    from backend.services.system.logging_service import LOG_DIR
    
    error_log_file = LOG_DIR / "errors.jsonl"
    errors = []
    
    if error_log_file.exists():
        try:
            with open(error_log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        error_data = json.loads(line)
                        if not error_type or error_data.get('error_type') == error_type:
                            errors.append(error_data)
        except:
            pass
    
    # 최신순 정렬
    errors.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    # 페이징
    total_count = len(errors)
    paginated_errors = errors[offset:offset + limit]
    
    return {
        'errors': paginated_errors,
        'total_count': total_count,
        'offset': offset,
        'limit': limit
    }
