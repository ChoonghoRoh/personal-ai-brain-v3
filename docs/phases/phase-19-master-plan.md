# Phase 19 Master Plan: 키워드 추천 고도화 + 그룹 UI 리뉴얼 + 청크 통합

> **상태**: DRAFT v2
> **작성일**: 2026-02-21
> **선행 조건**: Phase 18 체인 완료 (18-0 ~ 18-4)
> **리팩토링 레지스트리**: [refactoring-registry.md](../refactoring/refactoring-registry.md)
> **기획 문서**: [260218-phase19-작업목록.md](../planning/260218-phase19-작업목록.md), [260221-phase19-정밀분석.md](../planning/260221-phase19-정밀분석.md)

---

## 목표

1. **키워드 추천 엔진 고도화 (P0)** — LLM 키워드 추천 파이프라인 5건 버그/품질 수정. PAB 핵심 기능 정상화
2. **키워드 그룹 관리 UI 리뉴얼 (P1)** — D&D 제거 → 폴더형 트리 전환, 클릭 피드백, 인라인 편집, CSS Lv2 리팩토링
3. **청크 관리 통합·고도화 1단계 (P1)** — 생성·승인·관리 3메뉴 → 탭 기반 단일 페이지 통합, 다중 선택·일괄 작업
4. **통계 메뉴 레이아웃 변경 (P2)** — 반응형 1행+2단 CSS Grid 레이아웃

---

## 리팩토링 레지스트리 반영 (REFACTOR-2)

| 파일 | 줄 수 | Lv | 관련 Phase | 조치 |
|------|------:|:--:|:----------:|------|
| `admin-groups.css` | 805 | **Lv2** | 19-3 | 19-3 내 선행 Task로 CSS 분리 (아래 [예외] 참조) |
| `keyword-group-crud.js` | 527 | Lv2 후보 | 19-3 | 19-3에서 인라인 편집 구현 시 구조 정리 |
| `statistics_service.py` | 699 | Lv1 | — | 19-2는 FE만 변경, BE 미수정. 모니터링 유지 |

### Lv2 [예외] 확정: admin-groups.css — ✅ 승인 완료 (2026-02-21)

| # | 요건 | 충족 |
|---|------|------|
| 1 | 영향도 조사 실시 | 19-3이 D&D 제거·폴더형 전환·인라인 편집으로 CSS 대폭 변경 예정. 별도 Phase에서 분리 후 즉시 재수정은 비효율 |
| 2 | 분리 불가/비효율 입증 | CSS 분리 자체는 가능하나, 분리 결과물이 19-3에서 즉시 대폭 변경됨. 19-3 내 선행 Task로 편성 시 동일 품질 효과 |
| 3 | 사용자 승인 | **✅ 승인 완료** — 19-3 내 선행 Task(19-3-1)로 편성 확정 |

> **결정**: 별도 `phase-19-refactoring` 미편성. 19-3-1(CSS 분리)을 선행 Task로 실행하여 Lv2 해소.

---

## Phase 체인 구조

| Phase | 내용 | 예상 Task | 의존성 | 우선순위 |
|-------|------|:---------:|--------|:--------:|
| **19-1** | 키워드 추천 엔진 고도화 | 5 | 독립 (최우선) | P0 |
| **19-3** | 키워드 그룹 관리 UI 리뉴얼 | 6 | 독립 (CSS Lv2 분리를 선행 Task로 포함) | P1 |
| **19-4** | 청크 관리 통합 1단계 (탭 기반) | 5 | 독립 (19-1 완료 시 auto-label 품질 향상) | P1 |
| **19-2** | 통계 메뉴 레이아웃 변경 | 3 | 독립 | P2 |

```
19-1 (키워드 추천 P0) ──→ 19-3 (그룹 UI P1) ──→ 19-4 (청크 통합 P1) ──→ 19-2 (통계 P2)
  [BE 핵심]                [FE 리뉴얼]            [FE+BE 통합]            [FE 레이아웃]
```

