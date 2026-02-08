# Phase 7.8: 관리자 페이지 분리 테스트 체크리스트

## 테스트 목적

기존 `knowledge-admin.html`의 3개 탭을 독립 페이지로 분리한 후, 각 페이지의 기능이 정상적으로 작동하는지 확인

## 테스트 환경

- URL: http://localhost:8000
- 테스트 날짜: 2026-01-08

---

## 1. admin/labels.html - 라벨 관리 페이지

### 접근 확인

- [x] URL: `http://localhost:8000/admin/labels` 접근 가능 (백엔드 라우팅 확인됨: `@app.get("/admin/labels")`)
- [ ] 헤더가 정상적으로 표시됨 (좌측: 사용자 메뉴, 우측: 관리자 메뉴) - 브라우저 테스트 필요
- [x] 페이지 제목: "🏷️ 라벨 관리" (코드 확인: `initializeAdminPage({ title: "🏷️ 라벨 관리" })`)
- [x] 부제목: "라벨 생성 및 청크 라벨 관리" (코드 확인: `subtitle: "라벨 생성 및 청크 라벨 관리"`)

### 라벨 관리 기능

- [x] 라벨 생성 폼 표시 (코드 확인: HTML에 폼 존재)
- [x] 라벨 타입 선택 가능 (project_phase, role, domain, importance, keyword) (코드 확인: select 요소에 타입 옵션 존재)
- [ ] 라벨 생성 버튼 클릭 시 라벨 생성 - 브라우저 테스트 필요
- [x] 라벨 목록 테이블에 생성된 라벨 표시 (코드 확인: `displayLabels()` 함수 존재)
- [ ] 라벨 삭제 버튼 클릭 시 라벨 삭제 - 브라우저 테스트 필요

### 청크 라벨 관리 기능

- [x] 청크 검색 입력창 표시 (코드 확인: `id="chunk-search"` 입력창 존재)
- [x] 청크 목록 로드 및 표시 (코드 확인: `loadChunks()` 함수 존재)
- [ ] 청크 선택 시 청크 정보 표시 - 브라우저 테스트 필요
- [x] 선택된 청크의 현재 라벨 표시 (코드 확인: `displayChunkLabels()` 함수 존재)
- [x] 라벨 추가 드롭다운에 모든 라벨 표시 (코드 확인: `updateLabelSelect()` 함수 존재)
- [ ] 라벨 추가 버튼 클릭 시 청크에 라벨 추가 - 브라우저 테스트 필요
- [ ] 라벨 칩의 "×" 버튼 클릭 시 라벨 제거 - 브라우저 테스트 필요

### API 엔드포인트 확인

- [x] `GET /api/labels` - 라벨 목록 조회 (코드 확인: `@router.get("")` 존재)
- [x] `POST /api/labels` - 라벨 생성 (코드 확인: `@router.post("")` 존재)
- [x] `DELETE /api/labels/{id}` - 라벨 삭제 (코드 확인: `@router.delete("/{label_id}")` 존재)
- [x] `GET /api/knowledge/chunks?limit=100` - 청크 목록 조회 (코드 확인: `@router.get("/chunks")` 존재)
- [x] `GET /api/labels/chunks/{chunkId}/labels` - 청크의 라벨 조회 (코드 확인: `@router.get("/chunks/{chunk_id}/labels")` 존재)
- [x] `POST /api/labels/chunks/{chunkId}/labels/{labelId}` - 청크에 라벨 추가 (코드 확인: `@router.post("/chunks/{chunk_id}/labels/{label_id}")` 존재)
- [x] `DELETE /api/labels/chunks/{chunkId}/labels/{labelId}` - 청크에서 라벨 제거 (코드 확인: `@router.delete("/chunks/{chunk_id}/labels/{label_id}")` 존재)

---

## 2. admin/groups.html - 키워드 그룹 관리 페이지

### 접근 확인

- [x] URL: `http://localhost:8000/admin/groups` 접근 가능 (백엔드 라우팅 확인됨: `@app.get("/admin/groups")`)
- [ ] 헤더가 정상적으로 표시됨 - 브라우저 테스트 필요
- [x] 페이지 제목: "📦 키워드 그룹 관리" (코드 확인: `initializeAdminPage({ title: "📦 키워드 그룹 관리" })`)
- [x] 부제목: "키워드 그룹 생성 및 관리" (코드 확인: `subtitle: "키워드 그룹 생성 및 관리"`)

