# Phase 14-5-1: 사용자 검증·로그인·회원관리 요구사항 및 단계별 플랜

**작성일**: 2026-02-16
**기준 문서**: `phase-14-master-plan-guide.md` §6, `middleware/auth.py`, `routers/auth/auth.py`, `config.py`
**선행 조건**: Phase 14-1(권한·메뉴), 14-2(Swagger), 14-3(LNB) 완료

---

## 1. 현재 인증 시스템 분석

### 1.1 아키텍처 현황

```
[Client]
  ├── X-API-Key 헤더 ──────────→ [middleware/auth.py]
  ├── Authorization: Bearer JWT ─→   ├── verify_api_key()
  └── (인증 없음) ───────────────→   ├── verify_jwt_token()
                                      └── get_current_user() → UserInfo(username, auth_type, role)
```

| 구성 요소 | 현재 상태 | 비고 |
|-----------|-----------|------|
| **인증 방식** | JWT Bearer + API Key | 두 방식 공존 |
| **토큰 발급** | `POST /api/auth/token` (API Key → JWT) | API Key 사용자는 `admin_system` 고정 |
| **로그인** | `POST /api/auth/login` → **501 미구현** | username/password 방식 미구현 |
| **로그아웃** | `POST /api/auth/logout` → 메시지만 반환 | 서버 측 토큰 무효화 없음 (stateless) |
| **상태 확인** | `GET /api/auth/me`, `GET /api/auth/status` | AUTH_ENABLED 여부 + 사용자 정보 |
| **역할(Role)** | `user`, `admin_knowledge`, `admin_system` | Phase 14-1 추가. 계층형 (0→1→2) |
| **역할 저장소** | JWT claim (`sub`, `role`)만 사용 | **users 테이블 없음** |
| **AUTH_ENABLED** | `false` (개발 환경 기본) | false일 때 anonymous/admin_system 반환 |
| **토큰 갱신** | 없음 (refresh token 미구현) | JWT_EXPIRE_MINUTES=30 고정 |
| **토큰 블랙리스트** | 없음 | 로그아웃 시 서버 측 무효화 불가 |
| **비밀번호 저장** | 없음 | users 테이블 자체가 없음 |

### 1.2 config.py 인증 관련 설정

| 변수 | 기본값 | 용도 |
|------|--------|------|
| `JWT_SECRET_KEY` | `development_secret_key_change_in_production` | JWT 서명 키 |
| `JWT_ALGORITHM` | `HS256` | 서명 알고리즘 |
| `JWT_EXPIRE_MINUTES` | `30` | 액세스 토큰 만료 (분) |
| `API_SECRET_KEY` | None (환경변수) | API Key 인증용 |
| `AUTH_ENABLED` | `ENVIRONMENT == "production"` | 인증 활성화 여부 |

### 1.3 인증 제외 경로

| 유형 | 경로 |
|------|------|
| **정확 일치** | `/`, `/health`, `/docs`, `/redoc`, `/openapi.json`, `/api/auth/login`, `/api/auth/token`, `/dashboard`, `/search`, `/ask`, `/logs`, `/knowledge`, `/reason` |
| **프리픽스** | `/static`, `/document/`, `/admin/` (개발 편의) |

### 1.4 Phase 14-1 권한 체계 (구현 완료)

```
역할 계층:
  admin_system (2)   → 모든 접근 가능
  admin_knowledge (1) → 지식 관리 + 사용자 기능
  user (0)            → 사용자 기능만

의존성 함수:
  require_auth()           → 인증 필수 (모든 역할)
  require_admin_knowledge() → admin_knowledge 이상
  require_admin_system()    → admin_system만
```

---

## 2. 요구사항 정의

### 2.1 사용자 검증 (Authentication)

| ID | 요구사항 | 우선순위 | 비고 |
|----|----------|----------|------|
| AUTH-01 | username/password 기반 로그인 | P1 | 현재 501 미구현 → 실제 구현 |
| AUTH-02 | JWT 액세스 토큰 발급 (로그인 성공 시) | P1 | 기존 create_access_token() 재활용 |
| AUTH-03 | Refresh Token 발급·갱신 | P2 | 액세스 토큰 만료 시 자동 갱신 |
| AUTH-04 | 토큰 블랙리스트 (로그아웃 시 무효화) | P2 | DB 또는 Redis 기반 |
| AUTH-05 | AUTH_ENABLED=false 호환 유지 | P1 | 개발 환경에서 기존 동작 보존 |
| AUTH-06 | API Key 인증 병행 유지 | P1 | 외부 시스템 연동용 |

