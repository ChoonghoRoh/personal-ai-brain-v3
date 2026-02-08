# Phase 7.9.8: 1000줄 초과 파일 코드 검증 및 리팩토링 계획

**작성일**: 2026-01-10  
**상태**: 📋 계획 단계

---

## 📊 대상 파일 분석

### 1. `web/public/js/admin-groups.js` (1064줄)

**주요 기능**:

- 키워드 그룹 CRUD (생성, 읽기, 수정, 삭제)
- 키워드 매칭 및 연결 기능
- 키워드 추천 기능 (AI 기반)
- 그룹-키워드 관계 관리

**함수 목록** (35개):

- 그룹 관리: `loadGroups()`, `loadGroupKeywordsCount()`, `createGroup()`, `updateGroup()`, `deleteGroup()`
- 키워드 관리: `loadKeywords()`, `createKeywordBadge()`, `toggleKeywordSelection()`, `applyGroupKeywords()`, `removeGroupKeywords()`
- UI 관리: `updateMatchingUI()`, `updateSelectAllButtons()`, `selectGroup()`, `clearSelection()`
- 모달 관리: `showCreateGroupModal()`, `showEditGroupModal()`, `closeCreateGroupModal()`, `handleCreateGroup()`
- 키워드 추천: `suggestKeywordsFromDescription()`, `toggleSuggestedKeyword()`, `removeSuggestedKeyword()`, `addKeywordsToGroup()`
- 기타: `searchGroupsAndKeywords()`, `selectAllKeywordsInSection()`, `toggleRemoveKeywordSelection()`, `toggleKeywordSelectionForGroupCheck()`

---

### 2. `web/public/js/knowledge-admin.js` (1446줄)

**주요 기능**:

- **탭 기반 멀티 기능 페이지**
  - 탭 1: 청크 승인/거절 관리
  - 탭 2: 라벨 관리
  - 탭 3: 청크 라벨 관리
  - 탭 4: 키워드 그룹 관리

**함수 목록** (57개):

- 청크 승인: `loadPendingChunks()`, `displayPendingChunks()`, `approveChunk()`, `rejectChunk()`, `showChunkDetail()`, `applyLabelSuggestion()`
- 라벨 관리: `loadLabels()`, `displayLabels()`, `createLabel()`, `deleteLabel()`, `updateLabelSelect()`
- 청크 라벨: `loadChunks()`, `displayChunks()`, `searchChunks()`, `selectChunk()`, `loadChunkLabels()`, `addLabelToChunk()`, `removeLabelFromChunk()`
- 키워드 그룹: `loadGroups()`, `loadKeywords()`, `createGroup()`, `updateGroup()`, `deleteGroup()`, `suggestKeywordsFromDescription()` 등
- 공통: `showError()`, `showSuccess()`, `switchTab()`, `filterByStatus()`

---

## 🔍 중복 코드 분석

### 중복 함수 목록

#### 1. 공통 유틸리티 함수

- `escapeHtml()`: **6개 파일**에 중복
  - admin-groups.js
  - admin-approval.js
  - admin-labels.js
  - knowledge.js
  - ask.js
  - search.js

#### 2. 키워드 그룹 관련 함수 (admin-groups.js ↔ knowledge-admin.js)

- `loadGroups()` - 중복
- `loadKeywords()` - 중복
- `loadGroupKeywordsCount()` - 중복
- `createGroup()` - 중복
- `updateGroup()` - 중복
- `deleteGroup()` - 중복 (단, knowledge-admin.js는 영향도 조회 없음)
- `showCreateGroupModal()` - 중복
- `showEditGroupModal()` - 중복
- `closeCreateGroupModal()` - 중복
- `handleCreateGroup()` - 중복
- `suggestKeywordsFromDescription()` - 중복
- `toggleSuggestedKeyword()` - 중복
- `removeSuggestedKeyword()` - 중복
- `addKeywordsToGroup()` - 중복 (구현 차이 있음)
- `createKeywordBadge()` - 중복
- `selectGroup()` - 중복
- `toggleKeywordSelection()` - 중복
- `updateMatchingUI()` - 중복
- `applyGroupKeywords()` - 중복
- `searchGroupsAndKeywords()` - 중복

