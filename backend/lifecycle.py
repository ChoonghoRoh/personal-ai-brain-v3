"""FastAPI 앱 라이프사이클 이벤트 (startup/shutdown) 핸들러"""
import logging
import os
import subprocess
import sys
import threading
import time

from backend.config import OLLAMA_BASE_URL, PROJECT_ROOT
from backend.models.database import init_db


def _llm_check_after_startup() -> None:
    """Backend 기동 완료 후 LLM 서버 확인. localhost면 미실행 시 ollama serve 기동, 이후 모델 작동 확인."""
    time.sleep(3)
    log = logging.getLogger(__name__)
    base = (OLLAMA_BASE_URL or "").strip().lower()
    script_path = PROJECT_ROOT / "scripts" / "llm_server_check.py"
    if "localhost" in base or "127.0.0.1" in base:
        if script_path.exists():
            try:
                env = {**os.environ, "OLLAMA_BASE_URL": OLLAMA_BASE_URL or "http://localhost:11434"}
                r = subprocess.run(
                    [sys.executable, str(script_path), "--start-if-missing", "--check-model"],
                    env=env,
                    cwd=str(PROJECT_ROOT),
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                if r.returncode == 0:
                    log.info("LLM 서버 확인 완료 (자동 기동·모델 검증): %s", r.stdout or "")
                else:
                    log.warning("LLM 서버 확인 실패 (exit %s): %s", r.returncode, (r.stderr or r.stdout or "").strip())
            except subprocess.TimeoutExpired:
                log.warning("LLM 서버 확인 타임아웃 (120초)")
            except Exception as e:
                log.warning("LLM 서버 확인 예외: %s", e)
        else:
            log.debug("scripts/llm_server_check.py 없음, LLM 확인 생략")
    else:
        try:
            from backend.services.ai.ollama_client import ollama_available, ollama_generate
            from backend.config import OLLAMA_MODEL
            if ollama_available():
                out = ollama_generate("한 줄로 자기소개해주세요.", max_tokens=20, temperature=0.3, timeout=30.0)
                if out and out.strip():
                    log.info("LLM 서버 연결·모델 작동 확인: %s", OLLAMA_MODEL)
                else:
                    log.warning("LLM 서버 연결됐으나 모델 응답 없음: %s", OLLAMA_MODEL)
            else:
                log.warning("LLM 서버 미연결 (호스트에서 ollama serve 또는 scripts/llm_server_check.py --start-if-missing 권장)")
        except Exception as e:
            log.debug("LLM 확인 중 예외: %s", e)


def _seed_admin_user() -> None:
    """Phase 14-5-2: 초기 관리자 계정이 없으면 생성"""
    from backend.config import ADMIN_DEFAULT_USERNAME, ADMIN_DEFAULT_PASSWORD
    from backend.models.database import SessionLocal
    from backend.models.user_models import User
    from passlib.context import CryptContext

    log = logging.getLogger(__name__)
    pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == ADMIN_DEFAULT_USERNAME).first()
        if not existing:
            admin_user = User(
                username=ADMIN_DEFAULT_USERNAME,
                hashed_password=pwd_ctx.hash(ADMIN_DEFAULT_PASSWORD),
                display_name="System Administrator",
                role="admin_system",
                is_active=True,
            )
            db.add(admin_user)
            db.commit()
            log.info("초기 관리자 계정 생성: %s (role=admin_system)", ADMIN_DEFAULT_USERNAME)
        else:
            log.debug("관리자 계정 이미 존재: %s", ADMIN_DEFAULT_USERNAME)
    except Exception as e:
        db.rollback()
        log.warning("초기 관리자 시드 실패: %s", e)
    finally:
        db.close()


def register_lifecycle_events(app) -> None:
    """FastAPI 앱에 startup/shutdown 이벤트 핸들러 등록"""

    @app.on_event("startup")
    async def on_startup():
        """앱 기동 시 DB 테이블이 없으면 생성 (labels 등). /knowledge 등 페이지 500 방지."""
        try:
            init_db()
        except Exception as e:
            logging.getLogger(__name__).warning("DB 초기화 실패 (테이블이 이미 있거나 DB 연결 문제): %s", e)

        # Phase 14-5-2: 초기 관리자 계정 시드
        try:
            _seed_admin_user()
        except Exception as e:
            logging.getLogger(__name__).warning("초기 관리자 시드 중 오류: %s", e)

        threading.Thread(target=_llm_check_after_startup, daemon=True).start()

        # Phase 12-3-4: 만료 기억 자동 정리 스케줄러
        from backend.services.cognitive.memory_scheduler import start_memory_cleanup
        await start_memory_cleanup()

    @app.on_event("shutdown")
    async def on_shutdown():
        """앱 종료 시 스케줄러 정리 (Phase 12-3-4)"""
        from backend.services.cognitive.memory_scheduler import stop_memory_cleanup
        await stop_memory_cleanup()
