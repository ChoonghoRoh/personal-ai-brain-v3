# Task 9-5-3: API 문서화 개선

**우선순위**: 9-5 내 3순위
**예상 작업량**: 1일
**의존성**: 없음
**상태**: ✅ 구현 완료 (AI 라우터 summary/responses 추가, main.py OpenAPI 메타데이터 유지)

**기반 문서**: [phase-9-5-todo-list.md](../phase-9-5-todo-list.md)

---

## 1. 개요

### 1.1 목표

OpenAPI(Swagger)/ReDoc 문서를 보강하고, 엔드포인트별 설명·예시·에러 응답을 문서화하며, Docstring을 통일한다.

### 1.2 대상

| 구분       | 대상                                                                          |
| ---------- | ----------------------------------------------------------------------------- |
| OpenAPI    | 모든 라우터의 `summary`, `description`, `responses`                           |
| 엔드포인트 | `/api/ai/`, `/api/knowledge/`, `/api/reason/`, `/api/search/`, `/api/system/` |
| Docstring  | 모든 public 클래스·함수 (Google Style 또는 NumPy Style 통일)                  |

---

## 2. 작업 체크리스트

### 2.1 OpenAPI(Swagger) 문서 개선

- [ ] 모든 엔드포인트에 `summary` (한 줄 설명)
- [ ] 복잡한 엔드포인트에 `description` (상세 설명)
- [ ] 요청/응답 예시 추가 (`example` 또는 `examples`)
- [ ] 에러 응답 문서화 (400, 401, 404, 422, 500 등)
- [ ] 태그별 그룹핑 정리 (`tags`)

### 2.2 엔드포인트별 문서화

- [ ] `/api/ai/` – AI 관련 API
- [ ] `/api/knowledge/` – 지식 관련 API
- [ ] `/api/reason/` – Reasoning API
- [ ] `/api/search/` – 검색 API
- [ ] `/api/system/` – 시스템 API (통계, 백업, 로그 등)

### 2.3 문서화 항목 (엔드포인트당)

- [ ] Summary (한 줄)
- [ ] Description (선택, 상세 시)
- [ ] Parameters (path/query)
- [ ] Request Body (스키마·예시)
- [ ] Response (200 등 성공 스키마)
- [ ] Errors (4xx, 5xx)
- [ ] 인증 요구사항 명시 (Bearer 등)

### 2.4 Docstring

- [ ] 모든 public 클래스에 클래스 독스트링
- [ ] 모든 public 함수에 함수 독스트링 (Args, Returns, Raises)
- [ ] Google Style 또는 NumPy Style 중 하나로 통일

### 2.5 README 업데이트

- [ ] API 사용 가이드 추가 (기본 URL, 인증, 예시)
- [ ] 환경 설정 가이드 업데이트
- [ ] 개발 가이드 추가 (로컬 실행, 스키마 생성 등)

---

## 3. 파일 변경 계획

### 3.1 수정

| 경로                                          | 변경 내용                                         |
| --------------------------------------------- | ------------------------------------------------- |
| `backend/main.py`                             | OpenAPI `title`, `description`, `version`         |
| `backend/routers/**/*.py`                     | 라우트별 `summary`, `response_model`, `responses` |
| `backend/README.md` 또는 프로젝트 `README.md` | API·환경·개발 가이드                              |

### 3.2 FastAPI 데코레이터 예시

```python
@router.get(
    "/items/{id}",
    summary="단일 항목 조회",
    description="ID로 항목을 조회합니다.",
    responses={200: {"description": "성공"}, 404: {"description": "없음"}},
)
def get_item(id: str) -> Item:
    ...
```

---

## 4. 참고 문서

- [Phase 9-5 Todo List](../phase-9-5-todo-list.md)
- FastAPI Metadata: https://fastapi.tiangolo.com/tutorial/metadata/
- OpenAPI: https://swagger.io/specification/
- Google Python Style (Docstring): https://google.github.io/styleguide/pyguide.html
