# Phase 11-5: Phase 10 고도화 — Todo List

**상태**: ⏳ 대기
**우선순위**: Phase 11 내 5순위
**예상 작업량**: 2~5일 (11-5-3~11-5-6 선택 시)
**시작일**: -
**완료일**: -

**기준 문서**: [phase-11-master-plan.md](../phase-11-master-plan.md)
**Plan**: [phase-11-5-plan.md](phase-11-5-plan.md)
**고도화 검토 상세**: [phase-10-improvement-plan.md](phase-10-improvement-plan.md) **§2.1~§2.5**

---

## Phase 진행 정보

### 현재 Phase

- **Phase ID**: 11-5
- **Phase 명**: Phase 10 고도화
- **핵심 목표**: phase-10-improvement-plan §2.1~§2.5 영역별 고도화 검토·계획·선택 실행·회귀 확장

### 이전 Phase

- **Prev Phase ID**: Phase 10
- **Prev Phase 명**: Reasoning Lab 고도화(10-1~10-4)
- **전환 조건**: Phase 10 완료·phase-10-final-summary-report 확정

### 다음 Phase

- **Next Phase ID**: (Phase 11 완료 후)
- **전환 조건**: 11-5 완료 시 Phase 11 내 5순위 완료. 11-1~11-4와 병행 가능.

### Phase 11 내 우선순위

| 순위  | Phase ID | Phase 명               | 상태    |
| ----- | -------- | ---------------------- | ------- |
| 1     | 11-1     | DB 스키마·마이그레이션 | ⏳ 대기 |
| 2     | 11-2     | Admin 설정 Backend API | ⏳ 대기 |
| 3     | 11-3     | Admin UI               | ⏳ 대기 |
| 4     | 11-4     | 통합 테스트·운영 준비  | ⏳ 대기 |
| **5** | **11-5** | **Phase 10 고도화**    | ⏳ 대기 |

---

## Task 목록 (7개 Task · §2.1~§2.5 세분 반영)

### 11-5-1: Phase 10 고도화 항목 검토·우선순위 ✅ 완료

**우선순위**: 11-5 내 1순위
**예상 작업량**: 0.5일
**의존성**: Phase 10 완료·phase-10-final-summary-report 확정
**상태**: ✅ 완료 (이미 수행)

- [x] phase-10-final-summary-report·E2E 결과 검토
- [x] phase-10-improvement-plan **§2.1~§2.5** 표 항목 도출·우선순위 반영
- [x] 우선순위·일정 반영한 항목 목록 확정
- [x] 산출물: `phase-10-improvement-plan.md` §2 등에 반영

---

### 11-5-2: 고도화 개발 계획서·Task 정의 ✅ 완료

**우선순위**: 11-5 내 2순위
**예상 작업량**: 0.5일
**의존성**: 11-5-1 완료
**상태**: ✅ 완료 (이미 수행, 11-5-3~7 제작 근거)

- [x] **§2.1** Reasoning Lab 성능·안정성 → Task 11-5-3 세부·완료 기준 정의
- [x] **§2.2** 시각화 고도화 → Task 11-5-4 세부·완료 기준 정의
- [x] **§2.3** 결과물·접근성 → Task 11-5-5 세부·완료 기준 정의
- [x] **§2.4** 공유·저장 → Task 11-5-6 세부·완료 기준 정의
- [x] **§2.5** 회귀·E2E·Phase 11 연동 → Task 11-5-7 세부·완료 기준 정의
- [x] 산출물: `phase-11-5-plan.md`, `phase-11-5-todo-list.md`, `phase-11-5/tasks/` Task 문서(11-5-3~7)

---

### 11-5-3: Reasoning Lab 성능·안정성 고도화 (§2.1) ✅ 완료 (선택)

**우선순위**: 11-5 내 3순위
**예상 작업량**: 0.5~1일
**의존성**: 11-5-2 완료
**상태**: ✅ 완료
**기준**: [phase-10-improvement-plan.md](phase-10-improvement-plan.md) **§2.1** 표

