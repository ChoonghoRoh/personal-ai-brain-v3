# Task 17-1-2: [FE] 3단 레이아웃 HTML 구조

**우선순위**: 17-1 내 2순위
**예상 작업량**: 큼
**의존성**: 17-1-1 (API 응답 형식 확정)
**담당 팀원**: frontend-dev
**상태**: 완료

---

## §1. 개요

groups.html을 전면 개편하여 2단(목록+모달) → 3단(목록+상세+키워드) 레이아웃으로 전환한다. 기존 모달 HTML을 완전 제거하고, 상단에 "새 그룹" 버튼을 우측에 큰 크기로 배치한다.

## §2. 파일 변경 계획

| 구분 | 파일 | 변경 내용 |
|------|------|----------|
| 수정 | `web/src/pages/admin/groups.html` | 3단 그리드 컨테이너, 모달 HTML 제거, 상단 "새 그룹" 버튼 |
| 수정 | `web/public/js/admin/admin-groups.js` | 페이지 초기화 로직 수정 |
| 수정 | `web/public/js/admin/keyword-group-manager.js` | 모달 참조 제거, 3단 패널 참조 |

## §3. 작업 체크리스트 (Done Definition)

- [x] 3단 영역 DOM: #groups-list / #group-detail / #keyword-list
- [x] 모달 관련 HTML (modal backdrop, modal content) 완전 제거
- [x] 상단 "새 그룹" 버튼 제목 우측에 큰 크기로 배치
- [x] 검색/필터 영역 유지
- [x] 기존 JS 이벤트 바인딩 3단 구조에 맞게 조정

## §4. 참조

- [Phase 17 개발 요구사항 §2.2](../../../planning/260218-0830-phase17-개발-요구사항.md)
