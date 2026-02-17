"""지식관리 폴더 경로 설정 서비스 (Phase 15-1)

환경변수 기본값 + DB 오버라이드 방식으로 폴더 경로 관리.
Phase 15-1-2: 폴더 내 파일 목록 스캔 기능 추가
Phase 15-9: 디렉토리 탐색 API (트리뷰용)
"""
import os
from pathlib import Path
from typing import Optional, Literal, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.config import KNOWLEDGE_FOLDER_PATH, PROJECT_ROOT
from backend.models.admin_models import AdminSystemSetting
from backend.models.models import Document, KnowledgeChunk


SETTING_KEY_FOLDER_PATH = "knowledge.folder_path"

# 지원 파일 확장자 (Phase 15-1-2)
ALLOWED_EXTENSIONS = {
    '.md', '.txt', '.pdf', '.docx', '.hwp', '.hwpx',
    '.xlsx', '.xls', '.pptx', '.ppt'
}


def get_folder_path(db: Session) -> tuple[str, Literal["env", "db"]]:
    """
    지식관리 폴더 경로 조회.

    Args:
        db: DB 세션

    Returns:
        (folder_path, source) 튜플
        - folder_path: 폴더 경로 (절대 경로 또는 상대 경로)
        - source: "env" (환경변수) | "db" (DB 설정)
    """
    # DB에 설정값이 있으면 우선 사용
    setting = db.query(AdminSystemSetting).filter(
        AdminSystemSetting.key == SETTING_KEY_FOLDER_PATH
    ).first()

    if setting and setting.value:
        return (setting.value, "db")

    # DB 설정이 없으면 환경변수 사용
    return (KNOWLEDGE_FOLDER_PATH, "env")


def set_folder_path(db: Session, folder_path: str) -> str:
    """
    지식관리 폴더 경로 설정.

    Args:
        db: DB 세션
        folder_path: 설정할 폴더 경로

    Returns:
        설정된 폴더 경로

    Raises:
        ValueError: 폴더 경로가 유효하지 않을 때
    """
    # 경로 유효성 검증
    if not folder_path or not folder_path.strip():
        raise ValueError("폴더 경로는 비어있을 수 없습니다")

    folder_path = folder_path.strip()

    # 절대 경로 변환 (상대 경로인 경우 PROJECT_ROOT 기준)
    if not os.path.isabs(folder_path):
        abs_path = PROJECT_ROOT / folder_path
    else:
        abs_path = Path(folder_path)

    # 폴더가 존재하지 않으면 생성
    abs_path.mkdir(parents=True, exist_ok=True)

    # DB에 저장 (상대 경로 또는 절대 경로 그대로)
    setting = db.query(AdminSystemSetting).filter(
        AdminSystemSetting.key == SETTING_KEY_FOLDER_PATH
    ).first()

    if setting:
        setting.value = folder_path
    else:
        setting = AdminSystemSetting(
            key=SETTING_KEY_FOLDER_PATH,
            value=folder_path,
            description="지식관리 전용 폴더 경로 (Phase 15-1)"
        )
        db.add(setting)

    db.commit()
    db.refresh(setting)

    return folder_path


def get_absolute_folder_path(db: Session) -> Path:
    """
    지식관리 폴더 절대 경로 반환.

    Args:
        db: DB 세션

    Returns:
        절대 경로 (Path 객체)
    """
    folder_path, _ = get_folder_path(db)

    if os.path.isabs(folder_path):
        return Path(folder_path)
    else:
        return PROJECT_ROOT / folder_path


class FileInfo:
    """파일 정보 클래스 (Phase 15-1-2)"""

    def __init__(
        self,
        file_name: str,
        file_path: str,
        relative_path: str,
        size: int,
        updated_at: datetime,
        document_id: Optional[int] = None,
        chunk_count: int = 0,
        status: Literal["synced", "unsynced", "new"] = "new",
    ):
        self.file_name = file_name
        self.file_path = file_path
        self.relative_path = relative_path
        self.size = size
        self.updated_at = updated_at
        self.document_id = document_id
        self.chunk_count = chunk_count
        self.status = status


