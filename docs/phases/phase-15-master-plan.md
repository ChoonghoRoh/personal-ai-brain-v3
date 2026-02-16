# Phase 15 Master Plan — 지식관리 지정 폴더·파일관리·AI 자동화·Reasoning

**작성일**: 2026-02-09
**역할**: PM(Project Manager) 마스터 플랜
**선행 조건**: Phase 14 완료 (권한·LNB·API 문서·DB 샘플·2차 검증 등).
**현재 진행**: Phase 14-1·14-2·14-3·14-5·14-6 DONE (각 phase-14-_/phase-14-_-status.md 참조). Phase 15 착수 가능.
**기준 문서**:

- [260216-1459-지식관리-ai-자동화-추천-기능-설계.md](../planning/260216-1459-지식관리-ai-자동화-추천-기능-설계.md)
- [260210-1400-db-sample-data-and-high-level-strategy.md](../planning/260210-1400-db-sample-data-and-high-level-strategy.md)
- [260216-1725-PAB 지능형 지식 관리 시스템: Phase 15 고도화 전략 및 기술 아키텍처 보고서](../planning/260216-1725-PAB%20지능형%20지식%20관리%20시스템%3A%20Phase%2015%20고도화%20전략%20및%20기술%20아키텍처%20보고서.md)

---

## 1. 목표 및 범위

### 1.1 Phase 15 목표 (1문장)

**지식관리용 지정 폴더를 두고 해당 폴더의 파일을 관리(목록·업로드·동기화)하며, 지식관리 AI 자동화(청크·키워드·라벨·승인·임베딩)와 지정 폴더 파일 대상 Reasoning을 UI·Backend·API로 제공하여, 데이터 등록 자동화와 “지정 지식에 대한 추론” 경험을 완성한다.**

### 1.2 범위 요약

| 블록                               | 내용                                                                                                                                     |
| ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| **지정 폴더·파일관리**             | 지식관리 전용 폴더 생성·설정, 폴더 내 파일 목록·업로드·동기화·상태 관리 (UI + API).                                                      |
| **지식관리 AI 자동화**             | 기준 문서 260216 반영: AI 자동화 통합 워크플로우(문서→청크→키워드→라벨→승인→임베딩), 진행 상황(SSE), 신규 메뉴/페이지.                   |
| **지정 폴더 파일 Reasoning**       | 지정 폴더(또는 선택 파일)에 대해 Reasoning 실행하는 방식의 UI·Backend·API 인터페이스 추가.                                               |
| **DB 샘플·고도화 연동**            | 기준 문서 260210 반영: 지식관리 지정 폴더와 documents/chunks/labels 연동, 시드·검증 전략 일치.                                           |
| **회원 관리 시스템 완성 (15-5)**   | users 테이블 생성·마이그레이션, 회원 가입·프로필 수정·비밀번호 변경 CRUD, Admin 전용 사용자 목록·권한(Role) 할당 UI.                     |
| **보안·세션 관리 강화 (15-6)**     | 토큰 만료 처리·Refresh Token 도입, 로그아웃 시 토큰 블랙리스트(Redis), 비인증 접근 시 로그인 페이지 강제 리다이렉트(Phase 14 권장 반영). |
| **서비스 안정화·최종 검증 (15-7)** | 전체 시스템 부하 테스트·메모리 누수 점검, Docker Production 환경 설정 검증.                                                              |

---

## 2. 기준 문서 반영 요약

### 2.1 지식관리 AI 자동화 설계 (260216-1459)

| 항목            | 설계 내용                                                                                         | Phase 15 반영                                                       |
| --------------- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| **메뉴**        | ADMIN_MENU에 "🤖 AI 자동화" (/admin/ai-automation) 추가                                           | 15-2: 신규 메뉴·라우트·HTML                                         |
| **워크플로우**  | 문서 선택 → 청크 생성 → 키워드 추출 → 라벨 생성/매칭 → 청크-라벨 연결 → 승인 판단 → Qdrant 임베딩 | 15-2: `/api/automation/run-full`, BackgroundTasks, 6단계 순차       |
| **진행 상황**   | 3초 이상 작업 시 Progress Bar, SSE 실시간 업데이트                                                | 15-2: `/api/automation/progress/{task_id}` (SSE), FE Progress Panel |
| **API**         | run-full, progress/{task_id}, cancel/{task_id}, tasks, approve-pending                            | 15-2: Backend 라우터·스키마                                         |
| **UI**          | 3-Column: 문서 선택(좌) / AI 워크플로우·Progress(중) / 실시간 결과(우)                            | 15-2: FE 페이지·컴포넌트                                            |
| **AI 프롬프트** | 키워드 추출·승인 판단·라벨 추천 (Ollama llama3.2, nomic-embed-text)                               | 15-2: 프롬프트 전략·컨텍스트 제한                                   |

