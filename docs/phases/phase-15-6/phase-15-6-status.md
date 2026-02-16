# Phase 15-6 Status: 보안·세션 관리 강화

**상태**: DONE
**완료일**: 2026-02-16

## 완료 항목

| Task | 내용 | 상태 |
|------|------|------|
| 15-6-1 | [BE] Refresh Token 도입 (발급·갱신 API) | DONE |
| 15-6-2 | [BE] 로그아웃 시 토큰 블랙리스트 (Redis + 메모리 폴백) | DONE |
| 15-6-3 | [FE/BE] 비인증 접근 시 로그인 리다이렉트 | DONE |
| 15-6-4 | [DOC] 보안·세션 정책 문서화 | DONE |

## 산출물

### Backend
- `backend/middleware/auth.py` — Refresh Token 생성/검증, 블랙리스트 (Redis + 메모리)
- `backend/routers/auth/auth.py` — `/api/auth/refresh`, 로그아웃 블랙리스트, 로그인 시 refresh_token 발급

### Frontend
- `web/public/js/auth/login.js` — refresh_token 저장
- `web/public/js/components/header-component.js` — 보호 페이지 리다이렉트 강화

### Documentation
- `docs/phases/phase-15-6/security-session-policy.md` — 토큰·블랙리스트·리다이렉트 정책
