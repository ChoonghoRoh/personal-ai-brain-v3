"""Ollama API 클라이언트 — 로컬 LLM 생성 (EEVE-Korean 등)"""
import json
import logging
import urllib.request
from typing import Optional, List, Dict, Any, Generator

from backend.config import OLLAMA_BASE_URL, OLLAMA_MODEL

logger = logging.getLogger(__name__)

# LLM 호출 시 피드백에 넣을 공통 메시지 (연결 불가 시)
OLLAMA_UNAVAILABLE_MESSAGE = "Ollama에 연결할 수 없습니다. 서비스가 실행 중인지 확인해 주세요."


def ollama_connection_check(timeout: float = 5.0) -> Dict[str, Any]:
    """Ollama 연결 테스트 — 모든 LLM 호출 전/후 피드백에 넣을 수 있는 공통 결과.

    Returns:
        available True:  {"available": True, "message": None, "detail": None, "models": [...]}
        available False: {"available": False, "message": str, "detail": str, "models": []}
    """
    url = f"{OLLAMA_BASE_URL.rstrip('/')}/api/tags"
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        models = data.get("models", [])
        return {
            "available": True,
            "message": None,
            "detail": None,
            "models": models,
        }
    except Exception as e:
        detail = str(e)
        logger.debug("Ollama 연결 테스트 실패: %s", detail)
        return {
            "available": False,
            "message": OLLAMA_UNAVAILABLE_MESSAGE,
            "detail": detail,
            "models": [],
        }


def ollama_list_models() -> List[Dict[str, Any]]:
    """Ollama 설치 모델 목록 (GET /api/tags)."""
    url = f"{OLLAMA_BASE_URL.rstrip('/')}/api/tags"
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("models", [])
    except Exception as e:
        logger.debug("Ollama tags 확인 실패: %s", e)
        return []


def ollama_generate(
    prompt: str,
    max_tokens: int = 500,
    temperature: float = 0.7,
    top_p: float = 0.9,
    top_k: int = 40,
    repeat_penalty: float = 1.2,
    stream: bool = False,
    timeout: float = 120.0,
    model: Optional[str] = None,
    system_prompt: Optional[str] = None,
) -> Optional[str]:
    """Ollama /api/generate로 텍스트 생성.

    Args:
        prompt: 입력 프롬프트
        max_tokens: 최대 생성 토큰 수
        temperature: 샘플링 온도 (0~2)
        top_p, top_k, repeat_penalty: 생성 옵션
        stream: True면 스트리밍 (현재 미구현, False만 사용)
        timeout: 요청 타임아웃(초)
        model: 사용할 모델명. None이면 OLLAMA_MODEL 사용.
        system_prompt: 시스템 프롬프트 (role: system). None이면 생략.

    Returns:
        생성된 텍스트. 오류 시 None
    """
    use_model = (model or OLLAMA_MODEL).strip() or OLLAMA_MODEL
    # EEVE·instruct 등 채팅형 모델은 /api/chat을 먼저 사용 (generate에서 빈 응답/타임아웃 많음)
    if _is_chat_oriented_model(use_model):
        text = _ollama_chat_fallback(use_model, prompt, max_tokens, temperature, timeout, system_prompt=system_prompt)
        if text:
            return text
    url = f"{OLLAMA_BASE_URL.rstrip('/')}/api/generate"
    body = {
        "model": use_model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "repeat_penalty": repeat_penalty,
        },
    }
    if system_prompt:
        body["system"] = system_prompt
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            out = json.loads(resp.read().decode("utf-8"))
            err = out.get("error")
            if err:
                raise ValueError(str(err))
            text = out.get("response", "").strip() or None
            if text:
                return text
            return _ollama_chat_fallback(use_model, prompt, max_tokens, temperature, timeout, system_prompt=system_prompt)
    except (ValueError, json.JSONDecodeError):
        raise
    except Exception as e:
        logger.warning("Ollama generate 실패 (model=%s): %s", use_model, e)
        # 타임아웃 등 예외 시에도 채팅형 폴백 시도
        return _ollama_chat_fallback(use_model, prompt, max_tokens, temperature, timeout, system_prompt=system_prompt)


