"""자동 라벨링 서비스 — 문서/청크 Import 시 라벨·카테고리 추천 (Phase 9-3-2)"""
import logging
from typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session

from backend.models.models import KnowledgeChunk, Document, KnowledgeLabel, Label
from backend.services.knowledge.structure_matcher import get_structure_matcher

logger = logging.getLogger(__name__)


class AutoLabeler:
    """문서/청크 Import 시 자동 라벨·카테고리 추천."""

    def __init__(self, db: Session):
        self.db = db
        self.structure_matcher = get_structure_matcher(db)

    def label_on_import(
        self,
        document: Document,
        chunks: List[KnowledgeChunk],
    ) -> Dict[str, Any]:
        """문서·청크 Import 시 문서/청크별 라벨·카테고리 추천.

        Returns:
            {
                "document_labels": [...],
                "chunk_labels": { chunk_id: [...] },
                "suggested_category": {...},
                "total_suggestions": int
            }
        """
        result = {
            "document_labels": [],
            "chunk_labels": {},
            "suggested_category": None,
            "total_suggestions": 0,
        }
        try:
            result["suggested_category"] = self.suggest_category(document)
            if result["suggested_category"]:
                result["total_suggestions"] += 1
            for chunk in chunks:
                match = self.structure_matcher.match_on_chunk_create(chunk)
                labels = match.get("suggested_labels", [])
                result["chunk_labels"][chunk.id] = labels
                result["total_suggestions"] += len(labels)
        except Exception as e:
            logger.warning("label_on_import failed: %s", e)
        return result

    def suggest_category(self, document: Document) -> Optional[Dict[str, Any]]:
        """문서 카테고리 추천 (경로·유사 문서 기반)."""
        if not document or not document.file_path:
            return None
        cat = self.structure_matcher._infer_category_from_path(document.file_path)
        if cat:
            return cat
        # 유사 문서의 카테고리 참조
        similar = self.structure_matcher.find_similar_documents(document, max_docs=3)
        for s in similar:
            doc_row = self.db.query(Document).filter(Document.id == s["document_id"]).first()
            if doc_row and doc_row.category_label_id:
                from backend.models.models import Label
                lb = self.db.query(Label).filter(Label.id == doc_row.category_label_id).first()
                if lb:
                    return {
                        "label_id": lb.id,
                        "name": lb.name,
                        "confidence": 0.6,
                        "reason": f"유사 문서({s.get('file_name', '')})의 카테고리",
                    }
        return None

    def apply_suggested_labels(
        self,
        chunk_id: int,
        label_ids: List[int],
        auto_confirm: bool = False,
    ) -> Dict[str, Any]:
        """추천 라벨을 청크에 적용. 이미 있으면 스킵.

        Returns:
            { "chunk_id", "applied_labels", "skipped_labels", "total_applied" }
        """
        chunk = self.db.query(KnowledgeChunk).filter(KnowledgeChunk.id == chunk_id).first()
        if not chunk:
            return {"chunk_id": chunk_id, "applied_labels": [], "skipped_labels": [], "total_applied": 0}
        applied = []
        skipped = []
        status = "confirmed" if auto_confirm else "suggested"
        for label_id in label_ids:
            label = self.db.query(Label).filter(Label.id == label_id).first()
            if not label:
                skipped.append({"label_id": label_id, "reason": "label_not_found"})
                continue
            existing = (
                self.db.query(KnowledgeLabel)
                .filter(KnowledgeLabel.chunk_id == chunk_id, KnowledgeLabel.label_id == label_id)
                .first()
            )
            if existing:
                skipped.append({"label_id": label_id, "name": label.name, "reason": "already_exists"})
                continue
            kl = KnowledgeLabel(
                chunk_id=chunk_id,
                label_id=label_id,
                status=status,
                source="ai",
                confidence=1.0,
            )
            self.db.add(kl)
            applied.append({"label_id": label.id, "name": label.name})
        self.db.commit()
        return {
            "chunk_id": chunk_id,
            "applied_labels": applied,
            "skipped_labels": skipped,
            "total_applied": len(applied),
        }


def get_auto_labeler(db: Session) -> AutoLabeler:
    """AutoLabeler 인스턴스 반환."""
    return AutoLabeler(db=db)
