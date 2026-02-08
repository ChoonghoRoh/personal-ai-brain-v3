# Phase 8-2-8: Task 테스트 및 결과 저장 워크플로우 플랜

**작성일**: 2026-01-28  
**기반 문서**: phase8-2-7-task-execution-workflow.md  
**관련 문서**: phase8-2-6-task-test-plan-generation.md, phase8-master-plan.md

---

## 📋 개요

Phase 8-2-8은 **8-2-7(Task 실행)이 완료된 Task에 대해**, 결과물을 테스트하고 그 결과를 저장하는 워크플로우를 구축하기 위한 **플랜** 문서입니다.

**우선순위**: High  
**예상 소요 시간**: 1.5–2일  
**의존성**: Phase 8-2-7 완료 (Task 실행 워크플로우 동작 후)

---

## 🎯 목표

1. **입력**: 8-2-7 완료 Task (`workflow_tasks.status = 'completed'`, `task_id`, `task-N-test.md`)
2. **테스트**: Task Plan으로 변경된 결과물을 `task-N-test.md`(Test Plan) 기준으로 실행
3. **저장**: 테스트 결과를 `workflow_test_results` 테이블 및 `task-N-result.md` 파일에 저장
4. **알림**: (선택) Discord로 테스트 결과 요약 전송

---

## 🔄 워크플로우 구조

```
[8-2-7 완료 트리거 또는 Manual Trigger]
    ↓
[PostgreSQL] (status='completed' 이면서 아직 테스트 결과 없는 Task 조회)
    ↓
[Code] (task_id, task_name, test_plan_doc, plan_doc 정리)
    ↓
[Execute Command] 또는 [HTTP Request]
    → run_task_test.py (또는 run_task_test.sh) 호출
    → 인자: task_id, test_plan_doc 경로 또는 내용
    ↓
[스크립트 내부]
    → Test Plan에 따라 테스트 실행 (pytest / Claude로 테스트 수행 등)
    → 결과 수집 (pass/fail, 로그, 요약)
    ↓
[PostgreSQL] (workflow_test_results INSERT)
    ↓
[Write Binary File] (task-N-result.md 생성, 선택)
    ↓
[Discord Webhook] (테스트 결과 요약, 선택)
    ↓
[다음 Task 또는 Phase 완료 처리]
```

---

## 📝 작업 목록 (플랜)

### 1. 테스트 실행 스크립트 설계

**파일**: `scripts/n8n/run_task_test.py` (예정)

**역할**:

- 인자: `--task-id N` 또는 `--test-file path/to/task-N-test.md`
- DB에서 해당 Task의 `test_plan_doc`, `plan_doc` 조회 (필요 시)
- Test Plan 내용에 따라:
  - **옵션 A**: 프로젝트에서 `pytest` 등 실제 테스트 명령 실행, 결과 파싱
  - **옵션 B**: Claude API에 "다음 Test Plan대로 현재 코드베이스를 테스트하고 결과를 정리하라" 요청 후 결과 텍스트 수집
- 결과를 구조화 (status: pass/fail/error, result_doc: 상세 로그/요약)
- `workflow_test_results`에 INSERT
- (선택) `docs/phases/tasks/task-N-result.md` 파일로 저장

**완료 기준**:

- [ ] run_task_test.py로 Task 1건에 대해 테스트 실행 → DB 저장까지 동작

---

### 2. workflow_test_results 저장 형식

**테이블**: `workflow_test_results` (기존 스키마)

| 컬럼 | 용도 |
|------|------|
| task_id | workflow_tasks.id |
| test_type | 'auto' (자동 테스트) / 'manual' (수동 검토) 등 |
| status | 'pass' / 'fail' / 'error' |
| result_doc | 테스트 로그, 요약, 실패 사유 등 TEXT |
| tested_at | NOW() |

**저장 시점**: run_task_test.py 내부에서 DB 연결 후 INSERT.

---