def scan_folder_files(
    db: Session,
    max_depth: int = 3,
    allowed_extensions: Optional[set] = None
) -> List[FileInfo]:
    """
    지정 폴더 내 파일 스캔 및 DB 매칭 (Phase 15-1-2).

    Args:
        db: DB 세션
        max_depth: 최대 재귀 깊이 (기본값: 3)
        allowed_extensions: 허용 확장자 집합 (기본값: ALLOWED_EXTENSIONS)

    Returns:
        FileInfo 객체 리스트
    """
    if allowed_extensions is None:
        allowed_extensions = ALLOWED_EXTENSIONS

    folder_path = get_absolute_folder_path(db)

    if not folder_path.exists():
        return []

    # 파일 시스템 스캔
    file_infos = []

    def _scan_recursive(current_path: Path, depth: int):
        if depth > max_depth:
            return

        try:
            for item in current_path.iterdir():
                if item.is_file():
                    # 확장자 필터링
                    if item.suffix.lower() not in allowed_extensions:
                        continue

                    # 파일 정보 수집
                    stat = item.stat()
                    relative_path = str(item.relative_to(folder_path))

                    file_info = FileInfo(
                        file_name=item.name,
                        file_path=str(item),
                        relative_path=relative_path,
                        size=stat.st_size,
                        updated_at=datetime.fromtimestamp(stat.st_mtime),
                        status="new"
                    )
                    file_infos.append(file_info)

                elif item.is_dir() and not item.name.startswith('.'):
                    # 숨김 폴더 제외하고 재귀 스캔
                    _scan_recursive(item, depth + 1)

        except PermissionError:
            # 권한 없는 폴더는 건너뛰기
            pass

    _scan_recursive(folder_path, 0)

    # DB 문서와 매칭
    _match_with_documents(db, file_infos)

    return file_infos


def _match_with_documents(db: Session, file_infos: List[FileInfo]):
    """
    파일 정보와 documents 테이블 매칭 (Phase 15-1-2).

    Args:
        db: DB 세션
        file_infos: 파일 정보 리스트 (in-place 수정)
    """
    # 모든 documents 조회 (file_path 기준)
    documents = db.query(Document).all()
    doc_map = {doc.file_path: doc for doc in documents}

    # 각 파일과 매칭
    for file_info in file_infos:
        doc = doc_map.get(file_info.file_path)

        if doc:
            # 문서 존재 → synced or unsynced 판정
            file_info.document_id = doc.id

            # 청크 개수 조회
            chunk_count = db.query(func.count(KnowledgeChunk.id)).filter(
                KnowledgeChunk.document_id == doc.id
            ).scalar()
            file_info.chunk_count = chunk_count or 0

            # 파일 수정 시간과 DB 업데이트 시간 비교
            # 파일이 더 최신이면 unsynced, 같거나 오래되었으면 synced
            if doc.updated_at and file_info.updated_at > doc.updated_at:
                file_info.status = "unsynced"
            else:
                file_info.status = "synced"
        # else: status는 이미 "new"


# ============================================
# Phase 15-1-3: 파일 업로드 및 동기화
# ============================================

