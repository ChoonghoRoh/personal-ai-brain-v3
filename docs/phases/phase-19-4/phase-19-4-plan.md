# Phase 19-4 상세 계획서: 청크 관리 통합 1단계 (탭 기반)

> **상태**: DRAFT
> **작성일**: 2026-02-22
> **Master Plan**: [phase-19-master-plan.md](../phase-19-master-plan.md)
> **SSOT 버전**: 6.0-renewal-4th

---

## 1. 목표

현재 청크 관리가 3개 메뉴로 분산되어 있는 구조를 `/admin/knowledge-workflow`라는 단일 탭 기반 페이지로 통합한다.

- `/admin/chunk-create` (청크 생성) -> 생성 탭
- `/admin/approval` (청크 승인) -> 승인 탭
- `/admin/chunk-labels` (청크 관리) -> 관리 탭

**스코프**: 1단계(탭 기반 통합)만 포함. 2단계(Stepper)는 향후 Phase에서 편성.

---

## 2. 기존 코드 분석

### 2.1 파일 규모

| 파일 | 줄 수 | 역할 |
|------|------:|------|
| `chunk-create.js` | 468 | 청크 생성 (IIFE, 3단계 스텝) |
| `chunk-approval-api.js` | 148 | 승인 API 함수 (전역) |
| `chunk-approval-manager.js` | 322 | 승인 관리 클래스 |
| `admin-approval.js` | 74 | 승인 페이지 초기화 |
| `label-manager-api.js` | 314 | 라벨 API 함수 (전역) |
| `label-manager.js` | 469 | 라벨 관리 클래스 |
| `admin-chunk-labels.js` | 78 | 라벨 페이지 초기화 |
| **JS 합계** | **1,873** | |
| `admin-chunk-create.css` | 450 | 청크 생성 CSS |
| `admin-approval.css` | 400 | 승인 CSS |
| `admin-chunk-labels.css` | 324 | 라벨 관리 CSS |
| **CSS 합계** | **1,174** | |

### 2.2 기존 API 엔드포인트 정리

| 기능 | 메서드 | 엔드포인트 | 사용 페이지 |
|------|--------|-----------|------------|
| 스토리지 파일 목록 | GET | `/api/documents` | chunk-create |
| 파일 내용 조회 | GET | `/api/documents/{path}` | chunk-create |
| 문서 생성 | POST | `/api/knowledge/documents` | chunk-create |
| 문서 목록 | GET | `/api/knowledge/documents` | chunk-create |
| 청크 생성 | POST | `/api/knowledge/chunks` | chunk-create |
| 청크 목록 (전체) | GET | `/api/knowledge/chunks` | chunk-labels |
| 승인 대기 목록 | GET | `/api/approval/chunks/pending` | approval |
| 단일 청크 승인 | POST | `/api/approval/chunks/{id}/approve` | approval |
| 일괄 승인 | POST | `/api/approval/chunks/batch/approve` | approval |
| 단일 청크 거절 | POST | `/api/approval/chunks/{id}/reject` | approval |
| 청크 상세 | GET | `/api/knowledge/chunks/{id}` | approval |
| 관계 추천 | GET | `/api/knowledge/relations/suggest` | approval |
| AI 라벨 추천 | GET | `/api/knowledge/labels/suggest-llm` | approval, chunk-labels |
| 라벨 목록 | GET | `/api/labels` | chunk-labels |
| 청크 라벨 조회 | GET | `/api/labels/chunks/{id}/labels` | chunk-labels |
| 청크 라벨 추가 | POST | `/api/labels/chunks/{id}/labels/{labelId}` | chunk-labels |
| 청크 라벨 제거 | DELETE | `/api/labels/chunks/{id}/labels/{labelId}` | chunk-labels |
| 라벨 제안 적용 | POST | `/api/knowledge/labels/suggest/{id}/apply/{labelId}` | both |
| 라벨 생성 | POST | `/api/labels` | both |

### 2.3 공통 컴포넌트 추출 분석

**공통 패턴 식별**:

