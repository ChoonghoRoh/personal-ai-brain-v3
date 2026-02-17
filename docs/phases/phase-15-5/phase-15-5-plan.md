# Phase 15-5 Plan: 회원 관리 시스템 완성

**Phase**: 15-5
**작성일**: 2026-02-16
**상태**: G1 PASS

---

## 1. 목표

회원 관리 시스템을 완성하여 사용자 자기 서비스(셀프 서비스)와 관리자 전용 사용자 관리 기능을 제공한다.

- **users 테이블 마이그레이션**: 수동 SQL 스크립트로 users 테이블 생성 및 인덱스 정의
- **셀프 서비스 API**: 회원 가입(register), 프로필 조회/수정(profile), 비밀번호 변경(change-password)
- **Admin UI**: /admin/users 페이지에서 사용자 목록 조회, 역할(Role) 할당, 상태 관리

---

## 2. 범위

| 포함 | 제외 |
|------|------|
| users 테이블 DDL (CREATE TABLE IF NOT EXISTS) | Refresh Token 발급/갱신 (15-6) |
| users 인덱스 (username, role, is_active) | 토큰 블랙리스트/Redis (15-6) |
| POST /api/auth/register (회원 가입) | 비인증 리다이렉트 (15-6) |
| GET/PUT /api/auth/profile (프로필 조회/수정) | 부하 테스트/Docker Production (15-7) |
| POST /api/auth/change-password (비밀번호 변경) | SSO/LDAP 연동 |
| /admin/users 사용자 관리 페이지 (HTML + CSS + JS) | |
| LNB 시스템 관리 그룹에 "사용자 관리" 메뉴 추가 | |
| 회원 관리 API + 권한 매핑 문서화 | |

---

## 3. 설계 결정

| 결정 | 선택 | 근거 |
|------|------|------|
| 마이그레이션 방식 | 수동 SQL (`scripts/migrations/004_create_users_table.sql`) | Alembic 도입 대비 경량, `IF NOT EXISTS`로 멱등 실행 가능 |
| 비밀번호 해싱 | bcrypt via passlib (`CryptContext(schemes=["bcrypt"])`) | 업계 표준, 72자 제한 내 안전한 해싱 |
| 역할 체계 | `user` / `admin_knowledge` / `admin_system` 3단계 계층 | Phase 14-1에서 확립된 RBAC 구조 유지 |
| Admin UI 경로 | `/admin/users` | 시스템 관리 그룹 하위, `require_admin_system` 적용 |
| register 인증 | 인증 불필요 (공개 엔드포인트) | 미인증 상태에서 회원 가입 가능해야 함 |
| username 중복 처리 | DB UNIQUE 제약 + IntegrityError catch → 409 Conflict | 레이스 컨디션 방지를 위한 DB 레벨 보장 |

---

## 4. 리스크

| 리스크 | 영향 | 대응 |
|--------|------|------|
| username 중복 레이스 컨디션 | 중 | DB UNIQUE 제약 + IntegrityError 캐치로 409 반환 |
| 권한 에스컬레이션 | 고 | register 시 기본 role=user 강제, role 변경은 Admin API만 허용 |
| bcrypt 72자 제한 | 저 | Pydantic Field(max_length=72)로 입력 단계에서 검증 |
| ORM 테이블 이미 존재 | 저 | CREATE TABLE IF NOT EXISTS로 멱등 처리 |

---

## 5. 참조

- `docs/phases/phase-15-master-plan.md` -- Phase 15 전체 계획 (Section 6.1)
- `docs/phases/phase-14-5/phase-14-5-1-user-auth-plan.md` -- Phase 14-5 사용자 인증 기초 플랜
- `docs/phases/phase-15-5/user-management-api.md` -- API/권한 매핑 상세 문서
- `backend/routers/auth/auth.py` -- 셀프 서비스 API 구현체
- `backend/routers/admin/user_crud.py` -- Admin CRUD API 구현체
- `scripts/migrations/004_create_users_table.sql` -- users 테이블 마이그레이션
