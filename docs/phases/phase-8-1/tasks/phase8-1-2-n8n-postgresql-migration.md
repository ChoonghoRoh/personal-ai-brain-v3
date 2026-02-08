# Phase 8-1-2: n8n SQLite → PostgreSQL 마이그레이션

## 📋 개요

n8n을 SQLite에서 PostgreSQL로 마이그레이션하여 프로젝트 메인 데이터베이스와 통합 관리합니다.

**관련 문서:**
- [phase8-1-1-database-schema-n8n-setting.md](./phase8-1-1-database-schema-n8n-setting.md) - PostgreSQL 스키마 설정
- [phase8-1-0-plan.md](./phase8-1-0-plan.md) - 전체 계획
- [phase8-3-1-docker-compose-integration-guide.md](./phase8-3-1-docker-compose-integration-guide.md) - Docker Compose 통합 관리

## 🎯 목표

- n8n 데이터베이스를 SQLite에서 PostgreSQL로 전환
- 프로젝트 메인 DB와 통합 관리
- 기존 워크플로우 및 credentials 보존
- 향후 확장성 확보

## ✅ 사전 준비

### 1. PostgreSQL n8n 데이터베이스 확인

```bash
docker exec pab-postgres psql -U brain -d postgres -c "SELECT 1 FROM pg_database WHERE datname='n8n';"
```

데이터베이스가 없으면 생성:

```bash
docker exec pab-postgres psql -U brain -d postgres -c "CREATE DATABASE n8n;"
```

### 2. 기존 SQLite 데이터 백업 (선택사항)

기존 데이터는 볼륨에 보존되지만, 안전을 위해 백업:

```bash
# SQLite 데이터베이스 파일 확인
docker run --rm -v personal-ai-brain-v2_n8n_data:/data alpine ls -lh /data/database.sqlite
```

---

## 🔧 마이그레이션 단계

### Step 1: 기존 데이터 Export (선택사항)

n8n CLI를 사용하여 워크플로우와 credentials를 export:

```bash
# n8n 컨테이너에서 export
docker exec n8n n8n export:workflow --all --output=/tmp/workflows.json
docker exec n8n n8n export:credentials --all --output=/tmp/credentials.json

# 호스트로 복사
docker cp n8n:/tmp/workflows.json /tmp/workflows.json 2>/dev/null || echo "워크플로우 없음"
docker cp n8n:/tmp/credentials.json /tmp/credentials.json 2>/dev/null || echo "Credentials 없음"
```

**참고:** 기존 데이터가 많지 않다면 이 단계는 생략 가능합니다. n8n이 PostgreSQL로 전환되면 워크플로우를 다시 생성하면 됩니다.

### Step 2: docker-compose.yml 수정

`docker-compose.yml`의 n8n 서비스 설정을 PostgreSQL 모드로 변경:

**변경 전:**
```yaml
environment:
  - N8N_HOST=localhost
  - N8N_PORT=5678
  - N8N_PROTOCOL=http
  # SQLite 사용 (기존 데이터 사용)
  # PostgreSQL 사용하려면 아래 주석 해제
  # - DB_TYPE=postgresdb
  # ...
```

**변경 후:**
```yaml
environment:
  - N8N_HOST=localhost
  - N8N_PORT=5678
  - N8N_PROTOCOL=http
  # PostgreSQL 사용 (통합 관리)
  - DB_TYPE=postgresdb
  - DB_POSTGRESDB_HOST=postgres
  - DB_POSTGRESDB_PORT=5432
  - DB_POSTGRESDB_DATABASE=n8n
  - DB_POSTGRESDB_USER=brain
  - DB_POSTGRESDB_PASSWORD=brain_password
```

**depends_on 주석 해제:**
```yaml
depends_on:
  postgres:
    condition: service_healthy
```

### Step 3: n8n 컨테이너 재시작

```bash
cd /Users/map-rch/WORKS/personal-ai-brain-v2
docker compose stop n8n
docker compose rm -f n8n
docker compose up -d n8n
```

### Step 4: PostgreSQL 테이블 자동 생성 확인

n8n이 시작되면 자동으로 PostgreSQL에 필요한 테이블을 생성합니다.

```bash
# n8n 로그 확인
docker compose logs -f n8n

# PostgreSQL 테이블 확인
docker exec pab-postgres psql -U brain -d n8n -c "\dt"
```

**예상 테이블:**
- `workflow_entity` - 워크플로우
- `credentials_entity` - Credentials
- `execution_entity` - 실행 기록
- `webhook_entity` - Webhook
- 기타 n8n 내부 테이블들

### Step 5: 기존 데이터 Import