1. **청크 목록 표시** (ChunkList): approval과 chunk-labels 양쪽에서 유사한 청크 카드/리스트 렌더링
2. **청크 상세 표시** (ChunkDetail): approval과 chunk-labels 양쪽에서 청크 내용 + 라벨 표시
3. **AI 라벨 추천** (AiSuggestions): 양쪽에서 동일한 AI 추천 UI
4. **페이지네이션** (PaginationComponent): 양쪽에서 이미 공통 사용

**분리 불가능 로직**:

- `chunk-create.js`의 3단계 스텝 로직은 생성 탭 전용 (공통 추출 대상 아님)
- 승인/거절 버튼 로직은 승인 탭 전용

### 2.4 기존 페이지 구조

- **chunk-create**: IIFE 패턴, `DOMContentLoaded`에서 `initializeAdminPage()` 호출
- **approval**: `ChunkApprovalManager` 클래스, `window.approvalManager` 전역 노출
- **chunk-labels**: `LabelManager` 클래스, `window.labelManager` 전역 노출
- 세 페이지 모두 `admin-common.js`, `utils.js`, `layout-component.js`, `header-component.js` 공통 사용

---

## 3. 모듈 분리 전략 (500줄 사전 방지)

단일 `knowledge-workflow.js`에 모든 로직을 넣으면 1,500줄+ 예상. **반드시 모듈 분리**.

### 3.1 신규 파일 구조

```
web/src/pages/admin/knowledge-workflow.html          (신규, ~120줄)
web/public/js/admin/knowledge-workflow.js             (신규, ~200줄) -- 메인: 탭 상태 + 초기화
web/public/js/admin/kw-tab-create.js                  (신규, ~250줄) -- 생성 탭 로직
web/public/js/admin/kw-tab-approval.js                (신규, ~150줄) -- 승인 탭 로직 (ChunkApprovalManager 재사용)
web/public/js/admin/kw-tab-manage.js                  (신규, ~150줄) -- 관리 탭 로직 (LabelManager 재사용)
web/public/css/admin/admin-knowledge-workflow.css      (신규, ~300줄) -- 통합 CSS (탭 + 공통)
```

### 3.2 기존 모듈 재사용

기존 클래스를 **직접 재사용** (복사하지 않음):

- `ChunkApprovalManager` (chunk-approval-manager.js) -> 승인 탭에서 그대로 인스턴스화
- `LabelManager` (label-manager.js) -> 관리 탭에서 그대로 인스턴스화
- `chunk-approval-api.js` -> API 함수 재사용
- `label-manager-api.js` -> API 함수 재사용
- `PaginationComponent` (pagination-component.js) -> 페이지네이션 재사용

### 3.3 줄 수 예상

| 파일 | 예상 줄 수 | 500줄 초과 여부 |
|------|----------:|:-----------:|
| `knowledge-workflow.js` | ~200 | 안전 |
| `kw-tab-create.js` | ~250 | 안전 |
| `kw-tab-approval.js` | ~150 | 안전 |
| `kw-tab-manage.js` | ~150 | 안전 |
| `admin-knowledge-workflow.css` | ~300 | 안전 |

---

## 4. KnowledgeWorkflow 상태 클래스 설계

```javascript
class KnowledgeWorkflow {
  constructor() {
    this.currentTab = 'create';  // 'create' | 'approval' | 'manage'
    this.selectedChunks = new Set();
    this.tabInstances = {};      // { create: CreateTab, approval: ApprovalTab, manage: ManageTab }
  }

  // 탭 전환 (URL 쿼리 동기화)
  switchTab(tabName) { ... }

  // URL ?tab= 파라미터 처리
  syncFromUrl() { ... }

  // 브라우저 뒤로가기 호환
  handlePopState() { ... }

  // 탭 간 데이터 전달
  notifyTabChange(fromTab, event) { ... }

  // 2단계 Stepper 확장 지점
  // toStepper() { ... }  // 향후 2단계에서 탭 -> 스텝 전환
}
```

**2단계 전환 준비**:
- `switchTab()` 메서드를 `goToStep()` 으로 확장 가능
- `notifyTabChange()` 이벤트 패턴을 자동 전환에 활용 가능
- 탭 인스턴스 인터페이스(`init()`, `activate()`, `deactivate()`, `refresh()`)를 2단계에서 그대로 사용

---

## 5. Task 분해

### Task 19-4-1: 통합 페이지 스캐폴딩 [FS]

