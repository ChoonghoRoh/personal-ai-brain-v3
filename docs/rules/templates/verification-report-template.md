# Phase X-Y Verification Report

**Phase ID**: `X-Y` (예: 11-1, 11-2)
**Report Type**: Verification (검증)
**Agent**: [Tester]
**Date**: YYYY-MM-DD
**Status**: [DRAFT | IN_REVIEW | FINAL]

---

## 1. Verification Summary

**검증 대상**: Phase X-Y 전체 Task 및 산출물

**최종 판정**: `[PASS | FAIL | PARTIAL]`

**판정 기준**:

- `PASS`: 모든 필수 검증 항목 통과, Blocker 없음
- `FAIL`: 1개 이상의 Critical Blocker 존재, 다음 단계 진행 불가
- `PARTIAL`: Low/Medium 이슈만 존재, 조건부 진행 가능 (Technical Debt 등록)

---

## 2. Syntax Check (구문 검사)

### 2.1 Backend (Python)

| 파일 경로                  | 검사 도구         | 결과          | 비고                    |
| -------------------------- | ----------------- | ------------- | ----------------------- |
| `backend/main.py`          | pylint/flake8     | `[Pass/Fail]` | 오류 메시지 (있을 경우) |
| `backend/models/models.py` | mypy (type check) | `[Pass/Fail]` |                         |

**요약**:

- [ ] 모든 Python 파일 Syntax Error 없음
- [ ] Type hint 정합성 확인 완료

### 2.2 Frontend (JavaScript/HTML)

| 파일 경로               | 검사 도구 | 결과          | 비고 |
| ----------------------- | --------- | ------------- | ---- |
| `web/src/app.js`        | ESLint    | `[Pass/Fail]` |      |
| `web/public/index.html` | HTMLHint  | `[Pass/Fail]` |      |

**요약**:

- [ ] 모든 JS 파일 Syntax Error 없음
- [ ] HTML 구조 validation 통과

### 2.3 Database (SQL)

| 파일 경로                             | 검사 도구      | 결과          | 비고 |
| ------------------------------------- | -------------- | ------------- | ---- |
| `backend/models/schema_migration.sql` | psql --dry-run | `[Pass/Fail]` |      |

**요약**:

- [ ] Migration SQL 구문 오류 없음
- [ ] 스키마 충돌 없음

---

## 3. Logic Check (로직 검증)

### 3.1 Task 완료 기준 충족 여부

**참조**: [ai-rule-task-inspection.md](../ai/references/ai-rule-task-inspection.md) §1-2

| Task ID | Task 제목   | Done Definition 충족 | 비고             |
| ------- | ----------- | -------------------- | ---------------- |
| X-Y-1   | [Task 제목] | `[Yes/No]`           | 미충족 항목: ... |
| X-Y-2   | [Task 제목] | `[Yes/No]`           |                  |
| X-Y-3   | [Task 제목] | `[Yes/No]`           |                  |

**요약**:

- [ ] 모든 Task Done Definition 충족
- [ ] Phase Plan의 완료 기준(Exit Criteria) 충족

### 3.2 API 엔드포인트 검증 (Backend)

**대상**: 이번 Phase에서 추가/수정된 API

| Method | Endpoint           | 기대 결과   | 실제 결과 | Status        |
| ------ | ------------------ | ----------- | --------- | ------------- |
| GET    | `/api/v1/resource` | 200 OK      | 200 OK    | `[Pass/Fail]` |
| POST   | `/api/v1/resource` | 201 Created | 500 Error | `[Pass/Fail]` |

**요약**:

- [ ] 모든 API 정상 응답 (2xx)
- [ ] 에러 핸들링 적절

### 3.3 UI 동작 검증 (Frontend)

**대상**: 이번 Phase에서 추가/수정된 UI 페이지

| 페이지             | 동작           | 기대 결과     | 실제 결과   | Status        |
| ------------------ | -------------- | ------------- | ----------- | ------------- |
| `/admin/settings`  | 페이지 로드    | 데이터 렌더링 | 렌더링 성공 | `[Pass/Fail]` |
| `/admin/templates` | CRUD 버튼 클릭 | 모달 표시     | 모달 미표시 | `[Pass/Fail]` |

**요약**:

- [ ] 모든 UI 페이지 정상 로드
- [ ] 사용자 인터랙션 정상 작동

### 3.4 DB 데이터 정합성 (Database)

**대상**: 이번 Phase에서 추가/수정된 테이블

| 테이블명    | 검증 항목          | 기대값 | 실제값 | Status        |
| ----------- | ------------------ | ------ | ------ | ------------- |
| `schemas`   | 레코드 존재        | 10개   | 10개   | `[Pass/Fail]` |
| `templates` | Foreign Key 정합성 | 일치   | 일치   | `[Pass/Fail]` |