### 2.2 DB 샘플·고도화 전략 (260210-1400)

| 항목                 | 전략 내용                                                      | Phase 15 반영                                                   |
| -------------------- | -------------------------------------------------------------- | --------------------------------------------------------------- |
| **documents·chunks** | file_path 기반, projects·labels·knowledge_labels 연동          | 15-1: 지정 폴더 경로를 project 또는 file_path 규칙으로 매핑     |
| **카테고리**         | development/planning/review/rules/ai/general, labels(category) | 15-1·15-4: 지식관리 폴더 파일에 category 라벨 부여·시드 시 반영 |
| **시드·검증**        | projects→labels→documents→chunks→…, 1차/2차 검증               | 15-4: 지식관리 폴더를 포함한 시드·검증 옵션                     |

### 2.3 Phase 15 고도화 전략 및 기술 아키텍처 (260216-1725 보고서)

PAB 지능형 지식 관리 시스템 보고서에서 제시한 **현 상태 vs 목표 상태** 및 **전략·기술 아키텍처**를 Phase 15 실행 시 참고한다.

#### 2.3.1 현 상태 vs 목표 상태 (Baseline vs Target)

| 항목 | 현재 상태 (Baseline) | 목표 상태 (Target) | 기업 가치 |
|------|----------------------|--------------------|-----------|
| Redis 활용 | Rate Limiting 중심 (5% 미만) | 캐싱·세션·작업 큐 전면 통합 | 응답 속도 70%↑, 서버 부하 50%↓ |
| Qdrant 성능 | 기본 메모리 캐시 의존 | 다단계 캐싱 및 인덱스 최적화 | 검색 정확도 95% 이상 |
| Reasoning UX | 단순 로딩 스피너 대기 | 실시간 진행률 및 결과 시각화 | 사용자 이탈률 60% 감소 |
| 지식 관리 | 6개 메뉴 분산 구조 | AI 자동화 통합 워크플로우 | 데이터 등록 시간 78% 단축 |
| UI/UX | Vanilla JS 기본 UI | 폴더 트리 및 D3.js 그래프 시각화 | 엔터프라이즈 표준 대시보드 |

#### 2.3.2 핵심 차별화·전략

- **로컬 우선(Local-First)·에어갭 대응**: 외부 클라우드 의존 제거, 데이터 주권·폐쇄망 지원.
- **하이브리드 추론 확장**: Ollama 로컬 LLM + 규칙 기반 결합, 기업 특화 페르소나.
- **한국어 지식 처리**: paraphrase-multilingual 임베딩, 한국어 전용 프롬프트 엔지니어링.

#### 2.3.3 지능형 자동화 워크플로우·UX (보고서 정합)

- **6단계 프로세스**: 청크 분할 → 키워드 추출 → 라벨링 → 지식 연결 → 승인 → 임베딩 (15-2와 동일).
- **엔터프라이즈 인입**: FilePond 대용량 PDF/DOCX 드래그앤드롭·청크 업로드.
- **구조적 탐색**: Tree.js 기반 파일 트리 UI, 계층 구조.
- **실시간 피드백**: Redis Pub/Sub + SSE로 진행 상태 프로그레스 바 (15-2 SSE 반영).
- **효과**: 데이터 등록 시간 270초 → 60초 수준(약 78% 단축) 목표.

#### 2.3.4 Reasoning 고도화 (4대 추론 모드·검색)

- **4대 전문 모드**: design_explain(설계 설명·Mermaid 시각화), risk_review(리스크 검토), next_steps(후속 절차), history_trace(이력 추적).
- **하이브리드**: 규칙 기반(예산·연차 등) + AI 의미 해석.
- **재순위(Re-ranking)**: Cross-Encoder로 검색 정확도 85% → 95% 목표.
- **하이브리드 검색**: Sparse + Dense 결합, 고유명사·약어 대응 강화.
- **미래 페르소나**: legal_compliance, tech_support 등 확장 예정.

