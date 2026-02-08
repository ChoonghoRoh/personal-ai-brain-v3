"""지식구조 매칭 서비스 — 청크 생성/승인 시 라벨·관계·카테고리 추천 (Phase 9-3-2)"""
import logging
import re
from typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session

from backend.config import (
    AUTO_LABEL_MIN_CONFIDENCE,
    AUTO_RELATION_MIN_CONFIDENCE,
    AUTO_CATEGORY_MIN_CONFIDENCE,
    MAX_LABEL_SUGGESTIONS,
    MAX_RELATION_SUGGESTIONS,
    MAX_SIMILAR_DOCUMENTS,
)
from backend.models.models import (
    KnowledgeChunk,
    KnowledgeRelation,
    KnowledgeLabel,
    Label,
    Document,
)
from backend.services.search.hybrid_search import get_hybrid_search_service

logger = logging.getLogger(__name__)


def _extract_keywords(text: str, max_words: int = 20) -> List[str]:
    """텍스트에서 키워드 후보 추출 (2글자 이상, 마크다운 제목/코드 블록 제외)."""
    if not text or not text.strip():
        return []
    # 코드 블록 제거
    text = re.sub(r"```[\s\S]*?```", " ", text)
    text = re.sub(r"`[^`]+`", " ", text)
    # # 제목만 단어로
    headings = re.findall(r"^#+\s*(.+)$", text, re.MULTILINE)
    words = []
    for h in headings:
        words.extend(re.findall(r"[가-힣a-zA-Z0-9_]{2,}", h))
    # 본문 단어
    body = re.sub(r"^#+\s*.+$", "", text, flags=re.MULTILINE)
    words.extend(re.findall(r"[가-힣a-zA-Z0-9_]{2,}", body))
    seen = set()
    out = []
    for w in words:
        w = w.strip().lower()
        if w and w not in seen and len(w) >= 2:
            seen.add(w)
            out.append(w)
            if len(out) >= max_words:
                break
    return out


