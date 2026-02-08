#!/usr/bin/env python3
"""
LLM(Ollama) 서버 확인 및 localhost에서 미실행 시 자동 기동, 모델 작동 확인.

호스트에서 실행: backend 기동 후 Ollama가 꺼져 있으면 ollama serve 를 띄우고,
서버 확인 후 지정 모델로 짧은 생성 테스트를 수행합니다.

사용법:
  python scripts/llm_server_check.py
  python scripts/llm_server_check.py --start-if-missing --check-model
  python scripts/llm_server_check.py --url http://localhost:11434 --model qwen2.5:7b
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error
from typing import Optional, Tuple


def _read_ollama_error(exc: urllib.error.HTTPError) -> str:
    """HTTPError 시 Ollama 응답 본문의 error 메시지 추출."""
    try:
        body = exc.read().decode("utf-8", errors="replace")
        data = json.loads(body)
        return data.get("error", body) or str(exc)
    except Exception:
        return str(exc)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_URL = "http://localhost:11434"
DEFAULT_MODEL = "qwen2.5:7b"
POLL_INTERVAL = 1.0
POLL_TIMEOUT = 60.0
MODEL_TEST_TIMEOUT = 90.0


def _get_base_url(url: Optional[str]) -> str:
    return (url or os.environ.get("OLLAMA_BASE_URL") or DEFAULT_URL).rstrip("/")


def _get_model(model: Optional[str]) -> str:
    return (model or os.environ.get("OLLAMA_MODEL") or DEFAULT_MODEL).strip()


def check_ollama_reachable(base_url: str, timeout: float = 5.0) -> bool:
    """Ollama /api/tags 로 서버 도달 여부 확인."""
    url = f"{base_url}/api/tags"
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return "models" in data
    except Exception as e:
        logger.debug("Ollama 확인 실패: %s", e)
        return False


def start_ollama_serve() -> subprocess.Popen:
    """호스트에서 ollama serve 를 백그라운드로 기동. 호스트에서만 호출할 것."""
    logger.info("ollama serve 기동 중...")
    proc = subprocess.Popen(
        ["ollama", "serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    return proc


def wait_for_ollama(base_url: str, timeout: float = POLL_TIMEOUT) -> bool:
    """Ollama가 응답할 때까지 폴링."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if check_ollama_reachable(base_url):
            return True
        time.sleep(POLL_INTERVAL)
    return False


def _check_model_generate(base_url: str, model: str, timeout: float) -> Tuple[bool, str]:
    """/api/generate 로 생성 테스트 (completion 형식 모델용)."""
    url = f"{base_url}/api/generate"
    body = {
        "model": model,
        "prompt": "한 줄로 자기소개해주세요.",
        "stream": False,
        "options": {"num_predict": 30, "temperature": 0.3},
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            out = json.loads(resp.read().decode("utf-8"))
            if out.get("error"):
                return False, out.get("error", "")
            text = (out.get("response") or "").strip()
            return bool(text), "" if text else "모델 응답이 비어있음"
    except urllib.error.HTTPError as e:
        return False, _read_ollama_error(e)
    except Exception as e:
        return False, str(e)


def _check_model_chat(base_url: str, model: str, timeout: float) -> Tuple[bool, str]:
    """/api/chat 로 생성 테스트 (instruct/채팅 형식 모델용)."""
    url = f"{base_url}/api/chat"
    body = {
        "model": model,
        "messages": [{"role": "user", "content": "한 줄로 자기소개해주세요."}],
        "stream": False,
        "options": {"num_predict": 30, "temperature": 0.3},
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            out = json.loads(resp.read().decode("utf-8"))
            err = out.get("error")
            if err:
                return False, str(err)
            msg = out.get("message") or {}
            content = (msg.get("content") or "").strip()
            if content:
                return True, ""
            thinking = (msg.get("thinking") or "").strip()
            if thinking:
                return True, ""
            return False, "모델 응답이 비어있음"
    except urllib.error.HTTPError as e:
        return False, _read_ollama_error(e)
    except Exception as e:
        return False, str(e)


def check_model_works(base_url: str, model: str, timeout: float = MODEL_TEST_TIMEOUT) -> Tuple[bool, str]:
    """
    지정 모델로 짧은 생성 테스트.
    /api/generate 먼저 시도, 실패 시 /api/chat (instruct 모델).
    Returns:
        (성공 여부, 오류 메시지)
    """
    ok, err = _check_model_generate(base_url, model, timeout)
    if ok:
        return True, ""
    ok, err = _check_model_chat(base_url, model, timeout)
    if ok:
        return True, ""
    return False, err or "generate/chat 모두 실패"


def run(
    base_url: Optional[str] = None,
    model: Optional[str] = None,
    start_if_missing: bool = False,
    check_model: bool = True,
) -> int:
    """
    LLM 서버 확인 → 필요 시 기동 → 모델 작동 확인.
    Returns:
        0: 성공, 1: 실패
    """
    base_url = _get_base_url(base_url)
    model = _get_model(model)

    # 1) 서버 확인
    if check_ollama_reachable(base_url):
        logger.info("LLM 서버 연결됨: %s", base_url)
    else:
        if start_if_missing:
            if "localhost" not in base_url and "127.0.0.1" not in base_url:
                logger.warning("자동 기동은 localhost 전용입니다. URL=%s", base_url)
            else:
                proc = start_ollama_serve()
                if proc.poll() is not None:
                    _, err = proc.communicate(timeout=2)
                    logger.error("ollama serve 기동 실패: %s", (err or b"").decode("utf-8", errors="replace"))
                    return 1
                if wait_for_ollama(base_url):
                    logger.info("LLM 서버 기동 후 연결됨: %s", base_url)
                else:
                    logger.error("LLM 서버 기동 후 %s 초 내 응답 없음", POLL_TIMEOUT)
                    return 1
        else:
            logger.error("LLM 서버에 연결할 수 없습니다: %s (호스트에서 ollama serve 실행 또는 --start-if-missing)", base_url)
            return 1

    # 2) 모델 작동 확인
    if check_model:
        ok, err_msg = check_model_works(base_url, model)
        if ok:
            logger.info("모델 작동 확인 완료: %s", model)
        else:
            logger.error("모델 작동 확인 실패 (%s): %s", model, err_msg or "알 수 없는 오류")
            return 1

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="LLM(Ollama) 서버 확인 및 localhost에서 미실행 시 자동 기동, 모델 작동 확인"
    )
    parser.add_argument(
        "--url",
        default=None,
        help="Ollama base URL (기본: OLLAMA_BASE_URL 또는 http://localhost:11434)",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="확인할 모델명 (기본: OLLAMA_MODEL 또는 qwen2.5:7b)",
    )
    parser.add_argument(
        "--start-if-missing",
        action="store_true",
        help="서버가 꺼져 있으면 localhost에서 ollama serve 기동",
    )
    parser.add_argument(
        "--check-model",
        action="store_true",
        default=True,
        help="모델 생성 테스트 수행 (기본: True)",
    )
    parser.add_argument(
        "--no-check-model",
        action="store_true",
        help="모델 테스트 생략, 서버 연결만 확인",
    )
    args = parser.parse_args()
    check_model = args.check_model and not args.no_check_model
    return run(
        base_url=args.url,
        model=args.model,
        start_if_missing=args.start_if_missing,
        check_model=check_model,
    )


if __name__ == "__main__":
    sys.exit(main())
