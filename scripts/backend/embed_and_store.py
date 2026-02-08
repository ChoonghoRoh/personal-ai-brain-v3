#!/usr/bin/env python3
"""
Markdown 파일을 읽어서 임베딩을 생성하고 Qdrant에 저장하는 스크립트
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import hashlib
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from tqdm import tqdm

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, HnswConfigDiff
from sentence_transformers import SentenceTransformer

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.models.database import SessionLocal, init_db
from backend.models.models import Project, Document, KnowledgeChunk

# 프로젝트 루트 경로 설정
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BRAIN_DIR = PROJECT_ROOT / "brain"

# Qdrant 설정
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "brain_documents"

# 임베딩 모델 (한국어 지원 모델 사용)
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def get_file_hash(file_path: Path) -> str:
    """파일의 해시값을 계산하여 고유 ID 생성"""
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def read_markdown_file(file_path: Path) -> str:
    """Markdown 파일 읽기"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"파일 읽기 오류 {file_path}: {e}")
        return ""


def extract_title_from_markdown(content: str, use_ai: bool = False) -> Optional[Tuple[str, str]]:
    """마크다운 내용에서 첫 번째 헤딩을 제목으로 추출
    
    Args:
        content: 마크다운 내용
        use_ai: 헤딩이 없을 때 AI로 제목 생성할지 여부
    
    Returns:
        (title, source) 튜플 또는 None
        source: "heading" | "ai_extracted" | None
    """
    # 첫 번째 헤딩 찾기 (#, ##, ### 등)
    heading_pattern = r'^(#{1,6})\s+(.+)$'
    lines = content.split('\n')
    
    for line in lines:
        match = re.match(heading_pattern, line.strip())
        if match:
            title = match.group(2).strip()
            # 마크다운 링크 제거 [text](url) -> text
            title = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', title)
            # 볼드/이탤릭 제거
            title = re.sub(r'\*\*([^*]+)\*\*', r'\1', title)
            title = re.sub(r'\*([^*]+)\*', r'\1', title)
            # 코드 제거
            title = re.sub(r'`([^`]+)`', r'\1', title)
            if title:
                return (title, "heading")
    
    # 헤딩이 없고 AI 사용 옵션이 켜져 있으면 AI로 제목 생성
    if use_ai:
        ai_title = extract_title_with_ai(content)
        if ai_title:
            return (ai_title, "ai_extracted")
    
    return None


def extract_title_with_ai(content: str) -> Optional[str]:
    """AI를 사용하여 청크 내용에서 제목 추출
    
    Args:
        content: 청크 내용
    
    Returns:
        제목 문자열 또는 None
    """
    try:
        from gpt4all import GPT4All
    except ImportError:
        # GPT4All이 없으면 None 반환 (폴백)
        return None
    
    # 내용 정리 (마크다운 문법 제거)
    cleaned_content = re.sub(r'#+\s*', '', content)
    cleaned_content = re.sub(r'\*\*([^*]+)\*\*', r'\1', cleaned_content)
    cleaned_content = re.sub(r'\*([^*]+)\*', r'\1', cleaned_content)
    cleaned_content = re.sub(r'`([^`]+)`', r'\1', cleaned_content)
    cleaned_content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', cleaned_content)
    
    # 내용이 너무 길면 앞부분만 사용 (토큰 제한 고려)
    # 모델의 컨텍스트 윈도우가 2048 토큰이므로 여유를 두고 1000자로 제한
    # 프롬프트 템플릿이 약 200자, 답변 생성을 위해 200자 여유
    max_length = 1000
    if len(cleaned_content) > max_length:
        cleaned_content = cleaned_content[:max_length] + "..."
    
    # 프롬프트 생성
    prompt = f"""다음 문서 내용을 요약하여 적절한 제목을 생성해주세요.

문서 내용:
{cleaned_content}

요구사항:
1. 문서의 핵심 내용을 잘 나타내는 제목
2. 간결하고 명확한 제목 (최대 50자)
3. 설명 없이 제목만 출력

제목:"""

    try:
        model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf")  # 고성능 모델 (8B 파라미터)
        
        response = model.generate(
            prompt,
            max_tokens=100,
            temp=0.3,  # 일관성 있는 결과
            top_p=0.9
        )
        
        # 응답에서 제목 추출
        title = response.strip()
        # 첫 줄만 사용 (여러 줄이면 첫 줄)
        title = title.split('\n')[0].strip()
        # 따옴표 제거
        title = title.strip('"\'')
        
        # 최대 길이 제한
        if len(title) > 50:
            title = title[:47] + "..."
        
        return title if title else None
        
    except Exception as e:
        print(f"⚠️  AI 제목 추출 오류: {e}")
        return None


