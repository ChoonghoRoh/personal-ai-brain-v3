# Phase 8-0-22: 자기 인식 및 메타 인지 변경 보고서

**작성일**: 2026-01-10  
**작업 항목**: 8-0-22 - 자기 인식 및 메타 인지  
**버전**: 8-0-22

---

## 📋 변경 개요

자기 인식 및 메타 인지를 위해 다음 기능을 구현했습니다:

1. **신뢰도 점수 계산**
2. **지식 불확실성 표시**
3. **불확실성 맵**

---

## 🔧 변경 사항 상세

### 1. 메타 인지 서비스 생성 (`backend/services/metacognition_service.py`)

#### MetacognitionService 클래스

**주요 메서드**:
- `calculate_confidence_score()` - 신뢰도 점수 계산
- `indicate_uncertainty()` - 지식 불확실성 표시
- `get_knowledge_uncertainty_map()` - 불확실성 맵

### 2. 메타 인지 API 라우터 (`backend/routers/metacognition.py`)

#### 새로운 엔드포인트

1. **GET `/api/metacognition/confidence/{chunk_id}`**
   - 신뢰도 점수 조회

2. **GET `/api/metacognition/uncertainty/{chunk_id}`**
   - 지식 불확실성 표시

3. **POST `/api/metacognition/uncertainty/map`**
   - 지식 불확실성 맵

### 3. 라우터 등록 (`backend/main.py`)

- metacognition 라우터 추가

---

## 📊 기능 상세

### 신뢰도 점수 계산

**팩터**:
- 라벨 수 (30%): 최대 5개 기준
- 관계 수 (30%): 최대 10개 기준
- 승인 상태 (40%): approved=1.0, draft=0.5, rejected=0.0

**점수 범위**: 0.0 - 1.0

### 불확실성 레벨

- **high**: confidence < 0.3
- **medium**: 0.3 <= confidence < 0.5
- **low**: confidence >= 0.5

---

## ⚠️ 제한사항 및 향후 개선

### 현재 제한사항

1. **신뢰도 계산**: 기본 팩터만 사용
2. **프론트엔드 UI**: 미구현

### 향후 개선 계획

1. 신뢰도 계산 알고리즘 개선
2. 프론트엔드 불확실성 표시 UI
3. 자동 불확실성 해소

---

## 📝 파일 변경 목록

### 신규 파일

1. `backend/services/metacognition_service.py`
   - 메타 인지 서비스 클래스

2. `backend/routers/metacognition.py`
   - 메타 인지 API 라우터

### 수정된 파일

1. `backend/main.py`
   - metacognition 라우터 등록

---

## ✅ 완료 항목

- [x] 신뢰도 점수 계산 구현
- [x] 지식 불확실성 표시 구현
- [x] 불확실성 맵 구현

---

## 📈 다음 단계

1. 프론트엔드 불확실성 표시 UI
2. 실제 데이터로 테스트
3. 신뢰도 계산 알고리즘 개선

---

**변경 상태**: ✅ 기본 기능 완료  
**다음 작업**: 계속 진행
