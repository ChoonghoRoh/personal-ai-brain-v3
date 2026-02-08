# Personal AI Brain – Local Test Setup Guide (Mac + M1)

## ✅ 전략 확정

1️⃣ 현재 단계

- macOS(Local) + Python venv
- Qdrant만 Docker 사용

2️⃣ 이후 업그레이드

- 전체 환경 Docker 기반으로 이전 예정

---

## 1️⃣ 프로젝트 기본 구조 생성

현재 폴더 personal-ai-brain

현재 폴더에서 프로젝트 폴더 구성 personal-ai-brain 부분 중복으로 생기지 않게 함.

폴더 생성:

```bash
mkdir -p ~/brain/projects
mkdir -p ~/brain/reference
mkdir -p ~/brain/inbox
mkdir -p ~/brain/archive
mkdir -p ~/scripts
mkdir -p ~/docs
```

Git 초기화:

```bash
git init
echo "venv/" >> .gitignore
echo "__pycache__/" >> .gitignore
git add .
git commit -m "init: base structure created"
```

---

## 2️⃣ 테스트 프로젝트 생성 + 기본 문서

```bash
mkdir -p ~/brain/projects/alpha-project
```

다음 파일 생성

- context.md
- log.md
- ideas.md
- roadmap.md

내용은 간단히 작성 (초기 수동 단계)

---

## 3️⃣ Qdrant 실행 (Docker)

```bash
docker run -p 6333:6333 -p 6334:6334 \
  -v ~/personal-ai-brain/qdrant-data:/qdrant/storage \
  qdrant/qdrant
```

확인:

```
http://localhost:6333/dashboard
```

대시보드 보이면 OK

---

## 4️⃣ Python venv + 기본 패키지 준비

```bash
cd ~/scripts
python3 -m venv venv
source venv/bin/activate
pip install qdrant-client gpt4all sentence-transformers pypdf python-docx
```

---

## 🎯 1단계 목표

✔️ 폴더 구조 생성 완료
✔️ Git 관리 시작
✔️ `.md` 문서 등록
✔️ Qdrant 실행 확인
✔️ Python venv + 기본 라이브러리 설치

---

## ▶️ 다음 단계(예정)

- `.md → embedding → Qdrant 저장` 코드 작성
- Qdrant 검색 + GPT4All 응답 테스트
- 자동 기록 업데이트 설계
- Git 자동 커밋 자동화 1차 설계
