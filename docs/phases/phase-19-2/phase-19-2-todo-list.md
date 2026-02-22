# Phase 19-2 TODO List

## Task 체크리스트

- [ ] **19-2-1** [FE] CSS Grid 레이아웃 재구성
  - [ ] Desktop (1200px+): 요약 4단, 분포 3단, 상세 2단 좌우
  - [ ] Tablet (768~1200px): 요약 2단, 분포 2단, 상세 2단
  - [ ] Mobile (~768px): 전체 1단
  - [ ] Tier 헤더 스타일 유지/정리
  - [ ] 기존 카드 클릭 필터링 영역 레이아웃 유지

- [ ] **19-2-2** [FE] HTML 마크업 정리 + JS 렌더링 호환
  - [ ] HTML 시맨틱 구조 확인 (section/div 정리)
  - [ ] Chart.js canvas 크기 호환 확인
  - [ ] statistics.js 카드/테이블 렌더링 호환 확인
  - [ ] statistics-charts.js Chart.js responsive 옵션 호환 확인

- [ ] **19-2-3** [FE] 반응형 테스트 (3단계 검증)
  - [ ] Desktop (1200px+) 레이아웃 검증
  - [ ] Tablet (768~1200px) 레이아웃 검증
  - [ ] Mobile (~768px) 레이아웃 검증
  - [ ] 카드 클릭 → 필터링 목록 표시 검증
  - [ ] 차트 리사이즈 검증

## 품질 게이트

- [ ] **G2_fe**: CDN 없음, innerHTML+esc(), ESM 패턴, 콘솔 에러 없음
- [ ] **G3**: 페이지 로드 정상, 차트 렌더링 정상, 반응형 정상
- [ ] **G4**: G2+G3 통합 판정
