# Phase 8-2-5: Todo-List 생성 - 워크플로우 계획

**작성일**: 2026-01-28  
**기반 문서**: phase8-1-0-plan.md  
**관련 문서**: phase8-2-4-discord-approval-loop.md

---

## 📋 개요

Phase 8-2-5는 승인된 Plan을 기반으로 구체적인 Todo-List를 생성하고, Discord 승인 루프를 통해 검토하는 워크플로우입니다.

**우선순위**: High  
**예상 소요 시간**: 1.5시간  
**의존성**: Phase 8-2-4 완료 (Plan 승인 완료 후)

---

## 🔄 워크플로우 구조

```
[Manual Trigger 또는 Phase 8-2-4 완료 트리거]
    ↓
[PostgreSQL] (승인된 Plan 조회, status='approved')
    ↓
[HTTP Request] (GPT API - Todo-List 생성)
    ↓
[Write Binary File] (todo-list.md 생성)
    ↓
[Discord Webhook] (Todo-List 전송, 승인 루프 동일)
    ↓
[Wait] (Discord Webhook Trigger 대기)
    ↓
[Discord Trigger] (반응 감지)
    ↓
[IF] (반응별 분기)
    ├─ ✅ 승인 → [PostgreSQL] (todo-list 저장)
    └─ ✏️/❌ → [처리]
```

---

## 📝 작업 목록

### 1. "Todo Generation" 워크플로우 생성

**워크플로우 이름**: "Todo-List Generation"

### 2. HTTP Request 노드 (GPT API)

**Prompt 설계:**

```
Input:
- 승인된 Plan 문서 전체
- 기존 Phase 문서들 (참고용)

Task:
확정된 Plan을 기반으로 구체적인 Todo-List를 생성하세요.

형식:
- [ ] Todo 항목 1
- [ ] Todo 항목 2
- ...

각 Todo 항목은:
- 명확하고 실행 가능해야 함
- 우선순위 표시 (High/Medium/Low)
- 예상 소요 시간 포함
```

**HTTP Request 설정:**

- Method: POST
- URL: `https://api.openai.com/v1/chat/completions`
- Credential: `OpenAi account`
- Body:
  ```json
  {
    "model": "gpt-4",
    "messages": [
      {
        "role": "system",
        "content": "You are a project management assistant. Create a detailed todo list from the approved plan."
      },
      {
        "role": "user",
        "content": "Plan:\n{{ $json.plan_content }}\n\nCreate a detailed todo list with priorities and estimated time."
      }
    ],
    "temperature": 0.7,
    "max_tokens": 2000
  }
  ```

### 3. Write Binary File 노드

**파일 경로**: `/workspace/docs/phases/todo-list.md`  
**파일 내용**: `{{ $json.choices[0].message.content }}`

### 4. Discord 전송 (승인 루프 동일)

**Phase 8-2-4의 Discord 승인 루프 재사용:**

- 동일한 워크플로우 구조
- Todo-List 내용으로 메시지 변경

**메시지 포맷:**

```json
{
  "content": "📋 Phase-8 Todo-List 승인 요청",
  "embeds": [
    {
      "title": "Phase-8 Todo-List",
      "description": "{{ $json.todo_summary }}",
      "footer": {
        "text": "반응으로 응답해주세요: ✅ 승인 | ✏️ 수정 필요 | ❌ 거절"
      }
    }
  ]
}
```

### 5. PostgreSQL 저장

**승인 후 저장:**

- todo-list.md 내용을 PostgreSQL에 저장
- 별도 테이블 또는 workflow_plans에 추가 필드로 저장 가능

**저장 쿼리 (예시):**

```sql
UPDATE workflow_phases
SET todo_list_md = $1
WHERE phase_name = 'Phase-8-Current-State'
RETURNING id;
```

또는 별도 테이블 생성:

```sql
CREATE TABLE IF NOT EXISTS workflow_todo_lists (
    id SERIAL PRIMARY KEY,
    phase_id INT REFERENCES workflow_phases(id) ON DELETE CASCADE,
    content TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## ✅ 완료 기준

- [ ] 승인된 Plan 기반 Todo-List 생성 가능
- [ ] Discord 승인 프로세스 작동
- [ ] PostgreSQL 저장 완료
- [ ] 테스트 완료

---

## ⚠️ 리스크 및 대응 방안

**리스크 1**: GPT API 비용

- **대응**: 토큰 수 제한, 캐싱 활용

**리스크 2**: Todo-List 품질

- **대응**: 프롬프트 개선, 후처리 검증

**리스크 3**: Discord 승인 루프 재사용 문제

- **대응**: 공통 워크플로우 모듈화 고려

---

## 📝 다음 단계

**Phase 8-2-6: Task Plan & Test Plan 생성**

- 의존성: Phase 8-2-5 완료 (Todo-List 승인 완료 후)
- 입력: 승인된 Todo-List
- 출력: 각 Todo 항목별 Task Plan 및 Test Plan

---

## 🔗 관련 문서

- `phase8-2-4-discord-approval-loop.md` - Discord 승인 루프 워크플로우
- `phase8-1-0-plan.md` - n8n 워크플로우 개발 계획
- `phase8-master-plan.md` - Phase 8 전체 계획 (docs/phases/phase8-master-plan.md)

---

**문서 버전**: 1.0  
**최종 업데이트**: 2026-01-28
