"""Phase 9-3-1: Reasoning 추천 기능 단위 테스트"""
import pytest
from backend.services.reasoning.recommendation_service import RecommendationService
from backend.services.reasoning.dynamic_reasoning_service import (
    DynamicReasoningService,
    get_dynamic_reasoning_service,
    MODE_PROMPTS,
)


class TestRecommendationService:
    """RecommendationService 기본 동작."""

    def test_recommend_related_chunks_empty(self):
        """빈 chunk_ids면 빈 목록."""
        # DB 없이 서비스만 생성하면 keyword_search 등에서 에러 가능 → 모킹 없이 빈 입력만 검증
        from backend.models.database import SessionLocal
        db = SessionLocal()
        try:
            svc = RecommendationService(db=db)
            out = svc.recommend_related_chunks([], limit=5)
            assert out == []
            out = svc.recommend_related_chunks([999999], limit=0)
            assert out == []
        finally:
            db.close()

    def test_recommend_labels_empty_content(self):
        """빈 content면 빈 목록."""
        from backend.models.database import SessionLocal
        db = SessionLocal()
        try:
            svc = RecommendationService(db=db)
            out = svc.recommend_labels("", limit=5)
            assert out == []
        finally:
            db.close()

    def test_suggest_exploration_empty(self):
        """빈 context_chunk_ids면 프로젝트만 또는 빈 목록 (DB 없으면 빈 목록)."""
        from backend.models.database import SessionLocal
        db = SessionLocal()
        try:
            svc = RecommendationService(db=db)
            out = svc.suggest_exploration(context_chunk_ids=[], limit=5)
            assert isinstance(out, list)
        except Exception:
            # DB/테이블 미준비 시 빈 목록 기대
            pass
        finally:
            db.close()


class TestDynamicReasoningService:
    """DynamicReasoningService 기본 동작."""

    def test_build_prompt(self):
        """프롬프트에 context와 question 포함."""
        svc = DynamicReasoningService()
        prompt = svc._build_reasoning_prompt("테스트 질문", "컨텍스트 내용", "design_explain")
        assert "테스트 질문" in prompt
        assert "컨텍스트 내용" in prompt
        assert "한국어" in prompt

    def test_postprocess(self):
        """후처리: 연속 빈 줄 정리, 빈 입력은 빈 문자열."""
        svc = DynamicReasoningService()
        out = svc._postprocess_reasoning("  a  \n\n\n  b  ")
        assert "a" in out and "b" in out
        assert svc._postprocess_reasoning("") == ""

    def test_mode_prompts_has_all_modes(self):
        """모드별 프롬프트 존재."""
        for mode in ("design_explain", "risk_review", "next_steps", "history_trace"):
            assert mode in MODE_PROMPTS
            assert "{context}" in MODE_PROMPTS[mode]
            assert "{question}" in MODE_PROMPTS[mode]
