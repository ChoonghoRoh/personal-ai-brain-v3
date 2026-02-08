"""Reranking 서비스 — Cross-encoder 기반 검색 결과 재순위 (Phase 9-3-3)"""
import logging
from typing import List, Dict, Any, Optional

from backend.config import RERANKER_MODEL, RERANKER_ENABLED

logger = logging.getLogger(__name__)

# 싱글톤: 모델 한 번만 로딩
_reranker_model = None
_reranker_model_name: Optional[str] = None


def _get_reranker_model():
    """Cross-encoder 모델 싱글톤 로딩 (lazy)."""
    global _reranker_model, _reranker_model_name
    if not RERANKER_ENABLED:
        return None
    if _reranker_model is None:
        try:
            from sentence_transformers import CrossEncoder
            _reranker_model = CrossEncoder(RERANKER_MODEL)
            _reranker_model_name = RERANKER_MODEL
            logger.info("Reranker model loaded: %s", RERANKER_MODEL)
        except Exception as e:
            logger.warning("Reranker model load failed (rerank disabled): %s", e)
            _reranker_model = None
    return _reranker_model


class Reranker:
    """Cross-encoder 기반 Reranking. query–document 관련도로 재정렬."""

    def __init__(self, model_name: Optional[str] = None, enabled: bool = True):
        self.model_name = model_name or RERANKER_MODEL
        self.enabled = enabled and RERANKER_ENABLED
        self._model = None

    def _ensure_model(self):
        if self._model is None and self.enabled:
            self._model = _get_reranker_model()
        return self._model

    def _compute_relevance_score(self, query: str, document: str) -> float:
        """단일 query–document 쌍의 관련도 점수 (CrossEncoder 로짓)."""
        model = self._ensure_model()
        if model is None:
            return 0.0
        try:
            score = model.predict([[query, (document or "")[:8192]]])
            if hasattr(score, "__len__") and len(score) > 0:
                return float(score[0])
            return float(score)
        except Exception as e:
            logger.debug("rerank score failed: %s", e)
            return 0.0

    def rerank(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        top_k: int = 5,
        content_key: str = "content",
    ) -> List[Dict[str, Any]]:
        """후보 목록을 query 관련도로 재정렬해 상위 top_k 반환.

        Args:
            query: 검색 쿼리
            candidates: [{"content", "document_id", "score", ...}, ...]
            top_k: 반환할 개수
            content_key: 문서 본문 필드 키

        Returns:
            [{"content", "document_id", "original_score", "rerank_score", "final_score", ...}, ...]
        """
        if not query or not candidates:
            return candidates[:top_k]
        model = self._ensure_model()
        if model is None:
            return candidates[:top_k]
        try:
            pairs = []
            for c in candidates:
                text = c.get(content_key) or c.get("snippet") or ""
                if not text:
                    text = str(c)[:2000]
                pairs.append((query, text[:8192]))
            scores = model.predict(pairs)
            if hasattr(scores, "tolist"):
                scores = scores.tolist()
            elif not isinstance(scores, list):
                scores = [float(scores)] if len(pairs) == 1 else []
            score_list = [float(s) for s in scores]
            # 0~1 정규화 (min-max)
            min_s, max_s = min(score_list), max(score_list)
            norm = (max_s - min_s) or 1.0
            out = []
            for i, c in enumerate(candidates):
                rec = dict(c)
                rec["original_score"] = c.get("score", 0.0)
                raw = float(score_list[i]) if i < len(score_list) else 0.0
                rec["rerank_score"] = raw
                rec["final_score"] = (raw - min_s) / norm
                out.append(rec)
            out.sort(key=lambda x: x["final_score"], reverse=True)
            return out[:top_k]
        except Exception as e:
            logger.warning("rerank failed, returning original order: %s", e)
            return candidates[:top_k]


def get_reranker(
    model_name: Optional[str] = None,
    enabled: bool = True,
) -> Reranker:
    """Reranker 인스턴스 반환."""
    return Reranker(model_name=model_name, enabled=enabled)
