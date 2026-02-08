"""데이터 무결성 서비스"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from qdrant_client import QdrantClient

from backend.config import QDRANT_HOST, QDRANT_PORT, COLLECTION_NAME
from backend.models.models import KnowledgeChunk, Document, KnowledgeLabel, KnowledgeRelation


class IntegrityService:
    """데이터 무결성 서비스 클래스"""
    
    def __init__(self):
        self.qdrant_client = None
        self._initialize()
    
    def _initialize(self):
        """초기화"""
        try:
            self.qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        except Exception as e:
            print(f"Qdrant 클라이언트 초기화 오류: {e}")
    
    def check_qdrant_postgresql_sync(self, db: Session) -> Dict:
        """Qdrant-PostgreSQL 동기화 확인"""
        issues = []
        
        try:
            # Qdrant 포인트 수
            collection_info = self.qdrant_client.get_collection(COLLECTION_NAME)
            qdrant_count = collection_info.points_count
            
            # PostgreSQL 청크 수
            pg_count = db.query(KnowledgeChunk).count()
            
            if qdrant_count != pg_count:
                issues.append({
                    'type': 'count_mismatch',
                    'severity': 'high',
                    'message': f'Qdrant 포인트 수({qdrant_count})와 PostgreSQL 청크 수({pg_count})가 일치하지 않습니다.',
                    'qdrant_count': qdrant_count,
                    'pg_count': pg_count
                })
            
            # 개별 청크 검증
            chunks_with_qdrant_id = db.query(KnowledgeChunk).filter(
                KnowledgeChunk.qdrant_point_id.isnot(None)
            ).all()
            
            missing_in_qdrant = []
            for chunk in chunks_with_qdrant_id:
                try:
                    point = self.qdrant_client.retrieve(
                        collection_name=COLLECTION_NAME,
                        ids=[chunk.qdrant_point_id]
                    )
                    if not point:
                        missing_in_qdrant.append(chunk.id)
                except:
                    missing_in_qdrant.append(chunk.id)
            
            if missing_in_qdrant:
                issues.append({
                    'type': 'missing_in_qdrant',
                    'severity': 'high',
                    'message': f'PostgreSQL에 있지만 Qdrant에 없는 청크: {len(missing_in_qdrant)}개',
                    'chunk_ids': missing_in_qdrant[:10]  # 최대 10개만
                })
            
            return {
                'synced': len(issues) == 0,
                'issues': issues,
                'qdrant_count': qdrant_count,
                'pg_count': pg_count
            }
        except Exception as e:
            return {
                'synced': False,
                'issues': [{
                    'type': 'error',
                    'severity': 'critical',
                    'message': f'동기화 확인 중 오류: {str(e)}'
                }],
                'error': str(e)
            }
    
    def check_data_consistency(self, db: Session) -> Dict:
        """데이터 일관성 검증"""
        issues = []
        
        # 1. 청크-문서 관계 검증
        chunks_without_doc = db.query(KnowledgeChunk).filter(
            ~KnowledgeChunk.document_id.in_(
                db.query(Document.id)
            )
        ).all()
        
        if chunks_without_doc:
            issues.append({
                'type': 'orphan_chunk',
                'severity': 'medium',
                'message': f'문서가 없는 청크: {len(chunks_without_doc)}개',
                'chunk_ids': [c.id for c in chunks_without_doc[:10]]
            })
        
        # 2. 라벨-청크 관계 검증
        labels_without_chunk = db.query(KnowledgeLabel).filter(
            ~KnowledgeLabel.chunk_id.in_(
                db.query(KnowledgeChunk.id)
            )
        ).all()
        
        if labels_without_chunk:
            issues.append({
                'type': 'orphan_label',
                'severity': 'low',
                'message': f'청크가 없는 라벨 관계: {len(labels_without_chunk)}개',
                'label_ids': [l.id for l in labels_without_chunk[:10]]
            })
        
        # 3. 관계-청크 검증
        relations_without_source = db.query(KnowledgeRelation).filter(
            ~KnowledgeRelation.source_chunk_id.in_(
                db.query(KnowledgeChunk.id)
            )
        ).all()
        
        relations_without_target = db.query(KnowledgeRelation).filter(
            ~KnowledgeRelation.target_chunk_id.in_(
                db.query(KnowledgeChunk.id)
            )
        ).all()
        
        if relations_without_source or relations_without_target:
            issues.append({
                'type': 'orphan_relation',
                'severity': 'medium',
                'message': f'청크가 없는 관계: 소스 {len(relations_without_source)}개, 타겟 {len(relations_without_target)}개',
                'relation_ids': [
                    r.id for r in (relations_without_source + relations_without_target)[:10]
                ]
            })
        
        return {
            'consistent': len(issues) == 0,
            'issues': issues
        }
    
    def fix_orphan_chunks(self, db: Session) -> int:
        """고아 청크 수정 (문서가 없는 청크 삭제)"""
        chunks_to_delete = db.query(KnowledgeChunk).filter(
            ~KnowledgeChunk.document_id.in_(
                db.query(Document.id)
            )
        ).all()
        
        count = len(chunks_to_delete)
        for chunk in chunks_to_delete:
            db.delete(chunk)
        
        db.commit()
        return count
    
    def fix_orphan_labels(self, db: Session) -> int:
        """고아 라벨 관계 수정"""
        labels_to_delete = db.query(KnowledgeLabel).filter(
            ~KnowledgeLabel.chunk_id.in_(
                db.query(KnowledgeChunk.id)
            )
        ).all()
        
        count = len(labels_to_delete)
        for label in labels_to_delete:
            db.delete(label)
        
        db.commit()
        return count
    
    def fix_orphan_relations(self, db: Session) -> int:
        """고아 관계 수정"""
        relations_to_delete = db.query(KnowledgeRelation).filter(
            (
                ~KnowledgeRelation.source_chunk_id.in_(db.query(KnowledgeChunk.id)) |
                ~KnowledgeRelation.target_chunk_id.in_(db.query(KnowledgeChunk.id))
            )
        ).all()
        
        count = len(relations_to_delete)
        for relation in relations_to_delete:
            db.delete(relation)
        
        db.commit()
        return count
    
    def validate_all(self, db: Session) -> Dict:
        """전체 검증"""
        sync_result = self.check_qdrant_postgresql_sync(db)
        consistency_result = self.check_data_consistency(db)
        
        all_issues = sync_result.get('issues', []) + consistency_result.get('issues', [])
        
        return {
            'synced': sync_result.get('synced', False),
            'consistent': consistency_result.get('consistent', False),
            'total_issues': len(all_issues),
            'issues': all_issues,
            'sync_info': {
                'qdrant_count': sync_result.get('qdrant_count', 0),
                'pg_count': sync_result.get('pg_count', 0)
            }
        }


# 싱글톤 인스턴스
_integrity_service = None

def get_integrity_service() -> IntegrityService:
    """무결성 서비스 인스턴스 가져오기"""
    global _integrity_service
    if _integrity_service is None:
        _integrity_service = IntegrityService()
    return _integrity_service
