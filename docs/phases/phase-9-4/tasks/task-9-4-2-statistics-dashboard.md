# Task 9-4-2: 통계/분석 대시보드

**상태**: 대기 (Pending)
**우선순위**: 9-4 내 2순위
**예상 작업량**: 2일
**의존성**: 없음

---

## 1. 목표

시스템 사용 현황과 지식 베이스 상태를 시각화하는 통계 대시보드 구현

---

## 2. 배경

- 관리자가 시스템 상태를 한눈에 파악 필요
- 문서/청크/라벨 분포 시각화
- 사용량 트렌드 분석

---

## 3. 구현 범위

### 3.1 통계 항목

| 카테고리 | 항목 |
|----------|------|
| **문서** | 총 수, 유형별 분포, 일별 추가량 |
| **청크** | 총 수, 상태별 분포, 프로젝트별 분포 |
| **라벨** | 총 수, 유형별 분포, TOP 10 인기 라벨 |
| **사용량** | 검색 횟수, AI 질의 횟수, Reasoning 횟수 |
| **시스템** | DB 크기, Qdrant 벡터 수, 가동 시간 |

### 3.2 UI 구성

| 영역 | 설명 |
|------|------|
| 요약 카드 | 핵심 지표 4개 (문서, 청크, 라벨, 사용량) |
| 차트 영역 | 분포 차트, 트렌드 차트 |
| 상세 테이블 | 프로젝트별, 라벨별 상세 |

---

## 4. 기술 스택

### 4.1 Backend

- FastAPI Router
- SQLAlchemy 집계 쿼리
- Qdrant API (벡터 수 조회)

### 4.2 Frontend

- Chart.js (차트 라이브러리)
- 기존 UI 컴포넌트 활용

---

## 5. API 설계

### 5.1 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/system/statistics` | 전체 통계 요약 |
| GET | `/api/system/statistics/documents` | 문서 상세 통계 |
| GET | `/api/system/statistics/knowledge` | 지식(청크/라벨) 통계 |
| GET | `/api/system/statistics/usage` | 사용량 통계 |
| GET | `/api/system/statistics/trends` | 트렌드 데이터 (일별) |

### 5.2 응답 스키마

**`GET /api/system/statistics`**

```json
{
  "summary": {
    "total_documents": 150,
    "total_chunks": 2340,
    "total_labels": 89,
    "total_projects": 5
  },
  "documents": {
    "by_type": {
      "pdf": 45,
      "docx": 30,
      "md": 50,
      "txt": 25
    }
  },
  "chunks": {
    "by_status": {
      "approved": 2100,
      "pending": 200,
      "rejected": 40
    }
  },
  "usage": {
    "searches_today": 45,
    "asks_today": 12,
    "reasoning_today": 5
  },
  "system": {
    "db_size_mb": 256,
    "qdrant_vectors": 2340,
    "uptime_hours": 120
  }
}
```

**`GET /api/system/statistics/trends?days=7`**

```json
{
  "period": "7d",
  "data": [
    {"date": "2026-01-28", "documents": 5, "chunks": 45, "searches": 20},
    {"date": "2026-01-29", "documents": 3, "chunks": 28, "searches": 15},
    ...
  ]
}
```

---

## 6. 파일 구조

### 6.1 Backend

```
backend/routers/system/
├── __init__.py
├── statistics.py          # 신규: 통계 API
└── ...

backend/services/system/
├── statistics_service.py  # 신규: 통계 수집 서비스
└── ...
```

### 6.2 Frontend

```
web/
├── src/pages/admin/
│   └── statistics.html    # 신규: 통계 대시보드
├── public/css/
│   └── statistics.css     # 신규: 스타일
└── public/js/admin/
    └── statistics.js      # 신규: 차트 로직
```

---

## 7. 체크리스트

### 7.1 Backend 구현
- [ ] `statistics_service.py` 생성
- [ ] 문서 통계 쿼리 구현
- [ ] 청크 통계 쿼리 구현
- [ ] 라벨 통계 쿼리 구현
- [ ] 사용량 통계 구현
- [ ] 트렌드 데이터 구현
- [ ] `statistics.py` 라우터 생성
- [ ] `main.py`에 라우터 등록

### 7.2 Frontend 구현
- [ ] `statistics.html` 생성
- [ ] 요약 카드 UI
- [ ] 차트 컴포넌트 (Chart.js)
- [ ] 파이 차트 (유형별 분포)
- [ ] 바 차트 (상태별 분포)
- [ ] 라인 차트 (트렌드)
- [ ] 테이블 (상세 데이터)

### 7.3 테스트
- [ ] API 응답 테스트
- [ ] 빈 데이터 처리
- [ ] 대량 데이터 성능

---

## 8. 사용량 추적 구현

### 8.1 추적 대상

| 이벤트 | 소스 |
|--------|------|
| 검색 | `/api/search` 호출 |
| AI 질의 | `/api/ask` 호출 |
| Reasoning | `/api/reason` 호출 |

### 8.2 추적 방법

**옵션 1: 미들웨어 기반**
```python
@app.middleware("http")
async def track_usage(request, call_next):
    if request.url.path.startswith("/api/search"):
        await increment_counter("searches")
    ...
```

**옵션 2: 엔드포인트 내 직접 기록**
```python
@router.post("/search")
async def search(...):
    await usage_service.track("search")
    ...
```

### 8.3 저장소

- PostgreSQL `usage_logs` 테이블 (추후 확장 가능)
- 또는 인메모리 카운터 (간단 버전)

---

## 9. 차트 설계

### 9.1 요약 카드 (4개)

```
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  Documents  │ │   Chunks    │ │   Labels    │ │   Today's   │
│     150     │ │    2,340    │ │     89      │ │   Usage     │
│   +5 today  │ │ +45 today   │ │  +2 today   │ │  62 calls   │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
```

### 9.2 문서 유형 분포 (파이 차트)

```
    PDF: 30%
   DOCX: 20%
     MD: 33%
    TXT: 17%
```

### 9.3 청크 상태 분포 (바 차트)

```
Approved  ████████████████████████ 2100
Pending   ████ 200
Rejected  █ 40
```

### 9.4 일별 트렌드 (라인 차트)

```
     ^
     │    ╱╲
docs │   ╱  ╲   ╱
     │  ╱    ╲ ╱
     │ ╱      ╲
     └──────────────>
       Mon Tue Wed ...
```

---

## 10. 네비게이션 통합

### 10.1 메뉴 추가

- Admin 섹션에 "Statistics" 메뉴 추가
- `/admin/statistics` 경로

### 10.2 접근 권한

- 인증 필요 (AUTH_ENABLED=true 시)
- 또는 공개 (개발 환경)

---

## 11. 의존성

### 11.1 Frontend

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

### 11.2 Backend

- 기존 SQLAlchemy 활용
- 추가 패키지 없음

---

## 12. 테스트 케이스

| 케이스 | 조건 | 기대 결과 |
|--------|------|-----------|
| 정상 조회 | 데이터 있음 | 모든 통계 표시 |
| 빈 데이터 | 데이터 없음 | 0 표시, 에러 없음 |
| 대량 데이터 | 10,000+ 청크 | 3초 이내 응답 |
| 트렌드 | 7일 데이터 | 일별 차트 표시 |

---

## 13. 참고 자료

- Chart.js: https://www.chartjs.org/docs/latest/
- FastAPI Aggregation: https://fastapi.tiangolo.com/
- SQLAlchemy func: https://docs.sqlalchemy.org/

---

## 14. 작업 로그

| 날짜 | 작업 내용 | 상태 |
|------|----------|------|
| - | - | - |
