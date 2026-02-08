# Task 9-4-3: 백업/복원 시스템

**상태**: 대기 (Pending)
**우선순위**: 9-4 내 3순위
**예상 작업량**: 2일
**의존성**: 없음

---

## 1. 목표

PostgreSQL, Qdrant 데이터의 백업 및 복원 기능 구현

---

## 2. 배경

- 데이터 손실 방지
- 환경 이전 지원
- 정기 백업 자동화 기반 마련

---

## 3. 백업 대상

| 대상 | 데이터 | 형식 |
|------|--------|------|
| PostgreSQL | 전체 테이블 | SQL dump (.sql) |
| Qdrant | 벡터 컬렉션 | Snapshot (.snapshot) |
| 파일 (선택) | uploads 디렉토리 | tar.gz |

---

## 4. 구현 범위

### 4.1 백업 API

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/system/backup` | 백업 생성 |
| GET | `/api/system/backups` | 백업 목록 |
| GET | `/api/system/backup/{id}/download` | 백업 다운로드 |
| DELETE | `/api/system/backup/{id}` | 백업 삭제 |

### 4.2 복원 API

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/system/restore` | 복원 실행 |
| GET | `/api/system/restore/status` | 복원 상태 조회 |

### 4.3 CLI 스크립트

```
scripts/backup/
├── backup.sh           # 백업 스크립트
├── restore.sh          # 복원 스크립트
└── schedule.sh         # 스케줄 설정 (선택)
```

---

## 5. 기술 설계

### 5.1 PostgreSQL 백업

**방법: pg_dump**

```bash
pg_dump -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB \
  --format=custom --file=backup.dump
```

**복원: pg_restore**

```bash
pg_restore -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB \
  --clean --if-exists backup.dump
```

### 5.2 Qdrant 백업

**방법: Snapshot API**

```python
# 스냅샷 생성
POST /collections/{collection_name}/snapshots

# 스냅샷 목록
GET /collections/{collection_name}/snapshots

# 스냅샷 다운로드
GET /collections/{collection_name}/snapshots/{snapshot_name}
```

### 5.3 통합 백업 구조

```
backup_20260204_120000/
├── metadata.json         # 백업 메타데이터
├── postgres.dump         # PostgreSQL 덤프
├── qdrant_brain_documents.snapshot  # Qdrant 스냅샷
└── uploads.tar.gz        # 업로드 파일 (선택)
```

---

## 6. API 스키마

### 6.1 백업 생성

**Request: `POST /api/system/backup`**

```json
{
  "include_uploads": false,
  "description": "Daily backup"
}
```

**Response:**

```json
{
  "backup_id": "backup_20260204_120000",
  "created_at": "2026-02-04T12:00:00Z",
  "size_mb": 45.6,
  "components": {
    "postgres": true,
    "qdrant": true,
    "uploads": false
  },
  "status": "completed"
}
```

### 6.2 백업 목록

**Response: `GET /api/system/backups`**

```json
{
  "backups": [
    {
      "backup_id": "backup_20260204_120000",
      "created_at": "2026-02-04T12:00:00Z",
      "size_mb": 45.6,
      "description": "Daily backup"
    },
    ...
  ],
  "total": 5,
  "storage_used_mb": 228
}
```

### 6.3 복원 실행

**Request: `POST /api/system/restore`**

```json
{
  "backup_id": "backup_20260204_120000",
  "confirm": true,
  "components": ["postgres", "qdrant"]
}
```

**Response:**

```json
{
  "restore_id": "restore_20260204_130000",
  "status": "in_progress",
  "started_at": "2026-02-04T13:00:00Z"
}
```

---

## 7. 파일 구조

### 7.1 Backend

```
backend/
├── routers/system/
│   └── backup.py           # 신규: 백업/복원 API
├── services/system/
│   └── backup_service.py   # 신규: 백업 서비스
└── ...
```

### 7.2 Scripts

```
scripts/backup/
├── backup.sh               # 백업 실행
├── restore.sh              # 복원 실행
└── config.env.example      # 설정 예시
```

### 7.3 백업 저장소

```
backups/                    # 백업 디렉토리 (gitignore)
├── backup_20260204_120000/
├── backup_20260203_120000/
└── ...
```

---

## 8. 체크리스트

### 8.1 설계
- [ ] 백업 형식 확정
- [ ] 저장 위치 결정
- [ ] 보관 정책 정의

### 8.2 Backend 구현
- [ ] `backup_service.py` 생성
- [ ] PostgreSQL 백업 기능
- [ ] PostgreSQL 복원 기능
- [ ] Qdrant 스냅샷 기능
- [ ] Qdrant 복원 기능
- [ ] 백업 메타데이터 관리
- [ ] `backup.py` 라우터 생성
- [ ] `main.py`에 등록

