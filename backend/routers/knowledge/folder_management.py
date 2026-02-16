"""지식관리 폴더 경로 설정 API (Phase 15-1)

GET   /api/knowledge/folder-config  폴더 경로 조회
PUT   /api/knowledge/folder-config  폴더 경로 설정
GET   /api/knowledge/folder-files   폴더 내 파일 목록 조회 (Phase 15-1-2)
POST  /api/knowledge/upload         파일 업로드 (Phase 15-1-3)
POST  /api/knowledge/sync           폴더 전체 동기화 (Phase 15-1-3)
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.models.database import get_db
from backend.middleware.auth import require_admin_knowledge, UserInfo
from backend.services.knowledge.folder_service import (
    get_folder_path,
    set_folder_path,
    scan_folder_files,
    save_uploaded_file,
    sync_folder_to_db,
    FileInfo,
)
from backend.config import get_env_int


router = APIRouter(prefix="/api/knowledge", tags=["Knowledge - Folder Management"])

# 파일 크기 제한 (기본 50MB)
MAX_FILE_SIZE_MB = get_env_int("MAX_FILE_SIZE_MB", 50)
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


class FolderConfigResponse(BaseModel):
    """폴더 경로 조회 응답"""
    folder_path: str = Field(..., description="폴더 경로 (절대 경로 또는 상대 경로)")
    source: str = Field(..., description="설정 출처 (env: 환경변수, db: DB 설정)")

    class Config:
        json_schema_extra = {
            "example": {
                "folder_path": "brain/knowledge",
                "source": "env"
            }
        }


class FolderConfigUpdateRequest(BaseModel):
    """폴더 경로 설정 요청"""
    folder_path: str = Field(..., min_length=1, description="설정할 폴더 경로")

    class Config:
        json_schema_extra = {
            "example": {
                "folder_path": "brain/knowledge"
            }
        }


@router.get(
    "/folder-config",
    response_model=FolderConfigResponse,
    summary="지식관리 폴더 경로 조회",
    description="""
    지식관리 전용 폴더 경로를 조회합니다.

    **설정 우선순위**:
    1. DB 설정값 (source: "db")
    2. 환경변수 KNOWLEDGE_FOLDER_PATH (source: "env")
    3. 기본값: "brain/knowledge"

    **권한**: admin_knowledge 이상
    """,
    dependencies=[Depends(require_admin_knowledge)]
)
async def get_folder_config(
    db: Session = Depends(get_db),
    user: UserInfo = Depends(require_admin_knowledge)
):
    """지식관리 폴더 경로 조회"""
    folder_path, source = get_folder_path(db)
    return FolderConfigResponse(folder_path=folder_path, source=source)


@router.put(
    "/folder-config",
    response_model=FolderConfigResponse,
    summary="지식관리 폴더 경로 설정",
    description="""
    지식관리 전용 폴더 경로를 설정합니다.

    **동작**:
    - 폴더가 존재하지 않으면 자동 생성
    - DB에 설정값을 저장 (환경변수보다 우선)
    - 상대 경로인 경우 PROJECT_ROOT 기준

    **권한**: admin_knowledge 이상

    **예시**:
    ```json
    {
      "folder_path": "brain/knowledge"
    }
    ```
    """,
    dependencies=[Depends(require_admin_knowledge)]
)
async def update_folder_config(
    request: FolderConfigUpdateRequest,
    db: Session = Depends(get_db),
    user: UserInfo = Depends(require_admin_knowledge)
):
    """지식관리 폴더 경로 설정"""
    try:
        folder_path = set_folder_path(db, request.folder_path)
        return FolderConfigResponse(folder_path=folder_path, source="db")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except OSError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"폴더 생성 실패: {str(e)}"
        )


# ============================================
# Phase 15-1-2: 폴더 내 파일 목록 조회
# ============================================

class FileItemResponse(BaseModel):
    """파일 정보 응답"""
    file_name: str = Field(..., description="파일명")
    file_path: str = Field(..., description="절대 경로")
    relative_path: str = Field(..., description="폴더 기준 상대 경로")
    size: int = Field(..., description="파일 크기 (bytes)")
    updated_at: datetime = Field(..., description="파일 수정 시간")
    document_id: Optional[int] = Field(None, description="DB 문서 ID (없으면 null)")
    chunk_count: int = Field(0, description="청크 개수")
    status: str = Field(..., description="상태 (synced: 동기화됨, unsynced: 변경됨, new: 미등록)")

    class Config:
        json_schema_extra = {
            "example": {
                "file_name": "example.md",
                "file_path": "/path/to/brain/knowledge/example.md",
                "relative_path": "example.md",
                "size": 1024,
                "updated_at": "2026-02-16T10:00:00",
                "document_id": 123,
                "chunk_count": 5,
                "status": "synced"
            }
        }


class FolderFilesResponse(BaseModel):
    """폴더 파일 목록 응답"""
    items: List[FileItemResponse] = Field(..., description="파일 목록")
    total_count: int = Field(..., description="전체 파일 개수")
    limit: int = Field(..., description="페이지 크기")
    offset: int = Field(..., description="시작 위치")


@router.get(
    "/folder-files",
    response_model=FolderFilesResponse,
    summary="폴더 내 파일 목록 조회",
    description="""
    지정 폴더의 파일을 재귀 스캔하고 DB와 매칭하여 상태 정보를 반환합니다.

    **동작**:
    - 지정 폴더 내 파일 재귀 스캔 (기본 depth: 3)
    - 허용 확장자: .md, .txt, .pdf, .docx, .hwp, .hwpx, .xlsx, .pptx
    - documents 테이블과 file_path 매칭
    - 파일 상태 판정:
      - **synced**: DB에 등록되고 최신 상태
      - **unsynced**: DB에 등록되었으나 파일이 변경됨
      - **new**: DB에 미등록

    **페이징**: `limit`, `offset` 쿼리 파라미터

    **권한**: admin_knowledge 이상
    """,
    dependencies=[Depends(require_admin_knowledge)]
)
async def get_folder_files(
    max_depth: int = Query(3, ge=1, le=10, description="최대 재귀 깊이"),
    limit: int = Query(100, ge=1, le=1000, description="페이지 크기"),
    offset: int = Query(0, ge=0, description="시작 위치"),
    db: Session = Depends(get_db),
    user: UserInfo = Depends(require_admin_knowledge)
):
    """폴더 내 파일 목록 조회 (DB 매칭 포함)"""
    # 파일 스캔
    file_infos = scan_folder_files(db, max_depth=max_depth)

    # 전체 개수
    total_count = len(file_infos)

    # 페이징
    paginated_files = file_infos[offset:offset + limit]

    # 응답 변환
    items = [
        FileItemResponse(
            file_name=f.file_name,
            file_path=f.file_path,
            relative_path=f.relative_path,
            size=f.size,
            updated_at=f.updated_at,
            document_id=f.document_id,
            chunk_count=f.chunk_count,
            status=f.status
        )
        for f in paginated_files
    ]

    return FolderFilesResponse(
        items=items,
        total_count=total_count,
        limit=limit,
        offset=offset
    )


# ============================================
# Phase 15-1-3: 파일 업로드 및 동기화
# ============================================

class UploadResponse(BaseModel):
    """파일 업로드 응답"""
    success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="메시지")
    document_id: int = Field(..., description="생성된 문서 ID")
    file_path: str = Field(..., description="저장된 파일 경로")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "파일이 업로드되었습니다",
                "document_id": 123,
                "file_path": "/path/to/brain/knowledge/example.md"
            }
        }


class SyncResponse(BaseModel):
    """동기화 응답"""
    success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="메시지")
    added_count: int = Field(..., description="추가된 파일 개수")
    missing_count: int = Field(..., description="폴더에 없는 문서 개수")
    unchanged_count: int = Field(..., description="변경 없는 파일 개수")
    added_files: List[str] = Field(..., description="추가된 파일 목록 (상대 경로)")
    missing_files: List[str] = Field(..., description="폴더에 없는 문서 목록 (절대 경로)")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "동기화가 완료되었습니다",
                "added_count": 3,
                "missing_count": 1,
                "unchanged_count": 10,
                "added_files": ["new_file1.md", "subfolder/new_file2.md"],
                "missing_files": ["/path/to/deleted_file.md"]
            }
        }


@router.post(
    "/upload",
    response_model=UploadResponse,
    summary="파일 업로드",
    description=f"""
    지정 폴더로 파일을 업로드하고 documents 테이블에 등록합니다.

    **동작**:
    - 파일을 지정 폴더에 저장
    - documents 테이블에 레코드 생성
    - 허용 확장자 검증
    - 중복 file_path 시 409 Conflict

    **제한**:
    - 최대 파일 크기: {MAX_FILE_SIZE_MB}MB
    - 허용 확장자: .md, .txt, .pdf, .docx, .hwp, .hwpx, .xlsx, .pptx

    **권한**: admin_knowledge 이상
    """,
    dependencies=[Depends(require_admin_knowledge)]
)
async def upload_file(
    file: UploadFile = File(..., description="업로드할 파일"),
    relative_path: Optional[str] = Query(None, description="저장할 상대 경로 (지정 시 subfolder에 저장)"),
    db: Session = Depends(get_db),
    user: UserInfo = Depends(require_admin_knowledge)
):
    """파일 업로드 및 DB 등록"""
    # 파일 크기 검증
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"파일 크기가 {MAX_FILE_SIZE_MB}MB를 초과합니다"
        )

    try:
        document = save_uploaded_file(
            db=db,
            file_name=file.filename,
            file_content=file_content,
            relative_path=relative_path
        )

        return UploadResponse(
            success=True,
            message="파일이 업로드되었습니다",
            document_id=document.id,
            file_path=document.file_path
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except FileExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"파일 업로드 실패: {str(e)}"
        )


@router.post(
    "/sync",
    response_model=SyncResponse,
    summary="폴더 전체 동기화",
    description="""
    지정 폴더를 스캔하여 DB와 동기화합니다.

    **동작**:
    - 폴더에 있으나 DB에 없는 파일 → documents에 추가
    - DB에 있으나 폴더에 없는 파일 → 감지하여 응답에 포함
    - delete_missing=true 시 폴더에 없는 문서를 DB에서 삭제

    **권한**: admin_knowledge 이상
    """,
    dependencies=[Depends(require_admin_knowledge)]
)
async def sync_folder(
    max_depth: int = Query(3, ge=1, le=10, description="최대 재귀 깊이"),
    delete_missing: bool = Query(False, description="폴더에 없는 문서를 DB에서 삭제"),
    db: Session = Depends(get_db),
    user: UserInfo = Depends(require_admin_knowledge)
):
    """폴더 전체 동기화"""
    try:
        result = sync_folder_to_db(
            db=db,
            max_depth=max_depth,
            delete_missing=delete_missing
        )

        return SyncResponse(
            success=True,
            message="동기화가 완료되었습니다",
            added_count=result.added_count,
            missing_count=result.missing_count,
            unchanged_count=result.unchanged_count,
            added_files=result.added_files,
            missing_files=result.missing_files
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"동기화 실패: {str(e)}"
        )
