"""Context Manager — 질문 복잡도·컨텍스트 압축·토큰 제한 (Phase 9-3-3, 13-5-2)"""
import re
import logging
from typing import List, Dict, Any, Optional

from backend.config import CONTEXT_MAX_TOKENS_SIMPLE, CONTEXT_MAX_TOKENS_COMPLEX

logger = logging.getLogger(__name__)

# tiktoken 로드 (설치 시 정확한 토큰 계산, 미설치 시 근사치 폴백)
_tiktoken_encoding = None
try:
    import tiktoken
    _tiktoken_encoding = tiktoken.get_encoding("cl100k_base")
    logger.info("tiktoken cl100k_base 인코딩 로드 완료")
except ImportError:
    logger.info("tiktoken 미설치 — 문자 수 기반 토큰 근사 사용")

# 폴백 근사: 한국어 1.5~2 토큰/문자, 영어 ~0.25 토큰/문자 → 혼합 기준 2문자=1토큰
CHARS_PER_TOKEN_APPROX = 2


def _approx_tokens(text: str) -> int:
    """토큰 수 계산 — tiktoken 사용 가능 시 정확 계산, 아니면 문자 수 근사."""
    if not text:
        return 0
    text = text.strip()
    if _tiktoken_encoding is not None:
        return len(_tiktoken_encoding.encode(text))
    return max(1, len(text) // CHARS_PER_TOKEN_APPROX)


class ContextManager:
    """질문 복잡도 분석 및 RAG 컨텍스트 구성·압축."""

    def __init__(
        self,
        max_tokens_simple: int = CONTEXT_MAX_TOKENS_SIMPLE,
        max_tokens_complex: int = CONTEXT_MAX_TOKENS_COMPLEX,
    ):
        self.max_tokens_simple = max_tokens_simple
        self.max_tokens_complex = max_tokens_complex

    def analyze_question_complexity(self, question: str) -> str:
        """질문 복잡도 판단: simple | complex.

        기준: 질문 길이, 키워드 수, 복수 문장/질문 유형.
        """
        if not question or not question.strip():
            return "simple"
        q = question.strip()
        char_len = len(q)
        word_count = len(q.split())
        # 복수 질문 패턴 (?, 그리고, 또한, 그리고 나서 등)
        multi_part = bool(re.search(r"[?].*[?]|그리고|또한|그 다음|그리고 나서", q))
        if char_len > 80 or word_count > 15 or multi_part:
            return "complex"
        return "simple"

    def extract_relevant_sentences(
        self,
        content: str,
        question: str,
        max_sentences: int = 10,
    ) -> List[str]:
        """문장 단위로 분리 후 질문 키워드가 포함된 문장 우선 추출."""
        if not content or not content.strip():
            return []
        # 문장 분리 (., !, ?, \n 기준)
        raw = re.split(r"(?<=[.!?])\s+|\n+", content)
        sentences = [s.strip() for s in raw if s.strip()]
        if not sentences:
            return [content[:500]] if content else []
        q_lower = (question or "").lower().strip()
        terms = set(q_lower.split())
        scored = []
        for s in sentences:
            s_lower = s.lower()
            score = sum(1 for t in terms if t in s_lower)
            scored.append((score, s))
        scored.sort(key=lambda x: (-x[0], len(x[1])))
        out = []
        for _, s in scored[:max_sentences]:
            out.append(s)
        if not out:
            out = sentences[:max_sentences]
        return out

    def compress_context(
        self,
        content: str,
        question: str,
        max_length: int,
    ) -> str:
        """컨텍스트를 max_length(문자) 이내로 압축. 문장 단위 추출 우선."""
        if not content or max_length <= 0:
            return ""
        if len(content) <= max_length:
            return content
        sentences = self.extract_relevant_sentences(
            content, question, max_sentences=50
        )
        buf = []
        current = 0
        for s in sentences:
            if current + len(s) + 2 > max_length:
                break
            buf.append(s)
            current += len(s) + 2
        if not buf:
            return content[:max_length - 3] + "..."
        return " ".join(buf)

    def build_context(
        self,
        question: str,
        search_results: List[Dict[str, Any]],
        max_tokens: Optional[int] = None,
        content_key: str = "content",
        score_key: str = "score",
    ) -> Dict[str, Any]:
        """검색 결과로부터 LLM용 컨텍스트 문자열과 메타데이터 구성.

        Args:
            question: 사용자 질문
            search_results: [{"content", "score", "document_id", ...}, ...]
            max_tokens: None이면 복잡도에 따라 자동 결정
            content_key: 본문 필드 키
            score_key: 점수 필드 키

        Returns:
            {
                "context": str,
                "chunks_used": [{"chunk_id", "content", "relevance_score", "included_sentences"?}, ...],
                "question_complexity": "simple"|"complex",
                "total_tokens": int,
                "compressed": bool,
            }
        """
        complexity = self.analyze_question_complexity(question)
        if max_tokens is None:
            max_tokens = (
                self.max_tokens_complex
                if complexity == "complex"
                else self.max_tokens_simple
            )
        max_chars = max_tokens * CHARS_PER_TOKEN_APPROX
        chunks_used = []
        current_chars = 0
        compressed = False
        for r in search_results:
            content = r.get(content_key) or r.get("snippet") or ""
            if not content:
                continue
            score = float(r.get(score_key, 0.0))
            chunk_id = r.get("document_id") or r.get("chunk_id")
            if current_chars + len(content) > max_chars:
                compressed_content = self.compress_context(
                    content, question, max_chars - current_chars - 20
                )
                if compressed_content:
                    compressed = True
                    sentences = self.extract_relevant_sentences(
                        content, question, max_sentences=20
                    )
                    chunks_used.append({
                        "chunk_id": chunk_id,
                        "content": compressed_content,
                        "relevance_score": score,
                        "included_sentences": sentences[:5],
                    })
                    current_chars += len(compressed_content)
                break
            chunks_used.append({
                "chunk_id": chunk_id,
                "content": content,
                "relevance_score": score,
                "included_sentences": None,
            })
            current_chars += len(content) + 2
        context_parts = [c["content"] for c in chunks_used]
        context = "\n\n".join(context_parts)
        total_tokens = _approx_tokens(context)
        return {
            "context": context,
            "chunks_used": chunks_used,
            "question_complexity": complexity,
            "total_tokens": total_tokens,
            "compressed": compressed,
        }


def get_context_manager(
    max_tokens_simple: Optional[int] = None,
    max_tokens_complex: Optional[int] = None,
) -> ContextManager:
    """ContextManager 인스턴스 반환."""
    return ContextManager(
        max_tokens_simple=max_tokens_simple or CONTEXT_MAX_TOKENS_SIMPLE,
        max_tokens_complex=max_tokens_complex or CONTEXT_MAX_TOKENS_COMPLEX,
    )