### 키워드 그룹 관리 기능

- [x] 검색 입력창 표시 (코드 확인: 검색 입력창 존재)
- [x] 좌측: 키워드 그룹 카드 리스트 표시 (코드 확인: `loadGroups()` 함수 및 카드 렌더링 로직 존재)
- [x] 우측: 키워드 목록 배지 형태로 표시 (코드 확인: `loadKeywords()` 함수 및 배지 렌더링 로직 존재)
- [ ] "+ 새 그룹" 버튼 클릭 시 모달 표시 - 브라우저 테스트 필요
- [x] 그룹 생성 모달에서 그룹 이름, 설명, 색상 입력 가능 (코드 확인: 모달 폼에 입력 필드 존재)
- [x] "💡 설명 기반 키워드 추천" 버튼 클릭 시 키워드 추천 (코드 확인: `suggestKeywordsFromDescription()` 함수 존재)
- [x] 추천된 키워드 칩 표시 및 개별 삭제 가능 (코드 확인: `displaySuggestedKeywords()` 함수 존재)
- [x] "전체삭제" 버튼으로 모든 추천 키워드 삭제 (코드 확인: `clearSuggestedKeywords()` 함수 존재)
- [ ] 그룹 생성 시 선택한 추천 키워드 자동 연결 - 브라우저 테스트 필요
- [ ] 그룹 카드의 ✏️ 버튼으로 그룹 수정 - 브라우저 테스트 필요
- [ ] 그룹 카드의 🗑️ 버튼으로 그룹 삭제 - 브라우저 테스트 필요

### 키워드 매칭 기능

- [x] 그룹 선택 시 키워드 목록이 "그룹 키워드" / "그룹 외 키워드"로 분류 표시 (코드 확인: `displayKeywords()` 함수에서 분류 로직 존재)
- [x] 그룹 선택 시 하단 요약 바 표시 (코드 확인: `updateSummaryBar()` 함수 존재)
- [ ] 키워드 배지 클릭 시 선택 상태 토글 - 브라우저 테스트 필요
- [x] 선택된 키워드가 요약 바에 표시 (코드 확인: `updateSummaryBar()` 함수에서 선택된 키워드 표시)
- [ ] "이 그룹에 연결" 버튼 클릭 시 선택한 키워드 그룹에 연결 - 브라우저 테스트 필요
- [x] "선택 취소" 버튼으로 선택 초기화 (코드 확인: `clearSelection()` 함수 존재)

### API 엔드포인트 확인

- [x] `GET /api/labels/groups` - 그룹 목록 조회 (코드 확인: `@router.get("/groups")` 존재)
- [x] `POST /api/labels/groups` - 그룹 생성 (코드 확인: `@router.post("/groups")` 존재)
- [x] `PATCH /api/labels/groups/{id}` - 그룹 수정 (코드 확인: `@router.patch("/groups/{group_id}")` 존재)
- [x] `DELETE /api/labels/groups/{id}` - 그룹 삭제 (코드 확인: `@router.delete("/groups/{group_id}")` 존재)
- [x] `GET /api/labels/groups/{id}/keywords` - 그룹의 키워드 조회 (코드 확인: `@router.get("/groups/{group_id}/keywords")` 존재)
- [x] `POST /api/labels/groups/{id}/keywords` - 그룹에 키워드 추가 (코드 확인: `@router.post("/groups/{group_id}/keywords")` 존재)
- [x] `GET /api/labels?label_type=keyword` - 키워드 목록 조회 (코드 확인: `@router.get("")` with `label_type` 파라미터 지원)
- [x] `POST /api/labels/groups/suggest-keywords` - 설명 기반 키워드 추천 (코드 확인: `@router.post("/groups/suggest-keywords")` 존재)

---

## 3. admin/approval.html - 청크 승인 센터 페이지

### 접근 확인

- [x] URL: `http://localhost:8000/admin/approval` 접근 가능 (백엔드 라우팅 확인됨: `@app.get("/admin/approval")`)
- [ ] 헤더가 정상적으로 표시됨 - 브라우저 테스트 필요
- [x] 페이지 제목: "✅ 청크 승인 센터" (코드 확인: `initializeAdminPage({ title: "✅ 청크 승인 센터" })`)
- [x] 부제목: "청크 승인 및 거절 관리" (코드 확인: `subtitle: "청크 승인 및 거절 관리"`)

