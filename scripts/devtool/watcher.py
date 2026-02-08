#!/usr/bin/env python3
"""
파일 변경 감지 및 자동 임베딩 갱신 시스템
"""

import time
import json
from pathlib import Path
from typing import Dict, Set
from datetime import datetime
import hashlib

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent, FileDeletedEvent

# embed_and_store 모듈의 함수들 import
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# 작업 로그 시스템 import
try:
    from work_logger import log_action
    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False

from embed_and_store import (
    PROJECT_ROOT, BRAIN_DIR, QDRANT_HOST, QDRANT_PORT, 
    COLLECTION_NAME, EMBEDDING_MODEL,
    read_markdown_file, split_text, get_file_hash,
    create_collection_if_not_exists
)
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from sentence_transformers import SentenceTransformer

# 파일 해시 저장소 (변경 감지용)
HASH_STORE_FILE = PROJECT_ROOT / ".file_hashes.json"


class BrainFileHandler(FileSystemEventHandler):
    """brain 디렉토리의 파일 변경을 처리하는 핸들러"""
    
    def __init__(self):
        self.qdrant_client = None
        self.embedding_model = None
        self.vector_size = None
        self.file_hashes = self.load_file_hashes()
        self.pending_files: Set[Path] = set()
        self.last_process_time = 0
        self.process_delay = 2  # 파일 변경 후 2초 대기 후 처리
        
    def load_file_hashes(self) -> Dict[str, str]:
        """저장된 파일 해시 로드"""
        if HASH_STORE_FILE.exists():
            try:
                with open(HASH_STORE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_file_hashes(self):
        """파일 해시 저장"""
        with open(HASH_STORE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.file_hashes, f, indent=2, ensure_ascii=False)
    
    def init_models(self):
        """Qdrant 클라이언트 및 임베딩 모델 초기화"""
        if self.qdrant_client is None:
            self.qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        
        if self.embedding_model is None:
            print("[초기화] 임베딩 모델 로드 중...")
            self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
            self.vector_size = self.embedding_model.get_sentence_embedding_dimension()
            create_collection_if_not_exists(self.qdrant_client, COLLECTION_NAME, self.vector_size)
            print("[초기화] 완료")
    
    def is_markdown_file(self, file_path: Path) -> bool:
        """Markdown 파일인지 확인"""
        return file_path.suffix.lower() == '.md' and file_path.is_file()
    
    def is_brain_file(self, file_path: Path) -> bool:
        """brain 디렉토리 내 파일인지 확인"""
        try:
            relative = file_path.relative_to(PROJECT_ROOT)
            return str(relative).startswith('brain/')
        except ValueError:
            return False
    
    def file_changed(self, file_path: Path) -> bool:
        """파일이 변경되었는지 확인"""
        if not self.is_markdown_file(file_path) or not self.is_brain_file(file_path):
            return False
        
        current_hash = get_file_hash(file_path)
        relative_path = str(file_path.relative_to(PROJECT_ROOT))
        
        if relative_path not in self.file_hashes:
            # 새 파일
            self.file_hashes[relative_path] = current_hash
            self.save_file_hashes()
            return True
        
        if self.file_hashes[relative_path] != current_hash:
            # 파일 변경됨
            self.file_hashes[relative_path] = current_hash
            self.save_file_hashes()
            return True
        
        return False
    
    def process_file(self, file_path: Path):
        """파일을 처리하여 임베딩 생성 및 저장"""
        if not self.is_markdown_file(file_path) or not self.is_brain_file(file_path):
            return
        
        print(f"\n[처리 시작] {file_path.relative_to(PROJECT_ROOT)}")
        
        # 모델 초기화
        self.init_models()
        
        # 파일 읽기
        content = read_markdown_file(file_path)
        if not content:
            print(f"  ⚠️  파일이 비어있거나 읽을 수 없습니다.")
            return
        
        # 텍스트 청크 분할
        chunks = split_text(content)
        if not chunks:
            print(f"  ⚠️  처리할 내용이 없습니다.")
            return
        
        relative_path = str(file_path.relative_to(PROJECT_ROOT))
        
        # 기존 포인트 삭제 (해당 파일의 모든 청크)
        self.delete_file_points(relative_path)
        
        # 새 포인트 생성 및 저장
        points = []
        for idx, chunk in enumerate(chunks):
            # 임베딩 생성
            embedding = self.embedding_model.encode(chunk).tolist()
            
            # 고유 ID 생성
            point_id = hash(f"{relative_path}_{idx}") % (2**63)
            
            # Qdrant 포인트 생성
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    'file_path': relative_path,
                    'chunk_index': idx,
                    'content': chunk
                }
            )
            points.append(point)
        
        # 배치로 저장
        if points:
            self.qdrant_client.upsert(
                collection_name=COLLECTION_NAME,
                points=points
            )
            print(f"  ✅ {len(points)}개의 청크 저장 완료")
            
            # 작업 로그 기록
            if LOGGING_AVAILABLE:
                log_action(
                    action="embed",
                    description=f"파일 임베딩 및 저장: {relative_path}",
                    files=[relative_path],
                    metadata={
                        'chunks_count': len(points),
                        'file_path': relative_path
                    }
                )
        else:
            print(f"  ⚠️  저장할 포인트가 없습니다.")
    
    def delete_file_points(self, file_path: str):
        """특정 파일의 모든 포인트 삭제"""
        try:
            # 파일 경로로 필터링하여 삭제
            from qdrant_client.models import Filter, FieldCondition, MatchValue
            
            # 모든 포인트를 스크롤하여 해당 파일의 포인트 찾기
            scroll_result = self.qdrant_client.scroll(
                collection_name=COLLECTION_NAME,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="file_path",
                            match=MatchValue(value=file_path)
                        )
                    ]
                ),
                limit=1000
            )
            
            if scroll_result[0]:  # points가 있으면
                point_ids = [point.id for point in scroll_result[0]]
                self.qdrant_client.delete(
                    collection_name=COLLECTION_NAME,
                    points_selector=point_ids
                )
                print(f"  🗑️  기존 {len(point_ids)}개 포인트 삭제")
        except Exception as e:
            print(f"  ⚠️  기존 포인트 삭제 중 오류: {e}")
    
    def on_modified(self, event):
        """파일 수정 이벤트 처리"""
        if not event.is_directory:
            file_path = Path(event.src_path)
            if self.file_changed(file_path):
                self.pending_files.add(file_path)
                self.last_process_time = time.time()
                relative_path = str(file_path.relative_to(PROJECT_ROOT))
                print(f"\n[변경 감지] {relative_path}")
                
                # 작업 로그 기록
                if LOGGING_AVAILABLE:
                    log_action(
                        action="file_change",
                        description=f"파일 변경 감지: {relative_path}",
                        files=[relative_path],
                        metadata={'event': 'modified'}
                    )
    
    def on_created(self, event):
        """파일 생성 이벤트 처리"""
        if not event.is_directory:
            file_path = Path(event.src_path)
            if self.file_changed(file_path):
                self.pending_files.add(file_path)
                self.last_process_time = time.time()
                relative_path = str(file_path.relative_to(PROJECT_ROOT))
                print(f"\n[새 파일] {relative_path}")
                
                # 작업 로그 기록
                if LOGGING_AVAILABLE:
                    log_action(
                        action="file_change",
                        description=f"새 파일 생성: {relative_path}",
                        files=[relative_path],
                        metadata={'event': 'created'}
                    )
    
    def on_deleted(self, event):
        """파일 삭제 이벤트 처리"""
        if not event.is_directory:
            file_path = Path(event.src_path)
            relative_path = str(file_path.relative_to(PROJECT_ROOT))
            
            # 해시에서 제거
            if relative_path in self.file_hashes:
                del self.file_hashes[relative_path]
                self.save_file_hashes()
            
            # Qdrant에서 삭제
            self.init_models()
            self.delete_file_points(relative_path)
            print(f"\n[삭제] {relative_path}")
            
            # 작업 로그 기록
            if LOGGING_AVAILABLE:
                log_action(
                    action="file_change",
                    description=f"파일 삭제: {relative_path}",
                    files=[relative_path],
                    metadata={'event': 'deleted'}
                )
    
    def process_pending_files(self):
        """대기 중인 파일들 처리"""
        current_time = time.time()
        
        # 마지막 변경 후 일정 시간 경과했는지 확인
        if self.pending_files and (current_time - self.last_process_time) >= self.process_delay:
            files_to_process = list(self.pending_files)
            self.pending_files.clear()
            
            for file_path in files_to_process:
                try:
                    self.process_file(file_path)
                except Exception as e:
                    print(f"  ❌ 처리 오류: {e}")


def watch_brain_directory():
    """brain 디렉토리 감시 시작"""
    print("=" * 60)
    print("Personal AI Brain - 파일 변경 감지 시스템 시작")
    print("=" * 60)
    print(f"감시 디렉토리: {BRAIN_DIR}")
    print(f"Qdrant: {QDRANT_HOST}:{QDRANT_PORT}")
    print(f"컬렉션: {COLLECTION_NAME}")
    print("\n파일 변경을 감지하면 자동으로 임베딩을 갱신합니다.")
    print("종료하려면 Ctrl+C를 누르세요.\n")
    
    event_handler = BrainFileHandler()
    observer = Observer()
    observer.schedule(event_handler, str(BRAIN_DIR), recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(0.5)
            event_handler.process_pending_files()
    except KeyboardInterrupt:
        print("\n\n[종료] 파일 감시를 중지합니다...")
        observer.stop()
    
    observer.join()
    print("[종료] 완료")


if __name__ == "__main__":
    watch_brain_directory()

