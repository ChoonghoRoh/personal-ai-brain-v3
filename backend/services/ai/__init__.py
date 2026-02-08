# AI 서비스 (Ollama 로컬 LLM, Context Manager 등)
from backend.services.ai.ollama_client import (
    ollama_generate,
    ollama_available,
    ollama_connection_check,
    OLLAMA_UNAVAILABLE_MESSAGE,
)
from backend.services.ai import context_manager

__all__ = [
    "ollama_generate",
    "ollama_available",
    "ollama_connection_check",
    "OLLAMA_UNAVAILABLE_MESSAGE",
    "context_manager",
]
