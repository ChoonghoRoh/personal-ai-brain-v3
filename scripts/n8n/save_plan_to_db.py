#!/usr/bin/env python3
"""Phase 8-2-3: phase-8-plan.md를 PostgreSQL에 저장"""
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from backend.models.database import get_db

def save_plan():
    """phase-8-plan.md를 PostgreSQL에 저장"""
    plan_file = project_root / "docs" / "phases" / "phase-8-plan.md"
    
    if not plan_file.exists():
        print(f"❌ 오류: {plan_file} 파일이 없습니다.")
        return False
    
    with open(plan_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    db = next(get_db())
    
    try:
        # phase_id 조회
        phase_result = db.execute(text("""
            SELECT id FROM workflow_phases 
            WHERE phase_name = 'Phase-8-Current-State'
        """))
        phase_row = phase_result.fetchone()
        
        if not phase_row:
            print("❌ 오류: Phase-8-Current-State 레코드를 찾을 수 없습니다.")
            return False
        
        phase_id = phase_row[0]
        
        # 기존 plan 확인
        plan_result = db.execute(text("""
            SELECT id FROM workflow_plans 
            WHERE phase_id = :phase_id AND version = 1
        """), {"phase_id": phase_id})
        existing = plan_result.fetchone()
        
        if existing:
            # 업데이트
            db.execute(text("""
                UPDATE workflow_plans 
                SET content = :content,
                    status = 'draft'
                WHERE phase_id = :phase_id AND version = 1
            """), {"content": content, "phase_id": phase_id})
            print(f"✅ 기존 Plan 업데이트: ID {existing[0]}")
        else:
            # 새로 생성
            result = db.execute(text("""
                INSERT INTO workflow_plans (phase_id, version, content, status, created_at)
                VALUES (:phase_id, 1, :content, 'draft', NOW())
                RETURNING id
            """), {"phase_id": phase_id, "content": content})
            new_id = result.fetchone()[0]
            print(f"✅ 새 Plan 생성: ID {new_id}")
        
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
    success = save_plan()
    sys.exit(0 if success else 1)
