# SSOT 비교 분석 리포트 — claude/ (현행 9종) vs renewal/iterations/3rd/ (3차 고도화)

**작성일**: 2026-02-17 16:00  
**대상**: `docs/SSOT/claude/` (현 버전 9종), `docs/SSOT/renewal/iterations/3rd/` (3차 고도화)  
**목적**: 두 SSOT 세트 간 구조·내용·전략 차이를 분석하여 마이그레이션·선택 시 참고

---

## 1. 요약

| 구분 | claude/ (현행) | renewal/iterations/3rd/ (3차) |
|------|----------------|-------------------------------|
| **버전 체계** | 4.x (index 4.3, project 4.2, architecture 4.0, workflow 4.5) | 5.0-renewal-r3 (통합 릴리스) |
| **문서 수** | 9개 파일 | 13개 파일 (VERSION 포함) |
| **총 줄 수** | 약 3,174줄 | 약 2,496줄 (GUIDES 포함) |
| **진입점** | `0-ssot-index.md` (인덱스·역할 매핑·Lock/Freshness) | `0-entrypoint.md` (역할별 체크리스트·코어 요약) |
| **전략** | 단일 폴더·역할당 1개 전용 SSOT | 요약+상세 분리(방안 C) + 작업지시 GUIDES 분리 |
| **Planner 전용 문서** | 있음 (`role-planner-ssot.md`) | 없음 (진입점 내 팀 구조에만 포함) |

---

## 2. 문서 구성 비교

### 2.1 claude/ (9종)

| # | 파일명 | 줄 수 | 역할 |
|---|--------|:-----:|------|
| 0 | `0-ssot-index.md` | 299 | 진입점·역할 매핑·팀 라이프사이클·Lock/Freshness/Authority·로딩 순서·통신 프로토콜·비용 관리 |
| 1 | `1-project-ssot.md` | 577 | 프로젝트 정의·팀 구성·품질 게이트·테스트 전략·Task 도메인·산출물 |
| 2 | `2-architecture-ssot.md` | 515 | 인프라·백엔드/프론트엔드 코드 구조·DB·API·보안·검증 기준 |
| 3 | `3-workflow-ssot.md` | 1,058 | ENTRYPOINT·상태 머신·상태 파일·워크플로우 실행·에러 처리·리와인드·완료 판정·Phase Chain |
| — | `role-planner-ssot.md` | 125 | Planner 전용: SSOT 버전·리스크·Task 분해·G1 기준 |
| — | `role-backend-dev-ssot.md` | 153 | Backend Developer: 역할·디렉토리·코드 규칙·통신 |
| — | `role-frontend-dev-ssot.md` | 153 | Frontend Developer: 역할·디렉토리·코드 규칙·통신 |
| — | `role-verifier-ssot.md` | 148 | Verifier: G2 판정 기준·도메인별·출력 형식 |
| — | `role-tester-ssot.md` | 146 | Tester: 테스트 레벨·명령·G3·리포트 형식 |

**특징**: 코어 4개(0~3) + 역할별 5개(planner, backend-dev, frontend-dev, verifier, tester). 역할 문서에 “작업지시”까지 포함된 일괄 구조.

### 2.2 renewal/iterations/3rd/ (13종)

