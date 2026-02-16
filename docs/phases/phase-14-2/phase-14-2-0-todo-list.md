# Phase 14-2: API 문서(Swagger) 고도화 — Todo List

**상태**: ✅ 완료
**우선순위**: Phase 14 내 2순위 (P1, 14-1과 병렬 가능)
**예상 작업량**: 1일
**시작일**: 2026-02-16
**완료일**: 2026-02-16

**기준 문서**: `phase-14-master-plan-guide.md` §4, §8.3

---

## Task 목록

### 14-2-1: [BE] OpenAPI 태그 그룹화 + 엔드포인트 설명 보강 ✅

**우선순위**: 1순위
**상태**: ✅ 완료

- [x] main.py에 openapi_tags 배열 정의 (38개 태그, 메뉴 구조 반영)
- [x] 모든 라우터 tags 정규화 (PascalCase 통일, 28개 파일)
- [x] admin/__init__.py 하위 태그 정규화 (7개 서브라우터)
- [x] backup.py legacy 태그 통합 ("Backup (Legacy)" → "Backup")

### 14-2-2: [BE] securitySchemes 정의 + 경로별 security ✅

**우선순위**: 2순위
**상태**: ✅ 완료

- [x] custom_openapi() 함수에 securitySchemes 추가 (BearerToken JWT, APIKey X-API-Key)
- [x] 전역 security 기본 적용
- [x] 인증 제외 경로 security=[] 처리 (auth/token, auth/login, health/*)

### 14-2-3: [TEST] Swagger 문서 검증 ✅

**우선순위**: 3순위
**상태**: ✅ 완료

- [x] /openapi.json 스키마 검증 — securitySchemes 존재, 38개 tags 정상 순서
- [x] 인증 제외 경로 5개 확인 (POST /api/auth/token, POST /api/auth/login, GET /health, GET /health/live, GET /health/ready)
- [x] 기존 pytest 79개 회귀 확인 — 회귀 없음 (5 failed, 3 errors 기존 동일)