### 2.2 로그인/로그아웃 시나리오

#### 시나리오 A: 로그인 (username/password)

```
[사용자] → POST /api/auth/login { username, password }
           ↓
         [Backend]
           ├── users 테이블에서 username 조회
           ├── bcrypt 비밀번호 검증
           ├── 실패 → 401 Unauthorized
           └── 성공 → JWT 토큰 발급
                      ├── access_token (30분)
                      └── refresh_token (7일) [P2]
           ↓
[사용자] ← { access_token, refresh_token?, token_type, expires_in }
```

#### 시나리오 B: 토큰 갱신 (P2)

```
[사용자] → POST /api/auth/refresh { refresh_token }
           ↓
         [Backend]
           ├── refresh_token 검증 (만료·블랙리스트 확인)
           ├── 실패 → 401 (재로그인 필요)
           └── 성공 → 새 access_token 발급
           ↓
[사용자] ← { access_token, token_type, expires_in }
```

#### 시나리오 C: 로그아웃

```
[사용자] → POST /api/auth/logout (Authorization: Bearer <token>)
           ↓
         [Backend]
           ├── 현재 access_token 블랙리스트 등록 (P2)
           ├── refresh_token 무효화 (P2)
           └── 성공 응답
           ↓
[사용자] ← { message, success }
         → 클라이언트: localStorage/sessionStorage에서 토큰 삭제
```

#### 시나리오 D: 인증 비활성화 (개발 환경)

```
AUTH_ENABLED=false
  → require_auth() → UserInfo(username="anonymous", role="admin_system")
  → 모든 메뉴 노출, 모든 API 접근 허용
  → 로그인 페이지 불필요 (바로 대시보드)
```

### 2.3 회원관리 (User Management)

| ID | 요구사항 | 우선순위 | 비고 |
|----|----------|----------|------|
| USER-01 | 사용자 목록 조회 (admin_system) | P2 | 페이지네이션·검색 |
| USER-02 | 사용자 생성 (admin_system) | P2 | username, password, role 지정 |
| USER-03 | 사용자 정보 수정 (admin_system) | P2 | 역할 변경, 비활성화 |
| USER-04 | 사용자 비밀번호 초기화 (admin_system) | P3 | 관리자가 임시 비밀번호 설정 |
| USER-05 | 사용자 삭제/비활성화 (admin_system) | P2 | soft delete (is_active=false) |
| USER-06 | 내 정보 수정 (본인) | P3 | 비밀번호 변경 |
| USER-07 | 감사 로그 연동 | P2 | audit_logs.changed_by에 username 기록 |

### 2.4 비밀번호 정책

| 항목 | 정책 | 비고 |
|------|------|------|
| **최소 길이** | 8자 이상 | 필수 |
| **복잡성** | 영문 + 숫자 조합 권장 (강제 안 함) | On-Premise 특성 고려 |
| **해싱** | bcrypt (salt rounds: 12) | passlib[bcrypt] 사용 |
| **저장** | hashed_password 컬럼 (평문 절대 금지) | 필수 |
| **변경 주기** | 없음 (On-Premise) | 프로덕션 정책에 따라 추가 가능 |

---

## 3. DB 스키마 설계

### 3.1 users 테이블

```sql
CREATE TABLE users (
    id          SERIAL PRIMARY KEY,
    username    VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    display_name VARCHAR(200),
    email       VARCHAR(255),
    role        VARCHAR(50) NOT NULL DEFAULT 'user',
                -- 'user' | 'admin_knowledge' | 'admin_system'
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_username ON users (username);
CREATE INDEX idx_users_role ON users (role);
CREATE INDEX idx_users_is_active ON users (is_active);
```

### 3.2 SQLAlchemy 모델 (제안)

```python
# backend/models/user_models.py

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    display_name = Column(String(200), nullable=True)
    email = Column(String(255), nullable=True)
    role = Column(String(50), nullable=False, default="user")
    is_active = Column(Boolean, nullable=False, default=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
```

### 3.3 refresh_tokens 테이블 (P2, 선택)

```sql
CREATE TABLE refresh_tokens (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash  VARCHAR(255) UNIQUE NOT NULL,
    expires_at  TIMESTAMP WITH TIME ZONE NOT NULL,
    revoked     BOOLEAN NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens (user_id);
CREATE INDEX idx_refresh_tokens_expires_at ON refresh_tokens (expires_at);
```

