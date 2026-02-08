# Personal AI Brain — System Architecture Overview (Independent Review)

작성일: 2026-02-08  
기준: Phase 11 완료 구조

---

# 1. 시스템 정체성 (System Identity)

Personal AI Brain은 단순한 RAG 앱이 아니라 다음 4개 계층이 결합된 로컬 AI 지식 운영 시스템이다.

- Knowledge Layer (지식 저장)
- Reasoning Layer (판단·추론)
- Cognitive Layer (기억·맥락·학습)
- Admin Layer (설정·정책 운영)

구조적으로 보면:

Document System + Knowledge Graph + RAG + Reasoning Engine + Admin Config System

형태의 AI 운영 플랫폼이다.

---

# 2. 전체 아키텍처 구조

## 시스템 레이어 구조

Frontend (HTML/JS)
        ↓
FastAPI Backend
        ↓
Service Layer
        ↓
DB / Vector DB / Ollama

### 인프라 구성
- PostgreSQL → 구조 데이터
- Qdrant → 벡터 검색
- Ollama → LLM 실행
- Docker Compose → 전체 서비스 관리

---

# 3. Backend 구조 평가

현재 Backend는 기능 기준으로 잘 분리되어 있다.

Router 구성:

auth
search
knowledge
reasoning
cognitive
automation
admin
system
ingest

특히 아래 분리는 AI Brain 구조의 핵심이다:

- knowledge
- reasoning
- cognitive
- admin

---

# 4. Core Engine 구조

## Knowledge Engine
- chunk 관리
- label
- relation
- approval
- ingest

지식 그래프 관리 시스템 역할.

## Reasoning Engine
- reasoning chain
- streaming reasoning
- reasoning store
- recommendations

Decision Engine + Explanation Engine 역할.

## Cognitive Engine
- memory
- context
- learning
- personality
- metacognition

일반 RAG 시스템과 구분되는 핵심 영역.

---

# 5. Admin System (Phase 11)

Admin 설정 관리 시스템은 AI 운영 콘솔 역할.

구성:
- schemas
- templates
- presets
- rag-profiles
- policy-sets
- audit-logs

특징:
- DB 기반 설정 관리
- UI 관리 가능
- Audit 로그 존재

---

# 6. Frontend 구조 평가

Frontend는 SPA 없이 페이지 단위 HTML + JS 구조.

장점:
- 유지보수 단순
- 디버깅 쉬움
- Admin UI 구현에 적합
- Docker 환경 안정적

---

# 7. 프로젝트 성숙도 평가

완성 영역:
- RAG 시스템
- Knowledge 관리
- Reasoning Lab
- Admin 설정 관리
- API 구조
- 문서 체계

진행 영역:
- Phase 11-5 고도화
- 성능 개선
- 시각화 개선

---

# 8. 시스템 정의

Local AI Knowledge Operating System

또는

AI Decision Support Platform

구성:
Document System
+ Knowledge Graph
+ RAG
+ Reasoning Engine
+ Cognitive Memory
+ Admin Config System

---

# 9. 구조적 강점

1. Router → Service → Model 구조 명확
2. Knowledge / Reasoning / Cognitive 분리
3. Admin 설정 시스템 존재

---

# 10. 구조적 리스크

리스크 1 — reasoning 서비스 집중도 증가 가능
→ 서비스 분리 고려

리스크 2 — frontend 모듈화 부족
→ 페이지 증가 시 관리 비용 증가 가능

리스크 3 — workflow engine 위치
→ automation/workflow 재정의 필요

---

# 11. 한 줄 평가

AI Brain PoC를 넘어 운영 가능한 구조까지 도달한 상태
