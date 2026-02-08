# DBeaver에서 PostgreSQL 접속 가이드

## 📋 개요

DBeaver GUI를 사용하여 Docker로 실행 중인 PostgreSQL 데이터베이스에 접속하는 방법입니다.

## 🔧 연결 정보

### 메인 데이터베이스 (knowledge)

- **호스트**: `localhost`
- **포트**: `5432`
- **데이터베이스**: `knowledge`
- **사용자**: `brain`
- **비밀번호**: `brain_password`

### n8n 데이터베이스

- **호스트**: `localhost`
- **포트**: `5432`
- **데이터베이스**: `n8n`
- **사용자**: `brain`
- **비밀번호**: `brain_password`

## 🚀 DBeaver 연결 설정

### Step 1: 새 데이터베이스 연결 생성

1. **DBeaver 실행**
2. 상단 메뉴에서 **"Database"** → **"New Database Connection"** 클릭
   - 또는 `Cmd+Shift+N` (Mac) / `Ctrl+Shift+N` (Windows)
3. **"PostgreSQL"** 선택 후 **"Next"** 클릭

### Step 2: 연결 정보 입력

**Main 탭:**

```
Host: localhost
Port: 5432
Database: knowledge
Username: brain
Password: brain_password
```

**고급 설정 (선택사항):**

- **Show all databases**: 체크 (모든 데이터베이스 보기)
- **Save password**: 체크 (비밀번호 저장)

### Step 3: 드라이버 다운로드 (최초 1회)

1. **"Download"** 버튼 클릭
2. PostgreSQL 드라이버 자동 다운로드 및 설치
3. 완료 후 **"Test Connection"** 클릭

### Step 4: 연결 테스트

1. **"Test Connection"** 버튼 클릭
2. "Connected" 메시지 확인
3. **"Finish"** 클릭

## 📊 데이터베이스 탐색

### 스키마 확인

1. **Database Navigator**에서 연결 확장
2. **Databases** → **knowledge** → **Schemas** → **public** 확장
3. **Tables** 폴더에서 모든 테이블 확인

### 주요 테이블 목록

**knowledge 데이터베이스:**
- `workflow_phases` - Phase 정보 관리
- `workflow_plans` - Plan 문서 저장
- `workflow_approvals` - 승인 루프 관리
- `workflow_tasks` - Task 정보
- `workflow_test_results` - 테스트 결과
- `projects` - 프로젝트 정보
- `documents` - 문서 메타데이터
- `knowledge_chunks` - 지식 조각 정보
- `labels` - 라벨 정의
- `knowledge_labels` - 청크-라벨 관계
- `knowledge_relations` - 지식 관계

**n8n 데이터베이스:**
- `workflow_entity` - n8n 워크플로우
- `credentials_entity` - n8n credentials
- `execution_entity` - 실행 기록

### 테이블 구조 확인

1. 테이블 더블클릭 또는 우클릭 → **"View Data"**
2. 테이블 구조 확인: 우클릭 → **"Properties"** → **"Columns"** 탭

### SQL 쿼리 실행

1. 상단 메뉴에서 **"SQL Editor"** → **"New SQL Script"** 클릭
2. SQL 쿼리 작성
3. **"Execute SQL Statement"** 버튼 클릭 (또는 `Cmd+Enter` / `Ctrl+Enter`)

**예제 쿼리:**

```sql
-- workflow_phases 테이블 조회
SELECT * FROM workflow_phases;

-- 테이블 목록 확인
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- 테이블 구조 확인
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public' 
  AND table_name = 'workflow_phases'
ORDER BY ordinal_position;
```

## 🔄 여러 데이터베이스 연결

### n8n 데이터베이스 추가 연결

1. **"New Database Connection"** 다시 생성
2. **Database**만 `n8n`으로 변경
3. 나머지 설정은 동일

## 🛠️ 문제 해결

### 연결 실패 시

1. **PostgreSQL 컨테이너 실행 확인:**
   ```bash
   docker compose ps postgres
   ```

2. **포트 확인:**
   ```bash
   lsof -i :5432
   ```

3. **컨테이너 재시작:**
   ```bash
   docker compose restart postgres
   ```

### 드라이버 오류

1. **DBeaver** → **Window** → **Preferences**
2. **Connections** → **Drivers** → **PostgreSQL**
3. **"Download/Update"** 클릭하여 드라이버 재다운로드

### 비밀번호 저장 안 됨

1. 연결 우클릭 → **"Edit Connection"**
2. **"Save password"** 체크
3. 비밀번호 다시 입력 후 **"Test Connection"**

## 📝 유용한 기능

### ER 다이어그램 생성

1. 데이터베이스 우클릭 → **"View Diagram"**
2. 테이블 간 관계 시각화

### 데이터 내보내기/가져오기

1. 테이블 우클릭 → **"Export Data"** / **"Import Data"**
2. CSV, Excel, JSON 등 다양한 형식 지원

### SQL 히스토리

1. **Window** → **Show View** → **SQL History**
2. 실행한 모든 SQL 쿼리 기록 확인

## 🔗 관련 문서

- [database-console-access.md](./database-console-access.md) - 콘솔 접속 방법
- [database-schema.md](./database-schema.md) - 데이터베이스 스키마
- [phase8-1-1-database-schema-n8n-setting.md](../phases/phase-8-0/phase8-1-1-database-schema-n8n-setting.md) - workflow 테이블 스키마

---

**작성일**: 2026-01-28  
**버전**: 1.0
