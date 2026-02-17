"""AI 질의응답 핸들러 (ai.py에서 분리)

컨텍스트 준비, 프롬프트 구성, 답변 생성, 후처리, 스트리밍 등의 비즈니스 로직.
"""
import json
import logging
import re
from typing import Optional, AsyncGenerator
from sqlalchemy.orm import Session

from backend.services.search.search_service import get_search_service
from backend.services.search.hybrid_search import get_hybrid_search_service
from backend.services.search.reranker import get_reranker
from backend.services.search.multi_hop_rag import get_multi_hop_rag
from backend.services.ai.ollama_client import ollama_generate, ollama_generate_stream
from backend.services.ai.context_manager import get_context_manager

logger = logging.getLogger(__name__)

# 유사도 임계값 (0.3 미만이면 관련성 낮음)
SIMILARITY_THRESHOLD = 0.3

AI_SYSTEM_PROMPT = """당신은 한국어 전용 AI 어시스턴트입니다. 다음 규칙을 반드시 지키세요:
- 반드시 한국어로만 답변하세요. 영어·중국어(中文)·일본어로 답변하지 마세요.
- 컨텍스트에 없는 내용은 추측하지 마세요.
- 구체적이고 간결하게 답변하세요.
- 불필요한 반복, 이모지, 장식적 표현을 피하세요.
- 영어 문장, 영어 설명, 코드 블록을 포함하지 마세요."""


# ---------------------------------------------------------------------------
# 컨텍스트 준비
# ---------------------------------------------------------------------------

def prepare_question_context(request) -> tuple:
    """질문 컨텍스트 준비 (기본: 의미 검색만)."""
    search_service = get_search_service()
    context_docs = []
    if request.context_enabled:
        context_docs = search_service.search_simple(
            request.question.strip(), top_k=request.top_k
        )
    MAX_CONTEXT_LENGTH = 1000
    context_text = ""
    sources = []
    current_length = 0
    has_relevant_context = False
    similar_docs = []
    for doc in context_docs:
        score = doc.get("score", 0.0)
        if score < SIMILARITY_THRESHOLD:
            similar_docs.append({"file": doc["file"], "score": score})
            continue
        has_relevant_context = True
        doc_content = doc.get("content", "")
        if len(doc_content) > 300:
            doc_content = doc_content[:297] + "..."
        doc_text = f"[{doc.get('file', '')}]\n{doc_content}\n\n"
        if current_length + len(doc_text) > MAX_CONTEXT_LENGTH:
            remaining = MAX_CONTEXT_LENGTH - current_length
            if remaining > 50:
                doc_text = doc_text[:remaining]
                context_text += doc_text
            break
        context_text += doc_text
        current_length += len(doc_text)
        sources.append({
            "file": doc.get("file", ""),
            "score": doc.get("score", 0),
            "snippet": doc.get("snippet", ""),
        })
    return context_docs, context_text, sources, has_relevant_context, similar_docs


