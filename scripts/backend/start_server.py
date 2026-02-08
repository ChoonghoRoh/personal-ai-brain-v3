#!/usr/bin/env python3
"""FastAPI 서버 실행 스크립트 (로컬 실행용).
Docker Compose 사용 시: docker-compose up -d backend 로 백엔드 컨테이너 실행."""
import sys
import os
import subprocess
import platform
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 가상환경 확인 및 경고
VENV_PATH = PROJECT_ROOT / "scripts" / "venv"
VENV_ACTIVATED = os.environ.get("VIRTUAL_ENV") is not None

def check_docker():
    """Docker 설치 및 실행 상태 확인"""
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False, None

def check_container_running(container_name):
    """컨테이너가 실행 중인지 확인"""
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=True
        )
        return container_name in result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def start_container(container_name, docker_command):
    """컨테이너 시작"""
    try:
        print(f"   컨테이너 시작 중: {container_name}...")
        result = subprocess.run(
            docker_command,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"   ✅ {container_name} 시작 완료")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ {container_name} 시작 실패: {e.stderr}")
        return False

def check_and_start_docker_containers():
    """Docker 컨테이너 확인 및 시작 (Mac 환경)"""
    # Mac 환경 확인
    if platform.system() != "Darwin":
        print("⚠️  Docker 자동 시작은 Mac 환경에서만 지원됩니다.")
        return
    
    print("=" * 60)
    print("Docker 컨테이너 상태 확인")
    print("=" * 60)
    
    # Docker 설치 확인
    docker_available, docker_version = check_docker()
    if not docker_available:
        print("❌ Docker가 설치되어 있지 않거나 실행 중이 아닙니다.")
        print("   Docker Desktop을 설치하고 실행해주세요.")
        print("=" * 60)
        print()
        return
    
    print(f"✅ Docker 설치됨: {docker_version}")
    
    # Qdrant 컨테이너 확인 및 시작
    qdrant_running = check_container_running("qdrant")
    if qdrant_running:
        print("✅ Qdrant 컨테이너 실행 중")
    else:
        print("⚠️  Qdrant 컨테이너가 실행 중이 아닙니다.")
        # 컨테이너가 존재하는지 확인
        try:
            result = subprocess.run(
                ["docker", "ps", "-a", "--filter", "name=qdrant", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                check=True
            )
            if "qdrant" in result.stdout:
                # 컨테이너가 존재하면 시작
                if start_container("qdrant", "docker start qdrant"):
                    print("   잠시 대기 중...")
                    import time
                    time.sleep(2)
            else:
                # 컨테이너가 없으면 생성
                qdrant_data_dir = PROJECT_ROOT / "qdrant-data"
                qdrant_data_dir.mkdir(exist_ok=True)
                docker_cmd = (
                    f"docker run -d -p 6333:6333 -p 6334:6334 "
                    f"-v {qdrant_data_dir.absolute()}:/qdrant/storage "
                    f"--name qdrant qdrant/qdrant"
                )
                if start_container("qdrant", docker_cmd):
                    print("   잠시 대기 중...")
                    import time
                    time.sleep(3)
        except Exception as e:
            print(f"   ❌ Qdrant 컨테이너 확인 실패: {e}")
    
    # PostgreSQL 컨테이너 확인 및 시작
    postgres_running = check_container_running("pab-postgres")
    if postgres_running:
        print("✅ PostgreSQL 컨테이너 실행 중")
    else:
        print("⚠️  PostgreSQL 컨테이너가 실행 중이 아닙니다.")
        # 컨테이너가 존재하는지 확인
        try:
            result = subprocess.run(
                ["docker", "ps", "-a", "--filter", "name=pab-postgres", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                check=True
            )
            if "pab-postgres" in result.stdout:
                # 컨테이너가 존재하면 시작
                if start_container("pab-postgres", "docker start pab-postgres"):
                    print("   잠시 대기 중...")
                    import time
                    time.sleep(3)
            else:
                # 컨테이너가 없으면 생성
                postgres_data_dir = PROJECT_ROOT / "postgres-data"
                postgres_data_dir.mkdir(exist_ok=True)
                docker_cmd = (
                    f"docker run -d --name pab-postgres "
                    f"-e POSTGRES_USER=brain "
                    f"-e POSTGRES_PASSWORD=brain_password "
                    f"-e POSTGRES_DB=knowledge "
                    f"-p 5432:5432 "
                    f"-v {postgres_data_dir.absolute()}:/var/lib/postgresql/data "
                    f"postgres:15"
                )
                if start_container("pab-postgres", docker_cmd):
                    print("   잠시 대기 중...")
                    import time
                    time.sleep(5)  # PostgreSQL은 시작 시간이 더 필요
        except Exception as e:
            print(f"   ❌ PostgreSQL 컨테이너 확인 실패: {e}")
    
    print("=" * 60)
    print()

def check_venv():
    """가상환경 상태 확인"""
    print("=" * 60)
    print("가상환경 상태 확인")
    print("=" * 60)
    
    if VENV_ACTIVATED:
        venv_path = os.environ.get("VIRTUAL_ENV")
        print(f"✅ 가상환경 활성화됨: {venv_path}")
    else:
        print("⚠️  가상환경이 활성화되지 않았습니다.")
        if VENV_PATH.exists():
            print(f"💡 가상환경 경로: {VENV_PATH}")
            print("   다음 명령어로 가상환경을 활성화하세요:")
            print(f"   source {VENV_PATH}/bin/activate")
        else:
            print(f"⚠️  가상환경을 찾을 수 없습니다: {VENV_PATH}")
            print("   가상환경을 생성하려면:")
            print(f"   python3 -m venv {VENV_PATH}")
    
    # gpt4all 패키지 확인
    try:
        import gpt4all
        print("✅ gpt4all 패키지 설치됨")
    except ImportError:
        print("⚠️  gpt4all 패키지가 설치되지 않았습니다.")
        print("   설치하려면: pip install gpt4all")
    
    print("=" * 60)
    print()

if __name__ == "__main__":
    # Docker 컨테이너 확인 및 시작 (Mac 환경)
    check_and_start_docker_containers()
    
    # 가상환경 확인
    check_venv()
    
    import uvicorn
    from backend.config import API_HOST, API_PORT
    
    print("=" * 60)
    print("Personal AI Brain - Web Server 시작")
    print("=" * 60)
    print(f"서버 주소: http://{API_HOST}:{API_PORT}")
    print(f"대시보드: http://localhost:{API_PORT}/dashboard")
    print(f"검색: http://localhost:{API_PORT}/search")
    print(f"API 문서: http://localhost:{API_PORT}/docs")
    print("\n종료하려면 Ctrl+C를 누르세요.\n")
    
    uvicorn.run(
        "backend.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True
    )

