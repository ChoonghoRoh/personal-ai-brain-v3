# Phase 17-1: 키워드 그룹 3단 레이아웃 리뉴얼

## Status: DONE

## 목표
2단(목록+모달) -> 3단(목록+상세+키워드) 레이아웃으로 전환
- 모달 제거, 인라인 편집
- 페이지네이션 추가
- 최초 진입 시 1번째 그룹 자동 선택

## Tasks
1. [BE] 그룹 목록 페이지네이션 API (page/size + total)
2. [FE] 3단 레이아웃 HTML 구조 (groups.html 전면 개편, 모달 제거)
3. [FE] 상세 패널 인라인 편집 (crud.js 모달->인라인 전환)
4. [FE] 키워드 목록 3단 영역 이동 (matching.js)
5. [FE] 페이지네이션 + 자동 선택 (ui.js)
6. [FE] CSS 3단 그리드 (admin-groups.css)

## 진행 상황
- 2026-02-18: BUILDING 착수
- 2026-02-18: 6개 Task 모두 구현 완료 + 코드 리뷰 통과 → DONE
