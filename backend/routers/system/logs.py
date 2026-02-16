"""로그 API 라우터"""
from fastapi import APIRouter, Query
from typing import List, Dict, Optional
from pathlib import Path
import json
from datetime import datetime

from backend.config import PROJECT_ROOT, SYSTEM_DIR

router = APIRouter(prefix="/api/logs", tags=["Logs"])


@router.get("")
async def get_logs(
    limit: int = Query(50, ge=1, le=1000, description="최대 반환 개수"),
    offset: int = Query(0, ge=0, description="오프셋"),
    date: Optional[str] = Query(None, description="특정 날짜 (YYYY-MM-DD)"),
    action: Optional[str] = Query(None, description="액션 필터"),
    sort_by: str = Query("timestamp", description="정렬 기준 (timestamp, action)"),
    sort_order: str = Query("desc", description="정렬 방향 (asc, desc)")
) -> Dict:
    """작업 로그 조회 (페이징 지원)"""
    work_log_json = SYSTEM_DIR / "work_log.json"
    
    if not work_log_json.exists():
        return {
            'entries': [],
            'total_count': 0,
            'limit': limit,
            'offset': offset,
            'total_pages': 0,
            'current_page': 1,
            'date': date,
            'action': action
        }
    
    try:
        with open(work_log_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        entries = data.get('entries', [])
        
        # 날짜 필터
        if date:
            entries = [e for e in entries if e.get('date') == date]
        
        # 액션 필터
        if action:
            entries = [e for e in entries if e.get('action') == action]
        
        # 정렬 적용
        valid_sort_fields = ["timestamp", "action"]
        if sort_by not in valid_sort_fields:
            sort_by = "timestamp"
        
        reverse = sort_order.lower() != "asc"
        if sort_by == "timestamp":
            entries = sorted(entries, key=lambda x: x.get('timestamp', ''), reverse=reverse)
        elif sort_by == "action":
            entries = sorted(entries, key=lambda x: x.get('action', ''), reverse=reverse)
        
        # 총 개수 계산 (필터 적용 후)
        total_count = len(entries)
        
        # 페이징 적용
        paginated_entries = entries[offset:offset + limit]
        
        # 페이징 메타데이터 계산
        total_pages = (total_count + limit - 1) // limit if limit > 0 else 0
        current_page = (offset // limit) + 1 if limit > 0 else 1
        
        return {
            'entries': paginated_entries,
            'total_count': total_count,
            'limit': limit,
            'offset': offset,
            'total_pages': total_pages,
            'current_page': current_page,
            'date': date,
            'action': action,
            'last_update': data.get('last_update')
        }
    except Exception as e:
        return {
            'entries': [],
            'total_count': 0,
            'limit': limit,
            'offset': offset,
            'total_pages': 0,
            'current_page': 1,
            'error': str(e)
        }


@router.get("/stats")
async def get_log_stats() -> Dict:
    """로그 통계"""
    work_log_json = SYSTEM_DIR / "work_log.json"
    
    if not work_log_json.exists():
        return {
            'total_entries': 0,
            'by_action': {},
            'by_date': {},
            'recent_actions': []
        }
    
    try:
        with open(work_log_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        entries = data.get('entries', [])
        
        # 액션별 통계
        by_action = {}
        for entry in entries:
            action = entry.get('action', 'unknown')
            by_action[action] = by_action.get(action, 0) + 1
        
        # 날짜별 통계
        by_date = {}
        for entry in entries:
            date = entry.get('date', 'unknown')
            by_date[date] = by_date.get(date, 0) + 1
        
        # 최근 액션 (최근 10개)
        recent_actions = sorted(entries, key=lambda x: x.get('timestamp', ''), reverse=True)[:10]
        
        return {
            'total_entries': len(entries),
            'by_action': by_action,
            'by_date': dict(sorted(by_date.items(), reverse=True)[:30]),  # 최근 30일
            'recent_actions': recent_actions
        }
    except Exception as e:
        return {
            'total_entries': 0,
            'error': str(e)
        }

