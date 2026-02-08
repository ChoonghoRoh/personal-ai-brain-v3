# Task 9-2-2: Knowledge API 테스트

**우선순위**: 9-2 내 2순위
**예상 작업량**: 1일
**의존성**: 없음
**상태**: ✅ 구현 완료 (tests/test_knowledge_api.py 생성)

**기반 문서**: [phase-9-2-todo-list.md](../phase-9-2-todo-list.md)

---

## 1. 개요

### 1.1 목표

Knowledge 라우터(청크·라벨·관계 CRUD) 및 자동 매칭(Phase 9-3-2 구현물)에 대한 API 테스트를 작성한다.

### 1.2 테스트 대상

| 대상      | 엔드포인트/기능                                     | 비고        |
| --------- | --------------------------------------------------- | ----------- |
| 청크 CRUD | `POST/GET/PUT/DELETE /api/knowledge/chunks*`        |             |
| 라벨 API  | `POST/GET /api/knowledge/labels`, 청크-라벨 연결    |             |
| 관계 API  | `POST/GET /api/knowledge/relations`, 순환 관계 방지 |             |
| 자동 매칭 | 라벨 추천, 관계 추천                                | Phase 9-3-2 |

---

## 2. 파일 변경 계획

### 2.1 신규 생성

| 파일 경로                     | 용도                      |
| ----------------------------- | ------------------------- |
| `tests/test_knowledge_api.py` | Knowledge API 단위 테스트 |

### 2.2 수정

- 없음 (테스트만 추가)

---

## 3. 작업 체크리스트

### 3.1 Knowledge 라우터 테스트

- [ ] `tests/test_knowledge_api.py` 생성
- [ ] 청크 CRUD 테스트
  - [ ] `POST /api/knowledge/chunks` 생성
  - [ ] `GET /api/knowledge/chunks/{id}` 조회
  - [ ] `PUT /api/knowledge/chunks/{id}` 수정
  - [ ] `DELETE /api/knowledge/chunks/{id}` 삭제

### 3.2 라벨 API 테스트

- [ ] `POST /api/knowledge/labels` 라벨 생성
- [ ] `GET /api/knowledge/labels` 라벨 목록
- [ ] 청크-라벨 연결 테스트

### 3.3 관계 API 테스트

- [ ] `POST /api/knowledge/relations` 관계 생성
- [ ] `GET /api/knowledge/relations` 관계 목록
- [ ] 순환 관계 방지 테스트

### 3.4 자동 매칭 테스트 (Phase 9-3-2 구현물)

- [ ] 청크 생성 시 라벨 추천 테스트
- [ ] 승인 시 관계 추천 테스트

---

## 4. 참고 문서

- [Phase 9-2 Todo List](../phase-9-2-todo-list.md)
- [Phase 9-3-2 지식 구조 매칭](../phase-9-3/tasks/task-9-3-2-knowledge-structure-matching.md)
- 기존 테스트: `tests/test_structure_matching.py`
