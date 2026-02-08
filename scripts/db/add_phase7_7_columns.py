#!/usr/bin/env python3
"""
Phase 7.7 DB 스키마 확장 스크립트
- labels 테이블에 parent_label_id, color, updated_at 추가
- documents 테이블에 category_label_id 추가
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import DATABASE_URL
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError


def add_phase7_7_columns():
    """Phase 7.7 컬럼 추가"""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        try:
            # labels 테이블 확장
            print("📝 labels 테이블에 컬럼 추가 중...")
            
            # parent_label_id 추가
            try:
                conn.execute(text("""
                    ALTER TABLE labels 
                    ADD COLUMN IF NOT EXISTS parent_label_id INTEGER REFERENCES labels(id)
                """))
                conn.commit()
                print("  ✅ parent_label_id 추가 완료")
            except ProgrammingError as e:
                if "already exists" not in str(e).lower():
                    print(f"  ⚠️ parent_label_id 추가 중 오류 (이미 존재할 수 있음): {e}")
                conn.rollback()
            
            # color 추가
            try:
                conn.execute(text("""
                    ALTER TABLE labels 
                    ADD COLUMN IF NOT EXISTS color VARCHAR
                """))
                conn.commit()
                print("  ✅ color 추가 완료")
            except ProgrammingError as e:
                if "already exists" not in str(e).lower():
                    print(f"  ⚠️ color 추가 중 오류 (이미 존재할 수 있음): {e}")
                conn.rollback()
            
            # updated_at 추가
            try:
                conn.execute(text("""
                    ALTER TABLE labels 
                    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                """))
                conn.commit()
                print("  ✅ updated_at 추가 완료")
            except ProgrammingError as e:
                if "already exists" not in str(e).lower():
                    print(f"  ⚠️ updated_at 추가 중 오류 (이미 존재할 수 있음): {e}")
                conn.rollback()
            
            # parent_label_id 인덱스 추가
            try:
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_labels_parent_label_id ON labels(parent_label_id)
                """))
                conn.commit()
                print("  ✅ parent_label_id 인덱스 추가 완료")
            except ProgrammingError as e:
                print(f"  ⚠️ 인덱스 추가 중 오류 (이미 존재할 수 있음): {e}")
                conn.rollback()
            
            # label_type 인덱스 추가 (없는 경우)
            try:
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_labels_label_type ON labels(label_type)
                """))
                conn.commit()
                print("  ✅ label_type 인덱스 추가 완료")
            except ProgrammingError as e:
                print(f"  ⚠️ 인덱스 추가 중 오류 (이미 존재할 수 있음): {e}")
                conn.rollback()
            
            # documents 테이블 확장
            print("\n📝 documents 테이블에 컬럼 추가 중...")
            
            # category_label_id 추가
            try:
                conn.execute(text("""
                    ALTER TABLE documents 
                    ADD COLUMN IF NOT EXISTS category_label_id INTEGER REFERENCES labels(id)
                """))
                conn.commit()
                print("  ✅ category_label_id 추가 완료")
            except ProgrammingError as e:
                if "already exists" not in str(e).lower():
                    print(f"  ⚠️ category_label_id 추가 중 오류 (이미 존재할 수 있음): {e}")
                conn.rollback()
            
            # category_label_id 인덱스 추가
            try:
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_documents_category_label_id ON documents(category_label_id)
                """))
                conn.commit()
                print("  ✅ category_label_id 인덱스 추가 완료")
            except ProgrammingError as e:
                print(f"  ⚠️ 인덱스 추가 중 오류 (이미 존재할 수 있음): {e}")
                conn.rollback()
            
            print("\n✅ Phase 7.7 DB 스키마 확장 완료!")
            
        except Exception as e:
            print(f"\n❌ 오류 발생: {e}")
            conn.rollback()
            raise


if __name__ == "__main__":
    add_phase7_7_columns()

