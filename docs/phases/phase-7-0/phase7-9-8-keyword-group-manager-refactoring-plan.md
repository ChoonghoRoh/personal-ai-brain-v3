# Phase 7.9.8: keyword-group-manager.js 기능별 파일 분기 계획

**작성일**: 2026-01-10  
**대상 파일**: `web/public/js/keyword-group-manager.js` (1,108줄)  
**목적**: 기능별 파일 분기로 유지보수성 강화

---

## 📊 현재 상태 분석

### 파일 구조
- **총 줄 수**: 1,108줄
- **클래스**: `KeywordGroupManager`
- **주요 기능**: 
  1. 그룹 CRUD (생성, 읽기, 수정, 삭제)
  2. 키워드 매칭 (선택, 연결, 제거)
  3. 키워드 추천 (설명 기반)
  4. UI 업데이트 (매칭 UI, 선택 버튼)
  5. 검색 기능

### 사용 위치
- **HTML 파일**:
  - `web/src/pages/admin/groups.html`
  - `web/src/pages/knowledge-admin.html`
- **JavaScript 파일**:
  - `web/public/js/admin-groups.js` (window.groupManager)
  - `web/public/js/knowledge-admin.js` (groupsTabManager)

---

## 🎯 분기 계획

### Phase 1: 그룹 CRUD 모듈
**파일**: `keyword-group-crud.js`
- **기능**:
  - `loadGroups()` - 그룹 목록 로드
  - `createGroupCard()` - 그룹 카드 생성
  - `loadGroupKeywordsCount()` - 그룹 키워드 수 로드
  - `createGroup()` - 그룹 생성
  - `updateGroup()` - 그룹 수정
  - `deleteGroup()` - 그룹 삭제
  - `showCreateGroupModal()` - 그룹 생성 모달
  - `showEditGroupModal()` - 그룹 수정 모달
  - `closeCreateGroupModal()` - 모달 닫기
  - `handleCreateGroup()` - 그룹 생성/수정 처리
- **예상 줄 수**: 약 350줄

### Phase 2: 키워드 매칭 모듈
**파일**: `keyword-group-matching.js`
- **기능**:
  - `loadKeywords()` - 키워드 목록 로드
  - `createKeywordSection()` - 키워드 섹션 생성
  - `createKeywordBadge()` - 키워드 배지 생성
  - `selectGroup()` - 그룹 선택
  - `toggleKeywordSelection()` - 키워드 선택 토글
  - `toggleRemoveKeywordSelection()` - 키워드 제외 선택 토글
  - `toggleKeywordSelectionForGroupCheck()` - 그룹 미선택 시 키워드 선택
  - `selectAllKeywordsInSection()` - 섹션 전체 선택
  - `applyGroupKeywords()` - 그룹에 키워드 연결
  - `removeGroupKeywords()` - 그룹에서 키워드 제거
  - `addKeywordsToGroup()` - 그룹에 키워드 추가
- **예상 줄 수**: 약 400줄

### Phase 3: UI 업데이트 모듈
**파일**: `keyword-group-ui.js`
- **기능**:
  - `updateMatchingUI()` - 매칭 UI 업데이트
  - `updateSelectAllButtons()` - 전체 선택 버튼 업데이트
  - `clearSelection()` - 선택 초기화
- **예상 줄 수**: 약 150줄

### Phase 4: 키워드 추천 모듈
**파일**: `keyword-group-suggestion.js`
- **기능**:
  - `suggestKeywordsFromDescription()` - 설명 기반 키워드 추천
  - `createSuggestedKeywordChip()` - 추천 키워드 칩 생성
  - `toggleSuggestedKeyword()` - 추천 키워드 토글
  - `removeSuggestedKeyword()` - 추천 키워드 제거
  - `clearSuggestedKeywords()` - 추천 키워드 초기화
- **예상 줄 수**: 약 200줄

### Phase 5: 검색 모듈
**파일**: `keyword-group-search.js`
- **기능**:
  - `searchGroupsAndKeywords()` - 그룹/키워드 검색
- **예상 줄 수**: 약 10줄

### Phase 6: 메인 클래스
**파일**: `keyword-group-manager.js` (리팩토링 후)
- **기능**:
  - `KeywordGroupManager` 클래스 (모듈들을 조합)
  - 생성자 및 설정 관리
- **예상 줄 수**: 약 100줄

---

## 📋 영향도 검사

### HTML 파일 영향도