**실행 순서 근거**:
- 19-1 최우선: 키워드 품질이 전체 시스템(라벨→검색→추론) 품질을 좌우
- 19-3 후속: 독립적이나 그룹 관리 UX 개선이 19-4 청크 통합과 시너지
- 19-4 후속: 19-1 완료로 auto-label 품질이 개선된 상태에서 통합 효과 극대화
- 19-2 마지막: P2 난이도 낮음, 독립적

---

## Phase 19-1: 키워드 추천 엔진 고도화 (P0)

### 배경

키워드 추천은 PAB의 핵심 리소스(키워드) 수집 경로. 현재 5건의 구조적 결함으로 약 30% 데이터 손실 발생.
`generate_keywords_via_llm()`, `match_and_score_labels()`, `postprocess_korean_keywords()`는 `GroupKeywordRecommender`와 `ChunkLabelRecommender`가 공유하므로, 수정 시 양쪽 품질이 함께 개선됨.

### 수정 의존성

```
FIX-2 (계층 매칭) ──→ FIX-1 (공백 분리) ──→ FIX-3 (허용 문자) ──→ FIX-4 (garbled) ──→ FIX-5 (이중 정제)
  [BE 핵심]             [BE 핵심]             [BE 유틸]            [BE 유틸]            [FE]
```

### Task 구조

| Task | 내용 | 도메인 | 대상 파일 |
|------|------|--------|----------|
| 19-1-1 | **FIX-2**: 3단계 계층 매칭 도입 — Tier 1(정확)/2(접두사)/3(부분) + 글자수별 Tier 제한 | [BE] | `recommendation_llm.py` L93-154 |
| 19-1-2 | **FIX-1**: 공백 분리 로직 개선 — 쉼표/개행 우선, `_is_single_concept_word()` 헬퍼 추가 | [BE] | `recommendation_llm.py` L76-90 |
| 19-1-3 | **FIX-3+4**: 유틸 함수 개선 — 허용 문자 `+#&@` 추가 + garbled 오탐 완화(한글→영문 3자+) | [BE] | `korean_utils.py` L15-58 |
| 19-1-4 | **FIX-5**: FE 이중 정제 제거 — `extractKeywordsOnly()` 호출 제거, trim+길이 필터만 유지 | [FE] | `keyword-group-suggestion.js` L82 |
| 19-1-5 | 통합 테스트 — 추천 파이프라인 E2E (LLM mock + DB 매칭 + 정제) + 기존 테스트 회귀 확인 | [TEST] | `tests/test_keyword_recommenders.py` |

### 계층 매칭 설계 (FIX-2)

| Tier | 조건 | 신뢰도 | 글자수 제한 |
|------|------|--------|:----------:|
| **Tier 1**: 정확 매칭 | `func.lower(Label.name) == kw_lower` | base_conf (0.9~0.5) | 모든 키워드 |
| **Tier 2**: 접두사 매칭 | `Label.name.ilike(f"{kw}%")` | base_conf × 0.85 | 3자 이상 |
| **Tier 3**: 부분 매칭 | `Label.name.ilike(f"%{kw}%")` | base_conf × 0.7 | 4자 이상 |
| **미매칭** | Tier 1~3 모두 실패 | — | → `new_keywords`로 분류 |

### 리스크

| 리스크 | 심각도 | 대응 |
|--------|:------:|------|
| FIX-2 성능 (DB 쿼리 3단계) | 중간 | `Label.name` 인덱스 추가 검토 |
| LLM 응답 극단 포맷 | 중간 | 프롬프트 정규화 + 폴백 로직 |
| 공유 함수 영향도 | 낮음 | GroupKeyword + ChunkLabel 양쪽 테스트 |

---

## Phase 19-3: 키워드 그룹 관리 UI 리뉴얼 (P1)

### 배경

