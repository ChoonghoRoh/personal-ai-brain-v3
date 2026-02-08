# Phase 8-2-4: Discord 승인 루프 - 워크플로우 계획

**작성일**: 2026-01-28  
**기반 문서**: phase8-1-0-plan.md  
**관련 문서**: phase8-2-4-discord-approval-review.md

---

## 📋 개요

Phase 8-2-4는 n8n 워크플로우와 Discord를 연동하여 Plan 문서에 대한 승인 루프를 구축하는 작업입니다. 사용자가 Discord에서 Plan을 검토하고 승인/거절/수정 요청을 할 수 있도록 합니다.

**우선순위**: High  
**예상 소요 시간**: 4시간 (가장 복잡)  
**의존성**: Phase 8-2-3 완료

---

## 🔄 워크플로우 구조

```
[Manual Trigger 또는 자동 트리거]
    ↓
[PostgreSQL] (workflow_plans에서 최신 Plan 조회)
    ↓
[Discord Webhook] (Plan 전송)
    ↓
[Wait] (Discord Webhook Trigger 대기, 최대 24시간)
    ↓
[Discord Trigger] (Message Reaction 감지)
    ↓
[IF] (반응별 분기)
    ├─ ✅ 승인 → [PostgreSQL] (approvals 저장, plan status='approved')
    │              ↓
    │         [다음 단계로 진행]
    │
    ├─ ✏️ 수정 필요 → [HTTP Request] (GPT API - Plan 수정)
    │                  ↓
    │              [Write Binary File] (수정된 Plan 저장)
    │                  ↓
    │              [PostgreSQL] (plan 업데이트, approvals에 feedback 저장)
    │                  ↓
    │              [Loop] (최대 5회, iteration_count++)
    │                  ↓
    │              [Discord Webhook] (수정된 Plan 재전송)
    │                  ↓
    │              [Wait] (다시 대기)
    │
    └─ ❌ 거절 → [PostgreSQL] (approvals 저장, plan status='rejected')
                 ↓
            [워크플로우 종료]
```

---

## 📝 작업 목록

### 1. Discord Webhook 노드 설정

**노드**: Discord Webhook  
**Credential**: `Discord Webhook-n8n-ai-personal-brain`

**메시지 포맷:**

```json
{
  "content": "📋 Phase-8 Plan v1 승인 요청",
  "embeds": [
    {
      "title": "Phase-8 Plan v1",
      "description": "{{ $json.plan_summary }}",
      "fields": [
        { "name": "Phase", "value": "Phase-8-Current-State", "inline": true },
        { "name": "버전", "value": "1", "inline": true },
        { "name": "생성일", "value": "{{ $json.created_at }}", "inline": true }
      ],
      "footer": {
        "text": "반응으로 응답해주세요: ✅ 승인 | ✏️ 수정 필요 | ❌ 거절"
      }
    }
  ]
}
```

**Plan 요약 생성:**

- PostgreSQL에서 Plan content 읽기
- Code 노드로 첫 500자 추출하여 요약 생성

### 2. Wait 노드 설정

**노드**: Wait  
**Wait For**: `Webhook`  
**Webhook Path**: `discord-approval`  
**Timeout**: 24시간

### 3. Discord Trigger 워크플로우 생성

**별도 워크플로우**: "Discord Approval Trigger"

**노드 구성:**

- **Discord Trigger**: Message Reaction Added
  - Channel: 승인 채널 ID
  - Emoji Filter: ✅, ✏️, ❌
  - Message ID: Webhook으로 전송된 메시지 ID 저장 필요

**연동 방법:**

- Webhook 노드에서 반환된 메시지 ID를 PostgreSQL에 저장
- Discord Trigger에서 해당 메시지 ID의 반응만 감지

### 4. IF 노드 (반응별 분기)

**조건:**

- `{{ $json.emoji.name }} === '✅'` → 승인 분기
- `{{ $json.emoji.name }} === '✏️'` → 수정 필요 분기
- `{{ $json.emoji.name }} === '❌'` → 거절 분기

### 5. Loop 구현 (최대 5회)

