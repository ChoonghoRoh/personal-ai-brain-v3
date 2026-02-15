# Phase 12-1 Plan — P0 즉시 조치

**작성일**: 2026-02-15
**Phase**: 12-1
**목표**: CDN 로컬화, Base URL 통일, HTTPS/HSTS 활성화
**기준 문서**: [phase-12-master-plan.md](../phase-12-master-plan.md)

---

## 목표

4개 에이전트 교차 리뷰 P0 이슈 3건 해결:
1. 폐쇄망 호환 (CDN 제거)
2. 포트 통일성 (8000→8001)
3. 프로덕션 보안 (HSTS)

## Task 구성

| Task | 도메인 | 목표 | 변경 파일 | 예상 |
|------|--------|------|----------|------|
| 12-1-1 | [FE] | CDN → 로컬 라이브러리 | 4 HTML, libs/ 생성 | 1일 |
| 12-1-2 | [FS] | Base URL 8001 통일 | main.py, config.py, docs/ | 0.5일 |
| 12-1-3 | [INFRA] | HSTS 환경변수 활성화 | security.py, config.py, .env.example | 0.5일 |

## 구현 순서

3개 Task 모두 독립적이며 병렬 가능. 안전한 순서:
1. 12-1-3 (최소 변경, 환경변수만)
2. 12-1-2 (코드 1파일 + 문서 일괄)
3. 12-1-1 (라이브러리 다운로드 + HTML 수정)

## 핵심 발견 (Planner 분석)

- 프론트엔드 JS는 `/api/...` 상대경로 사용 → Base URL 변경 시 JS 수정 불필요
- FastAPI `/static` 마운트가 `web/public/` 서빙 → `libs/` 추가 설정 불필요
- `backend/config.py`에 `get_env_bool()` 헬퍼 존재 → HSTS 환경변수 패턴 일관성 유지

## 검증 방법

- Grep 검증: CDN URL 0건, localhost:8001 0건 (코드 파일)
- curl 검증: HSTS 헤더 조건부 확인
- 페이지 로드: Reasoning Lab, 통계, 로그, 문서 페이지 정상 동작