### 3. task-N-result.md 생성 (선택)

**경로**: `docs/phases/tasks/task-{{ N }}-result.md`

**내용 예**:

- 테스트 일시
- Test Plan 요약
- 실행 결과 (pass/fail)
- 상세 로그 또는 요약
- (선택) 보완 필요 사항

n8n의 Write Binary File 노드로 생성하거나, run_task_test.py에서 직접 작성해도 됨.

---

### 4. n8n 워크플로우 노드 (플랜)

| 순서 | 노드 | 설명 |
|------|------|------|
| 1 | Trigger | 8-2-7 완료 Webhook 또는 Manual |
| 2 | PostgreSQL | completed Task 중 workflow_test_results에 없는 task_id 1건 조회 |
| 3 | IF | 결과 있음 → 테스트 분기 |
| 4 | Execute Command | `python scripts/n8n/run_task_test.py --task-id {{ $json.id }}` |
| 5 | (선택) Read Binary File | task-N-result.md 읽기 |
| 6 | (선택) Discord Webhook | 테스트 결과 요약 전송 |
| 7 | Loop / 다음 단계 | 남은 Task 반복 또는 Phase 완료 처리 |

- 테스트 실패 시: status='fail'로 저장, Discord 알림 권장.

---

### 5. Test Plan .md와의 연동

8-2-6에서 생성한 `task-N-test.md` 형식이 다음을 포함하면 run_task_test.py에서 파싱하기 쉽습니다.

- 테스트 시나리오 목록
- 테스트 케이스 (예: "API GET /health 200 확인")
- 예상 결과
- (가능하면) 실행할 명령 예: `pytest tests/test_foo.py -v`

run_task_test.py 1차 버전에서는 **고정 명령**(예: `pytest`) 또는 **Claude에게 Test Plan 전체를 넘겨 결과만 받기**로 단순화한 뒤, 점진적으로 Test Plan 파싱을 추가할 수 있습니다.

---

## ✅ 완료 기준 (플랜 기준)

- [ ] `scripts/n8n/run_task_test.py` 설계 및 구현 (Task 1건 테스트 → DB 저장)
- [ ] workflow_test_results에 테스트 결과 저장 확인
- [ ] (선택) task-N-result.md 자동 생성
- [ ] n8n에서 8-2-7 완료 후 본 워크플로우 트리거 연동
- [ ] (선택) Discord 테스트 결과 알림
- [ ] 문서: 테스트 실행 방법 및 실패 시 확인 사항

---

## ⚠️ 리스크 및 대응

| 리스크 | 대응 |
|--------|------|
| Test Plan이 자연어라 자동 실행 불가 | 1차는 Claude에게 "Test Plan대로 검증하고 결과만 텍스트로 제출"하게 하고, 점진적으로 pytest 등 고정 명령 연동 |
| 테스트 환경 차이 | 동일 Docker/venv에서 실행하도록 Execute Command 작업 디렉토리·환경 명시 |
| 장시간 테스트 | 타임아웃 설정, 실패 시 status='error', result_doc에 타임아웃 기록 |

---

## 📝 다음 단계

- Phase 8-2-7이 완료되면 본 플랜(8-2-8)에 따라 **run_task_test.py 및 n8n 워크플로우**를 순서대로 구현.
- 모든 Task에 대해 테스트·저장이 끝나면 Phase 8-3(개발 시작/완료 감지) 또는 Phase 8-4(종합 보고서)와 연동 검토.

---

## 🔗 관련 문서

- `phase8-2-7-task-execution-workflow.md` - Task 실행 워크플로우
- `phase8-2-6-task-test-plan-generation.md` - Task/Test Plan 생성
- `phase8-1-1-database-schema-n8n-setting.md` - workflow_test_results 스키마
- `phase8-master-plan.md` - Phase 8 전체 (docs/phases/phase8-master-plan.md)

---

**문서 버전**: 1.0  
**최종 업데이트**: 2026-01-28
