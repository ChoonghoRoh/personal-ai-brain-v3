# 리팩토링 레지스트리

**최종 갱신**: 2026-02-22
**규정**: [refactoring-rules.md](refactoring-rules.md)
**SSOT**: [3-workflow.md §10](../SSOT/renewal/iterations/4th/3-workflow.md#10-코드-유지관리-리팩토링)

---

## 700줄 초과 — 리팩토링 대상

| # | 파일 경로 | 줄 수 | Lv | 상태 | 비고 |
|---|----------|------:|:--:|:----:|------|
| 1 | ~~`backend/routers/knowledge/labels_handlers.py`~~ | ~~748~~ | Lv1 | **해소** | Phase 18-0에서 3파일 분리 완료 |
| 2 | ~~`web/public/css/admin/admin-groups.css`~~ | ~~805~~ | Lv2 | **해소** | Phase 19-3-1에서 5파일 분리 완료 (base 190 + tree 192 + panel 208 + keywords 333 + responsive 20) |

## 500줄 초과 — 모니터링 대상

| # | 파일 경로 | 줄 수 | 잠재 Lv | 등록일 | 비고 |
|---|----------|------:|:------:|:------:|------|
| 1 | `backend/services/system/statistics_service.py` | 699 | Lv1 | 2026-02-21 | **700줄 1줄 차**. 증가 즉시 경고선 |
| 2 | `web/public/css/admin/admin-groups.css` | ~~613~~ **805** | **Lv2 확정** | 2026-02-21 | 700줄 돌파 → 700줄 초과 섹션에 등록 |
| 3 | ~~`web/public/css/reason.css`~~ | ~~607~~ | ~~Lv2~~ | **해소** | Phase 18-3 CSS 재구성: 5파일 분리 |
| 4 | ~~`web/public/css/reason-sections.css`~~ | ~~597~~ | ~~Lv2~~ | **해소** | Phase 18-3 CSS 재구성: 5파일 분리 |
| 5 | `backend/routers/reasoning/stream_executor.py` | 588 | Lv1 | 2026-02-21 | `reason_helpers.py`(484줄) 근접 감시 |
| 6 | `backend/routers/automation/automation.py` | 542 | Lv1 | 2026-02-21 | 독립적 |
| 7 | `web/public/css/admin/settings-common.css` | 534 | Lv1 | 2026-02-21 | 5개 설정 페이지 공유 |
| 8 | `web/public/js/admin/keyword-group-crud.js` | ~~527~~ **472** | Lv2 후보 | 2026-02-21 | Phase 19-3에서 472줄로 감소. 500줄 이하 유지 |
| 9 | `web/public/js/admin/keyword-group-matching.js` | 557 | Lv1 | 2026-02-22 | Phase 19-3에서 낙관적 UI·노드 이동 로직 추가로 증가. `keyword-group-treeview.js`(470줄) 근접 감시 |
| 10 | `backend/routers/knowledge/labels_crud.py` | 575 | Lv1 | 2026-02-22 | Phase 18-1에서 396→575줄 증가. 독립 분리 가능 |

## 페이지 단위 핫스팟 (Lv2 잠재 위험)

| 페이지 | 관련 파일 | 합산 줄 수 | 비고 |
|--------|----------|----------:|------|
| ~~`reason.html`~~ | ~~`reason.css`(607) + `reason-sections.css`(597)~~ | ~~**1,204**~~ | **해소** Phase 18-3: 5파일 분리 (base 227 + form 351 + steps 191 + results 170 + actions 432) |
| `admin/groups.html` | ~~`admin-groups.css`(805)~~ → 5파일(max 333) + `keyword-group-crud.js`(472) + `keyword-group-matching.js`(557) | 472+557=**1,029** | CSS Lv2 **해소**. JS 모니터링 |

## 해소 이력

| # | 원본 파일 (줄 수) | → 결과 파일 (줄 수, 관계) | 수행 Phase | 해소일 |
|---|-------------------|-------------------------|-----------|:------:|
| 1 | `labels_handlers.py` (748줄) | `labels_crud.py`(396줄, 독립) + `labels_tree.py`(151줄, 독립) + `labels_suggest.py`(227줄, 참조:labels_tree) | Phase 18-0 | 2026-02-21 |
| 2 | `reason.css`(607줄) + `reason-sections.css`(597줄) | `reason-base.css`(227줄) + `reason-form.css`(351줄) + `reason-steps.css`(191줄) + `reason-results.css`(170줄) + `reason-actions.css`(432줄) | Phase 18-3 | 2026-02-21 |
| 3 | `admin-groups.css`(805줄) | `admin-groups-base.css`(190줄, 독립) + `admin-groups-tree.css`(192줄, 독립) + `admin-groups-panel.css`(208줄, 독립) + `admin-groups-keywords.css`(333줄, 독립) + `admin-groups-responsive.css`(20줄, 독립) | Phase 19-3 | 2026-02-22 |

※ 관계: `독립` = 단독 수정 가능, `참조:파일명` = 수정 시 함께 확인 필요
※ Lv2 ADR: 수행 Phase의 plan.md 참조

## [예외]

| # | 파일 경로 | 줄 수 | Lv | 사유 | 리포트 | 승인일 |
|---|----------|------:|:--:|------|--------|:------:|
| 1 | `web/public/css/admin/admin-groups.css` | 805 | Lv2 | 19-3이 D&D 제거·폴더형 전환·인라인 편집으로 CSS 대폭 변경 예정. 별도 Phase 분리 후 즉시 재수정은 비효율. 19-3 내 선행 Task(19-3-1)로 CSS 분리 편성 | [phase-19-master-plan.md](../phases/phase-19-master-plan.md) | 2026-02-21 |

---

**상태값**: `조사 대기` → `조사 중` → `Plan 수립` → `리팩토링 중` → `해소` / `[예외]`
**재발 태그**: 해소 이력의 결과 파일이 다시 500줄 초과 시 `[재발]` 부여 → 우선 검토

## 갱신 이력

| 날짜 | 내용 |
|------|------|
| 2026-02-22 | Phase 19-2 완료: statistics.css(337줄), statistics.html(217줄) — 500줄 이내 유지. labels_crud.py(575줄) 누락 보정 등록. Phase Chain 19 전체 완료 |
| 2026-02-22 | Phase 19-3 완료: admin-groups.css(805줄) → 5파일 분리 해소 (max 333줄). keyword-group-matching.js 557줄 신규 등록. keyword-group-crud.js 527→472줄 감소 |
| 2026-02-21 | Phase 18-4 완료: search 관련 파일 500줄 이내 유지 (hybrid_search 347줄, search.js 452줄) |
| 2026-02-21 | Phase 18-3 완료: reason.css+reason-sections.css 1,204줄 핫스팟 해소 → 5파일 분리 (max 432줄) |
| 2026-02-21 | Phase 18-2 완료: document_handlers.py 458줄, folder-tree.js 275줄, knowledge-tree.js 326줄 |
| 2026-02-21 | Phase 18-1 완료: admin-groups.css 613→805줄 (Lv2 확정), labels_crud.py 396→575줄 (모니터링) |
| 2026-02-21 | Phase 18-0 완료: labels_handlers.py(748줄) → 3파일 분리 해소. 테스트 168 passed |
| 2026-02-21 | 해소 이력 섹션 + [재발] 태그 규칙 추가. 규정 v1.1 적용 |
| 2026-02-21 | Level 분류 + 잠재 Lv 분석 + 페이지 단위 핫스팟 추가. 규정 v1.0 적용 |
| 2026-02-21 | 초기 생성. 전체 스캔 (700줄+ 1건, 500줄+ 8건) |
