#!/usr/bin/env python3
"""Phase 8-2-2: gap-analysis.md를 PostgreSQL에 업데이트"""
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from backend.models.database import get_db

def save_gap_analysis():
    """gap-analysis.md를 PostgreSQL에 업데이트"""
    gap_file = project_root / "docs" / "phases" / "gap-analysis.md"
    
    if not gap_file.exists():
        print(f"❌ 오류: {gap_file} 파일이 없습니다.")
        return False
    
    with open(gap_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    db = next(get_db())
    
    try:
        result = db.execute(text("""
            UPDATE workflow_phases 
            SET gap_analysis_md = :content,
                status = 'gap_analyzed'
            WHERE phase_name = 'Phase-8-Current-State'
            RETURNING id, phase_name, status
        """), {"content": content})
        
        updated = result.fetchone()
        if updated:
            print(f"✅ 업데이트 완료: ID {updated[0]}, Status: {updated[2]}")
        else:
            print("⚠️ 경고: 업데이트할 레코드가 없습니다. Phase-8-Current-State 레코드를 먼저 생성하세요.")
            return False
        
        db.commit()
        print(f"✅ PostgreSQL 업데이트 완료")
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
    success = save_gap_analysis()
    sys.exit(0 if success else 1)
