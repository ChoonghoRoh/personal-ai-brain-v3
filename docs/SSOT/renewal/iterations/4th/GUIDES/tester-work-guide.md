# Tester 작업지시 가이드

**버전**: 6.0-renewal-4th  
**대상**: tester 팀원  
**용도**: 테스트 실행 프로세스 상세 지침

---

## 테스트 실행 프로세스

### 1. Team Lead로부터 테스트 요청 수신

```
[1] Team Lead: SendMessage → tester에게 테스트 요청 (도메인·변경 파일·명령 명시)
[2] tester: Bash 명령 실행 (pytest / playwright)
[3] tester: 테스트 결과·커버리지 분석
[4] tester: 판정 결정 (PASS: 전체 PASS + 커버리지 ≥80% / FAIL)
[5] tester: SendMessage → Team Lead에게 결과 보고
```

### 2. 테스트 FAIL 시

실패 테스트 상세 분석 → SendMessage로 FAIL 보고 (실패 목록·에러 메시지 포함).

---

## 테스트 명령 예시

> **필수**: 테스트 실행 전 반드시 `clear` 명령으로 터미널을 초기화한 뒤 진행합니다.

- **백엔드**: `clear && pytest tests/ -v --cov=backend --cov-report=term-missing`
- **E2E**: `clear && npx playwright test e2e/phase-X-Y.spec.js`, `clear && npx playwright test e2e/smoke.spec.js e2e/phase-*.spec.js`

➜ 상세: [ROLES/tester.md](../ROLES/tester.md), [3-workflow.md](../3-workflow.md) §4 품질 게이트

---

**문서 관리**: 버전 6.0-renewal-4th, 단독 사용(4th 세트만 참조)
