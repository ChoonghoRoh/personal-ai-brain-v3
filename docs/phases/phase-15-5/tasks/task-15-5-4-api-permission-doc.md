# Task 15-5-4: [DOC] 회원 관리 API/권한 매핑 정리

**우선순위**: 15-5 내 4순위
**의존성**: 15-5-2, 15-5-3 완료 후
**담당 팀원**: backend-dev
**상태**: DONE

---

## §1. 개요

Phase 15-5에서 구현한 회원 관리 기능 전체를 문서화한다. 셀프 서비스 API 4개와 Admin CRUD API 6개의 엔드포인트, 역할(Role) 계층 및 메뉴/API 접근 권한 매핑, 비밀번호 정책, users 테이블 스키마를 정리한다.

---

## §2. 파일 변경 계획

| 파일 | 변경 유형 | 설명 |
|------|-----------|------|
| `docs/phases/phase-15-5/user-management-api.md` | 신규 | 회원 관리 API + 권한 매핑 + 비밀번호 정책 + 스키마 문서 |

---

## §3. 작업 체크리스트

- [x] Section 1: API 엔드포인트 정리
  - 1.1 셀프 서비스 API (4개: register, profile GET/PUT, change-password)
  - 1.2 Admin CRUD API (6개: 목록, 단건, 생성, 수정, 삭제, 비밀번호 초기화)
  - 각 엔드포인트별 메서드, 경로, 설명, 인증 요구사항 테이블
- [x] Section 2: 권한(Role) 매핑 정리
  - 2.1 역할 계층: admin_system(L2) > admin_knowledge(L1) > user(L0)
  - 2.2 메뉴 접근 권한 매트릭스 (사용자/지식관리/시스템관리/설정관리)
  - 2.3 API 접근 권한 (require_auth, require_admin_knowledge, require_admin_system)
- [x] Section 3: 비밀번호 정책
  - 최소 8자, 최대 72자 (bcrypt 제한)
  - bcrypt 해싱 (passlib CryptContext)
  - 셀프 서비스: 현재 비밀번호 검증 필수
  - Admin: 비밀번호 초기화 시 현재 비밀번호 검증 없음
- [x] Section 4: users 테이블 스키마
  - CREATE TABLE 전문
  - 마이그레이션 파일 경로 참조

---

## §4. 참조

- `docs/phases/phase-15-5/user-management-api.md` -- 산출물 문서
- `backend/routers/auth/auth.py` -- 셀프 서비스 API 구현
- `backend/routers/admin/user_crud.py` -- Admin CRUD API 구현
- `backend/middleware/auth.py` -- 인증/권한 미들웨어 (require_auth, require_admin_system)
- `scripts/migrations/004_create_users_table.sql` -- users 테이블 DDL
