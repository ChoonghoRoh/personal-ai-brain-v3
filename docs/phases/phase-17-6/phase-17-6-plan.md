# Phase 17-6: 통계 메뉴 4단 레이아웃 리뉴얼

## 목표

통계 대시보드를 4단 계층 레이아웃(요약→분포→트렌드→상세)으로 재구성하고,
시스템 상태 카드를 제거(Phase 17-7 대시보드로 이관)한다.

## 변경 파일

| 구분 | 파일 | 변경 내용 |
|------|------|-----------|
| 수정 | `web/src/pages/admin/statistics.html` | 4단 `stats-tier` 래퍼 + 서브타이틀 추가, 시스템 상태 카드 제거 |
| 수정 | `web/public/css/statistics.css` | `.stats-tier`, `.tier-header`, `.tier-subtitle` 스타일, 미사용 system-status 스타일 제거 |
| 수정 | `web/public/js/admin/statistics.js` | `updateSystemStatus()` 제거, `/system` + `/health` API 호출 제거 |

## 4단 구조

1. **1단 — 요약 수치**: 문서·청크·라벨·사용량 카드 4장
2. **2단 — 분포 차트**: 문서유형 도넛 + 청크상태 바 + 라벨유형 도넛
3. **3단 — 트렌드**: 일별 라인 차트 (7/14/30일 선택)
4. **4단 — 상세 테이블**: 인기 라벨 TOP10 + 프로젝트별 현황 (2-col)
