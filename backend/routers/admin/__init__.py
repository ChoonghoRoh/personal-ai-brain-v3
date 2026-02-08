"""Phase 11-2/11-3: Admin 설정 관리 API

Admin 설정 CRUD API 모듈:
- Task 11-2-1: Schema, Template, PromptPreset CRUD
- Task 11-2-2: RAG Profile, Policy Set CRUD
- Task 11-3: Audit Log 조회 API
"""
from fastapi import APIRouter

from . import schema_crud, template_crud, preset_crud, rag_profile_crud, policy_set_crud, audit_log_crud

router = APIRouter(prefix="/api/admin", tags=["admin"])

# 하위 라우터 포함
# Task 11-2-1
router.include_router(schema_crud.router, prefix="/schemas", tags=["admin-schemas"])
router.include_router(template_crud.router, prefix="/templates", tags=["admin-templates"])
router.include_router(preset_crud.router, prefix="/presets", tags=["admin-presets"])
# Task 11-2-2
router.include_router(rag_profile_crud.router, prefix="/rag-profiles", tags=["admin-rag-profiles"])
router.include_router(policy_set_crud.router, prefix="/policy-sets", tags=["admin-policy-sets"])
# Task 11-3
router.include_router(audit_log_crud.router, prefix="/audit-logs", tags=["admin-audit-logs"])
