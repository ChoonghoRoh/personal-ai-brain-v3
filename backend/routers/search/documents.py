"""문서 API 라우터"""
from fastapi import APIRouter, HTTPException, Query
from pathlib import Path
from typing import List, Dict, Optional

from backend.config import PROJECT_ROOT, SYSTEM_DIR, QDRANT_HOST, QDRANT_PORT, COLLECTION_NAME
from backend.models.database import SessionLocal
from backend.services.search.document_sync_service import sync_document_paths, sync_single_document
from qdrant_client import QdrantClient

BRAIN_DIR = PROJECT_ROOT / "brain"

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.get("/work-log")
async def get_work_log() -> Dict:
    """작업 로그 파일 (work_log.md) 직접 읽기"""
    work_log_path = SYSTEM_DIR / "work_log.md"
    
    if not work_log_path.exists():
        raise HTTPException(status_code=404, detail="작업 로그 파일을 찾을 수 없습니다.")
    
    try:
        with open(work_log_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {
            'id': 'brain/system/work_log.md',
            'file_path': 'brain/system/work_log.md',
            'name': 'work_log.md',
            'type': 'markdown',
            'content': content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"작업 로그 파일 읽기 오류: {str(e)}")


@router.get("")
async def list_documents(
    sync: bool = Query(False, description="문서 경로 자동 동기화 여부")
) -> List[Dict]:
    """모든 문서 목록 조회
    
    Args:
        sync: True인 경우 파일 시스템과 DB의 경로를 자동으로 동기화합니다.
    """
    # 경로 동기화 요청 시 실행
    if sync:
        try:
            db = SessionLocal()
            qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
            sync_stats = sync_document_paths(db, qdrant_client)
            db.close()
            print(f"문서 경로 동기화 완료: {sync_stats}")
        except Exception as e:
            print(f"문서 경로 동기화 오류: {e}")
    
    documents = []
    
    # brain 디렉토리의 모든 .md 파일 찾기
    for md_file in BRAIN_DIR.rglob("*.md"):
        if md_file.is_file():
            relative_path = md_file.relative_to(PROJECT_ROOT)
            try:
                stat = md_file.stat()
                documents.append({
                    'id': str(relative_path),
                    'file_path': str(relative_path),
                    'name': md_file.name,
                    'size': stat.st_size,
                    'modified': stat.st_mtime
                })
            except:
                pass
    
    # docs 디렉토리의 모든 .md 파일도 포함
    docs_dir = PROJECT_ROOT / "docs"
    if docs_dir.exists():
        for md_file in docs_dir.rglob("*.md"):
            if md_file.is_file():
                relative_path = md_file.relative_to(PROJECT_ROOT)
                try:
                    stat = md_file.stat()
                    documents.append({
                        'id': str(relative_path),
                        'file_path': str(relative_path),
                        'name': md_file.name,
                        'size': stat.st_size,
                        'modified': stat.st_mtime
                    })
                except:
                    pass
    
    # 수정 시간순으로 정렬 (최신이 위)
    documents.sort(key=lambda x: x.get('modified', 0), reverse=True)
    
    return documents


@router.get("/{document_id:path}")
async def get_document(document_id: str) -> Dict:
    """문서 내용 조회"""
    try:
        # 경로 보안 검사
        # document_id는 FastAPI가 자동으로 디코딩한 상태로 들어옴 (예: "brain/system/context.md" 또는 "test.md")
        # brain 디렉토리 내의 파일만 접근 허용
        
        # 경로 정규화: 앞뒤 공백 제거
        document_id = document_id.strip()
        
        # URL 인코딩된 부분이 남아있을 수 있으므로 추가 디코딩 시도
        import urllib.parse
        try:
            document_id = urllib.parse.unquote(document_id)
        except:
            pass
        
        # brain/ 또는 docs/로 시작하는 경우: PROJECT_ROOT 기준으로 경로 생성
        if document_id.startswith("brain/"):
            doc_path = PROJECT_ROOT / document_id
        elif document_id.startswith("docs/"):
            doc_path = PROJECT_ROOT / document_id
        # 파일명만 있는 경우 (슬래시 없음): brain 디렉토리 전체에서 검색
        elif "/" not in document_id:
            # brain 디렉토리 전체에서 파일 검색
            found_files = list(BRAIN_DIR.rglob(document_id))
            if found_files:
                # 첫 번째로 찾은 파일 사용
                doc_path = found_files[0]
            else:
                # 파일을 찾을 수 없으면 기본 경로로 시도 (하위 호환성)
                doc_path = BRAIN_DIR / document_id
        # 다른 경로는 거부
        else:
            raise HTTPException(status_code=403, detail=f"접근 권한이 없습니다. brain 또는 docs 디렉토리 내의 파일만 접근 가능합니다. (요청 경로: {document_id})")
        
        # 최종 경로 검증: brain 또는 docs 디렉토리 내의 파일만 접근 허용
        resolved_path = doc_path.resolve()
        resolved_brain = BRAIN_DIR.resolve()
        resolved_project = PROJECT_ROOT.resolve()
        docs_dir = resolved_project / "docs"
        
        # brain 디렉토리 또는 docs 디렉토리 내의 파일인지 확인
        is_in_brain = str(resolved_path).startswith(str(resolved_brain))
        is_in_docs = str(resolved_path).startswith(str(docs_dir))
        
        if not (is_in_brain or is_in_docs):
            raise HTTPException(status_code=403, detail=f"접근 권한이 없습니다. brain 또는 docs 디렉토리 내의 파일만 접근 가능합니다. (해석된 경로: {resolved_path}, brain 디렉토리: {resolved_brain}, docs 디렉토리: {docs_dir})")
        
        if not doc_path.exists() or not doc_path.is_file():
            # 파일을 찾을 수 없는 경우, 파일명으로 검색하여 경로 동기화 시도
            file_name = Path(document_id).name if "/" in document_id else document_id
            
            # brain과 docs 디렉토리에서 파일 검색
            found_files = []
            for search_dir in [BRAIN_DIR, PROJECT_ROOT / "docs"]:
                if search_dir.exists():
                    found_files.extend(list(search_dir.rglob(file_name)))
            
            if found_files:
                # 첫 번째로 찾은 파일로 경로 동기화 시도
                found_path = found_files[0]
                found_relative = str(found_path.relative_to(PROJECT_ROOT))
                try:
                    db = SessionLocal()
                    qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
                    sync_result = sync_single_document(found_relative, db, qdrant_client)
                    db.close()
                    if sync_result and "error" not in sync_result:
                        # 동기화 성공 시 새 경로로 다시 시도
                        doc_path = found_path
                        document_id = found_relative
                    else:
                        # 동기화 실패해도 파일은 사용
                        doc_path = found_path
                        document_id = found_relative
                except Exception as e:
                    # 동기화 실패해도 파일은 사용
                    print(f"경로 동기화 오류 (파일은 사용): {e}")
                    doc_path = found_path
                    document_id = found_relative
            else:
                # 더 친화적인 에러 메시지 제공
                suggestions = []
                filename_lower = file_name.lower()
                for search_dir in [BRAIN_DIR, PROJECT_ROOT / "docs"]:
                    if search_dir.exists():
                        for md_file in search_dir.rglob("*.md"):
                            if md_file.is_file() and filename_lower in md_file.name.lower():
                                relative = md_file.relative_to(PROJECT_ROOT)
                                suggestions.append(str(relative))
                
                error_detail = f"문서를 찾을 수 없습니다: {document_id}"
                if suggestions:
                    error_detail += f"\n유사한 파일: {', '.join(suggestions[:3])}"
                raise HTTPException(status_code=404, detail=error_detail)
        
        # 파일 확장자 확인
        ext = doc_path.suffix.lower()
        
        if ext == '.md':
            # Markdown 파일
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {
                'id': document_id,
                'file_path': document_id,
                'name': doc_path.name,
                'type': 'markdown',
                'content': content
            }
        elif ext == '.pdf':
            # PDF 파일
            return {
                'id': document_id,
                'file_path': document_id,
                'name': doc_path.name,
                'type': 'pdf',
                'content': None,
                'message': 'PDF 뷰어는 프론트엔드에서 처리합니다'
            }
        elif ext in ['.docx', '.doc']:
            # DOCX 파일
            return {
                'id': document_id,
                'file_path': document_id,
                'name': doc_path.name,
                'type': 'docx',
                'content': None,
                'message': 'DOCX 뷰어는 프론트엔드에서 처리합니다'
            }
        else:
            # 확장자가 없거나 지원하지 않는 형식
            # 기본적으로 텍스트 파일로 처리 시도
            if not ext:
                # 확장자가 없는 경우, 텍스트 파일로 시도
                try:
                    with open(doc_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    return {
                        'id': document_id,
                        'file_path': document_id,
                        'name': doc_path.name,
                        'type': 'text',
                        'content': content
                    }
                except:
                    raise HTTPException(status_code=400, detail=f"지원하지 않는 파일 형식입니다 (확장자 없음)")
            else:
                raise HTTPException(status_code=400, detail=f"지원하지 않는 파일 형식입니다: {ext}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"문서 읽기 오류: {str(e)}")


@router.post("/sync")
async def sync_documents() -> Dict:
    """모든 문서 경로 동기화
    
    파일 시스템을 스캔하여 실제 파일 경로와 DB의 경로를 비교하고,
    경로가 변경된 경우 자동으로 업데이트합니다.
    """
    try:
        db = SessionLocal()
        qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        stats = sync_document_paths(db, qdrant_client)
        db.close()
        
        return {
            "message": "문서 경로 동기화 완료",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"동기화 오류: {str(e)}")


@router.post("/sync/{file_path:path}")
async def sync_single_document_path(file_path: str) -> Dict:
    """단일 문서 경로 동기화
    
    Args:
        file_path: 동기화할 파일 경로 (예: brain/projects/alpha-project/context.md)
    """
    try:
        db = SessionLocal()
        qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        result = sync_single_document(file_path, db, qdrant_client)
        db.close()
        
        if result and "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result or {"message": "동기화 완료"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"동기화 오류: {str(e)}")