**요약**:

- [ ] 테이블 생성 확인
- [ ] 데이터 무결성 확인 (FK, Constraint)

---

## 4. Edge Case Check (경계 조건 검증)

### 4.1 입력 검증 (Input Validation)

| 시나리오                | 입력값    | 기대 동작             | 실제 동작       | Status        |
| ----------------------- | --------- | --------------------- | --------------- | ------------- |
| API: 빈 문자열 입력     | `""`      | 400 Bad Request       | 400 Bad Request | `[Pass/Fail]` |
| API: 초대형 데이터 입력 | 10MB JSON | 413 Payload Too Large | 500 Error       | `[Pass/Fail]` |
| UI: 필수 필드 누락      | null      | 에러 메시지 표시      | 정상 제출       | `[Pass/Fail]` |

**요약**:

- [ ] 입력 검증 로직 정상 작동
- [ ] 에러 메시지 사용자 친화적

### 4.2 권한 검증 (Authorization)

| 시나리오          | 사용자      | 기대 동작        | 실제 동작        | Status        |
| ----------------- | ----------- | ---------------- | ---------------- | ------------- |
| Admin 페이지 접근 | 비로그인    | 401 Unauthorized | 401 Unauthorized | `[Pass/Fail]` |
| 리소스 삭제       | 일반 사용자 | 403 Forbidden    | 403 Forbidden    | `[Pass/Fail]` |

**요약**:

- [ ] 권한 검증 로직 정상 작동

### 4.3 동시성 검증 (Concurrency)

| 시나리오       | 조건        | 기대 동작           | 실제 동작           | Status        |
| -------------- | ----------- | ------------------- | ------------------- | ------------- |
| 동시 POST 요청 | 10개 동시   | Race condition 없음 | Race condition 발생 | `[Pass/Fail]` |
| DB Lock        | 동시 UPDATE | Deadlock 방지       | Deadlock 발생       | `[Pass/Fail]` |

**요약**:

- [ ] 동시성 이슈 없음 (해당 Phase에서 요구하는 경우만)

---

## 5. 코드 오류 (Code Errors)

**발견된 오류 리스트**:

### 5.1 Critical (즉시 수정 필요)

| 오류 ID | 파일 경로                  | 라인 | 오류 메시지                                               | 재현 조건                        |
| ------- | -------------------------- | ---- | --------------------------------------------------------- | -------------------------------- |
| ERR-001 | `backend/routers/admin.py` | 45   | `AttributeError: 'NoneType' object has no attribute 'id'` | GET /api/admin/templates 호출 시 |

**Stack Trace**:

```
Traceback (most recent call last):
  File "backend/routers/admin.py", line 45, in get_templates
    return template.id
AttributeError: 'NoneType' object has no attribute 'id'
```

### 5.2 High (다음 단계 진행 전 수정 권장)

| 오류 ID | 파일 경로        | 라인 | 오류 메시지                                           | 재현 조건        |
| ------- | ---------------- | ---- | ----------------------------------------------------- | ---------------- |
| ERR-002 | `web/src/api.js` | 102  | `TypeError: Cannot read property 'data' of undefined` | API 호출 실패 시 |

### 5.3 Low (Technical Debt 등록 가능)

| 오류 ID | 파일 경로                  | 라인 | 오류 메시지               | 재현 조건 |
| ------- | -------------------------- | ---- | ------------------------- | --------- |
| ERR-003 | `backend/utils/helpers.py` | 78   | `DeprecationWarning: ...` | -         |

**요약**:

- Critical: X건
- High: X건
- Low: X건

---

## 6. 미해결 이슈 (Unresolved Issues)

| 이슈 ID   | 제목        | 설명          | 우선순위                     | 영향 범위             | 담당 Agent |
| --------- | ----------- | ------------- | ---------------------------- | --------------------- | ---------- |
| ISSUE-001 | [이슈 제목] | [구체적 설명] | `[Critical/High/Medium/Low]` | [Backend/Frontend/DB] | [Builder]  |

**Blocker 이슈** (다음 단계 진행 불가):

- [ ] ISSUE-XXX: [제목]

**Non-Blocker 이슈** (Technical Debt 등록):

- [ ] ISSUE-YYY: [제목]

---

## 7. 해결된 이슈 (Resolved Issues)

| 이슈 ID    | 제목        | 해결 방법        | 커밋/PR             | 해결 Agent |
| ---------- | ----------- | ---------------- | ------------------- | ---------- |
| ISSUE-R001 | [이슈 제목] | [해결 방법 요약] | #123, commit abc123 | [Builder]  |

---

## 8. 테스트 커버리지 (Test Coverage)

**참조**: [integration-test-guide.md](../../devtest/integration-test-guide.md)