class StructureMatcher:
    """청크/문서 생성·승인 시 지식 구조(라벨, 관계, 카테고리) 추천."""

    def __init__(self, db: Session):
        self.db = db
        self.hybrid_search = get_hybrid_search_service()

    def match_on_chunk_create(
        self,
        chunk: KnowledgeChunk,
        max_labels: int = MAX_LABEL_SUGGESTIONS,
        max_similar: int = 5,
    ) -> Dict[str, Any]:
        """청크 생성 시 추천: 라벨, 유사 청크, 카테고리.

        Returns:
            {
                "suggested_labels": [{ label_id, name, label_type, confidence, source }],
                "similar_chunks": [{ chunk_id, title, similarity }],
                "suggested_category": { label_id, name, confidence, reason } or None
            }
        """
        result = {
            "suggested_labels": [],
            "similar_chunks": [],
            "suggested_category": None,
        }
        content = (chunk.content or "").strip()
        if not content:
            return result

        # 1) 키워드 → Label 매칭
        keywords = _extract_keywords(content, max_words=15)
        for kw in keywords:
            labels = (
                self.db.query(Label)
                .filter(Label.name.ilike(f"%{kw}%"))
                .limit(5)
                .all()
            )
            for lb in labels:
                if lb.id not in [x["label_id"] for x in result["suggested_labels"]]:
                    result["suggested_labels"].append({
                        "label_id": lb.id,
                        "name": lb.name,
                        "label_type": lb.label_type or "keyword",
                        "confidence": max(AUTO_LABEL_MIN_CONFIDENCE, 0.85),
                        "source": "keyword",
                    })
                    if len(result["suggested_labels"]) >= max_labels:
                        break
            if len(result["suggested_labels"]) >= max_labels:
                break

        # 2) Hybrid 검색 → 유사 청크 + 유사 청크 라벨
        try:
            hybrid_results = self.hybrid_search.search_hybrid(
                db=self.db,
                query=content[:400],
                top_k=max_similar + 5,
            )
            for r in hybrid_results:
                doc_id = r.get("document_id")
                c = (
                    self.db.query(KnowledgeChunk)
                    .filter(
                        KnowledgeChunk.qdrant_point_id == str(doc_id),
                        KnowledgeChunk.status == "approved",
                        KnowledgeChunk.id != chunk.id,
                    )
                    .first()
                )
                if c:
                    result["similar_chunks"].append({
                        "chunk_id": c.id,
                        "title": (c.title or (c.content or "")[:50] or "").strip(),
                        "similarity": round(float(r.get("score", 0)), 2),
                    })
                    # 유사 청크의 라벨
                    kls = (
                        self.db.query(KnowledgeLabel)
                        .filter(KnowledgeLabel.chunk_id == c.id, KnowledgeLabel.status == "confirmed")
                        .all()
                    )
                    for kl in kls:
                        lb = self.db.query(Label).filter(Label.id == kl.label_id).first()
                        if lb and lb.id not in [x["label_id"] for x in result["suggested_labels"]]:
                            result["suggested_labels"].append({
                                "label_id": lb.id,
                                "name": lb.name,
                                "label_type": lb.label_type or "keyword",
                                "confidence": round(float(r.get("score", 0.7)), 2),
                                "source": "similar_chunk",
                            })
                            if len(result["suggested_labels"]) >= max_labels:
                                break
                if len(result["similar_chunks"]) >= max_similar:
                    break
        except Exception as e:
            logger.debug("match_on_chunk_create hybrid: %s", e)

        result["suggested_labels"] = result["suggested_labels"][:max_labels]
        result["similar_chunks"] = result["similar_chunks"][:max_similar]

        # 3) 카테고리: 문서 경로 분석
        if chunk.document_id:
            doc = self.db.query(Document).filter(Document.id == chunk.document_id).first()
            if doc and doc.file_path:
                cat = self._infer_category_from_path(doc.file_path)
                if cat:
                    result["suggested_category"] = cat
        return result

    def _infer_category_from_path(self, file_path: str) -> Optional[Dict[str, Any]]:
        """파일 경로로 카테고리 추론. DB Label 중 label_type=category 매칭."""
        path_lower = (file_path or "").lower()
        if "docs/phases" in path_lower or "phase-" in path_lower:
            name = "development"
        elif "brain/" in path_lower:
            name = "knowledge"
        elif "backend/" in path_lower or "scripts/" in path_lower:
            name = "code"
        else:
            name = "general"
        label = (
            self.db.query(Label)
            .filter(Label.name.ilike(name), Label.label_type == "category")
            .first()
        )
        if label:
            return {
                "label_id": label.id,
                "name": label.name,
                "confidence": AUTO_CATEGORY_MIN_CONFIDENCE,
                "reason": f"파일 경로 분석: {file_path[:80]}",
            }
        return None

    def suggest_relations_on_approve(
        self,
        chunk: KnowledgeChunk,
        max_relations: int = MAX_RELATION_SUGGESTIONS,
    ) -> List[Dict[str, Any]]:
        """승인된 청크에 대한 관계 제안. 이미 존재하는 관계 제외."""

        existing = set()
        for rel in self.db.query(KnowledgeRelation).filter(
            (KnowledgeRelation.source_chunk_id == chunk.id) | (KnowledgeRelation.target_chunk_id == chunk.id)
        ).all():
            existing.add((rel.source_chunk_id, rel.target_chunk_id))
            existing.add((rel.target_chunk_id, rel.source_chunk_id))

        out: List[Dict[str, Any]] = []

        # 1) 동일 문서 내 이전/다음 청크
        if chunk.document_id:
            prev_ = (
                self.db.query(KnowledgeChunk)
                .filter(
                    KnowledgeChunk.document_id == chunk.document_id,
                    KnowledgeChunk.chunk_index == (chunk.chunk_index or 0) - 1,
                    KnowledgeChunk.status == "approved",
                )
                .first()
            )
            next_ = (
                self.db.query(KnowledgeChunk)
                .filter(
                    KnowledgeChunk.document_id == chunk.document_id,
                    KnowledgeChunk.chunk_index == (chunk.chunk_index or 0) + 1,
                    KnowledgeChunk.status == "approved",
                )
                .first()
            )
            for other, rel_type in [(prev_, "follows"), (next_, "precedes")]:
                if other and other.id != chunk.id and (chunk.id, other.id) not in existing:
                    existing.add((chunk.id, other.id))
                    out.append({
                        "source_chunk_id": chunk.id,
                        "target_chunk_id": other.id,
                        "relation_type": rel_type,
                        "confidence": AUTO_RELATION_MIN_CONFIDENCE,
                        "reason": "동일 문서 내 순서 관계",
                    })
                    if len(out) >= max_relations:
                        return out

        # 2) 유사 청크 → related_to
        try:
            hybrid_results = self.hybrid_search.search_hybrid(
                db=self.db,
                query=(chunk.content or "")[:300],
                top_k=max_relations + 3,
            )
            for r in hybrid_results:
                if len(out) >= max_relations:
                    break
                doc_id = r.get("document_id")
                c = (
                    self.db.query(KnowledgeChunk)
                    .filter(
                        KnowledgeChunk.qdrant_point_id == str(doc_id),
                        KnowledgeChunk.status == "approved",
                        KnowledgeChunk.id != chunk.id,
                    )
                    .first()
                )
                if not c:
                    continue
                if (chunk.id, c.id) in existing or (c.id, chunk.id) in existing:
                    continue
                score = float(r.get("score", 0))
                if score < AUTO_RELATION_MIN_CONFIDENCE:
                    continue
                existing.add((chunk.id, c.id))
                out.append({
                    "source_chunk_id": chunk.id,
                    "target_chunk_id": c.id,
                    "relation_type": "related_to",
                    "confidence": round(score, 2),
                    "reason": f"유사도 {score:.2f}",
                })
        except Exception as e:
            logger.debug("suggest_relations hybrid: %s", e)

        return out[:max_relations]

    def find_similar_documents(
        self,
        document: Document,
        max_docs: int = MAX_SIMILAR_DOCUMENTS,
    ) -> List[Dict[str, Any]]:
        """문서와 유사한 다른 문서 목록 (청크 유사도 기반)."""
        chunks = (
            self.db.query(KnowledgeChunk)
            .filter(KnowledgeChunk.document_id == document.id, KnowledgeChunk.status == "approved")
            .limit(5)
            .all()
        )
        if not chunks:
            return []
        doc_scores: Dict[int, float] = {}
        doc_topics: Dict[int, set] = {}
        try:
            for c in chunks:
                hybrid_results = self.hybrid_search.search_hybrid(
                    db=self.db,
                    query=(c.content or "")[:300],
                    top_k=5,
                )
                for r in hybrid_results:
                    point_id = r.get("document_id")
                    other = (
                        self.db.query(KnowledgeChunk)
                        .filter(
                            KnowledgeChunk.qdrant_point_id == str(point_id),
                            KnowledgeChunk.document_id != document.id,
                            KnowledgeChunk.status == "approved",
                        )
                        .first()
                    )
                    if not other:
                        continue
                    doc_id = other.document_id
                    score = float(r.get("score", 0))
                    doc_scores[doc_id] = doc_scores.get(doc_id, 0) + score
                    if doc_id not in doc_topics:
                        doc_topics[doc_id] = set()
                    # 유사 청크의 라벨 이름을 shared_topics로
                    for kl in self.db.query(KnowledgeLabel).filter(
                        KnowledgeLabel.chunk_id == other.id, KnowledgeLabel.status == "confirmed"
                    ).all():
                        lb = self.db.query(Label).filter(Label.id == kl.label_id).first()
                        if lb:
                            doc_topics[doc_id].add(lb.name)
        except Exception as e:
            logger.debug("find_similar_documents: %s", e)
            return []

        sorted_docs = sorted(doc_scores.items(), key=lambda x: -x[1])[:max_docs]
        result = []
        for doc_id, score in sorted_docs:
            doc_row = self.db.query(Document).filter(Document.id == doc_id).first()
            if doc_row:
                result.append({
                    "document_id": doc_row.id,
                    "file_name": doc_row.file_name or doc_row.file_path or "",
                    "similarity": round(score / max(len(chunks), 1), 2),
                    "shared_topics": list(doc_topics.get(doc_id, []))[:5],
                })
        return result


def get_structure_matcher(db: Session) -> StructureMatcher:
    """StructureMatcher 인스턴스 반환."""
    return StructureMatcher(db=db)
