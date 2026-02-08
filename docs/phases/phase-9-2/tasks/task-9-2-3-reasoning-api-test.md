# Task 9-2-3: Reasoning API 테스트

**우선순위**: 9-2 내 3순위
**예상 작업량**: 0.5일
**의존성**: 없음
**상태**: ✅ 구현 완료 (tests/test_reasoning_api.py 생성)

**기반 문서**: [phase-9-2-todo-list.md](../phase-9-2-todo-list.md)

---

## 1. 개요

### 1.1 목표

Reasoning 라우터(`POST /api/reason`) 및 Recommendations API(Phase 9-3-1 구현물)에 대한 테스트를 확장·추가한다.

### 1.2 테스트 대상

| 대상            | 엔드포인트/기능                     | 비고                               |
| --------------- | ----------------------------------- | ---------------------------------- |
| Reasoning       | `POST /api/reason`                  | 모드별, 필터, 질문 유무            |
| Recommendations | `GET /api/reason/recommendations/*` | chunks, labels, questions, explore |

---

## 2. 파일 변경 계획

### 2.1 신규 생성

- 없음 (기존 테스트 파일 확장)

### 2.2 수정

| 파일 경로                                 | 수정 내용          |
| ----------------------------------------- | ------------------ |
| `tests/test_reasoning_api.py`             | 확장 (없으면 생성) |
| `tests/test_reasoning_recommendations.py` | 기존 파일 보완     |

---

## 3. 작업 체크리스트

### 3.1 Reasoning 라우터 테스트

- [ ] `tests/test_reasoning_api.py` 확장
- [ ] `POST /api/reason` 테스트
  - [ ] 모드별 (design_explain, risk_review, next_steps, history_trace)
  - [ ] 프로젝트/라벨 필터
  - [ ] 질문 있을 때 / 없을 때

### 3.2 Recommendations API 테스트 (Phase 9-3-1 구현물)

- [ ] `GET /api/reason/recommendations/chunks` 테스트
- [ ] `GET /api/reason/recommendations/labels` 테스트
- [ ] `GET /api/reason/recommendations/questions` 테스트
- [ ] `GET /api/reason/recommendations/explore` 테스트

---

## 4. 참고 문서

- [Phase 9-2 Todo List](../phase-9-2-todo-list.md)
- [Phase 9-3-1 Reasoning 추천](../phase-9-3/tasks/task-9-3-1-reasoning-recommendation.md)
- 기존 테스트: `tests/test_reasoning_recommendations.py`