**중복 함수 수**: 약 18개

#### 3. 라벨 관리 관련 함수 (admin-labels.js ↔ knowledge-admin.js)

- `loadLabels()` - 중복
- `displayLabels()` - 중복
- `createLabel()` - 중복
- `deleteLabel()` - 중복 (단, knowledge-admin.js는 영향도 조회 없음)
- `loadChunks()` - 중복
- `displayChunks()` - 중복
- `searchChunks()` - 중복
- `selectChunk()` - 중복
- `loadChunkLabels()` - 중복
- `addLabelToChunk()` - 중복
- `removeLabelFromChunk()` - 중복
- `updateLabelSelect()` - 중복

**중복 함수 수**: 약 12개

#### 4. 청크 승인 관련 함수 (admin-approval.js ↔ knowledge-admin.js)

- `loadPendingChunks()` - 중복
- `displayPendingChunks()` - 중복
- `approveChunk()` - 중복
- `rejectChunk()` - 중복
- `showChunkDetail()` - 중복
- `applyLabelSuggestion()` - 중복
- `closeChunkDetail()` - 중복

**중복 함수 수**: 약 7개

#### 5. 메시지 표시 함수

- `showError()`, `showSuccess()`: knowledge-admin.js에 중복 (admin-common.js에 이미 존재)

---

## 📋 리팩토링 계획

### Phase 1: 공통 유틸리티 모듈 생성

**목표**: 중복된 공통 함수들을 별도 모듈로 분리

#### 1.1 공통 유틸리티 파일 생성

- **파일**: `web/public/js/utils.js`
- **함수**:
  - `escapeHtml()` - XSS 방지
  - `validateColorCode()` - 색상 코드 검증
  - `formatNumber()` - 숫자 포맷팅
  - 기타 공통 유틸리티

**예상 효과**: 6개 파일에서 `escapeHtml()` 중복 제거

---

### Phase 2: 키워드 그룹 관리 모듈 분리

**목표**: 키워드 그룹 관련 로직을 공통 모듈로 분리

#### 2.1 키워드 그룹 모듈 생성

- **파일**: `web/public/js/keyword-group-manager.js`
- **클래스**: `KeywordGroupManager`
- **메서드**:
  - `loadGroups()`
  - `loadKeywords()`
  - `createGroup()`
  - `updateGroup()`
  - `deleteGroup()` (영향도 조회 포함)
  - `suggestKeywords()`
  - `addKeywordsToGroup()`
  - `removeKeywordsFromGroup()`
  - `createKeywordBadge()`
  - `updateMatchingUI()`

**사용 파일**:

- `admin-groups.js` - 모듈 사용
- `knowledge-admin.js` - 모듈 사용

**예상 효과**: 약 500줄 중복 코드 제거

---

### Phase 3: 라벨 관리 모듈 분리

**목표**: 라벨 관리 관련 로직을 공통 모듈로 분리

#### 3.1 라벨 관리 모듈 생성

- **파일**: `web/public/js/label-manager.js`
- **클래스**: `LabelManager`
- **메서드**:
  - `loadLabels()`
  - `displayLabels()`
  - `createLabel()`
  - `deleteLabel()` (영향도 조회 포함)
  - `loadChunks()`
  - `displayChunks()`
  - `searchChunks()`
  - `selectChunk()`
  - `loadChunkLabels()`
  - `addLabelToChunk()`
  - `removeLabelFromChunk()`

**사용 파일**:

- `admin-labels.js` - 모듈 사용
- `knowledge-admin.js` - 모듈 사용

**예상 효과**: 약 300줄 중복 코드 제거

---

### Phase 4: 청크 승인 모듈 분리

**목표**: 청크 승인 관련 로직을 공통 모듈로 분리

#### 4.1 청크 승인 모듈 생성

