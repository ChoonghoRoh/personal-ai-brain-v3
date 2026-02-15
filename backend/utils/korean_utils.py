"""한글 LLM 출력 후처리 유틸리티."""
import re
import unicodedata
from typing import List


def _chinese_ratio(text: str) -> float:
    """텍스트 내 한자(CJK Unified Ideographs) 비율 반환 (0.0~1.0)."""
    if not text:
        return 0.0
    cjk_count = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
    return cjk_count / len(text)


_ENGLISH_NOISE_PATTERNS = re.compile(
    r"^(please|here are|keywords?:|the following|below|note:|"
    r"i have|i will|let me|sure|certainly|of course|"
    r"based on|according to|as requested)",
    re.IGNORECASE,
)

_EMOJI_RE = re.compile(
    "["
    "\U0001f600-\U0001f64f"
    "\U0001f300-\U0001f5ff"
    "\U0001f680-\U0001f6ff"
    "\U0001f1e0-\U0001f1ff"
    "\U00002702-\U000027b0"
    "\U0001f900-\U0001f9ff"
    "\U0001fa00-\U0001fa6f"
    "\U0001fa70-\U0001faff"
    "\U00002600-\U000026ff"
    "]+",
    flags=re.UNICODE,
)


def postprocess_korean_keywords(raw_text: str) -> List[str]:
    """LLM 키워드 추출 응답을 정리하여 한글/영어 키워드 리스트로 반환.

    처리 흐름:
    1. 줄바꿈 분리 -> 쉼표/세미콜론 폴백
    2. 불릿/번호 제거
    3. 중국어 비율 높은 키워드 제거 (30%+)
    4. 영어 문장 패턴 제거
    5. 2자 미만 필터링
    """
    if not raw_text or not raw_text.strip():
        return []

    text = raw_text.strip()

    # 줄바꿈 분리
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]

    # 줄바꿈으로 키워드가 하나도 안 나오면 쉼표/세미콜론 폴백
    if len(lines) <= 1:
        for sep in (",", ";", "\u3001"):  # \u3001 = 、
            if sep in text:
                lines = [x.strip() for x in text.split(sep) if x.strip()]
                break

    result: List[str] = []
    seen_lower: set = set()

    for line in lines:
        # 불릿/번호 제거
        kw = line.lstrip("-*\u2022\u25cb\u25cf0123456789.) \t")
        kw = kw.strip()

        if not kw or len(kw) < 2:
            continue

        # 중국어 비율 30%+ 제거
        if _chinese_ratio(kw) >= 0.3:
            continue

        # 영어 문장 패턴 제거
        if _ENGLISH_NOISE_PATTERNS.match(kw):
            continue

        # 이모지 제거
        kw = _EMOJI_RE.sub("", kw).strip()
        if not kw or len(kw) < 2:
            continue

        # 중복 방지
        kw_lower = kw.lower()
        if kw_lower in seen_lower:
            continue
        seen_lower.add(kw_lower)

        result.append(kw)

    return result


def postprocess_korean_text(raw_text: str) -> str:
    """자유형 한글 LLM 출력을 정리.

    처리 흐름:
    1. 중국어 비율 높은 문단 제거 (60%+)
    2. 영어 전용 줄 제거
    3. 이모지 클러스터 제거
    4. 연속 빈 줄 정리
    """
    if not raw_text or not raw_text.strip():
        return ""

    lines = raw_text.split("\n")
    cleaned: List[str] = []

    for line in lines:
        stripped = line.strip()

        # 빈 줄은 일단 유지
        if not stripped:
            cleaned.append("")
            continue

        # 중국어 비율 60%+ 문단 제거
        if _chinese_ratio(stripped) >= 0.6:
            continue

        # 영어 전용 줄 제거 (한글이 하나도 없고 ASCII 알파벳만)
        has_korean = bool(re.search(r"[가-힣]", stripped))
        is_english_only = bool(re.match(r"^[a-zA-Z\s\d.,!?;:\-\'\"()\[\]{}/@#$%^&*+=<>~`]+$", stripped))
        if not has_korean and is_english_only and len(stripped) > 5:
            continue

        # 이모지 클러스터 제거
        line_cleaned = _EMOJI_RE.sub("", line).rstrip()
        cleaned.append(line_cleaned)

    # 연속 빈 줄 정리 (최대 1개)
    result_lines: List[str] = []
    prev_empty = False
    for line in cleaned:
        if not line.strip():
            if prev_empty:
                continue
            prev_empty = True
        else:
            prev_empty = False
        result_lines.append(line)

    # 앞뒤 빈 줄 제거
    text = "\n".join(result_lines).strip()
    return text
