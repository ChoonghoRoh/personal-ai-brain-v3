# Task 9-5-2: 타입 힌트 강화 (mypy)

**우선순위**: 9-5 내 2순위
**예상 작업량**: 1일
**의존성**: 없음
**상태**: ✅ 구현 완료 (pyproject.toml [tool.mypy], CI mypy 단계 추가)

**기반 문서**: [phase-9-5-todo-list.md](../phase-9-5-todo-list.md)

---

## 1. 개요

### 1.1 목표

mypy를 도입하고 backend 전역에 타입 힌트를 추가하여 정적 타입 검사 통과 및 유지보수성을 확보한다.

### 1.2 대상

| 대상     | 경로                  | 우선순위 |
| -------- | --------------------- | -------- |
| 서비스   | `backend/services/`   | 1        |
| 라우터   | `backend/routers/`    | 2        |
| 모델     | `backend/models/`     | 3        |
| 미들웨어 | `backend/middleware/` | 4        |
| 유틸     | `backend/utils/`      | 5        |

---

## 2. 작업 체크리스트

### 2.1 mypy 설정

- [ ] `pyproject.toml` 또는 `mypy.ini`에 `[tool.mypy]` 추가
- [ ] `python_version = "3.11"` (또는 프로젝트 버전)
- [ ] 검사 수준 결정: `strict = true` 목표, 단계적 적용 시 `warn_unused_ignores = true`
- [ ] `ignore_missing_imports = true` (서드파티 한정)
- [ ] 제외: `tests/`, `scripts/` 등

### 2.2 타입 힌트 추가

- [ ] 함수 파라미터 타입
- [ ] 함수 반환 타입
- [ ] 클래스 속성 타입
- [ ] 제네릭 타입 활용 (`list[str]`, `dict[str, Any]` 등)
- [ ] `Optional[X]` 또는 `X | None` (Python 3.10+)

### 2.3 품질 기준

- [ ] 모든 함수 파라미터에 타입 명시
- [ ] 모든 함수 반환값에 타입 명시
- [ ] `Any` 타입 최소화
- [ ] Union 시 `|` 연산자 사용 (Python 3.10+)
- [ ] mypy 검사 에러 0개, 경고 최소화

### 2.4 CI 통합

- [ ] GitHub Actions 워크플로우에 mypy 단계 추가 (`.github/workflows/test.yml` 등)

---

## 3. 파일 변경 계획

### 3.1 신규/수정

| 경로                         | 용도                              |
| ---------------------------- | --------------------------------- |
| `pyproject.toml`             | `[tool.mypy]` 설정 추가           |
| `.github/workflows/test.yml` | mypy 단계 추가 (이미 있다면 수정) |
| `backend/**/*.py`            | 타입 힌트 및 수정                 |

### 3.2 mypy 설정 예시 (pyproject.toml)

```toml
[tool.mypy]
python_version = "3.11"
strict = true
ignore_missing_imports = true
exclude = ["tests/", "scripts/", "e2e/"]
```

---

## 4. 참고 문서

- [Phase 9-5 Todo List](../phase-9-5-todo-list.md)
- mypy: https://mypy.readthedocs.io/
- PEP 484 – Type Hints: https://peps.python.org/pep-0484/
