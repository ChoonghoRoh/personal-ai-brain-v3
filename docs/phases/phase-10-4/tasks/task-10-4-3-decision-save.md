# Task 10-4-3: 의사결정 문서 저장

**우선순위**: 10-4 내 3순위  
**예상 작업량**: 2일  
**의존성**: Phase 10-3 완료 후 권장  
**상태**: ✅ 완료

**기반 문서**: [phase-10-4-0-todo-list.md](../phase-10-4-0-todo-list.md)  
**작업 순서**: [phase-10-navigation.md](../../phase-10-navigation.md)

---

## 1. 개요

### 1.1 목표

Reasoning **결과를 의사결정 문서로 저장**하고, 저장 목록(또는 링크)을 통해 나중에 조회할 수 있도록 한다.

### 1.2 대상

| 대상                 | 내용                                   |
| -------------------- | -------------------------------------- |
| 스키마               | 제목, 요약, 결과 스냅샷, 일시 등       |
| 저장 API·DB/스토리지 | 저장·조회 API 연동                     |
| UI                   | "저장" 버튼, 저장 목록(또는 링크) 제공 |

---

## 2. 파일 변경 계획

### 2.1 신규/수정

| 파일 경로                      | 용도                                |
| ------------------------------ | ----------------------------------- |
| 백엔드: 의사결정 문서 모델·API | 스키마 정의, 저장·조회 API          |
| DB/스토리지                    | 문서 저장 (PostgreSQL 또는 파일 등) |
| 프론트엔드: Reasoning 페이지   | "저장" 버튼, 저장 목록·조회 UI      |

---

## 3. 작업 체크리스트

### 3.1 스키마·API

- [x] 의사결정 문서 스키마: `reasoning_results` 테이블에 `title`, `summary` 컬럼 추가
- [x] 저장 API 및 DB 연동
  - [x] `POST /api/reason/decisions` — 저장
  - [x] `GET /api/reason/decisions` — 목록 조회 (최신순 50건)
  - [x] `GET /api/reason/decisions/{id}` — 상세 조회
  - [x] `DELETE /api/reason/decisions/{id}` — 삭제

### 3.2 UI

- [x] Reasoning 페이지 "저장" 버튼 (results-toolbar)
- [x] 저장 모달 (제목 필수, 요약 선택)
- [x] 저장 목록 UI (decisions-list-section) — 보기/삭제 기능

---

## 4. 참고 문서

- [Phase 10-4 Plan](../phase-10-4-0-plan.md)
- [Phase 10-4 Todo List](../phase-10-4-0-todo-list.md)
- [Task 10-3-1 공통 결과 구조](../../phase-10-3/tasks/task-10-3-1-common-result-structure.md) — 스냅샷 구조 참고
- [Task 10-4-2 결과 공유](task-10-4-2-share-url.md) — 스냅샷 저장과 연계 가능
