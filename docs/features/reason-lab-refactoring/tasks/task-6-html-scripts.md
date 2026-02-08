# Task 6: reason.html 스크립트 태그 반영

**순서**: 6/7  
**기준 문서**: [reason-lab-refactoring-design.md](../../reason-lab-refactoring-design.md)  
**산출물**: `web/src/pages/reason.html` 수정

---

## 1. 목표

Reasoning Lab 페이지에서 **model → common → render → control → 진입점** 순서로 스크립트가 로드되도록 reason.html을 수정한다.

---

## 2. 스크립트 로드 순서 (설계서 3.3)

```html
<script src="/static/js/components/utils.js"></script>
<script src="/static/js/components/layout-component.js"></script>
<script src="/static/js/components/header-component.js"></script>
<script src="/static/js/components/ollama-model-options.js"></script>
<!-- Phase 10-2: 모드별 시각화 -->
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<!-- Reason Lab 리팩터링: model → common → render → control → entry -->
<script src="/static/js/reason/reason-model.js"></script>
<script src="/static/js/reason/reason-common.js"></script>
<script src="/static/js/reason/reason-render.js"></script>
<script src="/static/js/reason/reason-control.js"></script>
<script src="/static/js/reason/reason.js"></script>
```

---

## 3. 작업 체크리스트

- [ ] reason.html 열기 (web/src/pages/reason.html 또는 프로젝트 내 실제 경로)
- [ ] 기존 `reason/reason.js` 단일 스크립트를 위 5개 스크립트(reason-model, reason-common, reason-render, reason-control, reason.js)로 교체
- [ ] utils, layout, header, ollama-model-options, mermaid, chart.js 순서 유지
- [ ] 로드 순서 주석 추가: model → common → render → control → entry
- [ ] 저장 후 브라우저에서 /reason 접속 시 스크립트 오류 없음 확인

---

## 4. 전제 조건

- Task 1~5 완료: reason-model.js, reason-common.js, reason-render.js, reason-control.js, reason.js가 모두 생성·반영되어 있어야 함.

---

## 5. 완료 기준

- reason.html이 설계서 3.3절 스크립트 순서를 따른다.
- /reason 페이지 로드 시 콘솔 에러 없이 초기화·실행·결과 표시가 동작한다.
