"""AI 자동화 워크플로우 서비스 — 오케스트레이터 (Phase 15-2-2, Phase 16-4-1 리팩토링)

문서 선택부터 임베딩까지 6단계 AI 자동화 파이프라인을 오케스트레이션합니다.
파이프라인 스텝은 Mixin 모듈에 분리되어 있습니다:
  - workflow_extract.py: Steps 1-3 (텍스트 추출, 청크 생성, 키워드 추출)
  - workflow_finalize.py: Steps 4-6 (라벨 매칭, 승인, 임베딩)
"""
import gc
import logging
from typing import List

from sqlalchemy.orm import Session

from backend.services.automation import ai_workflow_state
from backend.services.automation.workflow_extract import WorkflowExtractMixin
from backend.services.automation.workflow_finalize import WorkflowFinalizeMixin
from backend.services.ingest.file_parser_service import FileParserService
from backend.services.knowledge.chunk_sync_service import sync_chunk_to_qdrant  # noqa: F401 (개별 동기화용)

logger = logging.getLogger(__name__)


class AIWorkflowService(WorkflowExtractMixin, WorkflowFinalizeMixin):
    """AI 자동화 워크플로우 파이프라인 서비스

    Mixin 구성:
        WorkflowExtractMixin: _extract_texts, _create_chunks, _extract_keywords 등
        WorkflowFinalizeMixin: _match_labels, _approve_items, _embed_chunks
    """

    DOC_BATCH_SIZE = 20

    def __init__(self):
        self.file_parser = FileParserService()
        self._pct_base = 0
        self._pct_range = 100

    def _update_progress(self, **kwargs) -> None:
        """Progress 래퍼: raw 0-100%를 배치 할당 범위로 매핑."""
        if "progress_pct" in kwargs:
            raw = kwargs["progress_pct"]
            kwargs["progress_pct"] = self._pct_base + int(raw * self._pct_range / 100)
        ai_workflow_state.update_progress(**kwargs)

    def execute_workflow(self, task_id: str, db: Session) -> None:
        """6단계 워크플로우 실행 (문서 배치 분할 + 단계별 DB 세션 분리)

        document_ids를 DOC_BATCH_SIZE(20)개 단위로 분할하여 순차 처리합니다.
        각 배치마다 6단계 파이프라인을 실행하고, 배치 간 GC를 수행합니다.
        중간 배치 실패 시 이전 배치 결과는 DB에 보존됩니다.

        Args:
            task_id: 태스크 ID
            db: DB 세션 (호환성 유지용, 실제로는 단계별 세션 사용)
        """
        task = ai_workflow_state.get_task(task_id)
        if not task:
            logger.error("태스크를 찾을 수 없음: %s", task_id)
            return

        document_ids = task.document_ids
        auto_approve = task.auto_approve

        # 문서를 DOC_BATCH_SIZE 단위로 분할
        batches = [
            document_ids[i:i + self.DOC_BATCH_SIZE]
            for i in range(0, len(document_ids), self.DOC_BATCH_SIZE)
        ]
        num_batches = len(batches)

        # 누적 결과
        all_chunk_ids: List[int] = []
        total_keywords = 0
        total_labels = 0
        total_approved = 0
        total_embedded = 0
        current_stage_name = None

        try:
            for batch_idx, batch_doc_ids in enumerate(batches):
                # 배치별 진행률 범위 설정
                self._pct_base = int(100 * batch_idx / num_batches)
                self._pct_range = int(100 / num_batches)

                batch_label = f"배치 {batch_idx + 1}/{num_batches}"
                logger.info(
                    "워크플로우 %s 시작: %d개 문서 (task_id=%s)",
                    batch_label, len(batch_doc_ids), task_id,
                )

                chunk_ids, keyword_count, label_count, approved_count, embedded_count = (
                    self._run_batch_pipeline(
                        task_id, batch_doc_ids, auto_approve,
                    )
                )

                # 누적
                all_chunk_ids.extend(chunk_ids)
                total_keywords += keyword_count
                total_labels += label_count
                total_approved += approved_count
                total_embedded += embedded_count
                current_stage_name = batch_label

                # doc_result 이벤트 발행 (Phase 16-3-1)
                ai_workflow_state.add_doc_result(
                    task_id=task_id,
                    document_ids=batch_doc_ids,
                    batch_index=batch_idx,
                    batch_stats={
                        "chunks_created": len(chunk_ids),
                        "keywords_extracted": keyword_count,
                        "labels_matched": label_count,
                        "chunks_approved": approved_count,
                        "chunks_embedded": embedded_count,
                    },
                )

                # 배치 간 GC (마지막 배치 제외)
                if batch_idx < num_batches - 1:
                    gc.collect()

            # 진행률 범위 초기화
            self._pct_base = 0
            self._pct_range = 100

            # 완료
            results = {
                "chunk_ids": all_chunk_ids,
                "chunks_created": len(all_chunk_ids),
                "keywords_extracted": total_keywords,
                "labels_matched": total_labels,
                "chunks_approved": total_approved,
                "chunks_embedded": total_embedded,
                "batches_processed": num_batches,
            }
            ai_workflow_state.complete_task(task_id, results)

            logger.info(
                "AI 워크플로우 완료: task_id=%s chunks=%d keywords=%d labels=%d batches=%d",
                task_id, len(all_chunk_ids), total_keywords, total_labels, num_batches,
            )

        except Exception as e:
            self._pct_base = 0
            self._pct_range = 100
            # 취소된 경우 fail_task 호출 생략 (이미 cancelled 상태)
            if ai_workflow_state.is_cancelled(task_id):
                logger.info("AI 워크플로우 취소됨: task_id=%s", task_id)
                return
            logger.exception("AI 워크플로우 실패: task_id=%s stage=%s", task_id, current_stage_name)
            ai_workflow_state.fail_task(
                task_id=task_id,
                error=str(e),
                failed_stage=current_stage_name,
            )

    def _run_batch_pipeline(
        self,
        task_id: str,
        document_ids: List[int],
        auto_approve: bool,
    ) -> tuple:
        """단일 문서 배치에 대해 6단계 파이프라인 실행.

        Returns:
            (chunk_ids, keyword_count, label_count, approved_count, embedded_count)
        """
        from backend.models.database import SessionLocal

        # 단계 1: 문서 텍스트 추출 (0-15%)
        if ai_workflow_state.is_cancelled(task_id):
            raise RuntimeError("사용자에 의해 취소됨")
        db1 = SessionLocal()
        try:
            texts = self._extract_texts(task_id, document_ids, db1)
            db1.commit()
        except Exception:
            db1.rollback()
            raise
        finally:
            db1.close()

        # 단계 2: 청크 생성 (15-30%)
        if ai_workflow_state.is_cancelled(task_id):
            raise RuntimeError("사용자에 의해 취소됨")
        db2 = SessionLocal()
        try:
            chunk_ids = self._create_chunks(task_id, document_ids, texts, db2)
            db2.commit()
        except Exception:
            db2.rollback()
            raise
        finally:
            db2.close()

        # 단계 3: 키워드 추출 (30-50%)
        if ai_workflow_state.is_cancelled(task_id):
            raise RuntimeError("사용자에 의해 취소됨")
        db3 = SessionLocal()
        try:
            keyword_count = self._extract_keywords(task_id, chunk_ids, db3)
            db3.commit()
        except Exception:
            db3.rollback()
            raise
        finally:
            db3.close()

        # 단계 4: 라벨 생성/매칭 (50-70%)
        if ai_workflow_state.is_cancelled(task_id):
            raise RuntimeError("사용자에 의해 취소됨")
        db4 = SessionLocal()
        try:
            label_count = self._match_labels(task_id, chunk_ids, db4)
            db4.commit()
        except Exception:
            db4.rollback()
            raise
        finally:
            db4.close()

        # 단계 5: 승인 처리 (70-80%)
        if ai_workflow_state.is_cancelled(task_id):
            raise RuntimeError("사용자에 의해 취소됨")
        db5 = SessionLocal()
        try:
            approved_count = self._approve_items(task_id, chunk_ids, auto_approve, db5)
            db5.commit()
        except Exception:
            db5.rollback()
            raise
        finally:
            db5.close()

        # 단계 6: Qdrant 임베딩 (80-100%, auto_approve=True인 경우만)
        embedded_count = 0
        if auto_approve:
            if ai_workflow_state.is_cancelled(task_id):
                raise RuntimeError("사용자에 의해 취소됨")
            db6 = SessionLocal()
            try:
                embedded_count = self._embed_chunks(task_id, chunk_ids, db6)
                db6.commit()
            except Exception:
                db6.rollback()
                raise
            finally:
                db6.close()

        return chunk_ids, keyword_count, label_count, approved_count, embedded_count


def get_ai_workflow_service() -> AIWorkflowService:
    """AIWorkflowService 인스턴스 반환"""
    return AIWorkflowService()
