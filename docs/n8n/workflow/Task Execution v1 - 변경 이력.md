# Task Execution v1 — 변경 이력

**기준:** 저장소의 `Task Execution v1.json`을 **n8n에서 다운로드한 실제 테스트 완료 버전**으로 교체한 뒤의 변경 사항을 기록함.

---

## 1. 교체 요약

| 항목 | 이전 (템플릿) | 이후 (다운로드·테스트 완료 버전) |
|------|----------------|----------------------------------|
| 출처 | 저장소 템플릿 JSON | n8n UI에서 Export한 워크플로우 |
| 노드 이름 | 접미사 없음 (예: DB_SelectPendingTask) | 접미사 `2` 또는 n8n 기본명 (예: DB_SelectPendingTask2, Send a message1) |
| Credential | 플레이스홀더 (YOUR_POSTGRES_CREDENTIAL_ID 등) | 실제 인스턴스 credential ID |
| Discord 노드 | V1, disabled | V2 Message Send, 활성, 노드명 "Send a message1" |
| 연결 구조 | DB_UpdateTaskStatus → Discord + LOOP (2출력) | DB_UpdateTaskStatus2 → Send a message1 → LOOP_NextTaskOrTrigger2 (1출력) |

---

## 2. 노드 이름 대응표

| 이전 (템플릿) | 이후 (다운로드 버전) |
|---------------|----------------------|
| Trigger_Manual | Trigger_Manual |
| DB_SelectPendingTask | **DB_SelectPendingTask2** |
| JS_NormalizePendingTaskResult | **JS_NormalizePendingTaskResult2** |
| IF_HasPendingTask | **IF_HasPendingTask2** |
| JS_PrepareTaskPayload | **JS_PrepareTaskPayload2** |
| HTTP_RunTaskExecution | **HTTP_RunTaskExecution2** |
| JS_SetTaskStatusFromResponse | **JS_SetTaskStatusFromResponse1** |
| DB_UpdateTaskStatus | **DB_UpdateTaskStatus2** |
| DISCORD_SendTaskComplete | **Send a message1** (Discord V2 Message > Send) |
| LOOP_NextTaskOrTrigger | **LOOP_NextTaskOrTrigger2** |
| SET_NoPendingTask | **SET_NoPendingTask2** |

---

## 3. 파라미터·로직 변경

### 3.1 Trigger_Manual
- **추가:** `executeOnce: false`

### 3.2 JS_PrepareTaskPayload2
- **코드:** `workspace_root` — `process.env.WORKSPACE_ROOT || '/workspace'` 제거, 고정값 `'/workspace'` 사용.
- **참고:** 다른 환경(예: 로컬)에서는 필요 시 다시 `process.env.WORKSPACE_ROOT || '/workspace'` 로 변경 가능.

### 3.3 HTTP_RunTaskExecution2
- **URL:** `http://localhost:8001/...` → `http://backend:8000/api/workflow/run-task`
- **저장소 반영:** 다운로드본에는 URL 끝 공백(`run-task `)이 있었음. 저장소 JSON에서는 해당 공백 제거함.

### 3.4 JS_SetTaskStatusFromResponse1
- **노드 참조:** `JS_PrepareTaskPayload` → `JS_PrepareTaskPayload2`
- **성공 판단 로직:** Backend가 본문만 반환할 때를 위해 `body.success === true` 우선 확인 추가.
  - 변경 후: `(body && body.success === true) || (statusCode >= 200 && statusCode < 300 && body && body.success !== false)`

### 3.5 DB_UpdateTaskStatus2
- **Query Parameters 옵션 키:** 저장소에서는 `queryParameters`(배열) 사용, 다운로드 버전에서는 **`queryReplacement`** 키로 내보내짐.
- **값:** `["={{ $json.status }}", "={{ $json.id }}"]` 형태 유지.
- **참고:** 다른 n8n 버전/재 import 시 Postgres 노드에서 “Query Parameters”가 비어 있으면, Options에서 **Query Parameters**를 두 개(`$json.status`, `$json.id`)로 직접 설정.

### 3.6 Discord 노드 (Send a message1)
- **타입:** Discord V1 → **Discord V2** (Resource: message, Operation: send).
- **상태:** 기존 `DISCORD_SendTaskComplete`는 `disabled: true`였음 → **Send a message1**은 비활성화 없음(실제 사용).
- **내용:**  
  - `guildId`: Resource Locator (list) — value `1465585145368018988`, cachedResultName "Ai-Personal-Brain-Bot".  
  - `channelId`: Resource Locator (list) — value `1465608311813701692`, cachedResultName "ai-workflow".  
  - `content`: `Task 실행 완료\nTask ID: {{ $node["JS_PrepareTaskPayload2"].json.id }}\nStatus: {{ $node["JS_SetTaskStatusFromResponse1"].json.status }}`
- **연결:** DB_UpdateTaskStatus2 → Send a message1 → LOOP_NextTaskOrTrigger2 (Discord 알림 후 LOOP으로만 진행).

---

## 4. 연결(connections) 변경

- 모든 노드 참조가 위 **노드 이름 대응표**에 맞게 변경됨.
- **DB_UpdateTaskStatus2** 출력:  
  - 이전: DISCORD_SendTaskComplete, LOOP_NextTaskOrTrigger 두 개로 분기.  
  - 이후: **Send a message1** 한 개만 다음 노드로 연결되고, **Send a message1**이 **LOOP_NextTaskOrTrigger2**로 연결됨.

---

## 5. Credential·메타

- **PostgreSQL:** `id: "YOUR_POSTGRES_CREDENTIAL_ID"` → 실제 credential ID (`tbx7tKTwKOdsxhQc`).
- **Discord:** `id: "YOUR_DISCORD_CREDENTIAL_ID"` → 실제 credential ID (`pT4DLXfrV4QLk8Aj`).
- **meta.templateCredsSetupCompleted:** `false` → `true`.
- **meta.instanceId:** n8n 인스턴스 식별자로 변경됨.
- **versionId:** n8n 버전 UUID로 변경됨.
- **id:** 워크플로우 ID (`YI8VlGp40RSF1Ya19VtcV`) 추가됨.

---

## 6. 다른 환경에서 사용 시 주의

1. **Credential:** PostgreSQL·Discord credential ID는 현재 n8n 인스턴스 기준이므로, 다른 n8n/환경에 import 시 해당 환경의 credential로 다시 지정해야 함.
2. **Discord guild/channel ID:** 다른 서버·채널을 쓰려면 노드에서 guild/channel을 다시 선택.
3. **Backend URL:** `http://backend:8000` 은 Docker Compose 등 동일 네트워크 전제. 호스트/다른 네트워크에서는 `docs/n8n/n8n-backend-call-manual-settings.md` 의 URL 표 참고해 수정.
4. **queryReplacement:** Postgres 노드 오류 시 Options에서 **Query Parameters**를 `$json.status`, `$json.id` 두 개로 설정해 보기.

---

## 7. 파일 정보

- **파일:** `docs/n8n/workflow/Task Execution v1.json`
- **기록 일자:** 2026-01-27 (실제 테스트 완료 후 n8n에서 다운로드하여 교체한 버전 기준 변경 내용 기록)
