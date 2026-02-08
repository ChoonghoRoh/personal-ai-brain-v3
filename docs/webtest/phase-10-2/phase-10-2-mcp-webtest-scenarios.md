# Phase 10-2 MCP(Cursor) 웹테스트 시나리오 — Task당 10개

**대상**: Phase 10-2 모드별 분석 고도화  
**기준**: [phase-10-2-0-todo-list.md](../../phases/phase-10-2/phase-10-2-0-todo-list.md), Task 10-2-1~10-2-4  
**전제**: E2E(Playwright) 완료 후, MCP cursor-ide-browser 또는 Playwright 시나리오 스펙 사용  
**환경**: http://localhost:8000

---

## 공통 준비

- 브라우저에서 `http://localhost:8000/reason` 접속
- 필요 시 질문 입력 후 모드 선택 → Reasoning 실행

---

## Task 10-2-1: design_explain 시각화 (Mermaid) — 시나리오 10개

| #   | 시나리오                             | 조치                                          | 기대 결과                                            | 검증 방법                           |
| --- | ------------------------------------ | --------------------------------------------- | ---------------------------------------------------- | ----------------------------------- |
| 1   | mode-viz 컨테이너 존재               | `/reason` 이동 후 DOM 확인                    | `#mode-viz-container`, `#mode-viz-title` 존재        | snapshot에서 노드 존재              |
| 2   | design_explain 패널 DOM              | `/reason` 로드 후                             | `#viz-design-explain` 요소 존재                      | snapshot                            |
| 3   | 모드 design_explain 선택             | `#mode` 에서 design_explain 선택              | 모드 설명 갱신                                       | mode-description 텍스트             |
| 4   | 실행 전 viz 영역 숨김/빈 상태        | 실행 전 스냅샷                                | mode-viz-container display:none 또는 패널 빈 내용    | container style 또는 패널 innerHTML |
| 5   | design_explain 실행 후 컨테이너 표시 | 질문 입력 → design_explain → 실행 → 결과 수신 | mode-viz-container 표시, 제목 "설계/배경 시각화"     | container visible, title 텍스트     |
| 6   | Mermaid 블록 있으면 SVG/다이어그램   | LLM 응답에 mermaid 포함 시                    | viz-design-explain 내 SVG 또는 다이어그램            | .mermaid-viz 또는 svg 노드          |
| 7   | Mermaid 없으면 fallback 문구         | mermaid 블록 없을 때                          | "Mermaid 다이어그램을 표시하려면..." 안내            | viz-fallback 또는 유사 텍스트       |
| 8   | Mermaid 스크립트 로드                | 페이지 소스/스냅샷                            | script[src*="mermaid"] 존재                          | DOM 확인                            |
| 9   | 시각화 위치(요약 아래·결론 위)       | 결과 표시 후                                  | result-summary 아래, #answer 위에 mode-viz-container | DOM 순서                            |
| 10  | 모드 변경 후 다른 패널 표시          | next_steps 등으로 변경 후 재실행              | 해당 모드 패널만 표시, design_explain 패널 비표시    | 패널 display/가시성                 |

---

## Task 10-2-2: risk_review 매트릭스 — 시나리오 10개

| #   | 시나리오                        | 조치                                | 기대 결과                                       | 검증 방법                  |
| --- | ------------------------------- | ----------------------------------- | ----------------------------------------------- | -------------------------- |
| 1   | viz-risk-review 패널 DOM        | `/reason` 로드 후                   | `#viz-risk-review` 존재                         | snapshot                   |
| 2   | 모드 risk_review 선택           | `#mode` 에서 risk_review 선택       | 모드 설명 갱신                                  | mode-description           |
| 3   | risk_review 실행 후 제목        | 질문 입력 → risk_review → 실행      | "리스크 매트릭스" 제목                          | mode-viz-title             |
| 4   | 5x5 테이블 렌더                 | risk_review 결과 수신 후            | .risk-matrix-table 또는 5x5 구조                | table thead 5열, tbody 5행 |
| 5   | 셀별 risk 클래스                | 스냅샷                              | risk-cell, high/medium/low 등                   | class 포함                 |
| 6   | severity·likelihood 라벨        | 테이블 헤더                         | "낮음"~"높음" 또는 1~5 라벨                     | th 텍스트                  |
| 7   | Chart.js 스크립트 로드          | 페이지                              | script[src*="chart"] 존재                       | DOM                        |
| 8   | 결과 없을 때 빈 매트릭스/메시지 | 컨텍스트 없이 실행                  | 빈 테이블 또는 "다음 단계 항목이 없습니다" 유사 | 패널 내용                  |
| 9   | 연속 모드 전환 시 패널 전환     | design_explain → risk_review 재실행 | viz-risk-review 표시, 이전 viz 숨김             | display/가시성             |
| 10  | 매트릭스 가독성                 | 스냅샷                              | 테이블이 한 화면 또는 스크롤 가능               | 레이아웃                   |

