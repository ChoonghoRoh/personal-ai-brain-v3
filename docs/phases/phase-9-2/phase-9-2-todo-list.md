# Phase 9-2: 테스트 확대 - Todo List

**상태**: 대기 (Pending)
**우선순위**: 3
**예상 작업량**: 4.5일
**시작일**: -
**완료일**: -

---

## Phase 진행 정보

### 현재 Phase
- **Phase ID**: 9-2
- **Phase 명**: 테스트 확대 (Test Expansion)
- **핵심 목표**: API 테스트, 통합 테스트, CI/CD 파이프라인

### 이전 Phase
- **Prev Phase ID**: 9-1
- **Prev Phase 명**: 보안 강화
- **전환 조건**: 9-1 전체 Task 완료

### 다음 Phase
- **Next Phase ID**: 9-4
- **Next Phase 명**: 기능 확장
- **전환 조건**: 9-2 전체 Task 완료 (9-4와 병행 가능)

### Phase 우선순위 전체 현황

| 순위 | Phase | 상태 | 의존성 |
|------|-------|------|--------|
| 1 | 9-3 AI 기능 고도화 | ✅ 완료 | - |
| 2 | 9-1 보안 강화 | ⏳ 대기 | 9-3 완료 |
| **3** | **9-2 테스트 확대** | ⏳ 대기 | 9-1 부분 의존 |
| 4 | 9-4 기능 확장 | ⏳ 대기 | - |
| 5 | 9-5 코드 품질 | ⏳ 대기 | - |

---

## Task 목록

### 9-2-1: AI API 테스트
**우선순위**: 9-2 내 1순위
**예상 작업량**: 1일
**의존성**: 없음

- [ ] AI 라우터 테스트
  - [ ] `tests/test_ai_api.py` 생성
  - [ ] `POST /api/ai/ask` 테스트
    - [ ] 정상 질문 응답
    - [ ] 빈 질문 에러
    - [ ] 컨텍스트 없을 때 처리
  - [ ] `GET /api/ai/models` 테스트 (Ollama 모델 목록)

- [ ] RAG 파이프라인 테스트 (Phase 9-3 구현물)
  - [ ] Hybrid Search 테스트
  - [ ] Reranking 테스트
  - [ ] Context Manager 테스트
  - [ ] Multi-hop RAG 테스트

- [ ] 엣지 케이스 테스트
  - [ ] LLM 타임아웃 시 폴백
  - [ ] Qdrant 연결 실패 시 처리

---

### 9-2-2: Knowledge API 테스트
**우선순위**: 9-2 내 2순위
**예상 작업량**: 1일
**의존성**: 없음

- [ ] Knowledge 라우터 테스트
  - [ ] `tests/test_knowledge_api.py` 생성
  - [ ] 청크 CRUD 테스트
    - [ ] `POST /api/knowledge/chunks` 생성
    - [ ] `GET /api/knowledge/chunks/{id}` 조회
    - [ ] `PUT /api/knowledge/chunks/{id}` 수정
    - [ ] `DELETE /api/knowledge/chunks/{id}` 삭제

- [ ] 라벨 API 테스트
  - [ ] `POST /api/knowledge/labels` 라벨 생성
  - [ ] `GET /api/knowledge/labels` 라벨 목록
  - [ ] 청크-라벨 연결 테스트

- [ ] 관계 API 테스트
  - [ ] `POST /api/knowledge/relations` 관계 생성
  - [ ] `GET /api/knowledge/relations` 관계 목록
  - [ ] 순환 관계 방지 테스트

- [ ] 자동 매칭 테스트 (Phase 9-3-2 구현물)
  - [ ] 청크 생성 시 라벨 추천 테스트
  - [ ] 승인 시 관계 추천 테스트

---

### 9-2-3: Reasoning API 테스트
**우선순위**: 9-2 내 3순위
**예상 작업량**: 0.5일
**의존성**: 없음

- [ ] Reasoning 라우터 테스트
  - [ ] `tests/test_reasoning_api.py` 확장
  - [ ] `POST /api/reason` 테스트
    - [ ] 모드별 (design_explain, risk_review, next_steps, history_trace)
    - [ ] 프로젝트/라벨 필터
    - [ ] 질문 있을 때 / 없을 때

