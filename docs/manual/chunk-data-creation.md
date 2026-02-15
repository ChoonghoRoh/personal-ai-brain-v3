# 청크 데이터 생성

지식 청크(Knowledge Chunk)는 **문서 스토리지(brain/, docs/)에 있는 마크다운 파일**을 기준으로 만듭니다. 방법은 **웹 UI**, **API**, **스크립트(마크다운 일괄 처리)** 세 가지입니다.

- **웹 UI**: 관리자 → 청크 생성에서 스토리지 파일을 선택한 뒤 분할·선택·등록합니다.
- **API**: 문서(Document)를 생성한 뒤 청크를 추가합니다 (자동화·연동용).
- **스크립트**: brain/, docs/ 내 .md 파일을 읽어 문서·청크·임베딩까지 한 번에 반영합니다.

---

## 1. API로 청크 생성

청크는 **문서(Document)** 에 속합니다. 문서가 없으면 먼저 문서를 만든 뒤 청크를 추가합니다. 문서는 아래 **1.1 문서 생성**처럼 `POST /api/knowledge/documents` API로 생성합니다.

### 1.1 문서 생성

```http
POST /api/knowledge/documents
Content-Type: application/json

{
  "file_path": "brain/projects/my-project/note.md",
  "file_name": "note.md",
  "file_type": "md",
  "size": 0,
  "project_id": null
}
```

- `project_id`: 선택. 프로젝트 ID를 넣으면 해당 프로젝트에 연결됩니다.
- 동일한 `file_path`가 있으면 400 에러가 납니다.

### 1.2 청크 생성

```http
POST /api/knowledge/chunks?include_suggestions=true
Content-Type: application/json

{
  "document_id": 1,
  "content": "이 청크의 본문 내용입니다.",
  "chunk_index": 0,
  "title": "첫 번째 섹션",
  "title_source": "manual"
}
```

- `document_id`: 위에서 만든 문서 ID.
- `chunk_index`: 같은 문서 내 순서(0부터).
- `title`, `title_source`: 선택. `title_source`는 `"heading"` | `"ai_extracted"` | `"manual"` 등.
- `include_suggestions=true`: 라벨·유사 청크·카테고리 추천을 함께 받을 수 있습니다.

### 1.3 예시 (curl)

```bash
# 문서 생성
DOC=$(curl -s -X POST http://localhost:8001/api/knowledge/documents \
  -H "Content-Type: application/json" \
  -d '{"file_path":"brain/test/sample.md","file_name":"sample.md","file_type":"md"}')
DOC_ID=$(echo $DOC | python3 -c "import sys,json; print(json.load(sys.stdin)['document']['id'])")

# 청크 생성
curl -s -X POST "http://localhost:8001/api/knowledge/chunks?include_suggestions=false" \
  -H "Content-Type: application/json" \
  -d "{\"document_id\":$DOC_ID,\"content\":\"샘플 청크 내용\",\"chunk_index\":0}"
```

---

## 2. 스크립트로 청크 일괄 생성 (마크다운 → DB + Qdrant)

`brain/`, `docs/` 아래 마크다운을 읽어 **문서·청크 생성 + 임베딩·Qdrant 저장**까지 한 번에 하려면 아래 스크립트를 사용합니다.

### 2.1 embed_and_store.py (전체 파이프라인)

```bash
# 프로젝트 루트에서
python scripts/backend/embed_and_store.py
```

- **입력**: `brain/`, `docs/` 내 `.md` 파일 (설정에 따라 경로 변경 가능).
- **동작**:
  - 마크다운을 헤딩 또는 고정 길이로 분할해 청크 생성
  - PostgreSQL에 Document·KnowledgeChunk 저장
  - 임베딩 생성 후 Qdrant에 저장
- **옵션**: 스크립트 내부 인자로 `use_heading_split`, `use_ai_for_title`, `recreate_collection` 등 설정 가능.

### 2.2 create_chunks.py (문서·청크만 DB에 생성)

임베딩/Qdrant 없이 **문서 1개 + 청크 여러 개**만 DB에 넣고 싶을 때:

```bash
python scripts/create_chunks.py --file-path brain/test/sample.md --content "첫 번째 청크 내용"
# 또는 여러 청크를 파일에서 읽어서 생성
python scripts/create_chunks.py --file-path brain/test/sample.md --from-file sample_chunks.txt
```

- 서버 기동 없이 DB만 사용합니다.
- 검색/유사도는 이후 `embed_and_store.py`를 실행해 임베딩을 채우면 사용할 수 있습니다.

---

## 3. 요약

| 방법                                                               | 용도                                                   |
| ------------------------------------------------------------------ | ------------------------------------------------------ |
| **웹 UI (관리자 → 청크 생성)**                                     | brain/, docs/ 스토리지 파일 선택 → 분할·선택 → DB 등록 |
| **POST /api/knowledge/documents** + **POST /api/knowledge/chunks** | 문서·청크를 1건씩 생성 (자동화·연동)                   |
| **scripts/backend/embed_and_store.py**                             | 마크다운 전체를 청크로 만들고 임베딩·Qdrant까지 반영   |
| **scripts/create_chunks.py**                                       | 문서 1개 + 청크 N개만 DB에 빠르게 생성 (테스트/시드용) |

청크는 항상 **문서(document_id)** 에 소속되며, 문서의 **file_path** 는 스토리지(brain/, docs/) 경로와 맞추는 것이 좋습니다.
