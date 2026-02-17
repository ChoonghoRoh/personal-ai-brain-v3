"""AI 워크플로우 파이프라인 Steps 4-6: 라벨 매칭, 승인, 임베딩

Phase 16-4-1: ai_workflow_service.py 954줄 → 3파일 분리
Mixin 패턴으로 AIWorkflowService에 합성됩니다.
"""
import logging
import time
from typing import List, Dict, Any, Optional, Set
from datetime import datetime

from sqlalchemy.orm import Session

from backend.models.models import Document, KnowledgeChunk, Label, KnowledgeLabel
from backend.services.automation import ai_workflow_state

logger = logging.getLogger(__name__)


class WorkflowFinalizeMixin:
    """Steps 4-6: 라벨 매칭, 승인, 임베딩 Mixin"""

    def _match_labels(
        self,
        task_id: str,
        chunk_ids: List[int],
        db: Session,
    ) -> int:
        """단계 4: 라벨 생성/매칭 (50-70%)

        역인덱스(keyword -> [label_id]) 기반으로 라벨을 매칭합니다.

        Args:
            task_id: 태스크 ID
            chunk_ids: 청크 ID 목록
            db: DB 세션

        Returns:
            매칭된 라벨 수
        """
        self._update_progress(
            task_id=task_id,
            stage_name="라벨 생성/매칭",
            progress_pct=50,
            message="청크에 라벨 추천 중...",
        )

        label_count: int = 0
        total: int = len(chunk_ids)
        stage_start: float = time.time()

        # 전체 라벨을 1회만 조회
        all_labels: List[Label] = db.query(Label).filter(
            Label.label_type.in_(["category", "domain", "project"])
        ).all()

        # 역인덱스 구축: label_name_lower -> [label_id, ...]
        label_index: Dict[str, List[int]] = {}
        label_map: Dict[int, Label] = {}
        for label in all_labels:
            label_map[label.id] = label
            key: str = label.name.lower().strip()
            if key not in label_index:
                label_index[key] = []
            label_index[key].append(label.id)

        # 청크별 역인덱스 매칭
        for idx, chunk_id in enumerate(chunk_ids):
            if ai_workflow_state.is_cancelled(task_id):
                raise RuntimeError("사용자에 의해 취소됨")

            chunk = db.query(KnowledgeChunk).filter(
                KnowledgeChunk.id == chunk_id
            ).first()
            if not chunk:
                continue

            item_name: str = f"청크 #{chunk_id}"
            chunk_text_lower: str = chunk.content.lower()

            # 역인덱스 키를 순회하며 텍스트 포함 여부 확인
            candidate_label_ids: Set[int] = set()
            for key, label_ids in label_index.items():
                if key in chunk_text_lower:
                    candidate_label_ids.update(label_ids)

            # 후보 라벨에 대해서만 KnowledgeLabel 생성
            for label_id in candidate_label_ids:
                existing = db.query(KnowledgeLabel).filter(
                    KnowledgeLabel.chunk_id == chunk_id,
                    KnowledgeLabel.label_id == label_id,
                ).first()

                if not existing:
                    knowledge_label = KnowledgeLabel(
                        chunk_id=chunk_id,
                        label_id=label_id,
                        status="suggested",
                        source="ai",
                        confidence=0.7,
                    )
                    db.add(knowledge_label)
                    label_count += 1

            # ETA 계산
            current: int = idx + 1
            elapsed: float = time.time() - stage_start
            eta: Optional[float] = (
                (elapsed / current) * (total - current) if current > 0 else None
            )

            # 진행률 업데이트
            progress: int = 50 + int(20 * current / total)
            self._update_progress(
                task_id=task_id,
                stage_name="라벨 생성/매칭",
                progress_pct=progress,
                message=f"{current}/{total} 청크 처리 완료",
                detail={"current": current, "total": total, "item_name": item_name},
                eta_seconds=round(eta, 1) if eta is not None else None,
            )

        db.commit()
        logger.info("라벨 매칭 완료: %d개", label_count)
        return label_count

    def _approve_items(
        self,
        task_id: str,
        chunk_ids: List[int],
        auto_approve: bool,
        db: Session,
    ) -> int:
        """단계 5: 승인 처리 (70-80%)

        Args:
            task_id: 태스크 ID
            chunk_ids: 청크 ID 목록
            auto_approve: 자동 승인 여부
            db: DB 세션

        Returns:
            승인된 청크 수
        """
        self._update_progress(
            task_id=task_id,
            stage_name="승인 처리",
            progress_pct=70,
            message="자동 승인 중..." if auto_approve else "승인 대기 상태로 설정 중...",
        )

        approved_count = 0

        if auto_approve:
            # 청크 승인
            chunks = db.query(KnowledgeChunk).filter(
                KnowledgeChunk.id.in_(chunk_ids),
                KnowledgeChunk.status == "draft",
            ).all()

            for chunk in chunks:
                chunk.status = "approved"
                chunk.approved_at = datetime.utcnow()
                chunk.approved_by = "ai_workflow"
                approved_count += 1

            # 라벨 승인
            labels = db.query(KnowledgeLabel).filter(
                KnowledgeLabel.chunk_id.in_(chunk_ids),
                KnowledgeLabel.status == "suggested",
            ).all()

            for label in labels:
                label.status = "confirmed"

            db.commit()

            self._update_progress(
                task_id=task_id,
                stage_name="승인 처리",
                progress_pct=80,
                message=f"{approved_count}개 청크 자동 승인됨",
            )
        else:
            self._update_progress(
                task_id=task_id,
                stage_name="승인 처리",
                progress_pct=80,
                message=f"{len(chunk_ids)}개 청크가 승인 대기 중",
            )

        logger.info("승인 처리 완료: approved=%d", approved_count)
        return approved_count

    def _embed_chunks(
        self,
        task_id: str,
        chunk_ids: List[int],
        db: Session,
    ) -> int:
        """단계 6: Qdrant 배치 임베딩 (80-100%)

        50건 단위 배치로 인코딩 + upsert합니다.

        Args:
            task_id: 태스크 ID
            chunk_ids: 청크 ID 목록
            db: DB 세션

        Returns:
            임베딩된 청크 수
        """
        BATCH_SIZE = 50

        self._update_progress(
            task_id=task_id,
            stage_name="Qdrant 임베딩",
            progress_pct=80,
            message="Qdrant에 벡터 임베딩 중...",
        )

        # 승인된 청크 중 미동기화 건만 대상
        chunks = db.query(KnowledgeChunk).filter(
            KnowledgeChunk.id.in_(chunk_ids),
            KnowledgeChunk.status == "approved",
            KnowledgeChunk.qdrant_point_id.is_(None),
        ).all()

        embed_total = len(chunks)
        if embed_total == 0:
            self._update_progress(
                task_id=task_id,
                stage_name="Qdrant 임베딩",
                progress_pct=100,
                message="임베딩 대상 청크 없음",
            )
            return 0

        # 모델 & 클라이언트 1회 초기화
        try:
            from backend.config import EMBEDDING_MODEL, QDRANT_HOST, QDRANT_PORT, COLLECTION_NAME
            from sentence_transformers import SentenceTransformer
            from qdrant_client import QdrantClient
            from qdrant_client.models import PointStruct

            model = SentenceTransformer(EMBEDDING_MODEL)
            qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        except Exception as e:
            logger.warning("Qdrant/임베딩 모델 초기화 실패: %s", e)
            return 0

        embedded_count = 0
        stage_start = time.time()

        # Document file_path 사전 조회
        doc_ids = list({c.document_id for c in chunks})
        docs = db.query(Document).filter(Document.id.in_(doc_ids)).all()
        doc_path_map: Dict[int, str] = {d.id: d.file_path or "unknown" for d in docs}

        # 배치 분할 처리
        for batch_start in range(0, embed_total, BATCH_SIZE):
            if ai_workflow_state.is_cancelled(task_id):
                raise RuntimeError("사용자에 의해 취소됨")

            batch = chunks[batch_start:batch_start + BATCH_SIZE]
            batch_texts = [c.content for c in batch]

            try:
                # 배치 인코딩
                embeddings = model.encode(batch_texts, batch_size=BATCH_SIZE)

                # PointStruct 배치 구성
                points = [
                    PointStruct(
                        id=chunk.id,
                        vector=embedding.tolist(),
                        payload={
                            "content": chunk.content[:500],
                            "file_path": doc_path_map.get(chunk.document_id, "unknown"),
                            "chunk_index": chunk.chunk_index,
                            "document_id": chunk.document_id,
                            "status": chunk.status,
                        },
                    )
                    for chunk, embedding in zip(batch, embeddings)
                ]

                # 배치 upsert
                qdrant.upsert(collection_name=COLLECTION_NAME, points=points)

                # PG qdrant_point_id 일괄 업데이트
                for chunk in batch:
                    chunk.qdrant_point_id = str(chunk.id)
                    chunk.embedding_model = EMBEDDING_MODEL

                embedded_count += len(batch)

            except Exception as e:
                logger.warning(
                    "배치 임베딩 실패 (offset=%d, size=%d): %s",
                    batch_start, len(batch), e,
                )
                continue

            # ETA 및 진행률 업데이트
            processed = min(batch_start + BATCH_SIZE, embed_total)
            elapsed = time.time() - stage_start
            eta = (elapsed / processed) * (embed_total - processed) if processed > 0 else None

            batch_num = batch_start // BATCH_SIZE + 1
            total_batches = (embed_total + BATCH_SIZE - 1) // BATCH_SIZE
            progress = 80 + int(20 * processed / embed_total)

            self._update_progress(
                task_id=task_id,
                stage_name="Qdrant 임베딩",
                progress_pct=progress,
                message=f"{processed}/{embed_total} 청크 처리 완료 (배치 {batch_num}/{total_batches})",
                detail={"current": processed, "total": embed_total, "item_name": f"배치 {batch_num}/{total_batches}"},
                eta_seconds=round(eta, 1) if eta is not None else None,
            )

        logger.info("Qdrant 배치 임베딩 완료: %d/%d개", embedded_count, embed_total)
        return embedded_count