#### 2.3.5 D3.js 지식 그래프 시각화·UI 전략

- **D3.js (Force-Directed Graph)**: 지식 노드 간 관계(Relational Knowledge Map) 시각화, 노드 선택 시 연관 문서·청크 탐색.
- **Mermaid.js**: 선형 프로세스·순서도 등 절차적 로직 보조.
- **Tree.js / FilePond**: 계층적 파일 구조·업로드 UX (15-1·15-2와 연동).
- **성능 목표**: P95 1초 이내(100+ 노드), P99 2초 이내 렌더링, Lighthouse 검증.

#### 2.3.6 Redis·Qdrant 성능 최적화

- **Redis**: 중복 질의 캐시(응답 0.3초 이내 목표), AOF 영속성, maxmemory-policy allkeys-lru, Pub/Sub 워크플로우 상태 동기화 (15-2·15-6와 연동).
- **Qdrant**: 벡터 양자화(32bit→8bit, 메모리 75% 절감), 문서량 2.5만→10만 확장 목표; Redis 히트 10ms 이하, Qdrant 검색 100ms 이하 목표.

#### 2.3.7 엔터프라이즈 가치·보안·마일스톤

- **TCO/ROI**: 100명 5년 기준 SaaS 대비 연간 약 1억 원 수준 비용 절감 가능성 제시.
- **보안 체크리스트**: JWT·감사 로그·Swagger 기완료; Phase 15 적용 시 감사 추적 테이블, AES-256 민감 데이터 암호화, SSO(LDAP/AD) 준비.
- **단계별 마일스톤 제안**:
  - **1주차 (M1–M2)**: 파일 관리 MVP, 6단계 AI 자동화 Core.
  - **2주차 (M3–M4)**: 하이브리드 Reasoning 통합, Redis/Qdrant 튜닝.
  - **3주차 (M5–M6)**: D3.js 지식 그래프 시각화 완성, 전사 배포 준비.

---

## 3. Phase 15 구조

```
Phase 15

15-1   지식관리 지정 폴더·파일관리
       ├── 15-1-1   [BE] 지정 폴더 경로 설정·저장 (설정 또는 기본 brain/knowledge 등)
       ├── 15-1-2   [BE] 폴더 내 파일 목록 API (file_path, size, updated_at, document_id 유무)
       ├── 15-1-3   [BE] 파일 업로드·동기화 API (지정 폴더로 업로드, documents 반영)
       ├── 15-1-4   [FE] 지식관리 파일관리 UI (폴더 선택·파일 목록·업로드·상태)
       └── 15-1-5   [DOC] 지정 폴더 규칙·권한 정리

15-2   지식관리 AI 자동화 (260216 설계 반영)
       ├── 15-2-1   [BE] /api/automation/run-full, progress/{task_id}, cancel, tasks, approve-pending
       ├── 15-2-2   [BE] 6단계 워크플로우 구현 (청크→키워드→라벨→연결→승인→임베딩)
       ├── 15-2-3   [BE] SSE 진행 상황·Redis/메모리 상태 저장
       ├── 15-2-4   [FE] /admin/ai-automation 페이지 (3-Column, Progress Bar, SSE 연동)
       └── 15-2-5   [FE] LNB/메뉴에 "AI 자동화" 추가

15-3   지정 폴더 파일 Reasoning (UI/Backend/API)
       ├── 15-3-1   [BE] 지정 폴더/문서 대상 Reasoning API (document_ids 또는 folder_path)
       ├── 15-3-2   [BE] Reasoning 모드·템플릿 연동 (기존 reason_store, reasoning_results)
       ├── 15-3-3   [FE] 지식관리 화면에서 "이 폴더로 Reasoning" 진입점
       ├── 15-3-4   [FE] Reasoning 실행·진행·결과 표시 (기존 /reason UI 재사용 또는 연동)
       └── 15-3-5   [API] 인터페이스 명세 (요청/응답·스트리밍)

15-4   DB 샘플·고도화 연동 (260210 연동)
       ├── 15-4-1   [DOC] 지식관리 지정 폴더와 documents/projects/labels 매핑 규칙
       ├── 15-4-2   [SCRIPT] 시드 시 지정 폴더 경로 포함 옵션
       └── 15-4-3   [QA] 검증 시 지식관리 폴더·자동화 결과 포함 여부

15-5   회원 관리 시스템 완성
       ├── 15-5-1   [BE] users 테이블 실제 생성 및 마이그레이션 (Alembic 등)
       ├── 15-5-2   [BE] 회원 가입·프로필 수정·비밀번호 변경 CRUD API
       ├── 15-5-3   [FE] Admin 전용 사용자 목록·권한(Role) 할당 UI 개발
       └── 15-5-4   [DOC] 회원 관리 API·권한 매핑 정리

15-6   보안 및 세션 관리 강화
       ├── 15-6-1   [BE] 토큰 만료 처리 및 Refresh Token 도입 (발급·갱신 API)
       ├── 15-6-2   [BE] 로그아웃 시 토큰 블랙리스트 처리 (Redis 활용)
       ├── 15-6-3   [FE/BE] 비인증 접근 시 로그인 페이지 강제 리다이렉트 (Phase 14 권장사항 반영)
       └── 15-6-4   [DOC] 보안·세션 정책 문서화

15-7   서비스 안정화 및 최종 검증
       ├── 15-7-1   [QA] 전체 시스템 부하 테스트 및 메모리 누수 점검
       ├── 15-7-2   [QA/INFRA] Docker Production 환경에서 설정 검증
       └── 15-7-3   [DOC] 운영 체크리스트·검증 리포트

15-8   (선택) 지식 그래프 시각화·인프라 고도화 (260216-1725 보고서 반영)
       ├── 15-8-1   [FE] D3.js Force-Directed Graph 지식 노드 관계 시각화 (P95 1초·P99 2초 목표)
       ├── 15-8-2   [BE] Redis 캐싱 확대 (중복 질의 캐시·AOF·Pub/Sub 상태), Qdrant 벡터 양자화·인덱스 최적화
       └── 15-8-3   [DOC] 4대 추론 모드(design_explain·risk_review·next_steps·history_trace)·Re-ranking·하이브리드 검색 정리
```

