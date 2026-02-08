# References 문서 — 개발 해야 할 일 포함 여부 내용 검증

**검증일**: 2026-02-06  
**대상**: `reason-lab-refactoring-design-ref.md`, `reasoning-lab-feature-report-ref.md`  
**질의**: 두 문서 중 **개발 해야 할 일(작업·태스크)**이 포함되어 있는지 내용 검증.

---

## 1. 검증 결과 요약

| 문서 | 개발 해야 할 일 포함 | 비고 |
|------|----------------------|------|
| **reason-lab-refactoring-design-ref.md** | **예** | 마이그레이션 순서·파일 작성·회귀 테스트 등 명시적 작업 목록 있음 |
| **reasoning-lab-feature-report-ref.md** | **부분적** | 구현 현황 기술 위주; §12 확장 포인트만 “추가 시 할 일”에 해당 |

---

## 2. reason-lab-refactoring-design-ref.md

### 2.1 문서 성격

- **리팩터링 설계 문서**. `reason.js` 단일 파일을 model / common / render / control / 진입점으로 분리하는 **작업 계획**.
- **Task 목록 링크**: [reason-lab-refactoring/tasks/README.md](reason-lab-refactoring/tasks/README.md) (단계별 task 문서) — 외부 작업 목록 참조.

### 2.2 포함된 “개발 해야 할 일”

| 위치 | 내용 | 개발 작업 여부 |
|------|------|----------------|
| **§3.1** | 디렉터리·파일 구성 (reason-model.js, reason-common.js, reason-render.js, reason-control.js, reason-mode-viz.js) | **예** — 신규 파일 작성 |
| **§3.3** | HTML 스크립트 로드 순서 반영 | **예** — reason.html 수정 |
| **§6 마이그레이션 순서 제안** | 1. reason-model.js 작성 및 변수 이동<br>2. reason-common.js 작성 및 로직 이동<br>3. reason-render.js 작성 및 렌더 이동<br>4. reason-control.js 작성 및 SSE/UI 이동<br>5. reason.js 축소·바인딩만 유지<br>6. reason.html script 태그 반영<br>7. Phase 10-1·10-2 E2E 및 MCP webtest 회귀 테스트 | **예** — 7단계 명시적 개발·검증 작업 |
| **§5.3** | 테스트·목업 (model/control/render 단위·목 교체) | **예** — 테스트 작업 |

**결론**: **개발 해야 할 일이 명확히 포함됨.** 리팩터링 단계·파일 분리·마이그레이션 순서·회귀 테스트가 모두 “할 일”로 기술되어 있음.

---

## 3. reasoning-lab-feature-report-ref.md

### 3.1 문서 성격

- **기능 종합 보고서**. Reasoning Lab의 구현 목표·아키텍처·Backend/Frontend/DB/Qdrant **현황**을 기술.
- “이미 무엇이 구현되어 있는가” 서술 위주.

### 3.2 “개발 해야 할 일”에 해당하는 부분

| 위치 | 내용 | 개발 작업 여부 |
|------|------|----------------|
| **§1~§11** | 구현 목표, 모드, 아키텍처, API, DB, Qdrant, 데이터 흐름, 파일 위치 | **아니오** — 구현 **현황** 기술 |
| **§12 확장 포인트** | 12.1 새 추론 모드 추가 (프롬프트·UI·modeDescriptions)<br>12.2 검색 알고리즘 개선 (가중치·RERANKER·MULTIHOP)<br>12.3 새 추천 유형 추가 (서비스·엔드포인트·프론트 패널) | **부분적** — “추가할 때 할 일” 가이드이지 필수 작업 목록은 아님 |

**결론**: **필수 개발 작업 목록은 아님.** 확장 포인트(§12)만 “추가 개발 시 참고할 작업”에 해당하며, 그 외는 설명·현황 문서.

---

## 4. Phase 11-6 ~ 11-14 plan과의 관계

- **Phase 11-6~11-14**는 reasoning-scenario-plan 문서(00~08, README)에 대한 **plan 검증**만 다룸.  
- **References 두 문서**는 “검증 시 참고할 원본”으로만 쓰이고, phase plan 자체는 **검증 대상 문서(00~08 등)만** 검증.
- **리팩터링/기능 확장** 같은 “개발 할 일”은 Phase 11-6~11-14 범위가 아니며, 별도 phase(예: reason-lab 리팩터링 phase) 또는 task 목록에서 관리하는 것이 맞음.

---

## 5. 최종 정리

| 문서 | 개발 해야 할 일 포함 | 요약 |
|------|----------------------|------|
| **reason-lab-refactoring-design-ref.md** | **예** | 마이그레이션 7단계·파일 분리·회귀 테스트 등 **명시적 작업** 포함. |
| **reasoning-lab-feature-report-ref.md** | **부분적** | §12 확장 포인트만 “추가 개발 시 할 일”에 해당. 나머지는 구현 현황 기술. |

**문서 위치**: `docs/features/reasoning-scenario-plan/references/references-development-content-verification.md`
