# Task 15-5-2: [BE] 회원 가입/프로필 수정/비밀번호 변경 CRUD API

**우선순위**: 15-5 내 2순위
**의존성**: 15-5-1 완료 후
**담당 팀원**: backend-dev
**상태**: DONE

---

## §1. 개요

사용자가 스스로 계정을 관리할 수 있는 셀프 서비스 API 4개를 구현한다. 회원 가입은 인증 없이 접근 가능하며, 프로필 조회/수정 및 비밀번호 변경은 `require_auth` 인증을 요구한다. 비밀번호는 bcrypt로 해싱하고, username 중복은 DB UNIQUE 제약으로 방지한다.

---

## §2. 파일 변경 계획

| 파일 | 변경 유형 | 설명 |
|------|-----------|------|
| `backend/routers/auth/auth.py` | 수정 | 셀프 서비스 API 4개 추가 (register, profile GET/PUT, change-password) |
| `backend/middleware/auth.py` | 수정 | `/api/auth/register` 경로를 인증 제외 목록에 추가 |

---

## §3. 작업 체크리스트

- [x] Pydantic 모델 정의
  - RegisterRequest (username, password, display_name, email)
  - ProfileResponse (id, username, display_name, email, role, is_active, last_login_at, created_at)
  - ProfileUpdateRequest (display_name, email)
  - ChangePasswordRequest (current_password, new_password)
- [x] POST `/api/auth/register` 구현
  - 인증 불필요 (공개 엔드포인트)
  - bcrypt 해싱 (passlib CryptContext)
  - 기본 role=user 강제
  - IntegrityError catch -> 409 Conflict
  - 응답: ProfileResponse (201 Created)
- [x] GET `/api/auth/profile` 구현
  - Depends(require_auth) 적용
  - users 테이블에서 현재 사용자 조회
  - 응답: ProfileResponse
- [x] PUT `/api/auth/profile` 구현
  - Depends(require_auth) 적용
  - display_name, email 수정
  - updated_at 갱신
  - 응답: ProfileResponse
- [x] POST `/api/auth/change-password` 구현
  - Depends(require_auth) 적용
  - 현재 비밀번호 검증 (pwd_context.verify)
  - 새 비밀번호 bcrypt 해싱
  - 실패 시 400 Bad Request
  - 응답: MessageResponse
- [x] middleware/auth.py에 register 경로 인증 제외 추가

---

## §4. 참조

- `backend/routers/auth/auth.py` -- 구현 파일 (Phase 15-5-2 섹션)
- `backend/middleware/auth.py` -- 인증 미들웨어
- `backend/models/user_models.py` -- User ORM 모델
- `docs/phases/phase-15-5/user-management-api.md` -- Section 1.1 (셀프 서비스 API 명세)
- `docs/phases/phase-15-5/user-management-api.md` -- Section 3 (비밀번호 정책)