### 상태 필터 기능

- [ ] "📝 대기 중 (Draft)" 버튼 클릭 시 draft 상태 청크 표시
- [ ] "✅ 승인됨 (Approved)" 버튼 클릭 시 approved 상태 청크 표시
- [ ] "❌ 거절됨 (Rejected)" 버튼 클릭 시 rejected 상태 청크 표시
- [ ] 필터 버튼 활성화 상태 표시

### 청크 승인/거절 기능

- [ ] 청크 카드 표시 (ID, 문서 ID, 인덱스, 내용, 상태)
- [ ] draft 상태 청크에 "✅ 승인" / "❌ 거절" 버튼 표시
- [ ] "✅ 승인" 버튼 클릭 시 청크 승인
- [ ] "❌ 거절" 버튼 클릭 시 거절 사유 입력 및 청크 거절
- [ ] "상세 보기" 버튼 클릭 시 청크 상세 모달 표시

### 청크 상세 모달 기능

- [ ] 청크 내용 표시
- [ ] 현재 라벨 표시
- [ ] AI 라벨 추천 표시 (있는 경우)
- [ ] AI 유사 청크 추천 표시 (있는 경우)
- [ ] 라벨 추천 "적용" 버튼 클릭 시 라벨 적용
- [ ] 유사 청크 클릭 시 해당 청크 상세 보기
- [ ] draft 상태 청크에 "✅ 승인" / "❌ 거절" 버튼 표시
- [ ] "닫기" 버튼으로 모달 닫기

### API 엔드포인트 확인

- [x] `GET /api/approval/chunks/pending?status={status}&limit=50` - 승인 대기 청크 조회 (코드 확인: `@router.get("/pending")` 존재)
- [x] `POST /api/approval/chunks/{id}/approve` - 청크 승인 (코드 확인: `@router.post("/{chunk_id}/approve")` 존재)
- [x] `POST /api/approval/chunks/{id}/reject` - 청크 거절 (코드 확인: `@router.post("/{chunk_id}/reject")` 존재)
- [x] `GET /api/knowledge/chunks/{id}` - 청크 상세 조회 (코드 확인: `@router.get("/chunks/{chunk_id}")` 존재)
- [x] `GET /api/knowledge/labels/suggest?chunk_id={id}` - 라벨 추천 (코드 확인: `@router.get("/labels/suggest")` 존재)
- [x] `GET /api/knowledge/relations/suggest?chunk_id={id}&limit=5` - 관계 추천 (코드 확인: `@router.get("/relations/suggest")` 존재)
- [x] `POST /api/knowledge/labels/suggest/{chunkId}/apply/{labelId}?confidence={confidence}` - 라벨 추천 적용 (코드 확인: `@router.post("/labels/suggest/{chunk_id}/apply/{label_id}")` 존재)

---

## 4. 헤더 메뉴 확인

### 사용자 메뉴 (좌측)

- [x] 대시보드 (코드 확인: `USER_MENU`에 `/dashboard` 존재)
- [x] 검색 (코드 확인: `USER_MENU`에 `/search` 존재)
- [x] 지식 구조 (코드 확인: `USER_MENU`에 `/knowledge` 존재)
- [x] Reasoning (코드 확인: `USER_MENU`에 `/reason` 존재)
- [x] AI 질의 (코드 확인: `USER_MENU`에 `/ask` 존재)
- [x] 로그 (코드 확인: `USER_MENU`에 `/logs` 존재)

### 관리자 메뉴 (우측)

- [x] ⚙️ 🏷️ 라벨 관리 (`/admin/labels`) (코드 확인: `ADMIN_MENU`에 정의됨)
- [x] ⚙️ 📦 키워드 그룹 (`/admin/groups`) (코드 확인: `ADMIN_MENU`에 정의됨)
- [x] ⚙️ ✅ 청크 승인 (`/admin/approval`) (코드 확인: `ADMIN_MENU`에 정의됨)

### 메뉴 구분

- [x] 좌측과 우측이 구분선으로 분리됨 (코드 확인: `header nav`에 `user-menu`와 `admin-menu` div로 구분)
- [x] 관리자 메뉴 앞에 ⚙️ 아이콘 표시 (코드 확인: `adminIcon: '⚙️'` 설정됨)
- [x] 현재 페이지의 메뉴가 활성화 상태로 표시 (코드 확인: `isActive` 로직으로 `active` 클래스 적용)

