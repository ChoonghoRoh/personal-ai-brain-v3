"""Phase 11-2: Admin CRUD 공통 Pydantic 스키마

공통 CRUD 모듈:
1. 목록 조회 쿼리 (필터·페이징)
2. 공통 응답 래퍼 (목록/단건)
3. 리소스별 Request/Response 스키마
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Generic, TypeVar, Any
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer, ConfigDict


# =============================================================================
# 공통 스키마
# =============================================================================

T = TypeVar("T")


class PaginationParams(BaseModel):
    """목록 조회 페이징 파라미터"""
    limit: int = Field(default=20, ge=1, le=100, description="페이지당 항목 수 (1-100)")
    offset: int = Field(default=0, ge=0, description="시작 위치")


class ListResponse(BaseModel, Generic[T]):
    """목록 응답 래퍼"""
    items: List[T]
    total: int
    limit: int
    offset: int


class MessageResponse(BaseModel):
    """단순 메시지 응답"""
    message: str
    id: Optional[UUID] = None


# =============================================================================
# Schema (AdminSchema) 스키마
# =============================================================================

class SchemaBase(BaseModel):
    """Schema 기본 필드"""
    role_key: str = Field(..., min_length=1, max_length=50, description="역할 키 (unique)")
    display_name: str = Field(..., min_length=1, max_length=100, description="표시 이름")
    description: Optional[str] = Field(None, description="설명")
    is_required: bool = Field(default=False, description="필수 여부")
    output_length_limit: Optional[int] = Field(None, ge=0, description="출력 길이 제한")
    display_order: int = Field(default=0, description="표시 순서")
    is_active: bool = Field(default=True, description="활성 여부")


class SchemaCreate(SchemaBase):
    """Schema 생성 요청"""
    pass


class SchemaUpdate(BaseModel):
    """Schema 수정 요청 (부분 업데이트)"""
    role_key: Optional[str] = Field(None, min_length=1, max_length=50)
    display_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_required: Optional[bool] = None
    output_length_limit: Optional[int] = Field(None, ge=0)
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class SchemaResponse(SchemaBase):
    """Schema 응답"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, dt: Optional[datetime], _info) -> Optional[str]:
        return dt.isoformat() if dt else None


# =============================================================================
# Template (AdminTemplate) 스키마
# =============================================================================

class TemplateBase(BaseModel):
    """Template 기본 필드"""
    name: str = Field(..., min_length=1, max_length=200, description="템플릿 이름")
    description: Optional[str] = Field(None, description="설명")
    template_type: str = Field(..., min_length=1, max_length=50, description="템플릿 타입")
    content: str = Field(..., min_length=1, description="템플릿 내용")
    output_format: str = Field(default="markdown", max_length=20, description="출력 포맷")
    citation_rule: Optional[str] = Field(None, description="인용 규칙")
    created_by: Optional[str] = Field(None, max_length=100, description="작성자")


class TemplateCreate(TemplateBase):
    """Template 생성 요청"""
    pass


class TemplateUpdate(BaseModel):
    """Template 수정 요청 (부분 업데이트)"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    template_type: Optional[str] = Field(None, min_length=1, max_length=50)
    content: Optional[str] = Field(None, min_length=1)
    output_format: Optional[str] = Field(None, max_length=20)
    citation_rule: Optional[str] = None
    status: Optional[str] = Field(None, max_length=20)
    created_by: Optional[str] = Field(None, max_length=100)


class TemplateResponse(TemplateBase):
    """Template 응답"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    version: int
    status: str
    published_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_serializer("published_at", "created_at", "updated_at")
    def serialize_datetime(self, dt: Optional[datetime], _info) -> Optional[str]:
        return dt.isoformat() if dt else None


# =============================================================================
# PromptPreset (AdminPromptPreset) 스키마
# =============================================================================

class PresetBase(BaseModel):
    """PromptPreset 기본 필드"""
    name: str = Field(..., min_length=1, max_length=200, description="프리셋 이름")
    task_type: str = Field(..., min_length=1, max_length=50, description="작업 타입")
    model_name: Optional[str] = Field(None, max_length=50, description="모델 이름")
    temperature: Decimal = Field(default=Decimal("0.7"), ge=0, le=2, description="Temperature")
    top_p: Decimal = Field(default=Decimal("0.9"), ge=0, le=1, description="Top-P")
    max_tokens: int = Field(default=4000, ge=1, description="최대 토큰")
    system_prompt: str = Field(..., min_length=1, description="시스템 프롬프트")
    constraints: Optional[List[str]] = Field(None, description="제약 조건 목록")


class PresetCreate(PresetBase):
    """PromptPreset 생성 요청"""
    pass


