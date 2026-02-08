#!/usr/bin/env python3
"""
청크 제목 생성 진행 상황 모니터링 스크립트
"""

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.models.database import SessionLocal
from backend.models.models import KnowledgeChunk


def check_progress():
    """제목 생성 진행 상황 확인"""
    db = SessionLocal()
    try:
        total = db.query(KnowledgeChunk).count()
        with_title = db.query(KnowledgeChunk).filter(
            KnowledgeChunk.title != None,
            KnowledgeChunk.title != ""
        ).count()
        without_title = total - with_title
        
        # AI로 생성된 제목 수
        ai_generated = db.query(KnowledgeChunk).filter(
            KnowledgeChunk.title_source == "ai_extracted"
        ).count()
        
        return {
            "total": total,
            "with_title": with_title,
            "without_title": without_title,
            "ai_generated": ai_generated,
            "progress_percent": (with_title / total * 100) if total > 0 else 0
        }
    finally:
        db.close()


def main():
    print("="*60)
    print("청크 제목 생성 진행 상황 모니터링")
    print("="*60)
    print("\nCtrl+C를 눌러 종료할 수 있습니다.\n")
    
    try:
        while True:
            progress = check_progress()
            
            print(f"\r[{time.strftime('%H:%M:%S')}] "
                  f"전체: {progress['total']}개 | "
                  f"제목 있음: {progress['with_title']}개 ({progress['progress_percent']:.1f}%) | "
                  f"제목 없음: {progress['without_title']}개 | "
                  f"AI 생성: {progress['ai_generated']}개", end="", flush=True)
            
            if progress['without_title'] == 0:
                print("\n\n✅ 모든 청크의 제목 생성이 완료되었습니다!")
                break
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n\n모니터링을 종료합니다.")
        progress = check_progress()
        print(f"\n최종 상태:")
        print(f"  전체 청크: {progress['total']}개")
        print(f"  제목 있음: {progress['with_title']}개")
        print(f"  제목 없음: {progress['without_title']}개")
        print(f"  AI 생성: {progress['ai_generated']}개")


if __name__ == "__main__":
    main()
