# Task 16-2-4: [BE] 라벨 매칭 역인덱스

**우선순위**: 16-2 내 1순위 (실행 순서)
**예상 작업량**: 중간
**의존성**: Phase 16-1 완료
**담당 팀원**: backend-dev
**상태**: 대기

---

## §1. 개요

라벨 매칭 단계에서 모든 청크 x 모든 라벨을 비교하는 O(N*M) 브루트포스 대신, keyword→[label_id] 역인덱스를 구축하여 O(N*K) (K=평균 토큰 수)로 개선한다.

참조: [리스크 분석 §3.2 방안 G](../../../planning/260217-1600-AI자동화기능-리스크분석.md)

## §2. 파일 변경 계획

| 구분 | 파일 | 변경 내용 |
|------|------|----------|
| 수정 | `backend/services/automation/ai_workflow_service.py` | `_match_labels()` 내 역인덱스 구축 + 매칭 로직 변경 |

## §3. 작업 체크리스트 (Done Definition)

- [ ] 전체 라벨을 조회하여 `label_index: Dict[str, List[int]]` 구축 (라벨명/키워드 토큰 → label_id 리스트)
- [ ] 청크별로 content를 토큰화(lower + split)하여 label_index 조회
- [ ] 후보 라벨만 확정 매칭 (기존 매칭 로직의 결과와 동일)
- [ ] 기존 테스트 통과

## §4. 참조

- [Phase 16 Master Plan §5.2 — 16-2-4](../../phase-16-master-plan.md)
