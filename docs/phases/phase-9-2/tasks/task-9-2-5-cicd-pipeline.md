# Task 9-2-5: CI/CD 파이프라인

**우선순위**: 9-2 내 5순위
**예상 작업량**: 0.5일
**의존성**: 9-2-4 완료 후
**상태**: ✅ 구현 완료 (.github/workflows/test.yml 생성)

**기반 문서**: [phase-9-2-todo-list.md](../phase-9-2-todo-list.md)

---

## 1. 개요

### 1.1 목표

GitHub Actions 워크플로우를 생성하여 PR/푸시 시 자동으로 pytest를 실행하고, 커버리지 측정·리포트를 설정한다. 테스트 통과를 PR 머지 조건으로 둔다.

### 1.2 목표 산출물

| 항목        | 내용                                  |
| ----------- | ------------------------------------- |
| 워크플로우  | `.github/workflows/test.yml`          |
| 테스트 실행 | Python 환경, 의존성 설치, pytest 실행 |
| 커버리지    | pytest-cov, 임계값 70% (선택)         |
| PR 체크     | 테스트 통과 필수                      |

---

## 2. 파일 변경 계획

### 2.1 신규 생성

| 파일 경로                    | 용도                 |
| ---------------------------- | -------------------- |
| `.github/workflows/test.yml` | CI 테스트 워크플로우 |

### 2.2 수정

- `pyproject.toml` 또는 `pytest.ini`: 커버리지 설정 (필요 시)
- GitHub 저장소 설정: 브랜치 보호 규칙에서 테스트 통과 필수 (선택)

---

## 3. 작업 체크리스트

### 3.1 GitHub Actions 워크플로우 생성

- [ ] `.github/workflows/test.yml` 생성
- [ ] Python 환경 설정
- [ ] 의존성 설치
- [ ] pytest 실행

### 3.2 테스트 환경 설정

- [ ] 테스트용 Docker Compose (선택)
- [ ] 환경변수 설정 (GitHub Secrets)

### 3.3 테스트 리포트

- [ ] pytest-cov로 커버리지 측정
- [ ] 커버리지 배지 (선택)

### 3.4 PR 체크

- [ ] 테스트 통과 필수 설정
- [ ] 커버리지 임계값 설정 (70%)

---

## 4. 참고 문서

- [Phase 9-2 Todo List](../phase-9-2-todo-list.md)
- GitHub Actions: https://docs.github.com/en/actions
- pytest-cov: https://github.com/pytest-dev/pytest-cov
