"""지식관리 폴더 경로 설정 API 테스트 (Phase 15-1)

pytest tests/test_folder_management.py -v
"""
import pytest
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session

from backend.services.knowledge.folder_service import (
    get_folder_path,
    set_folder_path,
    get_absolute_folder_path,
    scan_folder_files,
    save_uploaded_file,
    sync_folder_to_db,
    SETTING_KEY_FOLDER_PATH,
)
from backend.models.admin_models import AdminSystemSetting
from backend.models.models import Document, KnowledgeChunk
from backend.config import PROJECT_ROOT


@pytest.fixture
def clean_db_settings(db: Session):
    """테스트 전 DB 설정 초기화"""
    db.query(AdminSystemSetting).filter(
        AdminSystemSetting.key == SETTING_KEY_FOLDER_PATH
    ).delete()
    db.commit()
    yield
    # 테스트 후 정리
    db.query(AdminSystemSetting).filter(
        AdminSystemSetting.key == SETTING_KEY_FOLDER_PATH
    ).delete()
    db.commit()


def test_get_folder_path_default_env(db: Session, clean_db_settings):
    """환경변수 기본값 사용 (DB 설정 없음)"""
    folder_path, source = get_folder_path(db)
    assert source == "env"
    assert folder_path == "brain/knowledge"  # config.py 기본값


def test_set_folder_path_relative(db: Session, clean_db_settings):
    """상대 경로 설정 및 조회"""
    new_path = "brain/test_knowledge"
    result = set_folder_path(db, new_path)
    assert result == new_path

    # DB에서 조회
    folder_path, source = get_folder_path(db)
    assert source == "db"
    assert folder_path == new_path

    # 절대 경로 확인
    abs_path = get_absolute_folder_path(db)
    assert abs_path == PROJECT_ROOT / new_path
    assert abs_path.exists()  # 폴더 자동 생성 확인

    # 정리
    abs_path.rmdir()


def test_set_folder_path_absolute(db: Session, clean_db_settings, tmp_path: Path):
    """절대 경로 설정 및 조회"""
    test_folder = tmp_path / "knowledge_abs"
    result = set_folder_path(db, str(test_folder))
    assert result == str(test_folder)

    # DB에서 조회
    folder_path, source = get_folder_path(db)
    assert source == "db"
    assert folder_path == str(test_folder)

    # 절대 경로 확인
    abs_path = get_absolute_folder_path(db)
    assert abs_path == test_folder
    assert abs_path.exists()


def test_set_folder_path_empty(db: Session, clean_db_settings):
    """빈 경로 설정 시 에러"""
    with pytest.raises(ValueError, match="비어있을 수 없습니다"):
        set_folder_path(db, "")

    with pytest.raises(ValueError, match="비어있을 수 없습니다"):
        set_folder_path(db, "   ")


def test_set_folder_path_update(db: Session, clean_db_settings):
    """기존 설정 업데이트"""
    # 첫 번째 설정
    path1 = "brain/knowledge1"
    set_folder_path(db, path1)
    folder_path, source = get_folder_path(db)
    assert folder_path == path1
    assert source == "db"

    # 두 번째 설정 (업데이트)
    path2 = "brain/knowledge2"
    set_folder_path(db, path2)
    folder_path, source = get_folder_path(db)
    assert folder_path == path2
    assert source == "db"

    # DB 레코드가 1개만 존재하는지 확인
    count = db.query(AdminSystemSetting).filter(
        AdminSystemSetting.key == SETTING_KEY_FOLDER_PATH
    ).count()
    assert count == 1

    # 정리
    abs_path1 = PROJECT_ROOT / path1
    abs_path2 = PROJECT_ROOT / path2
    if abs_path1.exists():
        abs_path1.rmdir()
    if abs_path2.exists():
        abs_path2.rmdir()


def test_get_folder_path_priority(db: Session, clean_db_settings):
    """DB 설정이 환경변수보다 우선"""
    # DB 설정 추가
    db_path = "brain/db_priority"
    set_folder_path(db, db_path)

    # 조회 시 DB 설정이 우선
    folder_path, source = get_folder_path(db)
    assert source == "db"
    assert folder_path == db_path

    # 정리
    abs_path = PROJECT_ROOT / db_path
    if abs_path.exists():
        abs_path.rmdir()


# ============================================
# Phase 15-1-2: 폴더 내 파일 목록 스캔 테스트
# ============================================

