# 콘솔에서 데이터베이스 접근 방법

## 1. Docker 컨테이너 내부에서 psql 사용 (가장 일반적)

### 기본 접속
```bash
docker exec -it pab-postgres psql -U brain -d knowledge
```

### 단일 쿼리 실행
```bash
docker exec pab-postgres psql -U brain -d knowledge -c "SELECT version();"
```

### 여러 쿼리 실행
```bash
docker exec pab-postgres psql -U brain -d knowledge -c "
SELECT COUNT(*) FROM knowledge_chunks;
SELECT COUNT(*) FROM documents;
SELECT COUNT(*) FROM projects;
"
```

## 2. 대화형 psql 세션

```bash
# 컨테이너 내부로 들어가기
docker exec -it pab-postgres psql -U brain -d knowledge

# psql 프롬프트에서 사용 가능한 명령어:
# \dt          - 테이블 목록 보기
# \d table_name - 테이블 구조 보기
# \q           - 종료
# \l           - 데이터베이스 목록
# \du          - 사용자 목록
# \?           - 도움말
```

## 3. 로컬 psql 클라이언트 사용 (설치되어 있는 경우)

```bash
# 환경 변수로 비밀번호 설정
export PGPASSWORD=brain_password

# psql 접속
psql -h localhost -p 5432 -U brain -d knowledge
```

## 4. Python 스크립트를 통한 접근

### 간단한 쿼리 실행
```python
from backend.models.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    result = db.execute(text("SELECT COUNT(*) FROM knowledge_chunks"))
    count = result.scalar()
    print(f"청크 수: {count}")
finally:
    db.close()
```

### Python 인터랙티브 셸에서
```bash
cd /Users/map-rch/WORKS/personal-ai-brain-v2
source scripts/venv/bin/activate
python3

# Python 셸에서:
>>> from backend.models.database import SessionLocal
>>> from sqlalchemy import text
>>> db = SessionLocal()
>>> result = db.execute(text("SELECT version()"))
>>> print(result.fetchone()[0])
>>> db.close()
```

## 5. 유용한 쿼리 예제

### 데이터베이스 정보 확인
```bash
docker exec pab-postgres psql -U brain -d knowledge -c "
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
```

### 테이블 목록
```bash
docker exec pab-postgres psql -U brain -d knowledge -c "\dt"
```

### 특정 테이블 구조 확인
```bash
docker exec pab-postgres psql -U brain -d knowledge -c "\d knowledge_chunks"
```

### 데이터 개수 확인
```bash
docker exec pab-postgres psql -U brain -d knowledge -c "
SELECT 
    'projects' as table_name, COUNT(*) as count FROM projects
UNION ALL
SELECT 'documents', COUNT(*) FROM documents
UNION ALL
SELECT 'knowledge_chunks', COUNT(*) FROM knowledge_chunks
UNION ALL
SELECT 'knowledge_labels', COUNT(*) FROM knowledge_labels
UNION ALL
SELECT 'knowledge_relations', COUNT(*) FROM knowledge_relations;
"
```

### 최근 문서 확인
```bash
docker exec pab-postgres psql -U brain -d knowledge -c "
SELECT id, file_name, file_type, created_at 
FROM documents 
ORDER BY created_at DESC 
LIMIT 10;
"
```

### 청크 샘플 확인
```bash
docker exec pab-postgres psql -U brain -d knowledge -c "
SELECT id, chunk_index, LEFT(content, 100) as content_preview, document_id
FROM knowledge_chunks 
LIMIT 5;
"
```

## 6. 데이터베이스 연결 정보

- **호스트**: localhost (또는 Docker 컨테이너 내부: pab-postgres)
- **포트**: 5432
- **데이터베이스**: knowledge
- **사용자**: brain
- **비밀번호**: brain_password
- **연결 문자열**: `postgresql://brain:brain_password@localhost:5432/knowledge`

## 7. 백업 및 복원

### 백업
```bash
# pg_dump 사용 (로컬에 설치되어 있는 경우)
export PGPASSWORD=brain_password
pg_dump -h localhost -p 5432 -U brain -d knowledge -F c -f backup.dump

# 또는 Docker를 통한 백업
docker exec pab-postgres pg_dump -U brain -d knowledge > backup.sql
```

### 복원
```bash
# Docker를 통한 복원
docker exec -i pab-postgres psql -U brain -d knowledge < backup.sql
```

## 8. 트러블슈팅

### 연결이 안 될 때
```bash
# 컨테이너 상태 확인
docker ps | grep pab-postgres

# 컨테이너 로그 확인
docker logs pab-postgres --tail 50

# 컨테이너 재시작
docker restart pab-postgres
```

### 권한 문제
```bash
# 컨테이너 내부에서 확인
docker exec -it pab-postgres psql -U brain -d knowledge -c "\du"
```