def split_markdown_by_headings(
    text: str, 
    min_chunk_size: int = 100, 
    max_chunk_size: int = 2000,
    use_ai_for_title: bool = False
) -> List[Dict[str, any]]:
    """마크다운을 헤딩 기반으로 의미 단위로 분할
    
    Returns:
        List[Dict] with keys: 'content', 'title', 'title_source', 'chunk_index'
    """
    chunks = []
    lines = text.split('\n')
    current_chunk = []
    current_title = None
    current_title_source = None
    chunk_index = 0
    
    heading_pattern = r'^(#{1,6})\s+(.+)$'
    
    for line in lines:
        match = re.match(heading_pattern, line.strip())
        
        if match:
            # 새 헤딩 발견 - 현재 청크 저장
            if current_chunk:
                chunk_content = '\n'.join(current_chunk).strip()
                word_count = len(chunk_content.split())
                
                # 최소 크기 체크
                if word_count >= min_chunk_size:
                    chunks.append({
                        'content': chunk_content,
                        'title': current_title,
                        'title_source': current_title_source,
                        'chunk_index': chunk_index
                    })
                    chunk_index += 1
                elif chunks:
                    # 최소 크기 미만이면 이전 청크에 병합
                    chunks[-1]['content'] += '\n\n' + chunk_content
                    continue
            
            # 새 청크 시작
            title_text = match.group(2).strip()
            # 마크다운 문법 제거
            title_text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', title_text)
            title_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', title_text)
            title_text = re.sub(r'\*([^*]+)\*', r'\1', title_text)
            title_text = re.sub(r'`([^`]+)`', r'\1', title_text)
            
            current_title = title_text if title_text else None
            current_title_source = "heading" if current_title else None
            current_chunk = [line]
        else:
            current_chunk.append(line)
    
    # 마지막 청크 저장
    if current_chunk:
        chunk_content = '\n'.join(current_chunk).strip()
        word_count = len(chunk_content.split())
        
        # 제목이 없고 AI 옵션이 켜져 있으면 AI로 제목 생성
        if not current_title and use_ai_for_title:
            ai_title = extract_title_with_ai(chunk_content)
            if ai_title:
                current_title = ai_title
                current_title_source = "ai_extracted"
        
        if word_count >= min_chunk_size:
            chunks.append({
                'content': chunk_content,
                'title': current_title,
                'title_source': current_title_source,
                'chunk_index': chunk_index
            })
        elif chunks:
            chunks[-1]['content'] += '\n\n' + chunk_content
    
    # 헤딩이 없거나 청크가 생성되지 않은 경우 기존 방식으로 폴백
    if not chunks:
        return split_text_fallback(text, use_ai_for_title)
    
    # 큰 청크를 하위 헤딩으로 재분할
    final_chunks = []
    for chunk in chunks:
        content = chunk['content']
        word_count = len(content.split())
        
        if word_count > max_chunk_size:
            # 하위 헤딩으로 재분할
            sub_chunks = split_markdown_by_headings(content, min_chunk_size, max_chunk_size, use_ai_for_title)
            for sub_chunk in sub_chunks:
                # 상위 제목이 없으면 하위 제목 사용
                if not sub_chunk.get('title'):
                    sub_chunk['title'] = chunk.get('title')
                    sub_chunk['title_source'] = chunk.get('title_source')
                final_chunks.append(sub_chunk)
        else:
            final_chunks.append(chunk)
    
    return final_chunks


def split_text_fallback(text: str, chunk_size: int = 500, overlap: int = 50, use_ai_for_title: bool = False) -> List[Dict[str, any]]:
    """기존 방식으로 텍스트를 청크로 분할 (폴백용)"""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk_content = ' '.join(words[i:i + chunk_size])
        if chunk_content.strip():
            # 제목 추출 시도 (헤딩 우선, 없으면 AI)
            title_info = extract_title_from_markdown(chunk_content, use_ai=use_ai_for_title)
            chunks.append({
                'content': chunk_content,
                'title': title_info[0] if title_info else None,
                'title_source': title_info[1] if title_info else None,
                'chunk_index': len(chunks)
            })
    
    return chunks


def split_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """텍스트를 청크로 분할 (기존 함수, 호환성 유지)"""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    
    return chunks


