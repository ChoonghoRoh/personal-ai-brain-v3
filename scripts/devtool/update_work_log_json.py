#!/usr/bin/env python3
"""
work_log.md의 내용을 기반으로 work_log.json 업데이트
주요 단계들을 JSON 항목으로 변환
"""

import json
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SYSTEM_DIR = PROJECT_ROOT / "brain" / "system"
WORK_LOG_JSON = SYSTEM_DIR / "work_log.json"

# work_log.md의 주요 단계들을 JSON 항목으로 변환
# 각 단계는 하나의 항목으로 추가
entries = [
    {
        "timestamp": "2026-01-07T00:00:00",
        "date": "2026-01-07",
        "time": "00:00:00",
        "action": "system",
        "description": "1단계: 프로젝트 기본 구조 및 핵심 기능 구축 완료",
        "files": [
            "scripts/embed_and_store.py",
            "scripts/search_and_query.py"
        ],
        "metadata": {
            "phase": 1,
            "status": "completed"
        }
    },
    {
        "timestamp": "2026-01-07T01:00:00",
        "date": "2026-01-07",
        "time": "01:00:00",
        "action": "system",
        "description": "2단계: 자동화 시스템 구축 완료 (변경 감지, 자동 커밋, 문서 수집, 시스템 관리)",
        "files": [
            "scripts/watcher.py",
            "scripts/auto_commit.py",
            "scripts/collector.py",
            "scripts/system_agent.py"
        ],
        "metadata": {
            "phase": 2,
            "status": "completed"
        }
    },
    {
        "timestamp": "2026-01-07T02:00:00",
        "date": "2026-01-07",
        "time": "02:00:00",
        "action": "system",
        "description": "3단계: 통합 작업 기록 시스템 구축 완료",
        "files": [
            "scripts/work_logger.py",
            "brain/system/work_log.md",
            "brain/system/work_log.json"
        ],
        "metadata": {
            "phase": 3,
            "status": "completed"
        }
    },
    {
        "timestamp": "2026-01-07T03:00:00",
        "date": "2026-01-07",
        "time": "03:00:00",
        "action": "system",
        "description": "4단계: 웹 인터페이스 구축 완료 (Phase 4.1, 4.2, 4.3)",
        "files": [
            "backend/main.py",
            "web/src/pages/dashboard.html",
            "web/src/pages/search.html",
            "web/src/pages/document.html",
            "web/src/pages/ask.html",
            "web/src/pages/logs.html"
        ],
        "metadata": {
            "phase": 4,
            "status": "completed"
        }
    },
    {
        "timestamp": "2026-01-07T04:00:00",
        "date": "2026-01-07",
        "time": "04:00:00",
        "action": "system",
        "description": "5단계: 지식 구조화 및 Reasoning 시스템 구축 완료 (Phase 5.1~5.5)",
        "files": [
            "backend/models/",
            "backend/routers/labels.py",
            "backend/routers/relations.py",
            "backend/routers/reason.py"
        ],
        "metadata": {
            "phase": 5,
            "status": "completed"
        }
    }
]

# 기존 JSON 로드
if WORK_LOG_JSON.exists():
    try:
        with open(WORK_LOG_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
        existing_entries = data.get('entries', [])
    except:
        existing_entries = []
else:
    existing_entries = []

# 기존 항목과 새 항목 병합 (중복 제거)
# timestamp를 기준으로 중복 체크
existing_timestamps = {e.get('timestamp') for e in existing_entries}
new_entries = [e for e in entries if e.get('timestamp') not in existing_timestamps]

if new_entries:
    all_entries = existing_entries + new_entries
    # timestamp 순으로 정렬
    all_entries.sort(key=lambda x: x.get('timestamp', ''))
    
    data = {
        'entries': all_entries,
        'last_update': datetime.now().isoformat()
    }
    
    with open(WORK_LOG_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ {len(new_entries)}개의 새 항목이 추가되었습니다.")
    print(f"총 {len(all_entries)}개의 항목이 있습니다.")
else:
    print("추가할 새 항목이 없습니다.")


