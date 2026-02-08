"""프로젝트 파일 분석 유틸리티 - Task Plan 생성을 위한 컨텍스트 수집"""
import os
import re
import logging
from pathlib import Path
from typing import List, Dict, Optional, Set

from backend.config import PROJECT_ROOT

logger = logging.getLogger(__name__)

# 분석 대상 파일 확장자
CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".vue", ".html", ".css", ".scss",
    ".json", ".yaml", ".yml", ".toml", ".md", ".sql"
}

# 제외할 디렉터리
EXCLUDE_DIRS = {
    "__pycache__", "node_modules", ".git", ".venv", "venv", "env",
    "dist", "build", ".pytest_cache", ".mypy_cache", "qdrant-data",
    ".claude", ".idea", ".vscode"
}

# 최대 파일 크기 (100KB)
MAX_FILE_SIZE = 100 * 1024


def find_related_files(
    keywords: List[str],
    context_hint: Optional[str] = None,
    workspace_root: Optional[str] = None,
    max_files: int = 20
) -> List[Dict]:
    """
    키워드와 컨텍스트 힌트로 관련 파일 찾기.

    Args:
        keywords: 검색 키워드 목록 (task 제목에서 추출)
        context_hint: 추가 컨텍스트 힌트 (예: "backend API", "frontend component")
        workspace_root: 프로젝트 루트 경로
        max_files: 반환할 최대 파일 수

    Returns:
        관련 파일 목록 [{path, relevance_score, match_type}]
    """
    root = Path(workspace_root) if workspace_root else PROJECT_ROOT
    results = []
    seen_files: Set[str] = set()

    # 키워드 정규화
    normalized_keywords = [kw.lower().strip() for kw in keywords if kw.strip()]

    # 컨텍스트 힌트에서 추가 키워드 추출
    if context_hint:
        hint_words = re.findall(r'\w+', context_hint.lower())
        normalized_keywords.extend([w for w in hint_words if len(w) > 2])

    # 디렉터리 힌트 추출 (backend, frontend, services 등)
    dir_hints = []
    for kw in normalized_keywords:
        if kw in ("backend", "frontend", "web", "services", "routers", "models", "scripts"):
            dir_hints.append(kw)

    def score_file(file_path: Path, content: str) -> tuple:
        """파일 관련성 점수 계산"""
        score = 0
        match_types = []
        relative = str(file_path.relative_to(root))
        relative_lower = relative.lower()
        content_lower = content.lower()

        for kw in normalized_keywords:
            # 파일명에 키워드 포함
            if kw in file_path.name.lower():
                score += 10
                match_types.append(f"filename:{kw}")
            # 경로에 키워드 포함
            elif kw in relative_lower:
                score += 5
                match_types.append(f"path:{kw}")
            # 파일 내용에 키워드 포함
            if kw in content_lower:
                count = content_lower.count(kw)
                score += min(count * 2, 10)  # 최대 10점
                if f"content:{kw}" not in match_types:
                    match_types.append(f"content:{kw}")

        # 디렉터리 힌트 보너스
        for dh in dir_hints:
            if dh in relative_lower.split(os.sep)[:3]:  # 상위 3단계 경로만
                score += 3

        return score, match_types

    # 파일 탐색
    for dirpath, dirnames, filenames in os.walk(root):
        # 제외 디렉터리 건너뛰기
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]

        rel_dir = Path(dirpath).relative_to(root)

        for filename in filenames:
            file_path = Path(dirpath) / filename

            # 확장자 필터
            if file_path.suffix.lower() not in CODE_EXTENSIONS:
                continue

            # 이미 처리한 파일 건너뛰기
            rel_path_str = str(file_path.relative_to(root))
            if rel_path_str in seen_files:
                continue
            seen_files.add(rel_path_str)

            # 파일 크기 체크
            try:
                if file_path.stat().st_size > MAX_FILE_SIZE:
                    continue
            except OSError:
                continue

            # 파일 읽기
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            score, match_types = score_file(file_path, content)

            if score > 0:
                results.append({
                    "path": rel_path_str,
                    "relevance_score": score,
                    "match_types": match_types,
                    "size": len(content),
                })

    # 점수 순 정렬 후 상위 N개 반환
    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    return results[:max_files]


