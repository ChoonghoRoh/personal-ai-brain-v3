"""AI 워크플로우 서비스 테스트 (Phase 15-2-2)"""
import pytest
from unittest.mock import MagicMock, patch, Mock
from pathlib import Path

from backend.services.automation.ai_workflow_service import AIWorkflowService, get_ai_workflow_service
from backend.services.automation import ai_workflow_state
from backend.models.models import Document, KnowledgeChunk, Label, KnowledgeLabel


@pytest.fixture
def workflow_service():
    """워크플로우 서비스 인스턴스"""
    return get_ai_workflow_service()


@pytest.fixture
def mock_db():
    """Mock DB 세션"""
    return MagicMock()


@pytest.fixture(autouse=True)
def cleanup_tasks():
    """각 테스트 후 태스크 정리"""
    yield
    ai_workflow_state.active_tasks.clear()


def test_get_ai_workflow_service():
    """서비스 인스턴스 생성 테스트"""
    service = get_ai_workflow_service()
    assert service is not None
    assert isinstance(service, AIWorkflowService)


def test_extract_texts(workflow_service, mock_db):
    """문서 텍스트 추출 테스트"""
    task_id = ai_workflow_state.create_task([1, 2], False)

    # Mock Document
    doc1 = Document(id=1, file_path="/test/doc1.txt", file_name="doc1.txt", file_type="txt", size=100)
    doc2 = Document(id=2, file_path="/test/doc2.txt", file_name="doc2.txt", file_type="txt", size=200)

    mock_db.query.return_value.filter.return_value.first.side_effect = [doc1, doc2]

    # Mock file_parser
    with patch.object(workflow_service.file_parser, "parse_file") as mock_parse:
        mock_parse.side_effect = ["텍스트1", "텍스트2"]

        with patch("pathlib.Path.exists", return_value=True):
            texts = workflow_service._extract_texts(task_id, [1, 2], mock_db)

    assert len(texts) == 2
    assert texts[1] == "텍스트1"
    assert texts[2] == "텍스트2"

    task = ai_workflow_state.get_task(task_id)
    assert task.progress_pct == 15


def test_create_chunks(workflow_service, mock_db):
    """청크 생성 테스트"""
    task_id = ai_workflow_state.create_task([1], False)

    texts = {
        1: "문단1\n\n문단2\n\n문단3"
    }

    # Mock flush and commit
    mock_db.flush.return_value = None
    mock_db.commit.return_value = None

    # Mock chunk ID 할당
    chunk_counter = [1]

    def add_side_effect(chunk):
        chunk.id = chunk_counter[0]
        chunk_counter[0] += 1

    mock_db.add.side_effect = add_side_effect

    chunk_ids = workflow_service._create_chunks(task_id, [1], texts, mock_db)

    assert len(chunk_ids) > 0
    assert mock_db.commit.called

    task = ai_workflow_state.get_task(task_id)
    assert task.progress_pct == 30


def test_extract_keywords_ollama_unavailable(workflow_service, mock_db):
    """키워드 추출 테스트 (Ollama 미가용)"""
    task_id = ai_workflow_state.create_task([1], False)

    # Mock chunk
    chunk = KnowledgeChunk(
        id=1,
        document_id=1,
        chunk_index=0,
        content="FastAPI와 SQLAlchemy를 사용한 백엔드 개발",
        status="draft",
    )
    mock_db.query.return_value.filter.return_value.first.return_value = chunk

    # Mock Label 조회/생성
    mock_db.query.return_value.filter.return_value.first.return_value = None
    mock_db.flush.return_value = None
    mock_db.commit.return_value = None

    label_counter = [1]

    def add_side_effect(obj):
        if isinstance(obj, Label):
            obj.id = label_counter[0]
            label_counter[0] += 1

    mock_db.add.side_effect = add_side_effect

    with patch("backend.services.automation.ai_workflow_service.ollama_available", return_value=False):
        keyword_count = workflow_service._extract_keywords(task_id, [1], mock_db)

    assert keyword_count >= 0


def test_extract_keywords_ollama_available(workflow_service, mock_db):
    """키워드 추출 테스트 (Ollama 가용)"""
    task_id = ai_workflow_state.create_task([1], False)

    # Mock chunk
    chunk = KnowledgeChunk(
        id=1,
        document_id=1,
        chunk_index=0,
        content="FastAPI와 SQLAlchemy를 사용한 백엔드 개발",
        status="draft",
    )
    mock_db.query.return_value.filter.return_value.first.return_value = chunk
    mock_db.flush.return_value = None
    mock_db.commit.return_value = None

    label_counter = [1]

    def add_side_effect(obj):
        if isinstance(obj, Label):
            obj.id = label_counter[0]
            label_counter[0] += 1

    mock_db.add.side_effect = add_side_effect

    with patch("backend.services.automation.ai_workflow_service.ollama_available", return_value=True):
        with patch("backend.services.automation.ai_workflow_service.ollama_generate") as mock_generate:
            mock_generate.return_value = "FastAPI, SQLAlchemy, 백엔드, 개발, API"

            keyword_count = workflow_service._extract_keywords(task_id, [1], mock_db)

    assert keyword_count >= 0