#### 1. `web/src/pages/admin/groups.html`
**사용 함수**:
- `searchGroupsAndKeywords()` (onkeyup)
- `showCreateGroupModal()` (onclick)
- `closeCreateGroupModal()` (onclick)
- `handleCreateGroup()` (onsubmit)
- `suggestKeywordsFromDescription()` (onclick)
- `clearSuggestedKeywords()` (onclick)
- `applyGroupKeywords()` (onclick)
- `removeGroupKeywords()` (onclick)
- `clearSelection()` (onclick)
- `window.groupManager.showEditGroupModal()` (onclick - 그룹 카드 내부)
- `window.groupManager.deleteGroup()` (onclick - 그룹 카드 내부)

**영향도**: 🔴 높음
- **변경 필요**: 없음 (전역 함수 래퍼 유지)
- **테스트 필요**: 모든 기능 테스트

#### 2. `web/src/pages/knowledge-admin.html`
**사용 함수**:
- `searchGroupsAndKeywords()` (onkeyup)
- `showCreateGroupModal()` (onclick)
- `applyGroupKeywords()` (onclick)
- `clearSelection()` (onclick)
- `suggestKeywordsFromDescription()` (onclick)
- `clearSuggestedKeywords()` (onclick)

**영향도**: 🔴 높음
- **변경 필요**: 없음 (전역 함수 래퍼 유지)
- **테스트 필요**: 모든 기능 테스트

### JavaScript 파일 영향도

#### 1. `web/public/js/admin-groups.js`
**사용**:
- `new KeywordGroupManager()` (인스턴스 생성)
- `window.groupManager` (전역 노출)

**영향도**: 🟡 중간
- **변경 필요**: import 문 추가 (모듈 로드 순서)
- **테스트 필요**: 인스턴스 생성 및 초기화

#### 2. `web/public/js/knowledge-admin.js`
**사용**:
- `new KeywordGroupManager()` (인스턴스 생성)
- `window.groupsTabManager` (전역 노출)

**영향도**: 🟡 중간
- **변경 필요**: import 문 추가 (모듈 로드 순서)
- **테스트 필요**: 인스턴스 생성 및 초기화

---

## 🔄 분기 전략

### 옵션 1: ES6 모듈 방식 (권장)
- 각 기능을 별도 모듈로 분리
- `keyword-group-manager.js`에서 import하여 조합
- **장점**: 명확한 의존성, 트리 쉐이킹 가능
- **단점**: 브라우저 호환성 (현재 프로젝트는 모던 브라우저 지원)

### 옵션 2: 전역 네임스페이스 방식
- 각 기능을 별도 파일로 분리하되 전역 네임스페이스 사용
- `keyword-group-manager.js`에서 조합
- **장점**: 기존 코드와 호환성 유지
- **단점**: 전역 네임스페이스 오염

### 옵션 3: 하이브리드 방식 (권장)
- 각 기능을 별도 클래스/객체로 분리
- `KeywordGroupManager`에서 인스턴스로 조합
- **장점**: 명확한 책임 분리, 기존 코드 호환성 유지
- **단점**: 약간의 오버헤드

---

## 📝 상세 분기 계획

### Phase 1: 그룹 CRUD 모듈 생성
**파일**: `keyword-group-crud.js`
```javascript
class KeywordGroupCRUD {
  constructor(manager) {
    this.manager = manager; // KeywordGroupManager 인스턴스 참조
  }
  
  async loadGroups() { ... }
  createGroupCard(group) { ... }
  async loadGroupKeywordsCount(groupId) { ... }
  async createGroup(name, description, color) { ... }
  async updateGroup(groupId, name, description, color) { ... }
  async deleteGroup(groupId) { ... }
  showCreateGroupModal() { ... }
  async showEditGroupModal(groupId) { ... }
  closeCreateGroupModal() { ... }
  async handleCreateGroup(event) { ... }
}
```

### Phase 2: 키워드 매칭 모듈 생성
**파일**: `keyword-group-matching.js`
```javascript
class KeywordGroupMatching {
  constructor(manager) {
    this.manager = manager;
  }
  
  async loadKeywords() { ... }
  createKeywordSection(sectionType, keywords, isGroupSection) { ... }
  createKeywordBadge(keyword, isInGroup) { ... }
  selectGroup(groupId) { ... }
  toggleKeywordSelection(keywordId) { ... }
  toggleRemoveKeywordSelection(keywordId) { ... }
  toggleKeywordSelectionForGroupCheck(keywordId) { ... }
  selectAllKeywordsInSection(isGroupSection) { ... }
  async applyGroupKeywords() { ... }
  async removeGroupKeywords() { ... }
  async addKeywordsToGroup(groupId, keywordNames) { ... }
}
```