def ollama_generate_stream(
    prompt: str,
    max_tokens: int = 500,
    temperature: float = 0.7,
    top_p: float = 0.9,
    top_k: int = 40,
    repeat_penalty: float = 1.2,
    timeout: float = 120.0,
    model: Optional[str] = None,
    system_prompt: Optional[str] = None,
) -> Generator[str, None, None]:
    """Ollama /api/generate 스트리밍 — 토큰 단위 yield (Phase 10-4-1).

    Args:
        prompt: 입력 프롬프트
        max_tokens: 최대 생성 토큰 수
        temperature: 샘플링 온도 (0~2)
        top_p, top_k, repeat_penalty: 생성 옵션
        timeout: 요청 타임아웃(초)
        model: 사용할 모델명. None이면 OLLAMA_MODEL 사용.
        system_prompt: 시스템 프롬프트 (role: system). None이면 생략.

    Yields:
        생성된 텍스트 토큰
    """
    use_model = (model or OLLAMA_MODEL).strip() or OLLAMA_MODEL
    if _is_chat_oriented_model(use_model):
        yield from _ollama_chat_stream(use_model, prompt, max_tokens, temperature, timeout, system_prompt=system_prompt)
        return
    url = f"{OLLAMA_BASE_URL.rstrip('/')}/api/generate"
    body = {
        "model": use_model,
        "prompt": prompt,
        "stream": True,
        "options": {
            "num_predict": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "repeat_penalty": repeat_penalty,
        },
    }
    if system_prompt:
        body["system"] = system_prompt
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            for raw_line in resp:
                line = raw_line.decode("utf-8").strip()
                if not line:
                    continue
                try:
                    chunk = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if chunk.get("error"):
                    raise ValueError(str(chunk["error"]))
                token = chunk.get("response", "")
                if token:
                    yield token
                if chunk.get("done"):
                    break
    except (ValueError, json.JSONDecodeError):
        raise
    except Exception as e:
        logger.warning("Ollama generate stream 실패 (model=%s): %s", use_model, e)
        yield from _ollama_chat_stream(use_model, prompt, max_tokens, temperature, timeout)


def _is_chat_oriented_model(model_name: str) -> bool:
    """instruct/eeve 등 채팅 전용 모델이면 True (이 경우 /api/chat 우선 사용)."""
    name = (model_name or "").lower()
    return "instruct" in name or "eeve" in name or "chat" in name


def _ollama_chat_fallback(
    model: str,
    prompt: str,
    max_tokens: int = 500,
    temperature: float = 0.7,
    timeout: float = 120.0,
    system_prompt: Optional[str] = None,
) -> Optional[str]:
    """채팅형 모델용 /api/chat 호출 (generate 빈 응답/예외 시 폴백 또는 우선 사용)."""
    url = f"{OLLAMA_BASE_URL.rstrip('/')}/api/chat"
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    body = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {
            "num_predict": max_tokens,
            "temperature": temperature,
        },
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            out = json.loads(raw)
            err = out.get("error")
            if err:
                logger.warning("Ollama chat 오류 (model=%s): %s", model, err)
                raise ValueError(str(err))
            msg = out.get("message") or {}
            content_raw = msg.get("content")
            if isinstance(content_raw, list):
                content = " ".join(
                    (item.get("text", item) if isinstance(item, dict) else str(item))
                    for item in content_raw
                ).strip()
            else:
                content = (content_raw or "").strip()
            if content:
                return content
            # 일부 모델은 reasoning을 message.thinking에 반환
            thinking_raw = msg.get("thinking")
            thinking = (thinking_raw if isinstance(thinking_raw, str) else "") or ""
            thinking = thinking.strip()
            if thinking:
                return thinking
            # 구버전/일부 환경에서 상위 response 필드 사용
            top_response = (out.get("response") or "").strip()
            if top_response:
                return top_response
            # 빈 응답 시 원인 파악용 로그 (done_reason 등)
            done_reason = out.get("done_reason", "")
            logger.info(
                "Ollama chat 빈 응답 (model=%s) done=%s done_reason=%s keys=%s",
                model,
                out.get("done"),
                done_reason,
                list(out.keys()),
            )
            return None
    except (ValueError, json.JSONDecodeError):
        raise
    except Exception as e:
        logger.debug("Ollama chat 폴백 실패 (model=%s): %s", model, e)
        return None


def _ollama_chat_stream(
    model: str,
    prompt: str,
    max_tokens: int = 500,
    temperature: float = 0.7,
    timeout: float = 120.0,
    system_prompt: Optional[str] = None,
) -> Generator[str, None, None]:
    """채팅형 모델용 /api/chat 스트리밍 호출 (Phase 10-4-1)."""
    url = f"{OLLAMA_BASE_URL.rstrip('/')}/api/chat"
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    body = {
        "model": model,
        "messages": messages,
        "stream": True,
        "options": {
            "num_predict": max_tokens,
            "temperature": temperature,
        },
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            for raw_line in resp:
                line = raw_line.decode("utf-8").strip()
                if not line:
                    continue
                try:
                    chunk = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if chunk.get("error"):
                    raise ValueError(str(chunk["error"]))
                msg = chunk.get("message", {})
                token = msg.get("content", "")
                if token:
                    yield token
                if chunk.get("done"):
                    break
    except (ValueError, json.JSONDecodeError):
        raise
    except Exception as e:
        logger.debug("Ollama chat stream 실패 (model=%s): %s", model, e)


def ollama_available() -> bool:
    """Ollama 서비스 및 모델 사용 가능 여부 확인 (GET /api/tags). 연결 테스트는 ollama_connection_check 사용."""
    check = ollama_connection_check(timeout=5.0)
    if not check["available"]:
        return False
    models = check.get("models", [])
    names = [m.get("name", "") for m in models]
    for n in names:
        if n == OLLAMA_MODEL or n.startswith((OLLAMA_MODEL or "").split(":")[0]):
            return True
    return bool(names)
