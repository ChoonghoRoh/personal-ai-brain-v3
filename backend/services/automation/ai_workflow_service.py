"""AI 자동화 워크플로우 서비스 (Phase 15-2-2)

문서 선택부터 임베딩까지 6단계 AI 자동화 파이프라인을 구현합니다.
기존 서비스를 오케스트레이션하고 각 단계별 진행 상황을 상태 관리자에 업데이트합니다.
"""
import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from backend.models.models import Document, KnowledgeChunk, Label, KnowledgeLabel
from backend.services.automation import ai_workflow_state
from backend.services.ingest.file_parser_service import FileParserService
from backend.services.knowledge.structure_matcher import _extract_keywords
from backend.services.knowledge.auto_labeler import get_auto_labeler
from backend.services.knowledge.chunk_sync_service import sync_chunk_to_qdrant
from backend.services.ai.ollama_client import ollama_generate, ollama_available

logger = logging.getLogger(__name__)


class AIWorkflowService:
    """AI 자동화 워크플로우 파이프라인 서비스"""

    def __init__(self):
        self.file_parser = FileParserService()

    def execute_workflow(self, task_id: str, db: Session) -> None:
        """6단계 워크플로우 실행

        Args:
            task_id: 태스크 ID
            db: DB 세션
        """
        task = ai_workflow_state.get_task(task_id)
        if not task:
            logger.error("태스크를 찾을 수 없음: %s", task_id)
            return

        try:
            # 단계 1: 문서 텍스트 추출 (0-15%)
            if ai_workflow_state.is_cancelled(task_id):
                return
            texts = self._extract_texts(task_id, task.document_ids, db)

            # 단계 2: 청크 생성 (15-30%)
            if ai_workflow_state.is_cancelled(task_id):
                return
            chunk_ids = self._create_chunks(task_id, task.document_ids, texts, db)

            # 단계 3: 키워드 추출 (30-50%)
            if ai_workflow_state.is_cancelled(task_id):
                return
            keyword_count = self._extract_keywords(task_id, chunk_ids, db)

            # 단계 4: 라벨 생성/매칭 (50-70%)
            if ai_workflow_state.is_cancelled(task_id):
                return
            label_count = self._match_labels(task_id, chunk_ids, db)

            # 단계 5: 승인 처리 (70-80%)
            if ai_workflow_state.is_cancelled(task_id):
                return
            approved_count = self._approve_items(task_id, chunk_ids, task.auto_approve, db)

            # 단계 6: Qdrant 임베딩 (80-100%, auto_approve=True인 경우만)
            embedded_count = 0
            if task.auto_approve:
                if ai_workflow_state.is_cancelled(task_id):
                    return
                embedded_count = self._embed_chunks(task_id, chunk_ids, db)

            # 완료
            results = {
                "chunk_ids": chunk_ids,
                "chunks_created": len(chunk_ids),
                "keywords_extracted": keyword_count,
                "labels_matched": label_count,
                "chunks_approved": approved_count,
                "chunks_embedded": embedded_count,
            }
            ai_workflow_state.complete_task(task_id, results)

            logger.info(
                "AI 워크플로우 완료: task_id=%s chunks=%d keywords=%d labels=%d",
                task_id,
                len(chunk_ids),
                keyword_count,
                label_count,
            )

        except Exception as e:
            logger.exception("AI 워크플로우 실패: task_id=%s", task_id)
            ai_workflow_state.fail_task(
                task_id=task_id,
                error=str(e),
                failed_stage=ai_workflow_state.get_task(task_id).current_stage if ai_workflow_state.get_task(task_id) else None,
            )

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
        ai_workflow_state.update_progress(
            task_id=task_id,
            stage_name="문서 텍스트 추출",
            progress_pct=0,
            message=f"{len(document_ids)}개 문서 텍스트 추출 중...",
        )

        texts: Dict[int, str] = {}
        total = len(document_ids)

        for idx, doc_id in enumerate(document_ids):
            if ai_workflow_state.is_cancelled(task_id):
                raise RuntimeError("사용자에 의해 취소됨")

            document = db.query(Document).filter(Document.id == doc_id).first()
            if not document:
                logger.warning("문서를 찾을 수 없음: %d", doc_id)
                continue

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

            # 진행률 업데이트
            progress = int(15 * (idx + 1) / total)
            ai_workflow_state.update_progress(
                task_id=task_id,
                stage_name="문서 텍스트 추출",
                progress_pct=progress,
                message=f"{idx + 1}/{total} 문서 처리 완료",
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
        ai_workflow_state.update_progress(
            task_id=task_id,
            stage_name="청크 생성",
            progress_pct=15,
            message="텍스트를 청크로 분할 중...",
        )

        chunk_ids: List[int] = []
        total = len(texts)

        for idx, (doc_id, text) in enumerate(texts.items()):
            if ai_workflow_state.is_cancelled(task_id):
                raise RuntimeError("사용자에 의해 취소됨")

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

            # 진행률 업데이트
            progress = 15 + int(15 * (idx + 1) / total)
            ai_workflow_state.update_progress(
                task_id=task_id,
                stage_name="청크 생성",
                progress_pct=progress,
                message=f"{len(chunk_ids)}개 청크 생성됨",
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

        Args:
            task_id: 태스크 ID
            chunk_ids: 청크 ID 목록
            db: DB 세션

        Returns:
            추출된 키워드 수
        """
        ai_workflow_state.update_progress(
            task_id=task_id,
            stage_name="키워드 추출",
            progress_pct=30,
            message="청크에서 키워드 추출 중...",
        )

        keyword_count = 0
        total = len(chunk_ids)
        use_ollama = ollama_available()

        for idx, chunk_id in enumerate(chunk_ids):
            if ai_workflow_state.is_cancelled(task_id):
                raise RuntimeError("사용자에 의해 취소됨")

            chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == chunk_id).first()
            if not chunk:
                continue

            keywords: List[str] = []

            # Ollama 가용 시: LLM 기반 키워드 추출
            if use_ollama:
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
                        # 쉼표로 분리
                        keywords = [kw.strip() for kw in response.split(",") if kw.strip()]
                        keywords = keywords[:5]
                except Exception as e:
                    logger.debug("Ollama 키워드 추출 실패: %s", e)
                    keywords = []

            # Ollama 미가용 또는 실패 시: regex 기반 fallback
            if not keywords:
                keywords = _extract_keywords(chunk.content, max_words=5)

            # Label 테이블에 keyword 타입으로 저장
            for kw in keywords:
                if not kw or len(kw) < 2:
                    continue

                # 기존 라벨 조회 또는 생성
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

                # KnowledgeLabel 생성 (중복 체크)
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
                    keyword_count += 1

            # 진행률 업데이트
            progress = 30 + int(20 * (idx + 1) / total)
            ai_workflow_state.update_progress(
                task_id=task_id,
                stage_name="키워드 추출",
                progress_pct=progress,
                message=f"{idx + 1}/{total} 청크 처리 완료",
            )

        db.commit()
        logger.info("키워드 추출 완료: %d개", keyword_count)
        return keyword_count

    def _match_labels(
        self,
        task_id: str,
        chunk_ids: List[int],
        db: Session,
    ) -> int:
        """단계 4: 라벨 생성/매칭 (50-70%)

        Args:
            task_id: 태스크 ID
            chunk_ids: 청크 ID 목록
            db: DB 세션

        Returns:
            매칭된 라벨 수
        """
        ai_workflow_state.update_progress(
            task_id=task_id,
            stage_name="라벨 생성/매칭",
            progress_pct=50,
            message="청크에 라벨 추천 중...",
        )

        label_count = 0
        total = len(chunk_ids)
        auto_labeler = get_auto_labeler(db)

        for idx, chunk_id in enumerate(chunk_ids):
            if ai_workflow_state.is_cancelled(task_id):
                raise RuntimeError("사용자에 의해 취소됨")

            chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == chunk_id).first()
            if not chunk:
                continue

            # auto_labeler.label_on_import() 활용
            # 이미 document와 chunks가 있으므로 간단히 apply_suggested_labels 사용
            # 여기서는 기존 라벨과의 매칭만 수행 (키워드는 단계 3에서 이미 처리)

            # 청크 내용 기반 기존 라벨 검색 (간단한 텍스트 매칭)
            chunk_text_lower = chunk.content.lower()
            all_labels = db.query(Label).filter(
                Label.label_type.in_(["category", "domain", "project"])
            ).all()

            for label in all_labels:
                label_name_lower = label.name.lower()
                if label_name_lower in chunk_text_lower:
                    # 기존 라벨 적용
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
                            confidence=0.7,
                        )
                        db.add(knowledge_label)
                        label_count += 1

            # 진행률 업데이트
            progress = 50 + int(20 * (idx + 1) / total)
            ai_workflow_state.update_progress(
                task_id=task_id,
                stage_name="라벨 생성/매칭",
                progress_pct=progress,
                message=f"{idx + 1}/{total} 청크 처리 완료",
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
        ai_workflow_state.update_progress(
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

            ai_workflow_state.update_progress(
                task_id=task_id,
                stage_name="승인 처리",
                progress_pct=80,
                message=f"{approved_count}개 청크 자동 승인됨",
            )
        else:
            # auto_approve=False: draft/suggested 상태 유지
            ai_workflow_state.update_progress(
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
        """단계 6: Qdrant 임베딩 (80-100%)

        Args:
            task_id: 태스크 ID
            chunk_ids: 청크 ID 목록
            db: DB 세션

        Returns:
            임베딩된 청크 수
        """
        ai_workflow_state.update_progress(
            task_id=task_id,
            stage_name="Qdrant 임베딩",
            progress_pct=80,
            message="Qdrant에 벡터 임베딩 중...",
        )

        embedded_count = 0
        total = len(chunk_ids)

        # 승인된 청크만 임베딩
        chunks = db.query(KnowledgeChunk).filter(
            KnowledgeChunk.id.in_(chunk_ids),
            KnowledgeChunk.status == "approved",
        ).all()

        for idx, chunk in enumerate(chunks):
            if ai_workflow_state.is_cancelled(task_id):
                raise RuntimeError("사용자에 의해 취소됨")

            try:
                # chunk_sync_service.sync_chunk_to_qdrant() 호출
                result = sync_chunk_to_qdrant(db, chunk.id)
                if result.success:
                    embedded_count += 1
                else:
                    logger.warning("Qdrant 동기화 실패: chunk_id=%d error=%s", chunk.id, result.error)
            except Exception as e:
                logger.warning("Qdrant 임베딩 실패: chunk_id=%d error=%s", chunk.id, e)
                # Qdrant 미연결 시에도 계속 진행 (skip)
                continue

            # 진행률 업데이트
            progress = 80 + int(20 * (idx + 1) / total)
            ai_workflow_state.update_progress(
                task_id=task_id,
                stage_name="Qdrant 임베딩",
                progress_pct=progress,
                message=f"{idx + 1}/{total} 청크 처리 완료",
            )

        logger.info("Qdrant 임베딩 완료: %d개", embedded_count)
        return embedded_count


def get_ai_workflow_service() -> AIWorkflowService:
    """AIWorkflowService 인스턴스 반환"""
    return AIWorkflowService()
