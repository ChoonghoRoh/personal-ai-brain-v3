"""LLM 기반 동적 추론 서비스 — 모드별 프롬프트·Ollama 호출 (Phase 9-3-1)"""
import logging
import re
from typing import List, Dict, Optional, Generator

logger = logging.getLogger(__name__)

# 컨텍스트가 없을 때(질문과 관련 지식 0건) 사용하는 프롬프트 — 질문별로 다른 안내 생성
# 언어: 한국어 전용. 중국어(中文) 사용 금지 (Phase 9 reasoning language improvement)
NO_CONTEXT_PROMPT = """다음 사용자 질문에 대해, 현재 지식베이스에서 관련 내용을 찾지 못했습니다.
질문: {question}

위 질문에 대해 "해당 주제에 대한 지식이 수집되어 있지 않습니다"를 안내하고, 다른 질문 시도나 보조 조회(프로젝트·라벨 선택)를 권유하는 짧은 답변을 반드시 한국어로만 하세요. 중국어(中文)로 답변하지 마세요. 질문 내용을 그대로 인용해 언급하세요."""

# design_explain 모드 + 컨텍스트 없음: 짧은 안내 + Mermaid 다이어그램 예시 포함 (Phase 10-2-1 다이어그램 테스트)
NO_CONTEXT_DESIGN_EXPLAIN_PROMPT = """다음 사용자 질문에 대해, 현재 지식베이스에서 관련 내용을 찾지 못했습니다.
질문: {question}

1) 위 질문에 대해 "해당 주제에 대한 지식이 수집되어 있지 않습니다"를 한 문장으로 안내하고, 다른 질문 시도나 보조 조회를 권유하세요. 반드시 한국어로만 하세요. 중국어(中文)로 답변하지 마세요.

2) 그 다음 줄에, 일반적인 웹/소프트웨어 아키텍처를 보여주는 Mermaid flowchart를 반드시 포함하세요. 다음 형식으로만 작성하세요:

```mermaid
flowchart LR
  A[사용자] --> B[프론트엔드]
  B --> C[백엔드]
  C --> D[DB]
```

위와 같이 ```mermaid 로 시작하고 ``` 로 끝나는 코드 블록 하나를 반드시 포함하세요."""

# 모든 모드 공통: 한국어만 사용, 중국어(中文) 사용 금지
MODE_PROMPTS = {
    "design_explain": """당신은 소프트웨어 아키텍트입니다. 반드시 한국어로만 답변하세요. 중국어(中文)로 답변하지 마세요.
주어진 질문에 직접 답변하고, 다음 컨텍스트를 바탕으로 설계 의도와 배경을 설명하세요.

컨텍스트:
{context}

질문: {question}

위 질문에 직접 답변하세요. 한국어로만 답변하세요.

추가 요청: 답변 마지막에 설계 구조나 컴포넌트/모듈 관계를 보여주는 Mermaid 다이어그램을 반드시 포함하세요. 다음 형식으로만 작성하세요 (다른 설명 없이 코드 블록만):

```mermaid
flowchart LR
  A[요소A] --> B[요소B]
  B --> C[요소C]
```

또는 flowchart TB, graph LR, diagram 등 Mermaid 문법을 사용하세요. 반드시 ```mermaid 로 시작하고 ``` 로 끝나는 코드 블록 하나를 포함하세요.""",
    "risk_review": """당신은 리스크 분석가입니다. 반드시 한국어로만 답변하세요. 중국어(中文)로 답변하지 마세요.
주어진 질문에 직접 답변하고, 다음 컨텍스트에서 잠재적 위험과 고려사항을 분석하세요.

컨텍스트:
{context}

질문: {question}

위 질문에 직접 답변하세요. 한국어로만 답변하세요:""",
    "next_steps": """당신은 프로젝트 매니저입니다. 반드시 한국어로만 답변하세요. 중국어(中文)로 답변하지 마세요.
주어진 질문에 직접 답변하고, 다음 컨텍스트를 바탕으로 다음 단계를 제안하세요.

컨텍스트:
{context}

질문: {question}

위 질문에 직접 답변하세요. 한국어로만 답변하세요:""",
    "history_trace": """당신은 기술 문서 전문가입니다. 반드시 한국어로만 답변하세요. 중국어(中文)로 답변하지 마세요.
주어진 질문에 직접 답변하고, 다음 컨텍스트에서 히스토리와 맥락을 추적하여 설명하세요.

컨텍스트:
{context}

질문: {question}

위 질문에 직접 답변하세요. 한국어로만 답변하세요:""",
}


