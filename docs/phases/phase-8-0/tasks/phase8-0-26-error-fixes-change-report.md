# Phase 8-0-26: 에러 수정 및 문서 경로 동기화 변경 보고서

**작성일**: 2026-01-11  
**작업 항목**: 8-0-26 - 에러 수정 및 문서 경로 동기화  
**버전**: 8-0-26

---

## 📋 변경 개요

다음 에러들을 수정하고 문서 경로 동기화 기능을 추가했습니다:

1. **검색 오류 수정** (`TypeError: results.map is not a function`)
2. **문서 경로 동기화 기능 추가**
3. **프론트엔드 JavaScript 오류 수정** (`apiUrl is not defined`)
4. **이중 URL 인코딩 방지**
5. **전체 문서 재임베딩 및 DB 동기화**

---

## 🔧 변경 사항 상세

### 1. 검색 오류 수정 (`web/public/js/search.js`)

#### 문제점

- API 응답이 객체 형식(`{"results": [...], "total": ...}`)인데 배열로 처리하여 `results.map is not a function` 오류 발생

#### 해결 방법

- API 응답 형식 검증 로직 추가
- 배열/객체 자동 감지 및 처리
- 브라우저 캐시 방지를 위한 버전 파라미터 추가

**변경된 코드**:

```javascript
const data = await response.json();

// API 응답이 객체인 경우 results 속성 사용, 배열인 경우 직접 사용
let results = [];
if (Array.isArray(data)) {
  results = data;
} else if (data && typeof data === "object") {
  results = Array.isArray(data.results) ? data.results : [];
}

// results가 배열인지 최종 확인
if (!Array.isArray(results)) {
  console.error("검색 결과가 배열이 아닙니다:", typeof results, results);
  resultsDiv.innerHTML = '<div class="no-results">검색 결과 형식 오류가 발생했습니다.</div>';
  return;
}
```

**파일**: `web/public/js/search.js`, `web/src/pages/search.html`

---

### 2. 문서 경로 동기화 기능 추가

#### 문제점

- DB에 저장된 문서 경로와 실제 파일 시스템의 경로가 불일치
- 폴더 구조 변경 시 문서를 찾을 수 없음

#### 해결 방법

- 문서 경로 동기화 서비스 생성
- 파일 해시와 파일명으로 문서 매칭
- 자동 경로 업데이트 기능

**새로 생성된 파일**:

- `backend/services/document_sync_service.py`

**주요 기능**:

1. **`sync_document_paths()`**: 전체 문서 경로 동기화
2. **`sync_single_document()`**: 단일 문서 경로 동기화
3. **`find_document_by_hash()`**: 파일 해시로 문서 찾기

**API 엔드포인트 추가**:

- `POST /api/documents/sync`: 전체 문서 경로 동기화
- `POST /api/documents/sync/{file_path}`: 단일 문서 경로 동기화
- `GET /api/documents?sync=true`: 문서 목록 조회 시 자동 동기화

**파일**:

- `backend/services/document_sync_service.py` (신규)
- `backend/routers/documents.py` (수정)

---

### 3. 프론트엔드 JavaScript 오류 수정 (`web/public/js/document.js`)

#### 문제점

- `apiUrl is not defined` 오류 발생
- 문서를 찾을 수 없을 때 경로 동기화 시도하지 않음

#### 해결 방법

- `apiUrl` 변수 제거 및 실제 URL 사용
- 404 오류 시 자동 경로 동기화 시도
- 이중 URL 인코딩 방지 로직 추가

**변경된 코드**:

```javascript
// 이중 인코딩 방지: 이미 인코딩된 경우 디코딩
try {
  const decoded = decodeURIComponent(documentId);
  if (decoded !== documentId && !decoded.includes("%")) {
    documentId = decoded;
  }
} catch (e) {
  // 디코딩 실패 시 원본 사용
}

// 404 오류인 경우 경로 동기화 시도
if (response.status === 404) {
  console.log("문서를 찾을 수 없습니다. 경로 동기화 시도...", documentId);
  try {
    const syncResponse = await fetch(`/api/documents/sync/${encodeURIComponent(documentId)}`, {
      method: "POST",
    });

    if (syncResponse.ok) {
      const syncData = await syncResponse.json();
      console.log("경로 동기화 완료:", syncData);

      // 동기화 후 다시 문서 로드 시도
      const retryResponse = await fetch(`/api/documents/${encodeURIComponent(documentId)}`);
      if (retryResponse.ok) {
        const retryData = await retryResponse.json();
        documentId = retryData.file_path || documentId;
        return loadDocument();
      }
    }
  } catch (syncError) {
    console.error("경로 동기화 오류:", syncError);
  }
}
```

**파일**: `web/public/js/document.js`

---

### 4. 백엔드 문서 조회 개선 (`backend/routers/documents.py`)

#### 개선 사항

- 문서를 찾을 수 없을 때 파일명으로 검색
- `brain/`과 `docs/` 디렉토리 모두에서 검색
- 자동 경로 동기화 시도

**변경된 로직**:

```python
if not doc_path.exists() or not doc_path.is_file():
    # 파일을 찾을 수 없는 경우, 파일명으로 검색하여 경로 동기화 시도
    file_name = Path(document_id).name if "/" in document_id else document_id

    # brain과 docs 디렉토리에서 파일 검색
    found_files = []
    for search_dir in [BRAIN_DIR, PROJECT_ROOT / "docs"]:
        if search_dir.exists():
            found_files.extend(list(search_dir.rglob(file_name)))

    if found_files:
        # 첫 번째로 찾은 파일로 경로 동기화 시도
        found_path = found_files[0]
        found_relative = str(found_path.relative_to(PROJECT_ROOT))
        # ... 경로 동기화 로직
```