---

## 5. 기존 knowledge-admin.html 비교

### 기능 비교

- [x] 라벨 관리 기능 - `admin/labels.html`에 포함
- [x] 키워드 그룹 관리 기능 - `admin/groups.html`에 포함
- [x] 청크 승인 센터 기능 - `admin/approval.html`에 포함

### 누락 확인

- [x] 탭 네비게이션 (기존에는 탭으로 전환, 새로는 독립 페이지) (확인됨: 각각 독립 페이지로 분리)
- [x] 공통 CSS/JS 분리 확인 (`admin-styles.css`, `admin-common.js`) (코드 확인: `web/public/css/admin-styles.css`, `web/public/js/admin-common.js` 존재)

---

## 발견된 문제점

### 문제 1: (없음)

- 설명:
- 해결 방법:

---

## 테스트 결과 요약

### 코드 레벨 확인 완료 항목

- [x] admin/labels.html - HTML 구조, JavaScript 함수, API 엔드포인트 확인 완료
- [x] admin/groups.html - HTML 구조, JavaScript 함수, API 엔드포인트 확인 완료
- [x] admin/approval.html - HTML 구조, JavaScript 함수, API 엔드포인트 확인 완료
- [x] 헤더 메뉴 - 코드 레벨에서 구조 및 로직 확인 완료
- [x] 공통 CSS/JS 파일 - `admin-styles.css`, `admin-common.js` 존재 확인
- [x] 백엔드 라우팅 - 모든 `/admin/*` 경로 라우팅 확인 완료
- [x] API 엔드포인트 - 모든 필요한 API 엔드포인트 존재 확인 완료

### 브라우저 테스트 필요 항목

다음 항목들은 실제 브라우저에서 테스트가 필요합니다:

**admin/labels.html:**

- 헤더 표시 확인
- 라벨 생성/삭제 기능 동작 확인
- 청크 선택 및 라벨 추가/제거 기능 동작 확인

**admin/groups.html:**

- 헤더 표시 확인
- 그룹 생성 모달 동작 확인
- 키워드 추천 기능 동작 확인
- 그룹 수정/삭제 기능 동작 확인
- 키워드 매칭 기능 동작 확인

**admin/approval.html:**

- 헤더 표시 확인
- 상태 필터 동작 확인
- 청크 승인/거절 기능 동작 확인
- 청크 상세 모달 동작 확인

### 실패 항목

- (없음)

### 개선 필요 항목

- (없음)

---

## 다음 단계

1. ✅ 코드 레벨 확인 완료 (2026-01-08)

   - HTML 파일 구조 확인
   - JavaScript 함수 존재 확인
   - 백엔드 API 엔드포인트 확인
   - 공통 CSS/JS 파일 확인
   - 헤더 컴포넌트 구조 확인

2. 🔄 브라우저에서 실제 테스트 수행 (대기 중)

   - 서버 실행: `python scripts/start_server.py` 또는 `uvicorn backend.main:app --reload`
   - 각 페이지 접근 및 기능 테스트
   - 브라우저 개발자 도구로 네트워크 요청 확인

3. 발견된 문제점 수정 (대기 중)

4. 최종 검증 후 Git 커밋 (대기 중)

---

## 코드 레벨 확인 상세 결과

### 확인된 파일 구조

- ✅ `web/src/pages/admin/labels.html` - 존재 및 구조 확인
- ✅ `web/src/pages/admin/groups.html` - 존재 및 구조 확인
- ✅ `web/src/pages/admin/approval.html` - 존재 및 구조 확인
- ✅ `web/public/css/admin-styles.css` - 존재 확인
- ✅ `web/public/js/admin-common.js` - 존재 및 함수 확인

### 확인된 백엔드 라우팅

- ✅ `GET /admin/labels` - `backend/main.py:162`
- ✅ `GET /admin/groups` - `backend/main.py:175`
- ✅ `GET /admin/approval` - `backend/main.py:188`

### 확인된 API 엔드포인트

모든 필요한 API 엔드포인트가 `backend/routers/labels.py`, `backend/routers/approval.py`, `backend/routers/knowledge.py`에 존재함을 확인했습니다.