SQLite에서 export한 데이터를 PostgreSQL로 import:

```bash
# 1. 임시 SQLite 모드 컨테이너에서 export
docker run -d --name n8n-temp-export -v personal-ai-brain-v2_n8n_data:/home/node/.n8n n8nio/n8n:latest
sleep 10
docker exec n8n-temp-export sh -c "cd /home/node/.n8n && n8n export:workflow --all --output=./workflows.json && n8n export:credentials --all --output=./credentials.json"

# 2. 호스트로 복사
mkdir -p /tmp/n8n_migration
docker cp n8n-temp-export:/home/node/.n8n/workflows.json /tmp/n8n_migration/
docker cp n8n-temp-export:/home/node/.n8n/credentials.json /tmp/n8n_migration/

# 3. 임시 컨테이너 제거
docker stop n8n-temp-export && docker rm n8n-temp-export

# 4. PostgreSQL 모드 n8n에 import
docker cp /tmp/n8n_migration/workflows.json n8n:/tmp/workflows.json
docker cp /tmp/n8n_migration/credentials.json n8n:/tmp/credentials.json
docker exec n8n n8n import:workflow --input=/tmp/workflows.json
docker exec n8n n8n import:credentials --input=/tmp/credentials.json
```

**주의:** 
- n8n CLI export/import는 워크플로우와 credentials만 마이그레이션합니다
- 사용자 관계, 공유 설정 등은 수동으로 재설정해야 할 수 있습니다
- Webhook 관련 경고가 나올 수 있지만, 워크플로우는 정상적으로 import됩니다

### Step 6: n8n 웹 인터페이스 확인

1. `http://localhost:5678` 접속
2. 워크플로우 목록 확인
3. Credentials 확인
4. 새 워크플로우 생성 테스트

---

## 🔍 문제 해결

### 문제 1: "database 'n8n' does not exist"

**해결:**
```bash
docker exec pab-postgres psql -U brain -d postgres -c "CREATE DATABASE n8n;"
```

### 문제 2: PostgreSQL 연결 실패

**확인 사항:**
- `DB_POSTGRESDB_HOST=postgres` (컨테이너명 사용)
- `depends_on` 설정 확인
- PostgreSQL 컨테이너가 healthy 상태인지 확인

### 문제 3: 기존 워크플로우가 보이지 않음

**원인:**
- SQLite 데이터가 PostgreSQL로 자동 마이그레이션되지 않음
- n8n CLI로 export/import 필요

**해결:**
- Step 1의 export/import 과정 수행
- 또는 워크플로우를 수동으로 재생성

---

## ✅ 완료 체크리스트

- [x] PostgreSQL n8n 데이터베이스 생성 ✅
- [x] docker-compose.yml PostgreSQL 설정 활성화 ✅
- [x] n8n 컨테이너 재시작 ✅
- [x] PostgreSQL 테이블 자동 생성 확인 ✅
- [x] n8n 웹 인터페이스 접속 확인 ✅
- [x] 기존 워크플로우 및 credentials export ✅
- [x] PostgreSQL로 데이터 import ✅
- [ ] 워크플로우 생성 테스트 (수동 확인 필요)
- [ ] Credentials 등록 테스트 (수동 확인 필요)

**마이그레이션 완료일**: 2026-01-28

**마이그레이션 결과:**
- 워크플로우: 4개 import 완료
- Credentials: 6개 import 완료

---

## 📊 마이그레이션 전후 비교

### SQLite (이전)
- 데이터 위치: `/home/node/.n8n/database.sqlite`
- 백업: 파일 복사
- 동시성: 제한적
- 확장성: 낮음

### PostgreSQL (현재)
- 데이터 위치: PostgreSQL `n8n` 데이터베이스
- 백업: `pg_dump` 사용
- 동시성: 우수
- 확장성: 높음
- 통합 관리: 프로젝트 메인 DB와 통합

---

## 🎯 다음 단계

PostgreSQL 마이그레이션 완료 후:

1. **Phase 8-2-1**: 코드 분석 워크플로우 구축
2. **Phase 8-2-2**: Gap 분석 워크플로우 구축
3. **Phase 8-2-3**: Plan 생성 워크플로우 구축

---

**작성일**: 2026-01-28  
**버전**: 1.0  
**관련 문서**: 
- [phase8-1-1-database-schema-n8n-setting.md](./phase8-1-1-database-schema-n8n-setting.md)
- [phase8-1-0-plan.md](./phase8-1-0-plan.md)
- [phase8-3-1-docker-compose-integration-guide.md](./phase8-3-1-docker-compose-integration-guide.md)
