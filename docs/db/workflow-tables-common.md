# workflow 관련 테이블 공통 컬럼 및 DDL 규약

phases, plans, tasks, test_results 4개 테이블 컬럼 조회 결과를 바탕으로 공통 패턴을 정리하고, 코드화·신규 테이블 DDL 시 재사용할 수 있도록 함.

**코드화 위치:**
- **Python:** `backend/models/workflow_common.py` — 공통 컬럼명 상수, 테이블명, Phase/Plan/Task/TestResult 상태 Enum
- **DDL 참고:** `scripts/db/workflow_common_ddl.sql` — 신규 workflow 테이블 생성 시 복사용 DDL 조각

---

## 1. 4개 테이블 컬럼 매트릭스

| 공통 패턴 | workflow_phases | workflow_plans | workflow_tasks | workflow_test_results |
|-----------|-----------------|---------------|----------------|------------------------|
| **PK** | id SERIAL | id SERIAL | id SERIAL | id SERIAL |
| **상태** | status VARCHAR(20) DEFAULT 'draft' | status VARCHAR(20) DEFAULT 'draft' | status VARCHAR(20) DEFAULT 'pending' | status VARCHAR(20) |
| **등록 시각** | created_at TIMESTAMP DEFAULT NOW() | created_at TIMESTAMP DEFAULT NOW() | created_at TIMESTAMP DEFAULT NOW() | tested_at TIMESTAMP DEFAULT NOW() |
| **종료/완료 시각** | started_at, completed_at | approved_at | completed_at | (tested_at가 종료 시각 겸함) |
| **부모 FK** | - | phase_id → phases | phase_id → phases | task_id → tasks |
| **문서형 TEXT** | current_state_md, gap_analysis_md | content | plan_doc, test_plan_doc | result_doc |
| **기타** | phase_name VARCHAR(50) | version INT, approved_at | task_name, plan_md_path | test_type VARCHAR(20) |

---

## 2. 공통으로 쓸 수 있는 부분 (Common)

| 구분 | 컬럼/규칙 | 타입/기본값 | 비고 |
|------|-----------|-------------|------|
| **PK** | id | SERIAL PRIMARY KEY | 4개 테이블 동일 |
| **상태** | status | VARCHAR(20), 테이블별 default 상이 | phases/plans: 'draft', tasks: 'pending', test_results: 없음 |
| **등록 시각** | created_at | TIMESTAMP DEFAULT NOW() | test_results만 `tested_at` 이름 사용 |
| **종료 시각** | completed_at / approved_at / tested_at | TIMESTAMP | 테이블별 컬럼명만 다름 |
| **인덱스** | status, 부모 FK | btree | status·부모 id 인덱스 공통 권장 |

**공통 DDL 조각 (신규 workflow 테이블 생성 시 복사용):**

```sql
id          SERIAL PRIMARY KEY,
status      VARCHAR(20) DEFAULT 'pending',   -- 테이블별 default 변경
created_at  TIMESTAMP DEFAULT NOW(),
completed_at TIMESTAMP,                       -- 또는 approved_at, tested_at 등 테이블별 이름
-- 부모 FK가 있으면:
-- parent_id INT REFERENCES workflow_xxx(id) ON DELETE CASCADE,
```

---

## 3. 테이블별 status 허용값 (코드화용)

| 테이블 | 기본값 | 허용값 예시 |
|--------|--------|-------------|
| workflow_phases | draft | draft, in_progress, completed |
| workflow_plans | draft | draft, approved |
| workflow_tasks | pending | pending, in_progress, completed, failed |
| workflow_test_results | (없음) | pending, passed, failed 등 |

---

## 4. Common Table (물리 테이블) vs 코드 공통화

- **물리 Common Table:**  
  공통 컬럼만 모은 `workflow_common(id, status, created_at, completed_at)` 테이블을 만들고, phases/plans/tasks/test_results가 `common_id` FK로 참조하는 방식은 스키마 변경·마이그레이션이 크므로 **현재는 적용하지 않음**.
- **코드 공통화:**  
  컬럼명·status 값·타입을 **Python 상수/Enum**으로 정의하고, SQL 문자열·ORM에서 재사용. 신규 workflow 테이블 DDL 작성 시 위 공통 DDL 조각을 참고하여 일관되게 생성.

---

## 5. 참고: workflow_approvals

| 컬럼 | 타입 | 비고 |
|------|------|------|
| id | SERIAL PK | 공통 |
| phase_id | INT FK → workflow_phases | 공통(부모 FK) |
| step, version, feedback, approved | 각각 타입 상이 | 승인 전용 |
| created_at | TIMESTAMP DEFAULT NOW() | 공통 |

status 컬럼은 없고, `approved` BOOLEAN으로 승인 여부만 가짐.