---

## 4. 지식관리 지정 폴더·파일관리 (15-1)

### 4.1 지정 폴더 정의

- **목적**: 지식관리(청크·라벨·검색·Reasoning)의 “원본 파일”을 한 곳에서 관리.
- **기본 경로 제안**: `brain/knowledge/`(프로젝트 루트 기준 상대경로). 설정 가능 경로는 Admin 설정 테이블 또는 환경변수(예: `KNOWLEDGE_FOLDER_PATH`)로 저장(§9.5 반영).
- **허용 파일**: .md, .txt, .pdf, .docx 등 기존 ingest 지원 확장자. 업로드/동기화 시 기존 문서 파싱·청크 생성 파이프라인(ingest, knowledge)과 동일 규칙 사용. `file_path`는 지정 폴더 기준 상대 경로 또는 정책에 따라 절대 경로 명확화(§9.5 #6).

### 4.2 파일관리 기능

| 기능                    | 설명                                                        | API (제안)                                |
| ----------------------- | ----------------------------------------------------------- | ----------------------------------------- |
| **폴더 경로 조회/설정** | 현재 지정 폴더 경로 조회, Admin에서 변경                    | GET/PUT `/api/knowledge/folder-config`    |
| **파일 목록**           | 지정 폴더 내 파일 목록 (파일시스템 + documents 테이블 매칭) | GET `/api/knowledge/folder-files`?folder= |
| **파일 업로드**         | 지정 폴더로 파일 업로드, documents 반영                     | POST `/api/knowledge/upload` (multipart)  |
| **동기화**              | 폴더 스캔 후 신규/삭제 반영, documents 갱신                 | POST `/api/knowledge/sync`                |
| **상태**                | 파일별 document_id, chunk 수, 최종 처리 일시                | 목록 응답에 포함                          |

### 4.3 UI 요구사항 (15-1-4)

- 지식관리 메뉴 하위 또는 전용 "파일관리" 영역.
- 지정 폴더 경로 표시·변경(권한 시).
- 테이블: 파일명, 크기, 수정일, document_id 유무, 청크 수, [Reasoning 실행] [AI 자동화] 액션.
- 업로드 버튼·드래그앤드롭, 동기화 버튼.

---

## 5. 지정 폴더 파일 Reasoning (15-3) — 인터페이스

### 5.1 목표

- **지정 폴더** 또는 **선택한 파일(document_ids)**에 대해 기존 Reasoning 엔진을 실행하고, 결과를 reasoning_results에 저장·표시.

### 5.2 Backend API 인터페이스

| 메서드 | 엔드포인트                                         | 설명                                | 요청                                                                                                    | 응답                                                            |
| ------ | -------------------------------------------------- | ----------------------------------- | ------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| POST   | `/api/reasoning/run-on-documents`                  | 지정 문서(들)에 대해 Reasoning 실행 | `{ "document_ids": [1,2,3] }` 또는 `{ "folder_path": "brain/knowledge" }`, `mode`, `template_id` (선택) | `{ "session_id", "task_id", "message" }` (비동기) 또는 스트리밍 |
| GET    | `/api/reasoning/run-on-documents/status/{task_id}` | 실행 중인 Reasoning 진행 상황       | —                                                                                                       | `{ "status", "progress", "current_document" }`                  |
| GET    | `/api/reasoning/results-by-documents`              | 문서별 Reasoning 결과 목록          | `?document_ids=1,2,3`                                                                                   | `[ { document_id, reasoning_results[] } ]`                      |

- **run-on-documents** 동작: document_ids 또는 folder_path로 documents 조회 → 해당 document의 chunks 또는 본문을 컨텍스트로 Reasoning 실행 (기존 `/api/reason/*`, reason_store, reasoning_results 연동).

### 5.3 Frontend 인터페이스

- **진입점 1**: 지식관리 파일관리 UI에서 파일/폴더 선택 후 **"Reasoning 실행"** 버튼 → 모드/템플릿 선택 모달 → 실행 → 결과 페이지(/reason 또는 전용)로 이동.
- **진입점 2**: 기존 /reason 페이지에 **"지식관리 폴더에서 가져오기"** 옵션: 폴더/문서 선택 후 질의 컨텍스트로 사용.
- **공통**: 진행 중 Progress, 완료 시 session_id·결과 링크, reasoning_results 목록 표시.

### 5.4 Backend 연동

- 기존 `reason_store`, `reasoning_results`, 스트리밍(Phase 13-5) 재사용.
- 신규: “문서/폴더 단위 트리거” 및 “문서별 결과 묶음” 조회 API.

### 5.5 지정 폴더 Reasoning — UI/Backend/API 구성 인터페이스 요약

| 계층           | 구성 요소                                               | 설명                                                                                                                     |
| -------------- | ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| **API**        | `POST /api/reasoning/run-on-documents`                  | 요청: document_ids 또는 folder_path, mode, template_id(선택). 응답: session_id, task_id. (스트리밍 시 StreamingResponse) |
| **API**        | `GET /api/reasoning/run-on-documents/status/{task_id}`  | 실행 중 진행 상황 (polling 또는 SSE).                                                                                    |
| **API**        | `GET /api/reasoning/results-by-documents?document_ids=` | 문서별 reasoning_results 목록.                                                                                           |
| **Backend**    | 서비스 레이어                                           | document_ids/folder_path → documents·chunks 조회 → 기존 reason/reason_store 호출, reasoning_results 저장.                |
| **Backend**    | 라우터                                                  | `routers/reasoning/` 또는 `routers/knowledge/` 하위에 run_on_documents.py 등.                                            |
| **Frontend**   | 진입점                                                  | 지식관리 파일관리 화면: 파일/폴더 선택 → [Reasoning 실행] → 모드 선택 → 실행.                                            |
| **Frontend**   | 진행·결과                                               | Progress 표시, 완료 시 session_id·결과 링크. /reason 또는 전용 결과 페이지에서 reasoning_results 표시.                   |
| **인터페이스** | 요청 스키마                                             | `RunOnDocumentsRequest`: document_ids?: number[], folder_path?: string, mode?: string, template_id?: string.             |
| **인터페이스** | 응답 스키마                                             | `RunOnDocumentsResponse`: session_id, task_id, message. 결과 조회: `ReasoningResultByDocument[]`.                        |

---

## 6. 회원 관리·보안·안정화 (15-5·15-6·15-7) — 요약

### 6.1 회원 관리 시스템 완성 (15-5)

- **users 테이블**: 실제 생성 및 마이그레이션(Alembic 등). Phase 14-5 플랜에서 확장.
- **CRUD**: 회원 가입, 프로필 수정, 비밀번호 변경 API 및 검증(비밀번호 정책·중복 체크).
- **Admin UI**: 전용 사용자 목록 페이지, 권한(Role) 할당 UI. require_admin_system 적용.

### 6.2 보안 및 세션 관리 강화 (15-6)

- **토큰 만료·Refresh Token**: Access Token 만료 처리, Refresh Token 발급·갱신 API 도입.
- **로그아웃 블랙리스트**: 로그아웃 시 해당 토큰을 Redis에 블랙리스트 등록, 검증 시 차단.
- **비인증 리다이렉트**: Phase 14 권장 반영 — 비인증 사용자가 보호된 페이지 접근 시 로그인 페이지로 강제 리다이렉트(HTML 요청 시 302, API는 401 유지).

### 6.3 서비스 안정화 및 최종 검증 (15-7)

- **부하 테스트**: 전체 시스템 부하 테스트 시나리오 실행, 목표 RPS·지연 시간 검증.
- **메모리 누수 점검**: 장시간 실행·반복 요청 시 메모리 사용량 모니터링 및 이상 여부 점검.
- **Docker Production**: 실제 운영 환경(Docker Production) 설정 검증(환경변수·볼륨·헬스체크·리소스 제한).

### 6.4 지식관리 AI 자동화 (15-2) — API·UI 요약

- **API**: `POST /api/automation/run-full`, `GET /api/automation/progress/{task_id}`, `POST /api/automation/cancel/{task_id}`, `GET /api/automation/tasks`, `POST /api/automation/approve-pending` (260216 §6.1).
- **UI**: /admin/ai-automation, 3-Column(문서 선택 / Progress / 결과), SSE로 진행률·단계명 갱신.
- **메뉴**: LNB 지식관리 그룹에 "AI 자동화" 추가.

---

## 7. 의존성 및 순서

- **15-1** 선행: 지정 폴더·파일 목록/업로드/동기화가 있어야 15-2(자동화 대상 문서), 15-3(Reasoning 대상 문서) 선택 가능.
- **15-2**와 **15-3**은 15-1 완료 후 병렬 가능.
- **15-4**는 15-1 폴더 규칙 확정 후 시드·검증 옵션 반영.
- **15-5** 회원 관리: Phase 14-5(플랜·기본 API) 확장. users 테이블·마이그레이션 선행 후 CRUD·Admin UI. 15-6(Refresh Token·블랙리스트)과 연동.
- **15-6** 보안·세션: 15-5와 병렬 또는 이후. Redis 사용 시 인프라 전제.
- **15-7** 안정화·검증: 15-1~15-6 완료 후 또는 병렬로 부하 테스트·Docker Production 검증.
- **15-8** (선택) 260216-1725 보고서 반영: D3.js 지식 그래프·Redis/Qdrant 고도화·4대 추론 모드 정리. 15-2·15-3·15-6·15-7과 연계 가능.

---

## 8. 성공 기준 (체크리스트)

- [ ] **15-1** 지정 폴더 설정·파일 목록·업로드·동기화 API 및 파일관리 UI 동작.
- [ ] **15-2** AI 자동화 메뉴·run-full·SSE progress·3-Column 페이지·6단계 워크플로우 동작.
- [ ] **15-3** 지정 폴더/문서 대상 Reasoning API·FE 진입점·진행·결과 표시 동작.
- [ ] **15-4** 지식관리 폴더와 documents/projects/labels 매핑 규칙 문서화·시드/검증 옵션 반영.
- [ ] **15-5** users 테이블·마이그레이션, 회원 가입·프로필·비밀번호 CRUD, Admin 사용자 목록·Role 할당 UI 동작.
- [ ] **15-6** Refresh Token·토큰 블랙리스트(Redis)·비인증 시 로그인 리다이렉트 동작.
- [ ] **15-7** 부하 테스트·메모리 누수 점검·Docker Production 설정 검증 완료.
- [ ] **15-8** (선택) D3.js 지식 그래프 시각화·Redis 캐싱 확대·Qdrant 양자화·4대 추론 모드 정리.

---

## 9. 현재 개발 진행 상황과의 교차 체크

Phase 15 마스터 플랜과 실제 코드·라우트·Phase 14 상태를 대조한 결과이다.

### 9.1 Phase 14 완료 상태

| Phase | 상태 | 비고                                                   |
| ----- | ---- | ------------------------------------------------------ |
| 14-1  | DONE | 권한·메뉴·403 (phase-14-1-status.md)                   |
| 14-2  | DONE | Swagger 태그·securitySchemes (phase-14-2-status.md)    |
| 14-3  | DONE | 와이드 레이아웃·LNB (phase-14-3-status.md)             |
| 14-5  | DONE | 사용자·로그인·회원관리 플랜·API (phase-14-5-status.md) |
| 14-6  | DONE | DB 샘플·1차 검증 (phase-14-6-status.md)                |

→ **선행 조건 충족**. Phase 15 착수 시 14-4(선택) 제외하고 반영 완료된 상태 기준으로 진행.

### 9.2 Automation (15-2 대비)

| 항목         | 현재 상태                                                                              | Phase 15 지시                                                                                                                         |
| ------------ | -------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| **API**      | `/api/automation/labels/auto`, `/labels/batch-auto`, `/relations/auto-suggest` 만 존재 | **run-full, progress/{task_id}, cancel/{task_id}, tasks, approve-pending** 신규 구현 필요 (260216 §6.1)                               |
| **서비스**   | automation_service: auto_label_chunks, batch_auto_label, auto_suggest_relations        | 6단계 워크플로우(청크 생성→키워드→라벨→연결→승인→임베딩)는 **신규 구현** 또는 automation_service 확장. 기존 auto_label 등 재사용 가능 |
| **SSE/상태** | 없음                                                                                   | Redis 또는 메모리로 task_id별 progress 저장, `/api/automation/progress/{task_id}` SSE 응답 구현                                       |
| **HTML**     | \_HTML_ROUTES에 `/admin/ai-automation` **없음**                                        | **15-2-4**: 라우트 추가 `("/admin/ai-automation", "admin/ai-automation.html", "AI 자동화")`, 템플릿 신규 작성                         |
| **LNB**      | 지식관리 그룹에 "AI 자동화" 메뉴 **없음**                                              | **15-2-5**: LNB/메뉴 상수에 path `/admin/ai-automation`, label "AI 자동화" 추가                                                       |

### 9.3 Knowledge·지정 폴더 (15-1 대비)

| 항목            | 현재 상태                                                                                   | Phase 15 지시                                                                                                                     |
| --------------- | ------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| **API**         | `/api/knowledge` (chunks, labels 등), **folder-config / folder-files / upload / sync 없음** | **15-1-1~15-1-3**: folder-config(GET/PUT), folder-files(GET), upload(POST), sync(POST) **신규 구현**                              |
| **폴더 경로**   | 설정 없음                                                                                   | 기본값 `brain/knowledge`(프로젝트 루트 기준 상대경로). Admin 설정 또는 환경변수(예: KNOWLEDGE_FOLDER_PATH)로 변경 가능하도록 설계 |
| **파일관리 UI** | 없음                                                                                        | 15-1-4: 지식관리 메뉴 하위 또는 전용 "파일관리" 페이지·테이블·업로드/동기화 버튼                                                  |

### 9.4 Reasoning (15-3 대비)

| 항목     | 현재 상태                                                                                  | Phase 15 지시                                                                                                                                            |
| -------- | ------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **API**  | `/api/reason/*`, reason_stream: project_ids, label_names, label_ids, category 로 청크 수집 | **document_ids 또는 folder_path** 기준 run-on-documents **없음**                                                                                         |
| **연동** | collect_knowledge_from_projects, from_labels, from_label_ids, from_category 존재           | **15-3-1**: document_ids 또는 folder_path → documents 조회 → 해당 청크로 컨텍스트 구성하는 엔드포인트·서비스 신규. reason_store·reasoning_results 재사용 |

### 9.5 누락 지시사항 보완 (반영 사항)

| #   | 누락·보완 내용       | 반영                                                                                                                                                                |
| --- | -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | **권한**             | 15-1·15-2·15-3 API는 Phase 14 권한(require_admin_knowledge) 적용 대상. 새 라우트 등록 시 Depends(require_admin_knowledge) 적용                                      |
| 2   | **HTML 라우트**      | 15-2-4 시 \_HTML_ROUTES에 `("/admin/ai-automation", "admin/ai-automation.html", "AI 자동화")` 추가 필요함을 §9.2에 명시                                             |
| 3   | **지정 폴더 저장소** | 폴더 경로 저장: Admin 설정 테이블(예: policy_sets 또는 별도 key-value) 또는 환경변수. 15-1-1에서 "설정 또는 기본 brain/knowledge" 구체화                            |
| 4   | **자동화 취소·에러** | run-full 취소 시 task 상태를 cancelled로 갱신, 진행 중인 백그라운드에는 중단 플래그 전달. 부분 실패 시 단계별 롤백 또는 "실패 단계부터 재시도" 정책 문서화 권장     |
| 5   | **E2E·테스트**       | Phase 15 완료 시 E2E: 파일관리(목록·업로드), AI 자동화(run-full·progress), Reasoning run-on-documents 시나리오 추가 권장. 성공 기준에 "E2E(선택)" 항목 추가         |
| 6   | **기존 ingest 연동** | 지정 폴더 업로드/동기화 시 기존 문서 파싱·청크 생성 파이프라인(ingest, knowledge)과 동일 규칙 사용. file_path는 지정 폴더 기준 상대 경로 또는 절대 경로 정책 명확화 |

---

## 10. 참고 문서

| 문서                                                                                                                       | 용도                                      |
| -------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| [260216-1459-지식관리-ai-자동화-추천-기능-설계.md](../planning/260216-1459-지식관리-ai-자동화-추천-기능-설계.md)           | AI 자동화 워크플로우·API·UI·프롬프트 상세 |
| [260210-1400-db-sample-data-and-high-level-strategy.md](../planning/260210-1400-db-sample-data-and-high-level-strategy.md) | DB 구조·시드·카테고리·검증                |
| [260216-1725-PAB 지능형 지식 관리 시스템: Phase 15 고도화 전략 및 기술 아키텍처 보고서](../planning/260216-1725-PAB%20지능형%20지식%20관리%20시스템%3A%20Phase%2015%20고도화%20전략%20및%20기술%20아키텍처%20보고서.md) | 고도화 전략·Baseline/Target·Redis/Qdrant·D3.js·마일스톤 |
| [phase-14-master-plan-guide.md](phase-14-master-plan-guide.md)                                                             | 선행 Phase 14 범위·14-6 DB 샘플           |
| [phase-14-1/phase-14-1-status.md](phase-14-1/phase-14-1-status.md) 등                                                      | Phase 14 진행 상태 교차 체크              |
| [phase-13-2/route-menu-mapping.md](phase-13-2/route-menu-mapping.md)                                                       | 메뉴 path·라우트 대응                     |

---

## 11. 성공 기준 보강 (체크리스트)

- [ ] **15-1** 지정 폴더 설정·파일 목록·업로드·동기화 API 및 파일관리 UI 동작. 권한(require_admin_knowledge) 적용.
- [ ] **15-2** AI 자동화 메뉴(/admin/ai-automation)·run-full·SSE progress·3-Column 페이지·6단계 워크플로우 동작. \_HTML_ROUTES·LNB 메뉴 반영.
- [ ] **15-3** 지정 폴더/문서 대상 Reasoning API·FE 진입점·진행·결과 표시 동작.
- [ ] **15-4** 지식관리 폴더와 documents/projects/labels 매핑 규칙 문서화·시드/검증 옵션 반영.
- [ ] **15-5** users 테이블·마이그레이션, 회원 가입·프로필·비밀번호 CRUD, Admin 사용자 목록·Role 할당 UI. 권한(require_admin_system) 적용.
- [ ] **15-6** Refresh Token·토큰 블랙리스트(Redis)·비인증 시 로그인 리다이렉트 동작.
- [ ] **15-7** 부하 테스트·메모리 누수 점검·Docker Production 설정 검증 완료.
- [ ] **15-8** (선택) D3.js 지식 그래프·Redis/Qdrant 고도화·4대 추론 모드 문서화.
- [ ] **E2E** 파일관리·AI 자동화 실행·Reasoning run-on-documents 시나리오 추가 및 회귀 통과.

---

**문서 상태**: Phase 15 마스터 플랜. 회원 관리(15-5)·보안·세션(15-6)·안정화·검증(15-7) 포함. 260216-1725 고도화 전략·기술 아키텍처 보고서 반영(§2.3·선택 15-8). 현재 개발 진행과 교차 체크(§9)·누락 지시사항 보완(§9.5)·성공 기준 보강(§11) 반영.
**다음 단계**: 15-1부터 Task 세분화·착수. 구현 시 §9(교차 체크) 참고하여 기존 코드와 충돌 없이 신규 API·라우트·메뉴 추가. 고도화 목표는 §2.3·15-8 참고.
