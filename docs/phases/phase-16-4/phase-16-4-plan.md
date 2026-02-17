# Phase 16-4: Backend 500줄 초과 리팩토링

## 목표
Backend 500줄 초과 파일 9개를 영향도 기반으로 단계적 리팩토링하여 유지보수성 향상.
공개 API 시그니처·import 경로 유지, 기능 동일성 보장.

## 대상 파일 현황

| 파일 | 현재 줄 수 | 리팩토링 방법 |
|------|:---------:|------------|
| ai_workflow_service.py | 954 | 파이프라인 스텝 서브모듈 분리 |
| knowledge.py (router) | 792 | 핸들러 분리 |
| recommendation_service.py | 646 | 도메인별 서브모듈 분리 |
| reason_stream.py | 642 | 실행 로직 서비스 분리 |
| reason.py | 626 | 수집 로직 서비스 분리 |
| labels.py (router) | 613 | 핸들러 분리 |
| main.py | 558 | 라우터 레지스트리/이벤트 분리 |
| ai.py (router) | 543 | 핸들러 분리 |
| statistics_service.py | 503 | 도메인별 서브모듈 분리 |

## Task 구성

### Task 16-4-1 [BE] 서비스 리팩토링 (3파일)
- `ai_workflow_service.py` (954줄) → 오케스트레이터 + pipeline_steps/ 서브모듈
- `recommendation_service.py` (646줄) → 추천/LLM/탐색 분리
- `statistics_service.py` (503줄) → 도메인별 통계 분리

### Task 16-4-2 [BE] 라우터 리팩토링 (5파일)
- 각 라우터에서 비즈니스 로직을 `*_handlers.py`로 분리
- 라우터는 @router 등록 + Pydantic 모델만 유지

### Task 16-4-3 [BE] main.py 축소
- 라우터 등록 → `routers/registry.py`
- 이벤트 핸들러 → `startup.py`
- HTML 라우트 → `html_routes.py`

## 리팩토링 원칙
1. **한 번에 한 파일** — 다른 파일과의 충돌 최소화
2. **공개 API 유지** — 기존 import 경로 호환 (re-export)
3. **테스트 선행** — 리팩토링 전 기존 테스트 통과 확인
4. **기능 동일성** — 동작 변경 없음, 구조만 개선

## 의존성
- Phase 16-1~16-3 완료 (ai_workflow_service 변경사항 안정화)
