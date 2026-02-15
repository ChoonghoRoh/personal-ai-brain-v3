"""청크-Qdrant 동기화 서비스 (Phase 12-2-5)

청크 승인(approved) 시 Qdrant에 벡터를 upsert하고,
PG의 qdrant_point_id를 업데이트하는 플로우에
보상 트랜잭션 패턴을 적용한다.

Flow:
  1. 청크 임베딩 생성 (SentenceTransformer)
  2. Qdrant upsert (벡터 + 메타데이터)
  3. PG qdrant_point_id 업데이트
  실패 시 → 역순 보상 (Qdrant 포인트 삭제 → PG 원복)
"""
import logging
from typing import Optional

from sqlalchemy.orm import Session

from backend.models.models import KnowledgeChunk, Document
from backend.config import QDRANT_HOST, QDRANT_PORT, COLLECTION_NAME
from backend.services.knowledge.transaction_manager import CompensatingTransaction, TransactionResult

logger = logging.getLogger(__name__)


def _get_qdrant_client():
    """Qdrant 클라이언트 lazy import"""
    from qdrant_client import QdrantClient
    return QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)


def _get_embedding_model():
    """임베딩 모델 lazy import"""
    from backend.config import EMBEDDING_MODEL
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(EMBEDDING_MODEL)


def sync_chunk_to_qdrant(
    db: Session,
    chunk_id: int,
) -> TransactionResult:
    """청크를 Qdrant에 동기화한다 (보상 트랜잭션 적용).

    Args:
        db: SQLAlchemy 세션
        chunk_id: 동기화할 청크 ID

    Returns:
        TransactionResult: 실행 결과
    """
    chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == chunk_id).first()
    if not chunk:
        return TransactionResult(
            success=False,
            transaction_id=f"sync_chunk_{chunk_id}",
            failed_step="load_chunk",
            error=f"Chunk {chunk_id} not found",
        )

    # 이미 동기화 완료 상태
    if chunk.qdrant_point_id is not None:
        logger.info("Chunk %d already synced (point_id=%s)", chunk_id, chunk.qdrant_point_id)
        return TransactionResult(
            success=True,
            transaction_id=f"sync_chunk_{chunk_id}",
            completed_steps=["already_synced"],
        )

    document = db.query(Document).filter(Document.id == chunk.document_id).first()
    file_path = document.file_path if document else "unknown"

    qdrant = _get_qdrant_client()
    model = _get_embedding_model()

    # 임베딩 생성
    embedding = model.encode(chunk.content).tolist()
    point_id = chunk.id  # PG chunk.id를 Qdrant point ID로 사용

    tx = CompensatingTransaction(f"sync_chunk_{chunk_id}")

    # Step 1: Qdrant upsert
    def qdrant_upsert():
        from qdrant_client.models import PointStruct
        qdrant.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "content": chunk.content[:500],
                        "file_path": file_path,
                        "chunk_index": chunk.chunk_index,
                        "document_id": chunk.document_id,
                        "status": chunk.status,
                    },
                )
            ],
        )
        return point_id

    def qdrant_delete():
        qdrant.delete(
            collection_name=COLLECTION_NAME,
            points_selector=[point_id],
        )

    tx.add_step(
        name="qdrant_upsert",
        action=qdrant_upsert,
        compensate=qdrant_delete,
    )

    # Step 2: PG qdrant_point_id 업데이트
    old_point_id = chunk.qdrant_point_id

    def pg_update():
        chunk.qdrant_point_id = str(point_id)
        chunk.embedding_model = model.get_sentence_embedding_dimension().__class__.__name__
        db.commit()

    def pg_rollback():
        chunk.qdrant_point_id = old_point_id
        chunk.embedding_model = None
        db.commit()

    tx.add_step(
        name="pg_update_point_id",
        action=pg_update,
        compensate=pg_rollback,
    )

    return tx.execute()


def delete_chunk_from_qdrant(
    db: Session,
    chunk_id: int,
) -> TransactionResult:
    """Qdrant에서 청크 포인트를 삭제한다 (보상 트랜잭션 적용).

    Args:
        db: SQLAlchemy 세션
        chunk_id: 삭제할 청크 ID

    Returns:
        TransactionResult: 실행 결과
    """
    chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == chunk_id).first()
    if not chunk:
        return TransactionResult(
            success=False,
            transaction_id=f"delete_chunk_{chunk_id}",
            failed_step="load_chunk",
            error=f"Chunk {chunk_id} not found",
        )

    if chunk.qdrant_point_id is None:
        return TransactionResult(
            success=True,
            transaction_id=f"delete_chunk_{chunk_id}",
            completed_steps=["no_qdrant_point"],
        )

    qdrant = _get_qdrant_client()
    old_point_id = chunk.qdrant_point_id

    tx = CompensatingTransaction(f"delete_chunk_{chunk_id}")

    # Step 1: PG qdrant_point_id 를 None으로 설정
    def pg_clear():
        chunk.qdrant_point_id = None
        chunk.embedding_model = None
        db.commit()

    def pg_restore():
        chunk.qdrant_point_id = old_point_id
        db.commit()

    tx.add_step(
        name="pg_clear_point_id",
        action=pg_clear,
        compensate=pg_restore,
    )

    # Step 2: Qdrant 포인트 삭제
    def qdrant_delete():
        qdrant.delete(
            collection_name=COLLECTION_NAME,
            points_selector=[int(old_point_id)],
        )

    tx.add_step(
        name="qdrant_delete",
        action=qdrant_delete,
        compensate=None,  # Qdrant 삭제 복구는 재 upsert 필요 (비용 높음)
    )

    return tx.execute()
