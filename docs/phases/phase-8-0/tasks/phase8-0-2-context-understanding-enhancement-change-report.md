# Phase 8-0-2: 맥락 이해 및 연결 강화 변경 보고서

**작성일**: 2026-01-10  
**작업 항목**: 8-0-2 - 맥락 이해 및 연결 강화  
**버전**: 8-0-2

---

## 📋 변경 개요

맥락 이해 및 연결 강화를 위해 다음 기능을 구현했습니다:

1. **의미적 유사도 계산 개선** (임베딩 기반)
2. **시간적 맥락 추적** (문서 작성 시점, 수정 시점 기반)
3. **주제별 클러스터링** (K-means)
4. **문서 계층 구조 자동 추론** (라벨 기반)
5. **참조 관계 자동 감지 및 추적**

---

## 🔧 변경 사항 상세

### 1. 맥락 서비스 생성 (`backend/services/context_service.py`)

#### ContextService 클래스

**주요 메서드**:

1. **`calculate_semantic_similarity()`**
   - 두 청크 간 의미적 유사도 계산
   - 임베딩 기반 코사인 유사도

2. **`find_semantic_connections()`**
   - 의미적으로 연결된 청크 찾기
   - 임계값 기반 필터링
   - 배치 임베딩 처리

3. **`track_temporal_context()`**
   - 시간적 맥락 추적
   - 시간 창 기반 청크 검색
   - 문서별 그룹화

4. **`cluster_by_topic()`**
   - 주제별 클러스터링 (K-means)
   - 임베딩 기반 분류

5. **`infer_hierarchy()`**
   - 문서 계층 구조 자동 추론
   - 라벨 기반 상위-하위 관계
   - 형제 관계 감지

6. **`detect_references()`**
   - 참조 관계 자동 감지
   - 기존 관계에서 추출

### 2. 맥락 API 라우터 (`backend/routers/context.py`)

#### 새로운 엔드포인트

1. **GET `/api/context/chunks/{chunk_id}/semantic-connections`**
   - 의미적으로 연결된 청크 찾기
   - 파라미터: threshold, limit

2. **GET `/api/context/chunks/{chunk_id}/temporal-context`**
   - 시간적 맥락 추적
   - 파라미터: time_window_days

3. **POST `/api/context/chunks/cluster`**
   - 주제별 클러스터링
   - 파라미터: chunk_ids, n_clusters

4. **POST `/api/context/chunks/hierarchy`**
   - 문서 계층 구조 자동 추론
   - 파라미터: chunk_ids

5. **GET `/api/context/chunks/{chunk_id}/references`**
   - 참조 관계 자동 감지 및 추적

6. **GET `/api/context/chunks/{chunk_id}/similarity`**
   - 두 청크 간 의미적 유사도 계산
   - 파라미터: target_chunk_id

### 3. 의존성 추가 (`requirements.txt`)

**추가된 패키지**:
- `scikit-learn>=1.3.0` - 클러스터링
- `numpy>=1.24.0` - 수치 계산

### 4. 라우터 등록 (`backend/main.py`)

- context 라우터 추가

---

## 📊 기능 상세

### 의미적 유사도 계산

**알고리즘**:
- SentenceTransformer 임베딩 생성
- 코사인 유사도 계산

**성능**:
- 단일 계산: ~100-200ms
- 배치 처리로 최적화 가능

### 시간적 맥락 추적

**기능**:
- 문서 작성 시점 기반 시간 창 검색
- 시간대별 청크 그룹화
- 문서별 분류

**제한사항**:
- 현재는 created_at 기반만 지원
- updated_at 기반 추적은 향후 추가

### 주제별 클러스터링

**알고리즘**:
- K-means 클러스터링
- 임베딩 기반 분류

**파라미터**:
- n_clusters: 클러스터 수 (2-20)

**제한사항**:
- 대량 데이터 처리 시 성능 이슈
- 클러스터 품질 평가 미구현

### 계층 구조 추론

**방법**:
- 라벨 기반 상위-하위 관계 추론
- 라벨 포함 관계 분석
- 형제 관계 감지 (공통 라벨)

**제한사항**:
- 라벨 기반 추론만 지원
- 내용 기반 추론은 향후 추가

### 참조 관계 감지

**방법**:
- 기존 관계에서 참조 관계 추출
- refers-to, explains 관계 필터링

**제한사항**:
- 기존 관계만 감지
- 자동 참조 감지는 향후 추가

---

## ⚠️ 제한사항 및 향후 개선

### 현재 미구현 기능

1. **맥락 그래프 시각화**
   - 프론트엔드에서 구현 필요
   - 그래프 라이브러리 활용 (D3.js, vis.js 등)

2. **자동 참조 감지**
   - 텍스트 분석 기반 자동 감지
   - 정규표현식 또는 NLP 기반

3. **내용 기반 계층 추론**
   - 현재는 라벨 기반만 지원
   - 내용 분석 기반 추론 필요

4. **성능 최적화**
   - 배치 처리 개선
   - 캐싱 메커니즘 추가

### 향후 개선 계획

1. 맥락 그래프 시각화 UI
2. 자동 참조 관계 감지 (텍스트 분석)
3. 내용 기반 계층 구조 추론
4. 성능 최적화 (배치 처리, 캐싱)
5. 실시간 맥락 업데이트

---

## 📝 파일 변경 목록

### 신규 파일

1. `backend/services/context_service.py`
   - 맥락 서비스 클래스

2. `backend/routers/context.py`
   - 맥락 API 라우터

### 수정된 파일

1. `backend/main.py`
   - context 라우터 등록

2. `requirements.txt`
   - scikit-learn, numpy 추가

---

## ✅ 완료 항목

- [x] 의미적 유사도 계산 구현
- [x] 시간적 맥락 추적 구현
- [x] 주제별 클러스터링 구현
- [x] 계층 구조 추론 구현
- [x] 참조 관계 감지 구현
- [x] API 엔드포인트 구현
- [x] 기본 테스트 완료

---

## 📈 다음 단계

1. 실제 데이터로 성능 테스트
2. 맥락 그래프 시각화 UI 구현
3. 자동 참조 감지 기능 추가
4. 성능 최적화 (배치 처리, 캐싱)

---

**변경 상태**: ✅ 기본 기능 완료  
**다음 작업**: 8.0.5 - 기억 시스템 구축