**파일**: `backend/routers/documents.py`

---

### 5. 문서 재임베딩 스크립트 개선 (`scripts/embed_and_store.py`)

#### 문제점

- `KnowledgeLabel` 삭제 로직 누락으로 외래 키 제약 조건 오류 발생

#### 해결 방법

- `KnowledgeLabel` 삭제 로직 추가
- 관계 삭제 순서 개선

**변경된 코드**:

```python
# 해당 청크와 관련된 모든 관계 삭제
db.query(KnowledgeRelation).filter(
    (KnowledgeRelation.source_chunk_id == chunk.id) |
    (KnowledgeRelation.target_chunk_id == chunk.id)
).delete()
# 해당 청크와 관련된 모든 라벨 삭제
db.query(KnowledgeLabel).filter(
    KnowledgeLabel.chunk_id == chunk.id
).delete()
```

**파일**: `scripts/embed_and_store.py`

---

### 6. 문서 경로 동기화 서비스 개선

#### 개선 사항

- 파일이 없을 때 파일명으로 검색
- `brain/`과 `docs/` 디렉토리 모두에서 검색

**변경된 로직**:

```python
def sync_single_document(file_path: str, db: Session, qdrant_client: QdrantClient):
    # 파일이 존재하지 않으면 파일명으로 검색
    if not full_path.exists():
        file_name = Path(file_path).name

        # brain과 docs 디렉토리에서 파일 검색
        found_files = []
        for search_dir in [PROJECT_ROOT / "brain", PROJECT_ROOT / "docs"]:
            if search_dir.exists():
                found_files.extend(list(search_dir.rglob(file_name)))

        if found_files:
            found_path = found_files[0]
            found_relative = str(found_path.relative_to(PROJECT_ROOT))
            file_path = found_relative
            full_path = found_path
```

**파일**: `backend/services/document_sync_service.py`

---

## 📊 테스트 결과

### 1. 검색 기능 테스트

- ✅ 검색 결과 정상 표시
- ✅ API 응답 형식 자동 감지 및 처리
- ✅ 브라우저 캐시 문제 해결

### 2. 문서 경로 동기화 테스트

- ✅ 전체 문서 경로 동기화 실행 완료
- ✅ 단일 문서 경로 동기화 정상 작동
- ✅ 파일명으로 문서 검색 및 매칭 성공

### 3. 문서 조회 테스트

- ✅ 경로가 변경된 문서도 정상 조회
- ✅ 자동 경로 동기화 정상 작동
- ✅ 이중 URL 인코딩 방지 확인

### 4. 재임베딩 테스트

- ✅ 전체 문서 재임베딩 완료
- ✅ PostgreSQL: 332개 청크 저장
- ✅ Qdrant: 332개 포인트 저장
- ✅ 외래 키 제약 조건 오류 해결

---

## 🔍 수정된 파일 목록

### 신규 생성

1. `backend/services/document_sync_service.py` - 문서 경로 동기화 서비스

### 수정된 파일

1. `web/public/js/search.js` - 검색 오류 수정
2. `web/src/pages/search.html` - 캐시 방지 버전 파라미터 추가
3. `web/public/js/document.js` - apiUrl 오류 수정, 자동 경로 동기화
4. `backend/routers/documents.py` - 문서 조회 개선, 동기화 API 추가
5. `backend/services/document_sync_service.py` - 파일 검색 로직 개선
6. `scripts/embed_and_store.py` - KnowledgeLabel 삭제 로직 추가

---

## ✅ 해결된 문제

1. ✅ `TypeError: results.map is not a function` - 검색 결과 처리 오류
2. ✅ `apiUrl is not defined` - 프론트엔드 JavaScript 오류
3. ✅ 문서 경로 불일치 - DB와 파일 시스템 동기화
4. ✅ 이중 URL 인코딩 - `docs%252F` → `docs%2F`
5. ✅ 외래 키 제약 조건 오류 - KnowledgeLabel 삭제 로직 추가

---

## 📝 사용 방법

### 전체 문서 경로 동기화

```bash
# API 호출
curl -X POST "http://localhost:8001/api/documents/sync"

# 또는 문서 목록 조회 시 자동 동기화
curl "http://localhost:8001/api/documents?sync=true"
```

### 단일 문서 경로 동기화

```bash
curl -X POST "http://localhost:8001/api/documents/sync/docs/phases/phase-7-0/phase7-upgrade-test-scenarios.md"
```

### 전체 문서 재임베딩

```bash
cd /Users/map-rch/WORKS/personal-ai-brain-v2
source scripts/venv/bin/activate
python3 scripts/embed_and_store.py --recreate
```

---

## 🎯 향후 개선 사항

1. **자동 경로 동기화**: 파일 변경 감지 시 자동 동기화
2. **경로 변경 이력**: 문서 경로 변경 이력 추적
3. **경로 검증**: 문서 조회 시 경로 유효성 검증 강화
4. **배치 동기화**: 대량 문서 경로 변경 시 배치 처리

---

**작업 상태**: ✅ 완료  
**테스트 상태**: ✅ 통과  
**다음 작업**: 계속 진행
