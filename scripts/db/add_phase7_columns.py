#!/usr/bin/env python3
"""
Phase 7 Upgrade 컬럼 추가 스크립트
기존 테이블에 새 컬럼 추가
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import text
from backend.models.database import engine, SessionLocal


def add_columns():
    """필요한 컬럼 추가"""
    db = SessionLocal()
    try:
        # KnowledgeChunk 테이블에 컬럼 추가
        print("🔄 knowledge_chunks 테이블에 컬럼 추가 중...")
        
        try:
            db.execute(text("""
                ALTER TABLE knowledge_chunks 
                ADD COLUMN IF NOT EXISTS status VARCHAR DEFAULT 'draft' NOT NULL
            """))
            print("  ✅ status 컬럼 추가")
        except Exception as e:
            print(f"  ⚠️ status 컬럼 추가 중 오류 (이미 존재할 수 있음): {e}")
        
        try:
            db.execute(text("""
                ALTER TABLE knowledge_chunks 
                ADD COLUMN IF NOT EXISTS source VARCHAR DEFAULT 'human_created' NOT NULL
            """))
            print("  ✅ source 컬럼 추가")
        except Exception as e:
            print(f"  ⚠️ source 컬럼 추가 중 오류 (이미 존재할 수 있음): {e}")
        
        try:
            db.execute(text("""
                ALTER TABLE knowledge_chunks 
                ADD COLUMN IF NOT EXISTS approved_at TIMESTAMP
            """))
            print("  ✅ approved_at 컬럼 추가")
        except Exception as e:
            print(f"  ⚠️ approved_at 컬럼 추가 중 오류 (이미 존재할 수 있음): {e}")
        
        try:
            db.execute(text("""
                ALTER TABLE knowledge_chunks 
                ADD COLUMN IF NOT EXISTS approved_by VARCHAR
            """))
            print("  ✅ approved_by 컬럼 추가")
        except Exception as e:
            print(f"  ⚠️ approved_by 컬럼 추가 중 오류 (이미 존재할 수 있음): {e}")
        
        try:
            db.execute(text("""
                ALTER TABLE knowledge_chunks 
                ADD COLUMN IF NOT EXISTS version INTEGER DEFAULT 1 NOT NULL
            """))
            print("  ✅ version 컬럼 추가")
        except Exception as e:
            print(f"  ⚠️ version 컬럼 추가 중 오류 (이미 존재할 수 있음): {e}")
        
        # 인덱스 추가
        try:
            db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_status 
                ON knowledge_chunks(status)
            """))
            print("  ✅ status 인덱스 추가")
        except Exception as e:
            print(f"  ⚠️ status 인덱스 추가 중 오류: {e}")
        
        # KnowledgeLabel 테이블에 컬럼 추가
        print("\n🔄 knowledge_labels 테이블에 컬럼 추가 중...")
        
        try:
            db.execute(text("""
                ALTER TABLE knowledge_labels 
                ADD COLUMN IF NOT EXISTS status VARCHAR DEFAULT 'confirmed' NOT NULL
            """))
            print("  ✅ status 컬럼 추가")
        except Exception as e:
            print(f"  ⚠️ status 컬럼 추가 중 오류 (이미 존재할 수 있음): {e}")
        
        try:
            db.execute(text("""
                ALTER TABLE knowledge_labels 
                ADD COLUMN IF NOT EXISTS source VARCHAR DEFAULT 'human' NOT NULL
            """))
            print("  ✅ source 컬럼 추가")
        except Exception as e:
            print(f"  ⚠️ source 컬럼 추가 중 오류 (이미 존재할 수 있음): {e}")
        
        # 인덱스 추가
        try:
            db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_knowledge_labels_status 
                ON knowledge_labels(status)
            """))
            print("  ✅ status 인덱스 추가")
        except Exception as e:
            print(f"  ⚠️ status 인덱스 추가 중 오류: {e}")
        
        # KnowledgeRelation 테이블에 컬럼 추가
        print("\n🔄 knowledge_relations 테이블에 컬럼 추가 중...")
        
        try:
            db.execute(text("""
                ALTER TABLE knowledge_relations 
                ADD COLUMN IF NOT EXISTS score FLOAT
            """))
            print("  ✅ score 컬럼 추가")
        except Exception as e:
            print(f"  ⚠️ score 컬럼 추가 중 오류 (이미 존재할 수 있음): {e}")
        
        try:
            db.execute(text("""
                ALTER TABLE knowledge_relations 
                ADD COLUMN IF NOT EXISTS confirmed VARCHAR DEFAULT 'true' NOT NULL
            """))
            print("  ✅ confirmed 컬럼 추가")
        except Exception as e:
            print(f"  ⚠️ confirmed 컬럼 추가 중 오류 (이미 존재할 수 있음): {e}")
        
        try:
            db.execute(text("""
                ALTER TABLE knowledge_relations 
                ADD COLUMN IF NOT EXISTS source VARCHAR DEFAULT 'human' NOT NULL
            """))
            print("  ✅ source 컬럼 추가")
        except Exception as e:
            print(f"  ⚠️ source 컬럼 추가 중 오류 (이미 존재할 수 있음): {e}")
        
        db.commit()
        print("\n✅ 모든 컬럼 추가 완료!")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def main():
    print("=" * 60)
    print("🔄 Phase 7 Upgrade DB 컬럼 추가 시작")
    print("=" * 60)
    print()
    
    add_columns()
    
    print()
    print("=" * 60)
    print("✅ 마이그레이션 완료!")
    print("💡 서버를 재시작하면 변경사항이 적용됩니다.")
    print("=" * 60)


if __name__ == "__main__":
    main()

