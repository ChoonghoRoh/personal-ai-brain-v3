#!/usr/bin/env python3
"""Phase 8-2-1: current-state.md를 PostgreSQL에 저장"""
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from backend.models.database import get_db

def save_current_state():
    """current-state.md를 PostgreSQL에 저장"""
    current_state_file = project_root / "docs" / "phases" / "current-state.md"
    
    if not current_state_file.exists():
        print(f"❌ 오류: {current_state_file} 파일이 없습니다.")
        return False
    
    # 파일 읽기
    with open(current_state_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # DB 세션 생성
    db = next(get_db())
    
    try:
        # 기존 레코드 확인
        result = db.execute(text("""
            SELECT id FROM workflow_phases 
            WHERE phase_name = 'Phase-8-Current-State'
        """))
        existing = result.fetchone()
        
        if existing:
            # 업데이트
            db.execute(text("""
                UPDATE workflow_phases 
                SET current_state_md = :content,
                    status = 'completed'
                WHERE phase_name = 'Phase-8-Current-State'
            """), {"content": content})
            print(f"✅ 기존 레코드 업데이트: ID {existing[0]}")
        else:
            # 새로 생성
            result = db.execute(text("""
                INSERT INTO workflow_phases (phase_name, status, current_state_md, created_at)
                VALUES ('Phase-8-Current-State', 'completed', :content, NOW())
                RETURNING id
            """), {"content": content})
            new_id = result.fetchone()[0]
            print(f"✅ 새 레코드 생성: ID {new_id}")
        
        db.commit()
        print(f"✅ PostgreSQL 저장 완료")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ 오류: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = save_current_state()
    sys.exit(0 if success else 1)
