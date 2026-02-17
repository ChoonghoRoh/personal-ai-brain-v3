"""Reasoning 스트리밍 실행 엔진 (reason_stream.py에서 분리)

execute_reasoning_with_progress 및 관련 헬퍼 함수를 포함합니다.
"""
import asyncio
import json
import time
import logging
from typing import Dict, List, Optional, AsyncGenerator
from sqlalchemy.orm import Session

from backend.models.models import (
    Project, Document, KnowledgeChunk, Label, KnowledgeLabel, KnowledgeRelation,
)
from backend.services.search.search_service import get_search_service
from backend.services.reasoning.dynamic_reasoning_service import get_dynamic_reasoning_service
from backend.services.reasoning.recommendation_service import get_recommendation_service
from backend.routers.reasoning.reason_helpers import (
    collect_chunks_by_document_ids,
    collect_chunks_by_question_in_documents,
)

logger = logging.getLogger(__name__)

# 진행 중인 태스크 관리 (취소 기능용)
active_tasks: Dict[str, Dict] = {}

# 진행 단계 정의
PROGRESS_STAGES = [
    {"stage": 1, "message": "질문 분석 중...", "percent": 10},
    {"stage": 2, "message": "관련 문서 검색 중...", "percent": 30},
    {"stage": 3, "message": "연관 지식 확장 중...", "percent": 50},
    {"stage": 4, "message": "AI 추론 중...", "percent": 70},
    {"stage": 5, "message": "추천 정보 생성 중...", "percent": 90},
]


def format_sse_event(event_type: str, data: dict) -> str:
    """SSE 형식으로 이벤트 포맷팅"""
    return f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


# ---------------------------------------------------------------------------
# 지식 수집 헬퍼 (스트리밍 전용 — 간소화 버전)
# ---------------------------------------------------------------------------

def collect_knowledge_from_projects(db: Session, project_ids: List[int]) -> List[KnowledgeChunk]:
    """프로젝트에서 지식 청크 수집"""
    chunks = []
    for project_id in project_ids:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            continue
        documents = db.query(Document).filter(Document.project_id == project_id).all()
        for doc in documents:
            doc_chunks = db.query(KnowledgeChunk).filter(
                KnowledgeChunk.document_id == doc.id,
                KnowledgeChunk.status == "approved"
            ).all()
            chunks.extend(doc_chunks)
    return chunks


def collect_knowledge_from_labels(db: Session, label_names: List[str]) -> List[KnowledgeChunk]:
    """라벨에서 지식 수집"""
    chunks = []
    labels = db.query(Label).filter(Label.name.in_(label_names)).all()
    for label in labels:
        knowledge_labels = db.query(KnowledgeLabel).filter(KnowledgeLabel.label_id == label.id).all()
        for kl in knowledge_labels:
            chunk = db.query(KnowledgeChunk).filter(
                KnowledgeChunk.id == kl.chunk_id,
                KnowledgeChunk.status == "approved"
            ).first()
            if chunk:
                chunks.append(chunk)
    return chunks


def collect_knowledge_from_label_ids(db: Session, label_ids: List[int]) -> List[KnowledgeChunk]:
    """라벨 ID로 지식 수집"""
    chunks = []
    knowledge_labels = db.query(KnowledgeLabel).filter(
        KnowledgeLabel.label_id.in_(label_ids),
        KnowledgeLabel.status == "confirmed"
    ).all()
    chunk_ids = {kl.chunk_id for kl in knowledge_labels}
    if chunk_ids:
        chunks = db.query(KnowledgeChunk).filter(
            KnowledgeChunk.id.in_(chunk_ids),
            KnowledgeChunk.status == "approved"
        ).all()
    return chunks


def trace_relations(db: Session, chunks: List[KnowledgeChunk], depth: int = 2) -> List[KnowledgeChunk]:
    """관계를 따라 지식 청크 추적"""
    all_chunks = {chunk.id: chunk for chunk in chunks}
    current_chunk_ids = [chunk.id for chunk in chunks]

    for _ in range(depth):
        if not current_chunk_ids:
            break
        relations = db.query(KnowledgeRelation).filter(
            (
                (KnowledgeRelation.source_chunk_id.in_(current_chunk_ids)) |
                (KnowledgeRelation.target_chunk_id.in_(current_chunk_ids))
            ),
            KnowledgeRelation.confirmed == "true"
        ).all()

        related_chunk_ids = set()
        for rel in relations:
            if rel.source_chunk_id in current_chunk_ids:
                related_chunk_ids.add(rel.target_chunk_id)
            if rel.target_chunk_id in current_chunk_ids:
                related_chunk_ids.add(rel.source_chunk_id)

        related_chunk_ids = related_chunk_ids - set(all_chunks.keys())
        if not related_chunk_ids:
            break

        next_chunks = db.query(KnowledgeChunk).filter(
            KnowledgeChunk.id.in_(related_chunk_ids),
            KnowledgeChunk.status == "approved"
        ).all()

        for chunk in next_chunks:
            all_chunks[chunk.id] = chunk
        current_chunk_ids = [chunk.id for chunk in next_chunks]

    return list(all_chunks.values())


