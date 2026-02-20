# 리팩토링 레지스트리

**최종 갱신**: 2026-02-21
**규정**: [refactoring-rules.md](refactoring-rules.md)
**SSOT**: [3-workflow.md §10](../SSOT/renewal/iterations/4th/3-workflow.md#10-코드-유지관리-리팩토링)

---

## 700줄 초과 — 리팩토링 대상

| # | 파일 경로 | 줄 수 | Lv | 상태 | 비고 |
|---|----------|------:|:--:|:----:|------|
| 1 | `backend/routers/knowledge/labels_handlers.py` | 748 | Lv1 | 조사 대기 | 연관 500줄+ 파일 없음. 트리 API + CRUD + 추천 핸들러 밀집 |

## 500줄 초과 — 모니터링 대상

| # | 파일 경로 | 줄 수 | 잠재 Lv | 등록일 | 비고 |
|---|----------|------:|:------:|:------:|------|
| 1 | `backend/services/system/statistics_service.py` | 699 | Lv1 | 2026-02-21 | **700줄 1줄 차**. 증가 즉시 경고선 |
| 2 | `web/public/css/admin/admin-groups.css` | 613 | Lv2 후보 | 2026-02-21 | `keyword-group-crud.js`(527줄)와 동일 페이지 로드 |
| 3 | `web/public/css/reason.css` | 607 | Lv2 후보 | 2026-02-21 | `reason-sections.css`(597줄)와 동일 페이지, 합산 1,204줄 |
| 4 | `web/public/css/reason-sections.css` | 597 | Lv2 후보 | 2026-02-21 | #3과 쌍 |
| 5 | `backend/routers/reasoning/stream_executor.py` | 588 | Lv1 | 2026-02-21 | `reason_helpers.py`(484줄) 근접 감시 |
| 6 | `backend/routers/automation/automation.py` | 542 | Lv1 | 2026-02-21 | 독립적 |
| 7 | `web/public/css/admin/settings-common.css` | 534 | Lv1 | 2026-02-21 | 5개 설정 페이지 공유 |
| 8 | `web/public/js/admin/keyword-group-crud.js` | 527 | Lv2 후보 | 2026-02-21 | #2와 쌍 |

## 페이지 단위 핫스팟 (Lv2 잠재 위험)

| 페이지 | 관련 파일 | 합산 줄 수 | 비고 |
|--------|----------|----------:|------|
| `reason.html` | `reason.css`(607) + `reason-sections.css`(597) | **1,204** | 한쪽 700줄 돌파 시 Lv2 확정 |
| `admin/groups.html` | `admin-groups.css`(613) + `keyword-group-crud.js`(527) | **1,140** | 한쪽 700줄 돌파 시 Lv2 확정 |

## 해소 이력

| # | 원본 파일 (줄 수) | → 결과 파일 (줄 수, 관계) | 수행 Phase | 해소일 |
|---|-------------------|-------------------------|-----------|:------:|
| - | *(아직 없음)* | - | - | - |

※ 관계: `독립` = 단독 수정 가능, `참조:파일명` = 수정 시 함께 확인 필요
※ Lv2 ADR: 수행 Phase의 plan.md 참조

## [예외]

| # | 파일 경로 | 줄 수 | Lv | 사유 | 리포트 | 승인일 |
|---|----------|------:|:--:|------|--------|:------:|
| - | *(해당 없음)* | - | - | - | - | - |

---

**상태값**: `조사 대기` → `조사 중` → `Plan 수립` → `리팩토링 중` → `해소` / `[예외]`
**재발 태그**: 해소 이력의 결과 파일이 다시 500줄 초과 시 `[재발]` 부여 → 우선 검토

## 갱신 이력

| 날짜 | 내용 |
|------|------|
| 2026-02-21 | 해소 이력 섹션 + [재발] 태그 규칙 추가. 규정 v1.1 적용 |
| 2026-02-21 | Level 분류 + 잠재 Lv 분석 + 페이지 단위 핫스팟 추가. 규정 v1.0 적용 |
| 2026-02-21 | 초기 생성. 전체 스캔 (700줄+ 1건, 500줄+ 8건) |