| 위치 | 파일명 | 줄 수 | 역할 |
|------|--------|:-----:|------|
| 루트 | `0-entrypoint.md` | 383 | 진입점·역할별 필독 체크리스트·코어 개념 요약·BE/FE/Verifier/Tester 규칙 요약·상세 링크 |
| 루트 | `1-project.md` | 434 | 프로젝트 정의·팀 구성 (요약, 기반: 1-project-ssot.md) |
| 루트 | `2-architecture.md` | 387 | 인프라·BE/FE 구조 (요약, 기반: 2-architecture-ssot.md) |
| 루트 | `3-workflow.md` | 326 | ENTRYPOINT·상태 머신·Action Table (요약, 기반: 3-workflow-ssot.md) |
| 루트 | `VERSION.md` | 96 | 통합 버전·파일별 변경·역할별 읽기 경로·Breaking Changes |
| ROLES/ | `backend-dev.md` | 73 | Backend Developer: 역할 정의·필독 체크리스트·코드 규칙 요약·GUIDES 참조 |
| ROLES/ | `frontend-dev.md` | 72 | Frontend Developer: 동일 구조 |
| ROLES/ | `verifier.md` | 100 | Verifier: 역할·검증 기준 요약·GUIDES 참조 |
| ROLES/ | `tester.md` | 89 | Tester: 역할·테스트 요약·GUIDES 참조 |
| GUIDES/ | `backend-work-guide.md` | 137 | Backend 작업지시: Task 실행 프로세스·수정 플로우·완료 보고 형식 |
| GUIDES/ | `frontend-work-guide.md` | 120 | Frontend 작업지시 |
| GUIDES/ | `verifier-work-guide.md` | 127 | Verifier 검증 프로세스 |
| GUIDES/ | `tester-work-guide.md` | 150 | Tester 테스트 프로세스 |

**특징**: 코어 4개는 “요약”만 두고, 상세는 claude/ 참조. ROLES/는 역할 정의+규칙 요약만 두고, **작업지시(실행 프로세스)**는 GUIDES/로 분리. Planner 전용 문서 없음.

---

## 3. 차이점 상세 분석

### 3.1 진입점·인덱스

