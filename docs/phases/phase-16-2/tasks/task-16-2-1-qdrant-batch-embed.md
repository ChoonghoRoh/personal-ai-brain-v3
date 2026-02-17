# Task 16-2-1: [BE] Qdrant 배치 임베딩

**우선순위**: 16-2 내 2순위 (실행 순서)
**예상 작업량**: 중간
**의존성**: Phase 16-1 완료
**담당 팀원**: backend-dev
**상태**: 대기

---

## §1. 개요

Qdrant 임베딩 단계에서 청크를 단건으로 처리하는 대신, 50건 단위로 배치 인코딩 + batch upsert하여 API 호출 횟수를 대폭 줄인다.

참조: [리스크 분석 §3.2 방안 E](../../../planning/260217-1600-AI자동화기능-리스크분석.md)

## §2. 파일 변경 계획

| 구분 | 파일 | 변경 내용 |
|------|------|----------|
| 수정 | `backend/services/automation/ai_workflow_service.py` | `_embed_chunks()` 배치 처리 |

## §3. 작업 체크리스트 (Done Definition)

- [ ] approved 청크를 50건 단위 배치로 분할
- [ ] 배치 단위로 embedding_model.encode(texts, batch_size=50) 호출
- [ ] 배치 단위로 qdrant_client.upsert(points=[]) 한 번에 전송
- [ ] 배치마다 progress 갱신 (detail.current/total 포함)
- [ ] 960청크 시 Qdrant 호출 약 20회 이하
- [ ] 기존 단건과 동일한 벡터/메타데이터

## §4. 참조

- [Phase 16 Master Plan §5.2 — 16-2-1](../../phase-16-master-plan.md)
