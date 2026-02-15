#!/usr/bin/env python3
"""
docs 폴더의 .md 파일에서 키워드를 추출하고 라벨을 자동 생성하는 스크립트
"""
import sys
from pathlib import Path
from typing import List, Dict, Set, Optional
import re
from collections import Counter
from sqlalchemy.orm import Session

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.models.database import SessionLocal
from backend.models.models import Label, KnowledgeChunk, KnowledgeLabel, Document

DOCS_DIR = PROJECT_ROOT / "docs"
BRAIN_DIR = PROJECT_ROOT / "brain"


def extract_keywords_from_markdown(content: str, top_n: int = 10, use_llm: bool = False) -> List[str]:
    """마크다운 파일에서 키워드 추출

    Args:
        content: 마크다운 파일 내용
        top_n: 추출할 키워드 개수
        use_llm: LLM을 사용한 키워드 추출 여부 (True면 LLM 사용, False면 정규식 기반)
    """
    if use_llm:
        return extract_keywords_with_llm(content, top_n)
    else:
        return extract_keywords_with_regex(content, top_n)


def extract_keywords_with_regex(content: str, top_n: int = 10) -> List[str]:
    """정규식 기반 키워드 추출 (기본 방법)"""
    # 한글 명사 패턴 (간단한 버전)
    korean_noun_pattern = r'[가-힣]{2,}'

    # 마크다운 문법 제거
    content = re.sub(r'#+\s*', '', content)  # 헤더 제거
    content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)  # 볼드 제거
    content = re.sub(r'\*([^*]+)\*', r'\1', content)  # 이탤릭 제거
    content = re.sub(r'`([^`]+)`', r'\1', content)  # 코드 제거
    content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)  # 링크 제거

    # 한글 명사 추출
    nouns = re.findall(korean_noun_pattern, content)

    # 빈도수 계산
    noun_counter = Counter(nouns)

    # 불용어 제거 (간단한 버전)
    stopwords = {'것', '수', '등', '때', '이', '그', '저', '의', '가', '을', '를', '에', '와', '과'}
    filtered_nouns = [(noun, count) for noun, count in noun_counter.items()
                      if noun not in stopwords and len(noun) >= 2]

    # 빈도수 순으로 정렬
    filtered_nouns.sort(key=lambda x: x[1], reverse=True)

    # 상위 N개 반환
    return [noun for noun, _ in filtered_nouns[:top_n]]


def extract_keywords_with_llm(content: str, top_n: int = 10) -> List[str]:
    """LLM을 활용한 키워드 추출 (문맥 이해 기반)"""
    # 마크다운 문법 제거 (LLM에 전달하기 전 정리)
    cleaned_content = re.sub(r'#+\s*', '', content)
    cleaned_content = re.sub(r'\*\*([^*]+)\*\*', r'\1', cleaned_content)
    cleaned_content = re.sub(r'\*([^*]+)\*', r'\1', cleaned_content)

    # 내용이 너무 길면 앞부분만 사용 (토큰 제한 고려)
    # 모델의 컨텍스트 윈도우가 2048 토큰이므로 여유를 두고 1000자로 제한
    # 프롬프트 템플릿이 약 200자, 답변 생성을 위해 200자 여유
    max_length = 1000
    if len(cleaned_content) > max_length:
        cleaned_content = cleaned_content[:max_length] + "..."

    # LLM 프롬프트 생성
    prompt = f"""다음 문서의 내용을 분석하여 핵심 키워드를 추출해주세요.

문서 내용:
{cleaned_content}

요구사항:
1. 문서의 주요 주제와 관련된 의미 있는 키워드만 추출
2. 불용어(것, 수, 등, 때 등)는 제외
3. 일반적인 단어보다 문서에 특화된 전문 용어나 개념을 우선
4. 키워드는 한글로, 2글자 이상
5. 상위 {top_n}개만 추출
6. 중국어(中文)나 일본어로 작성하지 마세요

키워드를 쉼표로 구분하여 나열해주세요. 설명 없이 키워드만 출력하세요.
예시: 프로젝트, 개발, 시스템, API, 데이터베이스"""

    try:
        # 방법 1: Ollama 사용 (로컬 LLM 우선)
        return extract_keywords_with_ollama(prompt, top_n)
    except Exception as e:
        print(f"⚠️  Ollama 오류: {e}, OpenAI API로 대체 시도...")
        try:
            # 방법 2: OpenAI API 사용 (폴백)
            return extract_keywords_with_openai(prompt, top_n)
        except Exception as e2:
            print(f"⚠️  OpenAI API 오류: {e2}, 정규식 기반으로 대체...")
            # 방법 3: 정규식 기반으로 폴백
            return extract_keywords_with_regex(content, top_n)