### 8.3 스크립트 구현
- [ ] `backup.sh` 생성
- [ ] `restore.sh` 생성
- [ ] Docker 환경 지원
- [ ] 로컬 환경 지원

### 8.4 테스트
- [ ] 백업 생성 테스트
- [ ] 복원 테스트 (테스트 DB)
- [ ] 부분 복원 테스트
- [ ] 에러 처리 테스트

---

## 9. 안전장치

### 9.1 복원 전 확인

```json
{
  "warning": "This will overwrite existing data",
  "affected": {
    "documents": 150,
    "chunks": 2340,
    "vectors": 2340
  },
  "confirm_required": true
}
```

### 9.2 복원 중 상태

| 상태 | 설명 |
|------|------|
| `pending` | 대기 중 |
| `in_progress` | 진행 중 |
| `completed` | 완료 |
| `failed` | 실패 |
| `rolled_back` | 롤백됨 |

### 9.3 롤백 전략

1. 복원 전 현재 상태 임시 백업
2. 복원 실패 시 임시 백업으로 롤백
3. 성공 시 임시 백업 삭제

---

## 10. 설정

### 10.1 환경 변수

```bash
# 백업 설정
BACKUP_DIR=/app/backups
BACKUP_RETENTION_DAYS=30
BACKUP_MAX_COUNT=10

# PostgreSQL (기존)
POSTGRES_HOST=localhost
POSTGRES_USER=brain
POSTGRES_PASSWORD=...
POSTGRES_DB=knowledge

# Qdrant (기존)
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

### 10.2 config.py 추가

```python
BACKUP_DIR = get_env("BACKUP_DIR", str(PROJECT_ROOT / "backups"))
BACKUP_RETENTION_DAYS = get_env_int("BACKUP_RETENTION_DAYS", 30)
BACKUP_MAX_COUNT = get_env_int("BACKUP_MAX_COUNT", 10)
```

---

## 11. 스크립트 예시

### 11.1 backup.sh

```bash
#!/bin/bash
set -e

BACKUP_ID="backup_$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="${BACKUP_BASE_DIR:-./backups}/$BACKUP_ID"
mkdir -p "$BACKUP_DIR"

# PostgreSQL 백업
echo "Backing up PostgreSQL..."
pg_dump -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
  --format=custom --file="$BACKUP_DIR/postgres.dump"

# Qdrant 스냅샷
echo "Creating Qdrant snapshot..."
curl -X POST "http://$QDRANT_HOST:$QDRANT_PORT/collections/brain_documents/snapshots"

echo "Backup completed: $BACKUP_ID"
```

### 11.2 restore.sh

```bash
#!/bin/bash
set -e

BACKUP_ID="$1"
if [ -z "$BACKUP_ID" ]; then
  echo "Usage: restore.sh <backup_id>"
  exit 1
fi

BACKUP_DIR="${BACKUP_BASE_DIR:-./backups}/$BACKUP_ID"

# PostgreSQL 복원
echo "Restoring PostgreSQL..."
pg_restore -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
  --clean --if-exists "$BACKUP_DIR/postgres.dump"

echo "Restore completed from: $BACKUP_ID"
```

---

## 12. 자동 백업 (선택)

### 12.1 Cron 설정

```bash
# 매일 새벽 3시 백업
0 3 * * * /app/scripts/backup/backup.sh >> /var/log/backup.log 2>&1
```

### 12.2 Docker Compose 스케줄러

```yaml
services:
  backup-scheduler:
    image: mcuadros/ofelia:latest
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    command: daemon --docker
    labels:
      ofelia.job-run.backup.schedule: "0 3 * * *"
      ofelia.job-run.backup.container: "pab-backend"
      ofelia.job-run.backup.command: "/app/scripts/backup/backup.sh"
```

---

## 13. 테스트 시나리오

| 시나리오 | 단계 | 검증 |
|----------|------|------|
| 전체 백업 | POST /backup | 백업 파일 생성 확인 |
| 목록 조회 | GET /backups | 생성한 백업 표시 |
| 다운로드 | GET /backup/{id}/download | 파일 다운로드 |
| 복원 | POST /restore | 데이터 복원 확인 |
| 삭제 | DELETE /backup/{id} | 백업 삭제 확인 |

---

## 14. 참고 자료

- pg_dump: https://www.postgresql.org/docs/current/app-pgdump.html
- pg_restore: https://www.postgresql.org/docs/current/app-pgrestore.html
- Qdrant Snapshots: https://qdrant.tech/documentation/concepts/snapshots/
- Docker backup: https://docs.docker.com/storage/volumes/

---

## 15. 작업 로그

| 날짜 | 작업 내용 | 상태 |
|------|----------|------|
| - | - | - |
