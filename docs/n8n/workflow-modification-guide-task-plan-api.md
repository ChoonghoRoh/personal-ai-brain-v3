# n8n 워크플로우 수정 가이드: Task Plan API 연동

## 개요

기존 n8n 워크플로우의 `JS_CreateTaskPlanAndTestPlan1` 노드는 정적 템플릿으로 Task Plan을 생성합니다.
이를 새로운 `POST /api/workflow/generate-task-plan` API를 사용하도록 수정하면 **프로젝트 코드를 분석하여 구체적인 Task Plan**을 생성할 수 있습니다.

## 변경 사항

### 기존 방식 (정적 템플릿)

`JS_CreateTaskPlanAndTestPlan1` 노드에서 고정된 템플릿 사용:

```javascript
const taskPlan = `# Task Plan: ${content}\n\n## 목표\n${content}를 수행한다.\n\n## 단계\n1. 작업 대상 확인\n2. 필요 시 파일/폴더 생성\n3. 완료 기준 충족 확인\n\n## 완료 기준\n- 작업이 반영되어 저장됨\n`;
```

### 새로운 방식 (API 호출)

Backend API를 호출하여 프로젝트 코드 분석 후 Task Plan 생성.

---

## 수정 방법

### 1단계: HTTP Request 노드 추가

`LOOP_TodoItems` 노드 다음에 **HTTP Request** 노드를 추가합니다.

**노드 설정:**
- **Name**: `HTTP_GenerateTaskPlan`
- **Method**: `POST`
- **URL**: `http://backend:8000/api/workflow/generate-task-plan`
- **Headers**: `Content-Type: application/json`
- **Body (JSON)**:

```json
{
  "task_num": "{{ $json.task_num }}",
  "task_title": "{{ $json.content }}",
  "phase_slug": "{{ $json.phase_slug }}",
  "context_hint": ""
}
```

### 2단계: JS 노드 수정

기존 `JS_CreateTaskPlanAndTestPlan1` 노드를 삭제하거나 수정합니다.

**새로운 노드 이름**: `JS_ProcessApiResponse`

**코드**:

```javascript
// HTTP Request 응답에서 Task Plan과 Test Plan 추출
const item = $input.first().json;
const httpResponse = $('HTTP_GenerateTaskPlan').item.json;

const task_num = String(item.task_num || '').trim();
const content = item.content || '';
const phaseId = item.phase_id ?? 1;
const phaseDirId = String(item.phase_dir_id || 'phase-8-0').trim();
const phaseSlug = String(item.phase_slug || '').trim();

// API 응답에서 Plan 추출
const taskPlan = httpResponse.task_plan || `# Task Plan: ${content}\n\n(생성 실패)`;
const testPlan = httpResponse.test_plan || `# Test Plan: ${content}\n\n(생성 실패)`;

// 파일 경로 계산
const b64 = (s) => Buffer.from(s, 'utf8').toString('base64');
const taskDirPath = `docs/phases/${phaseDirId}/tasks`;
const planFilename = `phase${task_num}-task.md`;
const testFilename = `phase${task_num}-task-test-result.md`;
const planMdPath = `${taskDirPath}/${planFilename}`;
const testPlanMdPath = `${taskDirPath}/${testFilename}`;

return [{
  json: {
    index: item.index,
    content,
    phase_id: phaseId,
    phase_dir_id: phaseDirId,
    phase_slug: phaseSlug,
    task_num,
    task_name: content.trim().substring(0, 80),
    plan_doc: taskPlan,
    test_plan_doc: testPlan,
    plan_md_path: planMdPath,
    test_plan_md_path: testPlanMdPath,
    task_dir_path: taskDirPath,
    plan_filename: planFilename,
    test_filename: testFilename,
    plan_b64: b64(taskPlan),
    test_b64: b64(testPlan),
    analyzed_files: httpResponse.analyzed_files || [],
    api_success: httpResponse.success || false
  }
}];
```

### 3단계: 노드 연결 수정

```
LOOP_TodoItems → HTTP_GenerateTaskPlan → JS_ProcessApiResponse → CMD_WriteTaskFiles → ...
```

---

## API 명세

### POST /api/workflow/generate-task-plan

**Request Body:**

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| task_num | string | O | Task 번호 (예: "8-2-7") |
| task_title | string | O | Task 제목 |
| phase_slug | string | O | Phase 식별자 (예: "phase-8-2") |
| context_hint | string | X | 추가 컨텍스트 힌트 |

**Response:**

```json
{
  "success": true,
  "task_plan": "# Task Plan: ...\n\n## 목표\n...",
  "test_plan": "# Test Plan: ...\n\n## 테스트 범위\n...",
  "analyzed_files": [
    "backend/config.py",
    "backend/routers/automation/workflow.py"
  ],
  "error": null
}
```

---

## 동작 흐름

1. **Claude Code CLI 확인**: CLI 설치 및 인증 토큰 확인
2. **키워드 추출**: Task 제목에서 검색 키워드 추출
3. **파일 검색**: 프로젝트 내 관련 파일 탐색
4. **컨텍스트 수집**: 관련 파일 내용 수집 (최대 20KB)
5. **Claude 생성**: Claude Code CLI로 Task Plan/Test Plan 생성
6. **오류 시**: 토큰 없음 등의 오류 메시지 반환 (폴백 템플릿 없음)

---

## 테스트 방법

### cURL로 API 직접 테스트

```bash
curl -X POST http://localhost:8000/api/workflow/generate-task-plan \
  -H "Content-Type: application/json" \
  -d '{
    "task_num": "8-2-9",
    "task_title": "Backend 설정 관리 기능 추가",
    "phase_slug": "phase-8-2",
    "context_hint": "config settings backend"
  }'
```

### 응답 예시

```json
{
  "success": true,
  "task_plan": "# Task Plan: Backend 설정 관리 기능 추가\n\n## 목표\nBackend 설정을 동적으로 관리할 수 있는 API를 추가한다.\n\n## 관련 파일\n- backend/config.py: 현재 설정 정의\n- backend/routers/system/system.py: 시스템 관련 API\n\n## 구현 단계\n1. **설정 모델 정의**: settings 테이블 및 Pydantic 모델 추가\n2. **서비스 레이어**: settings_service.py 생성\n3. **API 엔드포인트**: GET/PUT /api/system/settings 추가\n...",
  "test_plan": "# Test Plan: Backend 설정 관리 기능 추가\n\n## 테스트 범위\n...",
  "analyzed_files": ["backend/config.py", "backend/routers/system/system.py"],
  "error": null
}
```

---

## 주의사항

1. **Claude Code CLI 필수**: Task Plan 생성을 위해 Claude Code CLI가 설치되고 인증되어 있어야 합니다.
2. **인증 토큰 필요**: Claude Code CLI 인증이 없으면 `"Claude Code 인증 토큰이 없습니다"` 오류가 반환됩니다.
   - 인증 방법: `claude login` 명령 실행
3. **타임아웃**: API 응답 시간이 길 수 있으므로 HTTP Request 노드의 타임아웃을 충분히 설정하세요 (권장: 300초).
4. **Ollama 미사용**: 이 API는 Ollama를 사용하지 않습니다. Claude Code CLI만 사용합니다.

---

## 파일 위치

- **API 엔드포인트**: `backend/routers/automation/workflow.py`
- **Task Plan 생성기**: `backend/services/automation/task_plan_generator.py`
- **프로젝트 분석기**: `backend/services/automation/project_analyzer.py`
- **테스트**: `tests/test_task_plan_generator.py`
