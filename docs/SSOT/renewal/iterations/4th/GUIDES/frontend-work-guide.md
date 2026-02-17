# Frontend 작업지시 가이드

**버전**: 6.0-renewal-4th  
**대상**: frontend-dev 팀원  
**용도**: Task 실행 프로세스 상세 지침

---

## Task 실행 프로세스

### 1. Task 할당 → 구현 → 보고

```
[1] Team Lead: SendMessage → frontend-dev에게 Task 지시
[2] frontend-dev: TaskList 조회 → Task X-Y-N 확인
[3] frontend-dev: task-X-Y-N.md 읽기 → 완료 기준 확인
[4] frontend-dev: 파일 3개 생성 (HTML, JS, CSS) — web/src/pages, web/public/js, web/public/css
[5] frontend-dev: 로컬 테스트 (브라우저 로드, 콘솔 확인)
[6] frontend-dev: TaskUpdate(status: "completed")
[7] frontend-dev: SendMessage → Team Lead에게 완료 보고
```

### 2. verifier가 FAIL 판정 시 수정

Team Lead가 수정 요청 전달 → frontend-dev 이슈 수정 → 재보고.

---

## 코드 작성 예시

- **ESM**: `type="module"`, `import`/`export` 사용.
- **XSS 방지**: innerHTML 사용 시 `esc()` 필수.
- **외부 CDN 금지**: 로컬 배치(`web/public/libs/`)만 사용.

➜ 상세: [ROLES/frontend-dev.md](../ROLES/frontend-dev.md), [2-architecture.md](../2-architecture.md)

---

**문서 관리**: 버전 6.0-renewal-4th, 단독 사용(4th 세트만 참조)
