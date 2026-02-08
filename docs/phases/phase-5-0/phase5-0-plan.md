# Personal AI Brain – Phase 5 실행 전략 문서

**(지식 구조화 + 관계형 Reasoning 단계)**

Phase 1~4를 통해 시스템은

- 문서를 저장하고
- 임베딩/검색하고
- 로그/상태를 관리하고
- Web UI까지 갖춘
  ➡️ **개인 AI 브레인 플랫폼**이 되었다.

Phase 5의 목표는:

> **“지식을 구조화하고 연결해서,
> A + B + (과거 경험들)을 기반으로
> 다음 방향/아이디어를 같이 고민해주는 Reasoning AI”** 로 진화시키는 것.

이를 위해 **PostgreSQL 기반 지식 DB를 도입**하고,
기존 Qdrant + FastAPI + Web UI와 연계하여 단계적으로 확장한다.

---

# 🧭 Phase 5 전체 로드맵

1️⃣ Phase 5.1 – PostgreSQL 기반 지식 DB 도입
2️⃣ Phase 5.2 – 지식 라벨링 / 메타데이터 시스템 추가
3️⃣ Phase 5.3 – 지식 관계(그래프) 관리 계층 구축
4️⃣ Phase 5.4 – Reasoning Pipeline (A+B+경험 → 제안/방향 생성)
5️⃣ Phase 5.5 – 통합 검증 및 회귀 테스트

각 단계에는:

- 기존 시스템과 연계 방식
- 실행 절차 (step-by-step)
- 테스트 / 검증 전략
  이 포함된다.

---

# 1️⃣ Phase 5.1 – PostgreSQL 지식 DB 도입

## 🎯 목표

- 기존 **파일 + Qdrant 중심 구조**에 더해
  **프로젝트 / 문서 / 지식 조각(Chunk)** 의 관계형 메타데이터를 PostgreSQL에 저장
- 이후 라벨/관계/Reasoning의 “기본 데이터 모델” 제공

## 🔗 기존 시스템 연계

- `brain/` 문서 구조
- `embed_and_store.py`
- `/api/search`
- `work_logger.py`

---

## 🪜 실행 절차

### 5.1-1 PostgreSQL 컨테이너 실행

```bash
docker run --name pab-postgres \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_USER=brain \
  -e POSTGRES_DB=knowledge \
  -p 5432:5432 \
  -d postgres
```

### 5.1-2 Python DB 환경 구성

```bash
pip install psycopg2-binary sqlalchemy alembic
```

### 5.1-3 1차 DB 스키마 (핵심)

- projects
- documents
- knowledge_chunks

> 라벨/관계는 이후 단계에서 추가

### 5.1-4 FastAPI DB 연동

- `/backend/models`
- `/backend/config.py`
- DB Session 관리 추가

### 5.1-5 embed_and_store → DB 연동 추가

- 문서 저장 시 DB insert
- chunk 저장 시 DB insert
- Qdrant 저장은 기존 유지

---

## 🧪 검증 전략

- DB 연결 확인 (`psql`)
- 테이블 정상 생성 확인
- embed_and_store 실행 후:

  - PostgreSQL 데이터 생성 확인
  - Qdrant 데이터 확인

- Web 검색 정상 동작 확인
- work_log 기록 확인

---

# 2️⃣ Phase 5.2 – 지식 라벨링 / 메타데이터

## 🎯 목표

- **문서 단위가 아니라 “지식 조각(Chunk)” 단위에 의미 부여**
- AI가 “이 지식이 어떤 역할/주제/맥락인지” 이해 가능하도록 구성

## 🧩 추가 구조

- labels
- knowledge_labels

라벨 타입 예:

- project_phase
- role
- domain
- importance

---

## 🪜 실행 절차

1️⃣ 라벨 테이블 생성
2️⃣ FastAPI 라벨 API 구축
3️⃣ Web UI — 라벨 관리자 & Chunk 라벨 UI 추가
4️⃣ (옵션) AI 추천 라벨 기능 추가

---

## 🧪 검증 전략

- 라벨 CRUD 정상 동작
- Chunk 라벨링 저장 확인
- `/api/search` 라벨 필터 테스트
- AI 라벨 추천 품질 점검
- 기존 기능 정상 유지 확인

---

# 3️⃣ Phase 5.3 – 지식 관계(그래프) 구축

## 🎯 목표

독립된 지식이 아니라,
➡️ “원인 → 결과 → 대안 → 발전” 흐름을 갖는 **지식 네트워크** 구축

## 🧩 테이블 추가

- knowledge_relations

  - source_chunk_id
  - target_chunk_id
  - relation_type
  - confidence
  - description

relation_type 예:

- cause-of
- result-of
- refers-to
- explains
- evolved-from
- risk-related-to

---

## 🪜 실행 절차

1️⃣ 관계 테이블 생성
2️⃣ 관계 API 구축 (`/api/relations`)
3️⃣ Web UI 관계 관리/조회 UI 추가
4️⃣ AI 기반 관계 추천 기능 도입

---

## 🧪 검증 전략

- 관계 생성/조회 테스트
- Web 탐색 UX 검증
- 관계 네비게이션 UX 체감 확인
- 추천 관계 품질 분석
- 기존 기능 회귀 확인

---

# 4️⃣ Phase 5.4 – Reasoning Pipeline 구축

## 🎯 목표

지금까지 구축한

- Project
- Document
- Chunk
- Label
- Relation

을 이용해:

> “A와 B를 연결하면 뭐가 가능?”
> “이번엔 뭘 조심해야 해?”
> “이 흐름의 다음 단계 추천해줘”

➡️ **조합적 추론 & 방향 제안 AI** 구현

---

## 🧠 Reasoning API 설계

```
POST /api/reason
{
  "mode": "combine",
  "inputs": {
    "projects": [1,3],
    "labels": ["ai","architecture"],
    "question": "다음에 뭐하면 좋을까?"
  }
}
```

---

## 🔍 Reasoning Pipeline

1️⃣ 입력 파싱
2️⃣ PostgreSQL 지식 수집
3️⃣ 관계(graph) 추적
4️⃣ Qdrant 의미 검색 추가
5️⃣ 컨텍스트 구성
6️⃣ Reasoning 모델 실행
7️⃣ reasoning_history 저장

---

## 🧪 검증 전략

- 단일 프로젝트 reasoning 확인
- cross-project reasoning 확인
- 결과 품질 주관 점검
- fallback 처리
- 기존 기능 정상 동작 확인

---

# 5️⃣ Phase 5.5 – 통합 회귀 검증

## 🎯 목표

Phase 5 전체가
Phase 1~4 시스템을 깨지 않고 자연스럽게 통합되는지 확인

---

## 🧪 통합 테스트

- 엔드투엔드 시나리오 수행
- DB + Qdrant + Web UI 전체 흐름 점검
- 속도/응답성 확인
- 로그 검증
- 시스템 안정성 확인

---

# ✅ 정리

Phase 5는 다음과 같이 실행된다.

- 5.1: PostgreSQL 지식 DB
- 5.2: 라벨링 / 메타데이터
- 5.3: 지식 관계 그래프
- 5.4: Reasoning AI
- 5.5: 통합 검증

---

## 🎯 Phase 5가 완성되면?

이 시스템은 단순한
“문서 저장 + 검색 도구”를 넘어서

✔️ 지식이 연결되고
✔️ 맥락을 이해하고
✔️ 과거 + 현재를 조합하여
➡️ **새로운 생각을 제안하는 AI 브레인**으로 진화한다.
