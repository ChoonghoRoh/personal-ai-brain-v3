#!/usr/bin/env python3
"""
Label 테이블의 name unique 제약조건 수정
- 기존: name만 unique (다른 label_type과 이름 충돌 가능)
- 수정: (name, label_type) 복합 unique 제약조건
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import DATABASE_URL
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError


def fix_label_unique_constraint():
    """Label 테이블의 unique 제약조건 수정"""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        try:
            print("=" * 60)
            print("🔧 Label 테이블 unique 제약조건 수정 시작")
            print("=" * 60)
            
            # 1. 기존 unique 제약조건 확인 및 제거
            print("\n📝 기존 unique 제약조건 확인 중...")
            try:
                # PostgreSQL에서 unique 제약조건 찾기
                result = conn.execute(text("""
                    SELECT constraint_name 
                    FROM information_schema.table_constraints 
                    WHERE table_name = 'labels' 
                    AND constraint_type = 'UNIQUE'
                    AND constraint_name LIKE '%name%'
                """))
                constraints = result.fetchall()
                
                if constraints:
                    for constraint in constraints:
                        constraint_name = constraint[0]
                        print(f"  발견된 제약조건: {constraint_name}")
                        try:
                            conn.execute(text(f"""
                                ALTER TABLE labels 
                                DROP CONSTRAINT IF EXISTS {constraint_name}
                            """))
                            conn.commit()
                            print(f"  ✅ 제약조건 제거: {constraint_name}")
                        except Exception as e:
                            print(f"  ⚠️ 제약조건 제거 중 오류: {e}")
                            conn.rollback()
                else:
                    print("  ℹ️ name 관련 unique 제약조건을 찾을 수 없습니다 (인덱스로 관리될 수 있음)")
            except Exception as e:
                print(f"  ⚠️ 제약조건 확인 중 오류: {e}")
            
            # 2. 기존 unique 인덱스 확인 및 제거
            print("\n📝 기존 unique 인덱스 확인 중...")
            try:
                result = conn.execute(text("""
                    SELECT indexname 
                    FROM pg_indexes 
                    WHERE tablename = 'labels' 
                    AND indexdef LIKE '%UNIQUE%'
                    AND indexdef LIKE '%name%'
                """))
                indexes = result.fetchall()
                
                if indexes:
                    for index in indexes:
                        index_name = index[0]
                        print(f"  발견된 인덱스: {index_name}")
                        try:
                            conn.execute(text(f"""
                                DROP INDEX IF EXISTS {index_name}
                            """))
                            conn.commit()
                            print(f"  ✅ 인덱스 제거: {index_name}")
                        except Exception as e:
                            print(f"  ⚠️ 인덱스 제거 중 오류: {e}")
                            conn.rollback()
                else:
                    print("  ℹ️ name 관련 unique 인덱스를 찾을 수 없습니다")
            except Exception as e:
                print(f"  ⚠️ 인덱스 확인 중 오류: {e}")
            
            # 3. name 단일 인덱스는 유지 (검색 성능을 위해)
            print("\n📝 name 인덱스 확인 중...")
            try:
                result = conn.execute(text("""
                    SELECT indexname 
                    FROM pg_indexes 
                    WHERE tablename = 'labels' 
                    AND indexname LIKE '%name%'
                    AND indexdef NOT LIKE '%UNIQUE%'
                """))
                indexes = result.fetchall()
                
                if not indexes:
                    # name 인덱스가 없으면 생성 (unique가 아닌 일반 인덱스)
                    try:
                        conn.execute(text("""
                            CREATE INDEX IF NOT EXISTS idx_labels_name 
                            ON labels(name)
                        """))
                        conn.commit()
                        print("  ✅ name 인덱스 생성 완료")
                    except Exception as e:
                        print(f"  ⚠️ name 인덱스 생성 중 오류: {e}")
                        conn.rollback()
                else:
                    print("  ℹ️ name 인덱스가 이미 존재합니다")
            except Exception as e:
                print(f"  ⚠️ 인덱스 확인 중 오류: {e}")
            
            # 4. (name, label_type) 복합 unique 제약조건 추가
            print("\n📝 (name, label_type) 복합 unique 제약조건 추가 중...")
            try:
                conn.execute(text("""
                    ALTER TABLE labels 
                    ADD CONSTRAINT labels_name_label_type_unique 
                    UNIQUE (name, label_type)
                """))
                conn.commit()
                print("  ✅ (name, label_type) 복합 unique 제약조건 추가 완료")
            except ProgrammingError as e:
                if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                    print("  ℹ️ 제약조건이 이미 존재합니다")
                else:
                    print(f"  ⚠️ 제약조건 추가 중 오류: {e}")
                    conn.rollback()
                    raise
            
            # 5. 복합 인덱스 추가 (성능 향상)
            print("\n📝 (name, label_type) 복합 인덱스 추가 중...")
            try:
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_labels_name_label_type 
                    ON labels(name, label_type)
                """))
                conn.commit()
                print("  ✅ (name, label_type) 복합 인덱스 추가 완료")
            except Exception as e:
                print(f"  ⚠️ 인덱스 추가 중 오류 (이미 존재할 수 있음): {e}")
                conn.rollback()
            
            print("\n" + "=" * 60)
            print("✅ Label 테이블 unique 제약조건 수정 완료!")
            print("=" * 60)
            print("\n💡 이제 같은 이름의 라벨이 다른 label_type으로 존재할 수 있습니다.")
            print("   예: name='AI', label_type='keyword' 와 name='AI', label_type='keyword_group'")
            
        except Exception as e:
            print(f"\n❌ 오류 발생: {e}")
            conn.rollback()
            raise


if __name__ == "__main__":
    fix_label_unique_constraint()

