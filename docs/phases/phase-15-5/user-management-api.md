# Phase 15-5-4: 회원 관리 API 및 권한 매핑

**작성일**: 2026-02-16

---

## 1. API 엔드포인트

### 1.1 셀프 서비스 API (`/api/auth/*`)

| 메서드 | 경로 | 설명 | 인증 |
|--------|------|------|------|
| POST | `/api/auth/register` | 회원 가입 | 불필요 |
| GET | `/api/auth/profile` | 내 프로필 조회 | require_auth |
| PUT | `/api/auth/profile` | 내 프로필 수정 | require_auth |
| POST | `/api/auth/change-password` | 비밀번호 변경 | require_auth |

### 1.2 Admin CRUD API (`/api/admin/users/*`)

| 메서드 | 경로 | 설명 | 인증 |
|--------|------|------|------|
| GET | `/api/admin/users` | 목록 조회 (필터·페이징) | admin_system |
| GET | `/api/admin/users/{id}` | 단건 조회 | admin_system |
| POST | `/api/admin/users` | 사용자 생성 | admin_system |
| PUT | `/api/admin/users/{id}` | 사용자 수정 (역할·상태) | admin_system |
| DELETE | `/api/admin/users/{id}` | 비활성화 (soft delete) | admin_system |
| POST | `/api/admin/users/{id}/reset-password` | 비밀번호 초기화 | admin_system |

---

## 2. 권한(Role) 매핑

### 2.1 역할 계층

```
admin_system (레벨 2) — 시스템 전체 관리
  └── admin_knowledge (레벨 1) — 지식관리 기능 관리
       └── user (레벨 0) — 기본 사용자
```

### 2.2 메뉴 접근 권한

| 메뉴 그룹 | 최소 역할 |
|-----------|-----------|
| 사용자 메뉴 (대시보드, 검색, AI 질의) | user |
| 지식 관리 (라벨, 청크, 파일관리, AI 자동화) | admin_knowledge |
| 시스템 관리 (사용자 관리) | admin_system |
| 설정 관리 (템플릿, 프리셋, RAG, 정책) | admin_system |

### 2.3 API 접근 권한

| 의존성 함수 | 최소 역할 | 적용 범위 |
|-------------|-----------|-----------|
| `require_auth` | user | 인증 필요한 모든 API |
| `require_admin_knowledge` | admin_knowledge | 지식관리 CRUD |
| `require_admin_system` | admin_system | 사용자·설정 관리 |

---

## 3. 비밀번호 정책

- 최소 8자, 최대 72자 (bcrypt 제한)
- bcrypt 해싱 (passlib CryptContext)
- 비밀번호 변경 시 현재 비밀번호 검증 필수
- Admin 비밀번호 초기화는 현재 비밀번호 검증 없음

---

## 4. users 테이블 스키마

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    display_name VARCHAR(200),
    email VARCHAR(255),
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

마이그레이션: `scripts/migrations/004_create_users_table.sql`
