# Phase 7.6: 키워드 추출 및 자동 라벨링 기능

## 🎯 목표

`docs` 폴더의 `.md` 파일에서 키워드를 추출하고, 추출된 키워드로 라벨을 자동 생성한 후, 청크 단위로 자동 라벨링하는 기능을 구현한다.

## 📋 현재 시스템 분석

### 현재 구조

- **문서 처리**: `scripts/embed_and_store.py`에서 `brain` 디렉토리의 `.md` 파일을 청크로 분할
- **라벨 관리**: 수동 생성 (`/api/labels` POST)
- **청크-라벨 연결**: 수동 연결 (`/api/labels/chunks/{chunk_id}/labels/{label_id}`)
- **AI 추천**: 기존 라벨 중에서 추천만 수행 (새 라벨 생성 없음)

### 추가 필요 기능

1. `docs` 폴더의 `.md` 파일 처리
2. 키워드 추출 (TF-IDF, 명사 추출 등)
3. 추출된 키워드로 라벨 자동 생성
4. 청크 내용과 키워드 매칭하여 자동 라벨링

---

## 🛠️ 구현 제안

### 1. 키워드 추출 및 라벨 자동 생성 스크립트

**파일**: `scripts/extract_keywords_and_labels.py`

```python
#!/usr/bin/env python3
"""
docs 폴더의 .md 파일에서 키워드를 추출하고 라벨을 자동 생성하는 스크립트
"""
import sys
from pathlib import Path
from typing import List, Dict, Set
import re
from collections import Counter
from sqlalchemy.orm import Session

PROJECT_ROOT = Path(__file__).parent.parent
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
    stopwords = {'것', '수', '등', '때', '것', '이', '그', '저', '의', '가', '을', '를', '에', '와', '과'}
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
    max_length = 3000
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

키워드를 쉼표로 구분하여 나열해주세요. 설명 없이 키워드만 출력하세요.
예시: 프로젝트, 개발, 시스템, API, 데이터베이스"""

    try:
        # 방법 1: OpenAI API 사용 (권장)
        return extract_keywords_with_openai(prompt, top_n)
    except Exception as e:
        print(f"⚠️  OpenAI API 오류: {e}, GPT4All로 대체 시도...")
        try:
            # 방법 2: GPT4All 사용 (로컬)
            return extract_keywords_with_gpt4all(prompt, top_n)
        except Exception as e2:
            print(f"⚠️  GPT4All 오류: {e2}, 정규식 기반으로 대체...")
            # 방법 3: 정규식 기반으로 폴백
            return extract_keywords_with_regex(content, top_n)


def extract_keywords_with_openai(prompt: str, top_n: int = 10) -> List[str]:
    """OpenAI API를 사용한 키워드 추출"""
    import os
    from openai import OpenAI

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


def extract_keywords_with_gpt4all(prompt: str, top_n: int = 10) -> List[str]:
    """GPT4All을 사용한 키워드 추출 (로컬)"""
    try:
        from gpt4all import GPT4All

        model = GPT4All("gguf-gpt4all-j-v1.3-groovy.bin")

        response = model.generate(
            prompt,
            max_tokens=200,
            temp=0.3,  # 일관성 있는 결과
            top_p=0.9
        )

        # 응답에서 키워드 추출
        keywords_text = response.strip()
        # 쉼표나 줄바꿈으로 구분된 키워드 추출
        keywords = []
        for line in keywords_text.split('\n'):
            for kw in line.split(','):
                kw = kw.strip()
                if kw and len(kw) >= 2:
                    keywords.append(kw)

        return keywords[:top_n]
    except ImportError:
        raise ImportError("gpt4all 패키지가 설치되지 않았습니다. pip install gpt4all")


def process_docs_files() -> Dict[str, List[str]]:
    """docs 폴더의 모든 .md 파일에서 키워드 추출"""
    file_keywords = {}

    for md_file in DOCS_DIR.rglob("*.md"):
        if md_file.is_file():
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                keywords = extract_keywords_from_markdown(content)
                relative_path = str(md_file.relative_to(PROJECT_ROOT))
                file_keywords[relative_path] = keywords

                print(f"✅ {relative_path}: {len(keywords)}개 키워드 추출")
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
                    print(f"  🏷️  청크 {chunk.id}에 라벨 '{keyword}' 자동 연결")

        db.commit()


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="docs 폴더 키워드 추출 및 자동 라벨링")
    parser.add_argument("--llm", action="store_true", help="LLM을 사용한 키워드 추출 (기본값: 정규식 기반)")
    parser.add_argument("--openai", action="store_true", help="OpenAI API 사용 (--llm과 함께 사용)")
    args = parser.parse_args()

    print("=" * 60)
    print("docs 폴더 키워드 추출 및 자동 라벨링")
    if args.llm:
        print("모드: LLM 기반 키워드 추출")
        if args.openai:
            print("API: OpenAI")
        else:
            print("API: GPT4All (로컬)")
    else:
        print("모드: 정규식 기반 키워드 추출")
    print("=" * 60)

    # 1. 키워드 추출
    print("\n[1/3] docs 폴더에서 키워드 추출 중...")
    file_keywords = process_docs_files(use_llm=args.llm)

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
```