**구조:**

```
[Set] (iteration_count = 0, max_iterations = 5)
    ↓
[Loop Over Items] (최대 5회)
    ├─ [IF] (iteration_count < max_iterations)
    │   ├─ [Discord Webhook] (Plan 전송)
    │   ├─ [Wait] (응답 대기)
    │   ├─ [Discord Trigger] (반응 감지)
    │   ├─ [IF] (반응 타입)
    │   │   ├─ ✅ 승인 → [Break Loop]
    │   │   ├─ ✏️ 수정 → [HTTP Request] (GPT 수정)
    │   │   │              ↓
    │   │   │         [Set] (iteration_count++)
    │   │   │              ↓
    │   │   │         [Continue Loop]
    │   │   └─ ❌ 거절 → [Break Loop]
    │   └─ [Set] (iteration_count++)
    └─ [IF] (iteration_count >= max_iterations)
        └─ [Error] (최대 반복 횟수 초과)
```

### 6. PostgreSQL 노드 (approvals 테이블에 기록)

**승인 저장:**

```sql
INSERT INTO workflow_approvals (
    phase_id, step, version, feedback, approved, created_at
) VALUES (
    $1, 'plan-review', $2, NULL, true, NOW()
)
RETURNING id;
```

**수정 요청 저장:**

```sql
INSERT INTO workflow_approvals (
    phase_id, step, version, feedback, approved, created_at
) VALUES (
    $1, 'plan-review', $2, $3, false, NOW()
)
RETURNING id;
```

**거절 저장:**

```sql
INSERT INTO workflow_approvals (
    phase_id, step, version, feedback, approved, created_at
) VALUES (
    $1, 'plan-review', $2, NULL, false, NOW()
)
RETURNING id;
```

### 7. GPT API 노드 (Plan 수정)

**HTTP Request 노드:**

- Method: POST
- URL: `https://api.openai.com/v1/chat/completions`
- Headers:
  - `Authorization: Bearer {{ $credentials.openai.apiKey }}`
  - `Content-Type: application/json`
- Body:
  ```json
  {
    "model": "gpt-4",
    "messages": [
      {
        "role": "system",
        "content": "You are a technical planning assistant. Modify the plan based on feedback."
      },
      {
        "role": "user",
        "content": "Original Plan:\n{{ $json.plan_content }}\n\nFeedback:\n{{ $json.feedback }}\n\nPlease modify the plan according to the feedback."
      }
    ],
    "temperature": 0.7,
    "max_tokens": 2000
  }
  ```

---

## ✅ 완료 기준

- [ ] Discord를 통해 승인 요청 전송 가능
- [ ] 승인/거절 반응으로 응답 가능
- [ ] 수정 요청 시 GPT로 Plan 수정 가능
- [ ] 승인 상태가 PostgreSQL에 자동 저장
- [ ] 최대 5회 수정 루프 작동
- [ ] 전체 루프 테스트 완료

---

## ⚠️ 리스크 및 대응 방안

**리스크 1**: Discord API 제한

- **대응**: Rate limiting 고려, 큐 시스템 도입

**리스크 2**: 승인 상태 동기화 실패

- **대응**: 재시도 로직, 수동 동기화 스크립트

**리스크 3**: Discord 봇 권한 문제

- **대응**: 봇 권한 사전 확인, 테스트 환경 구축

**리스크 4**: 반응 감지 실패

- **대응**: 첫 번째 반응만 처리, 타임아웃 설정

---

## 📝 다음 단계

**Phase 8-2-5: Todo-List 생성**

- 의존성: Phase 8-2-4 완료 (Plan 승인 완료 후)
- 트리거: Plan 승인 완료 시 자동 또는 수동

---

## 🔗 관련 문서

- `phase8-2-4-discord-approval-review.md` - Discord 승인 루프 검토 문서
- `phase8-1-0-plan.md` - n8n 워크플로우 개발 계획
- `phase8-master-plan.md` - Phase 8 전체 계획 (docs/phases/phase8-master-plan.md)

---

**문서 버전**: 1.0  
**최종 업데이트**: 2026-01-28
