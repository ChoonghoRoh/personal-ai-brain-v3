# Task 11-5-5: 결과물·접근성 고도화 (§2.3)

**우선순위**: 11-5 내 5순위 (선택)
**예상 작업량**: 0.5~1일
**의존성**: 11-5-2 완료
**상태**: ✅ 완료

**기반 문서**: [phase-11-5-0-todo-list.md](../phase-11-5-0-todo-list.md)
**Plan**: [phase-11-5-0-plan.md](../phase-11-5-0-plan.md)
**고도화 검토 상세**: [phase-10-improvement-plan.md](../phase-10-improvement-plan.md) **§2.3**
**작업 순서**: [phase-11-navigation.md](../../phase-11-navigation.md)

---

## 1. 개요

### 1.1 목표

**phase-10-improvement-plan §2.3** 표에 따른 **결과물·접근성** 고도화를 구현·검증한다. PDF 품질·WCAG 2.1 AA·다크 모드 일관성 항목을 다룬다.

### 1.2 §2.3 표 항목 (phase-10-improvement-plan)

| 항목                 | 현황                               | 고도화 방향                                | 우선순위 |
| -------------------- | ---------------------------------- | ------------------------------------------ | -------- |
| **PDF 품질**         | 10-3-3 jsPDF/html2canvas 연동 완료 | 다크 모드 PDF 대응·페이지 나눔·폰트 임베드 | 중       |
| **WCAG 2.1 AA**      | 10-3-5 접근성 완료                 | 자동화 검증(axe 등) 도입·회귀 방지         | 중       |
| **다크 모드 일관성** | 10-3-4 다크 모드 완료              | 시각화·모달·공유 페이지 등 누락 영역 점검  | 하       |

---

## 2. 작업 범위 (파일 변경 계획)

### 2.1 수정·신규 (계획에 따름)

| 구분     | 내용                                    |
| -------- | --------------------------------------- |
| **코드** | `web/` — PDF·접근성·다크 모드 관련 경로 |
| **문서** | `docs/phases/phase-11-5/` — task report |

---

## 3. 작업 체크리스트 (Done Definition)

- [x] **PDF 품질**: 다크 모드 PDF 대응(backgroundColor #1e293b) (reason-pdf-export.js)
- [x] **WCAG 2.1 AA**: axe-core 도입 가이드 문서화 ([wcag-axe-guide.md](../wcag-axe-guide.md))
- [x] **다크 모드 일관성**: 모달·viz-retry-btn 다크 변수 적용 (reason.css)
- [x] 산출물: [task-11-5-5-report.md](task-11-5-5-report.md)

---

## 4. 참조·비고

- **선택 Task**: 11-5-2 완료 후 선택 실행.
- [phase-10-improvement-plan.md](../phase-10-improvement-plan.md) §2.3
