# Phase 7.9.5: Knowledge Chunk 제목 필드 추가 및 의미 단위 분할 개선

**작성일**: 2026-01-09  
**작업자**: 시스템  
**상태**: 완료 ✅

---

## 📋 작업 개요

Knowledge Chunk에 제목(title) 필드를 추가하고, 마크다운 문서를 헤딩 기반으로 의미 단위로 분할하는 기능을 구현했습니다. 이를 통해 청크의 구조화된 제목 정보를 관리하고, 더 의미 있는 단위로 문서를 분할할 수 있게 되었습니다.

---

## 🎯 작업 목표

1. **데이터베이스 스키마 확장**: KnowledgeChunk 모델에 `title`, `title_source` 필드 추가
2. **문서 분할 로직 개선**: 마크다운 헤딩 기반 의미 단위 분할 구현
3. **AI 기반 제목 추출**: 헤딩이 없는 경우 AI로 제목 생성 (선택적)
4. **프론트엔드 업데이트**: 청크 목록 및 상세 페이지에 제목 표시
5. **기존 데이터 마이그레이션**: 기존 청크에 title 필드 추가

---

## 🔧 구현 내용

### 1. 데이터베이스 모델 변경

**파일**: `backend/models/models.py`

```python
class KnowledgeChunk(Base):
    # ... 기존 필드들 ...
    
    # Phase 7.9.5: Title field
    title = Column(String, nullable=True)  # Chunk title extracted from heading or AI
    title_source = Column(String, nullable=True)  # "heading" | "ai_extracted" | "manual" | null
```

**변경 사항**:
- `title`: 청크 제목 (헤딩에서 추출하거나 AI로 생성)
- `title_source`: 제목 출처
  - `"heading"`: 마크다운 헤딩에서 추출
  - `"ai_extracted"`: AI로 생성
  - `"manual"`: 수동 입력 (향후 기능)
  - `null`: 제목 없음

---

### 2. API 응답 모델 업데이트

**파일**: `backend/routers/knowledge.py`

**변경 사항**:
- `ChunkResponse` 모델에 `title`, `title_source` 필드 추가
- `ChunkDetailResponse` 모델에 `title`, `title_source` 필드 추가
- API 응답에 제목 정보 자동 포함

```python
class ChunkResponse(BaseModel):
    # ... 기존 필드들 ...
    title: Optional[str] = None  # Phase 7.9.5: Chunk title
    title_source: Optional[str] = None  # Phase 7.9.5: Title source
```

---

### 3. 문서 분할 로직 개선

**파일**: `scripts/embed_and_store.py`

#### 3.1 마크다운 헤딩 기반 분할

**함수**: `split_markdown_by_headings()`

**주요 기능**:
- 마크다운 헤딩(`#`, `##`, `###` 등)을 기준으로 의미 단위 분할
- 각 헤딩을 청크의 제목으로 추출
- 최소 크기(`min_chunk_size`) 미만인 청크는 이전 청크에 병합
- 최대 크기(`max_chunk_size`) 초과 청크는 하위 헤딩으로 재분할

**처리 과정**:
1. 텍스트를 줄 단위로 분할
2. 헤딩 패턴(`^(#{1,6})\s+(.+)$`) 매칭
3. 헤딩 발견 시 현재 청크 저장 및 새 청크 시작
4. 헤딩 텍스트에서 마크다운 문법 제거 (링크, 볼드, 이탤릭 등)
5. 최소 크기 체크 및 병합 처리
6. 큰 청크 재분할 처리

