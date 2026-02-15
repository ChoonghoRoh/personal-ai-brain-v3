# Phase 7.5: Upgrade 테스트 시나리오

**작성일**: 2026-01-07  
**대상 버전**: Phase 7.5 Upgrade

---

## 📋 테스트 개요

### 테스트 목표

Phase 7 Upgrade의 핵심 기능을 검증합니다:
1. 청크 승인/거절 워크플로우
2. AI 라벨 추천 기능
3. AI 관계 추천 기능
4. Reasoning에서 승인된 청크만 사용하는지 확인

---

## 1️⃣ 데이터베이스 스키마 확장 검증

### 1.1 새 필드 확인

**테스트 항목**: KnowledgeChunk, KnowledgeLabel, KnowledgeRelation 테이블에 새 필드가 추가되었는지 확인

**검증 방법**:
```sql
-- PostgreSQL에서 확인
\d knowledge_chunks
\d knowledge_labels
\d knowledge_relations
```

**예상 결과**:
- `knowledge_chunks`: status, source, approved_at, approved_by, version 필드 존재
- `knowledge_labels`: status, source 필드 존재
- `knowledge_relations`: score, confirmed, source 필드 존재

**검증 기준**: ✅ 모든 새 필드가 존재해야 함

---

## 2️⃣ 청크 승인/거절 API 검증

### 2.1 청크 승인 API

**테스트 항목**: `POST /api/knowledge/chunks/{chunk_id}/approve`

**테스트 시나리오**:
1. draft 상태의 청크 생성 (또는 기존 청크 사용)
2. 승인 API 호출
3. 청크 상태가 `approved`로 변경되었는지 확인
4. `approved_at`, `approved_by`, `version` 필드 업데이트 확인

**요청 예시**:
```bash
curl -X POST http://localhost:8001/api/knowledge/chunks/1/approve \
  -H "Content-Type: application/json" \
  -d '{"approved_by": "admin"}'
```

**예상 응답**:
```json
{
  "id": 1,
  "status": "approved",
  "approved_at": "2026-01-07T...",
  "approved_by": "admin",
  "version": 2
}
```

**검증 기준**: ✅ 청크 상태가 `approved`로 변경되고, 관련 필드가 업데이트되어야 함

### 2.2 청크 거절 API

**테스트 항목**: `POST /api/knowledge/chunks/{chunk_id}/reject`

**테스트 시나리오**:
1. draft 상태의 청크 생성
2. 거절 API 호출
3. 청크 상태가 `rejected`로 변경되었는지 확인

**요청 예시**:
```bash
curl -X POST http://localhost:8001/api/knowledge/chunks/1/reject \
  -H "Content-Type: application/json" \
  -d '{"reason": "부적절한 내용"}'
```

**예상 응답**:
```json
{
  "id": 1,
  "status": "rejected",
  "rejected_at": "2026-01-07T..."
}
```

**검증 기준**: ✅ 청크 상태가 `rejected`로 변경되어야 함

### 2.3 승인 대기 청크 목록 조회

**테스트 항목**: `GET /api/knowledge/chunks/pending`

**테스트 시나리오**:
1. 여러 상태의 청크 생성 (draft, approved, rejected)
2. pending API 호출
3. draft 상태 청크만 반환되는지 확인

**요청 예시**:
```bash
curl http://localhost:8001/api/knowledge/chunks/pending?status=draft
```

**검증 기준**: ✅ draft 상태 청크만 반환되어야 함

---

## 3️⃣ AI 라벨 추천 API 검증

### 3.1 라벨 추천 생성

**테스트 항목**: `POST /api/knowledge/labels/suggest`

**테스트 시나리오**:
1. 청크 생성
2. 라벨 추천 API 호출
3. 추천된 라벨 목록과 confidence 점수 확인

**요청 예시**:
```bash
curl -X POST http://localhost:8001/api/knowledge/labels/suggest?chunk_id=1
```

**예상 응답**:
```json
{
  "chunk_id": 1,
  "suggestions": [
    {
      "label_id": 1,
      "label_name": "ai",
      "label_type": "domain",
      "confidence": 0.8
    }
  ]
}
```

**검증 기준**: ✅ 추천 라벨 목록과 confidence 점수가 반환되어야 함

### 3.2 추천 라벨 적용

**테스트 항목**: `POST /api/knowledge/labels/suggest/{chunk_id}/apply/{label_id}`

**테스트 시나리오**:
1. 라벨 추천 생성
2. 추천 라벨 적용 API 호출
3. KnowledgeLabel이 `suggested` 상태로 생성되었는지 확인

**요청 예시**:
```bash
curl -X POST http://localhost:8001/api/knowledge/labels/suggest/1/apply/1?confidence=0.8
```

**검증 기준**: ✅ KnowledgeLabel이 `status=suggested`, `source=ai`로 생성되어야 함

