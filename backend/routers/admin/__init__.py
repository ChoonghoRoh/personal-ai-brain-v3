"""Admin 설정 관리 API

Admin 설정 CRUD API 모듈:
- Task 11-2-1: Schema, Template, PromptPreset CRUD
- Task 11-2-2: RAG Profile, Policy Set CRUD
- Task 11-3: Audit Log 조회 API
- Task 13-4: Page Access Log 조회 API
- Phase 14-1: 역할 기반 권한 검증 (require_admin_system)
"""
from fastapi import APIRouter, Depends

from backend.middleware.auth import require_admin_system

from . import schema_crud, template_crud, preset_crud, rag_profile_crud, policy_set_crud, audit_log_crud
from . import page_access_log_crud  # Phase 13-4
from . import user_crud  # Phase 14-5-3

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"],
    dependencies=[Depends(require_admin_system)],
)

# 하위 라우터 포함
# Task 11-2-1
router.include_router(schema_crud.router, prefix="/schemas", tags=["Admin - Schemas"])
router.include_router(template_crud.router, prefix="/templates", tags=["Admin - Templates"])
router.include_router(preset_crud.router, prefix="/presets", tags=["Admin - Presets"])
# Task 11-2-2
router.include_router(rag_profile_crud.router, prefix="/rag-profiles", tags=["Admin - RAG Profiles"])
router.include_router(policy_set_crud.router, prefix="/policy-sets", tags=["Admin - Policy Sets"])
# Task 11-3
router.include_router(audit_log_crud.router, prefix="/audit-logs", tags=["Admin - Audit Logs"])
# Phase 13-4
router.include_router(page_access_log_crud.router, prefix="/page-access-logs", tags=["Admin - Page Access Logs"])
# Phase 14-5-3
router.include_router(user_crud.router, prefix="/users", tags=["Admin - Users"])