def prepare_question_context_enhanced(request, db: Session) -> tuple:
    """질문 컨텍스트 준비 (Phase 9-3-3: Hybrid/Rerank/Multi-hop + ContextManager)."""
    if not request.context_enabled:
        return [], "", [], False, []
    question = request.question.strip()
    top_k = request.top_k
    context_docs: list = []

    if request.use_multihop and db:
        mh = get_multi_hop_rag()
        out = mh.search(db=db, question=question, initial_top_k=top_k)
        context_docs = out.get("chunks", [])
    elif request.search_mode == "hybrid" and db:
        hybrid_svc = get_hybrid_search_service()
        context_docs = hybrid_svc.search_hybrid(
            db=db, query=question, top_k=top_k
        )
    else:
        search_svc = get_search_service()
        result = search_svc.search(query=question, top_k=top_k, offset=0)
        context_docs = result.get("results", [])

    if request.use_reranking and context_docs:
        reranker_svc = get_reranker()
        context_docs = reranker_svc.rerank(
            query=question,
            candidates=context_docs,
            top_k=top_k,
            content_key="content",
        )
        for d in context_docs:
            d["score"] = d.get("final_score", d.get("score", 0))

    ctx_mgr = get_context_manager()
    built = ctx_mgr.build_context(
        question=question,
        search_results=context_docs,
        max_tokens=None,
        content_key="content",
        score_key="score",
    )
    context_text = built.get("context", "")
    chunks_used = built.get("chunks_used", [])
    has_relevant_context = bool(context_text.strip())
    sources = []
    for c in chunks_used:
        sources.append({
            "file": "",
            "score": c.get("relevance_score", 0),
            "snippet": (c.get("content") or "")[:200],
        })
    similar_docs = []
    for doc in context_docs:
        if doc.get("score", 0) < SIMILARITY_THRESHOLD:
            similar_docs.append({
                "file": doc.get("file", ""),
                "score": doc.get("score", 0),
            })
    return context_docs, context_text, sources, has_relevant_context, similar_docs


# ---------------------------------------------------------------------------
# 프롬프트 구성 / 후처리
# ---------------------------------------------------------------------------

def build_prompt(question: str, context_text: str, has_relevant_context: bool, similar_docs: list) -> str:
    """프롬프트 구성 -- 시스템 지시는 AI_SYSTEM_PROMPT로 분리됨."""
    if not context_text or not has_relevant_context:
        similar_docs_text = ""
        if similar_docs:
            similar_docs_text = "\n\n참고: 다음 문서들이 유사하지만 직접적인 답변을 제공하기에는 관련성이 낮습니다:\n"
            similar_docs_text += "\n".join([f"- {doc['file']} (유사도: {doc['score']*100:.1f}%)" for doc in similar_docs[:3]])

        return f"""질문: {question}
{similar_docs_text}
지식 베이스에 정보가 없으면 "질문하신 내용에 대한 정보가 지식 베이스에 없습니다."라고만 답변하세요."""
    else:
        return f"""컨텍스트:
{context_text}

질문: {question}

컨텍스트의 정보를 바탕으로만 답변하세요."""


def postprocess_answer(answer: str) -> str:
    """답변 후처리 -- System Prompt 분리 후 경량화 (Phase 13-5-3)."""
    answer = answer.strip()

    # 이모지 클러스터 제거
    answer = re.sub(r'([😊🤔💪📝🔍🤝💭🎉]+\s*)+', '', answer)

    # LLM이 프롬프트를 반복하는 경우 제거
    answer = re.sub(r'^(Please|You should|I\'m waiting|Your answer|This code)[\s\S]*?\.\s*', '', answer, flags=re.IGNORECASE)

    # 연속된 빈 줄 정리
    answer = re.sub(r'\n{3,}', '\n\n', answer)

    return answer.strip()


# ---------------------------------------------------------------------------
# AI 답변 생성
# ---------------------------------------------------------------------------

