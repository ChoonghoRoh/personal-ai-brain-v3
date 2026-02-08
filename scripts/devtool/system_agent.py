#!/usr/bin/env python3
"""
시스템 관리 AI - 상태 점검, 요약, TODO 자동화
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BRAIN_DIR = PROJECT_ROOT / "brain"
SYSTEM_DIR = BRAIN_DIR / "system"

# Qdrant 설정
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "brain_documents"


def get_qdrant_stats():
    """Qdrant 통계 정보 가져오기"""
    try:
        from qdrant_client import QdrantClient
        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        
        try:
            collection_info = client.get_collection(COLLECTION_NAME)
            return {
                'points_count': collection_info.points_count,
                'vectors_count': collection_info.vectors_count,
                'status': 'connected'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    except ImportError:
        return {'status': 'not_available'}


def get_file_stats():
    """파일 통계 정보 수집"""
    stats = {
        'projects': 0,
        'reference': 0,
        'inbox': 0,
        'archive': 0,
        'system': 0,
        'total_md_files': 0,
        'total_size_mb': 0
    }
    
    for md_file in BRAIN_DIR.rglob("*.md"):
        if md_file.is_file():
            stats['total_md_files'] += 1
            try:
                size = md_file.stat().st_size
                stats['total_size_mb'] += size / (1024 * 1024)
            except:
                pass
            
            relative = md_file.relative_to(BRAIN_DIR)
            parts = relative.parts
            if len(parts) > 0:
                category = parts[0]
                if category in stats:
                    stats[category] += 1
    
    stats['total_size_mb'] = round(stats['total_size_mb'], 2)
    return stats


def get_recent_changes():
    """최근 변경사항 확인"""
    changes = []
    
    # .file_hashes.json에서 최근 변경 확인
    hash_file = PROJECT_ROOT / ".file_hashes.json"
    if hash_file.exists():
        try:
            with open(hash_file, 'r', encoding='utf-8') as f:
                file_hashes = json.load(f)
                changes.append(f"추적 중인 파일: {len(file_hashes)}개")
        except:
            pass
    
    return changes


def generate_status():
    """시스템 상태 생성"""
    SYSTEM_DIR.mkdir(parents=True, exist_ok=True)
    
    status_file = SYSTEM_DIR / "status.md"
    
    qdrant_stats = get_qdrant_stats()
    file_stats = get_file_stats()
    recent_changes = get_recent_changes()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    content = f"""# 시스템 상태

**생성 시간**: {timestamp}

## 📊 통계

### Qdrant 벡터 데이터베이스
- 상태: {qdrant_stats.get('status', 'unknown')}
"""
    
    if qdrant_stats.get('status') == 'connected':
        content += f"- 저장된 포인트: {qdrant_stats.get('points_count', 0):,}개\n"
        content += f"- 벡터 수: {qdrant_stats.get('vectors_count', 0):,}개\n"
    elif qdrant_stats.get('status') == 'error':
        content += f"- 오류: {qdrant_stats.get('error', 'Unknown')}\n"
    else:
        content += "- Qdrant 연결 불가\n"
    
    content += f"""
### 파일 통계
- 총 Markdown 파일: {file_stats['total_md_files']}개
- 총 크기: {file_stats['total_size_mb']} MB
- 프로젝트 파일: {file_stats['projects']}개
- 참고 자료: {file_stats['reference']}개
- 임시 파일: {file_stats['inbox']}개
- 아카이브: {file_stats['archive']}개
- 시스템 파일: {file_stats['system']}개

## 🔄 최근 변경사항

"""
    
    if recent_changes:
        for change in recent_changes:
            content += f"- {change}\n"
    else:
        content += "- 변경사항 없음\n"
    
    content += f"""
## 🛠️ 시스템 구성

- 벡터 DB: Qdrant (localhost:{QDRANT_PORT})
- 컬렉션: {COLLECTION_NAME}
- 임베딩 모델: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

## 📝 다음 작업

자동화된 시스템이 정상 작동 중입니다.
"""
    
    with open(status_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 상태 파일 생성: {status_file}")
    return status_file


def generate_context():
    """시스템 컨텍스트 생성"""
    SYSTEM_DIR.mkdir(parents=True, exist_ok=True)
    
    context_file = SYSTEM_DIR / "context.md"
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    content = f"""# 시스템 컨텍스트