현재 키워드 그룹 관리 화면의 UX 문제:
1. D&D 거의 미사용 + 모바일 미지원
2. 노드 클릭/이동 시 시각적 피드백 없음
3. 상세 → 수정 2단계 진입 (뎁스 낭비)
4. 트리 헤더/검색 분산 배치

### Task 구조

| Task | 내용 | 도메인 | 대상 파일 |
|------|------|--------|----------|
| 19-3-1 | **CSS 분리 (Lv2 리팩토링)**: `admin-groups.css`(805줄) → 기능별 4-5개 파일 분리 + HTML CSS 링크 업데이트 | [FE] | `admin-groups.css`, `groups.html` |
| 19-3-2 | **UI-1**: D&D 제거 + 폴더형 트리 전환 — 폴더 아이콘(📁/📂) + 화살표(▶/▼) 토글 + 우클릭/드롭다운 이동 대체 | [FE] | `keyword-group-treeview.js` |
| 19-3-3 | **UI-2**: 클릭 즉시 피드백 + 노드 이동 성능 — `.selected` 즉시 적용, 스피너, 낙관적 UI(백업/복구) | [FE] | `keyword-group-treeview.js`, `keyword-group-matching.js` |
| 19-3-4 | **UI-3**: 바로 수정 모드 — 그룹 선택 시 인라인 편집 폼(이름+설명+부모변경+저장/삭제) 즉시 표시 | [FE] | `keyword-group-crud.js`, `groups.html` |
| 19-3-5 | **UI-4**: 트리 헤더 + 검색 통합 — 검색+깊이 필터 컴팩트 배치, 반응형 CSS | [FE] | `groups.html`, `admin-groups-*.css` |
| 19-3-6 | 회귀 테스트 — 트리 렌더링, 노드 이동, CRUD, 검색 동작 확인 | [TEST] | — |

### CSS 분리 계획 (19-3-1)

```
현재:
  admin-groups.css (805줄) ← 트리+패널+모달+폼+반응형 혼재

TO-BE:
  admin-groups-base.css   (~150줄) ← 레이아웃, 변수, 공통
  admin-groups-tree.css   (~200줄) ← 트리 노드, 폴더 아이콘, 접기/펼치기
  admin-groups-panel.css  (~200줄) ← 상세 패널, 인라인 편집 폼
  admin-groups-modal.css  (~150줄) ← 모달, 컨텍스트 메뉴
  admin-groups-responsive.css (~100줄) ← 반응형 미디어 쿼리
```

### TO-BE 트리 UI

```
키워드 그룹                         [🔍] [깊이: 5]
─────────────────────────────────────────
▼ 📂 프로그래밍
    ▶ 📁 백엔드 개발          (12)
    ▼ 📂 프론트엔드 개발       (8)
        📁 React              (3)
        📁 Vue.js             (2)
    ▶ 📁 데이터베이스          (15)
▶ 📁 인공지능                  (20)
▶ 📁 DevOps                   (7)
─────────────────────────────────────────
```

### 리스크

| 리스크 | 심각도 | 대응 |
|--------|:------:|------|
| D&D 제거 후 이동 UX | 높음 | 우클릭 메뉴 + 상세 패널 드롭다운 병행 |
| 낙관적 UI 실패 시 복구 | 높음 | 백업/복구 로직 + 에러 토스트 |
| 인라인 편집 폼 검증 | 중간 | 필드별 유효성 규칙 정의 |
| 모바일 반응성 | 중간 | 터치 메뉴 변환 + 44px 타겟 크기 |

---

## Phase 19-4: 청크 관리 통합·고도화 1단계 (P1)

### 배경

현재 청크 관리가 3개 메뉴(`/admin/chunk-create`, `/admin/approval`, `/admin/chunk-labels`)로 분산 → 3회 메뉴 이동, 컨텍스트 손실 발생. 1단계에서 탭 기반 통합 + 다중 선택·일괄 작업을 구현.

