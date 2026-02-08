# Phase 9-2 테스트 수행 결과 요약

**대상**: Phase 9-2 테스트 확대 (API 테스트, 통합 테스트, CI/CD)  
**기반**: [phase-9-2-todo-list.md](phase-9-2-todo-list.md), [tasks/README.md](tasks/README.md)

---

## 1. [webtest: 9-2 start] 에 대하여

**Phase 9-2는 웹 UI phase가 아닙니다.** 테스트 확대(API·통합·CI/CD) phase이므로 **웹 사용자 체크리스트(phase-9-2-web-user-checklist.md) 및 E2E 스펙(phase-9-2.spec.js)이 없습니다.**

- **webtest: 9-2 start** 실행 시: `E2E 스펙 없음` 안내가 나오는 것이 정상입니다.
- **webtest**는 9-1, 9-3처럼 **웹 체크리스트가 있는 phase**용입니다.

---

## 2. Phase 9-2 Task 수행결과 테스트 (pytest)

Phase 9-2 작업 결과 검증은 **pytest**로 진행합니다.

### 2.1 실행 방법

```bash
# 의존성 설치 (가상환경 권장)
pip install -r requirements.txt
# 또는
pip install 'python-jose[cryptography]'  # jose 미설치 시

# Phase 9-2 단위 테스트 (9-2-1, 9-2-2, 9-2-3)
pytest tests/test_ai_api.py tests/test_knowledge_api.py tests/test_reasoning_api.py -v --tb=short

# 통합 테스트 제외한 전체 (integration 폴더 제외)
pytest tests/ -v --tb=short --ignore=tests/integration

# 통합 테스트만 (DB·Qdrant 등 준비된 환경)
pytest tests/integration/ -v -m integration
```

### 2.2 테스트 파일 (Phase 9-2 대응)

| Task  | 테스트 파일                   | 비고                                                    |
| ----- | ----------------------------- | ------------------------------------------------------- |
| 9-2-1 | `tests/test_ai_api.py`        | POST /api/ask, GET /api/system/status                   |
| 9-2-2 | `tests/test_knowledge_api.py` | /api/knowledge/chunks, /api/labels, /api/relations      |
| 9-2-3 | `tests/test_reasoning_api.py` | POST /api/reason, GET /api/reason/recommendations/\*    |
| 9-2-4 | `tests/integration/*.py`      | document_to_answer, knowledge_workflow, import_matching |
| 9-2-5 | `.github/workflows/test.yml`  | CI에서 pytest 자동 실행                                 |

### 2.3 로컬 실행 시 주의

- **ModuleNotFoundError: No module named 'jose'**  
  → `pip install -r requirements.txt` 또는 `pip install 'python-jose[cryptography]'` 후 재실행.
- **DB/Qdrant 미기동**  
  → 일부 테스트는 500/404 가능. API 스펙·검증 위주로 통과 여부 확인.

---

## 3. CI (GitHub Actions)

`.github/workflows/test.yml` 에서 push/PR 시 **pytest** 실행 (Python 3.11/3.12, `tests/integration` 제외).  
의존성은 `pip install -r requirements.txt` 로 설치됩니다.

---

**작성일**: 2026-02-04
