# Tester 작업지시 가이드

**버전**: 1.0 (3rd iteration)  
**대상**: tester 팀원  
**용도**: 테스트 실행 프로세스 상세 지침

---

## 테스트 실행 프로세스

### 1. Team Lead로부터 테스트 요청 수신

```
[1] Team Lead: SendMessage → tester에게 테스트 요청
    "Task X-Y-N 테스트 요청
     도메인: [BE]
     변경 파일:
       - backend/routers/admin/admin_crud.py
       - tests/test_admin_crud.py
     명령: pytest tests/test_admin_crud.py -v --cov=backend.routers.admin
     테스트 후 SendMessage로 결과 보고"
  │
  ▼
[2] tester: Bash 명령 실행
    pytest tests/test_admin_crud.py -v --cov=backend.routers.admin
  │
  ▼
[3] tester: 테스트 결과 분석
    Total: 4
    Passed: 4
    Failed: 0
    Coverage: 95% (backend.routers.admin.admin_crud)
  │
  ▼
[4] tester: 판정 결정
    모든 테스트 PASS, 커버리지 ≥80% → 판정: PASS
  │
  ▼
[5] tester: SendMessage → Team Lead에게 결과 보고
    "Task X-Y-N 테스트 결과: PASS
     Total: 4
     Passed: 4
     Failed: 0
     Coverage: 95% (backend.routers.admin.admin_crud)
     테스트 통과"
```

### 2. 테스트 FAIL 시

```
[1] tester: Bash 명령 실행 → 테스트 실패 발견
  │
  ▼
[2] tester: 실패 테스트 상세 분석
    Failed Tests:
      - test_admin_api::test_create_template → AssertionError
  │
  ▼
[3] tester: SendMessage → Team Lead에게 결과 보고
    "Task X-Y-N 테스트 결과: FAIL
     Total: 4
     Passed: 3
     Failed: 1
     Failed Tests:
       - test_admin_api::test_create_template → AssertionError: Expected 201, got 400
     수정 필요"
```

---

## 테스트 명령 예시

### 백엔드 테스트

```bash
# 전체 테스트 + 커버리지
pytest tests/ -v --cov=backend --cov-report=term-missing

# 특정 모듈 테스트
pytest tests/test_admin_api.py -v --tb=short

# 특정 테스트 함수
pytest tests/test_admin_api.py::test_create_document -v
```

### 프론트엔드 E2E 테스트

```bash
# 특정 Phase 테스트
npx playwright test e2e/phase-13-menu-admin.spec.js

# 전체 회귀 테스트
npx playwright test e2e/smoke.spec.js e2e/phase-*.spec.js

# UI 모드 (디버깅)
npx playwright test --ui
```

---

## 테스트 작성 예시

### pytest (백엔드)

```python
# tests/test_admin_crud.py
import pytest
from httpx import AsyncClient
from backend.main import app

@pytest.mark.asyncio
async def test_create_document():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/documents", json={
            "title": "테스트 문서",
            "content": "테스트 내용"
        })
        assert response.status_code == 201
        assert response.json()["title"] == "테스트 문서"
```

### Playwright (프론트엔드)

```javascript
// e2e/phase-13-admin.spec.js
import { test, expect } from '@playwright/test';

test('Admin 설정 페이지 로드', async ({ page }) => {
  await page.goto('/admin/settings');
  
  // 페이지 제목 확인
  await expect(page.locator('h1')).toContainText('관리자 설정');
  
  // 콘솔 에러 없음
  let consoleErrors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') consoleErrors.push(msg.text());
  });
  
  await page.waitForLoadState('networkidle');
  expect(consoleErrors).toHaveLength(0);
});
```

---

**문서 관리**:
- 버전: 1.0 (3rd iteration)
- 최종 수정: 2026-02-17
- 기반: tester.md § 4 (테스트 실행 프로세스 분리)
