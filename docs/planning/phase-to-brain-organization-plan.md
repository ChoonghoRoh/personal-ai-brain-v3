# Phase 폴더 → Brain 폴더 정리 방안

**작성일**: 2026-02-09  
**목표**: AI 질의(Ask/RAG)가 이번 프로젝트 전반에 대해 답변할 수 있도록, docs/phases 문서를 brain 폴더로 정리하는 방법을 구상·정리한다.  
**범위**: 정리 방안 설계 및 planning 문서화. 실제 이전·스크립트 구현은 별도 Task에서 진행.

---

## 1. 목표 및 배경

### 1.1 목표

- **AI 질의에 프로젝트 전반 답변 가능**: 사용자가 "Phase 14에서 뭘 하나요?", "지금 메뉴 구조는?", "권한 검증은 어디서 하죠?" 등 질문 시, RAG/검색이 **phase·planning·개발 현황** 문서를 참조해 답할 수 있게 한다.
- **지식 소스 일원화**: phase 관련 문서가 `docs/phases/`에 산재해 있어, **brain**을 "프로젝트 지식 허브"로 두고 phase 문서를 정리해 두면 검색·임베딩·AI 질의 시 한 곳에서 관리할 수 있다.

### 1.2 현황

| 구분 | 내용 |
|------|------|
| **docs/phases** | phase-12-*, phase-13-*, phase-14-* 등 마스터 플랜, status, todo, tasks, QC 리포트, 최종 요약 등 다수 .md 존재. |
| **brain** | `brain/system/`(work_log, todo, status, context), `brain/projects/alpha-project/` 등. context.md에는 reference, inbox, archive 디렉터리 언급. **phase 문서는 아직 없음.** |
| **RAG/검색** | documents 테이블의 file_path 기준으로 .md 수집·청크화·Qdrant 임베딩. 현재 ingest 경로에 brain 또는 docs가 포함되면 해당 경로 문서가 검색 대상. |
| **기존 전략** | [260210-1400-db-sample-data-and-high-level-strategy.md](260210-1400-db-sample-data-and-high-level-strategy.md)에서 docs/phases/* 를 development/planning/review 등 카테고리로 분류해 documents·chunks·labels에 반영하는 방안 정리됨. |

---

## 2. 방안 비교

| 방안 | 설명 | 장점 | 단점 |
|------|------|------|------|
| **A. Brain으로 복사** | docs/phases 내용을 brain 하위로 **복사**. | brain만 스캔하면 됨. 원본 phase와 독립. | 중복·동기화 이슈. docs/phases 수정 시 brain 반영 필요. |
| **B. Brain에 심볼릭 링크** | brain 하위에 docs/phases/** 에 대한 **심볼릭 링크**만 생성. | 단일 트리로 접근 가능. 원본은 docs 유지. | Git에서 심볼릭 링크 처리·OS별 차이. 일부 환경에서 링크 깨짐 가능. |
| **C. Brain 인덱스 + 경로 유지** | phase 문서는 docs에 두고, **brain에는 인덱스(목차)·요약**만 두고, RAG ingest 경로에 docs/phases 포함. | docs 단일 소스. brain은 "무엇이 어디 있는지"만 제공. | "정리해서 brain에 넣는다"는 요구와는 다소 다름. RAG 스코프만 넓히면 됨. |
| **D. Brain으로 주기 동기화** | 스크립트로 docs/phases → brain 하위로 **동기화**(복사 또는 링크). 원본은 docs. | brain이 항상 최신 스냅샷. 자동화 가능. | 스크립트·CI 유지보수. 삭제/이동 시 동기화 규칙 필요. |

**권장**: **D(주기 동기화)** 또는 **B(심볼릭 링크)** 를 1차로 검토.  
- **심볼릭 링크**: 구현이 빠르고, 원본(docs/phases) 유지·brain에서만 "한 트리로 보이게" 할 때 적합.  
- **동기화**: 복사 시 중복이 생기지만, brain 전용 가공(요약·메타 추가)을 넣을 때 유리.  
- **RAG 연동**: 어느 쪽이든 **ingest/검색 경로에 brain 포함**하거나, **documents.file_path 에 brain 상대 경로**가 들어가면 AI 질의 시 검색 대상이 됨.

---

## 3. Brain 폴더 구조 제안

phase 문서를 넣을 brain 하위 구조를 아래처럼 제안한다.

```
brain/
├── system/                    # 기존 유지 (work_log, todo, status, context)
├── projects/
│   └── alpha-project/         # 기존 유지
├── knowledge/                 # 신규: 프로젝트 지식 (phase·planning·개발)
│   ├── phases/                # phase 문서 정리
│   │   ├── phase-12/          # 12-1, 12-2, 12-3 등 하위 참조 또는 링크
│   │   ├── phase-13/
│   │   ├── phase-14/
│   │   └── _index.md          # phase 목차·현재 Phase 요약
│   ├── planning/              # planning 문서 정리
│   │   └── (planning용 링크 또는 복사)
│   └── _index.md              # knowledge 전체 목차 (AI 질의 시 컨텍스트용)
├── reference/                 # 기존 context.md 언급. 참고 자료
├── inbox/
└── archive/
```

- **knowledge/phases/** : docs/phases 의 phase-12, phase-13, phase-14 등을 대응. 하위는 phase-12-1, phase-12-2 … 와 동일 구조를 유지하거나, **한 단계만 펼쳐** phase-12, phase-13, phase-14 폴더만 두고 그 안에 링크/복사.
- **knowledge/planning/** : docs/planning 의 핵심 문서(마스터 플랜, 통합 메뉴, DB 전략 등)를 링크 또는 복사.
- **_index.md** : "지금 프로젝트는 Phase 14, 권한·LNB·DB 샘플 진행 중" 수준의 짧은 요약. RAG가 이 문서를 먼저 읽으면 "프로젝트 전반" 질문에 유리.

---

## 4. Phase → Brain 매핑

### 4.1 디렉터리 대응

| docs 경로 | brain 경로 (제안) | 비고 |
|-----------|-------------------|------|
| docs/phases/phase-12-* | brain/knowledge/phases/phase-12/ | phase-12-1, 12-2, 12-3 하위 그대로 매핑 |
| docs/phases/phase-13-* | brain/knowledge/phases/phase-13/ | phase-13-1 ~ 13-5, tasks 등 |
| docs/phases/phase-14-* | brain/knowledge/phases/phase-14/ | phase-14-1 ~ 14-6, master-plan-guide |
| docs/phases/*.md (루트) | brain/knowledge/phases/ | phase-13-master-plan.md, phase-14-master-plan-guide.md 등 |
| docs/planning/*.md | brain/knowledge/planning/ | 260216-0955-..., 260210-1400-... 등 |

### 4.2 파일 단위 규칙

- **심볼릭 링크 방식**: `brain/knowledge/phases/phase-14` → `../../docs/phases` (또는 phase-14만 링크).  
  또는 파일 단위로 `brain/knowledge/phases/phase-14-master-plan-guide.md` → `../../../docs/phases/phase-14-master-plan-guide.md`.
- **복사/동기화 방식**: 스크립트가 docs/phases/**/*.md 를 읽어 brain/knowledge/phases/ 에 동일 상대 경로로 복사.  
  `docs/phases/phase-14-1/phase-14-1-status.md` → `brain/knowledge/phases/phase-14/phase-14-1/phase-14-1-status.md`.

