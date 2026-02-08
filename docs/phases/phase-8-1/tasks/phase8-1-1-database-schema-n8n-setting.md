Step 1: PostgreSQL 테이블 생성
1-1. PostgreSQL 접속
bashdocker exec -it pab-postgres psql -U brain -d knowledge
비밀번호 입력: brain_password
1-2. 테이블 생성 SQL 실행
접속 후 다음 SQL을 복사해서 붙여넣으세요:
sql-- 1. phases 테이블
CREATE TABLE workflow_phases (
id SERIAL PRIMARY KEY,
phase_name VARCHAR(50) NOT NULL,
status VARCHAR(20) DEFAULT 'draft',
current_state_md TEXT,
gap_analysis_md TEXT,
created_at TIMESTAMP DEFAULT NOW(),
started_at TIMESTAMP,
completed_at TIMESTAMP
);

-- 2. plans 테이블
CREATE TABLE workflow_plans (
id SERIAL PRIMARY KEY,
phase_id INT REFERENCES workflow_phases(id) ON DELETE CASCADE,
version INT DEFAULT 1,
content TEXT,
status VARCHAR(20) DEFAULT 'draft',
created_at TIMESTAMP DEFAULT NOW(),
approved_at TIMESTAMP
);

-- 3. approvals 테이블
CREATE TABLE workflow_approvals (
id SERIAL PRIMARY KEY,
phase_id INT REFERENCES workflow_phases(id) ON DELETE CASCADE,
step VARCHAR(50),
version INT,
feedback TEXT,
approved BOOLEAN,
created_at TIMESTAMP DEFAULT NOW()
);

-- 4. tasks 테이블
CREATE TABLE workflow_tasks (
id SERIAL PRIMARY KEY,
phase_id INT REFERENCES workflow_phases(id) ON DELETE CASCADE,
task_name VARCHAR(100),
status VARCHAR(20) DEFAULT 'pending',
plan_doc TEXT,
test_plan_doc TEXT,
plan_md_path VARCHAR(500),
created_at TIMESTAMP DEFAULT NOW(),
completed_at TIMESTAMP
);
-- plan_md_path: Task Plan .md 파일 경로(workspace 기준). 있으면 Backend가 이 경로만 Claude CLI에 전달 (경로 기반 실행).
-- 기존 테이블에 추가 시: scripts/db/migrate_workflow_tasks_plan_md_path.sql 참고.

-- 5. test_results 테이블
CREATE TABLE workflow_test_results (
id SERIAL PRIMARY KEY,
task_id INT REFERENCES workflow_tasks(id) ON DELETE CASCADE,
test_type VARCHAR(20),
status VARCHAR(20),
result_doc TEXT,
tested_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX idx*workflow_phases_status ON workflow_phases(status);
CREATE INDEX idx_workflow_plans_phase_id ON workflow_plans(phase_id);
CREATE INDEX idx_workflow_tasks_phase_id ON workflow_tasks(phase_id);
CREATE INDEX idx_workflow_tasks_status ON workflow_tasks(status);
1-3. 테이블 확인
sql-- 생성된 테이블 목록
\dt workflow*\*

-- 각 테이블 구조 확인
\d workflow_phases
1-4. 종료
sql\q

```

**선택: 컨텍스트 절약용 요약 컬럼**  
다음 단계(Gap/Plan)에서 LLM 컨텍스트를 아끼려면, 요약만 넣을 컬럼을 추가할 수 있습니다. (가이드: [phase8-2-1-code-analysis-workflow-guide.md](./phase8-2-1-code-analysis-workflow-guide.md) 참고)

```sql
ALTER TABLE workflow_phases ADD COLUMN IF NOT EXISTS current_state_summary TEXT;
-- current_state_summary: 4000자 등 짧은 요약. Gap/Plan 단계에서는 이 컬럼만 사용 권장.
```

---

## Step 2: n8n PostgreSQL Credentials 등록

### 2-1. n8n에서 Credential 추가

1. **n8n > Credentials > Add Credential**
2. **"Postgres" 검색 및 선택**
3. **입력:**
```

Credential Name: PostgreSQL - PAB Knowledge
Host: localhost
Database: knowledge
User: brain
Password: brain_password
Port: 5432
SSL: disable

"Save" 클릭

⚠️ 만약 "Connection failed" 에러가 나면:

Host를 pab-postgres로 변경해보세요
또는 host.docker.internal (Mac/Windows)

Step 3: n8n 연결 테스트
3-1. 테스트 워크플로우 생성

n8n > 새 워크플로우: "PostgreSQL Test"
Manual Trigger 노드 추가
Postgres 노드 추가:

Credential: PostgreSQL - PAB Knowledge
Operation: Execute Query
Query:

sql SELECT
table*name,
table_type
FROM information_schema.tables
WHERE table_name LIKE 'workflow*%'
ORDER BY table_name;

```
4. **Execute Workflow** 클릭

**예상 결과:**
```

workflow_approvals
workflow_phases
workflow_plans
workflow_tasks
workflow_test_results

Step 4: CRUD 테스트
4-1. INSERT 테스트
새 Postgres 노드 추가:
Query:
sqlINSERT INTO workflow_phases (phase_name, status)
VALUES ('Phase-Test', 'draft')
RETURNING _;
Execute → 생성된 레코드 확인
4-2. SELECT 테스트
Query:
sqlSELECT _ FROM workflow_phases;
4-3. UPDATE 테스트
Query:
sqlUPDATE workflow_phases
SET status = 'in_progress', started_at = NOW()
WHERE phase_name = 'Phase-Test'
RETURNING _;
4-4. DELETE 테스트
Query:
sqlDELETE FROM workflow_phases
WHERE phase_name = 'Phase-Test'
RETURNING _;

완료 체크리스트 ✅

PostgreSQL에 5개 테이블 생성
n8n에 PostgreSQL Credential 등록
테이블 목록 조회 성공
INSERT 쿼리 작동
SELECT 쿼리 작동
UPDATE 쿼리 작동