### 3.4 기존 테이블과의 관계

- `audit_logs.changed_by` → `users.username` (문자열 참조, FK 미설정)
- `page_access_logs` → 향후 user_id 컬럼 추가 가능 (선택)
- 기존 `AdminSchema.role_key`는 **스키마 정의용** — RBAC 역할과 별개

---

## 4. API 설계

### 4.1 로그인/인증 API (14-5-2)

| Method | Path | 설명 | Auth | 요청 Body | 응답 |
|--------|------|------|------|-----------|------|
| POST | `/api/auth/login` | 로그인 | 없음 | `{ username, password }` | `{ access_token, token_type, expires_in }` |
| POST | `/api/auth/token` | API Key → JWT (기존 유지) | 없음 | `{ api_key }` | `{ access_token, token_type, expires_in }` |
| POST | `/api/auth/refresh` | 토큰 갱신 (P2) | 없음 | `{ refresh_token }` | `{ access_token, token_type, expires_in }` |
| POST | `/api/auth/logout` | 로그아웃 | Bearer | — | `{ message, success }` |
| GET | `/api/auth/me` | 현재 사용자 정보 | Bearer | — | `{ auth_enabled, authenticated, username, role }` |
| GET | `/api/auth/status` | 인증 시스템 상태 | 없음 | — | `{ auth_enabled, authenticated, role }` |
| PUT | `/api/auth/password` | 비밀번호 변경 (P3) | Bearer | `{ current_password, new_password }` | `{ message, success }` |

### 4.2 회원관리 API (14-5-3)

| Method | Path | 설명 | Auth | 비고 |
|--------|------|------|------|------|
| GET | `/api/admin/users` | 사용자 목록 | admin_system | 페이지네이션, 검색 |
| POST | `/api/admin/users` | 사용자 생성 | admin_system | username, password, role |
| GET | `/api/admin/users/{id}` | 사용자 상세 | admin_system | — |
| PUT | `/api/admin/users/{id}` | 사용자 수정 | admin_system | role 변경, 비활성화 |
| DELETE | `/api/admin/users/{id}` | 사용자 삭제 | admin_system | soft delete (is_active=false) |
| POST | `/api/admin/users/{id}/reset-password` | 비밀번호 초기화 | admin_system | 임시 비밀번호 설정 |

### 4.3 에러 응답 표준

| 상태 코드 | 상황 | 응답 Body |
|-----------|------|-----------|
| 401 | 토큰 없음/만료/유효하지 않음 | `{ detail: "Invalid authentication credentials" }` |
| 403 | 역할 부족 | `{ detail: "... permission required. Role '...' or higher is needed." }` |
| 404 | 사용자 없음 | `{ detail: "User not found" }` |
| 409 | username 중복 | `{ detail: "Username already exists" }` |
| 422 | 유효성 검증 실패 | `{ detail: [...] }` (FastAPI 표준) |
| 501 | 미구현 기능 | `{ detail: "... not implemented yet" }` |

---

## 5. FE 인증 플로우

### 5.1 로그인 페이지

```
[/login.html]
  ├── username 입력
  ├── password 입력
  └── "로그인" 버튼 → POST /api/auth/login
      ├── 성공 → localStorage.setItem("access_token", token)
      │          → window.location.href = "/dashboard"
      └── 실패 → 에러 메시지 표시
```

### 5.2 인증 상태 확인 (모든 페이지)

```javascript
// header-component.js 또는 auth-helper.js
async function checkAuth() {
    const res = await fetch('/api/auth/status');
    const data = await res.json();

    if (!data.auth_enabled) {
        // 인증 비활성 → 전체 메뉴 노출, 로그인 불필요
        return { role: 'admin_system', authenticated: false };
    }

    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/login';  // 로그인 페이지로 리다이렉트
        return;
    }

    // 토큰으로 /api/auth/me 호출하여 역할 확인
    const meRes = await fetch('/api/auth/me', {
        headers: { 'Authorization': `Bearer ${token}` }
    });

    if (meRes.status === 401) {
        localStorage.removeItem('access_token');
        window.location.href = '/login';
        return;
    }

    return await meRes.json();
}
```

### 5.3 API 호출 시 토큰 첨부

```javascript
// fetch wrapper
function authFetch(url, options = {}) {
    const token = localStorage.getItem('access_token');
    if (token) {
        options.headers = {
            ...options.headers,
            'Authorization': `Bearer ${token}`
        };
    }
    return fetch(url, options);
}
```

