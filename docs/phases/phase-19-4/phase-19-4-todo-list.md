# Phase 19-4 체크리스트: 청크 관리 통합 1단계 (탭 기반)

> **상태**: DRAFT
> **작성일**: 2026-02-22
> **계획서**: [phase-19-4-plan.md](phase-19-4-plan.md)

---

## Task 19-4-1: 통합 페이지 스캐폴딩 [FS]

- [ ] BE: `main.py` _HTML_ROUTES에 `/admin/knowledge-workflow` 라우트 등록
- [ ] FE: `web/src/pages/admin/knowledge-workflow.html` 신규 생성
  - [ ] 탭 바 (생성 / 승인 / 관리) HTML 구조
  - [ ] 3개 탭 콘텐츠 영역 (div#tab-create, #tab-approval, #tab-manage)
  - [ ] 공통 스크립트 로드 (admin-common, utils, pagination-component 등)
  - [ ] 기존 API 파일 로드 (chunk-approval-api, label-manager-api)
  - [ ] 기존 클래스 파일 로드 (chunk-approval-manager, label-manager)
  - [ ] 신규 JS 파일 로드 (knowledge-workflow, kw-tab-create, kw-tab-approval, kw-tab-manage)
- [ ] FE: `web/public/js/admin/knowledge-workflow.js` 신규 생성
  - [ ] KnowledgeWorkflow 클래스 (상태 관리, 탭 전환, URL 동기화)
  - [ ] DOMContentLoaded 초기화
  - [ ] `history.pushState` + `popstate` 이벤트 핸들링
- [ ] FE: `web/public/css/admin/admin-knowledge-workflow.css` 신규 생성
  - [ ] 탭 바 스타일
  - [ ] 탭 콘텐츠 영역 공통 레이아웃
- [ ] 동작 확인: 페이지 접근, 탭 전환, URL 쿼리 업데이트, 뒤로가기

---

## Task 19-4-2: 생성 탭 통합 [FE]

- [ ] FE: `web/public/js/admin/kw-tab-create.js` 신규 생성
  - [ ] CreateTab 클래스 (init, activate, deactivate, refresh 인터페이스)
  - [ ] 파일 목록 로드 + 페이지네이션
  - [ ] 파일 선택 -> 내용 표시
  - [ ] 분할 방식 선택 + 자동 생성
  - [ ] 2단계: 분할 청크 목록 (전체선택/해제, 병합)
  - [ ] 3단계: 등록 방식 (새문서/기존문서) + 등록
- [ ] FE: "빠른 승인" 버튼 추가
  - [ ] 등록 후 `approveChunkApi()` 자동 호출
- [ ] FE: 완료 시 탭 전환 이벤트 발행
  - [ ] `KnowledgeWorkflow.notifyTabChange()` 호출
  - [ ] 승인 탭 자동 전환 (옵션)
- [ ] HTML: `knowledge-workflow.html` 내 #tab-create 영역에 생성 탭 마크업 추가
- [ ] 동작 확인: 파일선택 -> 분할 -> 등록 -> 빠른승인 -> 탭전환

---

## Task 19-4-3: 승인 탭 통합 [FE]

- [ ] FE: `web/public/js/admin/kw-tab-approval.js` 신규 생성
  - [ ] ApprovalTab 클래스 (init, activate, deactivate, refresh)
  - [ ] 내부에서 ChunkApprovalManager 인스턴스 생성
  - [ ] DOM ID 매핑 (통합 페이지용 ID로 config 전달)
- [ ] FE: 다중 선택 기능 추가
  - [ ] 청크 카드에 체크박스 추가
  - [ ] 선택 카운트 표시
  - [ ] "선택 일괄 승인" 버튼
- [ ] FE: "전체 승인+라벨" 버튼 추가
  - [ ] 전체 대기중 승인 -> 관리 탭 자동 전환
- [ ] HTML: `knowledge-workflow.html` 내 #tab-approval 영역에 승인 탭 마크업 추가
- [ ] 동작 확인: 상태필터, 목록, 상세보기, 다중선택, 일괄승인, AI추천

---

## Task 19-4-4: 관리 탭 통합 [FE]

- [ ] FE: `web/public/js/admin/kw-tab-manage.js` 신규 생성
  - [ ] ManageTab 클래스 (init, activate, deactivate, refresh)
  - [ ] 내부에서 LabelManager 인스턴스 생성
  - [ ] DOM ID 매핑 (통합 페이지용 ID로 config 전달)
- [ ] FE: 다중 선택 기능 추가
  - [ ] 청크 목록에 체크박스 추가
  - [ ] 선택 카운트 표시
- [ ] FE: 일괄 라벨 추가/제거
  - [ ] 선택한 복수 청크에 동시 라벨 추가 (FE 루프)
  - [ ] 선택한 복수 청크에서 동시 라벨 제거 (FE 루프)
  - [ ] 진행 상태 표시 (N/M 처리 중)
- [ ] HTML: `knowledge-workflow.html` 내 #tab-manage 영역에 관리 탭 마크업 추가
- [ ] 동작 확인: 청크목록, 라벨피커, 다중선택, 일괄라벨추가/제거, AI추천

---

## Task 19-4-5: 네비게이션 + 리다이렉트 [FS]

- [ ] FE: `header-component.js` ADMIN_MENU 업데이트
  - [ ] 기존 3개 메뉴 제거 (chunk-create, approval, chunk-labels)
  - [ ] 신규 메뉴 추가: `/admin/knowledge-workflow` "지식 워크플로우"
- [ ] BE: `main.py`에 기존 3개 URL 리다이렉트 등록
  - [ ] `/admin/chunk-create` -> `/admin/knowledge-workflow?tab=create` (302)
  - [ ] `/admin/approval` -> `/admin/knowledge-workflow?tab=approval` (302)
  - [ ] `/admin/chunk-labels` -> `/admin/knowledge-workflow?tab=manage` (302)
- [ ] 회귀 테스트
  - [ ] LNB 메뉴 정상 표시
  - [ ] 기존 URL 리다이렉트 동작
  - [ ] 리다이렉트 후 올바른 탭 활성화
  - [ ] LNB active 상태 정확

---

## 품질 기준

- [ ] 모든 신규 JS 파일 500줄 이하 (REFACTOR-3)
- [ ] innerHTML 사용 시 escapeHtml/esc 적용 (XSS 방지)
- [ ] ESM import/export 또는 기존 전역 함수 패턴 일관성
- [ ] CDN 미사용
- [ ] 콘솔 에러 0건
- [ ] 기존 3페이지 기능 100% 동작 (기능 누락 없음)

---

**문서 관리**: Phase 19-4, 작성일 2026-02-22