### Phase 3: UI 업데이트 모듈 생성
**파일**: `keyword-group-ui.js`
```javascript
class KeywordGroupUI {
  constructor(manager) {
    this.manager = manager;
  }
  
  updateMatchingUI() { ... }
  updateSelectAllButtons() { ... }
  clearSelection() { ... }
}
```

### Phase 4: 키워드 추천 모듈 생성
**파일**: `keyword-group-suggestion.js`
```javascript
class KeywordGroupSuggestion {
  constructor(manager) {
    this.manager = manager;
  }
  
  async suggestKeywordsFromDescription() { ... }
  createSuggestedKeywordChip(keyword, isSimilar) { ... }
  toggleSuggestedKeyword(keyword, chip) { ... }
  removeSuggestedKeyword(keyword, chip) { ... }
  clearSuggestedKeywords() { ... }
}
```

### Phase 5: 검색 모듈 생성
**파일**: `keyword-group-search.js`
```javascript
class KeywordGroupSearch {
  constructor(manager) {
    this.manager = manager;
  }
  
  searchGroupsAndKeywords() { ... }
}
```

### Phase 6: 메인 클래스 리팩토링
**파일**: `keyword-group-manager.js` (리팩토링 후)
```javascript
class KeywordGroupManager {
  constructor(config = {}) {
    // 모듈 인스턴스 생성
    this.crud = new KeywordGroupCRUD(this);
    this.matching = new KeywordGroupMatching(this);
    this.ui = new KeywordGroupUI(this);
    this.suggestion = new KeywordGroupSuggestion(this);
    this.search = new KeywordGroupSearch(this);
    
    // 메서드 위임
    this.loadGroups = () => this.crud.loadGroups();
    this.createGroup = (...args) => this.crud.createGroup(...args);
    // ... 기타 메서드 위임
  }
}
```

---

## ⚠️ 주의사항

### 1. 순환 참조 방지
- 모듈 간 순환 참조가 발생하지 않도록 주의
- `manager` 인스턴스를 통해 접근

### 2. 상태 공유
- 상태는 `KeywordGroupManager`에서 관리
- 모듈은 `this.manager`를 통해 상태 접근

### 3. 하위 호환성
- 기존 전역 함수 래퍼 유지
- HTML에서 호출하는 함수명 변경 없음

### 4. 테스트
- 각 모듈별 단위 테스트
- 통합 테스트 (전체 기능)
- 브라우저 호환성 테스트

---

## 📊 예상 결과

### 파일 구조
```
web/public/js/
├── keyword-group-manager.js (100줄) - 메인 클래스
├── keyword-group-crud.js (350줄) - 그룹 CRUD
├── keyword-group-matching.js (400줄) - 키워드 매칭
├── keyword-group-ui.js (150줄) - UI 업데이트
├── keyword-group-suggestion.js (200줄) - 키워드 추천
└── keyword-group-search.js (10줄) - 검색
```

### 개선 효과
- **유지보수성**: 기능별 파일 분리로 수정 범위 명확화
- **가독성**: 각 파일이 단일 책임을 가짐
- **테스트 용이성**: 모듈별 독립 테스트 가능
- **확장성**: 새로운 기능 추가 시 해당 모듈만 수정

---

## 🚀 실행 계획

### Step 1: 영향도 검사 완료 ✅
- HTML 파일 사용 함수 확인
- JavaScript 파일 사용 패턴 확인

### Step 2: 분기 계획 수립 완료 ✅
- 기능별 모듈 분리 계획
- 파일 구조 설계

### Step 3: 개발 진행 (대기)
- 사용자 확인 후 진행
- 단계별 테스트 및 문서화

---

## 📝 다음 단계

1. **사용자 확인**: 분기 계획 검토 및 승인
2. **Phase 1 시작**: 그룹 CRUD 모듈 생성
3. **단계별 테스트**: 각 Phase 완료 후 테스트
4. **문서화**: 각 Phase 완료 보고서 작성

---

## ❓ 확인 사항

- [ ] 분기 계획 승인
- [ ] 모듈 구조 방식 선택 (옵션 3 권장)
- [ ] 진행 시작 여부 확인
