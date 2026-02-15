# Task 12-3-3: [TEST] pytest-cov CI 통합

**우선순위**: 12-3 내 4순위
**예상 작업량**: 소 (설정 파일 3개 수정)
**의존성**: 없음
**상태**: ✅ 완료

**기반 문서**: `phase-12-3-todo-list.md`
**Plan**: `phase-12-3-plan.md`
**작업 순서**: `phase-12-navigation.md`

---

## 1. 개요

### 1.1 목표

pytest-cov를 프로젝트에 통합하여 로컬과 CI 모두에서 코드 커버리지를 측정할 수 있도록 한다. GitHub Actions에서 커버리지 리포트를 아티팩트로 저장한다.

---

## 2. 파일 변경 계획

### 2.2 수정

| 파일 | 변경 내용 |
|------|----------|
| `requirements.txt` | `pytest-cov>=4.0.0` 추가 |
| `pytest.ini` | addopts에 `--cov=backend --cov-report=term-missing` 추가 |
| `.github/workflows/test.yml` | 커버리지 XML 생성 + 아티팩트 업로드 |

---

## 3. 작업 체크리스트

- [x] `requirements.txt`에 `pytest-cov>=4.0.0` 추가
- [x] `pytest.ini` addopts에 커버리지 옵션 추가
- [x] `test.yml` pytest 명령에 `--cov-report=xml:coverage.xml` 추가
- [x] `test.yml` actions/upload-artifact@v4로 커버리지 리포트 업로드 (30일 보존)

---

## 4. 참조

- Phase 12 Master Plan §12-3-3
- 1-project-ssot.md §5.2: "커버리지 변경 파일 기준 80% 이상"