@pytest.fixture
def test_folder(db: Session, tmp_path: Path):
    """테스트용 폴더 생성 및 설정"""
    test_folder_path = tmp_path / "knowledge_test"
    test_folder_path.mkdir(parents=True, exist_ok=True)

    # DB에 폴더 경로 설정
    set_folder_path(db, str(test_folder_path))

    yield test_folder_path

    # 정리
    db.query(AdminSystemSetting).filter(
        AdminSystemSetting.key == SETTING_KEY_FOLDER_PATH
    ).delete()
    db.commit()


def test_scan_folder_files_empty(db: Session, test_folder: Path):
    """빈 폴더 스캔"""
    file_infos = scan_folder_files(db)
    assert len(file_infos) == 0


def test_scan_folder_files_basic(db: Session, test_folder: Path):
    """기본 파일 스캔 (확장자 필터링 포함)"""
    # 허용 확장자 파일 생성
    (test_folder / "test1.md").write_text("# Test 1")
    (test_folder / "test2.txt").write_text("Test 2")
    (test_folder / "test3.pdf").touch()

    # 비허용 확장자 파일 (제외되어야 함)
    (test_folder / "test.json").write_text("{}")
    (test_folder / "test.py").write_text("print('hello')")

    file_infos = scan_folder_files(db)

    # 허용 확장자 파일만 3개
    assert len(file_infos) == 3

    file_names = {f.file_name for f in file_infos}
    assert file_names == {"test1.md", "test2.txt", "test3.pdf"}

    # 모든 파일은 상태가 "new"
    assert all(f.status == "new" for f in file_infos)
    assert all(f.document_id is None for f in file_infos)
    assert all(f.chunk_count == 0 for f in file_infos)


def test_scan_folder_files_recursive(db: Session, test_folder: Path):
    """재귀 스캔 (서브 폴더 포함)"""
    # 루트 파일
    (test_folder / "root.md").write_text("# Root")

    # 서브 폴더 파일
    sub1 = test_folder / "sub1"
    sub1.mkdir()
    (sub1 / "sub1.md").write_text("# Sub 1")

    # 깊이 2 폴더
    sub2 = sub1 / "sub2"
    sub2.mkdir()
    (sub2 / "sub2.md").write_text("# Sub 2")

    # 깊이 3 폴더
    sub3 = sub2 / "sub3"
    sub3.mkdir()
    (sub3 / "sub3.md").write_text("# Sub 3")

    # max_depth=3으로 스캔
    file_infos = scan_folder_files(db, max_depth=3)
    file_names = {f.file_name for f in file_infos}
    assert file_names == {"root.md", "sub1.md", "sub2.md", "sub3.md"}

    # max_depth=2로 스캔 (sub3.md 제외)
    file_infos = scan_folder_files(db, max_depth=2)
    file_names = {f.file_name for f in file_infos}
    assert file_names == {"root.md", "sub1.md", "sub2.md"}


