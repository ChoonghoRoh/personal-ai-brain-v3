#!/usr/bin/env python3
"""
Qdrant와 PostgreSQL 간 데이터 일관성 확인 스크립트
"""
import sys
from pathlib import Path
from qdrant_client import QdrantClient

# 프로젝트 루트 경로 설정
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import QDRANT_HOST, QDRANT_PORT, COLLECTION_NAME, DATABASE_URL
from backend.models.database import SessionLocal
from backend.models.models import KnowledgeChunk
from sqlalchemy import text

def check_data_sync():
    """데이터 일관성 확인"""
    print("=" * 60)
    print("데이터 일관성 확인")
    print("=" * 60)
    
    # Qdrant 연결
    print("\n[1/3] Qdrant 연결 중...")
    try:
        qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        collection_info = qdrant_client.get_collection(COLLECTION_NAME)
        qdrant_count = collection_info.points_count
        print(f"✅ Qdrant 포인트 수: {qdrant_count}")
    except Exception as e:
        print(f"❌ Qdrant 연결 실패: {e}")
        return False
    
    # PostgreSQL 연결
    print("\n[2/3] PostgreSQL 연결 중...")
    try:
        db = SessionLocal()
        pg_count = db.query(KnowledgeChunk).count()
        print(f"✅ PostgreSQL 청크 수: {pg_count}")
        db.close()
    except Exception as e:
        print(f"❌ PostgreSQL 연결 실패: {e}")
        return False
    
    # 일관성 확인
    print("\n[3/3] 데이터 일관성 확인...")
    print(f"  Qdrant 포인트 수: {qdrant_count}")
    print(f"  PostgreSQL 청크 수: {pg_count}")
    
    if qdrant_count == pg_count:
        print("\n✅ 데이터 일관성 확인됨!")
        return True
    else:
        diff = abs(qdrant_count - pg_count)
        print(f"\n⚠️ 데이터 불일치 발견!")
        print(f"  차이: {diff}개")
        if qdrant_count > pg_count:
            print(f"  Qdrant에 {diff}개 더 많음 (PostgreSQL 동기화 필요)")
        else:
            print(f"  PostgreSQL에 {diff}개 더 많음 (Qdrant 동기화 필요)")
        print("\n해결 방법:")
        print("  python scripts/embed_and_store.py")
        return False


if __name__ == "__main__":
    success = check_data_sync()
    sys.exit(0 if success else 1)

