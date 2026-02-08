# Phase 8-0-1: 데이터베이스 쿼리 최적화 변경 보고서

**작성일**: 2026-01-10  
**작업 항목**: 8-0-1 - 데이터베이스 쿼리 최적화  
**버전**: 8-0-1

---

## 📋 변경 개요

데이터베이스 쿼리 성능 개선을 위해 다음 개선 사항을 구현했습니다:

1. **인덱스 추가 및 최적화** (자주 사용되는 쿼리 분석)
2. **N+1 쿼리 문제 해결** (Eager loading, 배치 조회)
3. **쿼리 실행 계획 분석** (EXPLAIN ANALYZE)
4. **느린 쿼리 모니터링 시스템** 구축
5. **연결 풀 최적화**

---

## 🔧 변경 사항 상세

### 1. 인덱스 추가 (`backend/models/models.py`)

#### 추가된 인덱스

**KnowledgeChunk 모델**:
- `document_id`: 인덱스 추가 (문서별 청크 조회 최적화)
- `chunk_index`: 인덱스 추가 (청크 인덱스 조회 최적화)
- `qdrant_point_id`: 인덱스 추가 (Qdrant 동기화 최적화)

**KnowledgeLabel 모델**:
- `chunk_id`: 인덱스 추가 (청크별 라벨 조회 최적화)
- `label_id`: 인덱스 추가 (라벨별 청크 조회 최적화)

**KnowledgeRelation 모델**:
- `source_chunk_id`: 인덱스 추가 (출발 청크별 관계 조회 최적화)
- `target_chunk_id`: 인덱스 추가 (도착 청크별 관계 조회 최적화)
- `relation_type`: 인덱스 추가 (관계 타입별 조회 최적화)

**Document 모델**:
- `project_id`: 인덱스 추가 (프로젝트별 문서 조회 최적화)

**효과**:
- 필터링 쿼리 성능 향상
- 조인 쿼리 성능 향상
- 대용량 데이터 처리 개선

### 2. N+1 쿼리 문제 해결

#### `backend/routers/knowledge.py`

**기존 문제**:
```python
# 각 청크마다 별도 쿼리 실행 (N+1 문제)
for chunk in chunks:
    doc = db.query(Document).filter(Document.id == chunk.document_id).first()
    project = db.query(Project).filter(Project.id == doc.project_id).first()
    labels = db.query(Label).join(KnowledgeLabel).filter(...).all()
```

**개선**:
```python
# Eager loading으로 한 번에 로드
chunks = base_query.options(
    joinedload(KnowledgeChunk.document).joinedload(Document.project),
    selectinload(KnowledgeChunk.labels).joinedload(KnowledgeLabel.label)
).all()
```

**성능 개선**:
- 쿼리 수: 100개 청크 기준 300+ → 3-5개
- 응답 시간: 70-80% 단축 예상

#### `backend/routers/reason.py`

**trace_relations 함수**:
- 기존: 각 청크마다 관계 조회 (N+1)
- 개선: 배치 조회 (IN 절 사용)
- 쿼리 수: 10개 청크 기준 20+ → 2-3개

**build_context_chunks 함수**:
- 기존: 각 청크마다 문서, 프로젝트 조회 (N+1)
- 개선: 배치 조회 (IN 절 사용)
- 쿼리 수: 20개 청크 기준 40+ → 2-3개

**collect_relations 함수**:
- 기존: 각 관계마다 타겟 청크 조회 (N+1)
- 개선: 배치 조회 (IN 절 사용)
- 쿼리 수: 10개 관계 기준 20+ → 2-3개

### 3. 연결 풀 최적화 (`backend/models/database.py`)

#### 설정 변경

**기존**:
```python
engine = create_engine(DATABASE_URL, echo=False)
```

**개선**:
```python
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_size=10,  # 연결 풀 크기
    max_overflow=20,  # 최대 오버플로우 연결 수
    pool_pre_ping=True,  # 연결 유효성 사전 확인
    pool_recycle=3600,  # 1시간마다 연결 재활용
    connect_args={
        "connect_timeout": 10,
        "application_name": "personal_ai_brain"
    }
)
```

**효과**:
- 동시 연결 처리 능력 향상
- 연결 유효성 보장
- 연결 재활용으로 안정성 향상

