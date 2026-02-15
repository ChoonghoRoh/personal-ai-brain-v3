# Task 13-5-3: [BE] System Prompt 활용 (role: system, 후처리 축소)

**우선순위**: 13-5 내 3순위
**예상 작업량**: 중 (1일)
**의존성**: Task 13-5-1과 연동 시 이후 진행
**상태**: TODO

**기반 문서**: `phase-13-5-todo-list.md`
**Plan**: `phase-13-5-plan.md`

---

## 1. 개요

### 1.1 현재 상태

"한국어로만 답변" 등 시스템 지시를 User Prompt 앞에 매번 삽입. 프롬프트가 지저분하고, 코드블록/영문 삭제 등 과도한 후처리 정규식 존재.

### 1.2 목표

Ollama `/api/chat`의 `role: system` 메시지를 활용하여 페르소나·제약사항을 분리 정의하고, 과도한 후처리 정규식을 축소한다.

---

## 2. 파일 변경 계획

| 파일 | 변경 내용 |
|------|----------|
| `backend/services/ai/ollama_client.py` | `/api/chat` 엔드포인트 지원 (role: system) |
| `backend/routers/ai/ai.py` | 프롬프트에서 시스템 지시 분리, 후처리 정규식 축소 |
| `backend/services/reasoning/dynamic_reasoning_service.py` | 모드별 시스템 프롬프트 분리 |

---

## 3. 작업 체크리스트

- [ ] ollama_client에 `/api/chat` 지원 함수 추가
- [ ] System Prompt 메시지 정의 (페르소나·제약)
- [ ] User Prompt에서 시스템 지시 중복 제거
- [ ] 후처리 정규식 축소 (코드블록·영문 삭제 검토)
- [ ] 프롬프트 구조 문서화
- [ ] 답변 품질 A/B 비교

---

## 4. 참조

- Phase 13 Master Plan §L-3