| 항목 | claude/ `0-ssot-index.md` | 3rd `0-entrypoint.md` |
|------|---------------------------|------------------------|
| **초점** | 인덱스·Lock/Freshness·Authority Chain·로딩 순서·팀 통신 프로토콜·비용 관리 | **역할별 “당신의 역할은?”** 체크리스트·코어 개념 요약·빠른 시작 |
| **역할별 가이드** | 테이블로 팀원 이름·subagent_type·전용 SSOT 파일만 안내 | 역할별 **필독 체크리스트**(§2.1~2.5)·예상 읽기 시간(8~25분)·Task 시작 시 GUIDES 링크 |
| **코어 규칙 노출** | Document Authority·FRESH-6 팀원 로딩 규칙 상세 | §3 코어 개념 요약(Lock/Freshness/ENTRYPOINT/품질게이트/도메인태그)·§4~6 BE/FE/Verifier 핵심 규칙 요약 |
| **상세 위치** | 동일 폴더 내 1~3·role-* 참조 | 1~3·ROLES/*·GUIDES/* 링크 + “기존 SSOT 상세(claude/)” 링크 |
| **목표 읽기 시간** | 명시 없음 | 10~15분(500줄 수준) 명시 |

**차이 요약**: 3rd는 “역할 선택 → 체크리스트 → 코어 요약 → 필요 시 상세” 흐름으로, 진입 시 읽기 부담을 줄이고 Task 시작 시에만 GUIDES를 열도록 설계됨. claude는 인덱스와 규칙을 한 문서에 모아 팀 Lead 중심.

### 3.2 코어 문서 (1·2·3)

| 문서 | claude/ | 3rd | 차이 |
|------|---------|-----|------|
| **1 (Project)** | `1-project-ssot.md` 577줄, 품질 게이트·테스트 전략·Task 도메인·산출물·참조 문서 전부 포함 | `1-project.md` 434줄, “기반: 1-project-ssot.md” 명시·팀 구성·역할 매핑 중심 요약 | 3rd는 요약본, 상세는 claude/ 1-project-ssot 참조 |
| **2 (Architecture)** | `2-architecture-ssot.md` 515줄, 디렉토리 맵·DB 스키마·API 규칙·보안·검증 기준 §8 전부 | `2-architecture.md` 387줄, 인프라·BE/FE 구조 요약·Redis 포트 6380 기재(오타 가능, claude는 6379) | 3rd는 요약·상세는 claude/ 2-architecture-ssot 참조 |
| **3 (Workflow)** | `3-workflow-ssot.md` 1,058줄, ENTRYPOINT·상태 16개·전이 규칙·Step 1~8·에러·리와인드·완료 판정·Phase Chain·참조 매핑 | `3-workflow.md` 326줄, ENTRYPOINT·상태 정의·**상태별 Action Table**·품질 게이트 요약·상세는 claude/ 링크 | 3rd는 상태 머신·다음 행동 결정에 집중, 나머지는 claude/ 3-workflow-ssot 참조 |

**공통점**: ENTRYPOINT 규칙(ENTRY-1~5), FRESH-1~6, LOCK-1~5, 품질 게이트 G1~G4, 도메인 태그 개념은 양쪽 모두 유지. 3rd는 “요약+상세 분리(방안 C)”로 동일 내용을 짧게 보여 주고 상세는 claude/로 유도.

### 3.3 역할 문서

| 역할 | claude/ | 3rd | 차이 |
|------|---------|-----|------|
| **Planner** | `role-planner-ssot.md` 125줄: SSOT 버전·리스크 확인·Task 분해·G1 기준·출력 형식 | **전용 문서 없음**. 0-entrypoint §3.1 팀 구조에 `planner` 포함, §2에는 역할별 체크리스트 없음 | 3rd는 Planner를 “팀 구조 내 역할”로만 다루고, 전용 읽기 경로·체크리스트 없음 |
| **Backend Dev** | `role-backend-dev-ssot.md` 153줄: 역할·디렉토리·도메인 태그·코드 규칙·통신·Task 수신→구현→보고 | `ROLES/backend-dev.md` 73줄 + `GUIDES/backend-work-guide.md` 137줄. ROLES는 역할·체크리스트·코드 규칙 요약만, “Task 실행 프로세스·수정 플로우”는 GUIDES로 분리 | 3rd는 역할 정의와 **작업지시(언제 무엇을 읽을지)** 분리. Task 시작 시만 GUIDES 참조 |
| **Frontend Dev** | `role-frontend-dev-ssot.md` 153줄 (구조 동일) | `ROLES/frontend-dev.md` 72줄 + `GUIDES/frontend-work-guide.md` 120줄 | 동일 패턴 |
| **Verifier** | `role-verifier-ssot.md` 148줄: G2 BE/FE 기준·판정 규칙·도메인별·출력 형식 | `ROLES/verifier.md` 100줄 + `GUIDES/verifier-work-guide.md` 127줄. ROLES는 검증 기준 요약, “검증 프로세스”는 GUIDES | 동일 패턴 |
| **Tester** | `role-tester-ssot.md` 146줄: 테스트 레벨·명령·G3·리포트 형식 | `ROLES/tester.md` 89줄 + `GUIDES/tester-work-guide.md` 150줄. ROLES는 역할·테스트 요약, “테스트 프로세스”는 GUIDES | 동일 패턴 |

**차이 요약**:
- claude/: 역할당 **한 파일**에 “역할 정의 + 코드 규칙 + 작업지시” 모두 포함.
- 3rd: **ROLES/** = 역할 정의 + 필독 체크리스트 + 규칙 요약, **GUIDES/** = Task/검증/테스트 **실행 프로세스** 상세. “필수 읽기 1,962줄(GUIDES 제외)”로 역할별 상시 읽기 분량을 줄이고, 작업 시작 시에만 GUIDES 534줄 추가.

### 3.4 버전·릴리스 관리

| 항목 | claude/ | 3rd |
|------|---------|-----|
| **버전** | 파일별 헤더(0: 4.3, 1: 4.2, 2: 4.0, 3: 4.5, role-*: 1.x) | 통합 `VERSION.md`: 5.0-renewal-r3, 이전 5.0-renewal-r2/r1·4.5(claude/) 명시 |
| **변경 이력** | 0-ssot-index 하단 버전 히스토리 테이블 | VERSION.md 내 “변경 이력”·“Breaking Changes”·“파일별 버전” 테이블 |
| **읽기 분량 정리** | 없음 | VERSION.md에 “역할별 필수 읽기·시간·Task 시 추가 읽기” 표로 정리 |

3rd는 **한 곳(VERSION.md)**에서 릴리스·파일별 변경·역할별 읽기 경로를 관리함.

### 3.5 워크플로우·상태

| 항목 | claude/ | 3rd |
|------|---------|-----|
| **상태 수** | 16개 (IDLE, TEAM_SETUP, PLANNING, PLAN_REVIEW, TASK_SPEC, BUILDING, VERIFYING, TESTING, INTEGRATION, E2E, E2E_REPORT, TEAM_SHUTDOWN, BLOCKED, REWINDING, DONE 등) | 14개 + α (0-entrypoint §3.2 “8단계 + α”, TEAM_SHUTDOWN 포함). 3-workflow.md는 상태 정의·Action Table 위주 |
| **ENTRYPOINT** | 3-workflow-ssot §0 상세 플로우(팀 상태 확인 Step 6 포함) | 0-entrypoint §3.6·3-workflow §0 요약 플로우, 상세는 claude/ 링크 |
| **Phase Chain** | 3-workflow-ssot Section 9 — 복수 Phase 자동 순차 실행 프로토콜 | 3rd 문서에는 Phase Chain 섹션 없음 (claude/ 참조) |

3rd는 “다음에 할 일” 결정에 필요한 상태·Action 수준만 두고, 전이 상세·Phase Chain은 claude/ 3-workflow-ssot에 위임.

### 3.6 팀 통신·라이프사이클

| 항목 | claude/ | 3rd |
|------|---------|-----|
| **팀 라이프사이클** | 0-ssot-index에 TeamCreate → Task tool 스폰 → TaskCreate/Update → SendMessage → shutdown_request → TeamDelete 단계 명시 | 0-entrypoint §3.1 팀 구조·§3.3 Hub-and-Spoke만 요약, 상세는 claude/ |
| **SendMessage 유형** | message, broadcast, shutdown_request, shutdown_response 표로 정리 | 0-entrypoint §3.3 예시로 간단 기술 |
| **Hub-and-Spoke** | 동일 원칙 (모든 통신 Team Lead 경유) | 동일 원칙 |

원칙은 동일하고, 3rd는 요약·예시 위주로만 노출.

---

## 4. 정량 비교

| 구분 | claude/ | 3rd (GUIDES 포함) | 3rd (GUIDES 제외) |
|------|:-------:|:-----------------:|:-----------------:|
| **총 줄 수** | 약 3,174 | 약 2,496 | 약 1,962 |
| **진입점** | 299 | 383 | 383 |
| **코어 1+2+3** | 2,150 | 1,147 | 1,147 |
| **역할 문서** | 725 (5개) | 334 (ROLES 4개) | 334 |
| **작업지시** | 역할 문서 내 포함 | 534 (GUIDES 4개) | — |
| **버전 전용** | — | 96 (VERSION.md) | 96 |
| **Planner 전용** | 125 | 0 | 0 |

3rd는 GUIDES를 제외하면 **약 1,962줄**로, claude/ 대비 **약 38% 감소**. 역할별 “필수 읽기”는 8~25분으로 제한하고, 작업 시작 시에만 GUIDES를 추가로 읽도록 설계됨.

---

## 5. 전략 차이 요약

| 전략 | claude/ | 3rd |
|------|---------|-----|
| **구조** | 단일 디렉터리·파일명 규칙(0~3, role-*-ssot) | 루트(0~3, VERSION) + ROLES/ + GUIDES/ |
| **상세 위치** | 모든 상세를 동일 세트 내에 보유 | 요약만 3rd에 두고, 상세는 claude/ 참조(명시적 “기반: …” 표기) |
| **역할별 읽기** | 팀원당 1개 파일(role-*-ssot) 로딩 | 역할별 체크리스트(0-entrypoint) → ROLES/* → 필요 시 1~3·GUIDES/* |
| **작업지시** | 역할 문서에 포함 | GUIDES/로 분리해 “Task 시작 시만” 로딩 |
| **Planner** | 전용 문서로 SSOT 버전·리스크·Task 분해 명시 | 전용 문서 없음, 팀 구조에서만 언급 |
| **버전** | 파일별 버전 | VERSION.md 통합 릴리스·Breaking Changes |

---

## 6. 호환성·마이그레이션 고려사항

1. **3rd는 claude/에 의존**  
   1~3·ROLES가 “기반: claude/ …” 또는 “상세: claude/ …”로 링크하므로, 3rd만 사용할 경우에도 claude/ 코어 문서(1~3) 유지가 전제됨.

2. **Planner 사용 시**  
   Planner 팀원을 쓰는 워크플로우에서는 3rd만으로는 부족하고, `claude/role-planner-ssot.md`를 추가로 로딩하거나, 3rd에 ROLES/planner.md·GUIDES/planner-work-guide.md를 신설하는 선택이 필요함.

3. **진입점 선택**  
   - **팀 Lead·전체 규칙 한눈에**: claude/ `0-ssot-index.md` + 1~3.  
   - **역할별 빠른 시작·읽기 부담 감소**: 3rd `0-entrypoint.md` + 역할별 체크리스트 + ROLES/* + (작업 시) GUIDES/*.

4. **문서 이중 유지**  
   VERSION.md에 “하위 호환성: 기존 claude/ 문서 전체 유지”라고 되어 있으므로, 현재는 두 세트 병존이 전제. 장기적으로 3rd를 기본으로 하면 claude/는 “상세 참조용”으로만 둘 수 있음.

---

## 7. 결론 및 권장

- **claude/ (9종)**: 단일 세트로 “인덱스 + 코어 + 역할(작업지시 포함)”을 모두 갖춘 **완결형**. Planner 전용 문서 포함. 줄 수 많음(약 3,174줄).
- **3rd (13종)**: **요약+상세 분리 + 작업지시(GUIDES) 분리**로 역할별 필수 읽기 감소(약 1,962줄, GUIDES 제외). 진입점에서 “역할 선택 → 체크리스트 → 코어 요약” 흐름 제공. Planner 전용 문서 없음.

**권장**:
- 3rd를 **기본 진입점**으로 쓰고, 상세·Phase Chain·Planner는 claude/로 참조하는 조합이 적합.
- Planner를 3rd에서도 쓰려면 `ROLES/planner.md`(및 필요 시 GUIDES) 추가를 권장.
- SSOT 갱신 시: claude/ 0~3을 정답(Source of Truth)으로 두고, 3rd의 1~3·0-entrypoint는 “요약 동기화”로 유지하면 정합성 유지에 유리함.

---

## 8. 4th iteration 반영 (2026-02-17)

**경로**: `docs/SSOT/renewal/iterations/4th/`

4th는 **claude 의존성을 제거**하고 **단독 사용**이 가능하도록 만든 업그레이드이다.

| 항목 | 4th |
|------|-----|
| **팀 라이프사이클** | 0-entrypoint §3.9에 TeamCreate → Task tool 스폰 → TaskCreate/Update/SendMessage → shutdown_request → TeamDelete 단계 명시, DONE 후 루프 반복 |
| **Phase Chain** | 3-workflow.md §8에 Phase Chain 정의·실행 프로토콜·/clear 복구·CHAIN-1~9 규칙 포함 (claude 참조 없음) |
| **Planner** | ROLES/planner.md, GUIDES/planner-work-guide.md 신규. G1·Task 분해·출력 형식 4th 내부만 참조 |
| **참조** | 모든 상세 링크가 4th 내부(0~3, ROLES, GUIDES)만 사용. claude/ 폴더 없이 SSOT 완결 |

**권장**: 4th를 기본 진입점으로 사용하면 claude/ 유지 없이 단독 SSOT로 동작 가능.  
갱신 시 4th의 0~3·ROLES·GUIDES를 Source of Truth로 두면 정합성 유지에 유리함.

---

**문서 상태**: 비교 분석 완료. 4th iteration 반영.  
**참조**: docs/SSOT/claude/, docs/SSOT/renewal/iterations/3rd/, **iterations/4th/** (v6.0-renewal-4th).
