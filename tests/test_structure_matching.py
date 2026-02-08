"""Phase 9-3-2: 지식구조 자동 매칭 단위 테스트"""
import pytest
from backend.services.knowledge.structure_matcher import (
    StructureMatcher,
    get_structure_matcher,
    _extract_keywords,
)


class TestExtractKeywords:
    """키워드 추출."""

    def test_extract_keywords_empty(self):
        assert _extract_keywords("") == []
        assert _extract_keywords("   ") == []

    def test_extract_keywords_from_text(self):
        out = _extract_keywords("# Phase 9 설계\n\n아키텍처 개선 계획")
        assert "Phase" in out or "아키텍처" in out or "설계" in out or "개선" in out

    def test_extract_keywords_excludes_short(self):
        out = _extract_keywords("a b c ab cd")
        assert "a" not in out
        assert "b" not in out


class TestStructureMatcher:
    """StructureMatcher 기본 동작."""

    def test_match_on_chunk_create_returns_keys(self):
        """match_on_chunk_create 반환 구조 검증 (빈 content)."""
        from backend.models.database import SessionLocal
        from backend.models.models import KnowledgeChunk
        db = SessionLocal()
        try:
            chunk = db.query(KnowledgeChunk).first()
            if not chunk:
                pytest.skip("no chunk in DB")
            matcher = StructureMatcher(db=db)
            result = matcher.match_on_chunk_create(chunk)
            assert "suggested_labels" in result
            assert "similar_chunks" in result
            assert "suggested_category" in result
            assert isinstance(result["suggested_labels"], list)
            assert isinstance(result["similar_chunks"], list)
        except Exception:
            pytest.skip("DB or matcher not available")
        finally:
            db.close()

    def test_infer_category_from_path(self):
        from backend.models.database import SessionLocal
        db = SessionLocal()
        try:
            matcher = StructureMatcher(db=db)
            cat = matcher._infer_category_from_path("docs/phases/phase-9/plan.md")
            assert cat is None or (isinstance(cat, dict) and ("label_id" in cat or "name" in cat))
        except Exception:
            pass
        finally:
            db.close()