### 5.4 LNB 로그아웃 버튼

- LNB 하단에 사용자명 + "로그아웃" 버튼 추가
- 클릭 시: `POST /api/auth/logout` → localStorage 토큰 삭제 → `/login`으로 이동
- AUTH_ENABLED=false일 때: 로그아웃 버튼 숨김

### 5.5 401 자동 리다이렉트

- 모든 API 응답에서 401 감지 시 → 토큰 삭제 → `/login`으로 리다이렉트
- 선택: 토큰 만료 시 자동 갱신 시도 (refresh token, P2)

---

## 6. 보안 고려사항

### 6.1 비밀번호

| 항목 | 구현 | 라이브러리 |
|------|------|-----------|
| 해싱 | bcrypt (12 rounds) | `passlib[bcrypt]` |
| 전송 | HTTPS 필수 (프로덕션) | HSTS 설정 존재 (Phase 12-1-3) |
| 평문 저장 | 절대 금지 | — |
| 로깅 | 비밀번호 로깅 금지 | — |

### 6.2 JWT

| 항목 | 현재 | 개선 |
|------|------|------|
| 서명 키 | 개발용 고정 문자열 | 프로덕션: 환경변수 필수 (이미 경고 존재) |
| 만료 | 30분 | 유지 (적정) |
| Refresh Token | 없음 | P2에서 도입 (7일 만료) |
| 블랙리스트 | 없음 | P2에서 도입 (DB 또는 Redis) |

### 6.3 Rate Limiting

| 엔드포인트 | 제한 | 비고 |
|-----------|------|------|
| `/api/auth/login` | 5회/분 | 기존 RATE_LIMIT_AUTH_PER_MINUTE=5 활용 |
| `/api/auth/token` | 5회/분 | 동일 |
| `/api/auth/refresh` | 10회/분 | 새로 추가 |

### 6.4 초기 관리자 계정

- **시드 스크립트** 또는 **환경변수**로 초기 admin_system 계정 생성
- `ADMIN_USERNAME`, `ADMIN_PASSWORD` 환경변수 → 첫 실행 시 자동 생성
- 프로덕션에서는 즉시 비밀번호 변경 권고

---

## 7. 구현 단계별 플랜

### 7.1 단계 1 — 최소 로그인 (P1, Phase 14-5-2)

**목표**: username/password 로그인 동작, users 테이블 생성

| Task | 내용 | 산출물 |
|------|------|--------|
| 7.1.1 | `User` 모델 + Alembic 마이그레이션 | `backend/models/user_models.py`, migration |
| 7.1.2 | `POST /api/auth/login` 구현 (bcrypt 검증) | `routers/auth/auth.py` 수정 |
| 7.1.3 | 초기 admin 계정 시드 (환경변수 기반) | `init_db()` 또는 seed 스크립트 |
| 7.1.4 | `POST /api/auth/logout` 개선 (클라이언트 가이드) | — |
| 7.1.5 | pytest: 로그인 성공/실패, 토큰 발급 검증 | tests/auth/ |

### 7.2 단계 2 — 토큰 갱신·블랙리스트 (P2)

| Task | 내용 | 산출물 |
|------|------|--------|
| 7.2.1 | `refresh_tokens` 테이블 + 모델 | migration |
| 7.2.2 | `POST /api/auth/refresh` 구현 | — |
| 7.2.3 | 로그아웃 시 refresh_token 무효화 | — |
| 7.2.4 | (선택) 액세스 토큰 블랙리스트 (DB) | — |

### 7.3 단계 3 — 회원관리 CRUD (P2, Phase 14-5-3)

| Task | 내용 | 산출물 |
|------|------|--------|
| 7.3.1 | `GET/POST/PUT/DELETE /api/admin/users` 구현 | `routers/admin/users.py` |
| 7.3.2 | 사용자 목록·검색·페이지네이션 | — |
| 7.3.3 | 역할 변경·비활성화 | — |
| 7.3.4 | audit_logs.changed_by 연동 | — |
| 7.3.5 | pytest: 회원 CRUD 테스트 | tests/admin/ |

### 7.4 단계 4 — FE 연동 (P2~P3)

