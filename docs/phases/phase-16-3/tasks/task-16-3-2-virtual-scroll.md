# Task 16-3-2: [FE] Virtual Scroll 문서 리스트

**우선순위**: 16-3 내 2순위
**예상 작업량**: 중간
**의존성**: 16-3-1 완료
**담당 팀원**: frontend-dev
**상태**: 대기

---

## §1. 개요

문서 리스트를 Virtual Scroll로 전환하여 가시 영역(~22개 노드)만 DOM에 렌더링한다. 500개 문서 기준 96% DOM 절감.

참조: [리스크 분석 §3.3 방안 A](../../../planning/260217-1600-AI자동화기능-리스크분석.md)

## §2. 파일 변경 계획

| 구분 | 파일 | 변경 내용 |
|------|------|----------|
| 수정 | `web/public/js/admin/ai-automation.js` | renderDocumentList → Virtual Scroll |
| 수정 | `web/public/css/admin/admin-ai-automation.css` | 스크롤 컨테이너 스타일 |

## §3. 작업 체크리스트 (Done Definition)

- [ ] 문서 아이템 높이 고정 (예: 40px)
- [ ] 가시 영역 노드 수 = ceil(컨테이너 높이 / 아이템 높이) + 버퍼 2개
- [ ] scroll 이벤트에서 startIndex 계산 → 가시 범위만 렌더
- [ ] spacer div로 전체 스크롤 높이 유지
- [ ] 선택 상태(selectedDocuments)·완료 상태(doc_result) 유지
- [ ] 검색 필터링 시 Virtual Scroll 갱신
- [ ] 500개 문서에서 초기 렌더 <50ms

## §4. 참조

- [Phase 16 Master Plan §6 — 16-3-2](../../phase-16-master-plan.md)