- [ ] **대용량 결과 시각화**: (11-5-4 시각화 영역으로 일부 반영)
- [x] **스트리밍 중 취소**: 취소 후 상태 정리·재실행 전 UI 초기화
- [x] **ETA 정확도**: POST /api/reason/eta/feedback 피드백 반영
- [x] 산출물: [tasks/task-11-5-3-report.md](tasks/task-11-5-3-report.md)

---

### 11-5-4: 시각화 고도화 (§2.2) ✅ 완료 (선택)

**우선순위**: 11-5 내 4순위
**예상 작업량**: 0.5~1일
**의존성**: 11-5-2 완료
**상태**: ✅ 완료
**기준**: [phase-10-improvement-plan.md](phase-10-improvement-plan.md) **§2.2** 표

- [x] **에러·폴백**: Mermaid 파싱 실패 시 폴백 UI·재시도 버튼
- [x] **반응형·모바일**: 시각화 영역 max-height·overflow·터치 스크롤, @media 768px
- [ ] **시각화 성능**: 대용량 노드 시 렌더링 최적화(필요 시)
- [x] 산출물: [tasks/task-11-5-4-report.md](tasks/task-11-5-4-report.md)

---

### 11-5-5: 결과물·접근성 고도화 (§2.3) ✅ 완료 (선택)

**우선순위**: 11-5 내 5순위
**예상 작업량**: 0.5~1일
**의존성**: 11-5-2 완료
**상태**: ✅ 완료
**기준**: [phase-10-improvement-plan.md](phase-10-improvement-plan.md) **§2.3** 표

- [x] **PDF 품질**: 다크 모드 PDF 대응(backgroundColor)
- [x] **WCAG 2.1 AA**: axe-core 도입 가이드 문서화
- [x] **다크 모드 일관성**: 모달·viz-retry 다크 변수 적용
- [x] 산출물: [tasks/task-11-5-5-report.md](tasks/task-11-5-5-report.md)

---

### 11-5-6: 공유·저장 고도화 (§2.4) ✅ 완료 (선택)

**우선순위**: 11-5 내 6순위
**예상 작업량**: 0.5~1일
**의존성**: 11-5-2 완료
**상태**: ✅ 완료
**기준**: [phase-10-improvement-plan.md](phase-10-improvement-plan.md) **§2.4** 표

- [x] **공유 URL**: 만료(expires_in_days)·비공개(is_private)·조회(view_count)
- [x] **의사결정 문서**: 검색(q) title/summary 필터
- [x] 산출물: [tasks/task-11-5-6-report.md](tasks/task-11-5-6-report.md)

---

### 11-5-7: 회귀·E2E·Phase 11 연동 (§2.5) ✅ 완료

**우선순위**: 11-5 내 7순위
**예상 작업량**: 1일
**의존성**: Phase 11-2·11-3 일부 완료(Reasoning 연동) 또는 11-4 통합 테스트 시
**상태**: ✅ 완료
**기준**: [phase-10-improvement-plan.md](phase-10-improvement-plan.md) **§2.5** 표

- [x] **Phase 10 E2E 범위**: 시나리오 추가(에러 경로·취소·공유 만료), 회귀 시나리오 문서화 → [regression-e2e-phase11-scenarios.md](regression-e2e-phase11-scenarios.md)
- [x] **Phase 11 연동 후 회귀**: Admin 설정(템플릿·프리셋·RAG) 변경 시 Reasoning 동작 검증, 회귀 테스트 범위에 Phase 10 포함
- [x] **devtest·통합 테스트**: Phase 10 Reasoning Lab 시나리오를 devtest 또는 webtest와 연계 → [integration-test-guide.md](../../devtest/integration-test-guide.md) §7, [phase-10-regression-scenarios.md](../../devtest/scenarios/phase-10-regression-scenarios.md)
- [x] 산출물: `phase-11-5/regression-e2e-phase11-scenarios.md`, `docs/devtest/scenarios/phase-10-regression-scenarios.md`