---

### 2. `embed_and_store.py` 수정: `docs` 폴더도 처리

**파일**: `scripts/embed_and_store.py` 수정 부분

```python
def process_markdown_files(brain_dir: Path, docs_dir: Path = None) -> List[Dict]:
    """brain 디렉토리와 docs 디렉토리의 모든 .md 파일을 처리"""
    documents = []

    # brain 디렉토리 처리
    for md_file in brain_dir.rglob("*.md"):
        if md_file.is_file():
            content = read_markdown_file(md_file)
            if content:
                relative_path = md_file.relative_to(PROJECT_ROOT)
                chunks = split_text(content)

                for idx, chunk in enumerate(chunks):
                    documents.append({
                        'file_path': str(relative_path),
                        'chunk_index': idx,
                        'content': chunk,
                        'full_path': str(md_file)
                    })

    # docs 디렉토리도 처리 (선택적)
    if docs_dir and docs_dir.exists():
        for md_file in docs_dir.rglob("*.md"):
            if md_file.is_file():
                content = read_markdown_file(md_file)
                if content:
                    relative_path = md_file.relative_to(PROJECT_ROOT)
                    chunks = split_text(content)

                    for idx, chunk in enumerate(chunks):
                        documents.append({
                            'file_path': str(relative_path),
                            'chunk_index': idx,
                            'content': chunk,
                            'full_path': str(md_file)
                        })

    return documents
```

그리고 `embed_and_store()` 함수에서:

```python
# 1. Markdown 파일 수집
print("\n[1/5] Markdown 파일 수집 중...")
DOCS_DIR = PROJECT_ROOT / "docs"
documents = process_markdown_files(BRAIN_DIR, docs_dir=DOCS_DIR)
print(f"총 {len(documents)}개의 문서 청크 발견")
```

---

### 3. API 엔드포인트 추가: 문서별 키워드 추출

**파일**: `backend/routers/knowledge.py`에 추가

```python
@router.post("/documents/{document_id}/extract-keywords")
async def extract_keywords_from_document(
    document_id: int,
    top_n: int = 10,
    db: Session = Depends(get_db)
):
    """문서에서 키워드를 추출하고 라벨을 자동 생성"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다")

    # 문서 내용 가져오기
    chunks = db.query(KnowledgeChunk).filter(
        KnowledgeChunk.document_id == document_id
    ).all()

    if not chunks:
        raise HTTPException(status_code=400, detail="문서에 청크가 없습니다")

    # 모든 청크 내용 합치기
    full_content = "\n".join([chunk.content for chunk in chunks])

    # 키워드 추출 (extract_keywords_from_markdown 함수 사용)
    keywords = extract_keywords_from_markdown(full_content, top_n=top_n)

    # 라벨 생성
    keyword_to_label_id = {}
    for keyword in keywords:
        existing = db.query(Label).filter(Label.name == keyword).first()
        if existing:
            keyword_to_label_id[keyword] = existing.id
        else:
            new_label = Label(
                name=keyword,
                label_type="keyword",
                description=f"문서에서 자동 추출된 키워드"
            )
            db.add(new_label)
            db.commit()
            db.refresh(new_label)
            keyword_to_label_id[keyword] = new_label.id

    # 청크에 자동 라벨링
    labeled_count = 0
    for chunk in chunks:
        chunk_content_lower = chunk.content.lower()
        for keyword in keywords:
            if keyword.lower() in chunk_content_lower:
                label_id = keyword_to_label_id[keyword]
                existing = db.query(KnowledgeLabel).filter(
                    KnowledgeLabel.chunk_id == chunk.id,
                    KnowledgeLabel.label_id == label_id
                ).first()

                if not existing:
                    knowledge_label = KnowledgeLabel(
                        chunk_id=chunk.id,
                        label_id=label_id,
                        confidence=0.7,
                        source="ai",
                        status="suggested"
                    )
                    db.add(knowledge_label)
                    labeled_count += 1

    db.commit()

    return {
        "document_id": document_id,
        "keywords": keywords,
        "labels_created": len(keyword_to_label_id),
        "chunks_labeled": labeled_count
    }
```