> **스코프**: 본 Phase는 **1단계(탭 기반 통합)만** 포함. 2단계(Stepper) 및 3단계(전자동)는 향후 Phase에서 별도 편성.

### TO-BE 구조

```
URL: /admin/knowledge-workflow

┌─────────────────────────────────────────┐
│ [1. 생성]  [2. 승인]  [3. 관리]          │ ← 탭
├─────────────────────────────────────────┤
│                                         │
│  현재 탭의 상세 화면 렌더링              │
│                                         │
└─────────────────────────────────────────┘
```

### Task 구조

| Task | 내용 | 도메인 | 대상 파일 |
|------|------|--------|----------|
| 19-4-1 | 통합 페이지 스캐폴딩 — 라우트 등록 + HTML 탭 레이아웃 + 상태 관리 클래스 + 공통 컴포넌트(ChunkList/ChunkDetail) 추출 | [FS] | `main.py`, `knowledge-workflow.html`, `knowledge-workflow.js` (신규) |
| 19-4-2 | 생성 탭 통합 — 기존 chunk-create UI 이식 + "빠른 승인" 버튼 + 완료 시 탭2 자동 전환 | [FE] | `knowledge-workflow.js` |
| 19-4-3 | 승인 탭 통합 — 기존 approval UI 이식 + 다중 선택(체크박스) + 일괄 승인 + "전체 승인+라벨" 버튼 | [FE] | `knowledge-workflow.js` |
| 19-4-4 | 관리 탭 통합 — 기존 chunk-labels UI 이식 + 다중 선택 + 일괄 라벨 추가/제거 | [FE] | `knowledge-workflow.js` |
| 19-4-5 | 네비게이션 + 리다이렉트 — 메뉴 업데이트(`header-component.js`) + 기존 3개 URL 리다이렉트(?tab= 파라미터) + 회귀 테스트 | [FS] | `header-component.js`, `main.py` |

### 데이터 흐름

```
KnowledgeWorkflow State
  currentTab: 'create' | 'approval' | 'manage'
  selectedChunks: Set<ChunkId>
  newChunks: Array<Chunk>
  filters: { status, labels, page }

탭 전환 시:
  create → approval: newChunks를 승인 대기 목록에 반영
  approval → manage: filters.status='approved' 자동 설정
```

### 기존 메뉴 처리

```
/admin/chunk-create   → /admin/knowledge-workflow?tab=create
/admin/approval       → /admin/knowledge-workflow?tab=approval
/admin/chunk-labels   → /admin/knowledge-workflow?tab=manage
```

### 관련 파일 (기존)

| 구분 | 경로 |
|------|------|
| HTML | `chunk-create.html`, `approval.html`, `chunk-labels.html` |
| JS | `chunk-create.js`, `chunk-approval-api.js`, `chunk-approval-manager.js`, `admin-approval.js`, `admin-chunk-labels.js`, `label-manager.js` |
| CSS | `admin-chunk-create.css`, `admin-approval.css`, `admin-chunk-labels.css` |
| BE | `backend/routers/knowledge/approval.py`, `knowledge.py`, `suggestions.py` |

### 리스크

| 리스크 | 심각도 | 대응 |
|--------|:------:|------|
| 기존 3페이지 코드 이식 복잡도 | 높음 | 공통 컴포넌트 추출 우선, 점진적 이식 |
| 탭 간 상태 유지 | 중간 | KnowledgeWorkflow 상태 클래스로 중앙 관리 |
| 기존 URL 직접 접근 호환 | 낮음 | 리다이렉트로 대응 |

---

## Phase 19-2: 통계 메뉴 레이아웃 변경 (P2)

### TO-BE 레이아웃

