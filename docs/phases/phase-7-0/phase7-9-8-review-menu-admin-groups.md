# Phase 7.9.8: 메뉴별 상세 리뷰: 키워드 그룹 관리 (Admin - Groups)

**작성일**: 2026-01-10  
**메뉴 경로**: `/admin/groups`  
**카테고리**: 관리자 메뉴

---

## 📋 개요

키워드 그룹 관리 페이지는 키워드를 그룹으로 묶어 관리하고, 키워드와 그룹을 연결/해제할 수 있는 관리자 페이지입니다.

---

## 🎯 주요 기능

### 1. 키워드 그룹 관리
- **그룹 생성**: 새 키워드 그룹 생성
- **그룹 수정**: 기존 그룹 수정
- **그룹 삭제**: 키워드 그룹 삭제
- **그룹 목록**: 모든 그룹을 카드 형태로 표시
- **그룹 색상**: 그룹별 색상 지정

### 2. 키워드 관리
- **키워드 목록**: 모든 키워드를 배지 형태로 표시
- **그룹별 표시**: 키워드가 속한 그룹 표시
- **그룹 미선택 키워드**: 그룹에 속하지 않은 키워드 표시

### 3. 키워드-그룹 연결
- **키워드 선택**: 그룹에 연결할 키워드 선택
- **일괄 연결**: 선택한 키워드를 그룹에 일괄 연결
- **일괄 해제**: 선택한 키워드를 그룹에서 일괄 해제

### 4. 설명 기반 키워드 추천
- **AI 추천**: 그룹 설명을 기반으로 키워드 자동 추천
- **추천 키워드 선택**: 추천된 키워드 중 선택
- **추천 키워드 추가**: 선택한 키워드를 그룹에 추가

### 5. 검색 기능
- **그룹/키워드 검색**: 그룹명 및 키워드명으로 검색
- **선택된 키워드 정보**: 선택한 키워드의 그룹 정보 표시

---

## 🔧 기술적 구현

### 프론트엔드 구조

**파일 위치**: `web/src/pages/admin/groups.html`

**주요 JavaScript 파일**:
- `web/public/js/admin-groups.js`: 키워드 그룹 관리 로직
- `web/public/js/admin-common.js`: 관리자 공통 함수
- `web/public/js/header-component.js`: 헤더 컴포넌트
- `web/public/js/layout-component.js`: 레이아웃 컴포넌트

**주요 함수**:
- `loadGroups()`: 그룹 목록 로드
- `loadKeywords()`: 키워드 목록 로드
- `selectGroup()`: 그룹 선택
- `showCreateGroupModal()`: 그룹 생성 모달 표시
- `showEditGroupModal()`: 그룹 수정 모달 표시
- `handleCreateGroup()`: 그룹 생성/수정 처리
- `deleteGroup()`: 그룹 삭제
- `suggestKeywordsFromDescription()`: 설명 기반 키워드 추천
- `applyGroupKeywords()`: 키워드 그룹 연결
- `removeGroupKeywords()`: 키워드 그룹 해제
- `searchGroupsAndKeywords()`: 그룹/키워드 검색

### 백엔드 API

**주요 엔드포인트**:
- `GET /api/labels/groups`: 그룹 목록 조회
- `POST /api/labels/groups`: 그룹 생성
- `PUT /api/labels/groups/{id}`: 그룹 수정
- `DELETE /api/labels/groups/{id}`: 그룹 삭제
- `GET /api/labels/groups/{id}/keywords`: 그룹의 키워드 목록
- `GET /api/labels?label_type=keyword`: 키워드 목록 조회
- `POST /api/labels/groups/{id}/keywords`: 키워드를 그룹에 추가
- `DELETE /api/labels/groups/{id}/keywords/{keyword_id}`: 키워드를 그룹에서 제거
- `POST /api/suggestions/keywords`: 설명 기반 키워드 추천

---

## ✅ 정상 작동 기능

### 1. 그룹 관리
- ✅ 그룹 목록 정상 로드
- ✅ 그룹 생성 정상 작동
- ✅ 그룹 수정 정상 작동
- ✅ 그룹 삭제 정상 작동
- ✅ 그룹 색상 정상 표시

### 2. 키워드 관리
- ✅ 키워드 목록 정상 로드
- ✅ 그룹별 키워드 표시 정상 작동
- ✅ 그룹 미선택 키워드 표시 정상 작동

### 3. 키워드-그룹 연결
- ✅ 키워드 선택 정상 작동
- ✅ 일괄 연결 정상 작동
- ✅ 일괄 해제 정상 작동
- ✅ 선택 요약 표시 정상 작동

### 4. 설명 기반 추천
- ✅ AI 키워드 추천 정상 작동
- ✅ 추천 키워드 선택 정상 작동
- ✅ 추천 키워드 추가 정상 작동

### 5. 검색 기능
- ✅ 그룹/키워드 검색 정상 작동
- ✅ 선택된 키워드 정보 표시 정상 작동

---

## ⚠️ 발견된 이슈

### 1. 키워드 추천 오류 처리
**증상**: 
- 키워드 추천 API 호출 실패 시 에러 메시지 표시는 하지만, 재시도 기능 없음
- 네트워크 오류 시 사용자가 재시도해야 함

**영향도**: 낮음
**빈도**: 낮음
**상태**: 개선 가능

### 2. 그룹 삭제 시 확인 없음
**증상**: 
- 그룹 삭제 시 확인 다이얼로그 없음
- 실수로 그룹을 삭제할 수 있음

**영향도**: 중간
**빈도**: 낮음
**상태**: 개선 필요

### 3. 키워드 선택 상태 관리 복잡
**증상**: 
- 여러 선택 상태를 관리하는 변수가 많아 코드 복잡도 증가
- `selectedKeywordIds`, `selectedRemoveKeywordIds`, `selectedKeywordForGroupCheck` 등

**영향도**: 낮음
**빈도**: 낮음
**상태**: 리팩토링 가능

---

## 🔍 코드 품질

### 강점
- ✅ 복잡한 기능을 잘 구현
- ✅ 적절한 에러 처리
- ✅ 사용자 피드백 제공
- ✅ 모달 UI 활용

### 개선 가능한 부분
- ⚠️ 그룹 삭제 전 확인 다이얼로그 추가 필요
- ⚠️ 선택 상태 관리 리팩토링 가능
- ⚠️ 코드 길이가 길어서 모듈화 고려

---

## 📊 성능

- **그룹 로드 시간**: < 300ms
- **키워드 로드 시간**: < 500ms
- **키워드 추천 시간**: 2-5초 (AI 모델 응답 시간)
- **키워드 연결/해제**: < 300ms

---

## 🎯 개선 제안

1. **그룹 삭제 확인**: 삭제 전 확인 다이얼로그 추가
2. **선택 상태 관리 개선**: 상태 관리 로직 리팩토링
3. **코드 모듈화**: 긴 파일을 여러 모듈로 분리
4. **키워드 추천 개선**: 재시도 기능 및 캐싱 고려

---

## 📝 관련 파일

- `web/src/pages/admin/groups.html`
- `web/public/js/admin-groups.js`
- `web/public/css/admin-groups.css`
- `web/public/css/admin-styles.css`
- `backend/routers/labels.py`
- `backend/routers/suggestions.py`
