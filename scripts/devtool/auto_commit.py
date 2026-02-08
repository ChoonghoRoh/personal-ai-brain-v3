#!/usr/bin/env python3
"""
Git 자동 커밋 시스템
시스템이 스스로 성장 기록을 남기는 구조
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# 작업 로그 시스템 import
try:
    from work_logger import log_action
    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False


def run_git_command(cmd: List[str], check: bool = True) -> tuple[str, str, int]:
    """Git 명령어 실행"""
    try:
        result = subprocess.run(
            ['git'] + cmd,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=check
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout.strip(), e.stderr.strip(), e.returncode
    except FileNotFoundError:
        print("❌ Git이 설치되어 있지 않습니다.")
        sys.exit(1)


def get_git_status() -> dict:
    """Git 상태 확인"""
    stdout, stderr, code = run_git_command(['status', '--porcelain'], check=False)
    
    if code != 0:
        return {'error': stderr}
    
    lines = stdout.split('\n') if stdout else []
    modified = []
    added = []
    deleted = []
    untracked = []
    
    for line in lines:
        if not line.strip():
            continue
        
        status = line[:2]
        filename = line[3:].strip()
        
        if status[0] == 'M' or status[1] == 'M':
            modified.append(filename)
        if status[0] == 'A' or status[1] == 'A':
            added.append(filename)
        if status[0] == 'D' or status[1] == 'D':
            deleted.append(filename)
        if status == '??':
            untracked.append(filename)
    
    return {
        'modified': modified,
        'added': added,
        'deleted': deleted,
        'untracked': untracked,
        'has_changes': len(modified) + len(added) + len(deleted) + len(untracked) > 0
    }


def generate_commit_message(status: dict) -> str:
    """커밋 메시지 자동 생성"""
    parts = []
    
    if status['added']:
        if len(status['added']) == 1:
            parts.append(f"➕ 추가: {status['added'][0]}")
        else:
            parts.append(f"➕ 추가: {len(status['added'])}개 파일")
    
    if status['modified']:
        if len(status['modified']) == 1:
            parts.append(f"📝 수정: {status['modified'][0]}")
        else:
            parts.append(f"📝 수정: {len(status['modified'])}개 파일")
    
    if status['deleted']:
        if len(status['deleted']) == 1:
            parts.append(f"🗑️  삭제: {status['deleted'][0]}")
        else:
            parts.append(f"🗑️  삭제: {len(status['deleted'])}개 파일")
    
    if status['untracked']:
        if len(status['untracked']) == 1:
            parts.append(f"🆕 신규: {status['untracked'][0]}")
        else:
            parts.append(f"🆕 신규: {len(status['untracked'])}개 파일")
    
    if not parts:
        return "🤖 자동 커밋: 변경사항 없음"
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"🤖 자동 커밋: {timestamp}\n\n" + "\n".join(parts)
    
    return message


def check_remote_exists() -> bool:
    """원격 저장소가 설정되어 있는지 확인"""
    stdout, stderr, code = run_git_command(['remote', 'show', 'origin'], check=False)
    return code == 0


def auto_commit(push: Optional[bool] = None, message: Optional[str] = None, no_push: bool = False):
    """
    자동 커밋 실행
    
    Args:
        push: True면 강제 푸시, False면 푸시 안함, None이면 원격 저장소가 있으면 자동 푸시
        message: 커밋 메시지 (None이면 자동 생성)
        no_push: True면 푸시하지 않음 (push보다 우선)
    """
    print("=" * 60)
    print("Git 자동 커밋 시스템")
    print("=" * 60)
    
    # Git 저장소 확인
    stdout, stderr, code = run_git_command(['rev-parse', '--git-dir'], check=False)
    if code != 0:
        print("❌ Git 저장소가 아닙니다. 'git init'을 먼저 실행하세요.")
        return False
    
    # 상태 확인
    print("\n[1/3] 변경사항 확인 중...")
    status = get_git_status()
    
    if 'error' in status:
        print(f"❌ 오류: {status['error']}")
        return False
    
    if not status['has_changes']:
        print("✅ 커밋할 변경사항이 없습니다.")
        return True
    
    # 변경사항 출력
    if status['added']:
        print(f"  ➕ 추가: {len(status['added'])}개")
    if status['modified']:
        print(f"  📝 수정: {len(status['modified'])}개")
    if status['deleted']:
        print(f"  🗑️  삭제: {len(status['deleted'])}개")
    if status['untracked']:
        print(f"  🆕 신규: {len(status['untracked'])}개")
    
    # 커밋 메시지 생성
    commit_message = message or generate_commit_message(status)
    
    # 파일 추가
    print("\n[2/3] 파일 추가 중...")
    stdout, stderr, code = run_git_command(['add', '-A'])
    if code != 0:
        print(f"❌ 'git add' 실패: {stderr}")
        return False
    print("✅ 파일 추가 완료")
    
    # 커밋
    print("\n[3/3] 커밋 중...")
    stdout, stderr, code = run_git_command(['commit', '-m', commit_message])
    if code != 0:
        if 'nothing to commit' in stderr.lower():
            print("ℹ️  커밋할 변경사항이 없습니다.")
            return True
        print(f"❌ 커밋 실패: {stderr}")
        return False
    
    print(f"✅ 커밋 완료: {commit_message.split(chr(10))[0]}")
    
    # 푸시 여부 결정
    should_push = False
    if no_push:
        should_push = False
    elif push is not None:
        should_push = push
    else:
        # push가 None이면 원격 저장소가 있으면 자동 푸시
        should_push = check_remote_exists()
    
    # 작업 로그 기록
    if LOGGING_AVAILABLE:
        all_files = status['added'] + status['modified'] + status['deleted'] + status['untracked']
        log_action(
            action="commit",
            description=f"Git 커밋: {commit_message.split(chr(10))[0]}",
            files=all_files[:10],  # 최대 10개만
            metadata={
                'added_count': len(status['added']),
                'modified_count': len(status['modified']),
                'deleted_count': len(status['deleted']),
                'untracked_count': len(status['untracked']),
                'pushed': should_push
            }
        )
    
    # Push (자동 또는 옵션)
    if should_push:
        print("\n[4/4] 원격 저장소에 푸시 중...")
        # 현재 브랜치 확인
        stdout, stderr, code = run_git_command(['rev-parse', '--abbrev-ref', 'HEAD'], check=False)
        current_branch = stdout.strip() if code == 0 else 'main'
        
        # 푸시 실행
        stdout, stderr, code = run_git_command(['push', 'origin', current_branch], check=False)
        if code == 0:
            print("✅ GitHub 푸시 완료")
        else:
            # 푸시 실패해도 커밋은 성공으로 처리
            if 'no upstream branch' in stderr.lower() or 'could not read' in stderr.lower():
                print(f"⚠️  푸시 실패: 원격 저장소가 설정되지 않았거나 연결할 수 없습니다.")
                print(f"   힌트: 'git remote add origin <URL>' 또는 'git push -u origin {current_branch}' 실행")
            else:
                print(f"⚠️  푸시 실패: {stderr}")
                print(f"   커밋은 성공했지만 푸시에 실패했습니다. 나중에 'git push'로 수동 푸시하세요.")
    
    return True


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Git 자동 커밋 시스템',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
기본 동작:
  - 원격 저장소가 설정되어 있으면 자동으로 푸시합니다
  - 원격 저장소가 없으면 커밋만 수행합니다

예제:
  %(prog)s                    # 자동 커밋 (원격 저장소 있으면 자동 푸시)
  %(prog)s --push             # 강제 푸시
  %(prog)s --no-push          # 푸시하지 않음
  %(prog)s -m "커밋 메시지"   # 커밋 메시지 직접 지정
        """
    )
    parser.add_argument('--push', '-p', action='store_true', 
                       help='강제로 푸시 (원격 저장소가 없어도 시도)')
    parser.add_argument('--no-push', action='store_true',
                       help='푸시하지 않음 (원격 저장소가 있어도 푸시 안함)')
    parser.add_argument('--message', '-m', type=str, help='커밋 메시지 직접 지정')
    
    args = parser.parse_args()
    
    # push와 no_push가 동시에 지정되면 no_push 우선
    push_value = None if args.no_push else (True if args.push else None)
    
    success = auto_commit(push=push_value, message=args.message, no_push=args.no_push)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

