# Reason Lab 리팩터링 — Task 목록

**기준 문서**: [reason-lab-refactoring-design.md](../../reason-lab-refactoring-design.md)  
**대상**: `web/public/js/reason/reason.js` → model / common / render / control / 진입점 분리

---

## 작업 순서

| 순서 | Task                                                   | 파일              | 내용                        | 예상 라인 |
| ---- | ------------------------------------------------------ | ----------------- | --------------------------- | --------- |
| 1    | [task-1-model.md](task-1-model.md)                     | reason-model.js   | 상수·상태·데이터 형태       | ~80       |
| 2    | [task-2-common.md](task-2-common.md)                   | reason-common.js  | 옵션/시드 로드, 공통 유틸   | ~120      |
| 3    | [task-3-render.md](task-3-render.md)                   | reason-render.js  | 결과·시각화·추천 렌더       | ~480      |
| 4    | [task-4-control.md](task-4-control.md)                 | reason-control.js | 실행·취소·SSE·UI 상태       | ~380      |
| 5    | [task-5-entry.md](task-5-entry.md)                     | reason.js         | 진입점·초기화·바인딩        | ~180      |
| 6    | [task-6-html-scripts.md](task-6-html-scripts.md)       | reason.html       | 스크립트 태그 순서 반영     | -         |
| 7    | [task-7-regression-test.md](task-7-regression-test.md) | -                 | Phase 10-1·10-2 회귀 테스트 | -         |

---

## 의존 관계

```
model → common → render → control → reason.js (진입점)
```

- Task 1 완료 후 Task 2, Task 2 완료 후 Task 3 … 순서로 진행.
- Task 6은 Task 5까지 반영 후, Task 7은 전체 반영 후 수행.