---

## 4️⃣ AI 관계 추천 API 검증

### 4.1 관계 추천 생성

**테스트 항목**: `POST /api/knowledge/relations/suggest`

**테스트 시나리오**:
1. 여러 청크 생성 (승인된 청크 포함)
2. 관계 추천 API 호출
3. 유사 청크 추천 목록과 score 확인

**요청 예시**:
```bash
curl -X POST http://localhost:8001/api/knowledge/relations/suggest?chunk_id=1&limit=5
```

**예상 응답**:
```json
{
  "chunk_id": 1,
  "suggestions": [
    {
      "target_chunk_id": 2,
      "target_content_preview": "...",
      "relation_type": "similar",
      "score": 0.7
    }
  ]
}
```

**검증 기준**: ✅ 유사 청크 추천 목록과 score가 반환되어야 함

### 4.2 추천 관계 적용

**테스트 항목**: `POST /api/knowledge/relations/suggest/{chunk_id}/apply`

**테스트 시나리오**:
1. 관계 추천 생성
2. 추천 관계 적용 API 호출
3. KnowledgeRelation이 `confirmed=false`, `source=ai`로 생성되었는지 확인

**요청 예시**:
```bash
curl -X POST http://localhost:8001/api/knowledge/relations/suggest/1/apply \
  -H "Content-Type: application/json" \
  -d '{
    "target_chunk_id": 2,
    "relation_type": "similar",
    "score": 0.7
  }'
```

**검증 기준**: ✅ KnowledgeRelation이 `confirmed=false`, `source=ai`로 생성되어야 함

---

## 5️⃣ Reasoning 승인 청크 필터링 검증

### 5.1 승인된 청크만 사용 확인

**테스트 항목**: Reasoning API가 승인된 청크만 사용하는지 확인

**테스트 시나리오**:
1. draft 상태 청크 생성
2. approved 상태 청크 생성
3. Reasoning API 호출
4. approved 청크만 사용되는지 확인

**요청 예시**:
```bash
curl -X POST http://localhost:8001/api/reason \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "design_explain",
    "inputs": {"projects": [1]},
    "question": "테스트 질문"
  }'
```

**검증 기준**: 
- ✅ Reasoning이 승인된 청크만 사용해야 함
- ✅ draft/rejected 청크는 제외되어야 함
- ✅ 승인된 청크가 없으면 적절한 오류 메시지 반환

### 5.2 관계 추적에서 확정 관계만 사용 확인

**테스트 시나리오**:
1. 확정된 관계(`confirmed=true`) 생성
2. AI 제안 관계(`confirmed=false`) 생성
3. Reasoning 실행
4. 확정된 관계만 사용되는지 확인

**검증 기준**: ✅ 확정된 관계만 추적되어야 함

---

## 6️⃣ 통합 워크플로우 검증

### 6.1 Draft → Approval 워크플로우

**테스트 시나리오**:
1. AI가 청크 생성 (status=draft, source=ai_generated)
2. 관리자가 청크 승인
3. Reasoning에서 승인된 청크 사용 확인

**검증 기준**: ✅ 전체 워크플로우가 정상 작동해야 함

### 6.2 AI 추천 → 승인 워크플로우

**테스트 시나리오**:
1. AI가 라벨 추천 생성 (status=suggested)
2. 관리자가 라벨 확인 후 승인 (status=confirmed)
3. 승인된 라벨이 청크에 적용되는지 확인

**검증 기준**: ✅ AI 추천 → 관리자 승인 → 적용 워크플로우가 정상 작동해야 함

---

## 7️⃣ 오류 처리 검증

### 7.1 존재하지 않는 청크 처리

**테스트 항목**: 존재하지 않는 청크 ID로 API 호출

**검증 기준**: ✅ 적절한 404 오류 반환

### 7.2 데이터 부족 상황 처리

**테스트 항목**: 승인된 청크가 없을 때 Reasoning 호출

**검증 기준**: ✅ 적절한 오류 메시지 반환 ("승인된 지식이 없습니다")

---

## 📊 테스트 체크리스트

- [ ] DB 스키마 확장 확인
- [ ] 청크 승인 API 정상 작동
- [ ] 청크 거절 API 정상 작동
- [ ] 승인 대기 청크 목록 조회 정상 작동
- [ ] AI 라벨 추천 생성 정상 작동
- [ ] 추천 라벨 적용 정상 작동
- [ ] AI 관계 추천 생성 정상 작동
- [ ] 추천 관계 적용 정상 작동
- [ ] Reasoning에서 승인된 청크만 사용 확인
- [ ] 관계 추적에서 확정 관계만 사용 확인
- [ ] 통합 워크플로우 정상 작동
- [ ] 오류 처리 정상 작동

---

**작성자**: AI Assistant  
**최종 업데이트**: 2026-01-07