**담당**: backend-dev (BE 라우트) + frontend-dev (HTML/JS)
**의존성**: 없음 (첫 Task)

**구현 내용**:
- BE: `main.py` _HTML_ROUTES에 `/admin/knowledge-workflow` 라우트 등록
- FE: `knowledge-workflow.html` 신규 생성 (탭 레이아웃 + 3개 탭 콘텐츠 영역)
- FE: `knowledge-workflow.js` 신규 생성 (KnowledgeWorkflow 상태 관리 클래스)
- FE: `admin-knowledge-workflow.css` 신규 생성 (탭 바 + 공통 레이아웃)
- URL `?tab=create|approval|manage` 처리 + `popstate` 이벤트 연동

**완료 기준**:
- `/admin/knowledge-workflow` 접근 시 탭 UI 표시
- 탭 클릭 시 패널 전환 + URL 쿼리 업데이트
- 브라우저 뒤로가기로 이전 탭 복귀
- 기본 탭: create

---

### Task 19-4-2: 생성 탭 통합 [FE]

**담당**: frontend-dev
**의존성**: 19-4-1

**구현 내용**:
- `kw-tab-create.js` 신규 생성
- 기존 `chunk-create.js`의 3단계 로직을 클래스 기반으로 이식
  - `CreateTab` 클래스: `init()`, `activate()`, `deactivate()`, `refresh()`
  - 파일 선택 -> 분할 -> 등록 3단계 동일
- "빠른 승인" 버튼 추가 (등록 후 바로 승인 API 호출)
- 등록 완료 시 `KnowledgeWorkflow.notifyTabChange('create', { type: 'chunks_created', count: N })` 이벤트
- 완료 시 승인 탭 자동 전환 (옵션)

**완료 기준**:
- 생성 탭에서 파일 선택 -> 분할 -> 등록 전체 흐름 동작
- "빠른 승인" 버튼으로 등록+승인 원스텝 처리
- 등록 완료 시 승인 탭 자동 전환

---

### Task 19-4-3: 승인 탭 통합 [FE]

**담당**: frontend-dev
**의존성**: 19-4-1

**구현 내용**:
- `kw-tab-approval.js` 신규 생성
- `ApprovalTab` 클래스: 기존 `ChunkApprovalManager` 인스턴스를 내부에서 생성
- HTML 내 승인 탭 영역에 좌(목록)/우(상세) 레이아웃 구성
- **다중 선택 추가**: 청크 카드에 체크박스 추가
- **일괄 승인 강화**: 선택한 청크만 일괄 승인 (기존: 전체 대기 중 승인)
- **"전체 승인+라벨" 버튼**: 승인 후 관리 탭으로 자동 전환 (라벨 작업 유도)
- 탭 활성화 시 `ChunkApprovalManager.loadPendingChunks()` 자동 호출

**완료 기준**:
- 승인 탭에서 상태 필터 + 목록 + 상세 보기 동작
- 체크박스 다중 선택 + 선택 청크 일괄 승인
- "전체 승인+라벨" 버튼 -> 관리 탭 자동 전환
- AI 라벨 추천 동작

---

### Task 19-4-4: 관리 탭 통합 [FE]

**담당**: frontend-dev
**의존성**: 19-4-1

**구현 내용**:
- `kw-tab-manage.js` 신규 생성
- `ManageTab` 클래스: 기존 `LabelManager` 인스턴스를 내부에서 생성
- HTML 내 관리 탭 영역에 좌(청크 목록)/우(라벨 관리) 레이아웃 구성
- **다중 선택 추가**: 청크 목록에 체크박스 추가
- **일괄 라벨 추가/제거**: 선택한 복수 청크에 동시 라벨 추가/제거
  - FE 루프 처리 (기존 API 활용, Bulk API 미사용)
- AI 라벨 추천 + 라벨 피커 재사용

**완료 기준**:
- 관리 탭에서 청크 목록 + 라벨 관리 동작
- 체크박스 다중 선택 + 선택 청크 일괄 라벨 추가/제거
- 라벨 피커 + AI 추천 동작
- 기존 chunk-labels 페이지의 모든 기능이 관리 탭에서 동작

---

### Task 19-4-5: 네비게이션 + 리다이렉트 [FS]

