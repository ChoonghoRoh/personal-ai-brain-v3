"""백업 및 복원 API 라우터

Phase 9-4-3: 백업/복원 시스템
- POST /api/system/backup - 백업 생성
- GET /api/system/backups - 백업 목록
- GET /api/system/backup/{name}/download - 백업 다운로드
- DELETE /api/system/backup/{name} - 백업 삭제
- POST /api/system/restore - 복원 실행
- GET /api/system/backup/status - 백업 상태
"""
import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from pydantic import BaseModel

from backend.models.database import get_db
from backend.config import PROJECT_ROOT

# BackupSystem import with fallback
try:
    from scripts.devtool.backup_system import BackupSystem
except ImportError:
    BackupSystem = None

router = APIRouter(prefix="/api/system/backup", tags=["Backup"])


class BackupRequest(BaseModel):
    """백업 생성 요청"""
    backup_type: str = "full"  # full, incremental
    incremental: bool = False
    description: Optional[str] = None
    include_uploads: bool = False


class RestoreRequest(BaseModel):
    """복원 요청"""
    backup_name: str
    confirm: bool = False
    components: Optional[List[str]] = None  # ["postgres", "qdrant", "metadata"]


def _get_backup_system():
    """BackupSystem 인스턴스 반환 (없으면 에러)"""
    if BackupSystem is None:
        raise HTTPException(
            status_code=503,
            detail="백업 시스템을 사용할 수 없습니다. scripts/devtool/backup_system.py를 확인하세요."
        )
    return BackupSystem()


@router.post("")
async def create_backup(
    request: BackupRequest,
    background_tasks: BackgroundTasks
):
    """
    백업 생성

    Args:
        backup_type: 백업 타입 (full/incremental)
        description: 백업 설명
        include_uploads: 업로드 파일 포함 여부

    Returns:
        백업 생성 시작 메시지
    """
    backup_system = _get_backup_system()

    def run_backup():
        result = backup_system.create_backup(
            backup_type=request.backup_type,
            incremental=request.incremental
        )
        # description 저장 (향후 확장)
        if request.description and result:
            result['description'] = request.description

    background_tasks.add_task(run_backup)

    return {
        "message": "백업이 시작되었습니다.",
        "backup_type": request.backup_type,
        "status": "in_progress"
    }


@router.get("s")
async def list_backups():
    """
    백업 목록 조회

    Returns:
        backups: 백업 목록
        total: 총 백업 수
        storage_used_mb: 총 사용 용량 (MB)
    """
    backup_system = _get_backup_system()
    backups = backup_system.list_backups()

    # 용량 계산
    total_size = sum(
        sum(f.get('size', 0) for f in b.get('files', []))
        for b in backups
    )

    return {
        "backups": backups,
        "total": len(backups),
        "storage_used_mb": round(total_size / (1024 * 1024), 2)
    }


@router.get("/{backup_name}/download")
async def download_backup(backup_name: str, file_type: str = "postgresql"):
    """
    백업 파일 다운로드

    Args:
        backup_name: 백업 이름
        file_type: 파일 타입 (postgresql, qdrant, metadata)

    Returns:
        백업 파일 (FileResponse)
    """
    backup_system = _get_backup_system()

    # 백업 정보 찾기
    backups = backup_system.list_backups()
    backup_info = None
    for b in backups:
        if b['name'] == backup_name:
            backup_info = b
            break

    if not backup_info:
        raise HTTPException(status_code=404, detail="백업을 찾을 수 없습니다")

    # 파일 찾기
    file_info = None
    for f in backup_info.get('files', []):
        if f['type'] == file_type:
            file_info = f
            break

    if not file_info:
        raise HTTPException(
            status_code=404,
            detail=f"해당 타입의 백업 파일이 없습니다: {file_type}"
        )

    backup_dir = PROJECT_ROOT / "backups"
    file_path = backup_dir / file_info['path']

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="백업 파일이 존재하지 않습니다")

    return FileResponse(
        path=str(file_path),
        filename=file_path.name,
        media_type='application/octet-stream'
    )


