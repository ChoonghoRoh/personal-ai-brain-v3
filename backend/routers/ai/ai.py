"""AI API 라우터 — Ollama 로컬 LLM (EEVE-Korean 등) 사용"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, AsyncGenerator
from sqlalchemy.orm import Session
import logging
import json

from backend.services.search.search_service import get_search_service
from backend.services.search.hybrid_search import get_hybrid_search_service
from backend.services.search.reranker import get_reranker
from backend.services.search.multi_hop_rag import get_multi_hop_rag
from backend.services.ai.ollama_client import ollama_generate, ollama_available, ollama_connection_check
from backend.services.ai.context_manager import get_context_manager
from backend.models.database import get_db

router = APIRouter(prefix="/api/ask", tags=["ai"])

logger = logging.getLogger(__name__)

# 유사도 임계값 (0.3 미만이면 관련성 낮음)
SIMILARITY_THRESHOLD = 0.3


class AskRequest(BaseModel):
    question: str
    context_enabled: bool = True
    top_k: int = 5
    max_tokens: int = 500  # 기본값 증가
    temperature: float = 0.7
    # Phase 9-3-3: RAG 개선 옵션 (기본값 = 기존 동작 유지)
    search_mode: str = "semantic"  # semantic | hybrid
    use_reranking: bool = False
    use_multihop: bool = False


class AskResponse(BaseModel):
    answer: str
    context: list
    sources: list
    model_used: Optional[str] = None  # 사용된 모델 정보
    error: Optional[str] = None  # 오류 정보 (있는 경우)
    ollama_feedback: Optional[dict] = None  # Ollama 연결 테스트 결과 (available, message, detail) — 꺼져 있으면 피드백에 활용


def prepare_question_context(request: AskRequest) -> tuple:
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


def prepare_question_context_enhanced(request: AskRequest, db: Session) -> tuple:
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
            "file": "",  # chunks_used에는 file이 없을 수 있음
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


def build_prompt(question: str, context_text: str, has_relevant_context: bool, similar_docs: list) -> str:
    """프롬프트 구성"""
    if not context_text or not has_relevant_context:
        # 컨텍스트가 없거나 관련성이 낮은 경우
        similar_docs_text = ""
        if similar_docs:
            similar_docs_text = "\n\n참고: 다음 문서들이 유사하지만 직접적인 답변을 제공하기에는 관련성이 낮습니다:\n"
            similar_docs_text += "\n".join([f"- {doc['file']} (유사도: {doc['score']*100:.1f}%)" for doc in similar_docs[:3]])
        
        return f"""당신은 한국어로만 답변하는 AI 어시스턴트입니다. 절대로 영어로 답변하지 마세요.

질문: {question}

중요 지시사항:
1. 반드시 한국어로만 답변하세요. 영어·중국어(中文)로 답변하지 마세요.
2. 질문에 대한 정보가 지식 베이스에 없으면 "질문하신 내용에 대한 정보가 지식 베이스에 없습니다."라고만 답변하세요.
3. 일반적인 지식이나 추측으로 답변하지 마세요.
4. 컨텍스트가 없으면 절대 답변을 만들어내지 마세요.
5. 영어 문장, 영어 설명, 영어 코드 주석을 포함하지 마세요.{similar_docs_text}

한국어로만 답변하세요:"""
    else:
        # 관련 컨텍스트가 있는 경우
        return f"""당신은 한국어로만 답변하는 AI 어시스턴트입니다. 절대로 영어로 답변하지 마세요.

컨텍스트:
{context_text}

질문: {question}

중요 지시사항:
1. 반드시 한국어로만 답변하세요. 영어·중국어(中文)로 답변하지 마세요.
2. 컨텍스트의 정보를 바탕으로만 답변하세요.
3. 컨텍스트에 없는 내용은 추측하지 마세요.
4. 구체적이고 실용적인 답변을 제공하세요.
5. 불필요한 반복, 이모지, 장식적인 표현을 피하세요.
6. 답변은 간결하고 명확하게 작성하세요.
7. 영어 문장, 영어 설명, 영어 코드 주석을 포함하지 마세요.