**담당**: backend-dev (리다이렉트) + frontend-dev (메뉴)
**의존성**: 19-4-1, 19-4-2, 19-4-3, 19-4-4 (모든 탭 완성 후)

**구현 내용**:
- FE: `header-component.js`의 `ADMIN_MENU` 배열 업데이트
  - 기존 3개 메뉴 제거: `chunk-create`, `approval`, `chunk-labels`
  - 신규 1개 추가: `{ path: "/admin/knowledge-workflow", label: "지식 워크플로우", icon: "📋" }`
- BE: `main.py` _HTML_ROUTES에 기존 3개 경로에 대한 리다이렉트 등록
  - `/admin/chunk-create` -> `/admin/knowledge-workflow?tab=create`
  - `/admin/approval` -> `/admin/knowledge-workflow?tab=approval`
  - `/admin/chunk-labels` -> `/admin/knowledge-workflow?tab=manage`
- 회귀 테스트: 리다이렉트 동작 확인, 기존 북마크/링크 호환성 확인

**완료 기준**:
- LNB 메뉴에 "지식 워크플로우" 1개 표시
- 기존 3개 URL 접근 시 통합 페이지로 리다이렉트
- 리다이렉트 시 올바른 탭이 활성화

---

## 6. 실행 순서 및 의존성

```
19-4-1 (스캐폴딩) ──┬──→ 19-4-2 (생성 탭)  ──┐
                     ├──→ 19-4-3 (승인 탭)  ──┤──→ 19-4-5 (네비+리다이렉트)
                     └──→ 19-4-4 (관리 탭)  ──┘
```

- 19-4-2, 19-4-3, 19-4-4는 19-4-1 완료 후 **병렬 가능** (각 탭은 독립적)
- 19-4-5는 모든 탭 완성 후 실행

---

## 7. 리스크 및 대응

| # | 리스크 | 심각도 | 대응 |
|---|--------|:------:|------|
| R1 | 기존 3페이지 JS 이식 복잡도 (1,873줄) | 높음 | 기존 클래스(ChunkApprovalManager, LabelManager) 직접 재사용. 복사 아닌 인스턴스화 |
| R2 | knowledge-workflow.js 500줄 초과 | 높음 | 4파일 분리 구조 확정 (workflow + 탭3개). 각 파일 250줄 이하 목표 |
| R3 | 탭 간 상태 유지 | 중간 | KnowledgeWorkflow 상태 클래스로 중앙 관리 |
| R4 | 기존 전역 함수 의존성 | 중간 | 기존 API 파일(chunk-approval-api.js, label-manager-api.js) script 태그로 유지. 전역 함수 그대로 호출 |
| R5 | 브라우저 뒤로가기 호환 | 낮음 | `history.pushState` + `popstate` 이벤트 핸들링 |
| R6 | 기존 URL 북마크 깨짐 | 낮음 | `RedirectResponse`로 대응 |
| R7 | CSS 3파일 통합 시 충돌 | 중간 | 통합 CSS 신규 작성. 기존 CSS prefix 활용하되 탭 컨텍스트 내로 scope |

---

## 8. 기술 제약사항

- ESM import/export 패턴 (type="module")
- innerHTML 사용 시 반드시 `esc()` / `escapeHtml()` 적용
- CDN 사용 금지 (로컬 리소스만)
- window 전역 변수 새로 할당 금지 (기존 것은 하위 호환성을 위해 유지)
- Bulk API 신규 추가 불필요 (1단계는 기존 API 활용, FE 루프 처리)
- 2단계 전환을 고려한 설계 (KnowledgeWorkflow 상태 클래스를 Stepper 확장 가능하게)
- 기존 3개 페이지의 JS/CSS는 삭제하지 않음 (리다이렉트로 대응, 추후 정리)

---

## 9. 참조

- [Phase 19 Master Plan](../phase-19-master-plan.md)
- [Phase 19 정밀 분석](../../planning/260221-phase19-정밀분석.md)
- [청크관리 통합 최적화 전략](../../planning/260221-1802-청크관리-통합-최적화-전략-10대-전문가-분석.md)
- [SSOT 0-entrypoint](../../SSOT/renewal/iterations/4th/0-entrypoint.md)

---

**문서 관리**: Phase 19-4, 작성일 2026-02-22
