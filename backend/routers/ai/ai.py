"""AI API 라우터 -- Ollama 로컬 LLM (EEVE-Korean 등) 사용"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
import logging
import json

from backend.services.ai.ollama_client import ollama_available, ollama_connection_check
from backend.models.database import get_db

# --- 핸들러 import (ai_handlers.py) ---
from backend.routers.ai.ai_handlers import (
    prepare_question_context,
    prepare_question_context_enhanced,
    build_prompt,
    postprocess_answer,
    generate_ai_answer,
    generate_fallback_answer,
    generate_streaming_answer,
    AI_SYSTEM_PROMPT,
    SIMILARITY_THRESHOLD,
)

router = APIRouter(prefix="/api/ask", tags=["AI"])

logger = logging.getLogger(__name__)


# --- Pydantic 모델 ---

class AskRequest(BaseModel):
    question: str
    context_enabled: bool = True
    top_k: int = 5
    max_tokens: int = 500
    temperature: float = 0.7
    # Phase 9-3-3: RAG 개선 옵션
    search_mode: str = "semantic"  # semantic | hybrid
    use_reranking: bool = False
    use_multihop: bool = False


class AskResponse(BaseModel):
    answer: str
    context: list
    sources: list
    model_used: Optional[str] = None
    error: Optional[str] = None
    ollama_feedback: Optional[dict] = None


# --- 엔드포인트 ---

@router.post(
    "",
    summary="AI 질의 응답",
    description="지식베이스 컨텍스트를 활용한 AI 질의응답. search_mode(semantic|hybrid), use_reranking, use_multihop 옵션 지원.",
    responses={
        200: {"description": "성공 (AskResponse)"},
        400: {"description": "질문 누락 또는 잘못된 요청"},
        500: {"description": "AI 응답 생성 오류"},
    },
)
async def ask_question(
    request: AskRequest,
    db: Session = Depends(get_db),
) -> AskResponse:
    """AI 질의 응답 (Phase 9-3-3: search_mode, use_reranking, use_multihop 지원)."""
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="질문을 입력하세요")

    try:
        use_enhanced = (
            request.search_mode == "hybrid"
            or request.use_reranking
            or request.use_multihop
        )
        if use_enhanced:
            context_docs, context_text, sources, has_relevant_context, similar_docs = (
                prepare_question_context_enhanced(request, db)
            )
        else:
            context_docs, context_text, sources, has_relevant_context, similar_docs = (
                prepare_question_context(request)
            )

        # 컨텍스트가 없으면 AI 모델을 호출하지 않고 직접 답변 반환
        if not has_relevant_context:
            logger.info(f"관련 컨텍스트가 없어 AI 모델을 호출하지 않고 직접 답변 반환 (질문: {request.question[:50]}...)")
            answer = generate_fallback_answer(context_docs, False, has_relevant_context, similar_docs)
            return AskResponse(
                answer=answer,
                context=context_docs,
                sources=sources,
                model_used=None,
                error=None,
            )

        # Ollama 응답 생성
        answer = ""
        model_used = None
        error_message = None

        if ollama_available():
            try:
                answer = generate_ai_answer(
                    request.question,
                    context_text,
                    request.max_tokens,
                    request.temperature,
                    has_relevant_context,
                    similar_docs,
                )
                model_used = "ollama"
            except Exception as e:
                error_str = str(e)
                if "context window" in error_str.lower() or "exceeds" in error_str.lower():
                    error_message = f"프롬프트가 너무 깁니다. 컨텍스트 문서를 줄이거나 질문을 더 구체적으로 해주세요. (오류: {error_str})"
                    logger.warning(f"컨텍스트 윈도우 초과: {error_str}")
                    if context_docs and has_relevant_context:
                        reduced_context = context_text[:600] if len(context_text) > 600 else context_text
                        try:
                            from backend.services.ai.ollama_client import ollama_generate
                            reduced_prompt = build_prompt(request.question, reduced_context, has_relevant_context, similar_docs)
                            logger.info("컨텍스트를 줄여서 재시도 중...")
                            answer = ollama_generate(
                                reduced_prompt,
                                max_tokens=request.max_tokens,
                                temperature=request.temperature,
                                top_k=40,
                                top_p=0.9,
                                repeat_penalty=1.2,
                            )
                            if answer:
                                answer = postprocess_answer(answer)
                                model_used = "ollama"
                                error_message = None
                                logger.info("컨텍스트 축소 후 재시도 성공")
                            else:
                                raise ValueError("Ollama 응답 없음")
                        except Exception as retry_e:
                            logger.error(f"재시도도 실패: {retry_e}")
                            error_message = f"프롬프트가 너무 깁니다. 컨텍스트 문서를 줄이거나 질문을 더 구체적으로 해주세요."
                            answer = generate_fallback_answer(context_docs, True, has_relevant_context, similar_docs)
                else:
                    error_message = f"Ollama 답변 생성 중 오류: {error_str}"
                    logger.error(error_message, exc_info=True)
                    answer = generate_fallback_answer(context_docs, True, has_relevant_context, similar_docs)
        else:
            ollama_feedback = ollama_connection_check()
            logger.warning("Ollama를 사용할 수 없어 기본 응답 생성: %s", ollama_feedback.get("message"))
            answer = generate_fallback_answer(context_docs, False, has_relevant_context, similar_docs)
            error_message = ollama_feedback.get("message") or "Ollama를 사용할 수 없습니다"
            return AskResponse(
                answer=answer,
                context=context_docs,
                sources=sources,
                model_used=model_used,
                error=error_message,
                ollama_feedback=ollama_feedback,
            )

        ollama_feedback = ollama_connection_check()
        return AskResponse(
            answer=answer,
            context=context_docs,
            sources=sources,
            model_used=model_used,
            error=error_message,
            ollama_feedback=ollama_feedback if not ollama_feedback.get("available") else None,
        )

    except Exception as e:
        logger.error(f"AI 응답 생성 오류: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"AI 응답 생성 오류: {str(e)}")


@router.post(
    "/stream",
    summary="AI 질의 응답 (스트리밍)",
    description="SSE 스트리밍으로 AI 답변을 청크 단위로 반환. search_mode, use_reranking, use_multihop 지원.",
    responses={
        200: {"description": "성공 (SSE 스트림)"},
        400: {"description": "질문 누락"},
        500: {"description": "AI 응답 생성 오류"},
    },
)
async def ask_question_stream(
    request: AskRequest,
    db: Session = Depends(get_db),
):
    """AI 질의 응답 (스트리밍, Phase 9-3-3: search_mode/use_reranking/use_multihop 지원)."""
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="질문을 입력하세요")

    use_enhanced = (
        request.search_mode == "hybrid"
        or request.use_reranking
        or request.use_multihop
    )

    async def generate():
        try:
            if use_enhanced:
                context_docs, context_text, sources, has_relevant_context, similar_docs = (
                    prepare_question_context_enhanced(request, db)
                )
            else:
                context_docs, context_text, sources, has_relevant_context, similar_docs = (
                    prepare_question_context(request)
                )

            # 소스 정보 전송
            sources_data = {
                "type": "sources",
                "content": sources,
            }
            yield f"data: {json.dumps(sources_data, ensure_ascii=False)}\n\n"

            # 컨텍스트가 없으면 AI 모델을 호출하지 않고 직접 답변 반환
            if not has_relevant_context:
                answer = generate_fallback_answer(context_docs, False, has_relevant_context, similar_docs)
                for i in range(0, len(answer), 10):
                    chunk = answer[i:i + 10]
                    data = {
                        "type": "chunk",
                        "content": chunk,
                    }
                    yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

                data = {
                    "type": "done",
                    "content": "",
                }
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                return

            if ollama_available():
                async for chunk in generate_streaming_answer(
                    request.question,
                    context_text,
                    request.max_tokens,
                    request.temperature,
                    has_relevant_context,
                    similar_docs,
                ):
                    yield chunk
            else:
                ollama_feedback = ollama_connection_check()
                feedback_data = {"type": "ollama_feedback", "content": ollama_feedback}
                yield f"data: {json.dumps(feedback_data, ensure_ascii=False)}\n\n"
                answer = generate_fallback_answer(
                    context_docs, False, has_relevant_context, similar_docs
                )
                for i in range(0, len(answer), 10):
                    chunk = answer[i:i + 10]
                    data = {
                        "type": "chunk",
                        "content": chunk,
                    }
                    yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

                data = {
                    "type": "done",
                    "content": "",
                }
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

        except Exception as e:
            error_data = {
                "type": "error",
                "content": str(e),
            }
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
