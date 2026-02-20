# Phase 18-1 Todo List

## Task 18-1-1: 그룹 관리 페이지 탭 UI [FE]
- [ ] 1단 컬럼 col-header의 목록/트리 토글 버튼 → 탭 UI로 변환
- [ ] 탭 전환 시 목록/트리 컨테이너 표시/숨김 전환
- [ ] 기존 switchView() 함수 탭 연동

## Task 18-1-2: 트리 연결 탭 D&D 강화 [FE]
- [ ] 트리 탭에서 Breadcrumb 상시 표시
- [ ] D&D 이동 시 시각적 피드백 강화 (드롭 타겟 하이라이트)
- [ ] 트리 노드 선택 시 2단(상세)에 해당 그룹 정보 표시

## Task 18-1-3: LLM 추천 버튼 복구 [FE]
- [ ] 3단(키워드 목록) 상단에 [🤖 LLM 추천] 버튼 추가
- [ ] 클릭 시 현재 선택된 그룹의 description으로 suggestKeywordsFromDescription() 호출
- [ ] 추천 결과를 키워드 목록 하단에 표시

## Task 18-1-4: 연관 키워드 섹션 UI [FS]
- [ ] 3단(키워드 목록) 하단에 "연관 키워드 추천" 섹션 추가
- [ ] 검색 입력 + [조회] 버튼
- [ ] 결과 표시: 키워드명 + 유사도 % + 체크박스
- [ ] 선택 후 [추가] 버튼으로 그룹에 키워드 추가

## Task 18-1-5: 연관 키워드 API [BE]
- [ ] GET /api/labels/groups/{group_id}/related-keywords API 생성
- [ ] ILIKE 텍스트 검색 + Qdrant 유사도 결합
- [ ] 결과: 상위 20개 (id, name, similarity_score)
- [ ] 현재 그룹 소속 키워드 제외 로직

## Task 18-1-6: 하단 액션바 통합 [FE]
- [ ] matching-summary-bar에 [수정] [삭제] [저장] 버튼 추가
- [ ] 그룹 선택 시 수정/삭제 활성화
- [ ] 변경사항 있을 때 저장 활성화

## Task 18-1-7: CSS 정리 [FE]
- [ ] admin-groups.css 불필요한 중복 스타일 제거
- [ ] 탭 UI 스타일 추가
- [ ] 연관 키워드 섹션 스타일 추가
- [ ] 500줄 모니터링 (최종 줄 수 확인)