class PresetUpdate(BaseModel):
    """PromptPreset 수정 요청 (부분 업데이트)"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    task_type: Optional[str] = Field(None, min_length=1, max_length=50)
    model_name: Optional[str] = Field(None, max_length=50)
    temperature: Optional[Decimal] = Field(None, ge=0, le=2)
    top_p: Optional[Decimal] = Field(None, ge=0, le=1)
    max_tokens: Optional[int] = Field(None, ge=1)
    system_prompt: Optional[str] = Field(None, min_length=1)
    constraints: Optional[List[str]] = None
    status: Optional[str] = Field(None, max_length=20)


class PresetResponse(PresetBase):
    """PromptPreset 응답"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    version: int
    status: str
    published_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_serializer("temperature", "top_p")
    def serialize_decimal(self, v: Optional[Decimal], _info) -> Optional[float]:
        return float(v) if v is not None else None

    @field_serializer("published_at", "created_at", "updated_at")
    def serialize_datetime(self, dt: Optional[datetime], _info) -> Optional[str]:
        return dt.isoformat() if dt else None


# =============================================================================
# RAG Profile (AdminRagProfile) 스키마
# =============================================================================

class RagProfileBase(BaseModel):
    """RAG Profile 기본 필드"""
    name: str = Field(..., min_length=1, max_length=200, description="프로필 이름")
    description: Optional[str] = Field(None, description="설명")
    chunk_size: int = Field(default=1000, ge=100, le=10000, description="청크 크기")
    chunk_overlap: int = Field(default=200, ge=0, le=1000, description="청크 오버랩")
    top_k: int = Field(default=5, ge=1, le=50, description="검색 결과 개수")
    score_threshold: Decimal = Field(default=Decimal("0.7"), ge=0, le=1, description="점수 임계값")
    use_rerank: bool = Field(default=False, description="Rerank 사용 여부")
    rerank_model: Optional[str] = Field(None, max_length=50, description="Rerank 모델")
    filter_priority: Optional[dict] = Field(None, description="필터 우선순위 (JSON)")


class RagProfileCreate(RagProfileBase):
    """RAG Profile 생성 요청"""
    pass


class RagProfileUpdate(BaseModel):
    """RAG Profile 수정 요청 (부분 업데이트)"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    chunk_size: Optional[int] = Field(None, ge=100, le=10000)
    chunk_overlap: Optional[int] = Field(None, ge=0, le=1000)
    top_k: Optional[int] = Field(None, ge=1, le=50)
    score_threshold: Optional[Decimal] = Field(None, ge=0, le=1)
    use_rerank: Optional[bool] = None
    rerank_model: Optional[str] = Field(None, max_length=50)
    filter_priority: Optional[dict] = None
    status: Optional[str] = Field(None, max_length=20)


class RagProfileResponse(RagProfileBase):
    """RAG Profile 응답"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    version: int
    status: str
    published_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_serializer("score_threshold")
    def serialize_decimal(self, v: Optional[Decimal], _info) -> Optional[float]:
        return float(v) if v is not None else None

    @field_serializer("published_at", "created_at", "updated_at")
    def serialize_datetime(self, dt: Optional[datetime], _info) -> Optional[str]:
        return dt.isoformat() if dt else None


# =============================================================================
# Policy Set (AdminPolicySet) 스키마
# =============================================================================

class PolicySetBase(BaseModel):
    """Policy Set 기본 필드"""
    name: str = Field(..., min_length=1, max_length=200, description="정책 이름")
    description: Optional[str] = Field(None, description="설명")
    project_id: Optional[int] = Field(None, description="프로젝트 ID (FK)")
    user_group: Optional[str] = Field(None, max_length=100, description="사용자 그룹")
    template_id: Optional[UUID] = Field(None, description="템플릿 ID (FK)")
    prompt_preset_id: Optional[UUID] = Field(None, description="프롬프트 프리셋 ID (FK)")
    rag_profile_id: Optional[UUID] = Field(None, description="RAG 프로필 ID (FK)")
    priority: int = Field(default=0, description="우선순위")
    is_active: bool = Field(default=True, description="활성 여부")
    effective_from: Optional[datetime] = Field(None, description="적용 시작일")
    effective_until: Optional[datetime] = Field(None, description="적용 종료일")


class PolicySetCreate(PolicySetBase):
    """Policy Set 생성 요청"""
    pass


class PolicySetUpdate(BaseModel):
    """Policy Set 수정 요청 (부분 업데이트)"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    project_id: Optional[int] = None
    user_group: Optional[str] = Field(None, max_length=100)
    template_id: Optional[UUID] = None
    prompt_preset_id: Optional[UUID] = None
    rag_profile_id: Optional[UUID] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None
    effective_from: Optional[datetime] = None
    effective_until: Optional[datetime] = None


class PolicySetResponse(PolicySetBase):
    """Policy Set 응답"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_serializer("effective_from", "effective_until", "created_at", "updated_at")
    def serialize_datetime(self, dt: Optional[datetime], _info) -> Optional[str]:
        return dt.isoformat() if dt else None


# =============================================================================
# Audit Log (AdminAuditLog) 스키마 - Phase 11-3
# =============================================================================

class AuditLogResponse(BaseModel):
    """Audit Log 응답"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    table_name: str
    record_id: UUID
    action: str
    changed_by: Optional[str] = None
    change_reason: Optional[str] = None
    old_values: Optional[dict] = None
    new_values: Optional[dict] = None
    created_at: Optional[datetime] = None

    @field_serializer("created_at")
    def serialize_datetime(self, dt: Optional[datetime], _info) -> Optional[str]:
        return dt.isoformat() if dt else None