- **파일**: `web/public/js/chunk-approval-manager.js`
- **클래스**: `ChunkApprovalManager`
- **메서드**:
  - `loadPendingChunks()`
  - `displayPendingChunks()`
  - `approveChunk()`
  - `rejectChunk()`
  - `showChunkDetail()`
  - `applyLabelSuggestion()`
  - `closeChunkDetail()`

**사용 파일**:

- `admin-approval.js` - 모듈 사용
- `knowledge-admin.js` - 모듈 사용

**예상 효과**: 약 200줄 중복 코드 제거

---

### Phase 5: knowledge-admin.js 리팩토링

**목표**: knowledge-admin.js를 탭별 모듈로 분리

#### 5.1 탭별 모듈 분리

- **탭 1 (청크 승인)**: `ChunkApprovalManager` 사용
- **탭 2 (라벨 관리)**: `LabelManager` 사용
- **탭 3 (청크 라벨)**: `LabelManager` 사용
- **탭 4 (키워드 그룹)**: `KeywordGroupManager` 사용

#### 5.2 knowledge-admin.js 구조 개선

- 탭 전환 로직만 유지
- 각 탭은 해당 모듈 인스턴스 사용
- 공통 함수 제거 (`showError`, `showSuccess` → `admin-common.js` 사용)

**예상 효과**: 1446줄 → 약 300줄로 감소

---

## 📊 예상 개선 효과

### 코드 라인 수 감소

- **admin-groups.js**: 1064줄 → 약 600줄 (464줄 감소, 43.6%)
- **knowledge-admin.js**: 1446줄 → 약 300줄 (1146줄 감소, 79.2%)
- **신규 모듈**: 약 1000줄 추가
- **순 감소**: 약 610줄 (26.3%)

### 중복 제거

- 공통 유틸리티: 6개 파일에서 중복 제거
- 키워드 그룹: 18개 함수 중복 제거
- 라벨 관리: 12개 함수 중복 제거
- 청크 승인: 7개 함수 중복 제거

### 유지보수성 향상

- 모듈화로 기능별 독립적 수정 가능
- 버그 수정 시 한 곳만 수정하면 모든 페이지에 반영
- 테스트 용이성 향상

---

## ⚠️ 주의사항

### 1. 하위 호환성

- 기존 함수명 유지 (모듈 내부에서 래핑)
- 전역 함수로 노출하여 기존 코드와 호환

### 2. 상태 관리

- 각 모듈이 독립적인 상태 관리
- 전역 변수 최소화

### 3. 점진적 리팩토링

- 한 번에 하나씩 모듈 분리
- 각 단계마다 테스트 수행

---

## 📝 다음 단계

1. ✅ 코드 검증 및 분석 완료
2. ✅ 계획서 작성 완료
3. ⏳ 점검 진행 (사용자 검토)
4. ⏳ 개발 계획서 작성
5. ⏳ 개발 계획서 검토
6. ⏳ 코드 개선 진행

---

## 🔍 상세 기능 분리 계획

### Phase 1: 공통 유틸리티 모듈 (utils.js)

**파일**: `web/public/js/utils.js`

**함수 목록**:

```javascript
// XSS 방지
function escapeHtml(text)

// 색상 코드 검증
function validateColorCode(color)

// 숫자 포맷팅
function formatNumber(num)

// 날짜 포맷팅
function formatDate(date)

// 배열 중복 제거 및 정리
function cleanArray(arr)
```

**영향 파일**:

- admin-groups.js
- admin-approval.js
- admin-labels.js
- knowledge.js
- ask.js
- search.js
- knowledge-admin.js

**예상 감소**: 각 파일당 약 10줄 제거

---

### Phase 2: 키워드 그룹 관리 모듈

**파일**: `web/public/js/keyword-group-manager.js`

**클래스 구조**:

