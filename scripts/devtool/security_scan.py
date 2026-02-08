#!/usr/bin/env python3
"""
보안 취약점 점검 스크립트
의존성 취약점 스캔 및 입력 검증 확인
"""
import sys
import subprocess
from pathlib import Path
import json

# 프로젝트 루트 경로 설정
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def scan_dependencies():
    """의존성 취약점 스캔"""
    print("=" * 60)
    print("의존성 취약점 스캔")
    print("=" * 60)
    
    # pip-audit 사용 (설치되어 있는 경우)
    try:
        result = subprocess.run(
            ["pip-audit", "--requirement", str(PROJECT_ROOT / "requirements.txt")],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ pip-audit 스캔 완료")
            if result.stdout:
                print(result.stdout)
        else:
            print("⚠️  pip-audit 실행 실패")
            print("설치 방법: pip install pip-audit")
    except FileNotFoundError:
        print("⚠️  pip-audit이 설치되어 있지 않습니다.")
        print("설치 방법: pip install pip-audit")
    
    # safety 사용 (설치되어 있는 경우)
    try:
        result = subprocess.run(
            ["safety", "check", "--file", str(PROJECT_ROOT / "requirements.txt")],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("\n✅ safety 스캔 완료")
            if result.stdout:
                print(result.stdout)
        else:
            print("\n⚠️  safety 실행 실패")
            print("설치 방법: pip install safety")
    except FileNotFoundError:
        print("\n⚠️  safety가 설치되어 있지 않습니다.")
        print("설치 방법: pip install safety")


def check_input_validation():
    """입력 검증 확인"""
    print("\n" + "=" * 60)
    print("입력 검증 확인")
    print("=" * 60)
    
    issues = []
    
    # FastAPI 라우터에서 입력 검증 확인
    router_files = list((PROJECT_ROOT / "backend" / "routers").glob("*.py"))
    
    for router_file in router_files:
        with open(router_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # SQL injection 위험 확인
            if 'f"' in content and 'db.query' in content:
                issues.append({
                    'file': str(router_file.relative_to(PROJECT_ROOT)),
                    'type': 'potential_sql_injection',
                    'severity': 'high',
                    'message': 'f-string과 db.query 사용 확인 필요'
                })
            
            # XSS 위험 확인 (HTML 직접 반환)
            if 'HTMLResponse' in content and 'escape' not in content:
                issues.append({
                    'file': str(router_file.relative_to(PROJECT_ROOT)),
                    'type': 'potential_xss',
                    'severity': 'medium',
                    'message': 'HTMLResponse 사용 시 이스케이프 처리 확인 필요'
                })
    
    if issues:
        print(f"\n⚠️  {len(issues)}개의 잠재적 문제 발견:")
        for issue in issues:
            print(f"  [{issue['severity'].upper()}] {issue['file']}: {issue['message']}")
    else:
        print("\n✅ 입력 검증 확인 완료 (명확한 문제 없음)")


def check_security_headers():
    """보안 헤더 확인"""
    print("\n" + "=" * 60)
    print("보안 헤더 확인")
    print("=" * 60)
    
    main_file = PROJECT_ROOT / "backend" / "main.py"
    with open(main_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
        security_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection',
            'Strict-Transport-Security'
        ]
        
        found_headers = []
        for header in security_headers:
            if header.lower().replace('-', '_') in content.lower():
                found_headers.append(header)
        
        if found_headers:
            print(f"✅ 발견된 보안 헤더: {', '.join(found_headers)}")
        else:
            print("⚠️  보안 헤더가 설정되어 있지 않습니다.")
            print("권장: FastAPI 미들웨어로 보안 헤더 추가")


def main():
    """메인 함수"""
    print("보안 취약점 점검 시작\n")
    
    # 1. 의존성 취약점 스캔
    scan_dependencies()
    
    # 2. 입력 검증 확인
    check_input_validation()
    
    # 3. 보안 헤더 확인
    check_security_headers()
    
    print("\n" + "=" * 60)
    print("보안 점검 완료")
    print("=" * 60)


if __name__ == "__main__":
    main()
