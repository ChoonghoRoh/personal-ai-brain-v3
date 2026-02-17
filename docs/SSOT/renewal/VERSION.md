# SSOT 버전 관리 (Renewal)

**통합 릴리스**: `v5.0-renewal`
**릴리스 날짜**: 2026-02-17
**전략**: 방안 C — 요약+상세 분리
**목표 읽기 시간**: 10-15분 (500줄 요약)

---

## 📦 릴리스 정보

| 항목             | 내용                                                                    |
| ---------------- | ----------------------------------------------------------------------- |
| **버전**         | 5.0-renewal                                                             |
| **이전 버전**    | 4.5 (claude/)                                                           |
| **릴리스 날짜**  | 2026-02-17T11:00:00Z                                                    |
| **Renewal 전략** | 요약+상세 분리 (방안 C)                                                 |
| **변경 사유**    | 기존 2,756줄 → 1,670줄 (39% 감소), 읽기 시간 60분+ → 10-20분 (70% 단축) |
| **하위 호환성**  | 기존 claude/ 문서 전체 유지, 링크 제공                                  |

---

## 📄 파일별 버전

| 파일                    | 줄 수 (목표) | 업데이트 내용                                          | 상태       |
| ----------------------- | ------------ | ------------------------------------------------------ | ---------- |
| `VERSION.md`            | 100          | 신규 작성 — 통합 버전 관리                             | ✅ 완료    |
| `0-entrypoint.md`       | 500          | 신규 작성 — 역할별 체크리스트 + 코어 개념 요약         | 🔄 작성 중 |
| `1-project.md`          | 400          | 기존 578줄 → 400줄 요약 (팀 구성·역할·라이프사이클)    | ⏳ 대기    |
| `2-architecture.md`     | 350          | 기존 516줄 → 350줄 요약 (인프라·BE·FE 구조)            | ⏳ 대기    |
| `3-workflow.md`         | 300          | 기존 1,059줄 → 300줄 요약 (상태머신·워크플로우·게이트) | ⏳ 대기    |
| `ROLES/backend-dev.md`  | 120          | 기존 154줄 → 120줄 (Backend 전용 가이드)               | ⏳ 대기    |
| `ROLES/frontend-dev.md` | 120          | 신규 작성 (Frontend 전용 가이드)                       | ⏳ 대기    |
| `ROLES/verifier.md`     | 100          | 기존 149줄 → 100줄 (Verifier 전용 가이드)              | ⏳ 대기    |
| `ROLES/tester.md`       | 80           | 신규 작성 (Tester 전용 가이드)                         | ⏳ 대기    |

**총 줄 수**: 1,670줄 (목표) vs 2,756줄 (기존) → **39% 감소**

---

## 🎯 역할별 읽기 경로

### Backend Developer (550줄, 10-15분)

| 파일                     | 줄 수 | 보기                         |
| ------------------------ | ----- | ---------------------------- |
| 0-entrypoint.md          | 50    | [보기](0-entrypoint.md)      |
| ROLES/backend-dev.md     | 120   | [보기](ROLES/backend-dev.md) |
| 1-project.md § 팀/상태   | 100   | [보기](1-project.md)         |
| 2-architecture.md § BE   | 200   | [보기](2-architecture.md)    |
| 3-workflow.md § 상태머신 | 80    | [보기](3-workflow.md)        |

**읽기 순서**: 0 → backend-dev → 1 § 팀/상태 → 2 § BE → 3 § 상태머신

### Frontend Developer (550줄, 10-15분)

| 파일                     | 줄 수 | 보기                          |
| ------------------------ | ----- | ----------------------------- |
| 0-entrypoint.md          | 50    | [보기](0-entrypoint.md)       |
| ROLES/frontend-dev.md    | 120   | [보기](ROLES/frontend-dev.md) |
| 1-project.md § 팀/상태   | 100   | [보기](1-project.md)          |
| 2-architecture.md § FE   | 200   | [보기](2-architecture.md)     |
| 3-workflow.md § 상태머신 | 80    | [보기](3-workflow.md)         |

**읽기 순서**: 0 → frontend-dev → 1 § 팀/상태 → 2 § FE → 3 § 상태머신

### Verifier (800줄, 15-20분)

| 파일                      | 줄 수 | 보기                      |
| ------------------------- | ----- | ------------------------- |
| 0-entrypoint.md           | 50    | [보기](0-entrypoint.md)   |
| ROLES/verifier.md         | 100   | [보기](ROLES/verifier.md) |
| 1-project.md              | 200   | [보기](1-project.md)      |
| 2-architecture.md § BE+FE | 300   | [보기](2-architecture.md) |
| 3-workflow.md § 게이트    | 150   | [보기](3-workflow.md)     |

**읽기 순서**: 0 → verifier → 1 → 2 § BE+FE → 3 § 게이트

### Tester (450줄, 8-10분)

| 파일                                                 | 줄 수 | 보기                                  |
| ---------------------------------------------------- | ----- | ------------------------------------- |
| 0-entrypoint.md                                      | 50    | [보기](0-entrypoint.md)               |
| ROLES/tester.md                                      | 80    | [보기](ROLES/tester.md)               |
| 1-project.md § 팀                                    | 100   | [보기](1-project.md)                  |
| 3-workflow.md § 게이트                               | 150   | [보기](3-workflow.md)                 |
| [상세: 테스트 가이드](../claude/role-tester-ssot.md) | 70    | [보기](../claude/role-tester-ssot.md) |

