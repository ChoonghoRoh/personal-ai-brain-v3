"""AI 워크플로우 파이프라인 Steps 1-3: 텍스트 추출, 청크 생성, 키워드 추출

Phase 16-4-1: ai_workflow_service.py 954줄 → 3파일 분리
Mixin 패턴으로 AIWorkflowService에 합성됩니다.
"""
import logging
import os
import re
import time
from typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session

from backend.models.models import Document, KnowledgeChunk, Label, KnowledgeLabel
from backend.services.automation import ai_workflow_state
from backend.services.knowledge.structure_matcher import _extract_keywords
from backend.services.ai.ollama_client import ollama_generate, ollama_available

logger = logging.getLogger(__name__)


class WorkflowExtractMixin:
    """Steps 1-3: 텍스트 추출, 청크 생성, 키워드 추출 Mixin"""

    # LLM 키워드 추출 묶음 호출 배치 크기
    LLM_KEYWORD_BATCH_SIZE = 5

    def _extract_texts(
        self,
        task_id: str,
        document_ids: List[int],
        db: Session,
    ) -> Dict[int, str]:
        """단계 1: 문서 텍스트 추출 (0-15%)

        Args:
            task_id: 태스크 ID
            document_ids: 문서 ID 목록
            db: DB 세션

        Returns:
            {document_id: 텍스트}
        """
        from pathlib import Path

        self._update_progress(
            task_id=task_id,
            stage_name="문서 텍스트 추출",
            progress_pct=0,
            message=f"{len(document_ids)}개 문서 텍스트 추출 중...",
        )

        texts: Dict[int, str] = {}
        total = len(document_ids)
        stage_start = time.time()

        for idx, doc_id in enumerate(document_ids):
            if ai_workflow_state.is_cancelled(task_id):
                raise RuntimeError("사용자에 의해 취소됨")

            document = db.query(Document).filter(Document.id == doc_id).first()
            if not document:
                logger.warning("문서를 찾을 수 없음: %d", doc_id)
                continue

            item_name = document.file_name or f"문서 #{doc_id}"

            # file_path에서 텍스트 추출
            if document.file_path:
                file_path = Path(document.file_path)
                if file_path.exists():
                    text = self.file_parser.parse_file(file_path)
                    if text:
                        texts[doc_id] = text
                    else:
                        logger.warning("텍스트 추출 실패: %s", file_path)
                else:
                    logger.warning("파일이 존재하지 않음: %s", file_path)

            # ETA 계산
            current = idx + 1
            elapsed = time.time() - stage_start
            eta = (elapsed / current) * (total - current) if current > 0 else None

            # 진행률 업데이트
            progress = int(15 * current / total)
            self._update_progress(
                task_id=task_id,
                stage_name="문서 텍스트 추출",
                progress_pct=progress,
                message=f"{current}/{total} 문서 처리 완료",
                detail={"current": current, "total": total, "item_name": item_name},
                eta_seconds=round(eta, 1) if eta is not None else None,
            )

        logger.info("텍스트 추출 완료: %d개 문서", len(texts))
        return texts

    def _create_chunks(
        self,
        task_id: str,
        document_ids: List[int],
        texts: Dict[int, str],
        db: Session,
    ) -> List[int]:
        """단계 2: 청크 생성 (15-30%)

        Args:
            task_id: 태스크 ID
            document_ids: 문서 ID 목록
            texts: 문서별 텍스트
            db: DB 세션

        Returns:
            생성된 청크 ID 목록
        """
        self._update_progress(
            task_id=task_id,
            stage_name="청크 생성",
            progress_pct=15,
            message="텍스트를 청크로 분할 중...",
        )

        chunk_ids: List[int] = []
        total = len(texts)
        stage_start = time.time()

        for idx, (doc_id, text) in enumerate(texts.items()):
            if ai_workflow_state.is_cancelled(task_id):
                raise RuntimeError("사용자에 의해 취소됨")

            # 문서 이름 조회
            document = db.query(Document).filter(Document.id == doc_id).first()
            item_name = document.file_name if document else f"문서 #{doc_id}"

            # 문단 기반 분할 (빈 줄 기준)
            paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

            # 청크 생성 (최대 1000자)
            chunk_index = 0
            current_chunk = ""

            for para in paragraphs:
                if len(current_chunk) + len(para) + 2 > 1000:
                    # 현재 청크 저장
                    if current_chunk:
                        chunk = KnowledgeChunk(
                            document_id=doc_id,
                            chunk_index=chunk_index,
                            content=current_chunk.strip(),
                            status="draft",
                            source="ai_generated",
                        )
                        db.add(chunk)
                        db.flush()
                        chunk_ids.append(chunk.id)
                        chunk_index += 1
                        current_chunk = ""

                current_chunk += para + "\n\n"

            # 마지막 청크 저장
            if current_chunk.strip():
                chunk = KnowledgeChunk(
                    document_id=doc_id,
                    chunk_index=chunk_index,
                    content=current_chunk.strip(),
                    status="draft",
                    source="ai_generated",
                )
                db.add(chunk)
                db.flush()
                chunk_ids.append(chunk.id)

            # ETA 계산
            current = idx + 1
            elapsed = time.time() - stage_start
            eta = (elapsed / current) * (total - current) if current > 0 else None

            # 진행률 업데이트
            progress = 15 + int(15 * current / total)
            self._update_progress(
                task_id=task_id,
                stage_name="청크 생성",
                progress_pct=progress,
                message=f"{len(chunk_ids)}개 청크 생성됨",
                detail={"current": current, "total": total, "item_name": item_name},
                eta_seconds=round(eta, 1) if eta is not None else None,
            )

        db.commit()
        logger.info("청크 생성 완료: %d개", len(chunk_ids))
        return chunk_ids

    def _extract_keywords(
        self,
        task_id: str,
        chunk_ids: List[int],
        db: Session,
    ) -> int:
        """단계 3: 키워드 추출 (30-50%)

        Ollama 가용 시 5~10개 청크를 묶어 1회 LLM 호출로 키워드 추출합니다.

        Args:
            task_id: 태스크 ID
            chunk_ids: 청크 ID 목록
            db: DB 세션

        Returns:
            추출된 키워드 수
        """
        batch_size = int(os.environ.get("LLM_KEYWORD_BATCH_SIZE", self.LLM_KEYWORD_BATCH_SIZE))

        self._update_progress(
            task_id=task_id,
            stage_name="키워드 추출",
            progress_pct=30,
            message="청크에서 키워드 추출 중...",
        )

        keyword_count = 0
        total = len(chunk_ids)
        use_ollama = ollama_available()
        stage_start = time.time()

        # 청크 객체 사전 로드
        all_chunks = db.query(KnowledgeChunk).filter(
            KnowledgeChunk.id.in_(chunk_ids)
        ).all()
        chunk_map: Dict[int, Any] = {c.id: c for c in all_chunks}

        # 배치 분할 처리
        for batch_start in range(0, total, batch_size):
            if ai_workflow_state.is_cancelled(task_id):
                raise RuntimeError("사용자에 의해 취소됨")

            batch_ids = chunk_ids[batch_start:batch_start + batch_size]
            batch_chunks = [chunk_map[cid] for cid in batch_ids if cid in chunk_map]

            if not batch_chunks:
                continue

            # {chunk_id: [keywords]} 맵 구성
            batch_keywords: Dict[int, List[str]] = {c.id: [] for c in batch_chunks}

            # Ollama 묶음 호출
            if use_ollama and len(batch_chunks) > 1:
                batch_keywords = self._llm_batch_keywords(batch_chunks, batch_keywords)
            elif use_ollama:
                chunk = batch_chunks[0]
                batch_keywords[chunk.id] = self._llm_single_keywords(chunk)

            # Ollama 미가용 또는 실패 시: regex fallback
            for chunk in batch_chunks:
                if not batch_keywords.get(chunk.id):
                    batch_keywords[chunk.id] = _extract_keywords(chunk.content, max_words=5)

            # 키워드 → Label/KnowledgeLabel 저장
            for chunk in batch_chunks:
                keywords = batch_keywords.get(chunk.id, [])
                keyword_count += self._save_keywords(chunk.id, keywords, db)

            # ETA 및 진행률 업데이트 (배치 단위)
            processed = min(batch_start + batch_size, total)
            elapsed = time.time() - stage_start
            eta = (elapsed / processed) * (total - processed) if processed > 0 else None

            batch_num = batch_start // batch_size + 1
            total_batches = (total + batch_size - 1) // batch_size
            progress = 30 + int(20 * processed / total)

            self._update_progress(
                task_id=task_id,
                stage_name="키워드 추출",
                progress_pct=progress,
                message=f"{processed}/{total} 청크 처리 완료 (배치 {batch_num}/{total_batches})",
                detail={"current": processed, "total": total, "item_name": f"배치 {batch_num}/{total_batches}"},
                eta_seconds=round(eta, 1) if eta is not None else None,
            )

        db.commit()
        logger.info("키워드 추출 완료: %d개", keyword_count)
        return keyword_count

    def _llm_batch_keywords(
        self,
        batch_chunks: list,
        batch_keywords: Dict[int, List[str]],
    ) -> Dict[int, List[str]]:
        """여러 청크를 묶어 1회 LLM 호출로 키워드 추출."""
        parts = []
        for i, chunk in enumerate(batch_chunks, 1):
            parts.append(f"[{i}]\n{chunk.content[:500]}")
        joined = "\n---\n".join(parts)

        prompt = f"""다음 {len(batch_chunks)}개 텍스트에서 각각 중요한 키워드 5개씩 추출해주세요.
각 텍스트의 결과를 [번호] 형식으로 구분하고, 키워드는 쉼표로 구분하세요.
한글 또는 영어 단어만 추출하세요.

{joined}

결과:"""

        try:
            response = ollama_generate(
                prompt=prompt,
                max_tokens=50 * len(batch_chunks),
                temperature=0.3,
            )
            if response:
                batch_keywords = self._parse_batch_keywords(
                    response, batch_chunks, batch_keywords,
                )
        except Exception as e:
            logger.debug("LLM 묶음 키워드 추출 실패: %s", e)

        return batch_keywords

    @staticmethod
    def _parse_batch_keywords(
        response: str,
        batch_chunks: list,
        batch_keywords: Dict[int, List[str]],
    ) -> Dict[int, List[str]]:
        """LLM 응답에서 [N] kw1, kw2 형식을 파싱하여 chunk별 키워드 할당."""
        pattern = re.compile(r"\[(\d+)\]\s*(.+)")
        for line in response.split("\n"):
            line = line.strip()
            match = pattern.match(line)
            if not match:
                continue
            idx = int(match.group(1))
            kw_str = match.group(2)
            if 1 <= idx <= len(batch_chunks):
                chunk = batch_chunks[idx - 1]
                keywords = [kw.strip() for kw in kw_str.split(",") if kw.strip()]
                batch_keywords[chunk.id] = keywords[:5]
        return batch_keywords

    @staticmethod
    def _llm_single_keywords(chunk) -> List[str]:
        """단일 청크에 대한 LLM 키워드 추출 (기존 호환)."""
        try:
            prompt = f"""다음 텍스트에서 중요한 키워드 5개를 추출해주세요.
각 키워드는 쉼표로 구분하고, 한글 또는 영어 단어만 추출하세요.

텍스트:
{chunk.content[:500]}

키워드:"""
            response = ollama_generate(
                prompt=prompt,
                max_tokens=100,
                temperature=0.3,
            )
            if response:
                keywords = [kw.strip() for kw in response.split(",") if kw.strip()]
                return keywords[:5]
        except Exception as e:
            logger.debug("Ollama 키워드 추출 실패: %s", e)
        return []

    def _save_keywords(
        self,
        chunk_id: int,
        keywords: List[str],
        db: Session,
    ) -> int:
        """키워드 목록을 Label/KnowledgeLabel 테이블에 저장.

        Returns:
            새로 생성된 KnowledgeLabel 수
        """
        count = 0
        for kw in keywords:
            if not kw or len(kw) < 2:
                continue

            label = db.query(Label).filter(
                Label.name == kw,
                Label.label_type == "keyword",
            ).first()

            if not label:
                label = Label(
                    name=kw,
                    label_type="keyword",
                    description=f"AI 추출 키워드: {kw}",
                )
                db.add(label)
                db.flush()

            existing = db.query(KnowledgeLabel).filter(
                KnowledgeLabel.chunk_id == chunk_id,
                KnowledgeLabel.label_id == label.id,
            ).first()

            if not existing:
                knowledge_label = KnowledgeLabel(
                    chunk_id=chunk_id,
                    label_id=label.id,
                    status="suggested",
                    source="ai",
                    confidence=0.8,
                )
                db.add(knowledge_label)
                count += 1
        return count
