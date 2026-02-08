"""문서 경로 동기화 서비스"""
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session

from backend.config import PROJECT_ROOT
from backend.models.models import Document, KnowledgeChunk
from backend.models.database import SessionLocal
from qdrant_client import QdrantClient
from backend.config import QDRANT_HOST, QDRANT_PORT, COLLECTION_NAME


def get_file_hash(file_path: Path) -> str:
    """파일의 해시값을 계산"""
    try:
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return ""


def find_document_by_hash(db: Session, file_hash: str, file_name: str, current_path: str) -> Optional[Document]:
    """파일 해시와 파일명으로 문서 찾기
    
    Args:
        db: 데이터베이스 세션
        file_hash: 현재 파일의 해시
        file_name: 파일명
        current_path: 현재 파일 경로 (제외할 경로)
    """
    if not file_hash:
        return None
    
    # 먼저 파일명으로 찾기
    documents = db.query(Document).filter(Document.file_name == file_name).all()
    
    if not documents:
        return None
    
    # 파일 해시로 매칭 시도
    for doc in documents:
        # 현재 경로와 같으면 스킵
        if doc.file_path == current_path:
            continue
            
        old_path = PROJECT_ROOT / doc.file_path
        if old_path.exists():
            old_hash = get_file_hash(old_path)
            if old_hash == file_hash:
                return doc
    
    # 해시가 일치하지 않으면 파일 크기로도 비교 시도
    try:
        current_size = (PROJECT_ROOT / current_path).stat().st_size
        for doc in documents:
            if doc.file_path == current_path:
                continue
            old_path = PROJECT_ROOT / doc.file_path
            if old_path.exists():
                old_size = old_path.stat().st_size
                if old_size == current_size and doc.size == current_size:
                    # 파일 크기가 같으면 같은 파일일 가능성이 높음
                    return doc
    except:
        pass
    
    return None


def sync_document_paths(db: Session, qdrant_client: QdrantClient) -> Dict:
    """문서 경로 동기화
    
    파일 시스템을 스캔하여 실제 파일 경로와 DB의 경로를 비교하고,
    경로가 변경된 경우 업데이트합니다.
    """
    brain_dir = PROJECT_ROOT / "brain"
    docs_dir = PROJECT_ROOT / "docs"
    
    stats = {
        'scanned': 0,
        'updated': 0,
        'not_found': 0,
        'errors': []
    }
    
    # 모든 마크다운 파일 찾기
    all_files = []
    for md_file in brain_dir.rglob("*.md"):
        if md_file.is_file():
            all_files.append(md_file)
    for md_file in docs_dir.rglob("*.md"):
        if md_file.is_file():
            all_files.append(md_file)
    
    stats['scanned'] = len(all_files)
    
    for file_path in all_files:
        try:
            relative_path = str(file_path.relative_to(PROJECT_ROOT))
            file_name = file_path.name
            file_hash = get_file_hash(file_path)
            
            if not file_hash:
                continue
            
            # DB에서 해당 경로의 문서 찾기
            existing_doc = db.query(Document).filter(
                Document.file_path == relative_path
            ).first()
            
            if existing_doc:
                # 경로가 일치하면 스킵
                continue
            
            # 경로가 다른 경우, 파일명과 해시로 찾기
            matched_doc = find_document_by_hash(db, file_hash, file_name, relative_path)
            
            if matched_doc:
                old_path = matched_doc.file_path
                
                # 경로 업데이트
                matched_doc.file_path = relative_path
                
                # KnowledgeChunk의 file_path 정보도 업데이트 (Qdrant payload 업데이트)
                chunks = db.query(KnowledgeChunk).filter(
                    KnowledgeChunk.document_id == matched_doc.id
                ).all()
                
                # Qdrant에서 해당 문서의 포인트들 찾아서 업데이트
                for chunk in chunks:
                    if chunk.qdrant_point_id:
                        try:
                            point_id = int(chunk.qdrant_point_id)
                            # Qdrant에서 포인트 가져오기
                            points = qdrant_client.retrieve(
                                collection_name=COLLECTION_NAME,
                                ids=[point_id]
                            )
                            
                            if points:
                                # payload 업데이트
                                qdrant_client.set_payload(
                                    collection_name=COLLECTION_NAME,
                                    payload={"file_path": relative_path},
                                    points=[point_id]
                                )
                        except Exception as e:
                            stats['errors'].append(f"Qdrant 업데이트 오류 (chunk {chunk.id}): {str(e)}")
                
                db.commit()
                stats['updated'] += 1
                print(f"  ✅ 경로 업데이트: {old_path} → {relative_path}")
            else:
                # 매칭되는 문서를 찾을 수 없음 (새 파일일 수 있음)
                stats['not_found'] += 1
                
        except Exception as e:
            stats['errors'].append(f"파일 처리 오류 ({file_path}): {str(e)}")
    
    return stats


def sync_single_document(file_path: str, db: Session, qdrant_client: QdrantClient) -> Optional[Dict]:
    """단일 문서 경로 동기화
    
    파일이 존재하지 않으면 파일명으로 검색하여 매칭을 시도합니다.
    """
    try:
        full_path = PROJECT_ROOT / file_path
        
        # 파일이 존재하지 않으면 파일명으로 검색
        if not full_path.exists():
            file_name = Path(file_path).name
            
            # brain과 docs 디렉토리에서 파일 검색
            found_files = []
            for search_dir in [PROJECT_ROOT / "brain", PROJECT_ROOT / "docs"]:
                if search_dir.exists():
                    found_files.extend(list(search_dir.rglob(file_name)))
            
            if found_files:
                # 첫 번째로 찾은 파일 사용
                found_path = found_files[0]
                found_relative = str(found_path.relative_to(PROJECT_ROOT))
                file_path = found_relative
                full_path = found_path
            else:
                return {"error": f"파일을 찾을 수 없습니다: {file_path}"}
        
        file_name = full_path.name
        file_hash = get_file_hash(full_path)
        
        if not file_hash:
            return {"error": "파일 해시를 계산할 수 없습니다"}
        
        # DB에서 해당 경로의 문서 찾기
        existing_doc = db.query(Document).filter(
            Document.file_path == file_path
        ).first()
        
        if existing_doc:
            return {"message": "경로가 이미 일치합니다", "document_id": existing_doc.id}
        
        # 파일명과 해시로 찾기
        matched_doc = find_document_by_hash(db, file_hash, file_name, file_path)
        
        if matched_doc:
            old_path = matched_doc.file_path
            matched_doc.file_path = file_path
            
            # Qdrant 업데이트
            chunks = db.query(KnowledgeChunk).filter(
                KnowledgeChunk.document_id == matched_doc.id
            ).all()
            
            for chunk in chunks:
                if chunk.qdrant_point_id:
                    try:
                        point_id = int(chunk.qdrant_point_id)
                        qdrant_client.set_payload(
                            collection_name=COLLECTION_NAME,
                            payload={"file_path": file_path},
                            points=[point_id]
                        )
                    except:
                        pass
            
            db.commit()
            
            return {
                "message": "경로가 업데이트되었습니다",
                "old_path": old_path,
                "new_path": file_path,
                "document_id": matched_doc.id
            }
        else:
            return {"message": "매칭되는 문서를 찾을 수 없습니다 (새 파일일 수 있음)"}
            
    except Exception as e:
        return {"error": str(e)}
