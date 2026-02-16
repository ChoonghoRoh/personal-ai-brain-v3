---
chain_name: "phase-15-backend"
phases: ["15-4", "15-5", "15-6", "15-7", "15-8"]
current_index: 5
status: "completed"
ssot_version: "4.3"
created_at: "2026-02-16T17:30:00Z"
phase_summaries:
  "15-4": "매핑 규칙 DOC + seed --with-knowledge 옵션 + QA 체크리스트 완료"
  "15-5": "users 마이그레이션 + 셀프서비스 API(register/profile/change-pw) + Admin UI + LNB 추가"
  "15-6": "Refresh Token + 블랙리스트(Redis/메모리) + 비인증 리다이렉트 + 정책 문서"
  "15-7": "부하 테스트 스크립트 + Docker Production 오버라이드 + 운영 체크리스트"
  "15-8": "D3.js 지식 그래프(API+FE) + Redis/Qdrant 고도화 설정 + 4대 추론 모드 문서"
---

# Phase Chain: 15-4 ~ 15-8

## 실행 대상

| Phase | 내용 | 의존성 |
|-------|------|--------|
| 15-4 | DB 샘플·고도화 연동 (매핑 규칙·시드·검증) | 15-1 완료 |
| 15-5 | 회원 관리 시스템 (users CRUD, Admin UI) | 14-5 확장 |
| 15-6 | 보안·세션 (Refresh Token, 블랙리스트, 리다이렉트) | 15-5, Redis |
| 15-7 | 서비스 안정화 (부하 테스트, Docker Production) | 15-1~15-6 |
| 15-8 | (선택) D3.js 지식 그래프, Redis/Qdrant 고도화 | 15-2, 15-3 |

## 참조
- [Phase 15 Master Plan](phase-15-master-plan.md)
- [SSOT Phase Chain Protocol](../SSOT/claude/3-workflow-ssot.md#9)