@router.get("/{backup_name}")
async def get_backup_detail(backup_name: str):
    """
    백업 상세 정보 조회

    Args:
        backup_name: 백업 이름

    Returns:
        백업 상세 정보
    """
    backup_system = _get_backup_system()

    backups = backup_system.list_backups()
    for backup in backups:
        if backup['name'] == backup_name:
            # 파일 크기를 MB로 변환
            for f in backup.get('files', []):
                f['size_mb'] = round(f.get('size', 0) / (1024 * 1024), 2)
            return backup

    raise HTTPException(status_code=404, detail="백업을 찾을 수 없습니다")


@router.delete("/{backup_name}")
async def delete_backup(backup_name: str):
    """
    백업 삭제

    Args:
        backup_name: 백업 이름
    """
    backup_system = _get_backup_system()

    if backup_system.delete_backup(backup_name):
        return {"message": f"백업이 삭제되었습니다: {backup_name}"}
    else:
        raise HTTPException(status_code=404, detail="백업을 찾을 수 없습니다")


@router.post("/restore")
async def restore_backup(
    request: RestoreRequest,
    background_tasks: BackgroundTasks
):
    """
    백업 복원 (비동기)

    Args:
        backup_name: 복원할 백업 이름
        confirm: 복원 확인 (true 필수)
        components: 복원할 구성요소 (없으면 전체)

    Returns:
        복원 시작 메시지
    """
    if not request.confirm:
        raise HTTPException(
            status_code=400,
            detail="복원을 수행하려면 confirm: true가 필요합니다. 기존 데이터가 덮어씌워집니다."
        )

    backup_system = _get_backup_system()

    # 백업 존재 확인
    backups = backup_system.list_backups()
    backup_exists = any(b['name'] == request.backup_name for b in backups)

    if not backup_exists:
        raise HTTPException(status_code=404, detail="백업을 찾을 수 없습니다")

    def run_restore():
        backup_system.restore_backup(request.backup_name)

    background_tasks.add_task(run_restore)

    return {
        "message": f"백업 복원이 시작되었습니다: {request.backup_name}",
        "backup_name": request.backup_name,
        "status": "in_progress"
    }


@router.get("/{backup_name}/verify")
async def verify_backup(backup_name: str):
    """
    백업 검증

    Args:
        backup_name: 검증할 백업 이름

    Returns:
        검증 결과
    """
    backup_system = _get_backup_system()
    is_valid = backup_system.verify_backup(backup_name)

    if not is_valid:
        raise HTTPException(status_code=400, detail="백업 검증 실패")

    return {"message": "백업 검증 성공", "valid": True, "backup_name": backup_name}


@router.get("/status/summary")
async def get_backup_status():
    """
    백업 상태 요약

    Returns:
        last_backup: 마지막 백업 시간
        total_backups: 총 백업 수
        total_size_mb: 총 용량 (MB)
    """
    backup_system = _get_backup_system()
    backups = backup_system.list_backups()

    if not backups:
        return {
            "last_backup": None,
            "total_backups": 0,
            "total_size_mb": 0,
            "last_backup_name": None
        }

    last_backup = max(backups, key=lambda x: x.get('timestamp', ''))
    total_size = sum(
        sum(f.get('size', 0) for f in b.get('files', []))
        for b in backups
    )

    return {
        "last_backup": last_backup.get('timestamp'),
        "total_backups": len(backups),
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "last_backup_name": last_backup.get('name')
    }


# ================== Legacy API (하위 호환성) ==================
# 기존 /api/backup/* 경로 지원을 위한 별칭

legacy_router = APIRouter(prefix="/api/backup", tags=["Backup"])


@legacy_router.post("/create")
async def legacy_create_backup(
    request: BackupRequest,
    background_tasks: BackgroundTasks
):
    """[Legacy] 백업 생성 - /api/system/backup 사용 권장"""
    return await create_backup(request, background_tasks)


@legacy_router.get("/list")
async def legacy_list_backups():
    """[Legacy] 백업 목록 - /api/system/backups 사용 권장"""
    return await list_backups()


@legacy_router.post("/restore/{backup_name}")
async def legacy_restore_backup(backup_name: str, background_tasks: BackgroundTasks):
    """[Legacy] 백업 복원 - /api/system/backup/restore 사용 권장"""
    request = RestoreRequest(backup_name=backup_name, confirm=True)
    return await restore_backup(request, background_tasks)


@legacy_router.get("/status")
async def legacy_get_status():
    """[Legacy] 백업 상태 - /api/system/backup/status/summary 사용 권장"""
    return await get_backup_status()
