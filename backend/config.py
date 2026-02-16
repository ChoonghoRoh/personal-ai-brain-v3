"""백엔드 설정 — 환경 변수로 오버라이드 가능 (docker-compose 등)

Phase 9-1: 보안 강화
- 환경변수 기반 설정 관리
- 하드코딩 비밀번호 제거
- 헬퍼 함수 추가
"""
import os
import logging
from pathlib import Path
from typing import Optional, List

# .env 파일 로드 (로컬 개발 환경)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv가 없으면 환경변수만 사용

logger = logging.getLogger(__name__)

# ============================================
# 환경변수 헬퍼 함수
# ============================================

def get_env(key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """
    환경변수를 안전하게 가져오는 헬퍼 함수

    Args:
        key: 환경변수 키
        default: 기본값
        required: 필수 여부 (True이고 없으면 에러)

    Returns:
        환경변수 값

    Raises:
        ValueError: required=True이고 환경변수가 없을 때
    """
    value = os.getenv(key, default)
    if required and value is None:
        raise ValueError(f"Required environment variable '{key}' is not set")
    return value


def get_env_int(key: str, default: int) -> int:
    """정수형 환경변수 가져오기"""
    value = os.getenv(key)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        logger.warning(f"Invalid integer value for {key}: {value}, using default: {default}")
        return default


def get_env_float(key: str, default: float) -> float:
    """실수형 환경변수 가져오기"""
    value = os.getenv(key)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        logger.warning(f"Invalid float value for {key}: {value}, using default: {default}")
        return default


def get_env_bool(key: str, default: bool = False) -> bool:
    """불리언 환경변수 가져오기"""
    value = os.getenv(key, "").lower()
    if value in ("true", "1", "yes"):
        return True
    elif value in ("false", "0", "no"):
        return False
    return default


def get_env_list(key: str, default: Optional[List[str]] = None, separator: str = ",") -> List[str]:
    """리스트형 환경변수 가져오기 (쉼표 구분)"""
    value = os.getenv(key)
    if value is None:
        return default or []
    return [item.strip() for item in value.split(separator) if item.strip()]


# ============================================
# 프로젝트 경로 설정
# ============================================
_PROJECT_ROOT_DEFAULT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = Path(get_env("PROJECT_ROOT", str(_PROJECT_ROOT_DEFAULT)) or str(_PROJECT_ROOT_DEFAULT))
WORKSPACE_ROOT = Path(get_env("WORKSPACE_ROOT", str(PROJECT_ROOT)) or str(PROJECT_ROOT))
BRAIN_DIR = PROJECT_ROOT / "brain"
SYSTEM_DIR = BRAIN_DIR / "system"
COLLECTOR_DIR = PROJECT_ROOT / "collector"

# ============================================
# 애플리케이션 설정
# ============================================
ENVIRONMENT = get_env("ENVIRONMENT", "development")
DEBUG = get_env_bool("DEBUG", False)

# ============================================
# Database Configuration (PostgreSQL)
# ============================================
POSTGRES_HOST = get_env("POSTGRES_HOST", "localhost")
POSTGRES_PORT = get_env_int("POSTGRES_PORT", 5432)
POSTGRES_USER = get_env("POSTGRES_USER", "brain")
POSTGRES_PASSWORD = get_env("POSTGRES_PASSWORD", "brain_password")  # .env에서 오버라이드 권장
POSTGRES_DB = get_env("POSTGRES_DB", "knowledge")

# DATABASE_URL: 환경변수 우선, 없으면 개별 설정으로 구성
DATABASE_URL = get_env(
    "DATABASE_URL",
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

# ============================================
# Qdrant Configuration (Vector Database)
# ============================================
QDRANT_HOST = get_env("QDRANT_HOST", "localhost")
QDRANT_PORT = get_env_int("QDRANT_PORT", 6333)
QDRANT_API_KEY = get_env("QDRANT_API_KEY")  # 선택
COLLECTION_NAME = get_env("COLLECTION_NAME", "brain_documents")

# ============================================
# Ollama Configuration (Local LLM)
# ============================================
OLLAMA_BASE_URL = get_env("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = get_env("OLLAMA_MODEL", "qwen2.5:7b")
OLLAMA_MODEL_LIGHT = get_env("OLLAMA_MODEL_LIGHT", "qwen2.5:3b")

# ============================================
# API 설정
# ============================================
API_HOST = get_env("API_HOST", "0.0.0.0")
API_PORT = get_env_int("API_PORT", 8000)
EXTERNAL_PORT = get_env_int("EXTERNAL_PORT", 8001)  # 호스트 노출 포트 (Phase 12-1-2)

# 임베딩 모델
EMBEDDING_MODEL = get_env("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# ============================================
# Security Configuration (Phase 9-1)
# ============================================
# JWT 인증 설정
JWT_SECRET_KEY = get_env("JWT_SECRET_KEY", "development_secret_key_change_in_production")
JWT_ALGORITHM = get_env("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = get_env_int("JWT_EXPIRE_MINUTES", 30)

# API Key 인증 (간단한 API 키 방식)
API_SECRET_KEY = get_env("API_SECRET_KEY")

# 인증 활성화 여부 (개발 환경에서 비활성화 가능)
AUTH_ENABLED = get_env_bool("AUTH_ENABLED", ENVIRONMENT == "production")

# 초기 관리자 계정 (Phase 14-5-2: 첫 실행 시 자동 생성)
ADMIN_DEFAULT_USERNAME = get_env("ADMIN_DEFAULT_USERNAME", "admin")
ADMIN_DEFAULT_PASSWORD = get_env("ADMIN_DEFAULT_PASSWORD", "admin1234")

# ============================================
# CORS Configuration (Phase 9-1)
# ============================================
CORS_ORIGINS = get_env_list("CORS_ORIGINS", ["http://localhost:3000", "http://localhost:8080"])
CORS_ALLOW_CREDENTIALS = get_env_bool("CORS_ALLOW_CREDENTIALS", True)
CORS_ALLOW_METHODS = get_env_list("CORS_ALLOW_METHODS", ["*"])
CORS_ALLOW_HEADERS = get_env_list("CORS_ALLOW_HEADERS", ["*"])

# ============================================
# Rate Limiting Configuration (Phase 9-1)
# ============================================
RATE_LIMIT_ENABLED = get_env_bool("RATE_LIMIT_ENABLED", True)
RATE_LIMIT_PER_MINUTE = get_env_int("RATE_LIMIT_PER_MINUTE", 60)
RATE_LIMIT_LLM_PER_MINUTE = get_env_int("RATE_LIMIT_LLM_PER_MINUTE", 10)
RATE_LIMIT_SEARCH_PER_MINUTE = get_env_int("RATE_LIMIT_SEARCH_PER_MINUTE", 30)
RATE_LIMIT_IMPORT_PER_MINUTE = get_env_int("RATE_LIMIT_IMPORT_PER_MINUTE", 5)
RATE_LIMIT_AUTH_PER_MINUTE = get_env_int("RATE_LIMIT_AUTH_PER_MINUTE", 5)

# Redis (Rate Limiting 분산 환경용)
REDIS_URL = get_env("REDIS_URL")

# ============================================
# HSTS Configuration (Phase 12-1-3)
# ============================================
HSTS_ENABLED = get_env_bool("HSTS_ENABLED", ENVIRONMENT == "production")
HSTS_MAX_AGE = get_env_int("HSTS_MAX_AGE", 31536000)  # 1년 (초)
HSTS_INCLUDE_SUBDOMAINS = get_env_bool("HSTS_INCLUDE_SUBDOMAINS", True)
HSTS_PRELOAD = get_env_bool("HSTS_PRELOAD", False)

# ============================================
# Memory Cleanup Scheduler (Phase 12-3-4)
# ============================================
MEMORY_CLEANUP_ENABLED = get_env_bool("MEMORY_CLEANUP_ENABLED", True)
MEMORY_CLEANUP_INTERVAL_MINUTES = get_env_int("MEMORY_CLEANUP_INTERVAL_MINUTES", 60)

# ============================================
# RAG Enhancement (Phase 9-3-3)
# ============================================
HYBRID_SEARCH_SEMANTIC_WEIGHT = get_env_float("HYBRID_SEARCH_SEMANTIC_WEIGHT", 0.7)
HYBRID_SEARCH_KEYWORD_WEIGHT = get_env_float("HYBRID_SEARCH_KEYWORD_WEIGHT", 0.3)
RERANKER_MODEL = get_env("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
RERANKER_ENABLED = get_env_bool("RERANKER_ENABLED", True)
CONTEXT_MAX_TOKENS_SIMPLE = get_env_int("CONTEXT_MAX_TOKENS_SIMPLE", 800)
CONTEXT_MAX_TOKENS_COMPLEX = get_env_int("CONTEXT_MAX_TOKENS_COMPLEX", 2000)
MULTIHOP_MAX_DEPTH = get_env_int("MULTIHOP_MAX_DEPTH", 2)

# ============================================
# 지식구조 자동 매칭 (Phase 9-3-2)
# ============================================
AUTO_STRUCTURE_MATCHING_ENABLED = get_env_bool("AUTO_STRUCTURE_MATCHING_ENABLED", True)
AUTO_LABEL_MIN_CONFIDENCE = get_env_float("AUTO_LABEL_MIN_CONFIDENCE", 0.5)
AUTO_RELATION_MIN_CONFIDENCE = get_env_float("AUTO_RELATION_MIN_CONFIDENCE", 0.7)
AUTO_CATEGORY_MIN_CONFIDENCE = get_env_float("AUTO_CATEGORY_MIN_CONFIDENCE", 0.6)
MAX_LABEL_SUGGESTIONS = get_env_int("MAX_LABEL_SUGGESTIONS", 10)
MAX_RELATION_SUGGESTIONS = get_env_int("MAX_RELATION_SUGGESTIONS", 5)
MAX_SIMILAR_DOCUMENTS = get_env_int("MAX_SIMILAR_DOCUMENTS", 5)

# ============================================
# External API Keys
# ============================================
ANTHROPIC_API_KEY = get_env("ANTHROPIC_API_KEY")

# ============================================
# Knowledge Folder Configuration (Phase 15-1)
# ============================================
KNOWLEDGE_FOLDER_PATH = get_env("KNOWLEDGE_FOLDER_PATH", "brain/knowledge")

# ============================================
# 설정 검증 (프로덕션 환경)
# ============================================
def validate_production_config() -> None:
    """프로덕션 환경에서 필수 설정 검증"""
    if ENVIRONMENT == "production":
        errors = []

        # JWT 시크릿 키 검증
        if JWT_SECRET_KEY == "development_secret_key_change_in_production":
            errors.append("JWT_SECRET_KEY must be changed in production")

        # 비밀번호 기본값 검증
        if POSTGRES_PASSWORD == "brain_password":
            errors.append("POSTGRES_PASSWORD should be changed from default in production")

        if errors:
            for error in errors:
                logger.warning(f"Production config warning: {error}")
            # 프로덕션에서는 경고만 하고 시작은 허용 (운영자 판단)


# 모듈 로드 시 검증
validate_production_config()