- [ ] Recommendations API 테스트 (Phase 9-3-1 구현물)
  - [ ] `GET /api/reason/recommendations/chunks` 테스트
  - [ ] `GET /api/reason/recommendations/labels` 테스트
  - [ ] `GET /api/reason/recommendations/questions` 테스트
  - [ ] `GET /api/reason/recommendations/explore` 테스트

---

### 9-2-4: 통합 테스트
**우선순위**: 9-2 내 4순위
**예상 작업량**: 1.5일
**의존성**: 9-2-1, 9-2-2, 9-2-3 완료 후

- [ ] 통합 테스트 구조 설정
  - [ ] `tests/integration/` 디렉토리 생성
  - [ ] 테스트 픽스처 (테스트 DB, 테스트 데이터)

- [ ] E2E 시나리오 테스트
  - [ ] `test_document_to_answer.py`
    - [ ] 문서 업로드 → 청크 생성 → 임베딩 → 검색 → AI 응답
  - [ ] `test_knowledge_workflow.py`
    - [ ] 청크 생성 → 라벨 추가 → 관계 생성 → 승인 → Reasoning
  - [ ] `test_import_matching.py`
    - [ ] Import → 자동 라벨 추천 → 적용 → 검증

- [ ] 인증 통합 테스트 (9-1 완료 후)
  - [ ] 인증된 요청 플로우
  - [ ] 인증 실패 플로우

---

### 9-2-5: CI/CD 파이프라인
**우선순위**: 9-2 내 5순위
**예상 작업량**: 0.5일
**의존성**: 9-2-4 완료 후

- [ ] GitHub Actions 워크플로우 생성
  - [ ] `.github/workflows/test.yml` 생성
  - [ ] Python 환경 설정
  - [ ] 의존성 설치
  - [ ] pytest 실행

- [ ] 테스트 환경 설정
  - [ ] 테스트용 Docker Compose (선택)
  - [ ] 환경변수 설정 (GitHub Secrets)

- [ ] 테스트 리포트
  - [ ] pytest-cov로 커버리지 측정
  - [ ] 커버리지 배지 (선택)

- [ ] PR 체크
  - [ ] 테스트 통과 필수 설정
  - [ ] 커버리지 임계값 설정 (70%)

---

## 완료 기준

### Phase 9-2 완료 조건
- [ ] 9-2-1 AI API 테스트 완료
- [ ] 9-2-2 Knowledge API 테스트 완료
- [ ] 9-2-3 Reasoning API 테스트 완료
- [ ] 9-2-4 통합 테스트 완료
- [ ] 9-2-5 CI/CD 파이프라인 완료
- [ ] 테스트 커버리지 70% 이상

### 품질 기준

| 항목 | 기준 |
|------|------|
| 단위 테스트 | 주요 API 100% 커버 |
| 통합 테스트 | 핵심 시나리오 3개 이상 |
| 커버리지 | 70% 이상 |
| CI/CD | PR 시 자동 실행 |

---

## 테스트 파일 구조 (예상)

```
tests/
├── conftest.py                    # 공통 픽스처
├── test_ai_api.py                 # AI API 테스트
├── test_knowledge_api.py          # Knowledge API 테스트
├── test_reasoning_api.py          # Reasoning API 테스트 (기존 확장)
├── test_reasoning_recommendations.py  # 추천 API 테스트 (기존)
├── test_hybrid_search.py          # Hybrid Search 테스트 (기존)
├── test_structure_matching.py     # 자동 매칭 테스트 (기존)
└── integration/
    ├── __init__.py
    ├── test_document_to_answer.py
    ├── test_knowledge_workflow.py
    └── test_import_matching.py
```

---

## 작업 로그

| 날짜 | Task | 작업 내용 | 상태 |
|------|------|----------|------|
| - | - | - | - |

---

## 참고 문서

### Phase 문서
- [Phase 9 Master Plan](../phase-9-master-plan.md)
- [Phase 9 Navigation](../phase-9-navigation.md)
- [작업 지시사항](../phase-9-work-instructions.md)

### 기술 참고
- pytest: https://docs.pytest.org/
- pytest-asyncio: https://github.com/pytest-dev/pytest-asyncio
- pytest-cov: https://github.com/pytest-dev/pytest-cov
- GitHub Actions: https://docs.github.com/en/actions

### 기존 테스트 파일
- `tests/test_hybrid_search.py`
- `tests/test_reasoning_recommendations.py`
- `tests/test_structure_matching.py`