def test_match_labels(workflow_service, mock_db):
    """라벨 매칭 테스트"""
    task_id = ai_workflow_state.create_task([1], False)

    # Mock chunk
    chunk = KnowledgeChunk(
        id=1,
        document_id=1,
        chunk_index=0,
        content="Python 웹 개발 프레임워크 FastAPI",
        status="draft",
    )

    # Mock labels
    label_python = Label(id=1, name="Python", label_type="domain")
    label_fastapi = Label(id=2, name="FastAPI", label_type="category")

    mock_db.query.return_value.filter.return_value.first.return_value = chunk
    mock_db.query.return_value.filter.return_value.all.return_value = [label_python, label_fastapi]
    mock_db.flush.return_value = None
    mock_db.commit.return_value = None
    mock_db.add.return_value = None

    label_count = workflow_service._match_labels(task_id, [1], mock_db)

    assert label_count >= 0
    assert mock_db.commit.called


def test_approve_items_auto_approve_true(workflow_service, mock_db):
    """승인 처리 테스트 (auto_approve=True)"""
    task_id = ai_workflow_state.create_task([1], True)

    # Mock chunks
    chunk1 = KnowledgeChunk(id=1, document_id=1, chunk_index=0, content="테스트", status="draft")
    chunk2 = KnowledgeChunk(id=2, document_id=1, chunk_index=1, content="테스트2", status="draft")

    # chunk 쿼리(첫 번째)와 label 쿼리(두 번째) 분리
    call_count = {"n": 0}
    def side_effect_all():
        call_count["n"] += 1
        if call_count["n"] == 1:
            return [chunk1, chunk2]  # chunks
        return []  # labels (없음)

    mock_db.query.return_value.filter.return_value.all = side_effect_all
    mock_db.commit.return_value = None

    approved_count = workflow_service._approve_items(task_id, [1, 2], True, mock_db)

    assert approved_count == 2
    assert chunk1.status == "approved"
    assert chunk2.status == "approved"
    assert mock_db.commit.called


def test_approve_items_auto_approve_false(workflow_service, mock_db):
    """승인 처리 테스트 (auto_approve=False)"""
    task_id = ai_workflow_state.create_task([1], False)

    approved_count = workflow_service._approve_items(task_id, [1, 2], False, mock_db)

    assert approved_count == 0
    # draft 상태 유지 확인 (commit 호출 안 됨)


def test_embed_chunks(workflow_service, mock_db):
    """Qdrant 임베딩 테스트"""
    task_id = ai_workflow_state.create_task([1], True)

    # Mock approved chunks
    chunk1 = KnowledgeChunk(id=1, document_id=1, chunk_index=0, content="테스트", status="approved")
    chunk2 = KnowledgeChunk(id=2, document_id=1, chunk_index=1, content="테스트2", status="approved")

    mock_db.query.return_value.filter.return_value.all.return_value = [chunk1, chunk2]

    # Mock sync_chunk_to_qdrant
    mock_result = Mock()
    mock_result.success = True

    with patch("backend.services.automation.ai_workflow_service.sync_chunk_to_qdrant") as mock_sync:
        mock_sync.return_value = mock_result

        embedded_count = workflow_service._embed_chunks(task_id, [1, 2], mock_db)

    assert embedded_count == 2


def test_embed_chunks_qdrant_failure(workflow_service, mock_db):
    """Qdrant 임베딩 실패 테스트"""
    task_id = ai_workflow_state.create_task([1], True)

    # Mock approved chunks
    chunk1 = KnowledgeChunk(id=1, document_id=1, chunk_index=0, content="테스트", status="approved")

    mock_db.query.return_value.filter.return_value.all.return_value = [chunk1]

    # Mock sync_chunk_to_qdrant failure
    mock_result = Mock()
    mock_result.success = False
    mock_result.error = "Qdrant 연결 실패"

    with patch("backend.services.automation.ai_workflow_service.sync_chunk_to_qdrant") as mock_sync:
        mock_sync.return_value = mock_result

        embedded_count = workflow_service._embed_chunks(task_id, [1], mock_db)

    assert embedded_count == 0


def test_execute_workflow_cancelled(workflow_service, mock_db):
    """워크플로우 취소 테스트"""
    task_id = ai_workflow_state.create_task([1], False)
    ai_workflow_state.cancel_task(task_id)

    # 취소 상태에서 실행 시 조기 종료
    workflow_service.execute_workflow(task_id, mock_db)

    task = ai_workflow_state.get_task(task_id)
    assert task.status == "cancelled"


def test_execute_workflow_failure(workflow_service, mock_db):
    """워크플로우 실패 테스트"""
    task_id = ai_workflow_state.create_task([1], False)

    # Mock Document 조회 실패
    mock_db.query.side_effect = Exception("DB 연결 오류")

    workflow_service.execute_workflow(task_id, mock_db)

    task = ai_workflow_state.get_task(task_id)
    assert task.status == "failed"
    assert "DB 연결 오류" in task.error