```javascript
class KeywordGroupManager {
  constructor(config) {
    this.onGroupChange = config.onGroupChange;
    this.onKeywordChange = config.onKeywordChange;
    // 상태 관리
    this.selectedGroupId = null;
    this.selectedKeywordIds = new Set();
    this.selectedRemoveKeywordIds = new Set();
    this.selectedSuggestedKeywords = new Set();
  }

  // 그룹 CRUD
  async loadGroups()
  async loadGroupKeywordsCount(groupId)
  async createGroup(name, description, color)
  async updateGroup(groupId, name, description, color)
  async deleteGroup(groupId) // 영향도 조회 포함

  // 키워드 관리
  async loadKeywords()
  createKeywordBadge(keyword, isInGroup)
  toggleKeywordSelection(keywordId)
  toggleRemoveKeywordSelection(keywordId)
  async applyGroupKeywords()
  async removeGroupKeywords()

  // 키워드 추천
  async suggestKeywordsFromDescription(description)
  toggleSuggestedKeyword(keyword, chip)
  removeSuggestedKeyword(keyword, chip)
  async addKeywordsToGroup(groupId, keywordNames)

  // UI 업데이트
  updateMatchingUI()
  updateSelectAllButtons()
  selectGroup(groupId)
  clearSelection()
  searchGroupsAndKeywords(searchTerm)

  // 모달 관리
  showCreateGroupModal()
  async showEditGroupModal(groupId)
  closeCreateGroupModal()
  async handleCreateGroup(event)
}
```

**사용 예시**:

```javascript
// admin-groups.js
const groupManager = new KeywordGroupManager({
  onGroupChange: () => {
    /* UI 업데이트 */
  },
  onKeywordChange: () => {
    /* UI 업데이트 */
  },
});

// knowledge-admin.js (탭 4)
const groupsTabManager = new KeywordGroupManager({
  onGroupChange: () => {
    /* 탭별 UI 업데이트 */
  },
});
```

**예상 감소**:

- admin-groups.js: 1064줄 → 약 400줄 (664줄 감소)
- knowledge-admin.js: 1446줄 → 약 1200줄 (246줄 감소)

---

### Phase 3: 라벨 관리 모듈

**파일**: `web/public/js/label-manager.js`

**클래스 구조**:

```javascript
class LabelManager {
  constructor(config) {
    this.onLabelChange = config.onLabelChange;
    this.onChunkChange = config.onChunkChange;
    // 상태 관리
    this.allLabels = [];
    this.allChunks = [];
    this.selectedChunkId = null;
  }

  // 라벨 CRUD
  async loadLabels()
  displayLabels()
  async createLabel(name, labelType, description)
  async deleteLabel(labelId) // 영향도 조회 포함

  // 청크 관리
  async loadChunks()
  displayChunks(filteredChunks)
  searchChunks(searchTerm)
  async selectChunk(chunkId)

  // 청크 라벨 관리
  async loadChunkLabels(chunkId)
  async addLabelToChunk(chunkId, labelId)
  async removeLabelFromChunk(chunkId, labelId)
  updateLabelSelect()
}
```

**사용 예시**:

```javascript
// admin-labels.js
const labelManager = new LabelManager({
  onLabelChange: () => {
    /* UI 업데이트 */
  },
  onChunkChange: () => {
    /* UI 업데이트 */
  },
});

// knowledge-admin.js (탭 1, 2)
const labelsTabManager = new LabelManager({
  onLabelChange: () => {
    /* 탭별 UI 업데이트 */
  },
});
```

**예상 감소**:

- admin-labels.js: 약 50줄 감소
- knowledge-admin.js: 약 300줄 감소

---

### Phase 4: 청크 승인 모듈

**파일**: `web/public/js/chunk-approval-manager.js`

**클래스 구조**:

```javascript
class ChunkApprovalManager {
  constructor(config) {
    this.onChunkChange = config.onChunkChange;
    // 상태 관리
    this.currentStatusFilter = "draft";
    this.pendingChunks = [];
  }

  // 청크 승인 관리
  async loadPendingChunks(status)
  displayPendingChunks()
  async approveChunk(chunkId)
  async rejectChunk(chunkId, reason)
  filterByStatus(status)

  // 청크 상세
  async showChunkDetail(chunkId)
  closeChunkDetail()
  async applyLabelSuggestion(chunkId, labelId, confidence)
}
```

