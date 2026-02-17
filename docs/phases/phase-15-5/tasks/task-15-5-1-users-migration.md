# Task 15-5-1: [DB] users 테이블 실제 생성 및 마이그레이션

**우선순위**: 15-5 내 1순위
**의존성**: 없음
**담당 팀원**: backend-dev
**상태**: DONE

---

## §1. 개요

Phase 14-5-2에서 ORM(SQLAlchemy)으로 런타임 생성되던 users 테이블을 **수동 SQL 마이그레이션 스크립트**로 공식화한다. `IF NOT EXISTS` 구문으로 멱등 실행을 보장하며, 운영 환경에서도 안전하게 적용할 수 있도록 한다.

---

## §2. 파일 변경 계획

| 파일 | 변경 유형 | 설명 |
|------|-----------|------|
| `scripts/migrations/004_create_users_table.sql` | 신규 | users 테이블 DDL + 인덱스 + 코멘트 |

---

## §3. 작업 체크리스트

- [x] `CREATE TABLE IF NOT EXISTS users` 작성 (9개 컬럼)
  - id (SERIAL PRIMARY KEY)
  - username (VARCHAR(100) NOT NULL UNIQUE)
  - hashed_password (VARCHAR(255) NOT NULL)
  - display_name (VARCHAR(200))
  - email (VARCHAR(255))
  - role (VARCHAR(50) NOT NULL DEFAULT 'user')
  - is_active (BOOLEAN NOT NULL DEFAULT TRUE)
  - last_login_at (TIMESTAMPTZ)
  - created_at, updated_at (TIMESTAMPTZ DEFAULT NOW())
- [x] 인덱스 3개 생성 (IF NOT EXISTS)
  - `idx_users_username` (username)
  - `idx_users_role` (role)
  - `idx_users_is_active` (is_active)
- [x] 테이블/컬럼 COMMENT 추가
  - 테이블: 'Phase 14-5-2/15-5-1: 사용자 인증/역할 관리'
  - role: 'user | admin_knowledge | admin_system'
  - is_active: 'soft delete용 활성 상태'
- [x] 실행 가이드 주석 추가 (docker compose exec 명령)

---

## §4. 참조

- `backend/models/user_models.py` -- SQLAlchemy User 모델 (ORM 정의)
- `docs/phases/phase-14-5/phase-14-5-1-user-auth-plan.md` -- Phase 14-5 인증 플랜
- `docs/phases/phase-15-5/user-management-api.md` -- Section 4 (스키마 정의)
