"""입력 검증 유틸리티"""
import re
from typing import Optional
from html import escape


def sanitize_input(text: str, max_length: Optional[int] = None) -> str:
    """입력값 정제"""
    if not text:
        return ""
    
    # 공백 제거
    text = text.strip()
    
    # 길이 제한
    if max_length:
        text = text[:max_length]
    
    return text


def validate_email(email: str) -> bool:
    """이메일 검증"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """URL 검증"""
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url))


def escape_html(text: str) -> str:
    """HTML 이스케이프"""
    return escape(text)


def validate_sql_injection_safe(text: str) -> bool:
    """SQL injection 위험 검사"""
    dangerous_patterns = [
        r"';",
        r'";',
        r'--',
        r'/\*',
        r'\*/',
        r'union.*select',
        r'drop.*table',
        r'delete.*from',
        r'insert.*into',
        r'update.*set'
    ]
    
    text_lower = text.lower()
    for pattern in dangerous_patterns:
        if re.search(pattern, text_lower):
            return False
    
    return True
