# 개발자 요구사항 (Developer Requirements)

**대상**: 백엔드/프론트엔드 개발자, DevOps
**관점**: 기술 구현, 확장성, 유지보수성

---

## 기술 스택 현황

| 영역 | 기술 | 버전 |
|------|------|------|
| Backend | FastAPI | 0.100+ |
| Database | PostgreSQL | 15+ |
| Vector DB | Qdrant | 1.7+ |
| LLM | Ollama (로컬) | - |
| Frontend | Vanilla JS | ES6+ |
| CSS | Custom | - |

---

## 요구사항 목록

### DEV-001: 모드별 분석 플러그인 구조
**우선순위**: P0 | **상태**: 계획

**설명**:
새로운 분석 모드를 쉽게 추가할 수 있는 플러그인 아키텍처

**현재 문제**:
```python
# 현재: 모드별 if-else 분기
if mode == "design_explain":
    prompt = DESIGN_TEMPLATE
elif mode == "risk_review":
    prompt = RISK_TEMPLATE
# ... 모드 추가 시 코드 수정 필요
```

**개선 방향**:
```python
# 개선: 플러그인 레지스트리
class ReasoningMode(ABC):
    @abstractmethod
    def get_prompt(self, context, question) -> str: ...
    @abstractmethod
    def postprocess(self, result) -> dict: ...

MODE_REGISTRY = {
    "design_explain": DesignExplainMode(),
    "risk_review": RiskReviewMode(),
}
```

**수용 기준**:
- [ ] 새 모드 추가 시 기존 코드 수정 없음
- [ ] 모드별 설정 파일 분리
- [ ] 모드별 테스트 독립 실행 가능

---

### DEV-002: LLM 호출 타임아웃 및 취소
**우선순위**: P0 | **상태**: 계획

**설명**:
LLM 호출의 타임아웃 설정 및 사용자 취소 기능

**구현 방안**:
```python
# Backend
async def generate_with_timeout(prompt, timeout=30):
    try:
        async with asyncio.timeout(timeout):
            return await ollama_generate(prompt)
    except asyncio.TimeoutError:
        logger.warning("LLM timeout")
        return None  # 폴백으로 전환

# 취소 처리
@app.post("/api/reason")
async def reason(request: ReasonRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid4())
    # 취소 가능한 Task 등록
    active_tasks[task_id] = asyncio.current_task()
    ...

@app.post("/api/reason/{task_id}/cancel")
async def cancel_reason(task_id: str):
    if task_id in active_tasks:
        active_tasks[task_id].cancel()
```

**수용 기준**:
- [ ] 30초 타임아웃 기본 설정
- [ ] 취소 API 호출 시 2초 이내 중단
- [ ] 취소/타임아웃 시 적절한 응답 반환

---

### DEV-003: 분석 결과 캐싱
**우선순위**: P1 | **상태**: 계획

**설명**:
동일 질문/모드/필터에 대한 결과 캐싱으로 응답 시간 단축

**캐시 키 구조**:
```python
cache_key = hash(f"{question}:{mode}:{sorted(project_ids)}:{sorted(label_ids)}")
```

**캐시 정책**:
- TTL: 1시간 (지식 변경 시 무효화)
- 최대 크기: 100개 항목
- 저장소: Redis 또는 인메모리 (LRU)

**수용 기준**:
- [ ] 캐시 히트 시 응답 시간 < 500ms
- [ ] 지식 변경 시 관련 캐시 자동 무효화
- [ ] 캐시 통계 로깅

---

### DEV-004: 프롬프트 템플릿 외부 설정화
**우선순위**: P1 | **상태**: 계획

**설명**:
LLM 프롬프트를 코드에서 분리하여 외부 파일로 관리

**파일 구조**:
```
backend/prompts/
├── design_explain.txt
├── risk_review.txt
├── next_steps.txt
├── history_trace.txt
└── no_context.txt
```

**프롬프트 파일 형식**:
```
# design_explain.txt
system: 당신은 소프트웨어 아키텍트입니다.
---
template: |
  반드시 주어진 질문에 직접 답변하세요.
  다음 컨텍스트를 바탕으로 설계 의도와 배경을 설명하세요.

  컨텍스트:
  {context}

  질문: {question}
---
variables:
  - context
  - question
```

**수용 기준**:
- [ ] 코드 배포 없이 프롬프트 수정 가능
- [ ] 프롬프트 버전 관리 (git)
- [ ] 프롬프트 유효성 검사 (필수 변수 체크)

---

### DEV-005: 분석 로그 및 성능 메트릭
**우선순위**: P2 | **상태**: 계획

**설명**:
분석 요청의 상세 로그 및 성능 지표 수집

**수집 항목**:
```python
{
    "request_id": "uuid",
    "timestamp": "2026-02-03T10:30:00Z",
    "mode": "design_explain",
    "question_length": 50,
    "context_chunks_count": 15,
    "llm_model": "eeve-korean",
    "timings": {
        "search_ms": 1200,
        "relation_ms": 800,
        "llm_ms": 12000,
        "total_ms": 14500
    },
    "result": {
        "answer_length": 500,
        "cache_hit": false
    }
}
```

**수용 기준**:
- [ ] 모든 분석 요청 로깅
- [ ] Grafana 대시보드 연동 (선택)
- [ ] 느린 요청 알림 (30초 초과)

---

### DEV-006: 테스트 커버리지 유지
**우선순위**: P1 | **상태**: 계획

**설명**:
신규 기능 추가 시 테스트 커버리지 80% 이상 유지

**테스트 구조**:
```
tests/
├── test_reasoning_modes.py      # 모드별 단위 테스트
├── test_reasoning_api.py        # API 통합 테스트
├── test_reasoning_cancel.py     # 취소 기능 테스트
├── test_reasoning_cache.py      # 캐싱 테스트
└── test_reasoning_frontend.py   # E2E 테스트 (Playwright)
```

**수용 기준**:
- [ ] PR 머지 전 테스트 통과 필수
- [ ] 커버리지 리포트 자동 생성
- [ ] 중요 경로 100% 커버

---

## 기술 제약사항

| 항목 | 제약 | 대응 방안 |
|------|------|----------|
| LLM 응답 시간 | 5-30초 | 비동기 처리, 타임아웃 |
| 동시 요청 | Ollama 5개 제한 | 큐잉, 사용자 안내 |
| 메모리 | Reranker +500MB | 싱글톤, Lazy 로딩 |
| 브라우저 | IE 미지원 | Chrome/Firefox/Safari |

---

## API 변경 계획

### 신규 API

| Method | Endpoint | 용도 |
|--------|----------|------|
| POST | `/api/reason/{id}/cancel` | 분석 취소 |
| GET | `/api/reason/history` | 분석 이력 |
| GET | `/api/reason/cache/stats` | 캐시 통계 |

### 기존 API 변경

| Endpoint | 변경 내용 |
|----------|----------|
| `POST /api/reason` | 응답에 `task_id` 추가 |
| `POST /api/reason` | 요청에 `timeout` 옵션 추가 |

---

## 코드 리뷰 체크리스트

- [ ] 타입 힌트 적용
- [ ] Docstring 작성
- [ ] 에러 핸들링 (try-except)
- [ ] 로깅 추가
- [ ] 단위 테스트 작성
- [ ] 성능 영향 검토
