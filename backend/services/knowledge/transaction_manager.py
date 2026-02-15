"""PG-Qdrant 보상 트랜잭션 매니저 (Phase 12-2-5)

PostgreSQL과 Qdrant 간 데이터 정합성을 보장하기 위한 보상 트랜잭션 패턴.
순차적으로 액션을 실행하고, 중간 실패 시 이미 완료된 액션의 보상(rollback)을
역순으로 수행한다.

사용 예시:
    tx = CompensatingTransaction("embed_chunk_42")
    tx.add_step(
        name="qdrant_upsert",
        action=lambda: qdrant_client.upsert(...),
        compensate=lambda: qdrant_client.delete(...),
    )
    tx.add_step(
        name="pg_update_point_id",
        action=lambda: update_chunk_point_id(db, chunk_id, point_id),
        compensate=lambda: update_chunk_point_id(db, chunk_id, None),
    )
    result = await tx.execute()
"""
import logging
from dataclasses import dataclass, field
from typing import Callable, Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class TransactionStep:
    """보상 트랜잭션의 단일 스텝"""
    name: str
    action: Callable[[], Any]
    compensate: Optional[Callable[[], Any]] = None
    result: Any = None


@dataclass
class TransactionResult:
    """트랜잭션 실행 결과"""
    success: bool
    transaction_id: str
    completed_steps: list = field(default_factory=list)
    failed_step: Optional[str] = None
    error: Optional[str] = None
    compensated_steps: list = field(default_factory=list)
    compensation_errors: list = field(default_factory=list)


class CompensatingTransaction:
    """보상 트랜잭션 실행기

    순차적으로 스텝을 실행하고, 실패 시 이미 완료된 스텝의
    보상 액션을 역순으로 실행하여 데이터 정합성을 복구한다.
    """

    def __init__(self, transaction_id: str):
        self.transaction_id = transaction_id
        self._steps: list[TransactionStep] = []

    def add_step(
        self,
        name: str,
        action: Callable[[], Any],
        compensate: Optional[Callable[[], Any]] = None,
    ) -> "CompensatingTransaction":
        """스텝 추가 (체이닝 지원)"""
        self._steps.append(TransactionStep(name=name, action=action, compensate=compensate))
        return self

    def execute(self) -> TransactionResult:
        """동기 실행 — 순차적으로 스텝 실행 후 실패 시 보상"""
        completed: list[TransactionStep] = []
        result = TransactionResult(success=False, transaction_id=self.transaction_id)

        logger.info("[TX:%s] 시작 (%d 스텝)", self.transaction_id, len(self._steps))

        for step in self._steps:
            try:
                logger.debug("[TX:%s] 실행: %s", self.transaction_id, step.name)
                step.result = step.action()
                completed.append(step)
                result.completed_steps.append(step.name)
                logger.debug("[TX:%s] 성공: %s", self.transaction_id, step.name)
            except Exception as e:
                result.failed_step = step.name
                result.error = f"{type(e).__name__}: {e}"
                logger.error(
                    "[TX:%s] 실패: %s — %s", self.transaction_id, step.name, result.error
                )
                # 보상 실행 (역순)
                self._compensate(completed, result)
                return result

        result.success = True
        logger.info("[TX:%s] 완료 (%d 스텝 성공)", self.transaction_id, len(completed))
        return result

    def _compensate(self, completed: list[TransactionStep], result: TransactionResult) -> None:
        """완료된 스텝의 보상 액션을 역순으로 실행"""
        for step in reversed(completed):
            if step.compensate is None:
                continue
            try:
                logger.info("[TX:%s] 보상 실행: %s", self.transaction_id, step.name)
                step.compensate()
                result.compensated_steps.append(step.name)
                logger.info("[TX:%s] 보상 성공: %s", self.transaction_id, step.name)
            except Exception as comp_err:
                error_msg = f"{step.name}: {type(comp_err).__name__}: {comp_err}"
                result.compensation_errors.append(error_msg)
                logger.error(
                    "[TX:%s] 보상 실패: %s — %s",
                    self.transaction_id,
                    step.name,
                    error_msg,
                )
