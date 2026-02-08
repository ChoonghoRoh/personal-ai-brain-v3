# Phase 9-5: 코드 품질 - Todo List

**상태**: 대기 (Pending)
**우선순위**: 5
**예상 작업량**: 3.5일
**시작일**: -
**완료일**: -

---

## Phase 진행 정보

### 현재 Phase
- **Phase ID**: 9-5
- **Phase 명**: 코드 품질 (Code Quality)
- **핵심 목표**: 리팩토링, 타입 힌트 강화, API 문서화

### 이전 Phase
- **Prev Phase ID**: 9-4
- **Prev Phase 명**: 기능 확장
- **전환 조건**: 9-4 완료 (또는 병행 가능)

### 다음 Phase
- **Next Phase ID**: Phase 10
- **Next Phase 명**: Reasoning 페이지 고도화
- **전환 조건**: Phase 9 전체 완료

### Phase 우선순위 전체 현황

| 순위 | Phase | 상태 | 의존성 |
|------|-------|------|--------|
| 1 | 9-3 AI 기능 고도화 | ✅ 완료 | - |
| 2 | 9-1 보안 강화 | ⏳ 대기 | 9-3 완료 |
| 3 | 9-2 테스트 확대 | ⏳ 대기 | 9-1 부분 의존 |
| 4 | 9-4 기능 확장 | ⏳ 대기 | 독립적 |
| **5** | **9-5 코드 품질** | ⏳ 대기 | 독립적 (병행 가능) |

---

## Task 목록

### 9-5-1: 코드 리팩토링
**우선순위**: 9-5 내 1순위
**예상 작업량**: 1.5일
**의존성**: 없음 (다른 Phase와 병행 가능)

- [ ] 중복 코드 제거
  - [ ] 라우터 간 공통 로직 추출
  - [ ] 유틸리티 함수 통합
  - [ ] 중복 모델/스키마 정리

- [ ] 구조 개선
  - [ ] 서비스 레이어 일관성 확보
  - [ ] 의존성 주입 패턴 통일
  - [ ] 에러 핸들링 통일

- [ ] 불필요한 코드 정리
  - [ ] 사용하지 않는 import 제거
  - [ ] 주석 처리된 코드 정리
  - [ ] 빈 파일/디렉토리 제거

- [ ] 네이밍 개선
  - [ ] 일관된 네이밍 컨벤션 적용
  - [ ] 의미 명확한 변수/함수명

- [ ] 대상 파일 (예상)
  - [ ] `backend/routers/` - 라우터 정리
  - [ ] `backend/services/` - 서비스 정리
  - [ ] `backend/utils/` - 유틸리티 통합 (필요시 생성)

---

### 9-5-2: 타입 힌트 강화
**우선순위**: 9-5 내 2순위
**예상 작업량**: 1일
**의존성**: 없음 (다른 Phase와 병행 가능)

- [ ] mypy 설정
  - [ ] `pyproject.toml` 또는 `mypy.ini` 설정
  - [ ] 검사 수준 결정 (strict / normal)
  - [ ] 제외 파일/디렉토리 설정

- [ ] 타입 힌트 추가
  - [ ] 함수 파라미터 타입
  - [ ] 함수 반환 타입
  - [ ] 클래스 속성 타입
  - [ ] 제네릭 타입 활용

- [ ] 대상 파일 (우선순위)
  - [ ] `backend/services/` - 서비스 레이어
  - [ ] `backend/routers/` - 라우터 레이어
  - [ ] `backend/models/` - 모델 레이어

- [ ] mypy 검사 통과
  - [ ] 에러 0개 목표
  - [ ] 경고 최소화

- [ ] CI 통합
  - [ ] GitHub Actions에 mypy 검사 추가

---

### 9-5-3: API 문서화 개선
**우선순위**: 9-5 내 3순위
**예상 작업량**: 1일
**의존성**: 없음 (다른 Phase와 병행 가능)

