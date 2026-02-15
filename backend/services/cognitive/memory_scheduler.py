"""만료 기억 자동 정리 스케줄러 (Phase 12-3-4)

asyncio 기반 백그라운드 태스크로 주기적으로 만료된 단기 기억을 삭제한다.
APScheduler 등 외부 의존성 없이 asyncio.sleep 루프로 구현.

사용:
    from backend.services.cognitive.memory_scheduler import start_memory_cleanup, stop_memory_cleanup

    # FastAPI lifespan에서:
    task = await start_memory_cleanup()
    ...
    await stop_memory_cleanup(task)
"""
import asyncio
import logging

from backend.config import MEMORY_CLEANUP_ENABLED, MEMORY_CLEANUP_INTERVAL_MINUTES

logger = logging.getLogger(__name__)

_cleanup_task: asyncio.Task | None = None


async def _cleanup_loop() -> None:
    """만료 기억 정리 루프"""
    interval = MEMORY_CLEANUP_INTERVAL_MINUTES * 60
    logger.info(
        "Memory cleanup scheduler started (interval=%d min)", MEMORY_CLEANUP_INTERVAL_MINUTES
    )

    while True:
        try:
            await asyncio.sleep(interval)
            deleted = _run_cleanup()
            if deleted > 0:
                logger.info("Memory cleanup: %d expired memories deleted", deleted)
            else:
                logger.debug("Memory cleanup: no expired memories found")
        except asyncio.CancelledError:
            logger.info("Memory cleanup scheduler stopped")
            break
        except Exception as e:
            logger.error("Memory cleanup error: %s", e, exc_info=True)
            # 에러 발생해도 루프 유지 (다음 주기에 재시도)
            await asyncio.sleep(60)


def _run_cleanup() -> int:
    """동기 DB 작업으로 만료 기억 삭제"""
    from backend.models.database import SessionLocal
    from backend.services.cognitive.memory_service import MemoryService

    db = SessionLocal()
    try:
        service = MemoryService()
        count = service.delete_expired_memories(db=db)
        return count
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


async def start_memory_cleanup() -> asyncio.Task | None:
    """스케줄러 시작"""
    global _cleanup_task
    if not MEMORY_CLEANUP_ENABLED:
        logger.info("Memory cleanup scheduler disabled")
        return None

    _cleanup_task = asyncio.create_task(_cleanup_loop())
    return _cleanup_task


async def stop_memory_cleanup(task: asyncio.Task | None = None) -> None:
    """스케줄러 정지"""
    global _cleanup_task
    t = task or _cleanup_task
    if t and not t.done():
        t.cancel()
        try:
            await t
        except asyncio.CancelledError:
            pass
    _cleanup_task = None