def generate_ai_answer(
    question: str,
    context_text: str,
    max_tokens: int,
    temperature: float,
    has_relevant_context: bool = True,
    similar_docs: list = None,
) -> str:
    """AI 답변 생성 (Ollama)"""
    if similar_docs is None:
        similar_docs = []

    prompt = build_prompt(question, context_text, has_relevant_context, similar_docs)
    prompt_length = len(prompt)
    logger.info(f"Ollama 답변 생성 시작 (질문: {question[:50]}..., 프롬프트 길이: {prompt_length}자, 관련 컨텍스트: {has_relevant_context})")

    if prompt_length > 1600 and has_relevant_context:
        logger.warning(f"프롬프트가 길어서 컨텍스트를 축소합니다 ({prompt_length}자 -> 1600자로 제한)")
        template_length = len(prompt) - len(context_text) - len(question)
        max_context = 1600 - template_length - len(question)
        if max_context > 0 and len(context_text) > max_context:
            context_text = context_text[:max_context] + "..."
            prompt = build_prompt(question, context_text, has_relevant_context, similar_docs)

    answer = ollama_generate(
        prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        top_k=40,
        top_p=0.9,
        repeat_penalty=1.2,
        system_prompt=AI_SYSTEM_PROMPT,
    )
    if answer is None:
        raise ValueError("Ollama 응답 없음")
    answer = postprocess_answer(answer)
    logger.info(f"Ollama 답변 생성 완료 (길이: {len(answer)} 문자)")

    min_length = 10 if not has_relevant_context else 20
    if not answer or len(answer.strip()) < min_length:
        logger.warning(f"Ollama 답변이 너무 짧거나 비어있음 (최소 길이: {min_length})")
        if not has_relevant_context:
            return "질문하신 내용에 대한 정보가 지식 베이스에 없습니다."
        raise ValueError("생성된 답변이 너무 짧습니다")

    return answer


def generate_fallback_answer(
    context_docs: list,
    has_model: bool,
    has_relevant_context: bool = False,
    similar_docs: list = None,
) -> str:
    """폴백 답변 생성"""
    if similar_docs is None:
        similar_docs = []

    if not has_relevant_context:
        if similar_docs:
            similar_docs_text = "\n\n참고: 다음 문서들이 유사하지만 직접적인 답변을 제공하기에는 관련성이 낮습니다:\n"
            similar_docs_text += "\n".join([f"- {doc['file']} (유사도: {doc['score']*100:.1f}%)" for doc in similar_docs[:3]])
            return f"질문하신 내용에 대한 정보가 지식 베이스에 없습니다.{similar_docs_text}"
        else:
            return "질문하신 내용에 대한 정보가 지식 베이스에 없습니다."

    if context_docs:
        if has_model:
            return f"관련 문서 {len(context_docs)}개를 찾았습니다. 위의 컨텍스트를 참고하세요.\n\n참고: AI 모델 응답 생성에 실패했습니다."
        else:
            return f"""관련 문서 {len(context_docs)}개를 찾았습니다.

참고 문서:
{chr(10).join([f"- {doc['file']} (유사도: {doc['score']*100:.1f}%)" for doc in context_docs[:5]])}

위의 컨텍스트를 참고하여 질문에 답변하세요.

참고: AI 모델이 설치되지 않아 추론적 답변을 생성할 수 없습니다. Ollama를 실행하고 모델(eeve-korean 등)을 로드하면 더 상세한 답변을 받을 수 있습니다."""
    else:
        if has_model:
            return "관련 문서를 찾을 수 없습니다.\n\n참고: AI 모델 응답 생성에 실패했습니다."
        else:
            return "관련 문서를 찾을 수 없습니다.\n\n참고: AI 모델이 설치되지 않아 추론적 답변을 생성할 수 없습니다."


# ---------------------------------------------------------------------------
# 스트리밍 답변
# ---------------------------------------------------------------------------

async def generate_streaming_answer(
    question: str,
    context_text: str,
    max_tokens: int,
    temperature: float,
    has_relevant_context: bool = True,
    similar_docs: list = None,
) -> AsyncGenerator[str, None]:
    """True Streaming AI 답변 생성 -- Ollama 토큰 즉시 SSE 전달 (Phase 13-5-1)."""
    if similar_docs is None:
        similar_docs = []
    prompt = build_prompt(question, context_text, has_relevant_context, similar_docs)

    try:
        for token in ollama_generate_stream(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_k=40,
            top_p=0.9,
            repeat_penalty=1.2,
            system_prompt=AI_SYSTEM_PROMPT,
        ):
            data = {"type": "chunk", "content": token}
            yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
        data = {"type": "done", "content": ""}
        yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
    except Exception as e:
        error_data = {"type": "error", "content": str(e)}
        yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
