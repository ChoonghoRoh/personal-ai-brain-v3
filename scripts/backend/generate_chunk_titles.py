#!/usr/bin/env python3
"""
제목이 없는 청크에 AI로 제목 생성하는 스크립트

사용법:
    python scripts/generate_chunk_titles.py
    python scripts/generate_chunk_titles.py --limit 10  # 처음 10개만 처리
    python scripts/generate_chunk_titles.py --dry-run  # 실제 업데이트 없이 테스트
"""

import sys
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy.orm import Session
from backend.models.database import SessionLocal
from backend.models.models import KnowledgeChunk
from scripts.embed_and_store import extract_title_with_ai


def generate_titles_for_chunks(db: Session, limit: int = None, dry_run: bool = False):
    """제목이 없는 청크들에 AI로 제목 생성
    
    Args:
        db: 데이터베이스 세션
        limit: 처리할 최대 청크 수 (None이면 모두 처리)
        dry_run: True면 실제 업데이트 없이 테스트만 수행
    """
    # 제목이 없는 청크 조회
    query = db.query(KnowledgeChunk).filter(
        (KnowledgeChunk.title == None) | (KnowledgeChunk.title == "")
    )
    
    if limit:
        query = query.limit(limit)
    
    chunks = query.all()
    
    if not chunks:
        print("✅ 제목이 없는 청크가 없습니다.")
        return
    
    print(f"📋 제목이 없는 청크 {len(chunks)}개를 찾았습니다.")
    if dry_run:
        print("🔍 [DRY-RUN 모드] 실제 업데이트는 수행하지 않습니다.\n")
    else:
        print("🚀 AI 제목 생성을 시작합니다...\n")
    
    success_count = 0
    fail_count = 0
    skip_count = 0
    
    for idx, chunk in enumerate(chunks, 1):
        print(f"[{idx}/{len(chunks)}] 청크 ID {chunk.id} 처리 중...", end=" ")
        
        # 내용이 너무 짧으면 스킵
        if len(chunk.content.strip()) < 50:
            print("⏭️  내용이 너무 짧아 스킵")
            skip_count += 1
            continue
        
        # AI로 제목 생성
        try:
            title = extract_title_with_ai(chunk.content)
            
            if title:
                if not dry_run:
                    chunk.title = title
                    chunk.title_source = "ai_extracted"
                    db.commit()
                print(f"✅ '{title}'")
                success_count += 1
            else:
                print("⚠️  제목 생성 실패 (AI 응답 없음)")
                fail_count += 1
                
        except Exception as e:
            print(f"❌ 오류: {e}")
            fail_count += 1
            db.rollback()
    
    print("\n" + "="*60)
    print("📊 처리 결과:")
    print(f"  ✅ 성공: {success_count}개")
    print(f"  ❌ 실패: {fail_count}개")
    print(f"  ⏭️  스킵: {skip_count}개")
    print(f"  📝 총 처리: {len(chunks)}개")
    
    if dry_run:
        print("\n💡 실제 업데이트를 수행하려면 --dry-run 옵션을 제거하세요.")


def main():
    parser = argparse.ArgumentParser(
        description="제목이 없는 청크에 AI로 제목 생성"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="처리할 최대 청크 수 (기본값: 모두 처리)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="실제 업데이트 없이 테스트만 수행"
    )
    
    args = parser.parse_args()
    
    db = SessionLocal()
    try:
        generate_titles_for_chunks(
            db=db,
            limit=args.limit,
            dry_run=args.dry_run
        )
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자에 의해 중단되었습니다.")
        db.rollback()
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