def process_markdown_files(brain_dir: Path, docs_dir: Path = None, use_heading_split: bool = True, use_ai_for_title: bool = False) -> List[Dict]:
    """brain 디렉토리와 docs 디렉토리의 모든 .md 파일을 처리
    
    Args:
        brain_dir: brain 디렉토리 경로
        docs_dir: docs 디렉토리 경로 (선택적)
        use_heading_split: True면 헤딩 기반 의미 단위 분할 사용, False면 기존 방식
    """
    documents = []
    
    # brain 디렉토리 하위의 모든 .md 파일 찾기
    for md_file in brain_dir.rglob("*.md"):
        if md_file.is_file():
            content = read_markdown_file(md_file)
            if content:
                # 상대 경로 계산
                relative_path = md_file.relative_to(PROJECT_ROOT)
                
                # 의미 단위 분할 또는 기존 방식
                if use_heading_split:
                    chunk_dicts = split_markdown_by_headings(content, use_ai_for_title=use_ai_for_title)
                    for chunk_dict in chunk_dicts:
                        documents.append({
                            'file_path': str(relative_path),
                            'chunk_index': chunk_dict['chunk_index'],
                            'content': chunk_dict['content'],
                            'title': chunk_dict.get('title'),
                            'title_source': chunk_dict.get('title_source'),
                            'full_path': str(md_file)
                        })
                else:
                    chunks = split_text(content)
                    for idx, chunk in enumerate(chunks):
                        # 제목 추출 시도 (헤딩 우선, 없으면 AI)
                        title_info = extract_title_from_markdown(chunk, use_ai=use_ai_for_title)
                        documents.append({
                            'file_path': str(relative_path),
                            'chunk_index': idx,
                            'content': chunk,
                            'title': title_info[0] if title_info else None,
                            'title_source': title_info[1] if title_info else None,
                            'full_path': str(md_file)
                        })
    
    # docs 디렉토리도 처리 (선택적)
    if docs_dir and docs_dir.exists():
        for md_file in docs_dir.rglob("*.md"):
            if md_file.is_file():
                content = read_markdown_file(md_file)
                if content:
                    relative_path = md_file.relative_to(PROJECT_ROOT)
                    
                    if use_heading_split:
                        chunk_dicts = split_markdown_by_headings(content, use_ai_for_title=use_ai_for_title)
                        for chunk_dict in chunk_dicts:
                            documents.append({
                                'file_path': str(relative_path),
                                'chunk_index': chunk_dict['chunk_index'],
                                'content': chunk_dict['content'],
                                'title': chunk_dict.get('title'),
                                'title_source': chunk_dict.get('title_source'),
                                'full_path': str(md_file)
                            })
                    else:
                        chunks = split_text(content)
                        for idx, chunk in enumerate(chunks):
                            title_info = extract_title_from_markdown(chunk, use_ai=use_ai_for_title)
                            documents.append({
                                'file_path': str(relative_path),
                                'chunk_index': idx,
                                'content': chunk,
                                'title': title_info[0] if title_info else None,
                                'title_source': title_info[1] if title_info else None,
                                'full_path': str(md_file)
                            })
    
    return documents


def create_collection_if_not_exists(client: QdrantClient, collection_name: str, vector_size: int, recreate: bool = False):
    """컬렉션이 없으면 생성, recreate=True면 재생성 (최적화된 인덱스 설정)"""
    collections = client.get_collections().collections
    collection_names = [col.name for col in collections]
    
    # HNSW 인덱스 최적화 설정 (성능 향상)
    hnsw_config = HnswConfigDiff(
        m=16,  # 연결 수 (기본값: 16, 높을수록 정확도 향상, 메모리 증가)
        ef_construct=100,  # 인덱스 구축 시 탐색 범위 (기본값: 100)
        full_scan_threshold=10000  # 전체 스캔 임계값 (이 값 이하일 때 전체 스캔)
    )
    
    if collection_name in collection_names:
        if recreate:
            print(f"컬렉션 '{collection_name}' 삭제 중...")
            client.delete_collection(collection_name)
            print(f"컬렉션 '{collection_name}' 재생성 중... (최적화된 인덱스 설정)")
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE,
                    hnsw_config=hnsw_config
                )
            )
            print(f"컬렉션 '{collection_name}' 재생성 완료")
        else:
            print(f"컬렉션 '{collection_name}' 이미 존재함")
            # 기존 컬렉션의 인덱스 설정 확인 및 업데이트 (필요시)
            try:
                collection_info = client.get_collection(collection_name)
                print(f"  - 벡터 수: {collection_info.points_count}")
                print(f"  - 인덱스 상태: {collection_info.status}")
            except Exception as e:
                print(f"  - 컬렉션 정보 확인 오류: {e}")
    else:
        print(f"컬렉션 '{collection_name}' 생성 중... (최적화된 인덱스 설정)")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE,
                hnsw_config=hnsw_config
            )
        )
        print(f"컬렉션 '{collection_name}' 생성 완료")


