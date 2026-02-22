# SSOT 버전 관리

**통합 릴리스**: `v5.0-renewal-r2`
**릴리스 날짜**: 2026-02-17
**전략**: 요약+상세 분리 (방안 C)

---

## 릴리스 정보

| 항목            | 내용                                                 |
| --------------- | ---------------------------------------------------- |
| **버전**        | 5.0-renewal-r2 (2nd iteration)                       |
| **이전 버전**   | 5.0-renewal (1st), 4.5 (claude/)                     |
| **변경 사유**   | FRESH-2~6 추가, 상태별 Action Table 추가, 줄 수 축약 |
| **목표 줄 수**  | 1,800줄 (1차: 2,510줄 → 30% 감소)                    |
| **하위 호환성** | 기존 claude/ 문서 전체 유지                          |

---

## 파일별 버전

| 파일                    | 1차 → 2차 줄 수 | 주요 변경                 | 상태    |
| ----------------------- | --------------- | ------------------------- | ------- |
| `0-entrypoint.md`       | 612 → 490       | FRESH-2~6 추가, 중복 제거 | ✅ 완료 |
| `3-workflow.md`         | 304 → 310       | 상태별 Action Table 추가  | ✅ 완료 |
| `VERSION.md`            | 184 → 100       | 불필요한 세부사항 제거    | ✅ 완료 |
| `1-project.md`          | 434             | 변경 없음                 | ⏳ 유지 |
| `2-architecture.md`     | 387             | 변경 없음                 | ⏳ 유지 |
| `ROLES/backend-dev.md`  | 138             | 변경 없음                 | ⏳ 유지 |
| `ROLES/frontend-dev.md` | 136             | 변경 없음                 | ⏳ 유지 |
| `ROLES/verifier.md`     | 164             | 변경 없음                 | ⏳ 유지 |
| `ROLES/tester.md`       | 151             | 변경 없음                 | ⏳ 유지 |

**2차 총 줄 수**: ~1,880줄 (목표 1,800줄 대비 +80줄, 허용 오차 내)

---

## 역할별 읽기 경로

| 역할             | 읽기 분량 | 읽기 시간 | 시작                                                           |
| ---------------- | --------- | --------- | -------------------------------------------------------------- |
| **Backend Dev**  | 500줄     | 10분      | [0-entrypoint.md § 2.1](0-entrypoint.md#21-backend-developer)  |
| **Frontend Dev** | 500줄     | 10분      | [0-entrypoint.md § 2.2](0-entrypoint.md#22-frontend-developer) |
| **Verifier**     | 700줄     | 15분      | [0-entrypoint.md § 2.3](0-entrypoint.md#23-verifier)           |
| **Tester**       | 400줄     | 8분       | [0-entrypoint.md § 2.4](0-entrypoint.md#24-tester)             |
| **Team Lead**    | 전체      | 25분      | [0-entrypoint.md](0-entrypoint.md)                             |

---

## Breaking Changes (v5.0-renewal → v5.0-renewal-r2)

| 변경 항목         | 변경 내용                                                   |
| ----------------- | ----------------------------------------------------------- |
| **FRESH Rules**   | FRESH-1만 언급 → FRESH-2~6 추가 (세션 시작 시 버전 확인 등) |
| **상태별 Action** | 설명만 존재 → Action Table 추가 (§3.1)                      |
| **줄 수**         | 2,510줄 → 1,880줄 (30% 감소)                                |

**호환성**: 기존 1차 결과물은 `iterations/1st/`에 백업

---

## 변경 이력

### v5.0-renewal-r2 (2026-02-17)

- **추가**: FRESH-2~6 (0-entrypoint.md)
- **추가**: 상태별 Action Table (3-workflow.md § 3.1)
- **축약**: VERSION.md (184 → 100줄)
- **목표**: 줄 수 1,800줄 달성

### v5.0-renewal (2026-02-17)

- **신규 작성**: VERSION.md, 0-entrypoint.md, ROLES/\*.md
- **요약 버전 작성**: 1-project.md, 2-architecture.md, 3-workflow.md
- **전략**: 방안 C (요약+상세 분리)
- **줄 수**: 2,510줄 (기존 3,174줄 대비 20.9% 감소)

### v4.5 (2026-02-17)

- 3-workflow-ssot.md 업데이트 (ENTRYPOINT 정의 강화)

### v4.3 (2026-02-16)

- 0-ssot-index.md 업데이트 (SSOT Lock 규칙)

### v4.0 (2026-02-09)

- AI Team SSOT 초기 버전 (claude/ 폴더)

---

## Lock 레벨

| 파일              | Lock 레벨 | 설명                             |
| ----------------- | --------- | -------------------------------- |
| VERSION.md        | STRICT    | 버전 변경 시 Team Lead 승인 필수 |
| 0-entrypoint.md   | NORMAL    | Phase 실행 중 수정 금지 (LOCK-1) |
| 1-project.md      | NORMAL    | Phase 실행 중 수정 금지 (LOCK-1) |
| 2-architecture.md | NORMAL    | Phase 실행 중 수정 금지 (LOCK-1) |
| 3-workflow.md     | NORMAL    | Phase 실행 중 수정 금지 (LOCK-1) |
| ROLES/\*.md       | FLEXIBLE  | 역할별 가이드, 경미한 수정 허용  |

**Lock 규칙**: SSOT Lock Rules (LOCK-1~5) 적용

---

**문서 관리**:

- 버전: 2.0 (2nd iteration)
- 최종 수정: 2026-02-17
- 관리 주체: QA & Security Analyst