```
┌─────────────────────────────────────────┐
│ Statistics Dashboard       [🔄 새로고침] │ ← 1단 헤더
├─────────────────────────────────────────┤
│ [총 문서] [총 청크] [총 라벨] [오늘 사용] │ ← 요약 1행
├─────────────────────────────────────────┤
│ [문서유형 분포] [청크상태 분포] [라벨 분포]│ ← 분포 1행 3단
├─────────────────────────────────────────┤
│ [일별 트렌드 (최근 7일) 차트]             │ ← 트렌드 1행
├─────────────────────────────────────────┤
│ [인기 라벨 TOP 10]  |  [프로젝트별 현황]  │ ← 상세 2단 좌우
└─────────────────────────────────────────┘
```

### Task 구조

| Task | 내용 | 도메인 | 대상 파일 |
|------|------|--------|----------|
| 19-2-1 | CSS Grid 레이아웃 재구성 — 요약/분포/트렌드 1행 + 상세 2단 좌우 | [FE] | `statistics.css` |
| 19-2-2 | HTML 마크업 정리 + JS 렌더링 호환 확인 | [FE] | `statistics.html`, `statistics.js`, `statistics-charts.js` |
| 19-2-3 | 반응형 테스트 — Desktop(1200px+)/Tablet(768~1200px)/Mobile(~768px) 3단계 검증 | [FE] | `statistics.css` |

### 반응형 기준점

| 해상도 | 분포 차트 | 상세 현황 |
|--------|:--------:|:--------:|
| Desktop (1200px+) | 3단 1행 | 2단 좌우 |
| Tablet (768~1200px) | 2단 | 2단 좌우 |
| Mobile (~768px) | 1단 | 1단 상하 |

---

## 마일스톤

| 마일스톤 | 내용 | 포함 Phase |
|---------|------|-----------|
| **M1** | 키워드 추천 정상화 — 5건 버그 수정, 추천 품질 검증 | 19-1 |
| **M2** | 키워드 그룹 UX 리뉴얼 — 폴더형 트리, 인라인 편집, CSS Lv2 해소 | 19-3 |
| **M3** | 청크 관리 통합 — 탭 기반 단일 페이지, 다중 선택·일괄 작업 | 19-4 |
| **M4** | 통계 레이아웃 완성 — 반응형 Grid, 2단 상세 현황 | 19-2 |

---

## 기술 검토 사항

### 키워드 추천 (19-1)
- `recommendation_llm.py`의 `generate_keywords_via_llm()`, `match_and_score_labels()`는 `GroupKeywordRecommender`와 `ChunkLabelRecommender` 공유 → 양쪽 테스트 필수
- FIX-2 계층 매칭: `Label.name` 인덱스 존재 여부 확인, 없으면 추가
- FIX-1 공백 분리: `_is_single_concept_word()` 헬퍼 — `^[가-힣]{2,}$` 또는 `^[a-zA-Z]{2,}$`
- FIX-3 허용 문자: 정규식 `[^가-힣a-zA-Z0-9\s\-\./_+#&@]`
- FIX-5: `extractKeywordsOnly()`, `cleanKeyword()` 함수 자체는 삭제하지 않음 (호출만 제거)

### 키워드 그룹 UI (19-3)
- CSS 분리(19-3-1) 완료 후 D&D 제거(19-3-2) 진행 — 순서 엄수
- D&D 제거 시 `nodeMove()` API는 유지 → 우클릭 메뉴/드롭다운에서 호출
- 순환 참조 방지: 백엔드 API에서 체크 (`PATCH /api/keyword-groups/{id}`)
- `keyword-group-crud.js`(527줄) — 19-3-4 인라인 편집 구현 시 구조 정리, 500줄 이내 목표

### 청크 관리 통합 (19-4)
- 기존 3페이지 JS를 직접 이식하지 않고, 공통 컴포넌트(ChunkList, ChunkDetail) 추출 후 재사용
- `knowledge-workflow.js` 신규 파일 — 500줄 초과 사전 방지 (REFACTOR-3)
- 탭 URL 쿼리 `?tab=create|approval|manage` + 브라우저 뒤로가기 호환
- Bulk API 신규 추가 불필요 (1단계는 기존 API 활용, FE 루프 처리)

