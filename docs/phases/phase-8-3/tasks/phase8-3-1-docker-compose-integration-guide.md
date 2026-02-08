# Docker Compose 통합 관리 가이드

## 📋 개요

모든 서비스(PostgreSQL, Qdrant, n8n)를 docker-compose로 통합 관리합니다.

**관련 문서:**

- [phase8-1-0-plan.md](./phase8-1-0-plan.md) - 전체 계획
- [phase8-2-1-code-analysis-workflow-guide.md](./phase8-2-1-code-analysis-workflow-guide.md) - n8n 워크플로우 가이드

## ✅ 통합 완료

### 통합된 서비스

1. **PostgreSQL** (`pab-postgres`)
   - 포트: `5432`
   - 데이터베이스: `knowledge`
   - 사용자: `brain` / 비밀번호: `brain_password`
   - 볼륨: `postgres_data` (Docker 볼륨)

2. **Qdrant** (`qdrant`)
   - 포트: `6333`, `6334`
   - 볼륨: `./qdrant-data` (프로젝트 디렉토리)

3. **n8n** (`n8n`)
   - 포트: `5678`
   - 볼륨: `n8n_data` (Docker 볼륨) + 프로젝트 경로

4. **FastAPI Backend** (로컬 실행 권장)
   - 포트: `8000`
   - 개발 모드에서는 `scripts/backend/start_server.py`로 로컬 실행 권장 (hot reload 지원)
   - docker-compose에 포함 가능하지만 주석 처리됨

## 🚀 사용 방법

### 모든 서비스 시작

```bash
docker compose up -d
```

### 모든 서비스 중지

```bash
docker compose stop
```

### 모든 서비스 재시작

```bash
docker compose restart
```

### 특정 서비스만 시작/중지

```bash
# PostgreSQL만 시작
docker compose up -d postgres

# Qdrant만 중지
docker compose stop qdrant
```

### 서비스 상태 확인

```bash
docker compose ps
```

### 로그 확인

```bash
# 모든 서비스 로그
docker compose logs -f

# 특정 서비스 로그
docker compose logs -f postgres
docker compose logs -f qdrant
docker compose logs -f n8n
```

### 서비스 제거 (컨테이너만, 볼륨 유지)

```bash
docker compose down
```

### 서비스 제거 (볼륨 포함)

```bash
docker compose down -v
```

⚠️ **주의**: `-v` 옵션은 모든 볼륨을 삭제하므로 데이터가 손실됩니다!

## 📊 서비스 상태 확인

### PostgreSQL 연결 확인

```bash
docker exec pab-postgres pg_isready -U brain -d knowledge
```

### Qdrant 헬스 체크

```bash
curl http://localhost:6333/health
```

### n8n 접속

브라우저에서 `http://localhost:5678` 접속

### n8n Execute Command 노드 설정 확인

n8n Execute Command 노드를 사용하기 위해 다음 설정이 포함되어 있습니다:

- `NODES_EXCLUDE='[]'`: 모든 노드 차단 해제 (가이드 권장 방법)
- Docker socket 마운트: `/var/run/docker.sock:/var/run/docker.sock:ro` (읽기 전용)
- 프로젝트 볼륨 마운트: `/Users/map-rch/WORKS/personal-ai-brain-v2:/workspace` (가이드 권장 경로)

**테스트:**
```bash
# n8n 컨테이너에서 명령어 실행 테스트
docker exec n8n sh -c "echo 'Test' && ls /workspace | head -5"
```

**주의사항:**
- Docker socket 마운트는 보안상 프로덕션 환경에서는 신중하게 사용해야 합니다
- Execute Command 노드는 컨테이너 내부에서 직접 명령어를 실행합니다
- 호스트의 명령어를 실행하려면 Docker CLI가 필요하며, 별도로 설치해야 할 수 있습니다

### FastAPI Backend 실행 (로컬)

```bash
cd scripts
source venv/bin/activate
python start_server.py
```

서버 주소: `http://localhost:8000`

## 🔄 데이터 마이그레이션 (필요한 경우)

### PostgreSQL 데이터 마이그레이션

기존 PostgreSQL 볼륨에서 새 볼륨으로 데이터를 마이그레이션해야 할 수 있습니다.

1. **기존 볼륨 확인**

```bash
docker volume ls | grep postgres
```

2. **기존 데이터 백업**

```bash
# 기존 컨테이너가 있다면
docker run --rm \
  -v <기존_볼륨명>:/var/lib/postgresql/data:ro \
  -v $(pwd):/backup \
  postgres:15 \
  pg_dump -U brain -d knowledge > backup.sql
```

3. **새 볼륨으로 복원**

```bash
docker exec -i pab-postgres psql -U brain -d knowledge < backup.sql
```

## 🛠️ 문제 해결

### 서비스가 시작되지 않을 때

```bash
# 로그 확인
docker compose logs <서비스명>

# 서비스 재시작
docker compose restart <서비스명>
```

### 포트 충돌

다른 서비스가 같은 포트를 사용하고 있을 수 있습니다.

```bash
# 포트 사용 확인
lsof -i :5432  # PostgreSQL
lsof -i :6333  # Qdrant
lsof -i :5678  # n8n
```

### 볼륨 권한 문제

```bash
# 볼륨 권한 확인
docker compose exec postgres ls -la /var/lib/postgresql/data
docker compose exec qdrant ls -la /qdrant/storage
```

## 📝 네트워크 설정

모든 서비스는 `pab-network` 네트워크에 연결되어 있어 서로 통신할 수 있습니다.

- PostgreSQL: `postgres` (컨테이너명)
- Qdrant: `qdrant` (컨테이너명)
- n8n: `n8n` (컨테이너명)
- FastAPI Backend: 로컬 실행 시 `localhost` 또는 `host.docker.internal` 사용

## 🔐 환경 변수

### PostgreSQL

- `POSTGRES_USER=brain`
- `POSTGRES_PASSWORD=brain_password`
- `POSTGRES_DB=knowledge`

### n8n

- PostgreSQL을 n8n의 백엔드 DB로 사용하도록 설정됨
- `DB_POSTGRESDB_HOST=postgres`
- `DB_POSTGRESDB_DATABASE=n8n`

## 📚 참고 자료

- [Docker Compose 공식 문서](https://docs.docker.com/compose/)
- [PostgreSQL Docker 이미지](https://hub.docker.com/_/postgres)
- [Qdrant Docker 이미지](https://hub.docker.com/r/qdrant/qdrant)
- [n8n Docker 이미지](https://hub.docker.com/r/n8nio/n8n)

---

## 📝 참고

- FastAPI 서버는 개발 편의성을 위해 로컬에서 실행하는 것을 권장합니다
- 프로덕션 환경에서는 docker-compose에 포함하여 실행할 수 있습니다
- PostgreSQL 데이터 마이그레이션이 필요한 경우: `scripts/db/migrate_postgres_volume.sh` 참조

---

**작성일**: 2026-01-28  
**버전**: 1.0  
**관련 문서**: [phase8-1-0-plan.md](./phase8-1-0-plan.md), [phase8-2-1-code-analysis-workflow-guide.md](./phase8-2-1-code-analysis-workflow-guide.md)
