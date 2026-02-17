# SSOT 버전 관리

**통합 릴리스**: `v5.0-renewal-r3`  
**릴리스 날짜**: 2026-02-17  
**전략**: 요약+상세 분리 + 작업지시 분기 (방안 C 강화)

---

## 릴리스 정보

| 항목 | 내용 |
|------|------|
| **버전** | 5.0-renewal-r3 (3rd iteration) |
| **이전 버전** | 5.0-renewal-r2 (2nd), 5.0-renewal (1st), 4.5 (claude/) |
| **변경 사유** | 작업지시 GUIDES/ 분리, ROLES/ 축약, 필수 읽기 분량 감소 |
| **핵심 읽기** | 1,962줄 (GUIDES 제외) |
| **전체 줄 수** | 2,496줄 (GUIDES 포함) |
| **하위 호환성** | 기존 claude/ 문서 전체 유지 |

---

## 파일별 버전

| 파일 | 2차 → 3차 줄 수 | 주요 변경 | 상태 |
|------|----------------|----------|------|
| `ROLES/backend-dev.md` | 138 → 73 | § 4 작업지시를 GUIDES/로 분리 | ✅ 완료 |
| `ROLES/frontend-dev.md` | 136 → 72 | § 4 작업지시를 GUIDES/로 분리 | ✅ 완료 |
| `ROLES/verifier.md` | 164 → 100 | § 5 검증 프로세스를 GUIDES/로 분리 | ✅ 완료 |
| `ROLES/tester.md` | 151 → 89 | § 4 테스트 프로세스를 GUIDES/로 분리 | ✅ 완료 |
| `GUIDES/backend-work-guide.md` | — → 137 | 신규 작성 (작업지시) | ✅ 완료 |
| `GUIDES/frontend-work-guide.md` | — → 120 | 신규 작성 (작업지시) | ✅ 완료 |
| `GUIDES/verifier-work-guide.md` | — → 127 | 신규 작성 (검증 프로세스) | ✅ 완료 |
| `GUIDES/tester-work-guide.md` | — → 150 | 신규 작성 (테스트 프로세스) | ✅ 완료 |
| `0-entrypoint.md` | 490 → 490 | GUIDES 참조 링크 추가 | ✅ 완료 |
| `VERSION.md` | 100 | 3차 반영 | ✅ 완료 |
| `1-project.md` | 434 | 변경 없음 | ⏳ 유지 |
| `2-architecture.md` | 387 | 변경 없음 | ⏳ 유지 |
| `3-workflow.md` | 310 | 변경 없음 | ⏳ 유지 |

**3차 핵심 읽기 분량**: 1,962줄 (ROLES 334줄 포함, GUIDES 534줄 제외)  
**3차 전체 분량**: 2,496줄 (GUIDES 포함)

---

## 역할별 읽기 경로 (v5.0-renewal-r3)

| 역할 | 필수 읽기 | 시간 | Task 시작 시 추가 읽기 |
|------|----------|------|---------------------|
| **Backend Dev** | 400줄 | 8분 | +137줄 (backend-work-guide) |
| **Frontend Dev** | 400줄 | 8분 | +120줄 (frontend-work-guide) |
| **Verifier** | 600줄 | 12분 | +127줄 (verifier-work-guide) |
| **Tester** | 350줄 | 7분 | +150줄 (tester-work-guide) |
| **Team Lead** | 전체 | 25분 | +534줄 (GUIDES 전체) |

**효과**: 역할별 필수 읽기는 역할 정의 + 코드 규칙만 포함, 작업 시작 시 필요한 작업지시 가이드만 선택적으로 읽음

---

## Breaking Changes (v5.0-renewal-r2 → v5.0-renewal-r3)

| 변경 항목 | 변경 내용 |
|----------|----------|
| **작업지시 분리** | ROLES/*.md의 § 4~5 작업지시 부분을 GUIDES/*.md로 분리 |
| **ROLES/ 축약** | 589줄 → 334줄 (43% 감소) |
| **GUIDES/ 신규** | 4개 파일 신규 작성 (534줄) |
| **필수 읽기 축약** | 2,310줄 → 1,962줄 (15% 감소) |

**호환성**: 기존 1차/2차 결과물은 `iterations/1st/`, `iterations/2nd/`에 백업

---

## 변경 이력

### v5.0-renewal-r3 (2026-02-17)
- **신규**: GUIDES/ 폴더 + 4개 작업지시 가이드 (534줄)
- **축약**: ROLES/*.md (589 → 334줄, 43% 감소)
- **효과**: 필수 읽기 15% 감소, 작업 시작 시만 GUIDES 참조

### v5.0-renewal-r2 (2026-02-17)
- **추가**: FRESH-2~6 (0-entrypoint.md)
- **추가**: 상태별 Action Table (3-workflow.md § 3.1)
- **축약**: VERSION.md (184 → 100줄)
- **줄 수**: 2,310줄

### v5.0-renewal (2026-02-17)
- **신규 작성**: VERSION.md, 0-entrypoint.md, ROLES/*.md
- **요약 버전 작성**: 1-project.md, 2-architecture.md, 3-workflow.md
- **전략**: 방안 C (요약+상세 분리)
- **줄 수**: 2,510줄

---

**문서 관리**:
- 버전: 3.0 (3rd iteration)
- 최종 수정: 2026-02-17
- 관리 주체: QA & Security Analyst