**사용 예시**:

```javascript
// admin-approval.js
const approvalManager = new ChunkApprovalManager({
  onChunkChange: () => {
    /* UI 업데이트 */
  },
});

// knowledge-admin.js (탭 3)
const approvalTabManager = new ChunkApprovalManager({
  onChunkChange: () => {
    /* 탭별 UI 업데이트 */
  },
});
```

**예상 감소**:

- admin-approval.js: 약 50줄 감소
- knowledge-admin.js: 약 200줄 감소

---

### Phase 5: knowledge-admin.js 리팩토링

**목표**: 탭별 모듈 사용으로 구조 단순화

**리팩토링 후 구조**:

```javascript
// 탭별 매니저 인스턴스
let labelsTabManager;
let groupsTabManager;
let approvalTabManager;

// 탭 전환
function switchTab(tab) {
  // 탭별 매니저 초기화 (지연 로딩)
  if (tab === "labels" && !labelsTabManager) {
    labelsTabManager = new LabelManager({...});
  }
  if (tab === "groups" && !groupsTabManager) {
    groupsTabManager = new KeywordGroupManager({...});
  }
  if (tab === "approval" && !approvalTabManager) {
    approvalTabManager = new ChunkApprovalManager({...});
  }

  // 탭 표시/숨김
  // ...
}
```

**예상 감소**: 1446줄 → 약 200-300줄 (약 80% 감소)

---

## 📊 최종 예상 효과

### 코드 라인 수

| 파일               | 현재   | 리팩토링 후 | 감소      | 감소율    |
| ------------------ | ------ | ----------- | --------- | --------- |
| admin-groups.js    | 1064줄 | 400줄       | 664줄     | 62.4%     |
| knowledge-admin.js | 1446줄 | 250줄       | 1196줄    | 82.7%     |
| **신규 모듈**      | -      | ~1000줄     | -         | -         |
| **순 감소**        | 2510줄 | 1650줄      | **860줄** | **34.3%** |

### 중복 제거

- 공통 유틸리티: 7개 파일에서 중복 제거
- 키워드 그룹: 18개 함수 중복 제거
- 라벨 관리: 12개 함수 중복 제거
- 청크 승인: 7개 함수 중복 제거
- **총 약 44개 함수 중복 제거**

---

## ⚠️ 리스크 및 대응 방안

### 리스크 1: 하위 호환성

**문제**: 기존 코드가 전역 함수에 의존
**대응**: 모듈 내부에서 전역 함수로 래핑하여 노출

### 리스크 2: 상태 관리 복잡도

**문제**: 여러 모듈 간 상태 공유 필요
**대응**: 이벤트 기반 통신 또는 콜백 함수 사용

### 리스크 3: 테스트 부담

**문제**: 리팩토링 후 모든 기능 테스트 필요
**대응**: 단계별 리팩토링 및 각 단계마다 테스트

---

## 📋 점검 체크리스트

### 코드 분석 점검

- [x] 파일 구조 분석 완료
- [x] 중복 함수 식별 완료
- [x] 공통 로직 식별 완료
- [x] 분리 가능 모듈 식별 완료

### 계획서 점검

- [x] 리팩토링 계획 수립 완료
- [x] 예상 효과 계산 완료
- [x] 리스크 분석 완료
- [ ] 사용자 검토 대기

### 다음 단계

- [ ] 개발 계획서 작성
- [ ] 개발 계획서 검토
- [ ] 코드 개선 진행

---

## 🔍 상세 분석 결과

### admin-groups.js 구조

