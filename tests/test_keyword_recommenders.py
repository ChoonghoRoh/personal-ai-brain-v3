"""Phase 17-2: ChunkLabelRecommender / GroupKeywordRecommender 단위 테스트"""
import pytest
from unittest.mock import patch, MagicMock

from backend.services.reasoning.recommendation_llm import (
    extract_keywords_from_content,
    match_and_score_labels,
    fallback_extract,
)


# ---------------------------------------------------------------------------
# 공통 유틸 함수 테스트
# ---------------------------------------------------------------------------


class TestExtractKeywordsFromContent:
    def test_empty_content(self):
        assert extract_keywords_from_content("") == []
        assert extract_keywords_from_content(None) == []

    def test_basic_extraction(self):
        result = extract_keywords_from_content("파이썬 프로그래밍 입문서")
        assert len(result) > 0
        assert "파이썬" in result or "프로그래밍" in result

    def test_excludes_existing_labels(self):
        existing = {"파이썬", "프로그래밍"}
        result = extract_keywords_from_content("파이썬 프로그래밍 입문서", existing)
        assert "파이썬" not in [r.lower() for r in result]
        assert "프로그래밍" not in [r.lower() for r in result]

    def test_limit(self):
        result = extract_keywords_from_content("하나 둘 셋 넷 다섯 여섯 일곱 여덟 아홉 열 열하나 열둘", limit=3)
        assert len(result) <= 3

    def test_strips_markdown(self):
        result = extract_keywords_from_content("## **파이썬** `코드` (예제)")
        assert any("파이썬" in r for r in result)


