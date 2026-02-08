"""Database models for knowledge management"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Project(Base):
    """Project model"""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    path = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")


class Document(Base):
    """Document model"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)  # 인덱스 추가
    file_path = Column(String, unique=True, index=True, nullable=False)
    file_name = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # md, pdf, docx
    size = Column(Integer, nullable=False)
    qdrant_collection = Column(String, nullable=True)
    category_label_id = Column(Integer, ForeignKey("labels.id"), nullable=True, index=True)  # Phase 7.7: 카테고리/프로젝트/도메인 라벨
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="documents")
    chunks = relationship("KnowledgeChunk", back_populates="document", cascade="all, delete-orphan")
    category_label = relationship("Label", foreign_keys=[category_label_id])  # Phase 7.7: 카테고리 라벨 관계


class KnowledgeChunk(Base):
    """Knowledge chunk model"""
    __tablename__ = "knowledge_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)  # 인덱스 추가
    chunk_index = Column(Integer, nullable=False, index=True)  # 인덱스 추가
    content = Column(Text, nullable=False)
    qdrant_point_id = Column(String, nullable=True, index=True)  # Qdrant point ID, 인덱스 추가
    embedding_model = Column(String, nullable=True)
    
    # Phase 7 Upgrade: Approval workflow
    status = Column(String, default="draft", nullable=False, index=True)  # draft, approved, rejected
    source = Column(String, default="human_created", nullable=False)  # ai_generated, human_created
    approved_at = Column(DateTime, nullable=True)
    approved_by = Column(String, nullable=True)  # User identifier
    version = Column(Integer, default=1, nullable=False)
    
    # Phase 7.9.5: Title field
    title = Column(String, nullable=True)  # Chunk title extracted from heading or AI
    title_source = Column(String, nullable=True)  # "heading" | "ai_extracted" | "manual" | null
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="chunks")
    labels = relationship("KnowledgeLabel", back_populates="chunk", cascade="all, delete-orphan")


class Label(Base):
    """Label model"""
    __tablename__ = "labels"
    __table_args__ = (
        # Phase 7.7: (name, label_type) 복합 unique 제약조건
        # 같은 이름의 라벨이 다른 label_type으로 존재할 수 있도록
        UniqueConstraint('name', 'label_type', name='labels_name_label_type_unique'),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)  # unique 제거, 복합 unique로 대체
    label_type = Column(String, nullable=False, index=True)  # keyword, keyword_group, category, project, domain, project_phase, role, domain, importance
    parent_label_id = Column(Integer, ForeignKey("labels.id"), nullable=True, index=True)  # Phase 7.7: 계층 구조
    description = Column(Text, nullable=True)
    color = Column(String, nullable=True)  # Phase 7.7: UI용 색상 정보
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Phase 7.7: 업데이트 시간

    # Relationships
    knowledge_labels = relationship("KnowledgeLabel", back_populates="label")
    parent_label = relationship("Label", remote_side=[id], backref="child_labels")  # Phase 7.7: 자기 참조 관계


class KnowledgeLabel(Base):
    """Knowledge chunk label relationship"""
    __tablename__ = "knowledge_labels"

    id = Column(Integer, primary_key=True, index=True)
    chunk_id = Column(Integer, ForeignKey("knowledge_chunks.id"), nullable=False, index=True)  # 인덱스 추가
    label_id = Column(Integer, ForeignKey("labels.id"), nullable=False, index=True)  # 인덱스 추가
    confidence = Column(Float, default=1.0)
    
    # Phase 7 Upgrade: AI suggestion workflow
    status = Column(String, default="confirmed", nullable=False, index=True)  # suggested, confirmed, rejected
    source = Column(String, default="human", nullable=False)  # ai, human
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    chunk = relationship("KnowledgeChunk", back_populates="labels")
    label = relationship("Label", back_populates="knowledge_labels")


class KnowledgeRelation(Base):
    """Knowledge chunk relation model"""
    __tablename__ = "knowledge_relations"

    id = Column(Integer, primary_key=True, index=True)
    source_chunk_id = Column(Integer, ForeignKey("knowledge_chunks.id"), nullable=False, index=True)  # 인덱스 추가
    target_chunk_id = Column(Integer, ForeignKey("knowledge_chunks.id"), nullable=False, index=True)  # 인덱스 추가
    relation_type = Column(String, nullable=False, index=True)  # 인덱스 추가
    confidence = Column(Float, default=1.0)
    description = Column(Text, nullable=True)
    
    # Phase 7 Upgrade: AI suggestion workflow
    score = Column(Float, nullable=True)  # Similarity score for AI suggestions
    confirmed = Column(String, default="true", nullable=False)  # true, false (for suggested relations)
    source = Column(String, default="human", nullable=False)  # ai, human
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    source_chunk = relationship("KnowledgeChunk", foreign_keys=[source_chunk_id], backref="outgoing_relations")
    target_chunk = relationship("KnowledgeChunk", foreign_keys=[target_chunk_id], backref="incoming_relations")


class Memory(Base):
    """기억 시스템 모델 (Phase 8.0.5)"""
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)
    memory_type = Column(String, nullable=False, index=True)  # long_term, short_term, working
    content = Column(Text, nullable=False)
    importance_score = Column(Float, default=0.5, nullable=False)  # 0.0 - 1.0
    category = Column(String, nullable=True, index=True)  # principle, value, knowledge, conversation, context
    related_chunk_id = Column(Integer, ForeignKey("knowledge_chunks.id"), nullable=True, index=True)
    meta_data = Column(Text, nullable=True)  # JSON string for additional data (metadata는 SQLAlchemy 예약어)
    
    # Phase 8.0.5: 기억 관리
    access_count = Column(Integer, default=0, nullable=False)  # 접근 횟수
    last_accessed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)  # 단기 기억 만료 시간
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    related_chunk = relationship("KnowledgeChunk", foreign_keys=[related_chunk_id])


class Conversation(Base):
    """대화 기록 모델 (Phase 8.0.13)"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    sources = Column(Text, nullable=True)  # JSON string for sources
    model_used = Column(String, nullable=True)  # 사용된 모델 정보
    session_id = Column(String, nullable=True, index=True)  # 세션 ID
    meta_data = Column(Text, nullable=True)  # JSON string for additional data (metadata는 SQLAlchemy 예약어)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class ReasoningResult(Base):
    """Reasoning 결과 모델 (Phase 8.0.15-4, 10-4-2/3 확장)"""
    __tablename__ = "reasoning_results"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    reasoning_steps = Column(Text, nullable=True)  # JSON string for reasoning steps
    context_chunks = Column(Text, nullable=True)  # JSON string for context chunks
    relations = Column(Text, nullable=True)  # JSON string for relations
    mode = Column(String, nullable=True)  # reasoning mode
    session_id = Column(String, nullable=True, index=True)  # 세션 ID
    meta_data = Column(Text, nullable=True)  # JSON string for additional data (metadata는 SQLAlchemy 예약어)

    # Phase 10-4-2: 결과 공유
    share_id = Column(String, unique=True, nullable=True, index=True)
    recommendations = Column(Text, nullable=True)  # JSON string for recommendations snapshot
    # 11-5-6: 공유 URL 고도화
    expires_at = Column(DateTime, nullable=True, index=True)  # 만료 시각 (None이면 무제한)
    view_count = Column(Integer, default=0, nullable=False)  # 조회 횟수
    is_private = Column(Integer, default=0, nullable=False)  # 0=공개, 1=비공개 (SQLite 호환)

    # Phase 10-4-3: 의사결정 문서
    title = Column(String, nullable=True)
    summary = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

