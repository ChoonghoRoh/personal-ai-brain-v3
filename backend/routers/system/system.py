"""시스템 API 라우터"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Optional
from pathlib import Path

from backend.services.system.system_service import get_system_service
from backend.config import SYSTEM_DIR

router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("/status")
async def get_status() -> Dict:
    """시스템 상태 조회"""
    service = get_system_service()
    return service.get_status()


@router.get("/info")
async def get_system_info() -> Dict:
    """시스템 정보 조회"""
    service = get_system_service()
    status = service.get_status()
    
    # 추가 정보 수집
    import platform
    import sys
    from pathlib import Path
    from backend.config import PROJECT_ROOT
    
    return {
        "system": {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "python_version": sys.version,
            "project_root": str(PROJECT_ROOT)
        },
        "status": status,
        "version": "8.0.0"
    }


@router.get("/work-log")
async def get_work_log() -> Dict:
    """작업 로그 파일 (work_log.md) 내용 조회"""
    work_log_path = SYSTEM_DIR / "work_log.md"
    
    if not work_log_path.exists():
        raise HTTPException(status_code=404, detail="작업 로그 파일을 찾을 수 없습니다.")
    
    try:
        with open(work_log_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {
            'file_path': 'brain/system/work_log.md',
            'name': 'work_log.md',
            'content': content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"작업 로그 파일 읽기 오류: {str(e)}")


@router.post("/test/gpt4all")
async def test_gpt4all(model: Optional[str] = None) -> Dict:
    """GPT4All(Ollama) 실행 테스트. model을 지정하면 해당 모델로만 테스트 (쿼리: ?model=qwen2.5:7b)"""
    service = get_system_service()
    return service.test_gpt4all(model=model)


@router.post("/test/venv-packages")
async def test_venv_packages() -> Dict:
    """가상환경 패키지 재확인 (수동 실행)"""
    service = get_system_service()
    return service.check_venv_packages()