def extract_keywords_with_openai(prompt: str, top_n: int = 10) -> List[str]:
    """OpenAI API를 사용한 키워드 추출"""
    import os
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("openai 패키지가 설치되지 않았습니다. pip install openai")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다")

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # 또는 "gpt-3.5-turbo" (비용 절감)
        messages=[
            {"role": "system", "content": "당신은 문서 분석 전문가입니다. 문서에서 핵심 키워드를 정확하게 추출합니다."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,  # 일관성 있는 결과를 위해 낮은 temperature
        max_tokens=200
    )

    # 응답에서 키워드 추출
    keywords_text = response.choices[0].message.content.strip()
    keywords = [kw.strip() for kw in keywords_text.split(',') if kw.strip()]

    return keywords[:top_n]


def extract_keywords_with_ollama(prompt: str, top_n: int = 10, model: Optional[str] = None) -> List[str]:
    """Ollama를 사용한 키워드 추출 (로컬 LLM, EEVE-Korean 등)"""
    try:
        from backend.services.ai.ollama_client import ollama_generate
    except ImportError:
        raise ImportError("backend.services.ai.ollama_client를 사용할 수 없습니다. PYTHONPATH에 프로젝트 루트가 있어야 합니다.")

    from backend.config import OLLAMA_MODEL_LIGHT
    use_model = model or OLLAMA_MODEL_LIGHT

    response = ollama_generate(
        prompt,
        max_tokens=200,
        temperature=0.3,
        top_p=0.9,
        timeout=60.0,
        model=use_model,
    )
    if not response:
        raise RuntimeError("Ollama 응답 없음 (서비스 실행 여부 및 모델 로드 확인)")

    from backend.utils.korean_utils import postprocess_korean_keywords
    keywords = postprocess_korean_keywords(response)
    return keywords[:top_n]


def extract_keywords_with_gpt4all(prompt: str, top_n: int = 10, model: Optional[str] = None) -> List[str]:
    """GPT4All 호환 이름 — 실제로는 Ollama 호출 (하위 호환용)."""
    return extract_keywords_with_ollama(prompt, top_n, model=model)


def process_docs_files(use_llm: bool = False, include_brain: bool = True) -> Dict[str, List[str]]:
    """docs 폴더 및 brain 폴더의 모든 .md 파일에서 키워드 추출

    Args:
        use_llm: LLM을 사용한 키워드 추출 여부 (기본값: False, 정규식 기반)
        include_brain: brain 폴더도 처리할지 여부 (기본값: True)
    """
    file_keywords = {}

    # docs 폴더 처리
    for md_file in DOCS_DIR.rglob("*.md"):
        if md_file.is_file():
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                keywords = extract_keywords_from_markdown(content, use_llm=use_llm)
                relative_path = str(md_file.relative_to(PROJECT_ROOT))
                file_keywords[relative_path] = keywords

                method = "LLM" if use_llm else "정규식"
                print(f"✅ [{method}] {relative_path}: {len(keywords)}개 키워드 추출")
                if keywords:
                    print(f"   키워드: {', '.join(keywords[:5])}{'...' if len(keywords) > 5 else ''}")
            except Exception as e:
                print(f"❌ {md_file}: {e}")

    # brain 폴더도 처리 (기존 파일 포함)
    if include_brain:
        for md_file in BRAIN_DIR.rglob("*.md"):
            if md_file.is_file():
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    keywords = extract_keywords_from_markdown(content, use_llm=use_llm)
                    relative_path = str(md_file.relative_to(PROJECT_ROOT))
                    
                    # 이미 docs에서 처리한 파일이면 스킵
                    if relative_path not in file_keywords:
                        file_keywords[relative_path] = keywords

                        method = "LLM" if use_llm else "정규식"
                        print(f"✅ [{method}] {relative_path}: {len(keywords)}개 키워드 추출")
                        if keywords:
                            print(f"   키워드: {', '.join(keywords[:5])}{'...' if len(keywords) > 5 else ''}")
                except Exception as e:
                    print(f"❌ {md_file}: {e}")

    return file_keywords


def create_labels_from_keywords(keywords: Set[str], label_type: str = "keyword", db: Session = None) -> Dict[str, int]:
    """키워드로부터 라벨 생성 (이미 존재하면 ID만 반환)"""
    keyword_to_label_id = {}

    for keyword in keywords:
        # 기존 라벨 확인
        existing = db.query(Label).filter(Label.name == keyword).first()

        if existing:
            keyword_to_label_id[keyword] = existing.id
        else:
            # 새 라벨 생성
            new_label = Label(
                name=keyword,
                label_type=label_type,
                description=f"문서에서 자동 추출된 키워드: {keyword}"
            )
            db.add(new_label)
            db.commit()
            db.refresh(new_label)
            keyword_to_label_id[keyword] = new_label.id
            print(f"  📌 라벨 생성: {keyword} (ID: {new_label.id})")

    return keyword_to_label_id


def auto_label_chunks(file_keywords: Dict[str, List[str]], db: Session):
    """청크에 키워드 기반으로 자동 라벨링"""
    # 모든 키워드 수집
    all_keywords = set()
    for keywords in file_keywords.values():
        all_keywords.update(keywords)

    # 라벨 생성
    keyword_to_label_id = create_labels_from_keywords(all_keywords, label_type="keyword", db=db)

    # 문서별로 처리
    for file_path, keywords in file_keywords.items():
        # 해당 파일의 문서 찾기
        document = db.query(Document).filter(Document.file_path == file_path).first()

        if not document:
            print(f"⚠️  문서를 찾을 수 없음: {file_path}")
            continue

        # 해당 문서의 모든 청크 가져오기
        chunks = db.query(KnowledgeChunk).filter(
            KnowledgeChunk.document_id == document.id
        ).all()

        labeled_count = 0
        for chunk in chunks:
            chunk_content_lower = chunk.content.lower()

            # 청크 내용에 포함된 키워드 찾기
            matched_keywords = [kw for kw in keywords if kw.lower() in chunk_content_lower]

            for keyword in matched_keywords:
                label_id = keyword_to_label_id[keyword]

                # 이미 라벨이 연결되어 있는지 확인
                existing = db.query(KnowledgeLabel).filter(
                    KnowledgeLabel.chunk_id == chunk.id,
                    KnowledgeLabel.label_id == label_id
                ).first()

                if not existing:
                    # 자동 라벨링 (source="ai", status="suggested")
                    knowledge_label = KnowledgeLabel(
                        chunk_id=chunk.id,
                        label_id=label_id,
                        confidence=0.7,  # 키워드 매칭이므로 중간 신뢰도
                        source="ai",
                        status="suggested"
                    )
                    db.add(knowledge_label)
                    labeled_count += 1

        if labeled_count > 0:
            db.commit()
            print(f"  ✅ {file_path}: {labeled_count}개 청크에 라벨 연결")


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="키워드 추출 및 자동 라벨링 (docs 및 brain 폴더)")
    parser.add_argument("--llm", action="store_true", help="LLM을 사용한 키워드 추출 (기본값: 정규식 기반)")
    parser.add_argument("--openai", action="store_true", help="OpenAI API 사용 (--llm과 함께 사용)")
    parser.add_argument("--docs-only", action="store_true", help="docs 폴더만 처리 (기본값: docs + brain 모두 처리)")
    args = parser.parse_args()

    print("=" * 60)
    print("키워드 추출 및 자동 라벨링")
    if args.llm:
        print("모드: LLM 기반 키워드 추출")
        if args.openai:
            print("API: OpenAI")
        else:
            print("API: GPT4All (로컬)")
    else:
        print("모드: 정규식 기반 키워드 추출")
    
    if args.docs_only:
        print("대상: docs 폴더만")
    else:
        print("대상: docs 폴더 + brain 폴더 (기존 파일 포함)")
    print("=" * 60)

    # 1. 키워드 추출
    print("\n[1/3] 파일에서 키워드 추출 중...")
    file_keywords = process_docs_files(use_llm=args.llm, include_brain=not args.docs_only)

    if not file_keywords:
        print("처리할 파일이 없습니다.")
        return

    # 2. DB 연결
    print("\n[2/3] 데이터베이스 연결 중...")
    db = SessionLocal()

    try:
        # 3. 라벨 생성 및 자동 라벨링
        print("\n[3/3] 라벨 생성 및 청크 자동 라벨링 중...")
        auto_label_chunks(file_keywords, db)

        print("\n✅ 완료!")
    finally:
        db.close()


if __name__ == "__main__":
    main()

