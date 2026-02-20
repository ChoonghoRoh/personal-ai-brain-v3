# Task 17-8-3: [BE] AI 부모 노드 추천

**우선순위**: 17-8 내 2순위 (17-8-1 이후 병렬)
**예상 작업량**: 중간
**의존성**: 17-8-1
**상태**: 완료

---

## §1. 개요

LLM 기반으로 키워드에 적합한 부모 노드(그룹)를 자동 추천하는 API를 구현한다.
기존 트리 구조를 분석하여 LLM 컨텍스트로 주입한다.

## §2. 파일 변경 계획

| 구분 | 파일 | 변경 내용 |
|------|------|----------|
| 수정 | `backend/routers/knowledge/labels.py` | suggest-parent 엔드포인트 추가 |
| 수정 | `backend/services/knowledge/labels_handlers.py` | 트리 분석 + LLM 호출 로직 |
| 수정 | `backend/services/knowledge/group_keyword_recommender.py` | 부모 추천 로직 연동 |

## §3. API 엔드포인트

- `POST /api/labels/suggest-parent` — AI 부모 노드 추천

## §4. 작업 체크리스트

- [x] POST /api/labels/suggest-parent 엔드포인트 구현
- [x] 기존 트리 구조 분석 → LLM 컨텍스트 생성
- [x] group_keyword_recommender.py 연동
- [x] 추천 결과 (부모 노드 ID, 이름, 신뢰도) 응답