def collect_file_context(
    file_paths: List[str],
    workspace_root: Optional[str] = None,
    max_content_per_file: int = 5000,
    max_total_content: int = 30000
) -> Dict:
    """
    파일 목록에서 컨텍스트 수집.

    Args:
        file_paths: 파일 경로 목록 (상대 경로)
        workspace_root: 프로젝트 루트 경로
        max_content_per_file: 파일당 최대 문자 수
        max_total_content: 전체 최대 문자 수

    Returns:
        {files: [{path, content, truncated}], total_chars, file_count}
    """
    root = Path(workspace_root) if workspace_root else PROJECT_ROOT
    collected = []
    total_chars = 0

    for rel_path in file_paths:
        if total_chars >= max_total_content:
            break

        file_path = root / rel_path
        if not file_path.exists():
            continue

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            truncated = False

            # 파일 내용 제한
            if len(content) > max_content_per_file:
                content = content[:max_content_per_file]
                truncated = True

            # 전체 제한 체크
            remaining = max_total_content - total_chars
            if len(content) > remaining:
                content = content[:remaining]
                truncated = True

            total_chars += len(content)
            collected.append({
                "path": rel_path,
                "content": content,
                "truncated": truncated,
            })
        except Exception as e:
            logger.warning(f"파일 읽기 실패: {rel_path} - {e}")

    return {
        "files": collected,
        "total_chars": total_chars,
        "file_count": len(collected),
    }


def extract_keywords_from_task(task_title: str, task_description: str = "") -> List[str]:
    """
    Task 제목과 설명에서 검색 키워드 추출.

    Args:
        task_title: Task 제목
        task_description: Task 설명 (선택)

    Returns:
        추출된 키워드 목록
    """
    text = f"{task_title} {task_description}".lower()

    # 일반적인 불용어 제거
    stopwords = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "must", "shall", "can", "need", "to", "of",
        "in", "for", "on", "with", "at", "by", "from", "as", "into", "through",
        "during", "before", "after", "above", "below", "between", "under",
        "this", "that", "these", "those", "it", "its", "and", "or", "but",
        "if", "then", "else", "when", "where", "why", "how", "all", "each",
        "every", "both", "few", "more", "most", "other", "some", "such", "no",
        "not", "only", "own", "same", "so", "than", "too", "very", "just",
        # 한국어 불용어
        "및", "등", "를", "을", "이", "가", "은", "는", "에", "에서", "로", "으로",
        "와", "과", "의", "한", "할", "하는", "있는", "위한", "통한", "대한"
    }

    # 단어 추출 (영문, 한글, 숫자)
    words = re.findall(r'[a-zA-Z가-힣]+[a-zA-Z가-힣0-9]*', text)

    # 필터링
    keywords = []
    for word in words:
        if len(word) < 2:
            continue
        if word in stopwords:
            continue
        if word not in keywords:  # 중복 제거
            keywords.append(word)

    return keywords[:15]  # 최대 15개


def get_project_structure(
    workspace_root: Optional[str] = None,
    max_depth: int = 3
) -> Dict:
    """
    프로젝트 디렉터리 구조 요약.

    Args:
        workspace_root: 프로젝트 루트 경로
        max_depth: 최대 탐색 깊이

    Returns:
        {directories: [str], key_files: [str]}
    """
    root = Path(workspace_root) if workspace_root else PROJECT_ROOT
    directories = []
    key_files = []

    # 주요 파일 패턴
    key_patterns = {
        "README.md", "requirements.txt", "package.json", "docker-compose.yml",
        "Dockerfile", "config.py", "settings.py", "main.py", "app.py"
    }

    def scan_dir(path: Path, depth: int):
        if depth > max_depth:
            return

        try:
            for entry in sorted(path.iterdir()):
                if entry.name in EXCLUDE_DIRS:
                    continue
                if entry.name.startswith("."):
                    continue

                rel_path = str(entry.relative_to(root))

                if entry.is_dir():
                    directories.append(rel_path + "/")
                    scan_dir(entry, depth + 1)
                elif entry.name in key_patterns:
                    key_files.append(rel_path)
        except PermissionError:
            pass

    scan_dir(root, 0)

    return {
        "directories": directories[:50],  # 최대 50개
        "key_files": key_files,
    }