**제목 추출 로직**:
```python
# 헤딩 텍스트에서 마크다운 문법 제거
title_text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', title_text)  # 링크
title_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', title_text)  # 볼드
title_text = re.sub(r'\*([^*]+)\*', r'\1', title_text)  # 이탤릭
title_text = re.sub(r'`([^`]+)`', r'\1', title_text)  # 코드
```

#### 3.2 AI 기반 제목 추출

**함수**: `extract_title_with_ai()`

**주요 기능**:
- GPT4All을 사용하여 청크 내용에서 제목 추출
- 헤딩이 없는 경우에만 사용 (선택적)
- 제목은 최대 50자로 제한

**사용 조건**:
- `use_ai_for_title=True` 옵션 활성화 시
- 헤딩이 없는 청크에 대해서만 실행

#### 3.3 폴백 분할 로직

**함수**: `split_text_fallback()`

**주요 기능**:
- 헤딩이 없거나 청크가 생성되지 않은 경우 기존 방식으로 분할
- 고정 크기(`chunk_size`)와 오버랩(`overlap`) 기반 분할
- 제목 추출 시도 (헤딩 우선, 없으면 AI)

---

### 4. 프론트엔드 업데이트

#### 4.1 청크 목록 페이지

**파일**: `web/src/pages/knowledge.html`

**변경 사항**:
- 청크 카드에 제목 표시 추가
- 제목이 있는 경우 파란색 굵은 글씨로 표시
- 제목이 없는 경우 표시하지 않음

```javascript
${chunk.title ? `<div class="chunk-title" style="font-weight: 600; color: #2563eb; margin: 8px 0; font-size: 14px;">${chunk.title}</div>` : ""}
```

#### 4.2 청크 상세 페이지

**파일**: `web/src/pages/knowledge-detail.html`

**변경 사항**:
- 페이지 헤더에 청크 제목 표시
- 제목이 있으면 제목 사용, 없으면 내용의 첫 50자 사용

```javascript
const titleText = chunk.title || (chunk.content ? chunk.content.substring(0, 50).replace(/\n/g, " ").trim() + (chunk.content.length > 50 ? "..." : "") : "청크 상세");
```

---

### 5. 데이터베이스 마이그레이션

**파일**: `scripts/migrate_phase7_upgrade.py`

**변경 사항**:
- `knowledge_chunks` 테이블에 `title` 컬럼 추가
- `knowledge_chunks` 테이블에 `title_source` 컬럼 추가
- PostgreSQL 호환성 고려 (컬럼 존재 여부 확인 후 추가)

**마이그레이션 로직**:
```python
# 컬럼 존재 여부 확인
result = db.execute(text("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name='knowledge_chunks' AND column_name='title'
"""))
if not result.fetchone():
    db.execute(text("ALTER TABLE knowledge_chunks ADD COLUMN title VARCHAR"))
    db.commit()
```

---

## 📊 작업 결과

### 완료된 작업

- ✅ KnowledgeChunk 모델에 `title`, `title_source` 필드 추가
- ✅ API 응답 모델에 제목 필드 추가
- ✅ 마크다운 헤딩 기반 의미 단위 분할 구현
- ✅ AI 기반 제목 추출 기능 구현 (선택적)
- ✅ 프론트엔드 청크 목록에 제목 표시
- ✅ 프론트엔드 청크 상세 페이지에 제목 표시
- ✅ 데이터베이스 마이그레이션 스크립트 실행 완료

### 개선 효과

1. **구조화된 제목 관리**: 각 청크에 명확한 제목 정보 저장
2. **의미 단위 분할**: 헤딩 기반으로 문서의 논리적 구조 반영
3. **사용자 경험 개선**: 청크 목록에서 제목으로 빠른 식별 가능
4. **확장성**: 향후 제목 기반 검색, 필터링 기능 추가 가능

---

## 🔄 관련 파일

### 백엔드
- `backend/models/models.py` - KnowledgeChunk 모델에 title 필드 추가
- `backend/routers/knowledge.py` - API 응답 모델에 title 필드 추가

### 스크립트
- `scripts/embed_and_store.py` - 헤딩 기반 분할 및 제목 추출 로직 구현
- `scripts/migrate_phase7_upgrade.py` - 데이터베이스 마이그레이션 스크립트

### 프론트엔드
- `web/src/pages/knowledge.html` - 청크 목록에 제목 표시
- `web/src/pages/knowledge-detail.html` - 청크 상세 페이지에 제목 표시

---

## 🧪 테스트 시나리오

### 1. 마크다운 헤딩 기반 분할 테스트

**전제 조건**:
- 헤딩이 포함된 마크다운 문서 존재
- `use_heading_split=True` 옵션 활성화

**예상 결과**:
- 각 헤딩이 청크의 시작점이 됨
- 헤딩 텍스트가 청크의 제목으로 저장됨
- `title_source`가 `"heading"`으로 설정됨

### 2. AI 제목 추출 테스트

**전제 조건**:
- 헤딩이 없는 텍스트 청크
- `use_ai_for_title=True` 옵션 활성화
- GPT4All 모델 사용 가능

**예상 결과**:
- AI가 청크 내용을 분석하여 제목 생성
- `title_source`가 `"ai_extracted"`로 설정됨
- 제목이 최대 50자로 제한됨

### 3. 프론트엔드 제목 표시 테스트

**전제 조건**:
- 제목이 있는 청크와 없는 청크 모두 존재

**예상 결과**:
- 청크 목록에서 제목이 있는 청크는 제목 표시
- 청크 상세 페이지 헤더에 제목 표시
- 제목이 없는 경우 내용의 첫 50자 표시

---

## 📝 향후 개선 사항

1. **수동 제목 편집**: 사용자가 청크 제목을 직접 수정할 수 있는 기능
2. **제목 기반 검색**: 제목으로 청크 검색 기능
3. **제목 기반 필터링**: 제목이 있는/없는 청크 필터링
4. **제목 통계**: 문서별 제목 추출률 통계 표시
5. **제목 품질 개선**: AI 제목 추출 품질 향상 (더 긴 컨텍스트 사용 등)

---

## 🔗 관련 문서

- `docs/dev/phase7-9-4-chunk-detail-page-separation-test.md` - 청크 상세 페이지 분리 테스트
- `docs/dev/phase7-5-upgrade.md` - Phase 7.5 Upgrade 계획
- `brain/system/work_log.md` - 작업 로그

---

**작성일**: 2026-01-09  
**최종 업데이트**: 2026-01-09