class DynamicReasoningService:
    """LLM 기반 동적 추론. 실패 시 템플릿 폴백."""

    def _is_ollama_available(self) -> bool:
        try:
            from backend.services.ai.ollama_client import ollama_available
            return ollama_available()
        except Exception:
            return False

    def _build_reasoning_prompt(
        self,
        question: Optional[str],
        context: str,
        mode: str,
    ) -> str:
        """모드별 프롬프트 구성. 컨텍스트가 비어 있으면 질문에 맞는 '관련 지식 없음' 안내용 프롬프트 사용."""
        q = (question or "").strip() or "위 컨텍스트를 요약·설명해 주세요."
        if not (context and context.strip()):
            if mode == "design_explain":
                return NO_CONTEXT_DESIGN_EXPLAIN_PROMPT.format(question=q)
            return NO_CONTEXT_PROMPT.format(question=q)
        template = MODE_PROMPTS.get(mode, MODE_PROMPTS["design_explain"])
        if len(context) > 3000:
            context = context[:3000] + "\n..."
        return template.format(context=context, question=q)

    def _postprocess_reasoning(self, raw: str) -> str:
        """생성 텍스트 후처리. 중국어(한자) 비중이 높은 문단 제거(한국어 전용 유도)."""
        if not raw:
            return ""
        text = raw.strip()
        text = re.sub(r"\n{3,}", "\n\n", text)
        # 중국어(한자) 비중이 높은 문단 제거: 문단별 한자 수 / (한글+한자) 비율이 높으면 제거
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        filtered = []
        for para in paragraphs:
            cjk = len(re.findall(r"[\u4e00-\u9fff\u3400-\u4dbf]", para))  # 한자
            korean = len(re.findall(r"[가-힣]", para))
            total_lang = cjk + korean
            if total_lang == 0:
                filtered.append(para)  # 한글/한자 없으면 그대로 유지
            elif korean >= cjk or cjk / total_lang < 0.6:
                filtered.append(para)  # 한글이 많거나 한자 비율 60% 미만이면 유지
            # else: 한자 비중이 높은 문단은 제거 (중국어 출력 억제)
        text = "\n\n".join(filtered).strip()
        return text.strip()

    def generate_reasoning(
        self,
        question: Optional[str],
        context_chunks: List[Dict],
        mode: str,
        max_tokens: int = 500,
        model: Optional[str] = None,
    ) -> Optional[str]:
        """LLM으로 추론 답변 생성. model이 있으면 해당 Ollama 모델 사용. 실패 시 None (호출측에서 템플릿 폴백)."""
        if mode == "design_explain" and max_tokens < 800:
            max_tokens = 800  # Mermaid 블록 포함을 위해 여유 확보 (Phase 10-2-1)
        context_parts = []
        for c in context_chunks:
            content = c.get("content") or c.get("content_preview") or ""
            if content:
                context_parts.append(content)
        context_text = "\n\n".join(context_parts)
        prompt = self._build_reasoning_prompt(question, context_text, mode)
        try:
            from backend.services.ai.ollama_client import ollama_generate
            raw = ollama_generate(
                prompt,
                max_tokens=max_tokens,
                temperature=0.7,
                model=model,
            )
            if not raw:
                return None
            return self._postprocess_reasoning(raw)
        except Exception as e:
            logger.warning("DynamicReasoningService generate_reasoning failed: %s", e)
            return None


    def generate_reasoning_stream(
        self,
        question: Optional[str],
        context_chunks: List[Dict],
        mode: str,
        max_tokens: int = 500,
        model: Optional[str] = None,
    ) -> Generator[str, None, None]:
        """LLM으로 추론 답변을 토큰 단위로 스트리밍 (Phase 10-4-1). 실패 시 빈 제너레이터."""
        if mode == "design_explain" and max_tokens < 800:
            max_tokens = 800
        context_parts = []
        for c in context_chunks:
            content = c.get("content") or c.get("content_preview") or ""
            if content:
                context_parts.append(content)
        context_text = "\n\n".join(context_parts)
        prompt = self._build_reasoning_prompt(question, context_text, mode)
        try:
            from backend.services.ai.ollama_client import ollama_generate_stream
            yield from ollama_generate_stream(
                prompt,
                max_tokens=max_tokens,
                temperature=0.7,
                model=model,
            )
        except Exception as e:
            logger.warning("DynamicReasoningService generate_reasoning_stream failed: %s", e)


def get_dynamic_reasoning_service() -> DynamicReasoningService:
    """DynamicReasoningService 인스턴스 반환."""
    return DynamicReasoningService()
