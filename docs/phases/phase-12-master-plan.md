# Phase 12 Master Plan — 프로덕션 안정화 및 인프라 보강

**작성일**: 2026-02-15
**최종 수정**: 2026-02-15
**상태**: 확정
**선행 조건**: Phase 11 완료 (95%)
**기준 문서**: [4-Agent Cross-Review Synthesis](../overview/claude-backend-synthesis-260209-2022.md), [Lead Orchestrator Comprehensive](../overview/cursor-lead-orchestrator-comprehensive-260209-1800.md)
**명명 규칙**: Phase ID **12-Y**, Task **12-Y-N**
**산출물 규칙**: Task 당 report 작성, 저장 위치 `docs/phases/phase-12-Y/`

---

## Phase 12 목표 (1문장)

**4개 에이전트 교차 리뷰에서 발견된 P0~P2 이슈를 우선순위별로 해결하여, 프로덕션 배포 가능 수준의 보안·안정성·성능을 확보한다.**

---

## 목차

1. [관련 문서](#관련-문서)
2. [Phase 11 대비 및 Phase 12 위치](#1-phase-11-대비-및-phase-12-위치)
3. [목표 및 범위 (In / Out Scope)](#2-목표-및-범위-in--out-scope)
4. [단계 번호 체계 및 우선순위에 따른 단계별 계획](#3-단계-번호-체계-및-우선순위에-따른-단계별-계획)
5. [상세 Task 목록·산출물](#4-상세-task-목록산출물)
6. [의존성 및 진행 순서](#5-의존성-및-진행-순서)
7. [성공 기준 (체크리스트)](#6-성공-기준-체크리스트)
8. [예상 총 작업량](#7-예상-총-작업량)
9. [리스크 관리](#8-리스크-관리)

---

## 관련 문서

| 문서 | 용도 |
|------|------|
| [4-Agent Cross-Review Synthesis](../overview/claude-backend-synthesis-260209-2022.md) | P0/P1/P2 이슈 원본, 우선순위 매트릭스 |
| [Lead Orchestrator Comprehensive](../overview/cursor-lead-orchestrator-comprehensive-260209-1800.md) | 통합 로드맵, 우선순위 합의 |
| [Phase 11 Final Summary](phase-11-final-summary-report.md) | 선행 Phase 완료 상태, TD-001~003 |
| [Phase 12 Navigation](phase-12-navigation.md) | 작업 순서·진행 현황 |
| [SSOT v3.0](../SSOT/claude/) | AI Team 운영 규칙 |

---

## 1. Phase 11 대비 및 Phase 12 위치

### 1.1 Phase 11 완료 전제

Phase 11에서 Admin 설정 관리 시스템(DB·API·UI)이 구축·검증된 후, Phase 12는 **프로덕션 안정화**를 목표로 한다.

| Phase 11 산출물 (전제) | Phase 12에서 활용 |
|----------------------|------------------|
| 11-1~11-4 Admin CRUD 시스템 | 기존 API 경로 유지, 회귀 테스트 대상 |
| 11-5 Phase 10 고도화 (40%) | Phase 12와 독립, 별도 진행 가능 |
| TD-001 E2E spec 미존재 | 12-3에서 pytest-cov로 커버리지 확보 |
| TD-003 API 페이지네이션 기본값 | 12-2 에러 표준화에서 함께 처리 |

### 1.2 Phase 12 근거

4개 AI 에이전트(Cursor/Gemini/Copilot/Claude)가 **독립적으로** 발견한 이슈를 교차 검증하여 우선순위를 확정했다.

| 우선순위 | 항목 수 | 합의 에이전트 수 | 성격 |
|---------|--------|:-------------:|------|
| P0 즉시 | 3건 | 3~4개 | 보안·폐쇄망·통일성 |
| P1 계획적 | 5건 | 2~3개 | API 설계·성능·안정성 |
| P2 조기 대응 | 5건 | 2~3개 | XSS·테스트·운영 |

---

## 2. 목표 및 범위 (In / Out Scope)

### 2.1 In Scope (포함)

| 분류 | 항목 |
|------|------|
| **P0 보안/인프라** | CDN 로컬화, Base URL 8001 통일, HTTPS/HSTS 활성화 |
| **P1 API/DB** | API 버전 관리(/api/v1/), Redis 도입, GIN 인덱스, 에러 응답 표준화, PG-Qdrant 보상 트랜잭션 |
| **P2 보안/품질** | innerHTML XSS 방어, Rate Limit IP 개선, pytest-cov 80%, memories TTL, 헬스체크 확장 |

### 2.2 Out of Scope (제외)

| 항목 | 사유 |
|------|------|
| 멀티 테넌시 | Phase 13+ 별도 계획 |
| 타입 힌트 완성·DI 패턴 | P3 백로그, Phase 13+ |
| 구조화 로깅·모니터링 | P3 백로그 |
| 프론트엔드 전면 리팩토링 | P3 백로그 (window 전역 의존 등) |

---

## 3. 단계 번호 체계 및 우선순위에 따른 단계별 계획

### 3.1 단계 번호 체계

| 구분 | 형식 | 의미 | 예시 |
|------|------|------|------|
| **Phase** | **12-Y** | Y = 우선순위 단위 (1~3) | 12-1, 12-2, 12-3 |
| **Task** | **12-Y-N** | N = 해당 Phase 내 순번 | 12-1-1, 12-2-3 |
| **폴더** | `phase-12-Y/` | Phase 단위 문서 | `docs/phases/phase-12-1/` |

### 3.2 우선순위 요약

| 순위 | Phase ID | Phase 명 | 사유 | 예상 |
|------|----------|----------|------|------|
| **1** | 12-1 | P0 즉시 조치 | 보안·폐쇄망·통일성 (전 에이전트 합의) | 2~3일 |
| **2** | 12-2 | P1 계획적 개선 | API 설계·DB 성능·안정성 | 5~7일 |
| **3** | 12-3 | P2 조기 대응 | XSS·테스트·운영 안정화 | 3~4일 |

### 3.3 Phase 12 구조

```
Phase 12 (X=12, Y=우선순위 단위별 phase-12-Y)

1순위  Phase 12-1   P0 즉시 조치
       ├── Task 12-1-1   [FE] CDN 로컬화 (marked/mermaid/chart.js/html2canvas/jspdf)
       ├── Task 12-1-2   [FS] Base URL 8001 통일 (코드+문서)
       └── Task 12-1-3   [INFRA] HTTPS/HSTS 환경변수 기반 활성화

2순위  Phase 12-2   P1 계획적 개선
       ├── Task 12-2-1   [FS] API 버전 관리 (/api/v1/) 도입
       ├── Task 12-2-2   [INFRA] Redis 도입 + Rate Limit 연동
       ├── Task 12-2-3   [DB] PostgreSQL GIN 인덱스 추가
       ├── Task 12-2-4   [BE] API 에러 응답 형식 표준화
       └── Task 12-2-5   [BE] PG-Qdrant 보상 트랜잭션 도입

3순위  Phase 12-3   P2 조기 대응
       ├── Task 12-3-1   [FE] innerHTML XSS 방어 (API 응답 sanitize)
       ├── Task 12-3-2   [BE] Rate Limit X-Forwarded-For 대응
       ├── Task 12-3-3   [TEST] pytest-cov CI 통합 (목표 80%)
       ├── Task 12-3-4   [BE] memories TTL 스케줄러 구현
       └── Task 12-3-5   [BE] 헬스체크 확장 (/health/ready, /health/live)
```

---

## 4. 상세 Task 목록·산출물

### Phase 12-1 P0 즉시 조치 (1순위)

| Task | 도메인 | 목표 | 예상 | 산출물 |
|------|--------|------|------|--------|
| 12-1-1 | [FE] | CDN 참조를 로컬 라이브러리로 전환 (marked.js, mermaid.js, chart.js, html2canvas.js, jspdf.js) | 1일 | `web/public/libs/` 배치, HTML script 태그 수정 |
| 12-1-2 | [FS] | Base URL 8000→8001 통일 (코드 내 하드코딩 + 문서 일괄 수정, 환경변수화) | 0.5일 | docker-compose.yml 환경변수, 코드/문서 수정 |
| 12-1-3 | [INFRA] | HSTS 미들웨어 환경변수 기반 자동 활성화 | 0.5일 | `backend/middleware/security.py` 수정, 환경변수 문서화 |

### Phase 12-2 P1 계획적 개선 (2순위)

| Task | 도메인 | 목표 | 예상 | 산출물 |
|------|--------|------|------|--------|
| 12-2-1 | [FS] | `/api/v1/` prefix 도입, 기존 라우터 마이그레이션, 프론트 호출 경로 수정 | 2일 | 라우터 재구성, 프론트 API 경로 수정 |
| 12-2-2 | [INFRA] | Redis 컨테이너 추가, Rate Limit 백엔드 연동 | 1.5일 | docker-compose.yml, rate_limit.py 수정 |
| 12-2-3 | [DB] | knowledge_chunks GIN 인덱스, conversations session_id 인덱스, memories expires_at 인덱스 | 0.5일 | Alembic 마이그레이션 파일 |
| 12-2-4 | [BE] | API 에러 응답 표준 형식 정의 + 전역 예외 핸들러 통일 | 1.5일 | 에러 핸들러, Pydantic 에러 모델 |
| 12-2-5 | [BE] | PostgreSQL-Qdrant 간 보상 트랜잭션 패턴 구현 | 1.5일 | 보상 로직, 롤백 함수 |

### Phase 12-3 P2 조기 대응 (3순위)

| Task | 도메인 | 목표 | 예상 | 산출물 |
|------|--------|------|------|--------|
| 12-3-1 | [FE] | innerHTML 직접 사용 제거/esc() 적용 확대, API 응답 sanitize 검토 | 1일 | JS 파일 수정, sanitize 유틸 |
| 12-3-2 | [BE] | Rate Limit에서 X-Forwarded-For 헤더 대응 | 0.5일 | rate_limit.py 수정 |
| 12-3-3 | [TEST] | pytest-cov 설정 + CI 통합 + 커버리지 80% 목표 | 1일 | pyproject.toml, pytest 설정, 누락 테스트 추가 |
| 12-3-4 | [BE] | memories 테이블 만료 데이터 자동 정리 스케줄러 | 0.5일 | 스케줄러/크론잡 코드 |
| 12-3-5 | [BE] | /health/ready, /health/live 엔드포인트 추가 | 0.5일 | health.py 라우터 확장 |

---

## 5. 의존성 및 진행 순서

### 5.1 의존성

```
Phase 12-1 (P0) — 3개 Task 병렬 가능
  12-1-1 [FE] CDN 로컬화          ─┐
  12-1-2 [FS] Base URL 통일       ─┤── 모두 병렬, 상호 의존 없음
  12-1-3 [INFRA] HTTPS 활성화     ─┘

Phase 12-2 (P1) — 12-1 완료 후 착수
  12-2-1 [FS] API 버전 관리       ← 최우선 (후속 Task에 경로 영향)
  12-2-2 [INFRA] Redis 도입       ← 12-2-1 이후 (API 경로 확정 필요)
  12-2-3 [DB] GIN 인덱스           ← 독립 (12-2-1과 병렬 가능)
  12-2-4 [BE] 에러 표준화          ← 12-2-1 이후 (API 구조 확정 필요)
  12-2-5 [BE] 보상 트랜잭션        ← 독립 (12-2-1과 병렬 가능)

Phase 12-3 (P2) — 12-2 완료 후 착수
  12-3-1 [FE] XSS 방어             ─┐
  12-3-2 [BE] Rate Limit IP        ─┤── 12-2-2(Redis) 이후
  12-3-3 [TEST] pytest-cov         ─┤── 독립
  12-3-4 [BE] memories TTL         ─┤── 독립
  12-3-5 [BE] 헬스체크 확장        ─┘── 독립
```

### 5.2 의존성 그래프

```
Phase 11 완료
     │
     ▼
12-1 P0 즉시 조치
  ├── 12-1-1 [FE] CDN 로컬화      ─┐
  ├── 12-1-2 [FS] Base URL 통일   ─┤ 병렬
  └── 12-1-3 [INFRA] HTTPS        ─┘
     │ (전부 완료)
     ▼
12-2 P1 계획적 개선
  ├── 12-2-1 [FS] API 버전 관리   ← 최우선
  │     │
  │     ├──► 12-2-2 [INFRA] Redis
  │     └──► 12-2-4 [BE] 에러 표준화
  ├── 12-2-3 [DB] GIN 인덱스      ← 독립
  └── 12-2-5 [BE] 보상 트랜잭션   ← 독립
     │ (전부 완료)
     ▼
12-3 P2 조기 대응
  ├── 12-3-1~12-3-5               ← 대부분 병렬 가능
     │
     ▼
Phase 12 완료
```

---

## 6. 성공 기준 (체크리스트)

### 6.1 Phase 12 완료 조건 체크리스트

#### P0 즉시 조치 (12-1)

- [ ] **12-1-1** CDN 참조 0건 (Grep 검증), 로컬 라이브러리 정상 로드
- [ ] **12-1-2** 코드/문서 내 8000 참조 0건, 환경변수 `BACKEND_PORT` 적용
- [ ] **12-1-3** HSTS 미들웨어 환경변수 기반 활성화, 프로덕션 모드에서 헤더 확인

#### P1 계획적 개선 (12-2)

- [ ] **12-2-1** `/api/v1/` prefix 적용, 기존 엔드포인트 200 OK, 프론트 호출 정상
- [ ] **12-2-2** Redis 컨테이너 기동, Rate Limit Redis 백엔드 동작
- [ ] **12-2-3** GIN 인덱스 3건 생성, EXPLAIN 쿼리로 인덱스 사용 확인
- [ ] **12-2-4** 에러 응답 표준 형식 적용, 전역 예외 핸들러 동작
- [ ] **12-2-5** PG-Qdrant 보상 트랜잭션 로직 구현, 부분 실패 시 롤백 확인

#### P2 조기 대응 (12-3)

- [ ] **12-3-1** innerHTML 직접 사용 0건 (또는 esc() 적용), XSS 테스트 통과
- [ ] **12-3-2** X-Forwarded-For 기반 IP 추출 동작
- [ ] **12-3-3** pytest-cov 설정 완료, 커버리지 80% 이상
- [ ] **12-3-4** memories 만료 데이터 자동 정리 동작
- [ ] **12-3-5** /health/ready, /health/live 엔드포인트 200 OK

### 6.2 KPI (참고)

| 지표 | 목표 |
|------|------|
| CDN 외부 의존 | 0건 (폐쇄망 호환) |
| Base URL 불일치 | 0건 |
| 프로젝트 성숙도 | 72% → 82% (P0+P1 완료 기준) |
| 테스트 커버리지 | 80% 이상 |
| API 응답 시간 (GIN 적용 후) | 키워드 검색 50% 개선 |

---

## 7. 예상 총 작업량

| 단계 | 예상 일수 |
|------|----------|
| Phase 12-1 P0 즉시 조치 | 2~3일 |
| Phase 12-2 P1 계획적 개선 | 5~7일 |
| Phase 12-3 P2 조기 대응 | 3~4일 |
| **합계** | **약 10~14일** |

---

## 8. 리스크 관리

| ID | 리스크 | 영향도 | 대응 |
|----|--------|--------|------|
| R-001 | CDN 로컬화 시 라이브러리 버전 호환 이슈 | 중 | 현재 CDN 버전과 동일 버전 다운로드 |
| R-002 | API 버전 관리 도입 시 프론트엔드 전면 수정 | 높 | 12-2-1을 최우선 배치, 프론트 경로 일괄 치환 |
| R-003 | Redis 도입 시 docker-compose 복잡도 증가 | 중 | 최소 설정으로 시작, health check 포함 |
| R-004 | GIN 인덱스 생성 시 테이블 잠금 | 낮 | CONCURRENTLY 옵션 사용 |
| R-005 | 보상 트랜잭션 패턴의 설계 복잡도 | 높 | 청크 생성 플로우에만 우선 적용 |
| R-006 | innerHTML 제거 시 기존 렌더링 깨짐 | 중 | DOMPurify 또는 esc() 활용, UI 회귀 테스트 |
| R-007 | pytest-cov 80% 달성 어려움 | 중 | 핵심 서비스(reasoning, knowledge) 우선 커버 |
| R-008 | HSTS 활성화 후 HTTP 접근 차단 이슈 | 낮 | 환경변수로 제어, 개발 환경에서는 비활성화 |

---

**문서 상태**: 확정
**다음 단계**: Phase 12-1 착수 → `phase-12-1/` 폴더·status·plan·todo-list 생성