```
전역 변수 (7개)
├── matchingMode
├── selectedGroupId
├── selectedKeywordIds
├── selectedRemoveKeywordIds
├── selectedKeywordForGroupCheck
├── selectedSuggestedKeywords
└── editingGroupId

함수 그룹:
├── 그룹 CRUD (6개)
│   ├── loadGroups()
│   ├── loadGroupKeywordsCount()
│   ├── createGroup()
│   ├── updateGroup()
│   ├── deleteGroup()
│   └── handleCreateGroup()
├── 키워드 관리 (8개)
│   ├── loadKeywords()
│   ├── createKeywordBadge()
│   ├── toggleKeywordSelection()
│   ├── toggleRemoveKeywordSelection()
│   ├── toggleKeywordSelectionForGroupCheck()
│   ├── selectAllKeywordsInSection()
│   ├── applyGroupKeywords()
│   └── removeGroupKeywords()
├── UI 업데이트 (3개)
│   ├── updateMatchingUI()
│   ├── updateSelectAllButtons()
│   └── clearSelection()
├── 모달 관리 (4개)
│   ├── showCreateGroupModal()
│   ├── showEditGroupModal()
│   ├── closeCreateGroupModal()
│   └── handleCreateGroup()
├── 키워드 추천 (5개)
│   ├── suggestKeywordsFromDescription()
│   ├── toggleSuggestedKeyword()
│   ├── removeSuggestedKeyword()
│   ├── clearSuggestedKeywords()
│   └── addKeywordsToGroup()
└── 기타 (2개)
    ├── selectGroup()
    └── searchGroupsAndKeywords()
```

### knowledge-admin.js 구조

```
전역 변수 (9개)
├── allLabels
├── allChunks
├── selectedChunkId
├── currentStatusFilter
├── pendingChunks
├── matchingMode
├── selectedGroupId
├── selectedKeywordIds
└── editingGroupId

함수 그룹:
├── 초기화 (2개)
│   ├── initializePage()
│   └── switchTab()
├── 청크 승인 (7개) - admin-approval.js와 중복
│   ├── loadPendingChunks()
│   ├── displayPendingChunks()
│   ├── approveChunk()
│   ├── rejectChunk()
│   ├── showChunkDetail()
│   ├── applyLabelSuggestion()
│   └── closeChunkDetail()
├── 라벨 관리 (12개) - admin-labels.js와 중복
│   ├── loadLabels()
│   ├── displayLabels()
│   ├── createLabel()
│   ├── deleteLabel()
│   ├── loadChunks()
│   ├── displayChunks()
│   ├── searchChunks()
│   ├── selectChunk()
│   ├── loadChunkLabels()
│   ├── addLabelToChunk()
│   ├── removeLabelFromChunk()
│   └── updateLabelSelect()
├── 키워드 그룹 (18개) - admin-groups.js와 중복
│   └── (위와 동일)
└── 공통 (2개)
    ├── showError()
    └── showSuccess()
```

---

## 🎯 리팩토링 우선순위

### 우선순위 높음 (즉시 진행)

1. **공통 유틸리티 모듈** (utils.js)

   - 영향 범위: 6개 파일
   - 난이도: 낮음
   - 예상 소요: 0.5일

2. **키워드 그룹 모듈** (keyword-group-manager.js)
   - 영향 범위: 2개 파일
   - 난이도: 중간
   - 예상 소요: 2일

### 우선순위 중간

3. **라벨 관리 모듈** (label-manager.js)

   - 영향 범위: 2개 파일
   - 난이도: 중간
   - 예상 소요: 2일

4. **청크 승인 모듈** (chunk-approval-manager.js)
   - 영향 범위: 2개 파일
   - 난이도: 중간
   - 예상 소요: 1.5일

### 우선순위 낮음

5. **knowledge-admin.js 리팩토링**
   - 영향 범위: 1개 파일
   - 난이도: 높음
   - 예상 소요: 3일

---

## 📏 리팩토링 예상 코드 라인 수 상세 산출

### 현재 파일 라인 수

| 파일                 | 현재 라인 수 |
| -------------------- | ------------ |
| `admin-groups.js`    | 1,063줄      |
| `knowledge-admin.js` | 1,446줄      |
| `admin-labels.js`    | 359줄        |
| `admin-approval.js`  | 360줄        |
| **합계**             | **3,228줄**  |

---

