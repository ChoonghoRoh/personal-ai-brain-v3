# WCAG 2.1 AA·axe-core 자동화 검증 가이드 (11-5-5)

**Task**: 11-5-5 결과물·접근성 고도화 (§2.3)  
**목적**: Phase 10-3-5 접근성 완료 후, **회귀 방지**를 위해 axe-core 등 자동화 검증 도입 방법을 정리합니다.

---

## 1. axe-core 도입 방법

### 1.1 브라우저 콘솔 (수동)

Reasoning Lab 페이지(`/reason`) 로드 후 개발자 도구 콘솔에서:

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.7.2/axe.min.js"></script>
<script>
  axe.run().then(results => {
    if (results.violations.length) console.error('접근성 위반:', results.violations);
    else console.log('접근성 위반 없음');
  });
</script>
```

CDN 로드 후 `axe.run()` 실행하여 위반 목록 확인.

### 1.2 E2E(Playwright) 연동

- `@axe-core/playwright` 사용.
- 테스트 스펙에서 `/reason` 방문 후 `AxeBuilder`로 스캔, `violations.length === 0` 검증.
- 참고: [axe-core playwright](https://github.com/dequelabs/axe-core-npm/tree/develop/packages/playwright).

### 1.3 CI에서 실행 (선택)

- E2E 단계에서 axe 스캔 포함하여 PR 시 자동 검증.

---

## 2. 검증 대상·회귀 방지

- **대상 페이지**: `/reason` (Reasoning Lab), 공유 페이지 `/reason?share=...`, 의사결정 저장 모달 등.
- **회귀 방지**: Phase 10-3-5에서 적용한 시맨틱·ARIA·포커스·대비 등이 유지되는지 axe로 주기적 실행.

---

## 3. 참고

- [phase-10-improvement-plan.md](phase-10-improvement-plan.md) §2.3
- [task-11-5-5-outputs-accessibility.md](tasks/task-11-5-5-outputs-accessibility.md)
