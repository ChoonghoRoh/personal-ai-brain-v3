# Docker PostgreSQL에서 테이블 및 컬럼 생성 가이드

## 1. 기본 접속 방법

### 대화형 psql 세션
```bash
docker exec -it pab-postgres psql -U brain -d knowledge
```

### 단일 쿼리 실행
```bash
docker exec pab-postgres psql -U brain -d knowledge -c "YOUR_SQL_QUERY"
```

## 2. 테이블 생성 (CREATE TABLE)

### 기본 테이블 생성 예제
```sql
-- 간단한 테이블 생성
CREATE TABLE example_table (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 외래키가 있는 테이블 생성
```sql
-- projects 테이블 참조하는 테이블
CREATE TABLE example_with_fk (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 인덱스와 함께 테이블 생성
```sql
CREATE TABLE example_indexed (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성
CREATE INDEX idx_example_indexed_status ON example_indexed(status);
CREATE INDEX idx_example_indexed_name ON example_indexed(name);
```

### 실제 프로젝트 예제 (기존 모델 기반)
```sql
-- projects 테이블 생성 (이미 존재할 수 있음)
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    path VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_projects_name ON projects(name);
```

## 3. 컬럼 추가 (ALTER TABLE ADD COLUMN)

### 기본 컬럼 추가
```sql
-- 단일 컬럼 추가
ALTER TABLE knowledge_chunks 
ADD COLUMN new_column VARCHAR(255);
```

### 기본값이 있는 컬럼 추가
```sql
-- 기본값과 함께 컬럼 추가
ALTER TABLE knowledge_chunks 
ADD COLUMN status VARCHAR(50) DEFAULT 'draft' NOT NULL;
```

### NULL 허용 컬럼 추가
```sql
-- NULL 허용 컬럼 추가
ALTER TABLE knowledge_chunks 
ADD COLUMN optional_field TEXT;
```

### 타임스탬프 컬럼 추가
```sql
-- 타임스탬프 컬럼 추가
ALTER TABLE knowledge_chunks 
ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
```

### 외래키 컬럼 추가
```sql
-- 외래키 컬럼 추가
ALTER TABLE documents 
ADD COLUMN category_label_id INTEGER REFERENCES labels(id);
```

### IF NOT EXISTS 사용 (PostgreSQL 9.5+)
```sql
-- 컬럼이 없을 때만 추가 (에러 방지)
ALTER TABLE knowledge_chunks 
ADD COLUMN IF NOT EXISTS new_column VARCHAR(255);
```

## 4. 실제 사용 예제

### 예제 1: 새 테이블 생성
```bash
docker exec pab-postgres psql -U brain -d knowledge -c "
CREATE TABLE IF NOT EXISTS user_preferences (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    preference_key VARCHAR(255) NOT NULL,
    preference_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, preference_key)
);

CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);
"
```

### 예제 2: 기존 테이블에 컬럼 추가
```bash
docker exec pab-postgres psql -U brain -d knowledge -c "
ALTER TABLE knowledge_chunks 
ADD COLUMN IF NOT EXISTS priority INTEGER DEFAULT 0;

ALTER TABLE knowledge_chunks 
ADD COLUMN IF NOT EXISTS tags TEXT;
"
```

### 예제 3: 여러 컬럼 한번에 추가
```bash
docker exec pab-postgres psql -U brain -d knowledge -c "
ALTER TABLE documents 
ADD COLUMN IF NOT EXISTS author VARCHAR(255),
ADD COLUMN IF NOT EXISTS version INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS is_archived BOOLEAN DEFAULT FALSE;
"
```

### 예제 4: 외래키와 인덱스 함께 추가
```bash
docker exec pab-postgres psql -U brain -d knowledge -c "
ALTER TABLE knowledge_chunks 
ADD COLUMN IF NOT EXISTS parent_chunk_id INTEGER REFERENCES knowledge_chunks(id);

CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_parent ON knowledge_chunks(parent_chunk_id);
"
```

## 5. 컬럼 수정 (ALTER TABLE ALTER COLUMN)

### 컬럼 타입 변경
```sql
-- VARCHAR 길이 변경
ALTER TABLE knowledge_chunks 
ALTER COLUMN status TYPE VARCHAR(100);

-- TEXT로 변경
ALTER TABLE knowledge_chunks 
ALTER COLUMN content TYPE TEXT;
```

### 컬럼 기본값 변경
```sql
-- 기본값 변경
ALTER TABLE knowledge_chunks 
ALTER COLUMN status SET DEFAULT 'pending';
```

### 컬럼에 NOT NULL 제약 추가
```sql
-- NOT NULL 제약 추가 (기존 NULL 값이 없어야 함)
ALTER TABLE knowledge_chunks 
ALTER COLUMN status SET NOT NULL;
```

### 컬럼에 NOT NULL 제약 제거
```sql
-- NOT NULL 제약 제거
ALTER TABLE knowledge_chunks 
ALTER COLUMN status DROP NOT NULL;
```

## 6. 컬럼 삭제 (ALTER TABLE DROP COLUMN)

### 컬럼 삭제
```sql
-- 컬럼 삭제
ALTER TABLE knowledge_chunks 
DROP COLUMN IF EXISTS old_column;
```

### 여러 컬럼 한번에 삭제
```sql
-- 여러 컬럼 삭제
ALTER TABLE knowledge_chunks 
DROP COLUMN IF EXISTS column1,
DROP COLUMN IF EXISTS column2;
```

## 7. 테이블 삭제 (DROP TABLE)

### 테이블 삭제
```sql
-- 테이블 삭제 (주의!)
DROP TABLE IF EXISTS example_table CASCADE;
```

## 8. 유용한 확인 쿼리

### 테이블 목록 확인
```sql
-- 모든 테이블 목록
\dt

-- 또는 SQL로
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';
```

### 테이블 구조 확인
```sql
-- 테이블 구조 상세 보기
\d+ table_name

-- 또는 SQL로
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'knowledge_chunks'
ORDER BY ordinal_position;
```

### 컬럼 존재 여부 확인
```sql
-- 특정 컬럼이 존재하는지 확인
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'knowledge_chunks' 
  AND column_name = 'status';
```

### 인덱스 확인
```sql
-- 테이블의 인덱스 확인
SELECT 
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'knowledge_chunks';
```

### 외래키 확인
```sql
-- 테이블의 외래키 확인
SELECT
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_name = 'knowledge_chunks';
```

## 9. 실전 예제: 기존 프로젝트 스타일

### 기존 마이그레이션 스크립트 스타일
```python
# Python 스크립트로 실행하는 방법
from backend.models.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    # 컬럼 존재 여부 확인 후 추가
    result = db.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='knowledge_chunks' AND column_name='new_field'
    """))
    
    if not result.fetchone():
        db.execute(text("""
            ALTER TABLE knowledge_chunks 
            ADD COLUMN new_field VARCHAR(255)
        """))
        db.commit()
        print("✅ 컬럼 추가 완료")
    else:
        print("ℹ️  컬럼이 이미 존재합니다")
finally:
    db.close()
```

### Docker에서 직접 실행
```bash
# 컬럼 존재 여부 확인
docker exec pab-postgres psql -U brain -d knowledge -c "
SELECT column_name 
FROM information_schema.columns 
WHERE table_name='knowledge_chunks' AND column_name='new_field';
"

# 컬럼 추가
docker exec pab-postgres psql -U brain -d knowledge -c "
ALTER TABLE knowledge_chunks 
ADD COLUMN IF NOT EXISTS new_field VARCHAR(255);
"
```

## 10. 주의사항

### 1. 데이터 백업
```bash
# 테이블 구조 변경 전 백업
docker exec pab-postgres pg_dump -U brain -d knowledge -t knowledge_chunks > backup.sql
```

### 2. 트랜잭션 사용
```sql
-- 트랜잭션으로 여러 작업을 안전하게 실행
BEGIN;
ALTER TABLE knowledge_chunks ADD COLUMN col1 VARCHAR(255);
ALTER TABLE knowledge_chunks ADD COLUMN col2 INTEGER;
COMMIT;

-- 문제가 있으면 롤백
ROLLBACK;
```

### 3. 외래키 제약조건
```sql
-- 외래키가 있는 컬럼 삭제 시 주의
-- 먼저 외래키 제약조건 확인 필요
SELECT * FROM information_schema.table_constraints 
WHERE constraint_type = 'FOREIGN KEY' 
  AND table_name = 'your_table';
```

### 4. 인덱스 성능
```sql
-- 큰 테이블에 컬럼 추가 시 인덱스 생성은 별도로
ALTER TABLE large_table ADD COLUMN new_col VARCHAR(255);
CREATE INDEX CONCURRENTLY idx_large_table_new_col ON large_table(new_col);
```

## 11. 빠른 참조

### PostgreSQL 데이터 타입
- `SERIAL` - 자동 증가 정수 (INTEGER + SEQUENCE)
- `VARCHAR(n)` - 가변 길이 문자열
- `TEXT` - 무제한 텍스트
- `INTEGER` - 정수
- `BIGINT` - 큰 정수
- `FLOAT` / `REAL` - 부동소수점
- `DOUBLE PRECISION` - 배정밀도 부동소수점
- `BOOLEAN` - 불린값
- `TIMESTAMP` - 날짜/시간
- `DATE` - 날짜
- `TIME` - 시간
- `JSON` / `JSONB` - JSON 데이터
- `ARRAY` - 배열 (예: `INTEGER[]`)

### 제약조건
- `PRIMARY KEY` - 기본키
- `FOREIGN KEY` - 외래키
- `UNIQUE` - 고유 제약
- `NOT NULL` - NULL 불허
- `CHECK` - 체크 제약
- `DEFAULT` - 기본값

### 인덱스 타입
- `BTREE` - 기본 인덱스 (기본값)
- `HASH` - 해시 인덱스
- `GIN` - Generalized Inverted Index
- `GiST` - Generalized Search Tree