---

## 5. 동기화 방식

### 5.1 심볼릭 링크 (수동 1회)

- **작업**: brain/knowledge/phases/, brain/knowledge/planning/ 생성 후, 디렉터리 또는 파일 단위로 `ln -s` 실행.
- **예시 (bash)**:
  - `ln -s ../../../docs/phases/phase-14 brain/knowledge/phases/phase-14`
  - `ln -s ../../../docs/planning brain/knowledge/planning`
- **유지**: docs 쪽 수정은 그대로 반영됨. brain에는 새 phase 폴더 추가 시만 링크 추가.

### 5.2 스크립트 동기화 (주기 실행)

- **위치 제안**: `scripts/sync_phase_to_brain.py` 또는 `scripts/brain/sync_knowledge.py`.
- **동작**:  
  1) brain/knowledge/phases/, planning/ 디렉터리 존재 확인.  
  2) docs/phases, docs/planning 목록 수집.  
  3) 복사: 원본 수정 시간이 brain 쪽보다 최신이면 복사. 또는 항상 덮어쓰기.  
  4) (선택) _index.md 자동 생성: phase 목록·planning 목록을 나열한 목차.
- **실행**: 수동 실행 또는 CI(cron/워크플로)에서 주기 실행.

### 5.3 Git·버전 관리