### Phase 1: 공통 유틸리티 모듈 (utils.js)

**신규 생성 파일**:

- `web/public/js/utils.js`: **약 50줄**
  - `escapeHtml()`: 12줄
  - `validateColorCode()`: 15줄
  - `formatNumber()`: 10줄
  - `formatDate()`: 13줄

**제거될 코드**:

- `admin-groups.js`: 12줄 (escapeHtml)
- `admin-labels.js`: 12줄 (escapeHtml)
- `admin-approval.js`: 12줄 (escapeHtml)
- `knowledge.js`: 12줄 (escapeHtml)
- `ask.js`: 12줄 (escapeHtml)
- `search.js`: 12줄 (escapeHtml)
- **총 제거**: 72줄

**순 증가**: 50줄 - 72줄 = **-22줄** (감소)

---

### Phase 2: 키워드 그룹 관리 모듈 (keyword-group-manager.js)

**신규 생성 파일**:

- `web/public/js/keyword-group-manager.js`: **약 650줄**
  - 클래스 구조 및 생성자: 30줄
  - 그룹 CRUD 메서드: 150줄
  - 키워드 관리 메서드: 200줄
  - UI 업데이트 메서드: 120줄
  - 모달 관리 메서드: 80줄
  - 키워드 추천 메서드: 70줄

**제거될 코드**:

- `admin-groups.js`: 약 950줄 (키워드 그룹 관련 함수 전체)
  - escapeHtml 제외: 12줄
  - 초기화 코드 유지: 약 30줄
  - **제거**: 약 908줄
- `knowledge-admin.js`: 약 760줄 (684-1446줄, 키워드 그룹 관련)
  - **제거**: 약 760줄
- **총 제거**: 약 1,668줄

**리팩토링 후**:

- `admin-groups.js`: 1,063줄 → **약 150줄** (모듈 사용 코드만)
- `knowledge-admin.js`: 1,446줄 → **약 686줄** (키워드 그룹 관련 제거)

**순 증가**: 650줄 - 1,668줄 = **-1,018줄** (감소)

---

### Phase 3: 라벨 관리 모듈 (label-manager.js)

**신규 생성 파일**:

- `web/public/js/label-manager.js`: **약 250줄**
  - 클래스 구조 및 생성자: 25줄
  - 라벨 CRUD 메서드: 80줄
  - 청크 관리 메서드: 70줄
  - 청크 라벨 관리 메서드: 75줄

**제거될 코드**:

- `admin-labels.js`: 약 300줄 (라벨 관련 함수)
  - escapeHtml 제외: 12줄
  - 초기화 코드 유지: 약 50줄
  - **제거**: 약 238줄
- `knowledge-admin.js`: 약 200줄 (408-600줄, 라벨 관련)
  - **제거**: 약 200줄
- **총 제거**: 약 438줄

**리팩토링 후**:

- `admin-labels.js`: 359줄 → **약 120줄** (모듈 사용 코드만)
- `knowledge-admin.js`: 686줄 → **약 486줄** (라벨 관련 제거)

**순 증가**: 250줄 - 438줄 = **-188줄** (감소)

---

### Phase 4: 청크 승인 모듈 (chunk-approval-manager.js)

**신규 생성 파일**:

- `web/public/js/chunk-approval-manager.js`: **약 180줄**
  - 클래스 구조 및 생성자: 20줄
  - 청크 승인 메서드: 60줄
  - 청크 상세 메서드: 80줄
  - 필터 메서드: 20줄

**제거될 코드**:

- `admin-approval.js`: 약 300줄 (청크 승인 관련 함수)
  - escapeHtml 제외: 12줄
  - 초기화 코드 유지: 약 50줄
  - **제거**: 약 238줄
- `knowledge-admin.js`: 약 200줄 (122-380줄, 청크 승인 관련)
  - **제거**: 약 200줄
- **총 제거**: 약 438줄

**리팩토링 후**:

- `admin-approval.js`: 360줄 → **약 120줄** (모듈 사용 코드만)
- `knowledge-admin.js`: 486줄 → **약 286줄** (청크 승인 관련 제거)

