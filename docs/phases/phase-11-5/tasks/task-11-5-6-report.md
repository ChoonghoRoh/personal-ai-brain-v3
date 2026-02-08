# Task 11-5-6 실행 결과 리포트 (§2.4 공유·저장 고도화)

**실행일**: 2026-02-07  
**상태**: ✅ 완료

---

## 구현 내용

| 항목 | 구현 | 파일 |
|------|------|------|
| **공유 URL 만료** | ShareRequest expires_in_days, create_share 시 expires_at 설정 | `backend/routers/reasoning/reason_store.py` |
| **공유 URL 조회 제한** | get_shared_result 시 expires_at 검사(만료 시 410), view_count 증가 | `backend/routers/reasoning/reason_store.py` |
| **비공개 옵션** | ShareRequest is_private, ReasoningResult is_private 컬럼 | `backend/models/models.py`, `reason_store.py` |
| **의사결정 문서 검색** | GET /decisions?q= — title·summary ILIKE 필터 | `backend/routers/reasoning/reason_store.py` |
| **마이그레이션** | reasoning_results expires_at, view_count, is_private 컬럼 추가 | `scripts/db/migrate_phase11_5_6_reasoning_results.sql` |
| **프론트 연동** | share 요청 시 expires_in_days, is_private 전달 (window.__shareExpiresDays, __shareIsPrivate) | `web/public/js/reason/reason.js` |

---

## 검증

- POST /share with expires_in_days, is_private → 200, expires_at·is_private 반환.
- GET /share/{id} 만료 시 410, view_count 증가 확인.
- GET /decisions?q= 검색 동작 확인.
