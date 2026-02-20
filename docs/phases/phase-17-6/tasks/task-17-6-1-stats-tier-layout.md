# Task 17-6-1: [FE] 통계 4단 레이아웃 재구성

**우선순위**: 17-6 내 1순위
**예상 작업량**: 큰
**의존성**: 17-5 완료
**상태**: 완료

---

## §1. 개요

통계 대시보드를 4단 계층 레이아웃(요약→분포→트렌드→상세)으로 재구성하고,
시스템 상태 카드를 제거(Phase 17-7 대시보드로 이관)한다.

## §2. 파일 변경 계획

| 구분 | 파일 | 변경 내용 |
|------|------|----------|
| 수정 | `web/src/pages/admin/statistics.html` | 4단 `stats-tier` 래퍼 + 서브타이틀 추가, 시스템 상태 카드 제거 |
| 수정 | `web/public/css/statistics.css` | `.stats-tier`, `.tier-header`, `.tier-subtitle` 스타일, 미사용 system-status 스타일 제거 |
| 수정 | `web/public/js/admin/statistics.js` | `updateSystemStatus()` 제거, `/system` + `/health` API 호출 제거 |

## §3. 4단 구조

1. **1단 — 요약 수치**: 문서·청크·라벨·사용량 카드 4장
2. **2단 — 분포 차트**: 문서유형 도넛 + 청크상태 바 + 라벨유형 도넛
3. **3단 — 트렌드**: 일별 라인 차트 (7/14/30일 선택)
4. **4단 — 상세 테이블**: 인기 라벨 TOP10 + 프로젝트별 현황 (2-col)

## §4. 작업 체크리스트

- [x] statistics.html에 stats-tier 래퍼 4단 구조 적용
- [x] 각 tier에 tier-header + tier-subtitle 추가
- [x] 시스템 상태 카드 섹션 HTML 제거
- [x] statistics.css에 .stats-tier, .tier-header, .tier-subtitle 스타일 추가
- [x] system-status 관련 미사용 CSS 제거
- [x] statistics.js에서 updateSystemStatus() 함수 제거
- [x] /system, /health API 호출 코드 제거