### 4. 느린 쿼리 모니터링 시스템 (`scripts/analyze_slow_queries.py`)

#### 기능

1. **쿼리 실행 시간 모니터링**
   - SQLAlchemy 이벤트 리스너 사용
   - 모든 쿼리 실행 시간 기록

2. **느린 쿼리 감지**
   - 임계값: 100ms (설정 가능)
   - 느린 쿼리 목록 수집

3. **쿼리 실행 계획 분석**
   - EXPLAIN ANALYZE 지원
   - 자주 사용되는 쿼리 패턴 분석

4. **인덱스 확인**
   - 현재 인덱스 목록 조회
   - 인덱스 정의 확인

---

## 📊 성능 개선 예상치

### 쿼리 수 감소

| 작업 | 개선 전 | 개선 후 | 개선율 |
|------|--------|--------|--------|
| 청크 목록 조회 (100개) | 300+ 쿼리 | 3-5 쿼리 | **98-99%** |
| 관계 추적 (10개 청크) | 20+ 쿼리 | 2-3 쿼리 | **85-90%** |
| 컨텍스트 구성 (20개) | 40+ 쿼리 | 2-3 쿼리 | **92-95%** |

### 응답 시간 개선

| 작업 | 개선 전 | 개선 후 | 개선율 |
|------|--------|--------|--------|
| 청크 목록 조회 (100개) | 500-1000ms | 100-200ms | **70-80%** |
| 관계 추적 (10개 청크) | 200-500ms | 50-100ms | **75-80%** |
| 컨텍스트 구성 (20개) | 100-200ms | 20-50ms | **75-80%** |

---

## 🔄 마이그레이션 가이드

### 인덱스 추가

**주의사항**:
- 기존 데이터베이스에 인덱스 추가 필요
- 대용량 테이블의 경우 인덱스 생성 시간 소요

**권장 방법**:
1. Alembic 마이그레이션 스크립트 생성
2. 개발 환경에서 테스트
3. 운영 환경에 적용

**예제 마이그레이션**:
```python
# Alembic migration 예제
def upgrade():
    op.create_index('ix_knowledge_chunks_document_id', 'knowledge_chunks', ['document_id'])
    op.create_index('ix_knowledge_labels_chunk_id', 'knowledge_labels', ['chunk_id'])
    # ... 기타 인덱스
```

---

## 📝 파일 변경 목록

### 수정된 파일

1. `backend/models/models.py`
   - 인덱스 추가 (9개 컬럼)

2. `backend/models/database.py`
   - 연결 풀 최적화 설정

3. `backend/routers/knowledge.py`
   - Eager loading 적용
   - N+1 쿼리 문제 해결

4. `backend/routers/reason.py`
   - 배치 조회로 변경
   - N+1 쿼리 문제 해결 (3개 함수)

### 신규 파일

1. `scripts/analyze_slow_queries.py`
   - 느린 쿼리 분석 스크립트

---

## ⚠️ 주의사항

1. **인덱스 마이그레이션**: 기존 데이터베이스에 인덱스 추가 필요
   - Alembic 마이그레이션 스크립트 생성 권장
   - 대용량 테이블의 경우 인덱스 생성 시간 소요

2. **메모리 사용**: Eager loading 사용 시 메모리 사용량 증가 가능
   - 필요한 경우만 사용
   - 페이징으로 결과 수 제한

3. **연결 풀**: 연결 풀 크기는 실제 사용량에 맞게 조정 필요

---

## ✅ 완료 항목

- [x] 인덱스 추가 (9개 컬럼)
- [x] N+1 쿼리 문제 해결 (4개 함수)
- [x] 연결 풀 최적화
- [x] 느린 쿼리 모니터링 시스템 구축
- [x] 쿼리 실행 계획 분석 스크립트 작성
- [x] 테스트 완료

---

## 📈 다음 단계

1. Alembic 마이그레이션 스크립트 생성
2. 실제 운영 환경에서 성능 테스트
3. 인덱스 생성 및 성능 측정
4. 추가 최적화 기회 탐색

---

**변경 상태**: ✅ 완료  
**다음 작업**: 8.0.4 - 맥락 이해 및 연결 강화
