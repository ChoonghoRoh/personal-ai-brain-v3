#!/usr/bin/env python3
"""
데이터 동기화 스크립트
Qdrant와 PostgreSQL 간 데이터 불일치를 해결하기 위해 embed_and_store.py를 재실행
"""
import sys
import subprocess
from pathlib import Path

# 프로젝트 루트 경로 설정
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.check_data_sync import check_data_sync

def sync_data():
    """데이터 동기화 실행"""
    print("=" * 60)
    print("데이터 동기화 시작")
    print("=" * 60)
    
    # 1. 현재 상태 확인
    print("\n[1/3] 현재 데이터 상태 확인...")
    is_synced = check_data_sync()
    
    if is_synced:
        print("\n✅ 데이터가 이미 동기화되어 있습니다.")
        return True
    
    # 2. embed_and_store.py 재실행
    print("\n[2/3] embed_and_store.py 재실행 중...")
    print("  (모든 문서를 재임베딩하여 Qdrant와 PostgreSQL을 동기화합니다)")
    print("  (Qdrant 컬렉션 재생성 모드로 실행하여 중복 제거)")
    
    try:
        script_path = PROJECT_ROOT / "scripts" / "embed_and_store.py"
        result = subprocess.run(
            [sys.executable, str(script_path), "--recreate"],
            cwd=str(PROJECT_ROOT / "scripts"),
            capture_output=False,
            text=True
        )
        
        if result.returncode != 0:
            print(f"\n❌ embed_and_store.py 실행 실패 (종료 코드: {result.returncode})")
            return False
        
        print("\n✅ embed_and_store.py 실행 완료")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        return False
    
    # 3. 동기화 확인
    print("\n[3/3] 동기화 결과 확인...")
    is_synced = check_data_sync()
    
    if is_synced:
        print("\n✅ 데이터 동기화 완료!")
        return True
    else:
        print("\n⚠️ 데이터 불일치가 여전히 존재합니다.")
        print("  수동으로 확인이 필요할 수 있습니다.")
        return False


if __name__ == "__main__":
    success = sync_data()
    sys.exit(0 if success else 1)

