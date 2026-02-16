"""Admin 설정 관리 테이블 모델

- Phase 11-1: schemas, templates, prompt_presets, rag_profiles, context_rules, policy_sets, audit_logs
- Phase 13-4: page_access_logs
"""
from sqlalchemy import (
    Column, String, Text, Integer, Boolean, DateTime, Numeric,
    ForeignKey, Index, text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, ARRAY, JSONB
from .database import Base


# ---------------------------------------------------------------------------
# Task 11-1-1: schemas, templates, prompt_presets
# ---------------------------------------------------------------------------

class AdminSchema(Base):
    """Role 스키마 정의 (schemas 테이블)"""
    __tablename__ = "schemas"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    role_key = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_required = Column(Boolean, default=False, server_default=text("false"))
    output_length_limit = Column(Integer, nullable=True)
    display_order = Column(Integer, default=0, server_default=text("0"))
    is_active = Column(Boolean, default=True, server_default=text("true"))
    created_at = Column(DateTime, server_default=text("NOW()"))
    updated_at = Column(DateTime, server_default=text("NOW()"))


class AdminTemplate(Base):
    """판단 문서 템플릿 (templates 테이블)"""
    __tablename__ = "templates"
    __table_args__ = (
        Index("idx_templates_status", "status"),
        Index("idx_templates_type", "template_type"),
    )

    id = Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    template_type = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    output_format = Column(String(20), default="markdown", server_default=text("'markdown'"))
    citation_rule = Column(Text, nullable=True)
    version = Column(Integer, default=1, server_default=text("1"))
    status = Column(String(20), default="draft", server_default=text("'draft'"))
    published_at = Column(DateTime, nullable=True)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=text("NOW()"))
    updated_at = Column(DateTime, server_default=text("NOW()"))


class AdminPromptPreset(Base):
    """프롬프트 프리셋 (prompt_presets 테이블)"""
    __tablename__ = "prompt_presets"
    __table_args__ = (
        Index("idx_prompt_presets_task", "task_type"),
        Index("idx_prompt_presets_status", "status"),
    )

    id = Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(String(200), nullable=False)
    task_type = Column(String(50), nullable=False)
    model_name = Column(String(50), nullable=True)
    temperature = Column(Numeric(3, 2), default=0.7, server_default=text("0.7"))
    top_p = Column(Numeric(3, 2), default=0.9, server_default=text("0.9"))
    max_tokens = Column(Integer, default=4000, server_default=text("4000"))
    system_prompt = Column(Text, nullable=False)
    constraints = Column(ARRAY(Text), nullable=True)
    version = Column(Integer, default=1, server_default=text("1"))
    status = Column(String(20), default="draft", server_default=text("'draft'"))
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=text("NOW()"))
    updated_at = Column(DateTime, server_default=text("NOW()"))


# ---------------------------------------------------------------------------
# Task 11-1-2: rag_profiles, context_rules, policy_sets
# ---------------------------------------------------------------------------

class AdminRagProfile(Base):
    """RAG 검색 파라미터 프로필 (rag_profiles 테이블)"""
    __tablename__ = "rag_profiles"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    chunk_size = Column(Integer, default=1000, server_default=text("1000"))
    chunk_overlap = Column(Integer, default=200, server_default=text("200"))
    top_k = Column(Integer, default=5, server_default=text("5"))
    score_threshold = Column(Numeric(3, 2), default=0.7, server_default=text("0.7"))
    use_rerank = Column(Boolean, default=False, server_default=text("false"))
    rerank_model = Column(String(50), nullable=True)
    filter_priority = Column(JSONB, nullable=True)
    version = Column(Integer, default=1, server_default=text("1"))
    status = Column(String(20), default="draft", server_default=text("'draft'"))
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=text("NOW()"))
    updated_at = Column(DateTime, server_default=text("NOW()"))


class AdminContextRule(Base):
    """상황 분류 규칙 (context_rules 테이블)"""
    __tablename__ = "context_rules"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    rule_name = Column(String(200), nullable=False)
    document_type = Column(String(50), nullable=True)
    domain_tags = Column(ARRAY(Text), nullable=True)
    classification_logic = Column(JSONB, nullable=True)
    allow_manual_override = Column(Boolean, default=True, server_default=text("true"))
    priority = Column(Integer, default=0, server_default=text("0"))
    is_active = Column(Boolean, default=True, server_default=text("true"))
    created_at = Column(DateTime, server_default=text("NOW()"))
    updated_at = Column(DateTime, server_default=text("NOW()"))


class AdminPolicySet(Base):
    """설정 적용 정책 (policy_sets 테이블)

    Note: project_id는 Integer FK (projects.id가 Integer PK이므로).
    master-plan-sample에서는 UUID FK로 정의되어 있으나, 실제 projects 테이블의 PK 타입에 맞춤.
    """
    __tablename__ = "policy_sets"
    __table_args__ = (
        Index("idx_policy_sets_project", "project_id"),
        Index("idx_policy_sets_active", "is_active"),
    )

    id = Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    user_group = Column(String(100), nullable=True)
    template_id = Column(PG_UUID(as_uuid=True), ForeignKey("templates.id"), nullable=True)
    prompt_preset_id = Column(PG_UUID(as_uuid=True), ForeignKey("prompt_presets.id"), nullable=True)
    rag_profile_id = Column(PG_UUID(as_uuid=True), ForeignKey("rag_profiles.id"), nullable=True)
    priority = Column(Integer, default=0, server_default=text("0"))
    is_active = Column(Boolean, default=True, server_default=text("true"))
    effective_from = Column(DateTime, server_default=text("NOW()"))
    effective_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=text("NOW()"))
    updated_at = Column(DateTime, server_default=text("NOW()"))


# ---------------------------------------------------------------------------
# Task 11-1-3: audit_logs
# ---------------------------------------------------------------------------

class AdminAuditLog(Base):
    """변경 이력 (audit_logs 테이블)"""
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("idx_audit_logs_table", "table_name", "record_id"),
        Index("idx_audit_logs_date", "created_at"),
    )

    id = Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    table_name = Column(String(50), nullable=False)
    record_id = Column(PG_UUID(as_uuid=True), nullable=False)
    action = Column(String(20), nullable=False)
    changed_by = Column(String(100), nullable=False)
    change_reason = Column(Text, nullable=True)
    old_values = Column(JSONB, nullable=True)
    new_values = Column(JSONB, nullable=True)
    created_at = Column(DateTime, server_default=text("NOW()"))


# ---------------------------------------------------------------------------
# Phase 13-4: page_access_logs
# ---------------------------------------------------------------------------

class PageAccessLog(Base):
    """페이지 접근 로그 (page_access_logs 테이블)

    HTML 페이지 요청만 기록 (API/정적 파일 제외).
    고빈도 INSERT 대상이므로 Integer PK 사용.
    """
    __tablename__ = "page_access_logs"
    __table_args__ = (
        Index("idx_page_access_logs_path", "path"),
        Index("idx_page_access_logs_date", "accessed_at"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    path = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False, server_default=text("'GET'"))
    status_code = Column(Integer, nullable=False)
    response_time_ms = Column(Integer, nullable=True)
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    accessed_at = Column(DateTime, server_default=text("NOW()"), nullable=False)
