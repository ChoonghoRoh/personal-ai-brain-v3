# Phase 16-4 TODO List

## Task 16-4-1 [BE] 서비스 리팩토링
- [x] ai_workflow_service.py → 오케스트레이터 + pipeline_steps/
- [ ] recommendation_service.py → 도메인별 분리
- [ ] statistics_service.py → 도메인별 분리

## Task 16-4-2 [BE] 라우터 리팩토링
- [ ] knowledge.py → knowledge_handlers.py 분리
- [ ] labels.py → labels_handlers.py 분리
- [ ] reason.py → reason_helpers.py 분리
- [ ] reason_stream.py → stream_executor.py 분리
- [ ] ai.py → ai_handlers.py 분리

## Task 16-4-3 [BE] main.py 축소
- [ ] 라우터 등록 → routers/registry.py
- [ ] 이벤트 핸들러 → startup.py
- [ ] HTML 라우트 → html_routes.py

## G2 검증
- [ ] G2_BE Code Review

## G3 테스트
- [ ] pytest 28/28 PASS 유지
