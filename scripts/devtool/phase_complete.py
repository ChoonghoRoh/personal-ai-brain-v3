#!/usr/bin/env python3
"""
Phase 완료 시 자동으로 work_log 업데이트, README 요약 추가, Git push를 수행하는 스크립트

사용법:
    python scripts/phase_complete.py "작업 설명" --phase 7 --files file1.py file2.html
"""

import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.work_logger import get_logger


def update_readme_summary(phase_num: int, description: str, files: list):
    """README.md에 Phase 요약 추가"""
    readme_path = PROJECT_ROOT / "README.md"
    
    if not readme_path.exists():
        print(f"⚠️ README.md를 찾을 수 없습니다: {readme_path}")
        return False
    
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Phase 완료 섹션 찾기 (진행 단계 테이블 다음)
        phase_table_marker = "| **6단계** | ✅ 완료 |"
        
        if phase_table_marker in content:
            # 새로운 Phase 행 추가
            new_phase_row = f"| **{phase_num}단계** | ✅ 완료 | {description} |\n"
            
            # 6단계 행 다음에 추가
            insert_pos = content.find(phase_table_marker) + len(phase_table_marker)
            next_line_pos = content.find('\n', insert_pos)
            if next_line_pos != -1:
                content = content[:next_line_pos+1] + new_phase_row + content[next_line_pos+1:]
            else:
                content = content[:insert_pos] + '\n' + new_phase_row + content[insert_pos:]
        else:
            # 테이블을 찾을 수 없으면 "## 📋 작업 기록 요약" 섹션에 추가
            summary_marker = "## 📋 작업 기록 요약"
            if summary_marker in content:
                # 테이블 시작 찾기
                table_start = content.find("### 📊 진행 단계", content.find(summary_marker))
                if table_start != -1:
                    # 테이블 끝 찾기
                    table_end = content.find("\n---", table_start)
                    if table_end == -1:
                        table_end = content.find("\n\n###", table_start)
                    
                    if table_end != -1:
                        new_phase_row = f"| **{phase_num}단계** | ✅ 완료 | {description} |\n"
                        content = content[:table_end] + new_phase_row + content[table_end:]
        
        # Phase 상세 섹션 추가 (파일 끝에)
        phase_detail = f"""
### {phase_num}단계: {description} ({datetime.now().strftime('%Y-%m-%d')})

**구현 내용**

- ✅ {description}

**주요 파일**

{chr(10).join(f"- `{f}`" for f in files[:10])}

---

"""
        
        # 파일 끝에 추가
        content += phase_detail
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ README.md에 Phase {phase_num} 요약이 추가되었습니다.")
        return True
        
    except Exception as e:
        print(f"❌ README.md 업데이트 실패: {e}")
        return False


def git_add_and_commit(files: list, message: str):
    """Git에 파일 추가 및 커밋"""
    try:
        # 파일 추가
        subprocess.run(['git', 'add'] + files, check=True, cwd=PROJECT_ROOT)
        print(f"✅ Git에 {len(files)}개 파일 추가됨")
        
        # 커밋
        subprocess.run(['git', 'commit', '-m', message], check=True, cwd=PROJECT_ROOT)
        print(f"✅ Git 커밋 완료: {message}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git 작업 실패: {e}")
        return False


def git_push():
    """Git push"""
    try:
        result = subprocess.run(['git', 'push', 'origin', 'main'], 
                              check=True, cwd=PROJECT_ROOT,
                              capture_output=True, text=True)
        print("✅ Git push 완료")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git push 실패: {e}")
        if e.stdout:
            print(f"출력: {e.stdout}")
        if e.stderr:
            print(f"오류: {e.stderr}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Phase 완료 시 자동 업데이트 및 Git push')
    parser.add_argument('description', help='작업 설명')
    parser.add_argument('--phase', type=int, help='Phase 번호', default=7)
    parser.add_argument('--files', nargs='+', help='변경된 파일 목록', default=[])
    parser.add_argument('--no-push', action='store_true', help='Git push 하지 않음')
    parser.add_argument('--no-readme', action='store_true', help='README.md 업데이트 하지 않음')
    
    args = parser.parse_args()
    
    print(f"🚀 Phase {args.phase} 완료 처리 시작...")
    print(f"설명: {args.description}")
    print(f"파일: {', '.join(args.files) if args.files else '자동 감지'}")
    print()
    
    # 1. work_log에 추가
    logger = get_logger()
    logger.add_entry(
        action='system',
        description=f"Phase {args.phase} 완료: {args.description}",
        files=args.files if args.files else [],
        metadata={
            'phase': args.phase,
            'status': 'completed',
            'type': 'phase_completion'
        }
    )
    print("✅ work_log.json에 항목 추가됨")
    
    # work_log.md 재생성
    try:
        # work_logger.py의 generate_markdown_log 메서드 호출
        logger.generate_markdown_log()
        print("✅ work_log.md 재생성 완료")
    except Exception as e:
        print(f"⚠️ work_log.md 재생성 실패: {e}")
    
    # 2. README.md 업데이트
    if not args.no_readme:
        update_readme_summary(args.phase, args.description, args.files)
    
    # 3. Git 작업
    files_to_commit = []
    
    # work_log 파일들
    files_to_commit.extend([
        'brain/system/work_log.json',
        'brain/system/work_log.md'
    ])
    
    # README.md
    if not args.no_readme:
        files_to_commit.append('README.md')
    
    # 변경된 파일들
    if args.files:
        files_to_commit.extend(args.files)
    
    # Git 상태 확인
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, cwd=PROJECT_ROOT)
        if result.stdout.strip():
            print(f"\n📝 Git 변경사항 감지됨")
            
            # 커밋 메시지 생성
            commit_message = f"feat: Phase {args.phase} 완료 - {args.description}"
            
            # Git add & commit
            if git_add_and_commit(files_to_commit, commit_message):
                # Git push
                if not args.no_push:
                    git_push()
                else:
                    print("ℹ️ --no-push 옵션으로 인해 push를 건너뜁니다.")
            else:
                print("⚠️ Git 커밋 실패, push를 건너뜁니다.")
        else:
            print("ℹ️ Git 변경사항이 없습니다.")
    except Exception as e:
        print(f"⚠️ Git 작업 중 오류: {e}")
    
    print(f"\n✅ Phase {args.phase} 완료 처리 완료!")


if __name__ == "__main__":
    main()