---

## Task 10-2-3: next_steps 로드맵 — 시나리오 10개

| #   | 시나리오                       | 조치                          | 기대 결과                                 | 검증 방법            |
| --- | ------------------------------ | ----------------------------- | ----------------------------------------- | -------------------- |
| 1   | viz-next-steps 패널 DOM        | `/reason` 로드 후             | `#viz-next-steps` 존재                    | snapshot             |
| 2   | 모드 next_steps 선택           | `#mode` 에서 next_steps 선택  | 모드 설명 갱신                            | mode-description     |
| 3   | next_steps 실행 후 제목        | 질문 입력 → next_steps → 실행 | "다음 단계 로드맵" 제목                   | mode-viz-title       |
| 4   | 로드맵 카드/Phase 번호         | 결과 수신 후                  | .roadmap-timeline 또는 .roadmap-item 존재 | DOM                  |
| 5   | 단계별 콘텐츠                  | 스냅샷                        | roadmap-phase + roadmap-content           | 클래스·텍스트        |
| 6   | reasoning_steps 반영           | LLM이 steps 반환 시           | steps 수만큼 카드 또는 항목               | 항목 개수            |
| 7   | 결과 없을 때 fallback          | steps 없을 때                 | "다음 단계 항목이 없습니다" 유사          | 패널 텍스트          |
| 8   | 스크롤/레이아웃                | 항목 많을 때                  | 스크롤 가능 또는 축약 표시                | 레이아웃             |
| 9   | 모드 전환 후 next_steps만 표시 | 다른 모드 → next_steps 재실행 | viz-next-steps 표시, 나머지 viz 숨김      | display              |
| 10  | Phase 번호 순서                | 여러 단계 시                  | 1, 2, 3... 순서 표시                      | roadmap-phase 텍스트 |

---

## Task 10-2-4: history_trace 타임라인 — 시나리오 10개

| #   | 시나리오                          | 조치                             | 기대 결과                                                                   | 검증 방법        |
| --- | --------------------------------- | -------------------------------- | --------------------------------------------------------------------------- | ---------------- |
| 1   | viz-history-trace 패널 DOM        | `/reason` 로드 후                | `#viz-history-trace` 존재                                                   | snapshot         |
| 2   | 모드 history_trace 선택           | `#mode` 에서 history_trace 선택  | 모드 설명 갱신                                                              | mode-description |
| 3   | history_trace 실행 후 제목        | 질문 입력 → history_trace → 실행 | "히스토리 타임라인" 제목                                                    | mode-viz-title   |
| 4   | 타임라인 컨테이너                 | 결과 수신 후                     | .history-timeline 존재                                                      | DOM              |
| 5   | 타임라인 아이템                   | 스냅샷                           | .history-timeline-item, .history-timeline-marker, .history-timeline-content | 클래스           |
| 6   | steps 또는 answer 반영            | LLM 응답 시                      | steps 또는 answer 줄별로 항목                                               | 항목 개수        |
| 7   | 결과 없을 때 fallback             | 이벤트 없을 때                   | "타임라인 이벤트가 없습니다" 유사                                           | 패널 텍스트      |
| 8   | 수직 타임라인 레이아웃            | 스냅샷                           | marker + content 수직 배치                                                  | CSS/구조         |
| 9   | 모드 전환 후 history_trace만 표시 | 다른 모드 → history_trace 재실행 | viz-history-trace 표시                                                      | display          |
| 10  | 시간 순서 표시                    | 여러 이벤트 시                   | 항목이 순서대로 나열                                                        | DOM 순서         |

---

## MCP 실행 체크리스트 (권장 순서)

1. **10-2-1**: 시나리오 1→2→…→10 (design_explain 1회 실행으로 4~7)
2. **10-2-2**: 시나리오 1→…→10 (risk_review 1회 실행)
3. **10-2-3**: 시나리오 1→…→10 (next_steps 1회 실행)
4. **10-2-4**: 시나리오 1→…→10 (history_trace 1회 실행)

---

## 결과 기록 템플릿

| Task   | 시나리오 1~10        | 통과 | 비고 |
| ------ | -------------------- | ---- | ---- |
| 10-2-1 | 1 2 3 4 5 6 7 8 9 10 | ?/10 |      |
| 10-2-2 | 1 2 3 4 5 6 7 8 9 10 | ?/10 |      |
| 10-2-3 | 1 2 3 4 5 6 7 8 9 10 | ?/10 |      |
| 10-2-4 | 1 2 3 4 5 6 7 8 9 10 | ?/10 |      |

**총 40개 시나리오** — MCP 브라우저 또는 Playwright 시나리오 스펙으로 수행 후 통과/실패 기록.
