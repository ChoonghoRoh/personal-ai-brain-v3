#!/usr/bin/env python3
"""
Phase 7 Upgrade DB 마이그레이션 스크립트
기존 데이터에 새 필드의 기본값 설정
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import text
from backend.models.database import engine, SessionLocal
from backend.models.models import KnowledgeChunk, KnowledgeLabel, KnowledgeRelation


def migrate_chunks():
    """KnowledgeChunk 테이블 마이그레이션"""
    db = SessionLocal()
    try:
        # Phase 7.9.5: title 컬럼 추가 (PostgreSQL 호환)
        try:
            # 컬럼 존재 여부 확인
            result = db.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='knowledge_chunks' AND column_name='title'
            """))
            if not result.fetchone():
                db.execute(text("ALTER TABLE knowledge_chunks ADD COLUMN title VARCHAR"))
                db.commit()
                print("✅ title 컬럼 추가 완료")
            else:
                print("ℹ️  title 컬럼이 이미 존재합니다")
        except Exception as e:
            print(f"⚠️ title 컬럼 추가 중 오류: {e}")
            db.rollback()
        
        # Phase 7.9.5: title_source 컬럼 추가
        try:
            result = db.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='knowledge_chunks' AND column_name='title_source'
            """))
            if not result.fetchone():
                db.execute(text("ALTER TABLE knowledge_chunks ADD COLUMN title_source VARCHAR"))
                db.commit()
                print("✅ title_source 컬럼 추가 완료")
            else:
                print("ℹ️  title_source 컬럼이 이미 존재합니다")
        except Exception as e:
            print(f"⚠️ title_source 컬럼 추가 중 오류: {e}")
            db.rollback()
        
        # 기존 청크에 기본값 설정
        db.execute(text("""
            UPDATE knowledge_chunks 
            SET 
                status = COALESCE(status, 'draft'),
                source = COALESCE(source, 'human_created'),
                version = COALESCE(version, 1)
            WHERE status IS NULL OR source IS NULL OR version IS NULL
        """))
        db.commit()
        print("✅ KnowledgeChunk 마이그레이션 완료")
    except Exception as e:
        print(f"⚠️ KnowledgeChunk 마이그레이션 중 오류 (이미 마이그레이션되었을 수 있음): {e}")
        db.rollback()
    finally:
        db.close()


def migrate_labels():
    """KnowledgeLabel 테이블 마이그레이션"""
    db = SessionLocal()
    try:
        # 기존 라벨에 기본값 설정
        db.execute(text("""
            UPDATE knowledge_labels 
            SET 
                status = COALESCE(status, 'confirmed'),
                source = COALESCE(source, 'human')
            WHERE status IS NULL OR source IS NULL
        """))
        db.commit()
        print("✅ KnowledgeLabel 마이그레이션 완료")
    except Exception as e:
        print(f"⚠️ KnowledgeLabel 마이그레이션 중 오류 (이미 마이그레이션되었을 수 있음): {e}")
        db.rollback()
    finally:
        db.close()


def migrate_relations():
    """KnowledgeRelation 테이블 마이그레이션"""
    db = SessionLocal()
    try:
        # 기존 관계에 기본값 설정
        db.execute(text("""
            UPDATE knowledge_relations 
            SET 
                confirmed = COALESCE(confirmed, 'true'),
                source = COALESCE(source, 'human')
            WHERE confirmed IS NULL OR source IS NULL
        """))
        db.commit()
        print("✅ KnowledgeRelation 마이그레이션 완료")
    except Exception as e:
        print(f"⚠️ KnowledgeRelation 마이그레이션 중 오류 (이미 마이그레이션되었을 수 있음): {e}")
        db.rollback()
    finally:
        db.close()


def main():
    print("🔄 Phase 7 Upgrade DB 마이그레이션 시작...")
    print()
    
    migrate_chunks()
    migrate_labels()
    migrate_relations()
    
    print()
    print("✅ 마이그레이션 완료!")
    print("💡 서버를 재시작하면 변경사항이 적용됩니다.")


if __name__ == "__main__":
    main()

