#!/usr/bin/env python3
"""
Qdrant에서 검색하고 GPT4All로 응답을 생성하는 스크립트
"""

import sys
from pathlib import Path
from typing import List, Dict

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from gpt4all import GPT4All

# 프로젝트 루트 경로 설정
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Qdrant 설정
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "brain_documents"

# 임베딩 모델
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# GPT4All 모델 (작은 모델 사용)
GPT4ALL_MODEL = "Meta-Llama-3-8B-Instruct.Q4_0.gguf"  # 고성능 모델 (8B 파라미터)


def search_documents(query: str, top_k: int = 5) -> List[Dict]:
    """쿼리로 관련 문서 검색"""
    # 임베딩 모델 로드
    model = SentenceTransformer(EMBEDDING_MODEL)
    
    # 쿼리 임베딩 생성
    query_embedding = model.encode(query).tolist()
    
    # Qdrant 클라이언트 연결
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    
    # 검색 실행 (query_points 사용 - 벡터를 직접 전달)
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=top_k
    )
    
    # 결과 포맷팅
    documents = []
    for result in results.points:
        documents.append({
            'score': result.score,
            'content': result.payload.get('content', ''),
            'file_path': result.payload.get('file_path', ''),
            'chunk_index': result.payload.get('chunk_index', 0)
        })
    
    return documents


def create_context_from_documents(documents: List[Dict]) -> str:
    """검색된 문서들을 컨텍스트로 변환"""
    context_parts = []
    for i, doc in enumerate(documents, 1):
        context_parts.append(
            f"[문서 {i}] (파일: {doc['file_path']}, 유사도: {doc['score']:.3f})\n"
            f"{doc['content']}\n"
        )
    return "\n".join(context_parts)


def query_with_gpt4all(query: str, context: str) -> str:
    """GPT4All을 사용하여 컨텍스트 기반 응답 생성"""
    # GPT4All 모델 초기화 (첫 실행 시 자동 다운로드)
    model = GPT4All(GPT4ALL_MODEL)
    
    # 프롬프트 구성
    prompt = f"""다음 컨텍스트를 기반으로 질문에 답변해주세요.

컨텍스트:
{context}

질문: {query}

답변:"""
    
    # 응답 생성
    response = model.generate(prompt, max_tokens=200, temp=0.7)
    return response


def interactive_search():
    """대화형 검색 인터페이스"""
    print("=" * 60)
    print("Personal AI Brain - 검색 및 질의 시스템")
    print("=" * 60)
    print("\n종료하려면 'quit' 또는 'exit'를 입력하세요.\n")
    
    while True:
        try:
            query = input("질문을 입력하세요: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("종료합니다.")
                break
            
            if not query:
                continue
            
            # 1. 문서 검색
            print("\n[검색 중...]")
            documents = search_documents(query, top_k=5)
            
            if not documents:
                print("관련 문서를 찾을 수 없습니다.")
                continue
            
            # 검색 결과 출력
            print(f"\n[검색 결과] {len(documents)}개의 관련 문서 발견:\n")
            for i, doc in enumerate(documents, 1):
                print(f"{i}. [{doc['file_path']}] (유사도: {doc['score']:.3f})")
                print(f"   {doc['content'][:100]}...")
            
            # 2. 컨텍스트 생성
            context = create_context_from_documents(documents)
            
            # 3. GPT4All로 응답 생성
            print("\n[응답 생성 중...]")
            try:
                response = query_with_gpt4all(query, context)
                print(f"\n[AI 응답]\n{response}\n")
            except Exception as e:
                print(f"GPT4All 응답 생성 오류: {e}")
                print("검색 결과만 표시합니다.\n")
            
            print("-" * 60)
            
        except KeyboardInterrupt:
            print("\n\n종료합니다.")
            break
        except Exception as e:
            print(f"오류 발생: {e}\n")


def simple_search(query: str, use_gpt4all: bool = False):
    """단순 검색 모드"""
    print(f"검색 쿼리: {query}\n")
    
    # 문서 검색
    documents = search_documents(query, top_k=5)
    
    if not documents:
        print("관련 문서를 찾을 수 없습니다.")
        return
    
    # 검색 결과 출력
    print(f"[검색 결과] {len(documents)}개의 관련 문서:\n")
    for i, doc in enumerate(documents, 1):
        print(f"{i}. [{doc['file_path']}] (유사도: {doc['score']:.3f})")
        print(f"   {doc['content']}\n")
    
    # GPT4All 응답 생성 (옵션)
    if use_gpt4all:
        context = create_context_from_documents(documents)
        print("[AI 응답 생성 중...]")
        try:
            response = query_with_gpt4all(query, context)
            print(f"\n{response}\n")
        except Exception as e:
            print(f"GPT4All 응답 생성 오류: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 명령줄 인자로 쿼리 전달
        query = " ".join(sys.argv[1:])
        use_gpt4all = "--gpt4all" in sys.argv or "-g" in sys.argv
        simple_search(query, use_gpt4all)
    else:
        # 대화형 모드
        interactive_search()

