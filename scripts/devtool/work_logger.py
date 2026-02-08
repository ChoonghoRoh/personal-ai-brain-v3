#!/usr/bin/env python3
"""
통합 작업 로그 시스템
모든 작업 기록을 중앙에서 관리
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SYSTEM_DIR = PROJECT_ROOT / "brain" / "system"
WORK_LOG_FILE = SYSTEM_DIR / "work_log.md"
WORK_LOG_JSON = SYSTEM_DIR / "work_log.json"


class WorkLogger:
    """작업 로그 관리 클래스"""
    
    def __init__(self):
        SYSTEM_DIR.mkdir(parents=True, exist_ok=True)
        self.log_data = self.load_log_data()
    
    def load_log_data(self) -> Dict:
        """JSON 로그 데이터 로드"""
        if WORK_LOG_JSON.exists():
            try:
                with open(WORK_LOG_JSON, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {'entries': [], 'last_update': None}
        return {'entries': [], 'last_update': None}
    
    def save_log_data(self):
        """JSON 로그 데이터 저장"""
        self.log_data['last_update'] = datetime.now().isoformat()
        with open(WORK_LOG_JSON, 'w', encoding='utf-8') as f:
            json.dump(self.log_data, f, indent=2, ensure_ascii=False)
    
    def add_entry(self, 
                  action: str,
                  description: str,
                  files: Optional[List[str]] = None,
                  metadata: Optional[Dict] = None):
        """작업 로그 항목 추가"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'date': datetime.now().strftime("%Y-%m-%d"),
            'time': datetime.now().strftime("%H:%M:%S"),
            'action': action,
            'description': description,
            'files': files or [],
            'metadata': metadata or {}
        }
        
        self.log_data['entries'].append(entry)
        self.save_log_data()
        self.generate_markdown_log()
    
    def generate_markdown_log(self):
        """Markdown 형식의 로그 파일 생성"""
        entries = self.log_data.get('entries', [])
        
        if not entries:
            content = "# 작업 로그\n\n작업 기록이 없습니다.\n"
        else:
            # 날짜별로 그룹화
            entries_by_date = {}
            for entry in entries:
                date = entry.get('date', 'Unknown')
                if date not in entries_by_date:
                    entries_by_date[date] = []
                entries_by_date[date].append(entry)
            
            # 최신 날짜부터 정렬
            sorted_dates = sorted(entries_by_date.keys(), reverse=True)
            
            content = "# 작업 로그\n\n"
            content += f"**최종 업데이트**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            content += f"**총 작업 수**: {len(entries)}개\n\n"
            content += "---\n\n"
            
            for date in sorted_dates:
                content += f"## {date}\n\n"
                
                # 시간순으로 정렬 (최신이 위)
                day_entries = sorted(
                    entries_by_date[date],
                    key=lambda x: x.get('timestamp', ''),
                    reverse=True
                )
                
                for entry in day_entries:
                    time = entry.get('time', '')
                    action = entry.get('action', '')
                    description = entry.get('description', '')
                    files = entry.get('files', [])
                    metadata = entry.get('metadata', {})
                    
                    # 액션에 따른 이모지
                    emoji_map = {
                        'commit': '💾',
                        'file_change': '📝',
                        'embed': '🔍',
                        'search': '🔎',
                        'system': '⚙️',
                        'collect': '📚',
                        'watch': '👀',
                        'error': '❌',
                        'info': 'ℹ️'
                    }
                    emoji = emoji_map.get(action, '📌')
                    
                    content += f"### {emoji} {time} - {action}\n\n"
                    content += f"{description}\n\n"
                    
                    if files:
                        content += "**관련 파일:**\n"
                        for file in files[:5]:  # 최대 5개만 표시
                            content += f"- `{file}`\n"
                        if len(files) > 5:
                            content += f"- ... 외 {len(files) - 5}개\n"
                        content += "\n"
                    
                    if metadata:
                        content += "**메타데이터:**\n"
                        for key, value in metadata.items():
                            content += f"- {key}: {value}\n"
                        content += "\n"
                    
                    content += "---\n\n"
        
        with open(WORK_LOG_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def get_recent_entries(self, limit: int = 10) -> List[Dict]:
        """최근 작업 항목 가져오기"""
        entries = self.log_data.get('entries', [])
        return sorted(entries, key=lambda x: x.get('timestamp', ''), reverse=True)[:limit]
    
    def get_entries_by_date(self, date: str) -> List[Dict]:
        """특정 날짜의 작업 항목 가져오기"""
        entries = self.log_data.get('entries', [])
        return [e for e in entries if e.get('date') == date]
    
    def cleanup_old_entries(self, days: int = 90):
        """오래된 항목 정리 (JSON에서만 제거, Markdown은 유지)"""
        cutoff_date = datetime.now().replace(day=1).isoformat()  # 이번 달 1일
        entries = self.log_data.get('entries', [])
        
        # 최근 N일 이내 항목만 유지
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=days)
        
        filtered_entries = [
            e for e in entries
            if datetime.fromisoformat(e.get('timestamp', datetime.now().isoformat())) > cutoff
        ]
        
        removed_count = len(entries) - len(filtered_entries)
        if removed_count > 0:
            self.log_data['entries'] = filtered_entries
            self.save_log_data()
            print(f"✅ {removed_count}개의 오래된 항목이 정리되었습니다.")
        
        return removed_count


# 전역 로거 인스턴스
_logger_instance = None

def get_logger() -> WorkLogger:
    """로거 인스턴스 가져오기 (싱글톤)"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = WorkLogger()
    return _logger_instance


def log_action(action: str, description: str, files: Optional[List[str]] = None, metadata: Optional[Dict] = None):
    """작업 로그 기록 (편의 함수)"""
    logger = get_logger()
    logger.add_entry(action, description, files, metadata)


if __name__ == "__main__":
    """명령줄에서 직접 실행 시"""
    import sys
    
    logger = get_logger()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "cleanup":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 90
            logger.cleanup_old_entries(days)
        elif command == "recent":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            entries = logger.get_recent_entries(limit)
            for entry in entries:
                print(f"{entry.get('date')} {entry.get('time')} - {entry.get('action')}: {entry.get('description')}")
        elif command == "regenerate":
            logger.generate_markdown_log()
            print("✅ Markdown 로그 재생성 완료")
        else:
            print("사용법:")
            print("  python work_logger.py cleanup [days]  # 오래된 항목 정리")
            print("  python work_logger.py recent [limit]  # 최근 작업 보기")
            print("  python work_logger.py regenerate      # Markdown 재생성")
    else:
        # 테스트 항목 추가
        logger.add_entry(
            action="test",
            description="작업 로그 시스템 테스트",
            files=["test.md"],
            metadata={"test": True}
        )
        print("✅ 테스트 항목이 추가되었습니다.")