---

## 📝 사용 흐름

### 1단계: 문서 처리

```bash
python scripts/embed_and_store.py
```

- `brain` 디렉토리와 `docs` 디렉토리의 모든 `.md` 파일을 청크로 분할하여 저장

### 2단계: 키워드 추출 및 자동 라벨링

```bash
python scripts/extract_keywords_and_labels.py
```

- `docs` 폴더의 모든 `.md` 파일에서 키워드 추출
- 추출된 키워드로 라벨 자동 생성
- 각 청크에 키워드 매칭하여 자동 라벨링 (status="suggested")

### 3단계: 결과 확인 및 승인

- Knowledge Admin 페이지에서 "청크 승인 센터" 탭으로 이동
- "suggested" 상태의 라벨이 있는 청크 확인
- 필요시 라벨을 승인(confirmed)하거나 거절

---

## 🔧 향후 개선 사항

### 1. LLM 기반 키워드 추출 (✅ 구현됨)

**OpenAI API 사용** (권장):

- 더 정확한 키워드 추출
- 문맥 이해 기반 필터링
- 도메인 특화 키워드 우선 추출

**GPT4All 사용** (로컬, 무료):

- 오프라인에서도 사용 가능
- OpenAI API 비용 없음
- 처리 속도는 상대적으로 느림

### 2. 더 정교한 키워드 추출

**KoNLPy 사용** (한국어 형태소 분석):

```python
from konlpy.tag import Okt

def extract_keywords_with_konlpy(content: str, top_n: int = 10) -> List[str]:
    """KoNLPy를 사용한 명사 추출"""
    okt = Okt()
    nouns = okt.nouns(content)

    # 빈도수 계산 및 상위 N개 반환
    noun_counter = Counter(nouns)
    filtered_nouns = [(noun, count) for noun, count in noun_counter.items()
                      if len(noun) >= 2]
    filtered_nouns.sort(key=lambda x: x[1], reverse=True)

    return [noun for noun, _ in filtered_nouns[:top_n]]
```

**requirements.txt에 추가**:

```
konlpy>=0.6.0
```

### 2. TF-IDF 기반 키워드 추출

여러 문서 간의 중요도를 고려한 키워드 추출:

```python
from sklearn.feature_extraction.text import TfidfVectorizer

def extract_keywords_with_tfidf(documents: List[str], top_n: int = 10) -> List[str]:
    """TF-IDF를 사용한 키워드 추출"""
    vectorizer = TfidfVectorizer(max_features=100)
    tfidf_matrix = vectorizer.fit_transform(documents)

    feature_names = vectorizer.get_feature_names_out()
    # 각 문서별 상위 키워드 추출
    # ...
```

### 5. 키워드 필터링 개선

- 도메인별 불용어 사전 구축
- 최소 빈도수 임계값 설정
- 키워드 길이 제한 (너무 짧거나 긴 키워드 제외)
- LLM이 자동으로 불용어 필터링 (이미 구현됨)

### 6. UI 개선

- Knowledge Admin에 "키워드 추출" 버튼 추가
- 문서별로 키워드 추출 실행 가능
- 추출된 키워드 미리보기 및 선택적 라벨 생성

---

## ✅ 검증 방법

1. **키워드 추출 테스트**

   ```bash
   python scripts/extract_keywords_and_labels.py
   ```

   - `docs` 폴더의 파일에서 키워드가 정상적으로 추출되는지 확인

2. **라벨 생성 확인**

   ```sql
   SELECT * FROM labels WHERE label_type = 'keyword';
   ```

3. **자동 라벨링 확인**

   ```sql
   SELECT kl.*, l.name, kc.content
   FROM knowledge_labels kl
   JOIN labels l ON kl.label_id = l.id
   JOIN knowledge_chunks kc ON kl.chunk_id = kc.id
   WHERE kl.source = 'ai' AND kl.status = 'suggested';
   ```

4. **UI에서 확인**
   - Knowledge Admin > 청크 승인 센터에서 "suggested" 상태의 라벨 확인
   - 키워드가 청크 내용과 매칭되는지 검증

---

## 📌 참고사항

- 키워드 추출은 간단한 정규식 기반으로 시작하되, 향후 KoNLPy나 TF-IDF 등 더 정교한 방법으로 개선 가능
- 자동 생성된 라벨은 `status="suggested"`로 생성되므로, 관리자가 검토 후 승인 필요
- 기존 라벨과 중복되지 않도록 `Label.name`이 unique 제약 조건을 가짐
- 청크 단위로 라벨링되므로, 하나의 파일에 여러 주제가 있어도 각 청크에 적절한 라벨이 부여됨
