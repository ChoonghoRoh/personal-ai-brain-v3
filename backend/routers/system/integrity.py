"""데이터 무결성 API 라우터"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict

from backend.models.database import get_db
from backend.services.system.integrity_service import get_integrity_service

router = APIRouter(prefix="/api/integrity", tags=["Integrity"])


@router.get("/check")
async def check_integrity(db: Session = Depends(get_db)):
    """데이터 무결성 확인"""
    service = get_integrity_service()
    result = service.validate_all(db)
    
    return result


@router.get("/sync")
async def check_sync(db: Session = Depends(get_db)):
    """Qdrant-PostgreSQL 동기화 확인"""
    service = get_integrity_service()
    result = service.check_qdrant_postgresql_sync(db)
    
    return result


@router.get("/consistency")
async def check_consistency(db: Session = Depends(get_db)):
    """데이터 일관성 확인"""
    service = get_integrity_service()
    result = service.check_data_consistency(db)
    
    return result


@router.post("/fix/orphan-chunks")
async def fix_orphan_chunks(db: Session = Depends(get_db)):
    """고아 청크 수정"""
    service = get_integrity_service()
    count = service.fix_orphan_chunks(db)
    
    return {"message": f"{count}개의 고아 청크가 삭제되었습니다.", "fixed_count": count}


@router.post("/fix/orphan-labels")
async def fix_orphan_labels(db: Session = Depends(get_db)):
    """고아 라벨 관계 수정"""
    service = get_integrity_service()
    count = service.fix_orphan_labels(db)
    
    return {"message": f"{count}개의 고아 라벨 관계가 삭제되었습니다.", "fixed_count": count}


@router.post("/fix/orphan-relations")
async def fix_orphan_relations(db: Session = Depends(get_db)):
    """고아 관계 수정"""
    service = get_integrity_service()
    count = service.fix_orphan_relations(db)
    
    return {"message": f"{count}개의 고아 관계가 삭제되었습니다.", "fixed_count": count}
