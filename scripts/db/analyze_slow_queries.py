#!/usr/bin/env python3
"""
느린 쿼리 분석 및 모니터링 스크립트
"""
import time
import sys
from pathlib import Path
from typing import List, Dict
from sqlalchemy import event, text
from sqlalchemy.engine import Engine

# 프로젝트 루트 경로 설정
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.models.database import engine, SessionLocal
from backend.models.models import KnowledgeChunk, Document, Project, Label, KnowledgeLabel, KnowledgeRelation


class QueryMonitor:
    """쿼리 모니터링 클래스"""
    
    def __init__(self, slow_query_threshold: float = 0.1):
        self.slow_queries = []
        self.slow_query_threshold = slow_query_threshold
        self.query_count = 0
        self.total_time = 0.0
    
    def log_query(self, statement, parameters, duration):
        """쿼리 로깅"""
        self.query_count += 1
        self.total_time += duration
        
        if duration >= self.slow_query_threshold:
            self.slow_queries.append({
                'statement': str(statement),
                'parameters': str(parameters),
                'duration': duration
            })
    
    def get_stats(self) -> Dict:
        """통계 반환"""
        return {
            'total_queries': self.query_count,
            'total_time': self.total_time,
            'avg_time': self.total_time / self.query_count if self.query_count > 0 else 0,
            'slow_queries_count': len(self.slow_queries),
            'slow_query_threshold': self.slow_query_threshold
        }
    
    def print_slow_queries(self, limit: int = 10):
        """느린 쿼리 출력"""
        sorted_queries = sorted(self.slow_queries, key=lambda x: x['duration'], reverse=True)
        
        print(f"\n{'='*60}")
        print(f"느린 쿼리 (임계값: {self.slow_query_threshold*1000:.2f}ms)")
        print(f"{'='*60}\n")
        
        for i, query in enumerate(sorted_queries[:limit], 1):
            print(f"[{i}] 소요 시간: {query['duration']*1000:.2f}ms")
            print(f"쿼리: {query['statement'][:200]}...")
            if query['parameters']:
                print(f"파라미터: {query['parameters']}")
            print()


# 전역 모니터 인스턴스
monitor = QueryMonitor(slow_query_threshold=0.1)  # 100ms 이상


@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """쿼리 실행 전 이벤트"""
    conn.info.setdefault('query_start_time', []).append(time.time())


@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """쿼리 실행 후 이벤트"""
    total = conn.info['query_start_time'].pop(-1)
    duration = time.time() - total
    monitor.log_query(statement, parameters, duration)


def analyze_query_plans():
    """쿼리 실행 계획 분석"""
    print(f"\n{'='*60}")
    print("쿼리 실행 계획 분석")
    print(f"{'='*60}\n")
    
    db = SessionLocal()
    try:
        # 자주 사용되는 쿼리 패턴 분석
        
        # 1. KnowledgeChunk 조회 (status 필터)
        print("[1] KnowledgeChunk 조회 (status='approved')")
        result = db.execute(text("""
            EXPLAIN ANALYZE
            SELECT * FROM knowledge_chunks 
            WHERE status = 'approved' 
            LIMIT 100
        """))
        for row in result:
            print(f"  {row[0]}")
        print()
        
        # 2. KnowledgeChunk 조회 (document_id 필터)
        print("[2] KnowledgeChunk 조회 (document_id 필터)")
        result = db.execute(text("""
            EXPLAIN ANALYZE
            SELECT * FROM knowledge_chunks 
            WHERE document_id = 1
        """))
        for row in result:
            print(f"  {row[0]}")
        print()
        
        # 3. KnowledgeLabel 조인 쿼리
        print("[3] KnowledgeLabel 조인 쿼리")
        result = db.execute(text("""
            EXPLAIN ANALYZE
            SELECT kc.* FROM knowledge_chunks kc
            JOIN knowledge_labels kl ON kc.id = kl.chunk_id
            WHERE kl.label_id = 1
            LIMIT 100
        """))
        for row in result:
            print(f"  {row[0]}")
        print()
        
        # 4. KnowledgeRelation 조회
        print("[4] KnowledgeRelation 조회 (source_chunk_id)")
        result = db.execute(text("""
            EXPLAIN ANALYZE
            SELECT * FROM knowledge_relations 
            WHERE source_chunk_id = 1
        """))
        for row in result:
            print(f"  {row[0]}")
        print()
        
    finally:
        db.close()


def check_indexes():
    """인덱스 확인"""
    print(f"\n{'='*60}")
    print("인덱스 확인")
    print(f"{'='*60}\n")
    
    db = SessionLocal()
    try:
        result = db.execute(text("""
            SELECT 
                tablename,
                indexname,
                indexdef
            FROM pg_indexes
            WHERE schemaname = 'public'
            ORDER BY tablename, indexname
        """))
        
        current_table = None
        for row in result:
            table, index, definition = row
            if table != current_table:
                if current_table is not None:
                    print()
                print(f"[{table}]")
                current_table = table
            print(f"  {index}")
            print(f"    {definition}")
        
    finally:
        db.close()


def main():
    """메인 함수"""
    print("=" * 60)
    print("데이터베이스 쿼리 분석 도구")
    print("=" * 60)
    
    # 1. 인덱스 확인
    check_indexes()
    
    # 2. 쿼리 실행 계획 분석
    analyze_query_plans()
    
    # 3. 통계 출력
    stats = monitor.get_stats()
    print(f"\n{'='*60}")
    print("쿼리 통계")
    print(f"{'='*60}")
    print(f"총 쿼리 수: {stats['total_queries']}")
    print(f"총 소요 시간: {stats['total_time']*1000:.2f}ms")
    print(f"평균 소요 시간: {stats['avg_time']*1000:.2f}ms")
    print(f"느린 쿼리 수: {stats['slow_queries_count']}")
    
    # 4. 느린 쿼리 출력
    if monitor.slow_queries:
        monitor.print_slow_queries(limit=10)
    
    print("\n분석 완료!")


if __name__ == "__main__":
    main()
