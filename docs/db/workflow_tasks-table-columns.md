# workflow_tasks 테이블 컬럼 구조 및 용도

**확인 일시:** 마이그레이션 `migrate_workflow_tasks_plan_md_path.sql` 실행 후 조회.

---

## 1. 현재 컬럼 구조 (9개)

| # | 컬럼명 | 타입 | Nullable | 기본값 | 용도 |
|---|--------|------|----------|--------|------|
| 1 | **id** | integer | NO | `nextval('workflow_tasks_id_seq')` | PK. Task 실행·갱신 시 조회/UPDATE 대상. |
| 2 | **phase_id** | integer | YES | - | FK → workflow_phases(id). Phase 소속. **Task Plan Generation v2는 phase_slug만 INSERT, phase_id 생략.** |
| 2a | **task_num** | varchar(50) | YES | - | **고유 Task 번호**(예: 8-1-1, 1-1-2). UNIQUE. phase_slug-index 형식. 마이그레이션 `migrate_workflow_tasks_task_num.sql`. |
| 2b | **phase_slug** | varchar(50) | YES | - | Phase 식별자(예: 8-0, 1-1). Phase별 그룹/필터용. |
| 3 | **task_name** | varchar(100) | YES | - | Task 이름. 완료/실패 메시지·로그·UI 표시용. |
| 4 | **status** | varchar(20) | YES | `'pending'` | `pending` → `in_progress` → `completed` / `failed`. Task Execution이 갱신. |
| 5 | **plan_doc** | text | YES | - | Task Plan 전문(마크다운). **plan_md_path가 없을 때만** Backend가 CLI에 이 텍스트 전달. |
| 6 | **test_plan_doc** | text | YES | - | Test Plan 전문. **현재 Task Execution(8-2-7)에서는 미사용.** Phase 8-2-8(테스트 실행·저장)에서 사용 예정. |
| 7 | **created_at** | timestamp | YES | `now()` | Task 등록 시각. |
| 8 | **completed_at** | timestamp | YES | - | Task Execution이 status를 completed/failed로 바꿀 때 `NOW()` 로 설정. |
| 9 | **plan_md_path** | varchar(500) | YES | - | Task Plan .md **파일 경로**(workspace 기준 상대). **있으면** Backend는 이 경로만 Claude CLI에 전달하고, CLI가 해당 파일을 읽어 실행. |

**인덱스:** `workflow_tasks_pkey` (id), `idx_workflow_tasks_phase_id`, `idx_workflow_tasks_status`  
**FK:** `phase_id` → workflow_phases(id) ON DELETE CASCADE  
**참조:** workflow_test_results.task_id → workflow_tasks(id)

---

## 2. 컬럼별 용도 요약

| 컬럼 | 사용처 | 비고 |
|------|--------|------|
| id | Backend run_task, n8n SELECT/UPDATE | 필수 |
| phase_id | (선택) n8n INSERT, Phase별 목록/필터 | v2 Generation은 phase_slug만 사용, phase_id NULL |
| task_num | n8n INSERT(고유 Task 번호 8-1-1, 1-1-2) | UNIQUE. Task 단위 식별·중복 방지 |
| phase_slug | n8n INSERT(phase 번호), Phase별 그룹/필터 | workflow_phases FK 없이 사용 |
| task_name | Backend 완료 메시지, n8n·UI | 필수 |
| status | n8n SELECT(pending), Backend UPDATE | 필수 |
| plan_doc | Backend run_task (plan_md_path 없을 때) | plan_md_path 있으면 미사용 가능(중복) |
| test_plan_doc | 8-2-8 테스트 실행 예정 | 현재 8-2-7에서는 미사용 |
| created_at | 등록 시각 | 유지 권장 |
| completed_at | 완료 시각 | 유지 권장 |
| plan_md_path | Backend run_task (경로 기반 실행) | 있으면 plan_doc 대신 경로만 전달 |

---

## 3. 불필요·중복 가능성 체크

| 항목 | 판단 | 조치 제안 |
|------|------|------------|
| **plan_doc vs plan_md_path** | **중복 가능** | plan_md_path가 있으면 같은 내용이 디스크 .md와 plan_doc 양쪽에 존재. 경로 기반만 쓸 경우 plan_doc을 비우고 경로만 저장하는 정책 가능(선택). |
| **test_plan_doc** | **현재 미사용** | 8-2-8에서 사용 예정이면 유지. 당분간 사용 계획 없으면 NULL 허용 유지만 해도 됨. |
| **phase_id** | **실행 로직에 불필요** | Phase별 그룹·필터용이므로 스키마상 유지. 삭제 시 workflow_phases와의 관계가 깨짐. |
| **status 길이** | varchar(20) | `pending`, `in_progress`, `completed`, `failed` 만 사용하면 충분. 변경 불필요. |
| **task_name 길이** | varchar(100) | 80자 제한 등으로 잘라서 넣고 있으면 충분. 변경 불필요. |

---

## 4. 결론

- **삭제 권장 컬럼:** 없음. (test_plan_doc은 8-2-8에서 사용 예정.)
- **중복 완화(선택):** plan_md_path를 쓰는 Task는 plan_doc을 NULL로 두고 “경로만 저장” 하면 디스크와 DB 내용 중복을 줄일 수 있음. 기존 n8n 워크플로우는 두 값 다 넣고 있으므로, “경로만 넣기”로 바꾸려면 Generation 워크플로우에서 plan_doc INSERT 제거 또는 NULL 처리 필요.
- **마이그레이션:** `plan_md_path` 추가는 적용 완료. 신규 Task는 plan_md_path를 넣어 경로 기반 실행 가능.
