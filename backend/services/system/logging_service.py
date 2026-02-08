"""구조화된 로깅 서비스"""
import logging
import json
import traceback
from datetime import datetime
from typing import Dict, Optional, Any
from pathlib import Path
import sys

# 프로젝트 루트 경로 설정
PROJECT_ROOT = Path(__file__).parent.parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


class StructuredLogger:
    """구조화된 로거 클래스"""
    
    def __init__(self, name: str = "app", log_file: Optional[str] = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # 기존 핸들러 제거
        self.logger.handlers = []
        
        # 콘솔 핸들러
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # 파일 핸들러
        if log_file:
            file_path = LOG_DIR / log_file
            file_handler = logging.FileHandler(file_path, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(pathname)s:%(lineno)d'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
    
    def _log_structured(self, level: str, message: str, **kwargs):
        """구조화된 로그 기록"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            **kwargs
        }
        
        # JSON 형식으로 로그 파일에 저장
        json_log_file = LOG_DIR / "structured_logs.jsonl"
        try:
            with open(json_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_data, ensure_ascii=False) + '\n')
        except:
            pass
        
        # 표준 로깅
        getattr(self.logger, level.lower())(message, extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """정보 로그"""
        self._log_structured('INFO', message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """경고 로그"""
        self._log_structured('WARNING', message, **kwargs)
    
    def error(self, message: str, error: Optional[Exception] = None, **kwargs):
        """에러 로그"""
        error_data = {}
        if error:
            error_data = {
                'error_type': type(error).__name__,
                'error_message': str(error),
                'traceback': traceback.format_exc()
            }
        
        self._log_structured('ERROR', message, error=error_data, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """디버그 로그"""
        self._log_structured('DEBUG', message, **kwargs)
    
    def critical(self, message: str, error: Optional[Exception] = None, **kwargs):
        """치명적 오류 로그"""
        error_data = {}
        if error:
            error_data = {
                'error_type': type(error).__name__,
                'error_message': str(error),
                'traceback': traceback.format_exc()
            }
        
        self._log_structured('CRITICAL', message, error=error_data, **kwargs)


class ErrorTracker:
    """에러 추적 시스템"""
    
    def __init__(self):
        self.error_log_file = LOG_DIR / "errors.jsonl"
        self.error_counts = {}
    
    def track_error(
        self,
        error_type: str,
        error_message: str,
        context: Optional[Dict] = None,
        severity: str = "medium"
    ):
        """에러 추적"""
        error_data = {
            'timestamp': datetime.now().isoformat(),
            'error_type': error_type,
            'error_message': error_message,
            'severity': severity,
            'context': context or {},
            'count': self.error_counts.get(error_type, 0) + 1
        }
        
        # 에러 카운트 증가
        self.error_counts[error_type] = error_data['count']
        
        # JSONL 파일에 저장
        try:
            with open(self.error_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(error_data, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"에러 로그 저장 실패: {e}")
        
        return error_data
    
    def get_error_stats(self) -> Dict:
        """에러 통계 조회"""
        errors = []
        
        if self.error_log_file.exists():
            try:
                with open(self.error_log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            errors.append(json.loads(line))
            except:
                pass
        
        # 에러 타입별 통계
        error_type_counts = {}
        for error in errors:
            error_type = error.get('error_type', 'unknown')
            error_type_counts[error_type] = error_type_counts.get(error_type, 0) + 1
        
        return {
            'total_errors': len(errors),
            'error_type_counts': error_type_counts,
            'recent_errors': errors[-10:] if errors else []
        }


# 전역 로거 인스턴스
_app_logger = None
_error_tracker = None

def get_logger(name: str = "app") -> StructuredLogger:
    """로거 인스턴스 가져오기"""
    global _app_logger
    if _app_logger is None:
        _app_logger = StructuredLogger(name, log_file="app.log")
    return _app_logger

def get_error_tracker() -> ErrorTracker:
    """에러 추적기 인스턴스 가져오기"""
    global _error_tracker
    if _error_tracker is None:
        _error_tracker = ErrorTracker()
    return _error_tracker
