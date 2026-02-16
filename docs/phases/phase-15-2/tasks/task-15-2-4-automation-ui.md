# Task 15-2-4: AI 자동화 페이지 구현

**우선순위**: 15-2 내 3순위
**의존성**: 15-2-1, 15-2-3
**담당 팀원**: frontend-dev
**상태**: 대기

---

## §1. 개요

/admin/ai-automation 페이지를 3-Column 레이아웃으로 구현한다. 문서 선택, 워크플로우 실행/진행, 실시간 결과 표시 기능을 제공한다.

## §2. 파일 변경 계획

| 파일 | 유형 | 변경 내용 |
|------|------|----------|
| `web/src/pages/admin/ai-automation.html` | 신규 | AI 자동화 HTML 페이지 |
| `web/public/js/admin/ai-automation.js` | 신규 | AI 자동화 JS 모듈 |
| `web/public/css/admin/admin-ai-automation.css` | 신규 | AI 자동화 스타일 |

## §3. 작업 체크리스트 (Done Definition)

### HTML 페이지
- [ ] layout-component, header-component 포함
- [ ] 3-Column 레이아웃:
  - 좌측: 문서 선택 패널 (폴더 파일 목록, 체크박스 선택)
  - 중앙: 워크플로우 실행 패널 (실행 버튼, Progress Bar, 6단계 표시)
  - 우측: 결과 패널 (생성된 청크/라벨 목록, 승인/거절)
- [ ] `<script type="module">` 사용

### JS 모듈
- [ ] ESM 패턴
- [ ] 문서 선택: GET /api/knowledge/folder-files 호출 → 체크박스 목록
- [ ] 실행: POST /api/automation/run-full 호출 (선택된 document_ids + auto_approve 옵션)
- [ ] SSE 연동: EventSource로 /api/automation/progress/{task_id} 구독
  - progress 이벤트 → Progress Bar 업데이트
  - stage 이벤트 → 현재 단계 표시
  - complete 이벤트 → 결과 표시
  - error 이벤트 → 에러 메시지
- [ ] 취소: POST /api/automation/cancel/{task_id}
- [ ] 승인: POST /api/automation/approve-pending
- [ ] 태스크 목록: GET /api/automation/tasks → 이전 실행 이력
- [ ] innerHTML 사용 시 esc() 적용
- [ ] API 에러 핸들링 (try-catch + 사용자 메시지)

### CSS
- [ ] 3-Column 반응형 레이아웃 (768px 이하 1-Column)
- [ ] Progress Bar 스타일 (6단계 구간별 색상)
- [ ] 결과 카드 스타일 (청크/라벨 배지)
- [ ] 기존 admin-styles.css와 일관성

### 통합
- [ ] 페이지 로드 시 콘솔 에러 없음
- [ ] 기존 LNB·레이아웃 스타일과 일관성

## §4. 참조

- `web/src/pages/admin/knowledge-files.html` — 기존 Admin 페이지 구조
- `web/public/js/admin/knowledge-files.js` — Admin JS 패턴
- `web/public/css/admin/admin-knowledge-files.css` — Admin CSS 패턴
