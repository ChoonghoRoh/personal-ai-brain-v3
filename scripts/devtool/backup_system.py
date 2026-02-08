#!/usr/bin/env python3
"""
백업 및 복원 시스템
PostgreSQL과 Qdrant 데이터 백업/복원
"""
import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import hashlib
import tarfile

# 프로젝트 루트 경로 설정
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import DATABASE_URL, QDRANT_HOST, QDRANT_PORT, COLLECTION_NAME
from backend.models.database import SessionLocal
from qdrant_client import QdrantClient


class BackupSystem:
    """백업 시스템 클래스"""
    
    def __init__(self, backup_dir: Optional[Path] = None):
        self.backup_dir = backup_dir or (PROJECT_ROOT / "backups")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.backup_dir / "backup_metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """백업 메타데이터 로드"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {'backups': []}
        return {'backups': []}
    
    def _save_metadata(self):
        """백업 메타데이터 저장"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
    
    def _get_backup_name(self, backup_type: str = "full") -> str:
        """백업 이름 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{backup_type}_{timestamp}"
    
    def backup_postgresql(self, backup_name: str) -> Optional[Path]:
        """PostgreSQL 백업"""
        try:
            # pg_dump 사용
            backup_file = self.backup_dir / f"{backup_name}_postgresql.sql"
            
            # DATABASE_URL에서 정보 추출
            # postgresql://user:password@host:port/database
            import re
            match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', DATABASE_URL)
            if not match:
                print("❌ DATABASE_URL 파싱 실패")
                return None
            
            user, password, host, port, database = match.groups()
            
            # 환경 변수로 비밀번호 설정
            env = os.environ.copy()
            env['PGPASSWORD'] = password
            
            # pg_dump 실행
            cmd = [
                'pg_dump',
                '-h', host,
                '-p', port,
                '-U', user,
                '-d', database,
                '-F', 'c',  # custom format
                '-f', str(backup_file)
            ]
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ PostgreSQL 백업 실패: {result.stderr}")
                return None
            
            print(f"✅ PostgreSQL 백업 완료: {backup_file}")
            return backup_file
        except Exception as e:
            print(f"❌ PostgreSQL 백업 오류: {e}")
            return None
    
    def backup_qdrant(self, backup_name: str) -> Optional[Path]:
        """Qdrant 백업"""
        try:
            # Qdrant 데이터 디렉토리 백업
            qdrant_data_dir = PROJECT_ROOT / "qdrant-data"
            if not qdrant_data_dir.exists():
                print("⚠️  Qdrant 데이터 디렉토리가 없습니다.")
                return None
            
            backup_file = self.backup_dir / f"{backup_name}_qdrant.tar.gz"
            
            # tar.gz로 압축
            with tarfile.open(backup_file, 'w:gz') as tar:
                tar.add(qdrant_data_dir, arcname='qdrant-data')
            
            print(f"✅ Qdrant 백업 완료: {backup_file}")
            return backup_file
        except Exception as e:
            print(f"❌ Qdrant 백업 오류: {e}")
            return None
    
    def backup_metadata(self, backup_name: str) -> Optional[Path]:
        """메타데이터 백업 (작업 로그 등)"""
        try:
            metadata_dir = PROJECT_ROOT / "brain" / "system"
            if not metadata_dir.exists():
                return None
            
            backup_file = self.backup_dir / f"{backup_name}_metadata.tar.gz"
            
            with tarfile.open(backup_file, 'w:gz') as tar:
                tar.add(metadata_dir, arcname='metadata')
            
            print(f"✅ 메타데이터 백업 완료: {backup_file}")
            return backup_file
        except Exception as e:
            print(f"❌ 메타데이터 백업 오류: {e}")
            return None
    
    def create_backup(self, backup_type: str = "full", incremental: bool = False) -> Dict:
        """백업 생성"""
        print(f"\n{'='*60}")
        print(f"백업 생성 시작 ({backup_type})")
        print(f"{'='*60}\n")
        
        backup_name = self._get_backup_name(backup_type)
        backup_info = {
            'name': backup_name,
            'type': backup_type,
            'incremental': incremental,
            'timestamp': datetime.now().isoformat(),
            'files': [],
            'status': 'in_progress'
        }
        
        # PostgreSQL 백업
        print("[1/3] PostgreSQL 백업 중...")
        pg_file = self.backup_postgresql(backup_name)
        if pg_file:
            backup_info['files'].append({
                'type': 'postgresql',
                'path': str(pg_file.relative_to(self.backup_dir)),
                'size': pg_file.stat().st_size
            })
        
        # Qdrant 백업
        print("\n[2/3] Qdrant 백업 중...")
        qdrant_file = self.backup_qdrant(backup_name)
        if qdrant_file:
            backup_info['files'].append({
                'type': 'qdrant',
                'path': str(qdrant_file.relative_to(self.backup_dir)),
                'size': qdrant_file.stat().st_size
            })
        
        # 메타데이터 백업
        print("\n[3/3] 메타데이터 백업 중...")
        metadata_file = self.backup_metadata(backup_name)
        if metadata_file:
            backup_info['files'].append({
                'type': 'metadata',
                'path': str(metadata_file.relative_to(self.backup_dir)),
                'size': metadata_file.stat().st_size
            })
        
        # 백업 검증
        if backup_info['files']:
            backup_info['status'] = 'completed'
            print(f"\n✅ 백업 완료: {backup_name}")
        else:
            backup_info['status'] = 'failed'
            print(f"\n❌ 백업 실패: {backup_name}")
        
        # 메타데이터 저장
        self.metadata['backups'].append(backup_info)
        self.metadata['last_backup'] = backup_info['timestamp']
        self._save_metadata()
        
        return backup_info
    
    def list_backups(self) -> List[Dict]:
        """백업 목록 조회"""
        return self.metadata.get('backups', [])
    
    def restore_postgresql(self, backup_file: Path) -> bool:
        """PostgreSQL 복원"""
        try:
            import re
            match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', DATABASE_URL)
            if not match:
                print("❌ DATABASE_URL 파싱 실패")
                return False
            
            user, password, host, port, database = match.groups()
            
            env = os.environ.copy()
            env['PGPASSWORD'] = password
            
            # pg_restore 실행
            cmd = [
                'pg_restore',
                '-h', host,
                '-p', port,
                '-U', user,
                '-d', database,
                '-c',  # clean (기존 데이터 삭제)
                str(backup_file)
            ]
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ PostgreSQL 복원 실패: {result.stderr}")
                return False
            
            print(f"✅ PostgreSQL 복원 완료")
            return True
        except Exception as e:
            print(f"❌ PostgreSQL 복원 오류: {e}")
            return False
    
    def restore_qdrant(self, backup_file: Path) -> bool:
        """Qdrant 복원"""
        try:
            qdrant_data_dir = PROJECT_ROOT / "qdrant-data"
            
            # 기존 데이터 백업 (안전을 위해)
            if qdrant_data_dir.exists():
                old_backup = self.backup_dir / f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
                with tarfile.open(old_backup, 'w:gz') as tar:
                    tar.add(qdrant_data_dir, arcname='qdrant-data')
                print(f"⚠️  기존 데이터 백업: {old_backup}")
            
            # 기존 데이터 삭제
            if qdrant_data_dir.exists():
                shutil.rmtree(qdrant_data_dir)
            
            # 백업 파일 압축 해제
            with tarfile.open(backup_file, 'r:gz') as tar:
                tar.extractall(PROJECT_ROOT)
            
            print(f"✅ Qdrant 복원 완료")
            return True
        except Exception as e:
            print(f"❌ Qdrant 복원 오류: {e}")
            return False
    
    def restore_backup(self, backup_name: str) -> bool:
        """백업 복원"""
        print(f"\n{'='*60}")
        print(f"백업 복원 시작: {backup_name}")
        print(f"{'='*60}\n")
        
        # 백업 정보 찾기
        backup_info = None
        for backup in self.metadata['backups']:
            if backup['name'] == backup_name:
                backup_info = backup
                break
        
        if not backup_info:
            print(f"❌ 백업을 찾을 수 없습니다: {backup_name}")
            return False
        
        if backup_info['status'] != 'completed':
            print(f"❌ 완료되지 않은 백업입니다: {backup_name}")
            return False
        
        # 각 파일 복원
        for file_info in backup_info['files']:
            file_path = self.backup_dir / file_info['path']
            
            if not file_path.exists():
                print(f"⚠️  백업 파일이 없습니다: {file_path}")
                continue
            
            if file_info['type'] == 'postgresql':
                print(f"\n[PostgreSQL 복원] {file_path.name}")
                self.restore_postgresql(file_path)
            elif file_info['type'] == 'qdrant':
                print(f"\n[Qdrant 복원] {file_path.name}")
                self.restore_qdrant(file_path)
            elif file_info['type'] == 'metadata':
                print(f"\n[메타데이터 복원] {file_path.name}")
                # 메타데이터 복원은 선택적
                pass
        
        print(f"\n✅ 백업 복원 완료: {backup_name}")
        return True
    
    def verify_backup(self, backup_name: str) -> bool:
        """백업 검증"""
        backup_info = None
        for backup in self.metadata['backups']:
            if backup['name'] == backup_name:
                backup_info = backup
                break
        
        if not backup_info:
            return False
        
        # 파일 존재 확인
        for file_info in backup_info['files']:
            file_path = self.backup_dir / file_info['path']
            if not file_path.exists():
                return False
            if file_path.stat().st_size != file_info['size']:
                return False
        
        return True
    
    def delete_backup(self, backup_name: str) -> bool:
        """백업 삭제"""
        backup_info = None
        for i, backup in enumerate(self.metadata['backups']):
            if backup['name'] == backup_name:
                backup_info = backup
                del self.metadata['backups'][i]
                break
        
        if not backup_info:
            return False
        
        # 파일 삭제
        for file_info in backup_info['files']:
            file_path = self.backup_dir / file_info['path']
            if file_path.exists():
                file_path.unlink()
        
        self._save_metadata()
        return True


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='백업 및 복원 시스템')
    parser.add_argument('action', choices=['backup', 'restore', 'list', 'verify', 'delete'],
                       help='작업 선택')
    parser.add_argument('--name', help='백업 이름 (restore, verify, delete 시 필요)')
    parser.add_argument('--type', choices=['full', 'incremental'], default='full',
                       help='백업 타입')
    
    args = parser.parse_args()
    
    backup_system = BackupSystem()
    
    if args.action == 'backup':
        backup_system.create_backup(backup_type=args.type)
    elif args.action == 'restore':
        if not args.name:
            print("❌ --name 옵션이 필요합니다")
            return
        backup_system.restore_backup(args.name)
    elif args.action == 'list':
        backups = backup_system.list_backups()
        print(f"\n{'='*60}")
        print("백업 목록")
        print(f"{'='*60}\n")
        for backup in backups:
            print(f"이름: {backup['name']}")
            print(f"타입: {backup['type']}")
            print(f"시간: {backup['timestamp']}")
            print(f"상태: {backup['status']}")
            print(f"파일 수: {len(backup['files'])}")
            print()
    elif args.action == 'verify':
        if not args.name:
            print("❌ --name 옵션이 필요합니다")
            return
        is_valid = backup_system.verify_backup(args.name)
        if is_valid:
            print(f"✅ 백업 검증 성공: {args.name}")
        else:
            print(f"❌ 백업 검증 실패: {args.name}")
    elif args.action == 'delete':
        if not args.name:
            print("❌ --name 옵션이 필요합니다")
            return
        if backup_system.delete_backup(args.name):
            print(f"✅ 백업 삭제 완료: {args.name}")
        else:
            print(f"❌ 백업 삭제 실패: {args.name}")


if __name__ == "__main__":
    main()
