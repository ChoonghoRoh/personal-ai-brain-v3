# Task 9-2-4: 통합 테스트

**우선순위**: 9-2 내 4순위
**예상 작업량**: 1.5일
**의존성**: 9-2-1, 9-2-2, 9-2-3 완료 후
**상태**: ✅ 구현 완료 (tests/integration/ 및 3개 시나리오 파일 생성)

**기반 문서**: [phase-9-2-todo-list.md](../phase-9-2-todo-list.md)

---

## 1. 개요

### 1.1 목표

E2E 시나리오 통합 테스트를 구성하고, 문서→검색→AI 응답·지식 워크플로우·Import 매칭 시나리오를 검증한다. (선택) 9-1 완료 후 인증 통합 테스트 추가.

### 1.2 테스트 시나리오

| 시나리오                | 설명                                                 |
| ----------------------- | ---------------------------------------------------- |
| 문서→답변               | 문서 업로드 → 청크 생성 → 임베딩 → 검색 → AI 응답    |
| 지식 워크플로우         | 청크 생성 → 라벨 추가 → 관계 생성 → 승인 → Reasoning |
| Import 매칭             | Import → 자동 라벨 추천 → 적용 → 검증                |
| 인증 통합 (9-1 완료 후) | 인증된 요청 플로우, 인증 실패 플로우                 |

---

## 2. 파일 변경 계획

### 2.1 신규 생성

| 파일 경로                                      | 용도                |
| ---------------------------------------------- | ------------------- |
| `tests/integration/__init__.py`                | 패키지              |
| `tests/integration/test_document_to_answer.py` | 문서→답변 E2E       |
| `tests/integration/test_knowledge_workflow.py` | 지식 워크플로우 E2E |
| `tests/integration/test_import_matching.py`    | Import 매칭 E2E     |

### 2.2 수정

| 파일 경로           | 수정 내용                                     |
| ------------------- | --------------------------------------------- |
| `tests/conftest.py` | 통합 테스트 픽스처 (테스트 DB, 테스트 데이터) |

---

## 3. 작업 체크리스트

### 3.1 통합 테스트 구조 설정

- [ ] `tests/integration/` 디렉토리 생성
- [ ] 테스트 픽스처 (테스트 DB, 테스트 데이터)

### 3.2 E2E 시나리오 테스트

- [ ] `test_document_to_answer.py`
  - [ ] 문서 업로드 → 청크 생성 → 임베딩 → 검색 → AI 응답
- [ ] `test_knowledge_workflow.py`
  - [ ] 청크 생성 → 라벨 추가 → 관계 생성 → 승인 → Reasoning
- [ ] `test_import_matching.py`
  - [ ] Import → 자동 라벨 추천 → 적용 → 검증

### 3.3 인증 통합 테스트 (9-1 완료 후)

- [ ] 인증된 요청 플로우
- [ ] 인증 실패 플로우

---

## 4. 참고 문서

- [Phase 9-2 Todo List](../phase-9-2-todo-list.md)
- [Phase 9-1 API 인증](../phase-9-1/tasks/task-9-1-1-api-auth.md)
- pytest: https://docs.pytest.org/