- [ ] OpenAPI (Swagger) 문서 개선
  - [ ] 모든 엔드포인트 설명 추가
  - [ ] 요청/응답 예시 추가
  - [ ] 에러 응답 문서화
  - [ ] 태그별 그룹핑 정리

- [ ] 엔드포인트별 문서화
  - [ ] `/api/ai/` - AI 관련 API
  - [ ] `/api/knowledge/` - 지식 관련 API
  - [ ] `/api/reason/` - Reasoning API
  - [ ] `/api/search/` - 검색 API
  - [ ] `/api/system/` - 시스템 API (통계, 백업 등)

- [ ] 문서화 항목
  - [ ] Summary (한 줄 설명)
  - [ ] Description (상세 설명)
  - [ ] Parameters (쿼리/경로 파라미터)
  - [ ] Request Body (요청 본문)
  - [ ] Response (성공 응답)
  - [ ] Errors (에러 응답)

- [ ] Docstring 작성
  - [ ] 모든 클래스에 클래스 독스트링
  - [ ] 모든 함수에 함수 독스트링
  - [ ] Google Style 또는 NumPy Style 통일

- [ ] README 업데이트
  - [ ] API 사용 가이드 추가
  - [ ] 환경 설정 가이드 업데이트
  - [ ] 개발 가이드 추가

---

## 완료 기준

### Phase 9-5 완료 조건
- [ ] 9-5-1 코드 리팩토링 완료
- [ ] 9-5-2 타입 힌트 강화 완료
- [ ] 9-5-3 API 문서화 개선 완료
- [ ] mypy 검사 통과
- [ ] 기존 테스트 통과

### 품질 기준

| 항목 | 기준 |
|------|------|
| 중복 코드 | 동일 로직 2회 이상 반복 없음 |
| 타입 힌트 | mypy strict 모드 통과 |
| 문서화 | 모든 public API 문서화 |
| Docstring | 모든 클래스/함수 독스트링 |

---

## 코드 품질 체크리스트

### 리팩토링 체크리스트
- [ ] 함수 길이 50줄 이하
- [ ] 클래스 크기 300줄 이하
- [ ] 순환 복잡도 10 이하
- [ ] 중복 코드 없음
- [ ] 단일 책임 원칙 준수

### 타입 힌트 체크리스트
- [ ] 모든 함수 파라미터에 타입 명시
- [ ] 모든 함수 반환값에 타입 명시
- [ ] Optional 타입 명시적 사용
- [ ] Any 타입 최소화
- [ ] Union 대신 | 연산자 사용 (Python 3.10+)

### 문서화 체크리스트
- [ ] 모든 엔드포인트에 summary
- [ ] 복잡한 엔드포인트에 description
- [ ] 요청/응답 예시 포함
- [ ] 에러 케이스 문서화
- [ ] 인증 요구사항 명시

---

## 도구 설정

### mypy 설정 (예시)
```toml
# pyproject.toml
[tool.mypy]
python_version = "3.11"
strict = true
ignore_missing_imports = true
exclude = [
    "tests/",
    "scripts/",
]
```

### ruff 설정 (린터, 선택)
```toml
# pyproject.toml
[tool.ruff]
line-length = 120
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]
```

---

## 작업 로그

| 날짜 | Task | 작업 내용 | 상태 |
|------|------|----------|------|
| - | - | - | - |

---

## 참고 문서

### Phase 문서
- [Phase 9 Master Plan](../phase-9-master-plan.md)
- [Phase 9 Navigation](../phase-9-navigation.md)
- [작업 지시사항](../phase-9-work-instructions.md)

### 기술 참고
- mypy: https://mypy.readthedocs.io/
- ruff: https://github.com/astral-sh/ruff
- FastAPI Documentation: https://fastapi.tiangolo.com/tutorial/metadata/
- Google Python Style Guide: https://google.github.io/styleguide/pyguide.html

### 관련 파일
- `backend/` - 주요 리팩토링 대상
- `pyproject.toml` - 도구 설정
- `README.md` - 프로젝트 문서