### 통계 레이아웃 (19-2)
- `statistics_service.py`(699줄) — 19-2는 BE 미수정이므로 영향 없음. 모니터링 유지
- 기존 Chart.js 호환성 확인
- 데이터 100개 항목 이상 시 페이징 검토

---

## 청크 관리 2단계 연계 계획 (19-4 완료 후)

> **19-4(1단계) 완료 → 사용자 리뷰 → 2단계 Phase 편성** 프로토콜

### 리뷰 게이트

19-4(1단계: 탭 기반 통합) DONE 판정 후, 2단계 착수 전 **사용자 리뷰 게이트**를 거친다.

**리뷰 항목**:
1. 1단계 완성도 — 탭 전환·다중 선택·일괄 작업이 기대 수준 충족하는가
2. UX 피드백 — 실사용 결과 기반 개선 요구사항 수집
3. 2단계 스코프 조정 — Stepper 워크플로우·"빠른 생성+승인"·자동 승인 신뢰도 규칙 등 스펙 재검토
4. 우선순위 재판정 — 2단계 즉시 진행 vs 다른 Phase 우선 vs 스코프 축소

### 2단계 편성 방식

리뷰 통과 시, 별도 Master Plan 또는 Phase Chain 확장으로 편성:
- **Phase 20-N** 또는 **Phase 19-5** 등 번호는 리뷰 시점에 확정
- 2단계 상세 스펙: [260221-phase19-정밀분석.md §2.3](../planning/260221-phase19-정밀분석.md#23-2단계-6개월-stepper-기반-워크플로우)
- 핵심 기능: Stepper UI, "빠른 생성+승인" 워크플로우, 조건부 자동 승인, Bulk API
- 3단계(전자동+도메인 특화)는 2단계 완료 후 동일 리뷰 프로세스 적용

### 1단계에서 2단계 전환을 위한 준비 사항

19-4 구현 시 아래 사항을 **미리 고려**하여 2단계 전환 비용을 최소화한다:
- `KnowledgeWorkflow` 상태 클래스를 Stepper 확장 가능하게 설계 (탭 → 스텝 전환 용이)
- 공통 컴포넌트(ChunkList/ChunkDetail)를 독립적으로 추출하여 2단계에서 재사용
- 탭 간 데이터 전달 패턴을 2단계 자동 전환에 활용할 수 있도록 인터페이스 설계

---

## 향후 확장 (Phase 19 이후)

| 방향 | 관련 | 단계 | 비고 |
|------|------|:----:|------|
| 청크 관리 2단계: Stepper + "빠른 생성+승인" | 19-4 | 중기 | **19-4 완료 후 리뷰 게이트** → 별도 Phase 편성 |
| 청크 관리 3단계: 전자동 모드 + 도메인 특화 | 19-4 | 장기 | 2단계 완료 후 동일 리뷰 프로세스 |
| 키워드 의미 기반 매칭 (Qdrant 벡터 유사도 결합) | 19-1 | 중기 | |
| 유사 의미 키워드 자동 감지 (동의어 그룹) | 19-1 | 중기 | |
| 프롬프트 튜닝 UI (관리자 LLM 프롬프트 편집) | 19-1 | 장기 | |

---

## 참조

- [Phase 19 작업 목록](../planning/260218-phase19-작업목록.md)
- [Phase 19 정밀 분석](../planning/260221-phase19-정밀분석.md)
- [청크관리 통합 최적화 전략](../planning/260221-1802-청크관리-통합-최적화-전략-10대-전문가-분석.md)
- [Phase 18 Master Plan](phase-18-master-plan.md)
- [리팩토링 규정](../refactoring/refactoring-rules.md)
- [리팩토링 레지스트리](../refactoring/refactoring-registry.md)
- [SSOT Workflow §10](../SSOT/renewal/iterations/4th/3-workflow.md#10-코드-유지관리-리팩토링)