def save_uploaded_file(
    db: Session,
    file_name: str,
    file_content: bytes,
    relative_path: Optional[str] = None
) -> Document:
    """
    업로드된 파일을 지정 폴더에 저장하고 documents에 등록 (Phase 15-1-3).

    Args:
        db: DB 세션
        file_name: 파일명
        file_content: 파일 내용 (bytes)
        relative_path: 상대 경로 (지정 시 해당 경로에 저장)

    Returns:
        생성된 Document 객체

    Raises:
        ValueError: 파일 확장자가 허용되지 않을 때
        FileExistsError: 동일 file_path가 DB에 이미 존재할 때
    """
    # 확장자 검증
    file_suffix = Path(file_name).suffix.lower()
    if file_suffix not in ALLOWED_EXTENSIONS:
        raise ValueError(f"허용되지 않는 파일 확장자입니다: {file_suffix}")

    # 저장 경로 결정
    folder_path = get_absolute_folder_path(db)
    if relative_path:
        # 상대 경로가 지정되면 해당 경로에 저장
        save_path = folder_path / relative_path / file_name
    else:
        # 루트에 저장
        save_path = folder_path / file_name

    # 부모 디렉토리 생성
    save_path.parent.mkdir(parents=True, exist_ok=True)

    # 중복 체크
    existing = db.query(Document).filter(Document.file_path == str(save_path)).first()
    if existing:
        raise FileExistsError(f"파일이 이미 존재합니다: {save_path}")

    # 파일 저장
    save_path.write_bytes(file_content)

    # DB에 문서 등록
    file_stat = save_path.stat()
    file_type = file_suffix.lstrip('.')  # .md → md

    document = Document(
        file_path=str(save_path),
        file_name=file_name,
        file_type=file_type,
        size=file_stat.st_size,
        updated_at=datetime.fromtimestamp(file_stat.st_mtime)
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    return document


class SyncResult:
    """동기화 결과 (Phase 15-1-3)"""

    def __init__(
        self,
        added_count: int = 0,
        missing_count: int = 0,
        unchanged_count: int = 0,
        added_files: Optional[List[str]] = None,
        missing_files: Optional[List[str]] = None,
    ):
        self.added_count = added_count
        self.missing_count = missing_count
        self.unchanged_count = unchanged_count
        self.added_files = added_files or []
        self.missing_files = missing_files or []


def sync_folder_to_db(
    db: Session,
    max_depth: int = 3,
    delete_missing: bool = False
) -> SyncResult:
    """
    폴더 전체를 DB와 동기화 (Phase 15-1-3).

    Args:
        db: DB 세션
        max_depth: 최대 재귀 깊이
        delete_missing: True이면 폴더에 없는 문서를 DB에서 삭제

    Returns:
        SyncResult 객체
    """
    # 파일 스캔
    file_infos = scan_folder_files(db, max_depth=max_depth)

    added_count = 0
    missing_count = 0
    unchanged_count = 0
    added_files = []
    missing_files = []

    # 파일 시스템 → DB 동기화 (new 파일 추가)
    for file_info in file_infos:
        if file_info.status == "new":
            # DB에 추가
            file_type = Path(file_info.file_name).suffix.lstrip('.')
            document = Document(
                file_path=file_info.file_path,
                file_name=file_info.file_name,
                file_type=file_type,
                size=file_info.size,
                updated_at=file_info.updated_at
            )
            db.add(document)
            added_count += 1
            added_files.append(file_info.relative_path)
        else:
            # synced or unsynced (이미 DB에 존재)
            unchanged_count += 1

    db.commit()

    # DB → 파일 시스템 검증 (missing 파일)
    file_paths = {f.file_path for f in file_infos}
    all_documents = db.query(Document).all()

    for doc in all_documents:
        if doc.file_path not in file_paths:
            # 폴더에 없는 문서
            missing_count += 1
            missing_files.append(doc.file_path)

            if delete_missing:
                # DB에서 삭제 (cascade로 청크도 삭제)
                db.delete(doc)

    if delete_missing:
        db.commit()

    return SyncResult(
        added_count=added_count,
        missing_count=missing_count,
        unchanged_count=unchanged_count,
        added_files=added_files,
        missing_files=missing_files
    )


# ============================================
# Phase 15-9: 디렉토리 탐색 (트리뷰용)
# ============================================

def list_directory(
    relative_path: str = "",
    show_files: bool = False,
) -> List[Dict[str, Any]]:
    """
    PROJECT_ROOT 기준 디렉토리/파일 목록 반환 (트리뷰용).

    Args:
        relative_path: PROJECT_ROOT 기준 상대 경로 (빈 문자열이면 루트)
        show_files: True이면 파일도 포함, False이면 디렉토리만

    Returns:
        [{name, path, type("dir"|"file"), children_count}] 리스트

    Raises:
        ValueError: path traversal 시도 등 잘못된 경로
    """
    # 경로 조합
    if relative_path:
        target = (PROJECT_ROOT / relative_path).resolve()
    else:
        target = PROJECT_ROOT.resolve()

    # 보안: PROJECT_ROOT 내부인지 검증
    project_root_resolved = PROJECT_ROOT.resolve()
    if not (target == project_root_resolved or str(target).startswith(str(project_root_resolved) + os.sep)):
        raise ValueError("허용되지 않는 경로입니다")

    if not target.exists() or not target.is_dir():
        raise ValueError("존재하지 않는 디렉토리입니다")

    items = []
    try:
        for entry in target.iterdir():
            # 숨김 폴더/파일 제외
            if entry.name.startswith('.'):
                continue

            if entry.is_dir():
                # 하위 항목 수 계산 (1단계만)
                children_count = 0
                try:
                    children_count = sum(
                        1 for child in entry.iterdir()
                        if not child.name.startswith('.') and (child.is_dir() or show_files)
                    )
                except PermissionError:
                    pass

                rel_path = str(entry.relative_to(project_root_resolved))
                items.append({
                    "name": entry.name,
                    "path": rel_path,
                    "type": "dir",
                    "children_count": children_count,
                })
            elif show_files and entry.is_file():
                rel_path = str(entry.relative_to(project_root_resolved))
                items.append({
                    "name": entry.name,
                    "path": rel_path,
                    "type": "file",
                    "children_count": 0,
                })
    except PermissionError:
        pass

    # 정렬: 디렉토리 우선, 이름 알파벳순
    items.sort(key=lambda x: (0 if x["type"] == "dir" else 1, x["name"].lower()))

    return items