class TestMatchAndScoreLabels:
    def test_empty_keywords(self):
        db = MagicMock()
        result = match_and_score_labels(db, [], set(), set(), 10)
        assert result == {"suggestions": [], "new_keywords": []}

    def test_matching_labels(self):
        db = MagicMock()
        mock_label = MagicMock()
        mock_label.id = 1
        mock_label.name = "파이썬"
        mock_label.label_type = "keyword"

        db.query.return_value.filter.return_value.limit.return_value.all.return_value = [mock_label]
        db.query.return_value.filter.return_value.all.return_value = [mock_label]

        result = match_and_score_labels(db, ["파이썬"], set(), set(), 10)
        assert len(result["suggestions"]) > 0
        assert result["suggestions"][0]["name"] == "파이썬"
        assert result["suggestions"][0]["source"] == "llm"

    def test_new_keywords_when_no_match(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.limit.return_value.all.return_value = []
        db.query.return_value.filter.return_value.all.return_value = []

        result = match_and_score_labels(db, ["새로운키워드"], set(), set(), 10)
        assert "새로운키워드" in result["new_keywords"]

    def test_excludes_existing_ids(self):
        db = MagicMock()
        mock_label = MagicMock()
        mock_label.id = 5
        mock_label.name = "기존라벨"
        mock_label.label_type = "keyword"

        db.query.return_value.filter.return_value.limit.return_value.all.return_value = [mock_label]
        db.query.return_value.filter.return_value.all.return_value = [mock_label]

        result = match_and_score_labels(db, ["기존라벨"], {5}, set(), 10)
        assert len(result["suggestions"]) == 0

    def test_confidence_decreasing(self):
        db = MagicMock()

        def make_label(id_, name):
            lb = MagicMock()
            lb.id = id_
            lb.name = name
            lb.label_type = "keyword"
            return lb

        labels_by_query = {
            "첫번째": [make_label(1, "첫번째")],
            "두번째": [make_label(2, "두번째")],
        }

        def mock_query(*args, **kwargs):
            q = MagicMock()
            def mock_filter(*a, **kw):
                f = MagicMock()
                def mock_limit(*la, **lkw):
                    r = MagicMock()
                    # ilike 필터에서 keyword를 추출
                    for key in labels_by_query:
                        r.all.return_value = labels_by_query.get(key, [])
                        return r
                    r.all.return_value = []
                    return r
                f.limit = mock_limit
                f.all.return_value = list(labels_by_query.values())[0] + list(labels_by_query.values())[1]
                return f
            q.filter = mock_filter
            return q

        # 간단한 검증: 첫 키워드의 confidence가 더 높음
        db2 = MagicMock()
        lb1 = make_label(1, "첫번째")
        lb2 = make_label(2, "두번째")

        def side_effect_filter(*args, **kwargs):
            f = MagicMock()
            f.limit.return_value.all.return_value = [lb1]
            f.all.return_value = [lb1, lb2]
            return f

        db2.query.return_value.filter = side_effect_filter

        result = match_and_score_labels(db2, ["첫번째", "두번째"], set(), set(), 10)
        if len(result["suggestions"]) >= 2:
            assert result["suggestions"][0]["confidence"] >= result["suggestions"][1]["confidence"]


class TestFallbackExtract:
    def test_without_recommend_fn(self):
        result = fallback_extract("파이썬 프로그래밍", None, set())
        assert result["suggestions"] == []
        assert len(result["new_keywords"]) > 0

    def test_with_recommend_fn(self):
        mock_fn = MagicMock(return_value=[{"label_id": 1, "name": "테스트"}])
        result = fallback_extract("파이썬 프로그래밍", None, set(), recommend_labels_fn=mock_fn)
        assert len(result["suggestions"]) == 1
        assert result["suggestions"][0]["name"] == "테스트"
        mock_fn.assert_called_once()


# ---------------------------------------------------------------------------
# ChunkLabelRecommender 테스트
# ---------------------------------------------------------------------------


class TestChunkLabelRecommender:
    def _make_recommender(self, db=None, hybrid_search=None):
        from backend.services.reasoning.chunk_label_recommender import ChunkLabelRecommender
        return ChunkLabelRecommender(
            db=db or MagicMock(),
            hybrid_search=hybrid_search or MagicMock(),
        )

    def test_empty_content(self):
        recommender = self._make_recommender()
        result = recommender.recommend(chunk_id=1, content="")
        assert result == {"suggestions": [], "new_keywords": []}

    def test_zero_limit(self):
        recommender = self._make_recommender()
        result = recommender.recommend(chunk_id=1, content="테스트 내용", limit=0)
        assert result == {"suggestions": [], "new_keywords": []}

    @patch("backend.services.reasoning.chunk_label_recommender.ChunkLabelRecommender._gather_keyword_context")
    @patch("backend.services.reasoning.recommendation_llm.generate_keywords_via_llm")
    @patch("backend.services.reasoning.recommendation_llm.resolve_model")
    def test_llm_generates_keywords(self, mock_resolve, mock_generate, mock_gather):
        mock_resolve.return_value = "test-model"
        mock_generate.return_value = ["딥러닝", "신경망", "머신러닝"]
        mock_gather.return_value = ""

        db = MagicMock()
        db.query.return_value.distinct.return_value.all.return_value = []
        db.query.return_value.filter.return_value.limit.return_value.all.return_value = []
        db.query.return_value.filter.return_value.all.return_value = []

        with patch("backend.services.ai.ollama_client.ollama_available", return_value=True):
            recommender = self._make_recommender(db=db)
            result = recommender.recommend(chunk_id=1, content="딥러닝에 대한 내용")

        assert "new_keywords" in result
        assert "suggestions" in result

    @patch("backend.services.ai.ollama_client.ollama_available", return_value=False)
    def test_ollama_unavailable_fallback(self, mock_avail):
        db = MagicMock()
        db.query.return_value.distinct.return_value.all.return_value = []

        recommender = self._make_recommender(db=db)
        result = recommender.recommend(chunk_id=1, content="테스트 콘텐츠 입니다")
        assert "suggestions" in result
        assert "new_keywords" in result

    def test_prompt_contains_chunk_context(self):
        """프롬프트에 '텍스트의 의미를 분석' 문구가 포함되는지 검증."""
        from backend.services.reasoning.chunk_label_recommender import ChunkLabelRecommender

        db = MagicMock()
        db.query.return_value.distinct.return_value.all.return_value = []
        db.query.return_value.filter.return_value.limit.return_value.all.return_value = []
        db.query.return_value.filter.return_value.all.return_value = []

        hybrid_search = MagicMock()
        hybrid_search.search_hybrid.return_value = []

        captured_prompt = {}

        def capture_generate(prompt, model):
            captured_prompt["value"] = prompt
            return ["테스트키워드"]

        with patch("backend.services.ai.ollama_client.ollama_available", return_value=True), \
             patch("backend.services.reasoning.recommendation_llm.resolve_model", return_value="m"), \
             patch("backend.services.reasoning.recommendation_llm.generate_keywords_via_llm", side_effect=capture_generate):
            recommender = ChunkLabelRecommender(db, hybrid_search)
            recommender.recommend(chunk_id=1, content="파이썬 딥러닝 튜토리얼")

        assert "텍스트의 의미를 분석" in captured_prompt.get("value", "")


# ---------------------------------------------------------------------------
# GroupKeywordRecommender 테스트
# ---------------------------------------------------------------------------


class TestGroupKeywordRecommender:
    def _make_recommender(self, db=None):
        from backend.services.reasoning.group_keyword_recommender import GroupKeywordRecommender
        return GroupKeywordRecommender(db=db or MagicMock())

    def test_empty_description(self):
        recommender = self._make_recommender()
        result = recommender.recommend(description="")
        assert result == {"suggestions": [], "new_keywords": []}

    def test_zero_limit(self):
        recommender = self._make_recommender()
        result = recommender.recommend(description="프로그래밍 언어", limit=0)
        assert result == {"suggestions": [], "new_keywords": []}

    @patch("backend.services.reasoning.recommendation_llm.generate_keywords_via_llm")
    @patch("backend.services.reasoning.recommendation_llm.resolve_model")
    def test_llm_generates_group_keywords(self, mock_resolve, mock_generate):
        mock_resolve.return_value = "test-model"
        mock_generate.return_value = ["python", "java", "javascript", "go"]

        db = MagicMock()
        db.query.return_value.distinct.return_value.all.return_value = []
        db.query.return_value.filter.return_value.limit.return_value.all.return_value = []
        db.query.return_value.filter.return_value.all.return_value = []

        with patch("backend.services.ai.ollama_client.ollama_available", return_value=True):
            recommender = self._make_recommender(db=db)
            result = recommender.recommend(description="프로그래밍 언어")

        assert "new_keywords" in result
        assert len(result["new_keywords"]) > 0

    @patch("backend.services.ai.ollama_client.ollama_available", return_value=False)
    def test_ollama_unavailable_fallback(self, mock_avail):
        db = MagicMock()
        db.query.return_value.distinct.return_value.all.return_value = []

        recommender = self._make_recommender(db=db)
        result = recommender.recommend(description="프로그래밍 언어 모음")
        assert "suggestions" in result
        assert "new_keywords" in result

    def test_existing_keyword_names_exclusion(self):
        """existing_keyword_names가 프롬프트에 포함되는지 검증."""
        from backend.services.reasoning.group_keyword_recommender import GroupKeywordRecommender

        db = MagicMock()
        db.query.return_value.distinct.return_value.all.return_value = []
        db.query.return_value.filter.return_value.limit.return_value.all.return_value = []
        db.query.return_value.filter.return_value.all.return_value = []

        captured_prompt = {}

        def capture_generate(prompt, model):
            captured_prompt["value"] = prompt
            return ["go", "rust"]

        with patch("backend.services.ai.ollama_client.ollama_available", return_value=True), \
             patch("backend.services.reasoning.recommendation_llm.resolve_model", return_value="m"), \
             patch("backend.services.reasoning.recommendation_llm.generate_keywords_via_llm", side_effect=capture_generate):
            recommender = GroupKeywordRecommender(db)
            recommender.recommend(
                description="프로그래밍 언어",
                existing_keyword_names=["python", "java"],
            )

        prompt_text = captured_prompt.get("value", "")
        assert "python" in prompt_text
        assert "java" in prompt_text
        assert "추천하지 마세요" in prompt_text

    def test_prompt_contains_group_context(self):
        """프롬프트에 '키워드 그룹의 설명' 문구가 포함되는지 검증."""
        from backend.services.reasoning.group_keyword_recommender import GroupKeywordRecommender

        db = MagicMock()
        db.query.return_value.distinct.return_value.all.return_value = []
        db.query.return_value.filter.return_value.limit.return_value.all.return_value = []
        db.query.return_value.filter.return_value.all.return_value = []

        captured_prompt = {}

        def capture_generate(prompt, model):
            captured_prompt["value"] = prompt
            return ["테스트"]

        with patch("backend.services.ai.ollama_client.ollama_available", return_value=True), \
             patch("backend.services.reasoning.recommendation_llm.resolve_model", return_value="m"), \
             patch("backend.services.reasoning.recommendation_llm.generate_keywords_via_llm", side_effect=capture_generate):
            recommender = GroupKeywordRecommender(db)
            recommender.recommend(description="SI 프로젝트 역할")

        assert "키워드 그룹의 설명" in captured_prompt.get("value", "")
