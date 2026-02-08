"""맥락 이해 및 연결 서비스"""
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_

from backend.models.models import KnowledgeChunk, Document, KnowledgeRelation, KnowledgeLabel
from backend.services.search.search_service import get_search_service
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity

from backend.config import EMBEDDING_MODEL


class ContextService:
    """맥락 이해 및 연결 서비스 클래스"""
    
    def __init__(self):
        self.model = None
        self._initialize()
    
    def _initialize(self):
        """초기화"""
        try:
            self.model = SentenceTransformer(EMBEDDING_MODEL)
        except Exception as e:
            print(f"맥락 서비스 초기화 오류: {e}")
    
    def calculate_semantic_similarity(
        self, 
        chunk1: KnowledgeChunk, 
        chunk2: KnowledgeChunk
    ) -> float:
        """두 청크 간 의미적 유사도 계산 (임베딩 기반)"""
        if not self.model:
            return 0.0
        
        try:
            # 임베딩 생성
            embedding1 = self.model.encode(chunk1.content)
            embedding2 = self.model.encode(chunk2.content)
            
            # 코사인 유사도 계산
            similarity = cosine_similarity(
                embedding1.reshape(1, -1),
                embedding2.reshape(1, -1)
            )[0][0]
            
            return float(similarity)
        except Exception as e:
            print(f"유사도 계산 오류: {e}")
            return 0.0
    
    def find_semantic_connections(
        self,
        db: Session,
        chunk: KnowledgeChunk,
        threshold: float = 0.7,
        limit: int = 10
    ) -> List[Dict]:
        """의미적으로 연결된 청크 찾기"""
        if not self.model:
            return []
        
        try:
            # 현재 청크의 임베딩
            chunk_embedding = self.model.encode(chunk.content).reshape(1, -1)
            
            # 모든 승인된 청크 조회 (최적화: 배치 처리)
            all_chunks = db.query(KnowledgeChunk).filter(
                KnowledgeChunk.status == "approved",
                KnowledgeChunk.id != chunk.id
            ).limit(1000).all()  # 성능을 위해 제한
            
            if not all_chunks:
                return []
            
            # 배치로 임베딩 생성
            contents = [c.content for c in all_chunks]
            embeddings = self.model.encode(contents)
            
            # 유사도 계산
            similarities = cosine_similarity(chunk_embedding, embeddings)[0]
            
            # 임계값 이상인 청크 선택
            connections = []
            for i, similarity in enumerate(similarities):
                if similarity >= threshold:
                    connections.append({
                        'chunk_id': all_chunks[i].id,
                        'chunk_content': all_chunks[i].content[:200],
                        'similarity': float(similarity),
                        'document_id': all_chunks[i].document_id
                    })
            
            # 유사도 순으로 정렬
            connections.sort(key=lambda x: x['similarity'], reverse=True)
            
            return connections[:limit]
        except Exception as e:
            print(f"의미적 연결 찾기 오류: {e}")
            return []
    
    def track_temporal_context(
        self,
        db: Session,
        chunk: KnowledgeChunk,
        time_window_days: int = 30
    ) -> Dict:
        """시간적 맥락 추적 (문서 작성 시점, 수정 시점 기반)"""
        try:
            # 문서 정보
            doc = db.query(Document).filter(Document.id == chunk.document_id).first()
            if not doc:
                return {}
            
            # 시간 범위 계산
            chunk_time = chunk.created_at or doc.created_at
            time_window_start = chunk_time - datetime.timedelta(days=time_window_days)
            time_window_end = chunk_time + datetime.timedelta(days=time_window_days)
            
            # 같은 시간대의 청크 찾기
            temporal_chunks = db.query(KnowledgeChunk).filter(
                and_(
                    KnowledgeChunk.status == "approved",
                    KnowledgeChunk.id != chunk.id,
                    KnowledgeChunk.created_at >= time_window_start,
                    KnowledgeChunk.created_at <= time_window_end
                )
            ).order_by(KnowledgeChunk.created_at).all()
            
            # 문서별 그룹화
            doc_chunks = {}
            for tc in temporal_chunks:
                doc_id = tc.document_id
                if doc_id not in doc_chunks:
                    doc_chunks[doc_id] = []
                doc_chunks[doc_id].append({
                    'chunk_id': tc.id,
                    'content': tc.content[:200],
                    'created_at': tc.created_at.isoformat() if tc.created_at else None
                })
            
            return {
                'chunk_time': chunk_time.isoformat() if chunk_time else None,
                'time_window_days': time_window_days,
                'temporal_chunks_count': len(temporal_chunks),
                'documents': doc_chunks
            }
        except Exception as e:
            print(f"시간적 맥락 추적 오류: {e}")
            return {}
    
    def cluster_by_topic(
        self,
        db: Session,
        chunks: List[KnowledgeChunk],
        n_clusters: int = 5
    ) -> Dict:
        """주제별 클러스터링"""
        if not self.model or not chunks:
            return {}
        
        try:
            # 임베딩 생성
            contents = [chunk.content for chunk in chunks]
            embeddings = self.model.encode(contents)
            
            # K-means 클러스터링
            kmeans = KMeans(n_clusters=min(n_clusters, len(chunks)), random_state=42)
            cluster_labels = kmeans.fit_predict(embeddings)
            
            # 클러스터별 그룹화
            clusters = {}
            for i, chunk in enumerate(chunks):
                cluster_id = int(cluster_labels[i])
                if cluster_id not in clusters:
                    clusters[cluster_id] = []
                clusters[cluster_id].append({
                    'chunk_id': chunk.id,
                    'content': chunk.content[:200],
                    'document_id': chunk.document_id
                })
            
            return {
                'n_clusters': len(clusters),
                'clusters': clusters
            }
        except Exception as e:
            print(f"클러스터링 오류: {e}")
            return {}
    
    def infer_hierarchy(
        self,
        db: Session,
        chunks: List[KnowledgeChunk]
    ) -> Dict:
        """문서 계층 구조 자동 추론 (상위-하위 개념)"""
        if not chunks:
            return {}
        
        try:
            # 라벨 기반 계층 구조 추론
            hierarchy = {
                'parent_chunks': [],
                'child_chunks': [],
                'sibling_chunks': []
            }
            
            # 각 청크의 라벨 수집
            chunk_labels = {}
            for chunk in chunks:
                labels = db.query(KnowledgeLabel).filter(
                    KnowledgeLabel.chunk_id == chunk.id
                ).all()
                chunk_labels[chunk.id] = [kl.label_id for kl in labels]
            
            # 라벨 기반 관계 추론
            for i, chunk1 in enumerate(chunks):
                labels1 = set(chunk_labels.get(chunk1.id, []))
                
                for chunk2 in chunks[i+1:]:
                    labels2 = set(chunk_labels.get(chunk2.id, []))
                    
                    # 상위-하위 관계 (라벨 포함 관계)
                    if labels1.issuperset(labels2) and len(labels1) > len(labels2):
                        hierarchy['parent_chunks'].append({
                            'parent_id': chunk1.id,
                            'child_id': chunk2.id
                        })
                    elif labels2.issuperset(labels1) and len(labels2) > len(labels1):
                        hierarchy['parent_chunks'].append({
                            'parent_id': chunk2.id,
                            'child_id': chunk1.id
                        })
                    # 형제 관계 (공통 라벨)
                    elif labels1 & labels2:
                        hierarchy['sibling_chunks'].append({
                            'chunk1_id': chunk1.id,
                            'chunk2_id': chunk2.id,
                            'common_labels': list(labels1 & labels2)
                        })
            
            return hierarchy
        except Exception as e:
            print(f"계층 구조 추론 오류: {e}")
            return {}
    
    def detect_references(
        self,
        db: Session,
        chunk: KnowledgeChunk
    ) -> List[Dict]:
        """참조 관계 자동 감지 및 추적"""
        try:
            references = []
            
            # 기존 관계에서 참조 관계 찾기
            relations = db.query(KnowledgeRelation).filter(
                and_(
                    KnowledgeRelation.source_chunk_id == chunk.id,
                    KnowledgeRelation.relation_type.in_(['refers-to', 'explains'])
                )
            ).all()
            
            for rel in relations:
                target = db.query(KnowledgeChunk).filter(
                    KnowledgeChunk.id == rel.target_chunk_id
                ).first()
                
                if target:
                    references.append({
                        'target_chunk_id': target.id,
                        'target_content': target.content[:200],
                        'relation_type': rel.relation_type,
                        'confidence': rel.confidence
                    })
            
            return references
        except Exception as e:
            print(f"참조 감지 오류: {e}")
            return []


# 싱글톤 인스턴스
_context_service = None

def get_context_service() -> ContextService:
    """맥락 서비스 인스턴스 가져오기"""
    global _context_service
    if _context_service is None:
        _context_service = ContextService()
    return _context_service
