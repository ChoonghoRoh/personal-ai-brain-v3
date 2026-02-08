"""데이터베이스 모델 테스트"""
import pytest
from datetime import datetime
from backend.models.models import KnowledgeChunk, Document, Project, Memory


def test_project_model(db_session):
    """프로젝트 모델 테스트"""
    project = Project(
        name="Test Project",
        path="/test/path"
    )
    db_session.add(project)
    db_session.commit()
    
    assert project.id is not None
    assert project.name == "Test Project"


def test_document_model(db_session):
    """문서 모델 테스트"""
    project = Project(name="Test Project", path="/test")
    db_session.add(project)
    db_session.commit()
    
    document = Document(
        file_path="/test/doc.md",
        file_name="doc.md",
        file_type="md",
        size=0,
        project_id=project.id
    )
    db_session.add(document)
    db_session.commit()
    
    assert document.id is not None
    assert document.project_id == project.id


def test_memory_model(db_session):
    """기억 모델 테스트"""
    memory = Memory(
        memory_type="long_term",
        content="Test memory",
        importance_score=0.8
    )
    db_session.add(memory)
    db_session.commit()
    
    assert memory.id is not None
    assert memory.memory_type == "long_term"
    assert memory.importance_score == 0.8
