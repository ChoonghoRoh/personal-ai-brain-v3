"""시스템 서비스"""
from typing import Dict, Optional
from pathlib import Path
import json
import os
import logging
import subprocess
import threading

from backend.config import PROJECT_ROOT, SYSTEM_DIR, QDRANT_HOST, QDRANT_PORT, COLLECTION_NAME, OLLAMA_MODEL
from backend.services.ai.ollama_client import ollama_available, ollama_generate, ollama_list_models

logger = logging.getLogger(__name__)
BRAIN_DIR = PROJECT_ROOT / "brain"


class SystemService:
    """시스템 서비스 클래스"""
    
    def get_status(self) -> Dict:
        """시스템 상태 가져오기"""
        status = {}
        
        # 각 상태를 개별적으로 가져오기 (예외 발생 시에도 다른 상태는 정상 반환)
        try:
            status['qdrant'] = self._get_qdrant_status()
        except Exception as e:
            logger.error(f"Qdrant 상태 확인 실패: {e}", exc_info=True)
            status['qdrant'] = {'status': 'error', 'error': str(e)}
        
        try:
            logger.info("데이터베이스 상태 확인 시작")
            status['database'] = self._get_database_status()
            logger.info(f"데이터베이스 상태: {status['database']}")
        except Exception as e:
            logger.error(f"데이터베이스 상태 확인 실패: {e}", exc_info=True)
            status['database'] = {'status': 'error', 'error': str(e)}
        
        try:
            logger.info("가상환경 상태 확인 시작")
            status['venv'] = self._get_venv_status()
            logger.info(f"가상환경 상태: {status['venv']}")
        except Exception as e:
            logger.error(f"가상환경 상태 확인 실패: {e}", exc_info=True)
            status['venv'] = {'status': 'error', 'error': str(e)}
        
        try:
            logger.info("Ollama(로컬 LLM) 상태 확인 시작")
            status['gpt4all'] = self._get_ollama_status(run_test=False)
            logger.info(f"Ollama 상태: {status['gpt4all']}")
        except Exception as e:
            logger.error(f"Ollama 상태 확인 실패: {e}", exc_info=True)
            status['gpt4all'] = {'status': 'error', 'error': str(e)}
        
        try:
            status['files'] = self._get_file_stats()
        except Exception as e:
            status['files'] = {}
        
        try:
            status['recent_work'] = self._get_recent_work()
        except Exception as e:
            status['recent_work'] = []
        
        try:
            status['automation'] = self._get_automation_status()
        except Exception as e:
            status['automation'] = {}
        
        try:
            status['recent_documents'] = self._get_recent_documents()
        except Exception as e:
            status['recent_documents'] = []
        
        return status
    
    def _get_qdrant_status(self) -> Dict:
        """Qdrant 상태"""
        try:
            from qdrant_client import QdrantClient
            client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
            collection_info = client.get_collection(COLLECTION_NAME)
            
            # Qdrant 버전별 포인트 수 가져오기 (호환성 처리)
            points_count = None
            try:
                # 신버전 속성 시도
                points_count = collection_info.points_count
            except AttributeError:
                try:
                    # 구버전 속성 시도
                    points_count = collection_info.vectors_count
                except AttributeError:
                    # 최종 대체: API를 통해 직접 조회
                    try:
                        # get_collection의 결과에서 다른 방법으로 포인트 수 가져오기
                        # 또는 count API 사용
                        from qdrant_client.models import Filter
                        count_result = client.count(COLLECTION_NAME)
                        points_count = count_result.count if hasattr(count_result, 'count') else 0
                    except Exception:
                        points_count = 0
            
            return {
                'status': 'connected',
                'points_count': points_count or 0,
                'collection_name': COLLECTION_NAME
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _get_database_status(self) -> Dict:
        """PostgreSQL 데이터베이스 연결 상태"""
        try:
            from backend.models.database import SessionLocal
            from sqlalchemy import text
            db = SessionLocal()
            try:
                # 간단한 쿼리로 연결 테스트
                result = db.execute(text("SELECT 1"))
                result.fetchone()  # 결과 가져오기
                return {
                    'status': 'connected',
                    'message': '데이터베이스 연결 성공'
                }
            finally:
                db.close()
        except Exception as e:
            import traceback
            return {
                'status': 'error',
                'error': str(e),
                'traceback': traceback.format_exc()
            }
    
    def _get_venv_status(self) -> Dict:
        """가상환경 상태 및 패키지 설치 확인. Docker 컨테이너에서는 'docker' 상태 반환."""
        # Docker 컨테이너 여부 (PROJECT_ROOT가 /app 이거나 /.dockerenv 존재)
        running_in_docker = (
            str(PROJECT_ROOT) == "/app"
            or (Path("/.dockerenv").exists() if hasattr(Path, "exists") else os.path.exists("/.dockerenv"))
        )
        if running_in_docker:
            return {
                "status": "docker",
                "message": "Docker 컨테이너에서 실행 중",
                "venv_path": None,
                "activated": False,
                "running_in_docker": True,
            }

        venv_path = os.environ.get("VIRTUAL_ENV")
        venv_activated = venv_path is not None

        # 가상환경 경로 확인
        expected_venv_path = PROJECT_ROOT / "scripts" / "venv"
        venv_exists = expected_venv_path.exists()

        # 패키지 설치 확인
        packages_status = {}
        missing_packages = []

        if venv_activated or venv_exists:
            # 가상환경 Python 경로 결정
            if venv_activated:
                python_exe = Path(venv_path) / "bin" / "python"
            else:
                python_exe = expected_venv_path / "bin" / "python"
            
            # Python 실행 파일 존재 확인
            if python_exe.exists():
                # 주요 패키지 확인 (import 이름으로 변환)
                essential_packages = {
                    'fastapi': 'fastapi',
                    'uvicorn': 'uvicorn',
                    'qdrant_client': 'qdrant_client',
                    'sqlalchemy': 'sqlalchemy',
                    'psycopg2': 'psycopg2',
                    'sentence_transformers': 'sentence_transformers',
                    'gpt4all': 'gpt4all'  # 선택적
                }
                
                for package_display, package_import in essential_packages.items():
                    try:
                        # 가상환경 Python으로 import 시도 (방법 1: 권장)
                        # 타임아웃을 5초로 증가 (느린 시스템 대응)
                        result = subprocess.run(
                            [str(python_exe), '-c', f'import {package_import}'],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        if result.returncode == 0:
                            packages_status[package_display] = 'installed'
                        else:
                            packages_status[package_display] = 'missing'
                            if package_display != 'gpt4all':  # gpt4all은 선택적
                                missing_packages.append(package_display)
                            # stderr에 에러 메시지가 있으면 로깅
                            if result.stderr:
                                logger.debug(f"패키지 {package_display} import 실패: {result.stderr}")
                    except subprocess.TimeoutExpired:
                        packages_status[package_display] = 'timeout'
                        logger.warning(f"패키지 {package_display} 확인 시간 초과 (5초)")
                    except Exception as e:
                        packages_status[package_display] = 'error'
                        logger.warning(f"패키지 {package_display} 확인 중 오류: {e}")
        
        # 상태 결정
        if not venv_activated and not venv_exists:
            status = 'not_activated'
        elif missing_packages:
            status = 'packages_missing'
        else:
            status = 'activated' if venv_activated else 'not_activated'
        
        message = f"가상환경 {'활성화됨' if venv_activated else '비활성화됨'}"
        if missing_packages:
            message += f" (누락된 패키지: {', '.join(missing_packages)})"
        
        return {
            'status': status,
            'activated': venv_activated,
            'venv_path': venv_path if venv_activated else None,
            'expected_path': str(expected_venv_path),
            'exists': venv_exists,
            'packages_status': packages_status,
            'missing_packages': missing_packages,
            'message': message
        }
    
    def _get_ollama_status(self, run_test: bool = False, model: Optional[str] = None) -> Dict:
        """Ollama(로컬 LLM) 상태 및 실행 테스트.

        Args:
            run_test: True이면 짧은 생성 테스트 수행.
            model: 테스트할 모델명. None이면 기본 모델(OLLAMA_MODEL) 사용.
        """
        try:
            if not ollama_available():
                return {
                    'status': 'not_installed',
                    'message': 'Ollama가 실행 중이 아니거나 모델이 없습니다. Ollama 설치 후 모델을 로드하세요.',
                    'install_command': f'ollama run {OLLAMA_MODEL}',
                    'source': 'ollama'
                }
            # 설치된 모델 목록 (대시보드에서 모델별 테스트용)
            models = ollama_list_models()
            model_names = [m.get("name", "").strip() for m in models if m.get("name")]
            model_names = [n for n in model_names if n]

            # run_test 시 짧은 생성 테스트 (지정 모델 또는 기본 모델)
            test_result = None
            test_error = None
            tested_model = (model or OLLAMA_MODEL).strip() or OLLAMA_MODEL
            if run_test:
                logger.info("Ollama 실행 테스트 시작 (model=%s)", tested_model)
                out = ollama_generate(
                    "한 줄로 자기소개해주세요.",
                    max_tokens=30,
                    temperature=0.3,
                    timeout=90.0,
                    model=tested_model,
                )
                if out and len(out.strip()) > 0:
                    test_result = 'success'
                    logger.info("Ollama 실행 테스트 성공 (model=%s)", tested_model)
                else:
                    test_result = 'error'
                    test_error = "모델 응답이 비어있음"
            result = {
                'status': 'available',
                'model_name': OLLAMA_MODEL,
                'models': model_names,
                'test_result': test_result or ('not_tested' if not run_test else 'unknown'),
                'tested_model': tested_model if run_test else None,
                'message': 'Ollama 연결됨' + (' (실행 테스트 성공)' if test_result == 'success' else (' (실행 테스트 실패: ' + (test_error or '') + ')' if test_result == 'error' else '')),
                'source': 'ollama'
            }
            if test_error is not None:
                result['test_error'] = test_error
            return result
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'test_result': 'error',
                'test_error': str(e),
                'message': 'Ollama 상태 확인 실패',
                'source': 'ollama'
            }

    def test_gpt4all(self, model: Optional[str] = None) -> Dict:
        """로컬 LLM(Ollama) 실행 테스트 (수동 호출용, API 호환용 엔드포인트명 유지).
        model이 지정되면 해당 모델로만 테스트한다."""
        return self._get_ollama_status(run_test=True, model=model)
    
    def check_venv_packages(self) -> Dict:
        """가상환경 패키지 재확인 (수동 호출용)"""
        return self._get_venv_status()
    
    def _get_file_stats(self) -> Dict:
        """파일 통계"""
        stats = {
            'total_md_files': 0,
            'projects': 0,
            'reference': 0,
            'inbox': 0,
            'archive': 0
        }
        
        brain_dir = PROJECT_ROOT / "brain"
        for md_file in brain_dir.rglob("*.md"):
            if md_file.is_file():
                stats['total_md_files'] += 1
                relative = md_file.relative_to(brain_dir)
                parts = relative.parts
                if len(parts) > 0:
                    category = parts[0]
                    if category in stats:
                        stats[category] += 1
        
        return stats
    
    def _get_recent_work(self) -> list:
        """최근 작업 가져오기"""
        work_log_json = SYSTEM_DIR / "work_log.json"
        if not work_log_json.exists():
            return []
        
        try:
            with open(work_log_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
                entries = data.get('entries', [])
                # 최근 5개만 반환
                return sorted(entries, key=lambda x: x.get('timestamp', ''), reverse=True)[:5]
        except:
            return []
    
    def _get_automation_status(self) -> Dict:
        """자동화 상태 가져오기"""
        import os
        import subprocess
        
        status = {
            'watcher_running': False,
            'git_auto_commit': True  # 기본적으로 활성화 가능
        }
        
        # watcher 프로세스 확인 (간단한 체크)
        try:
            result = subprocess.run(['pgrep', '-f', 'watcher.py'], 
                                  capture_output=True, text=True)
            status['watcher_running'] = result.returncode == 0
        except:
            pass
        
        return status
    
    def _get_recent_documents(self) -> list:
        """최근 업데이트된 문서 가져오기"""
        documents = []
        
        for md_file in BRAIN_DIR.rglob("*.md"):
            if md_file.is_file():
                try:
                    stat = md_file.stat()
                    relative_path = md_file.relative_to(PROJECT_ROOT)
                    documents.append({
                        'file_path': str(relative_path),
                        'name': md_file.name,
                        'modified': stat.st_mtime,
                        'size': stat.st_size
                    })
                except:
                    pass
        
        # 수정 시간순으로 정렬 (최신이 위)
        documents.sort(key=lambda x: x.get('modified', 0), reverse=True)
        
        # 최근 5개만 반환
        return documents[:5]


# 싱글톤 인스턴스
_system_service = None

def get_system_service() -> SystemService:
    """시스템 서비스 인스턴스 가져오기"""
    global _system_service
    if _system_service is None:
        _system_service = SystemService()
    return _system_service

def reset_system_service():
    """시스템 서비스 인스턴스 재설정 (테스트/디버깅용)"""
    global _system_service
    _system_service = None