**순 증가**: 180줄 - 438줄 = **-258줄** (감소)

---

### Phase 5: knowledge-admin.js 리팩토링

**리팩토링 후**:

- `knowledge-admin.js`: 286줄 → **약 250줄**
  - 탭 전환 로직: 80줄
  - 모듈 초기화: 100줄
  - 공통 함수 제거 (showError, showSuccess): 20줄
  - 기타 정리: 50줄

**제거될 코드**: 약 36줄

---

## 📊 최종 예상 코드 라인 수

### 리팩토링 후 파일별 라인 수

| 파일                 | 현재        | 리팩토링 후 | 감소        | 감소율    |
| -------------------- | ----------- | ----------- | ----------- | --------- |
| `admin-groups.js`    | 1,063줄     | 150줄       | 913줄       | 85.9%     |
| `knowledge-admin.js` | 1,446줄     | 250줄       | 1,196줄     | 82.7%     |
| `admin-labels.js`    | 359줄       | 120줄       | 239줄       | 66.6%     |
| `admin-approval.js`  | 360줄       | 120줄       | 240줄       | 66.7%     |
| **기존 파일 합계**   | **3,228줄** | **640줄**   | **2,588줄** | **80.2%** |

### 신규 생성 모듈 파일

| 파일                        | 예상 라인 수 |
| --------------------------- | ------------ |
| `utils.js`                  | 50줄         |
| `keyword-group-manager.js`  | 650줄        |
| `label-manager.js`          | 250줄        |
| `chunk-approval-manager.js` | 180줄        |
| **신규 모듈 합계**          | **1,130줄**  |

### 전체 코드 라인 수 변화

| 구분            | 라인 수               |
| --------------- | --------------------- |
| **리팩토링 전** | 3,228줄               |
| **리팩토링 후** | 1,770줄 (640 + 1,130) |
| **순 감소**     | **1,458줄**           |
| **감소율**      | **45.2%**             |

---

## 📈 단계별 코드 라인 수 변화

### Phase 1 완료 후

- 기존 파일: 3,228줄 → 3,156줄 (-72줄)
- 신규 모듈: 50줄
- **합계**: 3,206줄 (-22줄)

### Phase 2 완료 후

- 기존 파일: 3,156줄 → 1,836줄 (-1,320줄)
- 신규 모듈: 700줄 (50 + 650)
- **합계**: 2,536줄 (-692줄)

### Phase 3 완료 후

- 기존 파일: 1,836줄 → 1,598줄 (-238줄)
- 신규 모듈: 950줄 (700 + 250)
- **합계**: 2,548줄 (-680줄)

### Phase 4 완료 후

- 기존 파일: 1,598줄 → 1,360줄 (-238줄)
- 신규 모듈: 1,130줄 (950 + 180)
- **합계**: 2,490줄 (-738줄)

### Phase 5 완료 후

- 기존 파일: 1,360줄 → 1,324줄 (-36줄)
- 신규 모듈: 1,130줄
- **합계**: 2,454줄 (-774줄)

**최종**: 약 **1,770줄** (최적화 후)

---

## 💡 주요 개선 효과

### 코드 감소

- **총 감소**: 약 1,458줄 (45.2%)
- **중복 제거**: 약 2,544줄 (중복 코드 제거)
- **모듈화**: 1,130줄 (재사용 가능한 모듈)

### 유지보수성

- **단일 책임**: 각 모듈이 명확한 역할
- **재사용성**: 모듈을 여러 페이지에서 사용
- **테스트 용이성**: 모듈별 독립 테스트 가능

### 확장성

- **새 기능 추가**: 모듈 확장으로 간단히 추가
- **버그 수정**: 한 곳 수정으로 모든 페이지 반영
- **성능 최적화**: 모듈별 최적화 가능

---

## 📚 참고

- [개발 계획서](./phase7-9-8-review-issues-development-plan.md)
- [개발 진행 상황](./phase7-9-8-review-issues-development-progress.md)