def get_or_create_project(db, project_name: str, project_path: str) -> Project:
    """프로젝트를 가져오거나 생성"""
    project = db.query(Project).filter(Project.name == project_name).first()
    if not project:
        project = Project(name=project_name, path=project_path)
        db.add(project)
        db.commit()
        db.refresh(project)
    return project


def get_or_create_document(db, file_path: str, project_id: int = None) -> Document:
    """문서를 가져오거나 생성"""
    document = db.query(Document).filter(Document.file_path == file_path).first()
    if not document:
        file_name = Path(file_path).name
        file_type = Path(file_path).suffix[1:] if Path(file_path).suffix else "md"
        file_size = Path(PROJECT_ROOT / file_path).stat().st_size if (PROJECT_ROOT / file_path).exists() else 0
        
        document = Document(
            project_id=project_id,
            file_path=file_path,
            file_name=file_name,
            file_type=file_type,
            size=file_size,
            qdrant_collection=COLLECTION_NAME
        )
        db.add(document)
        db.commit()
        db.refresh(document)
    return document


def embed_and_store(recreate_collection: bool = False, use_ai_for_title: bool = False):
    """메인 함수: 임베딩 생성 및 Qdrant + PostgreSQL 저장
    
    Args:
        recreate_collection: True면 Qdrant 컬렉션을 재생성 (기존 데이터 삭제)
        use_ai_for_title: True면 헤딩이 없을 때 AI로 제목 생성 (기본값: False)
    """
    print("=" * 60)
    print("Markdown 파일 임베딩 및 저장 시작 (Qdrant + PostgreSQL)")
    if recreate_collection:
        print("⚠️  Qdrant 컬렉션 재생성 모드 (기존 데이터 삭제)")
    print("=" * 60)
    
    # 0. 데이터베이스 초기화
    print("\n[0/5] 데이터베이스 초기화 중...")
    init_db()
    
    # 1. Markdown 파일 수집
    print("\n[1/5] Markdown 파일 수집 중...")
    DOCS_DIR = PROJECT_ROOT / "docs"
    documents = process_markdown_files(BRAIN_DIR, docs_dir=DOCS_DIR, use_heading_split=True, use_ai_for_title=use_ai_for_title)
    print(f"총 {len(documents)}개의 문서 청크 발견")
    if use_ai_for_title:
        print("   ℹ️  AI 기반 제목 추출 활성화됨")
    
    if not documents:
        print("처리할 문서가 없습니다.")
        return
    
    # 2. 임베딩 모델 로드
    print("\n[2/5] 임베딩 모델 로드 중...")
    model = SentenceTransformer(EMBEDDING_MODEL)
    vector_size = model.get_sentence_embedding_dimension()
    print(f"모델: {EMBEDDING_MODEL}")
    print(f"벡터 차원: {vector_size}")
    
    # 3. Qdrant 클라이언트 연결 및 컬렉션 생성
    print("\n[3/5] Qdrant 연결 및 컬렉션 설정 중...")
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    create_collection_if_not_exists(client, COLLECTION_NAME, vector_size, recreate=recreate_collection)
    
    # 4. PostgreSQL 세션 생성
    print("\n[4/5] PostgreSQL 연결 중...")
    db = SessionLocal()
    
    # 파일 경로별로 그룹화
    files_dict = {}
    for doc in documents:
        file_path = doc['file_path']
        if file_path not in files_dict:
            files_dict[file_path] = []
        files_dict[file_path].append(doc)
    
    # 5. 임베딩 생성 및 저장
    print("\n[5/5] 임베딩 생성 및 저장 중...")
    points = []
    total_chunks = 0
    
    for file_path, file_chunks in files_dict.items():
        # 프로젝트 추출 (brain/projects/xxx/... 형식)
        path_parts = file_path.split('/')
        project_name = None
        project_path = None
        
        if len(path_parts) >= 3 and path_parts[0] == 'brain' and path_parts[1] == 'projects':
            project_name = path_parts[2]
            project_path = '/'.join(path_parts[:3])
        
        # 프로젝트 생성 또는 가져오기
        project_id = None
        if project_name:
            project = get_or_create_project(db, project_name, project_path)
            project_id = project.id
        
        # 문서 생성 또는 가져오기
        document = get_or_create_document(db, file_path, project_id)
        
        # 기존 청크 및 Qdrant 포인트 삭제 (재처리 시)
        # 관계가 있는 경우를 대비해 관계와 라벨을 먼저 삭제
        from backend.models.models import KnowledgeRelation, KnowledgeLabel
        existing_chunks = db.query(KnowledgeChunk).filter(KnowledgeChunk.document_id == document.id).all()
        
        # Qdrant에서 기존 포인트 삭제
        qdrant_point_ids = []
        for chunk in existing_chunks:
            if chunk.qdrant_point_id:
                try:
                    qdrant_point_ids.append(int(chunk.qdrant_point_id))
                except:
                    pass
            # 해당 청크와 관련된 모든 관계 삭제
            db.query(KnowledgeRelation).filter(
                (KnowledgeRelation.source_chunk_id == chunk.id) |
                (KnowledgeRelation.target_chunk_id == chunk.id)
            ).delete()
            # 해당 청크와 관련된 모든 라벨 삭제
            db.query(KnowledgeLabel).filter(
                KnowledgeLabel.chunk_id == chunk.id
            ).delete()
        
        # Qdrant에서 포인트 삭제
        if qdrant_point_ids:
            try:
                client.delete(
                    collection_name=COLLECTION_NAME,
                    points_selector=qdrant_point_ids
                )
            except Exception as e:
                print(f"Qdrant 포인트 삭제 경고: {e}")
        
        # 이제 청크 삭제 가능
        db.query(KnowledgeChunk).filter(KnowledgeChunk.document_id == document.id).delete()
        db.commit()
        
        # 배치로 임베딩 생성 (성능 최적화)
        chunk_contents = [doc['content'] for doc in file_chunks]
        
        # 배치 임베딩 생성 (한 번에 여러 청크 처리)
        embeddings = model.encode(
            chunk_contents,
            batch_size=32,  # 배치 크기
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        # 각 청크 처리
        for idx, doc in enumerate(file_chunks):
            embedding = embeddings[idx].tolist()
            
            # 고유 ID 생성 (파일 경로 + 청크 인덱스)
            point_id = hash(f"{doc['file_path']}_{doc['chunk_index']}") % (2**63)
            
            # Qdrant 포인트 생성
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    'file_path': doc['file_path'],
                    'chunk_index': doc['chunk_index'],
                    'content': doc['content']
                }
            )
            points.append(point)
            
            # PostgreSQL에 청크 저장
            chunk = KnowledgeChunk(
                document_id=document.id,
                chunk_index=doc['chunk_index'],
                content=doc['content'],
                qdrant_point_id=str(point_id),
                embedding_model=EMBEDDING_MODEL,
                title=doc.get('title'),  # Phase 7.9.5: 제목 추가
                title_source=doc.get('title_source')  # Phase 7.9.5: 제목 출처 추가
            )
            db.add(chunk)
            total_chunks += 1
        
        db.commit()
        print(f"처리 완료: {file_path} ({len(file_chunks)} 청크)")
    
    # Qdrant에 배치로 저장 (최적화된 배치 크기)
    batch_size = 100
    total_batches = (len(points) + batch_size - 1) // batch_size
    
    print(f"\nQdrant 저장 중... (총 {len(points)}개 포인트, {total_batches}개 배치)")
    for i in tqdm(range(0, len(points), batch_size), desc="Qdrant 저장"):
        batch = points[i:i + batch_size]
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=batch
        )
    
    db.close()
    
    print(f"\n✅ 완료!")
    print(f"  - PostgreSQL: {total_chunks}개 청크 저장")
    print(f"  - Qdrant: {len(points)}개 포인트 저장")
    print(f"  - 컬렉션: {COLLECTION_NAME}")
    print(f"  - Qdrant 대시보드: http://{QDRANT_HOST}:{QDRANT_PORT}/dashboard")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="문서 임베딩 및 저장")
    parser.add_argument("--recreate", action="store_true", help="Qdrant 컬렉션 재생성 (기존 데이터 삭제)")
    parser.add_argument("--use-ai-title", action="store_true", help="헤딩이 없을 때 AI로 제목 생성 (GPT4All 필요)")
    args = parser.parse_args()
    embed_and_store(recreate_collection=args.recreate, use_ai_for_title=args.use_ai_title)

