-- Phase 8-2-6 테스트용: workflow_phases 1건 + workflow_tasks 2건 INSERT
-- 실행: docker exec -i pab-postgres psql -U brain -d knowledge < scripts/insert_test_tasks.sql
-- 또는 psql -U brain -d knowledge -f scripts/insert_test_tasks.sql

-- 1) Phase 없으면 생성
INSERT INTO workflow_phases (phase_name, status, created_at)
SELECT 'Phase-8-Test', 'draft', NOW()
WHERE NOT EXISTS (SELECT 1 FROM workflow_phases WHERE phase_name = 'Phase-8-Test');

-- 2) phase_id 조회 후 Task 2건 INSERT (phase_id = Phase-8-Test 의 id)
INSERT INTO workflow_tasks (phase_id, task_name, status, plan_doc, test_plan_doc, created_at)
SELECT p.id, '테스트 Task 1: README.md 존재 확인', 'pending',
'# Task Plan: 테스트 Task 1: README.md 존재 확인

## 목표
README.md 존재 여부를 확인한다.

## 단계
1. 프로젝트 루트에서 README.md 파일 확인
2. 없으면 생성, 있으면 통과
3. 완료 기준 충족 확인

## 완료 기준
- README.md 파일이 존재함
',
'# Test Plan: 테스트 Task 1

## 테스트 시나리오
- README.md 파일 존재 여부 확인

## 예상 결과
- README.md가 프로젝트 루트에 존재함
',
NOW()
FROM workflow_phases p WHERE p.phase_name = 'Phase-8-Test' LIMIT 1;

INSERT INTO workflow_tasks (phase_id, task_name, status, plan_doc, test_plan_doc, created_at)
SELECT p.id, '테스트 Task 2: docs/phases/tasks 폴더 생성', 'pending',
'# Task Plan: 테스트 Task 2: docs/phases/tasks 폴더 생성

## 목표
docs/phases/tasks 폴더를 생성한다.

## 단계
1. docs/phases/tasks 경로 확인
2. 없으면 mkdir -p로 생성
3. 완료 기준 충족 확인

## 완료 기준
- docs/phases/tasks 디렉토리가 존재함
',
'# Test Plan: 테스트 Task 2

## 테스트 시나리오
- docs/phases/tasks 디렉토리 존재 여부 확인

## 예상 결과
- docs/phases/tasks 폴더가 생성됨
',
NOW()
FROM workflow_phases p WHERE p.phase_name = 'Phase-8-Test' LIMIT 1;