| Task | 내용 | 산출물 |
|------|------|--------|
| 7.4.1 | `/login.html` 로그인 페이지 | web/public/login.html |
| 7.4.2 | `authFetch()` 래퍼 + 401 리다이렉트 | js/utils/auth-helper.js |
| 7.4.3 | LNB에 사용자명·로그아웃 버튼 추가 | header-component.js 수정 |
| 7.4.4 | (선택) 회원관리 Admin 페이지 | admin/users.html |

### 7.5 단계 5 — 보안·테스트 (P3)

| Task | 내용 | 산출물 |
|------|------|--------|
| 7.5.1 | 비밀번호 변경 API | PUT /api/auth/password |
| 7.5.2 | E2E 시나리오: 로그인→메뉴→로그아웃 | e2e/ |
| 7.5.3 | 권한별 접근 E2E (401/403 검증) | e2e/ |

---

## 8. On-Premise·단일 사용자 호환

### 8.1 AUTH_ENABLED=false (현재 기본)

- **영향 없음**: 로그인 페이지 건너뜀, anonymous/admin_system으로 모든 접근 허용
- users 테이블은 존재하되 로그인 강제 안 함
- LNB에 로그아웃 버튼 미노출

### 8.2 단일 사용자 모드 (선택)

- 환경변수 `SINGLE_USER_MODE=true` → 로그인 없이 고정 역할 부여
- 초기 admin 계정 1개만 사용
- 회원관리 메뉴 숨김

### 8.3 마이그레이션 영향

- `users` 테이블 추가는 **비파괴적** (기존 테이블에 영향 없음)
- AUTH_ENABLED=false 환경에서는 users 테이블이 비어 있어도 동작
- 기존 API Key 인증은 그대로 유지

---

## 9. 회원관리 메뉴 위치

### 9.1 LNB 구조 (제안)

```
설정 관리 (settings-menu)
  ├── 역할 스키마      /admin/settings/schemas
  ├── 판단 문서 템플릿  /admin/settings/templates
  ├── 프롬프트 프리셋   /admin/settings/presets
  ├── RAG 프로필       /admin/settings/rag-profiles
  ├── 정책 관리        /admin/settings/policy-sets
  └── 사용자 관리      /admin/users            ← 추가 (admin_system 전용)
```

- **위치**: 설정 관리 그룹 하단에 추가 (기존 5개 → 6개)
- **권한**: `admin_system` 전용 (admin_knowledge는 접근 불가)
- **대안**: 별도 "시스템 관리" 그룹 분리 가능 (향후)

---

## 10. 구현 범위·일정 제안

### 10.1 Phase 14 내 구현 (권장)

| 단계 | Phase | 우선순위 | 예상 작업량 |
|------|-------|----------|-------------|
| 단계 1 (최소 로그인) | **14-5-2** | P1 | 1일 |
| 단계 3 (회원 CRUD) | **14-5-3** | P2 | 1일 |
| 단계 4 (FE 연동) | 14-5-4 또는 Phase 15 | P2 | 1일 |

### 10.2 Phase 15로 이관 (선택)

| 단계 | 이관 사유 |
|------|-----------|
| 단계 2 (토큰 갱신·블랙리스트) | 30분 만료로 당분간 충분 |
| 단계 5 (보안·E2E) | Phase 14 범위 초과 시 |

### 10.3 의존성

```
14-5-1 (본 문서, 완료)
    → 14-5-2 (로그인 API, users 테이블)
        → 14-5-3 (회원 CRUD API)
            → (선택) FE 로그인 페이지, LNB 로그아웃
```

---

## 11. 검증 체크리스트

- [ ] `POST /api/auth/login` → 유효한 username/password로 JWT 토큰 발급
- [ ] `POST /api/auth/login` → 잘못된 credentials로 401 반환
- [ ] users 테이블에 최소 1개 admin_system 계정 존재
- [ ] bcrypt 해싱 검증 (평문 비밀번호 미저장)
- [ ] AUTH_ENABLED=false 시 기존 동작 유지 (anonymous/admin_system)
- [ ] API Key 인증 기존 동작 유지
- [ ] (P2) Refresh Token 발급·갱신·무효화
- [ ] (P2) 회원 CRUD: 목록·생성·수정·삭제 동작
- [ ] (P3) FE 로그인 페이지 → 토큰 저장 → 대시보드 리다이렉트
- [ ] (P3) 401 시 자동 로그인 리다이렉트

---

**문서 상태**: Phase 14-5-1 요구사항·단계별 플랜 완성
**다음 단계**: 14-5-2 (로그인 API + users 테이블) 또는 14-6 (DB 샘플 데이터) 진행