### 8.1 Integration Test 결과

| 시나리오 ID  | 제목            | 실행 결과     | 비고 |
| ------------ | --------------- | ------------- | ---- |
| SCENARIO-001 | [시나리오 제목] | `[Pass/Fail]` |      |
| SCENARIO-002 | [시나리오 제목] | `[Pass/Fail]` |      |

**요약**:

- 총 시나리오: X개
- Pass: X개
- Fail: X개
- Pass Rate: XX%

### 8.2 E2E Test 결과

**E2E Spec 파일**: `e2e/phase-X-Y.spec.js`

| 테스트 케이스 | 실행 결과     | 비고 |
| ------------- | ------------- | ---- |
| [테스트명]    | `[Pass/Fail]` |      |

**요약**:

- 총 테스트: X개
- Pass: X개
- Fail: X개

### 8.3 Web Test 결과

**참조**: `docs/webtest/phase-X-Y/phase-X-Y-webtest-execution-report.md`

**요약**:

- [ ] 웹 테스트 체크리스트 완료
- [ ] 사용자 시나리오 검증 완료

---

## 9. 회귀 테스트 (Regression Test)

**대상**: 이전 Phase 기능 유지 여부

| 기능          | Phase     | 검증 방법 | 결과          | 비고 |
| ------------- | --------- | --------- | ------------- | ---- |
| [기존 기능명] | Phase X-Y | E2E Test  | `[Pass/Fail]` |      |

**요약**:

- [ ] 모든 회귀 테스트 통과
- [ ] 기존 기능 정상 작동 확인

---

## 10. 최종 판정 (Final Decision)

### 10.1 판정 결과

**최종 판정**: `[PASS | FAIL | PARTIAL]`

**판정 근거**:

- [ ] Syntax Check: [Pass/Fail]
- [ ] Logic Check: [Pass/Fail]
- [ ] Edge Case Check: [Pass/Fail]
- [ ] 코드 오류: Critical X건, High X건, Low X건
- [ ] Blocker 이슈: X건
- [ ] 테스트 Pass Rate: XX%

### 10.2 다음 단계 (Next Action)

**IF PASS**:

- ✅ → [5. 통합 테스트 단계 실행](../ai-execution-workflow.md#5-통합-테스트-단계-실행)으로 진행
- ✅ Status 파일 업데이트: `current_step = "5. 통합 테스트"`
- ✅ Blockers 배열 비우기: `blockers = []`

**IF FAIL**:

- ❌ → [3. Task 생성 및 개발 단계](../ai-execution-workflow.md#3-task-생성-및-개발-단계)로 Rollback
- ❌ Status 파일 업데이트:
  - `current_step = "3. 개발 단계 (Fix)"`
  - `blockers = ["Verification failed: {구체적 이유}"]`
- ❌ Fix Task 생성: `task-X-Y-Z-fix.md`

**IF PARTIAL**:

- ⚠️ → 조건부 진행 (Orchestrator 판단 필요)
- ⚠️ Technical Debt 등록: [ISSUE-XXX, ISSUE-YYY]
- ⚠️ 다음 단계 진행 시 Known Issues 명시

### 10.3 Orchestrator 지시사항

**Orchestrator Agent에게**:

- 본 리포트의 "최종 판정" 필드를 읽고 다음 단계 결정
- `PASS`인 경우에만 다음 단계로 진행
- `FAIL`인 경우 Builder Agent에게 Fix Task 배정
- `PARTIAL`인 경우 PM 역할로 진행 여부 결정 (위험도 평가)

---

## 11. 서명 (Sign-off)

**작성자**: [Tester Agent]
**검토자**: [Orchestrator Agent]
**승인자**: [PM/Orchestrator]

**검증 완료 일시**: YYYY-MM-DD HH:MM:SS

---

## 부록: 체크리스트 (Quick Reference)

### Phase Verification 필수 항목

- [ ] 1. 모든 Task 문서 존재 (`task-X-Y-Z.md`)
- [ ] 2. 모든 Task Done Definition 충족
- [ ] 3. Syntax Check 모두 통과 (Backend/Frontend/DB)
- [ ] 4. API 엔드포인트 정상 응답
- [ ] 5. UI 페이지 정상 로드 및 동작
- [ ] 6. DB 데이터 정합성 확인
- [ ] 7. Edge Case 검증 완료
- [ ] 8. Critical/High 오류 0건
- [ ] 9. Blocker 이슈 0건
- [ ] 10. 통합 테스트 Pass Rate ≥ 90%
- [ ] 11. E2E Test 존재 및 실행 완료
- [ ] 12. 회귀 테스트 통과

**최소 통과 기준**: 1~9번 항목 모두 충족 + 10~12번 중 2개 이상 충족