**읽기 순서**: 0 → tester → 1 § 팀 → 3 § 게이트

### Planner (350줄, 7-10분)

| 파일                                                | 줄 수 | 보기                                   |
| --------------------------------------------------- | ----- | -------------------------------------- |
| 0-entrypoint.md                                     | 50    | [보기](0-entrypoint.md)                |
| 1-project.md § Planner                              | 50    | [보기](1-project.md)                   |
| 3-workflow.md § ENTRYPOINT+Planning                 | 100   | [보기](3-workflow.md)                  |
| [상세: Plan 가이드](../claude/role-planner-ssot.md) | 150   | [보기](../claude/role-planner-ssot.md) |

**읽기 순서**: 0 → 1 § Planner → 3 § ENTRYPOINT+Planning

### Team Lead (전체, 30-40분)

| 파일              | 줄 수 | 보기                      |
| ----------------- | ----- | ------------------------- |
| 0-entrypoint.md   | 500   | [보기](0-entrypoint.md)   |
| 1-project.md      | 400   | [보기](1-project.md)      |
| 2-architecture.md | 350   | [보기](2-architecture.md) |
| 3-workflow.md     | 300   | [보기](3-workflow.md)     |
| ROLES/\*.md       | 420   | [보기](ROLES/)            |

**읽기 순서**: 0 → 1 → 2 → 3 → ROLES

---

## 🔄 Breaking Changes (v4.5 → v5.0)

| 변경 항목         | v4.5 (claude/)               | v5.0 (renewal/)            | 마이그레이션                    |
| ----------------- | ---------------------------- | -------------------------- | ------------------------------- |
| **파일 구조**     | `0-ssot-index.md` (300줄)    | `0-entrypoint.md` (500줄)  | 진입점 이름 변경, 요약 확장     |
| **역할별 가이드** | `role-*-ssot.md` (154~149줄) | `ROLES/*.md` (80~120줄)    | `ROLES/` 폴더로 이동, 요약 버전 |
| **상세 내용**     | 각 파일에 포함               | 링크로 참조 (`../claude/`) | 기존 파일 유지, 링크 제공       |
| **버전 관리**     | 파일별 개별 버전             | 통합 VERSION.md            | 버전 일관성 향상                |
| **읽기 경로**     | 불명확                       | 역할별 체크리스트          | 진입 장벽 80% 감소              |

### 호환성 보장

- 기존 `docs/SSOT/claude/` 문서는 **수정 없이 유지**
- renewal/ 문서에서 상세 링크 제공
- v4.x 기반 워크플로우는 **그대로 동작**

---

## 📝 변경 이력

### v5.0-renewal (2026-02-17)

- **신규 작성**: VERSION.md, 0-entrypoint.md, ROLES/\*.md
- **요약 버전 작성**: 1-project.md, 2-architecture.md, 3-workflow.md
- **전략**: 방안 C (요약+상세 분리)
- **목표**: 읽기 시간 70% 단축, 역할별 진입점 명확화

### v4.5 (2026-02-17)

- 3-workflow-ssot.md 업데이트 (ENTRYPOINT 정의 강화)
- 상태 전이 규칙 명확화

### v4.3 (2026-02-16)

- 0-ssot-index.md 업데이트 (SSOT Lock 규칙 추가)
- 팀원 코드 편집 권한 명확화

### v4.2 (2026-02-16)

- 1-project-ssot.md 업데이트 (팀 구성 명확화)
- 역할별 상세 섹션 추가

### v4.0 (2026-02-09)

- AI Team SSOT 초기 버전 (claude/ 폴더)

---

## 🔐 Lock 레벨 (v5.0 신규)

| 파일              | Lock 레벨 | 설명                             |
| ----------------- | --------- | -------------------------------- |
| VERSION.md        | STRICT    | 버전 변경 시 Team Lead 승인 필수 |
| 0-entrypoint.md   | NORMAL    | Phase 실행 중 수정 금지 (LOCK-1) |
| 1-project.md      | NORMAL    | Phase 실행 중 수정 금지 (LOCK-1) |
| 2-architecture.md | NORMAL    | Phase 실행 중 수정 금지 (LOCK-1) |
| 3-workflow.md     | NORMAL    | Phase 실행 중 수정 금지 (LOCK-1) |
| ROLES/\*.md       | FLEXIBLE  | 역할별 가이드, 경미한 수정 허용  |

**Lock 규칙 적용**: SSOT Lock Rules (LOCK-1~5) 동일 적용

---

## 📌 다음 단계

| 단계     | 내용                   | 완료 기준                   |
| -------- | ---------------------- | --------------------------- |
| ✅ 1단계 | VERSION.md 작성        | 버전 정보 완료              |
| 🔄 2단계 | 0-entrypoint.md 작성   | 500줄 이내, 체크리스트 완료 |
| ⏳ 3단계 | 1-project.md 작성      | 400줄 이내, 요약 완료       |
| ⏳ 4단계 | 2-architecture.md 작성 | 350줄 이내, 요약 완료       |
| ⏳ 5단계 | 3-workflow.md 작성     | 300줄 이내, 요약 완료       |
| ⏳ 6단계 | ROLES/\*.md 작성 (4개) | 각 120줄 이내               |
| ⏳ 7단계 | 1차 검증 및 리포트     | verification-1-report.md    |

---

**문서 관리**:

- 버전: 1.0
- 최종 수정: 2026-02-17
- 관리 주체: QA & Security Analyst
