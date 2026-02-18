# Task 17-1-3: [FE] 상세 패널 인라인 편집

**우선순위**: 17-1 내 3순위
**예상 작업량**: 중간
**의존성**: 17-1-2 (3단 레이아웃 HTML 구조)
**담당 팀원**: frontend-dev
**상태**: 완료

---

## §1. 개요

모달 기반 CRUD를 인라인 편집으로 전환한다. 그룹 선택 시 상세 패널(2단 영역)에 편집 폼을 표시하고, 수정/삭제 버튼을 상세 패널 내로 이동한다.

## §2. 파일 변경 계획

| 구분 | 파일 | 변경 내용 |
|------|------|----------|
| 수정 | `web/public/js/admin/keyword-group-crud.js` | openModal→renderDetail, closeModal 제거, 인라인 폼 렌더링 |
| 수정 | `web/public/js/admin/keyword-group-suggestion.js` | 모달 내부 추천 → 상세 패널 추천 연동 |

## §3. 작업 체크리스트 (Done Definition)

- [x] 그룹 클릭 → 상세 패널에 이름/설명/키워드 편집 폼 표시
- [x] 수정 버튼 → API 호출 → 성공 시 목록 갱신
- [x] 삭제 버튼 → 확인 후 API 호출 → 목록에서 제거
- [x] 모달 관련 코드 완전 제거 (openModal, closeModal 등)

## §4. 참조

- [Phase 17 개발 요구사항 §2.3](../../../planning/260218-0830-phase17-개발-요구사항.md)