- **docs/phases 유지**: 원본은 계속 docs/phases 에서 편집. 단일 소스.
- **brain/knowledge**:  
  - **링크만 둘 경우**: brain 쪽에는 링크만 커밋.  
  - **복사할 경우**: brain/knowledge 는 "생성물"로 간주하고 .gitignore 할지, 커밋할지 팀 정책 결정. (커밋하면 PR에서 diff로 변경 보임.)

---

## 6. RAG·AI 질의 연동

### 6.1 검색 대상에 brain 포함

- **문서 수집(ingest) 경로**에 `brain/` (또는 `brain/knowledge/`)를 포함시켜, 해당 하위 .md가 **documents** 테이블에 등록되고 **knowledge_chunks** 로 청크화·Qdrant에 임베딩되도록 설정.
- **file_path**: 프로젝트 루트 기준 상대 경로. 예: `brain/knowledge/phases/phase-14/phase-14-master-plan-guide.md`.

### 6.2 라벨·카테고리

- 기존 [DB 샘플·고도화 전략](260210-1400-db-sample-data-and-high-level-strategy.md)과 맞추어, brain/knowledge/phases → **planning** 또는 **development**, brain/knowledge/planning → **planning** 등으로 **labels(category)** 부여하면, AI 질의 시 "계획 문서만", "phase 문서만" 필터링 가능.

### 6.3 _index.md 활용

- `brain/knowledge/_index.md`, `brain/knowledge/phases/_index.md` 에 "현재 Phase 14, 권한·LNB·DB 샘플·2차 검증 진행 중" 수준의 짧은 요약을 두면, RAG가 이 청크를 자주 참조해 "프로젝트 전반" 질의에 일관된 답을 줄 수 있다.

---

## 7. 단계별 실행 순서

| 단계 | 작업 | 산출물 |
|------|------|--------|
| 1 | brain/knowledge/phases/, brain/knowledge/planning/ 디렉터리 생성 | 폴더 구조 |
| 2 | 방식 결정: 심볼릭 링크 vs 복사 vs 스크립트 동기화 | 결정 문서(본 문서에 기록) |
| 3a | (링크) phase·planning 대상에 대해 ln -s 실행 | brain 하위 링크 |
| 3b | (동기화) sync 스크립트 작성·실행 | brain/knowledge 채움 |
| 4 | brain/knowledge/_index.md, phases/_index.md 초안 작성 | 목차·요약 |
| 5 | ingest/검색 경로에 brain/knowledge 포함 여부 확인·설정 | RAG 대상 반영 |
| 6 | (선택) documents·chunks 재구성 후 검색 테스트 | "Phase 14에서 뭘 하나요?" 등으로 검증 |

---

## 8. 요약 및 다음 단계

- **목표**: AI 질의가 프로젝트 전반(phase·planning·현황)에 답할 수 있도록 **phase 문서를 brain 폴더로 정리**.
- **권장**: brain/knowledge/phases/, brain/knowledge/planning/ 을 두고, **심볼릭 링크**로 docs/phases, docs/planning 을 연결하거나, **스크립트로 주기 동기화(복사)**. 원본은 docs 유지.
- **연동**: RAG ingest·검색 경로에 brain(또는 brain/knowledge) 포함 → documents·knowledge_chunks·Qdrant에 반영 → AI 질의 시 해당 청크 검색.
- **다음 단계**: 위 단계 1~2 수행 후, 3a 또는 3b로 실제 링크/동기화 적용. 필요 시 Phase 14 또는 백로그 Task로 "phase → brain 정리" 세부 Task 생성.

---

**관련 문서**

- [260210-1400-db-sample-data-and-high-level-strategy.md](260210-1400-db-sample-data-and-high-level-strategy.md) — .md 카테고리·documents/chunks 매핑
- [phase-14-master-plan-guide.md](../phases/phase-14-master-plan-guide.md) — Phase 14 범위·14-6 등
- brain/system/context.md — brain 디렉터리 구조