# ---------------------------------------------------------------------------
# 비동기 토큰 스트리밍
# ---------------------------------------------------------------------------

async def _async_stream_tokens(sync_gen):
    """동기 제너레이터를 비동기로 변환 (executor에서 next() 호출) -- Phase 10-4-1."""
    loop = asyncio.get_event_loop()
    it = iter(sync_gen)
    while True:
        try:
            token = await loop.run_in_executor(None, next, it)
            yield token
        except StopIteration:
            break


# ---------------------------------------------------------------------------
# 메인 실행기
# ---------------------------------------------------------------------------

async def execute_reasoning_with_progress(
    task_id: str,
    request,
    db: Session,
) -> AsyncGenerator[str, None]:
    """진행 상태를 포함한 Reasoning 실행 (제너레이터)"""
    start_time = time.time()
    reasoning_steps = []

    # 태스크 등록
    active_tasks[task_id] = {
        "status": "running",
        "started_at": start_time,
        "cancelled": False,
    }

    try:
        # Stage 1: 질문 분석
        yield format_sse_event("progress", {
            "task_id": task_id,
            "stage": 1,
            "total_stages": 5,
            "message": "질문 분석 중...",
            "percent": 10,
            "elapsed": round(time.time() - start_time, 1),
        })

        if active_tasks.get(task_id, {}).get("cancelled"):
            yield format_sse_event("cancelled", {"task_id": task_id, "message": "사용자에 의해 취소됨"})
            return

        reasoning_steps.append("입력 파싱 중...")
        project_ids = request.inputs.get("projects", [])
        label_names = request.inputs.get("labels", [])
        filter_label_ids = []

        # Phase 15-3: document_ids 파싱
        document_ids = []
        if request.filters:
            if request.filters.category_label_ids:
                filter_label_ids.extend(request.filters.category_label_ids)
            if request.filters.keyword_group_ids:
                filter_label_ids.extend(request.filters.keyword_group_ids)
            if request.filters.keyword_ids:
                filter_label_ids.extend(request.filters.keyword_ids)
            if request.filters.project_ids:
                project_ids = list(set(project_ids + request.filters.project_ids))
            if request.filters.document_ids:
                document_ids = request.filters.document_ids

        question = (request.question or "").strip()
        await asyncio.sleep(0.1)

        # Stage 2: 관련 문서 검색
        yield format_sse_event("progress", {
            "task_id": task_id,
            "stage": 2,
            "total_stages": 5,
            "message": "관련 문서 검색 중...",
            "percent": 30,
            "elapsed": round(time.time() - start_time, 1),
        })

        if active_tasks.get(task_id, {}).get("cancelled"):
            yield format_sse_event("cancelled", {"task_id": task_id, "message": "사용자에 의해 취소됨"})
            return

        chunks = []

        # Phase 15-3: 문서 기반 수집 우선
        if document_ids:
            if question:
                chunks = collect_chunks_by_question_in_documents(
                    db, question, document_ids, top_k=20, reasoning_steps=reasoning_steps
                )
                if len(chunks) < 5:
                    doc_chunks = collect_chunks_by_document_ids(db, document_ids)
                    seen = {c.id for c in chunks}
                    for c in doc_chunks:
                        if c.id not in seen:
                            seen.add(c.id)
                            chunks.append(c)
                    reasoning_steps.append(f"문서 전체 청크 보강: 총 {len(chunks)}개")
            else:
                chunks = collect_chunks_by_document_ids(db, document_ids)
                reasoning_steps.append(f"문서에서 {len(chunks)}개 청크 수집")
        elif question:
            reasoning_steps.append("질문 기반 의미 검색 중...")
            search_service = get_search_service()
            search_results = search_service.search_simple(question.strip(), top_k=20, use_cache=False)
            seen = set()
            for result in search_results:
                qdrant_id = result.get("document_id")
                chunk = db.query(KnowledgeChunk).filter(
                    KnowledgeChunk.qdrant_point_id == str(qdrant_id),
                    KnowledgeChunk.status == "approved",
                ).first()
                if chunk and chunk.id not in seen:
                    seen.add(chunk.id)
                    chunks.append(chunk)
            reasoning_steps.append(f"의미 검색으로 {len(chunks)}개 청크 수집")

        # 보조 필터 적용 (문서 필터가 아닌 경우)
        if not document_ids:
            if project_ids:
                project_chunks = collect_knowledge_from_projects(db, project_ids)
                seen = {c.id for c in chunks}
                for c in project_chunks:
                    if c.id not in seen:
                        seen.add(c.id)
                        chunks.append(c)
                reasoning_steps.append(f"프로젝트에서 {len(project_chunks)}개 청크 수집")

            if label_names:
                label_chunks = collect_knowledge_from_labels(db, label_names)
                seen = {c.id for c in chunks}
                for c in label_chunks:
                    if c.id not in seen:
                        seen.add(c.id)
                        chunks.append(c)
                reasoning_steps.append(f"라벨에서 {len(label_chunks)}개 청크 수집")

            if filter_label_ids:
                filter_chunks = collect_knowledge_from_label_ids(db, filter_label_ids)
                seen = {c.id for c in chunks}
                for c in filter_chunks:
                    if c.id not in seen:
                        seen.add(c.id)
                        chunks.append(c)
                reasoning_steps.append(f"키워드 필터에서 {len(filter_chunks)}개 청크 수집")

        # 질문 없이 필터도 없을 때 폴백
        if not chunks and not question and not document_ids:
            fallback = db.query(KnowledgeChunk).filter(
                KnowledgeChunk.status == "approved"
            ).order_by(KnowledgeChunk.id.desc()).limit(100).all()
            if fallback:
                chunks = fallback
                reasoning_steps.append(f"필터 없음 → 승인된 전체 청크 {len(fallback)}개 사용")

        await asyncio.sleep(0.1)

        # Stage 3: 연관 지식 확장
        yield format_sse_event("progress", {
            "task_id": task_id,
            "stage": 3,
            "total_stages": 5,
            "message": "연관 지식 확장 중...",
            "percent": 50,
            "elapsed": round(time.time() - start_time, 1),
        })

        if active_tasks.get(task_id, {}).get("cancelled"):
            yield format_sse_event("cancelled", {"task_id": task_id, "message": "사용자에 의해 취소됨"})
            return

        reasoning_steps.append("관계 추적 중...")
        all_chunks = trace_relations(db, chunks, depth=2)
        reasoning_steps.append(f"관계를 통해 {len(all_chunks) - len(chunks)}개 추가 청크 발견")

        await asyncio.sleep(0.1)

        # 컨텍스트 구성
        chunks_to_process = all_chunks[:20]
        chunk_ids = [c.id for c in chunks_to_process]

        document_ids = list(set([chunk.document_id for chunk in chunks_to_process]))
        documents = {doc.id: doc for doc in db.query(Document).filter(Document.id.in_(document_ids)).all()}

        project_ids_list = list(set([doc.project_id for doc in documents.values() if doc.project_id]))
        projects = {proj.id: proj for proj in db.query(Project).filter(Project.id.in_(project_ids_list)).all()} if project_ids_list else {}

        chunk_labels: Dict[int, List[str]] = {cid: [] for cid in chunk_ids}
        if chunk_ids:
            knowledge_labels = (
                db.query(KnowledgeLabel.chunk_id, Label.name)
                .join(Label, KnowledgeLabel.label_id == Label.id)
                .filter(
                    KnowledgeLabel.chunk_id.in_(chunk_ids),
                    KnowledgeLabel.status == "confirmed",
                )
                .all()
            )
            for cid, name in knowledge_labels:
                if name and cid in chunk_labels:
                    chunk_labels[cid].append(name)

        context_chunks = []
        for chunk in chunks_to_process:
            doc = documents.get(chunk.document_id)
            project = projects.get(doc.project_id) if doc and doc.project_id else None
            context_chunks.append({
                "id": chunk.id,
                "content": chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content,
                "document": doc.file_name if doc else None,
                "project": project.name if project else None,
                "project_id": doc.project_id if doc else None,
                "labels": chunk_labels.get(chunk.id) or [],
            })

        # 관계 정보 수집
        relations = []
        if chunks[:10]:
            chunk_ids_for_rel = [chunk.id for chunk in chunks[:10]]
            all_relations = db.query(KnowledgeRelation).filter(
                KnowledgeRelation.source_chunk_id.in_(chunk_ids_for_rel)
            ).all()
            target_chunk_ids = list(set([rel.target_chunk_id for rel in all_relations]))
            target_chunks = {
                chunk.id: chunk
                for chunk in db.query(KnowledgeChunk).filter(KnowledgeChunk.id.in_(target_chunk_ids)).all()
            }
            chunk_dict = {chunk.id: chunk for chunk in chunks[:10]}
            for rel in all_relations:
                source_chunk = chunk_dict.get(rel.source_chunk_id)
                target_chunk = target_chunks.get(rel.target_chunk_id)
                if source_chunk and target_chunk:
                    relations.append({
                        "type": rel.relation_type,
                        "source": source_chunk.content[:50],
                        "target": target_chunk.content[:50],
                        "description": rel.description,
                    })

        # Stage 4: AI 추론
        yield format_sse_event("progress", {
            "task_id": task_id,
            "stage": 4,
            "total_stages": 5,
            "message": "AI 추론 중...",
            "percent": 70,
            "elapsed": round(time.time() - start_time, 1),
        })

        if active_tasks.get(task_id, {}).get("cancelled"):
            yield format_sse_event("cancelled", {"task_id": task_id, "message": "사용자에 의해 취소됨"})
            return

        reasoning_steps.append("Reasoning 실행 중...")
        dynamic_svc = get_dynamic_reasoning_service()

        # Phase 10-4-1: 토큰 단위 스트리밍 시도
        answer_parts = []
        try:
            async for token in _async_stream_tokens(
                dynamic_svc.generate_reasoning_stream(
                    request.question, context_chunks, request.mode,
                    max_tokens=500, model=request.model
                )
            ):
                if active_tasks.get(task_id, {}).get("cancelled"):
                    yield format_sse_event("cancelled", {"task_id": task_id, "message": "사용자에 의해 취소됨"})
                    return
                answer_parts.append(token)
                yield format_sse_event("answer_token", {"task_id": task_id, "token": token})
        except Exception as e:
            logger.debug("Streaming fallback triggered: %s", e)

        if answer_parts:
            answer = dynamic_svc._postprocess_reasoning("".join(answer_parts))
        else:
            answer = dynamic_svc.generate_reasoning(
                request.question, context_chunks, request.mode, max_tokens=500, model=request.model
            )

        if answer is None:
            mode = request.mode
            if mode == "design_explain":
                answer = f"📐 설계/배경 설명\n\n수집된 {len(all_chunks)}개 지식 조각을 기반으로 설계 배경과 맥락을 설명합니다."
            elif mode == "risk_review":
                answer = f"⚠️ 리스크 분석\n\n{len(all_chunks)}개 관련 지식을 분석하여 잠재적 리스크를 식별합니다."
            elif mode == "next_steps":
                answer = f"🚀 다음 단계 제안\n\n{len(all_chunks)}개 관련 지식을 기반으로 다음 단계를 제안합니다."
            else:
                answer = f"📜 히스토리/맥락 추적\n\n{len(all_chunks)}개 지식을 시간적/논리적 순서로 추적합니다."

        reasoning_steps.append("Reasoning 완료")

        # Stage 5: 추천 정보 생성
        yield format_sse_event("progress", {
            "task_id": task_id,
            "stage": 5,
            "total_stages": 5,
            "message": "추천 정보 생성 중...",
            "percent": 90,
            "elapsed": round(time.time() - start_time, 1),
        })

        if active_tasks.get(task_id, {}).get("cancelled"):
            yield format_sse_event("cancelled", {"task_id": task_id, "message": "사용자에 의해 취소됨"})
            return

        recommendations = None
        try:
            rec_svc = get_recommendation_service(db)
            context_chunk_ids = [c.get("id") for c in context_chunks if c.get("id")]
            related_chunks = rec_svc.recommend_related_chunks(context_chunk_ids, limit=5) if context_chunk_ids else []
            combined_content = " ".join([(c.get("content") or "")[:300] for c in context_chunks])
            suggested_labels = rec_svc.recommend_labels(combined_content, limit=5) if combined_content.strip() else []
            sample_questions = rec_svc.generate_sample_questions(limit=3, model=request.model)
            explore_more = rec_svc.suggest_exploration(context_chunk_ids=context_chunk_ids, limit=5)
            recommendations = {
                "related_chunks": related_chunks,
                "suggested_labels": suggested_labels,
                "sample_questions": sample_questions,
                "explore_more": explore_more,
            }
        except Exception as e:
            logger.debug("recommendations build failed: %s", e)

        # 완료
        elapsed_time = round(time.time() - start_time, 1)
        yield format_sse_event("progress", {
            "task_id": task_id,
            "stage": 5,
            "total_stages": 5,
            "message": "완료!",
            "percent": 100,
            "elapsed": elapsed_time,
        })

        # 최종 결과 전송
        result = {
            "task_id": task_id,
            "answer": answer,
            "context_chunks": context_chunks,
            "relations": relations,
            "reasoning_steps": reasoning_steps,
            "recommendations": recommendations,
            "elapsed_time": elapsed_time,
        }
        yield format_sse_event("result", result)
        yield format_sse_event("done", {"task_id": task_id})

    except Exception as e:
        logger.error("Reasoning error: %s", e)
        yield format_sse_event("error", {
            "task_id": task_id,
            "message": str(e),
        })
    finally:
        if task_id in active_tasks:
            del active_tasks[task_id]
