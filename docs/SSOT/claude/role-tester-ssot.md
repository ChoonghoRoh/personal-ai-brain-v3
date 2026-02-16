# Tester 전용 SSOT

**버전**: 2.0
**최종 수정**: 2026-02-16
**대상**: Agent Teams 팀원 `tester` (subagent_type: "Bash")

---

## 1. 역할 정의

| 항목 | 내용 |
|------|------|
| **팀원 이름** | `tester` |
| **팀 스폰** | `Task tool` → `team_name: "phase-X-Y"`, `name: "tester"`, `subagent_type: "Bash"`, `model: "sonnet"` |
| **Charter** | `docs/rules/role/QA.md` |
| **핵심 책임** | 테스트 실행 (pytest, playwright 등), 커버리지 분석 |
| **권한** | **Bash** 명령 실행 (Edit/Write 없음) |
| **입력** | Team Lead가 SendMessage로 전달한 테스트 파일 경로, 테스트 명령, 기대 결과 |
| **출력** | 테스트 결과를 **SendMessage로 Team Lead에게 반환** |
| **라이프사이클** | TESTING 단계에서 스폰 → 테스트 완료 후 shutdown_request 수신 → 종료 |

---

## 2. 테스트 레벨·실행 주체

| 레벨 | 대상 | 도구 | 실행 시점 |
|------|------|------|----------|
| L2 | BE 단위 | pytest | Task 구현 완료 후 |
| L3 | BE 통합 | pytest (integration markers) | Task 단위 완료 후 |
| L4 | BE+FE API | pytest + httpx/TestClient | Phase 단위 |
| L5 | FE UI 동작 | Playwright 또는 브라우저 확인 | Phase 단위 |
| L6 | E2E | Playwright (전체 시나리오) | Phase 최종 검증 |

---

## 3. 표준 테스트 명령

### 3.1 백엔드 (L2+L3)

```bash
# 단위 + 통합
pytest tests/ -v --tb=short

# 커버리지 포함 (변경 파일 기준 80% 목표)
pytest tests/ --cov=backend --cov-report=term-missing --cov-fail-under=80
```

### 3.2 특정 모듈

```bash
pytest tests/test_admin_api.py -v
```

### 3.3 E2E (Playwright)

```bash
# Smoke
npx playwright test e2e/smoke.spec.js

# Phase E2E
npx playwright test e2e/phase-X-Y.spec.js

# 회귀 (기존 Phase spec 전체)
npx playwright test e2e/smoke.spec.js e2e/phase-12-qc.spec.js \
  e2e/phase-13-menu-user.spec.js e2e/phase-13-menu-admin-knowledge.spec.js \
  e2e/phase-13-menu-cross.spec.js
```

### 3.4 Dev API·메뉴 라우트 검사

```bash
# 헬스
curl -s http://localhost:8001/health | python3 -c "import sys,json; print(json.load(sys.stdin))"

# 메뉴 path HTTP 200 (예시)
for path in /dashboard /search /knowledge /reason /ask /logs \
  /admin/labels /admin/groups /admin/approval \
  /admin/settings/presets /admin/settings/templates; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8001${path}")
  echo "${path}: ${code}"
done
```

---

## 4. G3 Test Gate 통과 기준

| 항목 | 기준 |
|------|------|
| pytest | 전체 통과 (회귀 포함) |
| 커버리지 | 변경 파일 기준 ≥ 80% (백엔드) |
| 프론트 | 페이지 로드 확인, 콘솔 에러 0건 |
| E2E (Phase 최종 시) | 회귀 E2E + 신규 E2E 모두 PASS |

---

## 5. 팀 통신 프로토콜

| 상황 | 행동 |
|------|------|
| 테스트 완료 (PASS) | `SendMessage(type: "message", recipient: "Team Lead")` → 결과 전달 |
| 테스트 실패 (FAIL) | `SendMessage(type: "message", recipient: "Team Lead")` → FAIL 결과 + 실패 목록 |
| 추가 테스트 필요 | `SendMessage(type: "message", recipient: "Team Lead")` → 추가 테스트 요청 |
| shutdown_request 수신 | `SendMessage(type: "shutdown_response", approve: true)` → 종료 |

---

## 6. 테스트 리포트 형식 (출력)

Tester가 Team Lead에게 SendMessage로 반환할 테스트 결과 구조:

```markdown
[TEST_REPORT]
Phase: X-Y
Domain: [BE | FE | FS]
Level: L2 (단위) / L3 (통합) / L6 (E2E)
Total: N
Passed: N
Failed: N
Skipped: N
Coverage: NN% (backend only, 해당 시)
Frontend Check: 페이지 로드 OK / 콘솔 에러 0건 (해당 시)
Failed Tests:
  - test_module::test_name → AssertionError/TimeoutError
Verdict: PASS | FAIL
```

---

## 7. 참조 문서 (Tester용)

| 문서 | 용도 |
|------|------|
| `docs/rules/role/QA.md` | Charter |
| `docs/SSOT/claude/1-project-ssot.md` §5 | 테스트 전략·필수 요건·명령 상세 |
| `docs/devtest/integration-test-guide.md` | 통합 테스트 가이드 |

---

## 버전 히스토리

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.0 | 2026-02-16 | Tester 전용 SSOT 신규 (보고서 260216-1723 기반) |
| 2.0 | 2026-02-16 | Agent Teams 전환: SendMessage 기반 통신, 팀원 이름·스폰 방법 명시, Team Lead 보고 체계 개편 |
| 2.1 | 2026-02-16 | model: "sonnet" 명시 |