def test_scan_folder_files_with_documents(db: Session, test_folder: Path):
    """DB 문서와 매칭 (synced 상태)"""
    # 파일 생성
    file1 = test_folder / "doc1.md"
    file1.write_text("# Document 1")

    # DB에 문서 등록
    doc = Document(
        file_path=str(file1),
        file_name="doc1.md",
        file_type="md",
        size=file1.stat().st_size,
        updated_at=datetime.fromtimestamp(file1.stat().st_mtime)
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # 청크 추가
    chunk = KnowledgeChunk(
        document_id=doc.id,
        content="Test chunk",
        chunk_index=0
    )
    db.add(chunk)
    db.commit()

    # 스캔
    file_infos = scan_folder_files(db)
    assert len(file_infos) == 1

    f = file_infos[0]
    assert f.file_name == "doc1.md"
    assert f.document_id == doc.id
    assert f.chunk_count == 1
    assert f.status == "synced"  # 파일과 DB 업데이트 시간 동일


def test_scan_folder_files_unsynced(db: Session, test_folder: Path):
    """파일 변경 후 unsynced 상태"""
    import time

    # 파일 생성
    file1 = test_folder / "doc2.md"
    file1.write_text("# Document 2")

    # DB에 문서 등록
    doc = Document(
        file_path=str(file1),
        file_name="doc2.md",
        file_type="md",
        size=file1.stat().st_size,
        updated_at=datetime.fromtimestamp(file1.stat().st_mtime)
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # 파일 수정 (DB보다 최신)
    time.sleep(0.1)
    file1.write_text("# Document 2 - Updated")

    # 스캔
    file_infos = scan_folder_files(db)
    assert len(file_infos) == 1

    f = file_infos[0]
    assert f.status == "unsynced"  # 파일이 DB보다 최신
    assert f.document_id == doc.id


# ============================================
# Phase 15-1-3: 파일 업로드/동기화 테스트
# ============================================

def test_save_uploaded_file_basic(db: Session, test_folder: Path):
    """기본 파일 업로드"""
    file_content = b"# Test Upload"
    file_name = "upload_test.md"

    document = save_uploaded_file(
        db=db,
        file_name=file_name,
        file_content=file_content
    )

    # DB 레코드 확인
    assert document.id is not None
    assert document.file_name == file_name
    assert document.file_type == "md"
    assert document.size == len(file_content)

    # 파일 시스템 확인
    saved_path = Path(document.file_path)
    assert saved_path.exists()
    assert saved_path.read_bytes() == file_content


def test_save_uploaded_file_with_relative_path(db: Session, test_folder: Path):
    """상대 경로 지정하여 업로드"""
    file_content = b"# Subfolder Upload"
    file_name = "sub_upload.md"
    relative_path = "subfolder"

    document = save_uploaded_file(
        db=db,
        file_name=file_name,
        file_content=file_content,
        relative_path=relative_path
    )

    # 경로 확인
    saved_path = Path(document.file_path)
    assert saved_path.parent.name == "subfolder"
    assert saved_path.exists()
    assert saved_path.read_bytes() == file_content


def test_save_uploaded_file_invalid_extension(db: Session, test_folder: Path):
    """허용되지 않는 확장자 업로드 시 에러"""
    with pytest.raises(ValueError, match="허용되지 않는 파일 확장자"):
        save_uploaded_file(
            db=db,
            file_name="test.json",
            file_content=b"{}"
        )


def test_save_uploaded_file_duplicate(db: Session, test_folder: Path):
    """중복 file_path 업로드 시 에러"""
    file_content = b"# Test"
    file_name = "duplicate.md"

    # 첫 번째 업로드
    save_uploaded_file(db=db, file_name=file_name, file_content=file_content)

    # 두 번째 업로드 (중복)
    with pytest.raises(FileExistsError, match="파일이 이미 존재합니다"):
        save_uploaded_file(db=db, file_name=file_name, file_content=file_content)


def test_sync_folder_to_db_add_new(db: Session, test_folder: Path):
    """동기화: 폴더에 있으나 DB에 없는 파일 추가"""
    # 파일 생성 (DB에는 미등록)
    (test_folder / "sync1.md").write_text("# Sync 1")
    (test_folder / "sync2.txt").write_text("Sync 2")

    # 동기화
    result = sync_folder_to_db(db)

    assert result.added_count == 2
    assert result.missing_count == 0
    assert result.unchanged_count == 0
    assert len(result.added_files) == 2

    # DB 확인
    docs = db.query(Document).all()
    assert len(docs) == 2
    doc_names = {doc.file_name for doc in docs}
    assert doc_names == {"sync1.md", "sync2.txt"}


def test_sync_folder_to_db_detect_missing(db: Session, test_folder: Path):
    """동기화: DB에 있으나 폴더에 없는 파일 감지"""
    # 폴더에 파일 생성
    file1 = test_folder / "exists.md"
    file1.write_text("# Exists")

    # DB에 2개 문서 등록 (1개는 폴더에 없음)
    doc1 = Document(
        file_path=str(file1),
        file_name="exists.md",
        file_type="md",
        size=file1.stat().st_size
    )
    doc2 = Document(
        file_path=str(test_folder / "missing.md"),
        file_name="missing.md",
        file_type="md",
        size=100
    )
    db.add_all([doc1, doc2])
    db.commit()

    # 동기화 (delete_missing=False)
    result = sync_folder_to_db(db, delete_missing=False)

    assert result.added_count == 0
    assert result.missing_count == 1
    assert result.unchanged_count == 1
    assert "missing.md" in result.missing_files[0]

    # DB에는 여전히 2개 존재
    docs = db.query(Document).all()
    assert len(docs) == 2


def test_sync_folder_to_db_delete_missing(db: Session, test_folder: Path):
    """동기화: 폴더에 없는 문서를 DB에서 삭제"""
    # DB에 문서 등록 (폴더에는 없음)
    doc = Document(
        file_path=str(test_folder / "will_be_deleted.md"),
        file_name="will_be_deleted.md",
        file_type="md",
        size=100
    )
    db.add(doc)
    db.commit()

    # 동기화 (delete_missing=True)
    result = sync_folder_to_db(db, delete_missing=True)

    assert result.missing_count == 1

    # DB에서 삭제되었는지 확인
    docs = db.query(Document).all()
    assert len(docs) == 0