한국어로만 답변하세요:"""


def postprocess_answer(answer: str) -> str:
    """답변 후처리"""
    import re
    answer = answer.strip()
    
    # 코드 블록 제거 (```python, ``` 등)
    answer = re.sub(r'```[\s\S]*?```', '', answer)
    answer = re.sub(r'`[^`]+`', '', answer)
    
    # 영어 지시사항 패턴 제거
    answer = re.sub(r'Please respond in Korean[\s\S]*?You should[\s\S]*?\.', '', answer, flags=re.IGNORECASE)
    answer = re.sub(r'Please respond[\s\S]*?\.', '', answer, flags=re.IGNORECASE)
    answer = re.sub(r'I\'m waiting[\s\S]*?\.', '', answer, flags=re.IGNORECASE)
    answer = re.sub(r'You should only[\s\S]*?\.', '', answer, flags=re.IGNORECASE)
    answer = re.sub(r'Your answer should[\s\S]*?\.', '', answer, flags=re.IGNORECASE)
    
    # 영어 문장 제거 (대문자로 시작하고 마침표로 끝나는 영어 문장)
    # 단, 한국어와 섞인 경우는 보존
    lines = answer.split('\n')
    filtered_lines = []
    for line in lines:
        # 영어만 있는 줄 제거 (한국어가 포함된 줄은 보존)
        if re.match(r'^[A-Z][^가-힣]*[.!?]\s*$', line.strip()) and not re.search(r'[가-힣]', line):
            continue
        # "Please", "You should", "I'm waiting" 등으로 시작하는 줄 제거
        if re.match(r'^(Please|You should|I\'m waiting|Your answer)', line.strip(), re.IGNORECASE):
            continue
        filtered_lines.append(line)
    answer = '\n'.join(filtered_lines)
    
    # 불필요한 패턴 제거
    answer = re.sub(r'\(토큰 제한 고려하여[^)]*\)\s*💪', '', answer)
    answer = re.sub(r'💪\s*$', '', answer)
    answer = re.sub(r'\.\.\.\s*\(과정을 재현\)\s*💭', '', answer)
    answer = re.sub(r'([😊🤔💪📝🔍🤝💭🎉]+\s*)+', '', answer)
    
    # "This code", "This function" 같은 영어 설명 제거
    answer = re.sub(r'This (code|function|method|class)[\s\S]*?\.', '', answer, flags=re.IGNORECASE)
    answer = re.sub(r'This defines[\s\S]*?\.', '', answer, flags=re.IGNORECASE)
    
    # "import"로 시작하는 줄 제거 (코드 예제)
    lines = answer.split('\n')
    filtered_lines = []
    for line in lines:
        if not line.strip().startswith('import ') and not line.strip().startswith('def ') and not line.strip().startswith('class '):
            filtered_lines.append(line)
    answer = '\n'.join(filtered_lines)
    
    # 연속된 빈 줄 정리
    answer = re.sub(r'\n{3,}', '\n\n', answer)
    
    # 앞뒤 공백 제거
    answer = answer.strip()
    
    # 영어만 있는 문단 제거 (한국어가 전혀 없는 경우)
    paragraphs = answer.split('\n\n')
    filtered_paragraphs = []
    for para in paragraphs:
        if re.search(r'[가-힣]', para):  # 한국어가 포함된 문단만 보존
            filtered_paragraphs.append(para)
        elif not re.match(r'^[A-Z][^가-힣]*[.!?]\s*$', para.strip()):  # 영어 문장이 아닌 경우도 보존
            filtered_paragraphs.append(para)
    answer = '\n\n'.join(filtered_paragraphs)
    
    return answer.strip()


def generate_ai_answer(
    question: str,
    context_text: str,
    max_tokens: int,
    temperature: float,
    has_relevant_context: bool = True,
    similar_docs: list = None
) -> str:
    """AI 답변 생성 (Ollama)"""
    if similar_docs is None:
        similar_docs = []
    
    prompt = build_prompt(question, context_text, has_relevant_context, similar_docs)
    prompt_length = len(prompt)
    logger.info(f"Ollama 답변 생성 시작 (질문: {question[:50]}..., 프롬프트 길이: {prompt_length}자, 관련 컨텍스트: {has_relevant_context})")
    
    # 프롬프트가 너무 길면 경고 및 자동 축소
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
    )
    if answer is None:
        raise ValueError("Ollama 응답 없음")
    answer = postprocess_answer(answer)
    logger.info(f"Ollama 답변 생성 완료 (길이: {len(answer)} 문자)")
    
    # 컨텍스트가 없을 때는 짧은 답변도 허용
    min_length = 10 if not has_relevant_context else 20
    if not answer or len(answer.strip()) < min_length:
        logger.warning(f"Ollama 답변이 너무 짧거나 비어있음 (최소 길이: {min_length})")
        if not has_relevant_context:
            return "질문하신 내용에 대한 정보가 지식 베이스에 없습니다."
        raise ValueError("생성된 답변이 너무 짧습니다")
    
    return answer


def generate_fallback_answer(context_docs: list, has_model: bool, has_relevant_context: bool = False, similar_docs: list = None) -> str:
    """폴백 답변 생성"""
    if similar_docs is None:
        similar_docs = []
    
    if not has_relevant_context:
        # 관련 컨텍스트가 없는 경우
        if similar_docs:
            similar_docs_text = "\n\n참고: 다음 문서들이 유사하지만 직접적인 답변을 제공하기에는 관련성이 낮습니다:\n"
            similar_docs_text += "\n".join([f"- {doc['file']} (유사도: {doc['score']*100:.1f}%)" for doc in similar_docs[:3]])
            return f"질문하신 내용에 대한 정보가 지식 베이스에 없습니다.{similar_docs_text}"
        else:
            return "질문하신 내용에 대한 정보가 지식 베이스에 없습니다."
    
    # 관련 컨텍스트가 있는 경우
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
                error=None
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
                    similar_docs
                )
                model_used = "ollama"
            except Exception as e:
                error_str = str(e)
                # 컨텍스트 윈도우 초과 오류인 경우 특별 처리
                if "context window" in error_str.lower() or "exceeds" in error_str.lower():
                    error_message = f"프롬프트가 너무 깁니다. 컨텍스트 문서를 줄이거나 질문을 더 구체적으로 해주세요. (오류: {error_str})"
                    logger.warning(f"컨텍스트 윈도우 초과: {error_str}")
                    # 컨텍스트를 더 줄여서 재시도
                    if context_docs and has_relevant_context:
                        reduced_context = context_text[:600] if len(context_text) > 600 else context_text
                        try:
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
            # Ollama를 사용할 수 없는 경우 — 공통 연결 테스트 결과를 피드백에 포함
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


async def generate_streaming_answer(
    question: str,
    context_text: str,
    max_tokens: int,
    temperature: float,
    has_relevant_context: bool = True,
    similar_docs: list = None
) -> AsyncGenerator[str, None]:
    """스트리밍 AI 답변 생성 (Ollama 전체 응답 후 청크로 스트리밍)"""
    if similar_docs is None:
        similar_docs = []
    prompt = build_prompt(question, context_text, has_relevant_context, similar_docs)
    
    try:
        answer = ollama_generate(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_k=40,
            top_p=0.9,
            repeat_penalty=1.2,
        )
        if answer is None:
            answer = ""
        answer = postprocess_answer(answer)
        # 답변을 청크 단위로 스트리밍
        chunk_size = 10
        for i in range(0, len(answer), chunk_size):
            chunk = answer[i:i + chunk_size]
            data = {"type": "chunk", "content": chunk}
            yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
        data = {"type": "done", "content": ""}
        yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
    except Exception as e:
        error_data = {"type": "error", "content": str(e)}
        yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"


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
                "content": sources
            }
            yield f"data: {json.dumps(sources_data, ensure_ascii=False)}\n\n"
            
            # 컨텍스트가 없으면 AI 모델을 호출하지 않고 직접 답변 반환
            if not has_relevant_context:
                answer = generate_fallback_answer(context_docs, False, has_relevant_context, similar_docs)
                for i in range(0, len(answer), 10):
                    chunk = answer[i:i + 10]
                    data = {
                        "type": "chunk",
                        "content": chunk
                    }
                    yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                
                data = {
                    "type": "done",
                    "content": ""
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
                    similar_docs
                ):
                    yield chunk
            else:
                # Ollama 꺼져 있음 — 공통 연결 테스트 결과를 피드백 이벤트로 먼저 전송
                ollama_feedback = ollama_connection_check()
                feedback_data = {"type": "ollama_feedback", "content": ollama_feedback}
                yield f"data: {json.dumps(feedback_data, ensure_ascii=False)}\n\n"
                # 폴백 답변 스트리밍
                answer = generate_fallback_answer(
                    context_docs, False, has_relevant_context, similar_docs
                )
                for i in range(0, len(answer), 10):
                    chunk = answer[i:i + 10]
                    data = {
                        "type": "chunk",
                        "content": chunk
                    }
                    yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                
                data = {
                    "type": "done",
                    "content": ""
                }
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                
        except Exception as e:
            error_data = {
                "type": "error",
                "content": str(e)
            }
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