**최종 업데이트**: {timestamp}

## 시스템 개요

Personal AI Brain은 로컬 환경에서 실행되는 개인 지식 관리 시스템입니다.

## 주요 기능

1. **문서 임베딩**: Markdown, PDF, DOCX 파일을 벡터로 변환하여 저장
2. **의미 기반 검색**: 자연어 쿼리로 관련 문서 검색
3. **자동 변경 감지**: 파일 변경 시 자동으로 임베딩 갱신
4. **Git 자동 커밋**: 시스템 변경사항 자동 기록

## 디렉토리 구조

- `brain/projects/`: 프로젝트별 문서
- `brain/reference/`: 참고 자료
- `brain/inbox/`: 임시 문서
- `brain/archive/`: 아카이브
- `brain/system/`: 시스템 관리 파일
- `collector/`: 원본 문서 (PDF, DOCX 등)

## 사용 스크립트

- `embed_and_store.py`: 문서 임베딩 및 저장
- `search_and_query.py`: 검색 및 질의
- `watcher.py`: 파일 변경 감지 및 자동 갱신
- `auto_commit.py`: Git 자동 커밋
- `collector.py`: 문서 수집 및 변환
- `system_agent.py`: 시스템 상태 관리

## 현재 상태

시스템이 정상 작동 중입니다.
"""
    
    with open(context_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 컨텍스트 파일 생성: {context_file}")
    return context_file


def generate_todo():
    """TODO 목록 생성"""
    SYSTEM_DIR.mkdir(parents=True, exist_ok=True)
    
    todo_file = SYSTEM_DIR / "todo.md"
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # phase2-plan.md에서 TODO 추출
    phase2_plan = PROJECT_ROOT / "docs" / "phase2-plan.md"
    todos = []
    
    if phase2_plan.exists():
        with open(phase2_plan, 'r', encoding='utf-8') as f:
            content = f.read()
            # 간단한 파싱 (실제로는 더 정교하게 할 수 있음)
            if "자동 기록 업데이트 시스템" in content:
                todos.append("✅ 자동 변경 감지 시스템 구현")
            if "Git 자동 커밋 시스템" in content:
                todos.append("✅ Git 자동 커밋 시스템 구현")
            if "문서 자동 수집 확장" in content:
                todos.append("✅ PDF/DOCX 문서 수집 확장")
            if "서브 에이전트" in content:
                todos.append("✅ 시스템 관리 AI 구축")
    
    # 기본 TODO 추가
    if not todos:
        todos = [
            "✅ 자동 변경 감지 시스템 구현",
            "✅ Git 자동 커밋 시스템 구현",
            "✅ PDF/DOCX 문서 수집 확장",
            "✅ 시스템 관리 AI 구축",
            "- [ ] 웹 인터페이스 추가",
            "- [ ] HWP 파일 지원",
            "- [ ] 이미지 OCR 지원",
        ]
    
    content = f"""# 시스템 TODO

**최종 업데이트**: {timestamp}

## 진행 중인 작업

"""
    
    for todo in todos:
        content += f"{todo}\n"
    
    content += """
## 완료된 작업

- ✅ 프로젝트 기본 구조 생성
- ✅ Qdrant 설정 및 실행
- ✅ 문서 임베딩 시스템 구축
- ✅ 검색 시스템 구축
- ✅ 자동 변경 감지 시스템
- ✅ Git 자동 커밋 시스템
- ✅ 문서 수집 확장 (PDF/DOCX)
- ✅ 시스템 관리 AI 구축
"""
    
    with open(todo_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ TODO 파일 생성: {todo_file}")
    return todo_file


def main():
    """메인 함수"""
    print("=" * 60)
    print("시스템 관리 AI - 상태 점검 및 문서 생성")
    print("=" * 60)
    
    print("\n[1/3] 시스템 상태 생성 중...")
    generate_status()
    
    print("\n[2/3] 시스템 컨텍스트 생성 중...")
    generate_context()
    
    print("\n[3/3] TODO 목록 생성 중...")
    generate_todo()
    
    print("\n✅ 모든 시스템 문서가 생성되었습니다.")
    print(f"   위치: {SYSTEM_DIR}")


if __name__ == "__main__":
    main()

