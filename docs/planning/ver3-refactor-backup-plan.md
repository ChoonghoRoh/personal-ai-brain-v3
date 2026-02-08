# ver3 리팩토링 백업 절차 플랜

**작성일**: 2026-02-08  
**목적**: ver3 분기 후 DB·인프라 백업·복구 및 main 브랜치 보호 절차 정리

---

## 1. 개발 폴더·브랜치 분기 (완료)

| 단계 | 내용 | 상태 |
|------|------|------|
| 1-1 | 개발 폴더 ver2 → ver3 복사, 새 워크스페이스로 분기 | ✅ 완료 |
| 1-2 | GitHub 브랜치 `ver3-cursor` 생성·분기 | ✅ 완료 |

※ 현재는 **새 폴더·새 저장소**에서 시작하므로, ver2에서 브랜치 분기 후 재병합을 위한 main 병합 룰은 적용하지 않음 (해당 룰 삭제됨).

---

## 2. DB·데이터 백업·복구 장치

### 2.1 현재 구조 요약

| 구분 | 현재(ver3) | 비고 |
|------|------------|------|
| PostgreSQL | 컨테이너 `pab-postgres-ver3`, 포트 **5433**, 볼륨 `postgres_data_ver3` | docker-compose (ver2와 분리) |
| Qdrant | 컨테이너 `qdrant-ver3`, 포트 **6343/6344**, 호스트 경로 `./qdrant-data-ver3` | bind mount (ver2와 분리) |
| Backend | 컨테이너 `pab-backend-ver3`, 포트 **8001** | ver2는 8000 |
| 백업 스크립트 | `scripts/backup/backup.sh`, `restore.sh` (ver3: QDRANT_STORAGE_DIR 지원) | Phase 9-4-3 |
| 백업 저장소 | `backups/` (backup_YYYYMMDD_HHMMSS 또는 full_* 형식) | 프로젝트 내 |

### 2.2 ver2 폴더 복사와 DB 데이터 관계 (확인 사항)

- **코드·설정**: ver2 폴더를 통째로 복사해 ver3를 만들었으므로 **파일시스템 기준 코드·설정 백업은 완료된 상태**로 볼 수 있음.
- **DB 데이터**: 다음은 **폴더 복사만으로는 포함되지 않음**.
  - **PostgreSQL**: Docker **named volume** (`postgres_data`) — 프로젝트 디렉터리 밖에 있음.
  - **Qdrant**: `./qdrant-data`는 **같은 머신에서 ver2/ver3가 같은 경로를 쓰면** 동일 디렉터리를 가리킬 수 있음. ver3를 다른 경로에 두었다면 ver3에는 `qdrant-data`가 없거나 빈 상태일 수 있음.
- **결론**: **“DB 데이터 백업 완료”는 폴더 복사만으로 보장되지 않음.**  
  → **현재 기준으로 PostgreSQL·Qdrant를 명시적으로 백업한 뒤**, ver3 전용 컨테이너/포트로 분리하는 절차가 필요함.

### 2.3 ver3용 Docker 분리 (PostgreSQL, Qdrant)

목표: **기존(ver2) 컨테이너/포트는 건드리지 않고**, ver3만 별도 포트·볼륨으로 운영.

| 항목 | ver2(기존) 유지 | ver3(제안) |
|------|------------------|------------|
| PostgreSQL 컨테이너명 | `pab-postgres` | `pab-postgres-ver3` |
| PostgreSQL 포트 | 5432 | **5433** (호스트) |
| PostgreSQL 볼륨 | `postgres_data` | **postgres_data_ver3** |
| Qdrant 컨테이너명 | `qdrant` | `qdrant-ver3` |
| Qdrant 포트 | 6333, 6334 | **6343, 6344** |
| Qdrant 스토리지 | `./qdrant-data` | **./qdrant-data-ver3** |

- **backend** 서비스의 `DATABASE_URL`, `QDRANT_HOST`/포트는 **ver3용 컨테이너·포트**를 바라보도록 `.env` 또는 docker-compose에서 설정.
- 이렇게 하면 **ver2로 복구 시**: ver2 워크스페이스에서 기존 `docker-compose`만 사용(포트 5432, 6333 유지). **ver2 세팅 변경 없이** 이어서 작업 가능.

### 2.4 백업·복구 실행 절차

#### 사전(ver3 분리 전) — 현재 기준 백업 1회

```bash
# 프로젝트 루트 (ver3)
./scripts/backup/backup.sh
```

- 생성: `backups/backup_YYYYMMDD_HHMMSS/` (postgres.dump, qdrant.tar.gz, metadata.tar.gz, manifest.json).
- 이 백업은 **ver2와 동일한 DB를 쓰고 있던 시점**이면 ver2 복구용으로도 사용 가능.

#### 정기 백업 (마이그레이션·중요 변경 전)

| 시점 | 명령 | 용도 |
|------|------|------|
| 마이그레이션 직전 | `./scripts/backup/backup.sh --postgres-only` | Task 단위 롤백 |
| 전체 스냅샷 | `./scripts/backup/backup.sh` | 전체 복원용 |

#### 복원

```bash
# 전체 복원
./scripts/backup/restore.sh backup_YYYYMMDD_HHMMSS

# PostgreSQL만 복원
./scripts/backup/restore.sh backup_YYYYMMDD_HHMMSS --postgres-only

# Qdrant만 복원
./scripts/backup/restore.sh backup_YYYYMMDD_HHMMSS --qdrant-only
```

- 복원 후 필요 시: `docker compose restart backend`, `docker compose restart qdrant` (또는 ver3용 서비스명에 맞게 재시작).

### 2.5 ver2 DB 데이터를 ver3로 가져오기

ver2에 등록된 PostgreSQL·Qdrant 데이터를 ver3로 이전하는 방법은 두 가지다.

#### 방법 A: ver2에서 백업 후 ver3에서 복원 (권장)

1. **ver2에서 백업**  
   ver2 프로젝트 폴더에서 (ver2 Postgres 5432, Qdrant 6333 기동 중):
   ```bash
   cd /path/to/personal-ai-brain-v2
   ./scripts/backup/backup.sh
   ```
   → `backups/backup_YYYYMMDD_HHMMSS/` 생성 (postgres.dump, qdrant.tar.gz, metadata.tar.gz).

2. **백업 폴더를 ver3에서 사용**  
   - 같은 머신이면 ver3의 `backups/`에 위 폴더를 복사하거나,  
   - ver2와 ver3가 같은 `backups` 경로를 쓰지 않는다면 `backup_YYYYMMDD_HHMMSS` 폴더를 ver3 프로젝트의 `backups/` 아래로 복사.

3. **ver3 Postgres·Qdrant 기동**  
   ver3 프로젝트에서:
   ```bash
   cd /path/to/personal-ai-brain-v3
   docker compose up -d postgres qdrant
   ```

4. **ver3에 복원** (ver3 포트·경로 사용)  
   ver3의 `.env`에 `POSTGRES_PORT=5433`, `QDRANT_PORT=6343`이 있으면 그대로 두고:
   ```bash
   export POSTGRES_PORT=5433
   export QDRANT_STORAGE_DIR=qdrant-data-ver3
   ./scripts/backup/restore.sh backup_YYYYMMDD_HHMMSS
   ```
   또는 `.env`에 다음을 넣어 두고 `restore.sh`만 실행해도 된다.
   ```bash
   POSTGRES_PORT=5433
   QDRANT_STORAGE_DIR=qdrant-data-ver3
   ```
   - PostgreSQL은 5433으로 떠 있는 ver3 Postgres에 복원되고, Qdrant 데이터는 `qdrant-data-ver3/`로 복원된다.

5. **ver3 백엔드 재시작**  
   ```bash
   docker compose restart backend
   docker compose restart qdrant
   ```

#### 방법 B: ver2 Postgres에서 직접 덤프 후 ver3에 복원

ver2 백업 스크립트를 쓰지 않고, 호스트에서 pg_dump로 덤프한 뒤 ver3에 넣는 방법.

1. **ver2 Postgres 덤프** (ver2 Postgres 5432 기동 중):
   ```bash
   PGPASSWORD=brain_password pg_dump -h localhost -p 5432 -U brain -d knowledge -F c -f ver2_postgres.dump
   ```

2. **ver3 Postgres·Qdrant 기동**  
   ver3에서 `docker compose up -d postgres qdrant`.

3. **ver3 Postgres에 복원**:
   ```bash
   PGPASSWORD=brain_password pg_restore -h localhost -p 5433 -U brain -d knowledge -c --if-exists ver2_postgres.dump
   ```

4. **Qdrant**  
   ver2의 `qdrant-data/` 폴더 전체를 ver3 프로젝트의 `qdrant-data-ver3/`로 복사한 뒤, ver3 Qdrant 컨테이너 재시작:
   ```bash
   cp -a /path/to/ver2/qdrant-data/. /path/to/ver3/qdrant-data-ver3/
   docker compose restart qdrant
   ```

**요약**:  
- **방법 A**: ver2 백업 → ver3 `restore.sh` (POSTGRES_PORT=5433, QDRANT_STORAGE_DIR=qdrant-data-ver3) 로 한 번에 이전.  
- **방법 B**: pg_dump + pg_restore + qdrant-data 폴더 복사로 수동 이전.

---

## 3. ver2 복구 시 이어서 작업 가능 여부

| 조건 | 확인 |
|------|------|
| ver3에서 **PostgreSQL/Qdrant를 새 포트·새 볼륨/새 경로**로 분리했는가? | ✅ 하면 ver2는 기존 5432, 6333 그대로 사용 가능. |
| ver2 워크스페이스에서 **docker-compose·.env를 수정하지 않았는가?** | ✅ ver2는 그대로 두고 ver3만 분리했으면 수정 불필요. |
| ver2에서 사용하던 **postgres_data**, **qdrant-data**를 ver3가 덮어쓰지 않았는가? | ✅ ver3를 별도 볼륨·경로로 두면 덮어쓰기 없음. |

**정리**:  
- ver3를 **별도 컨테이너·포트·볼륨**으로 분리해 두면,  
- **ver2로 복구 = ver2 폴더에서 기존 설정으로 `docker compose up`** 하면 되며,  
- **ver2 세팅 변경 없이** 이어서 작업 가능.

---

## 4. docker-compose 세팅 변경 (ver3 전용 분리) 체크리스트

ver3에서 아래만 적용하면 됨. ver2의 `docker-compose.yml`은 수정하지 않음.

- [ ] **postgres** 서비스: `container_name: pab-postgres-ver3`, `ports: "5433:5432"`, `volumes: postgres_data_ver3:/var/lib/postgresql/data`
- [ ] **qdrant** 서비스: `container_name: qdrant-ver3`, `ports: "6343:6333", "6344:6334"`, `volumes: ./qdrant-data-ver3:/qdrant/storage`
- [ ] **backend** 환경변수: `DATABASE_URL` → `@postgres:5432` (컨테이너 내부는 5432 유지), 호스트에서 접속 시만 `localhost:5433`. `QDRANT_HOST=qdrant`(서비스명), `QDRANT_PORT=6333` (컨테이너 내부) — 변경 없음.  
  단, **호스트에서 직접 접속**할 때만 `localhost:6343` 사용.
- [ ] **volumes** 블록: `postgres_data_ver3: driver: local` 추가.
- [ ] (선택) `.env`에 `POSTGRES_PORT=5433`, `QDRANT_PORT=6333` 등 문서화용 변수 정리.

### 4.1 docker-compose 변경 예시 (ver3 전용 분리)

아래는 **ver3에서만** 적용할 변경 예시. 기존 ver2의 `docker-compose.yml`은 수정하지 않음.

```yaml
# postgres 서비스 — 변경할 부분만
  postgres:
    container_name: pab-postgres-ver3
    ports:
      - "5433:5432"
    volumes:
      - postgres_data_ver3:/var/lib/postgresql/data

# qdrant 서비스 — 변경할 부분만
  qdrant:
    container_name: qdrant-ver3
    ports:
      - "6343:6333"
      - "6344:6334"
    volumes:
      - ./qdrant-data-ver3:/qdrant/storage

# volumes 블록에 추가
volumes:
  postgres_data_ver3:
    driver: local
```

- backend 서비스의 `DATABASE_URL`, `QDRANT_HOST`/`QDRANT_PORT`는 **컨테이너 내부**에서 `postgres:5432`, `qdrant:6333`으로 그대로 두면 됨 (서비스명은 변경하지 않으면 `postgres`, `qdrant` 유지).
- 호스트에서 psql/클라이언트로 접속할 때만 `localhost:5433`, `localhost:6343` 사용.

---

## 5. (참고) main 병합 룰 — 삭제됨

ver2에서 브랜치로 ver3 분기 후 재병합을 위해 사용하던 **main 병합 금지·3단계 확인** 룰은, 현재 **새 폴더·새 저장소**에서 시작하는 구조에 해당하지 않아 삭제함. 필요 시 팀/저장소 정책에 맞게 별도 규칙을 두면 됨.

---

## 6. 요약

| 항목 | 상태·조치 |
|------|-----------|
| 1. 개발 폴더 ver3 분기 | ✅ 완료 |
| 2. GitHub ver3-cursor 브랜치 | ✅ 완료 |
| 3. main 병합 룰 | (삭제) 새 저장소에서 시작하므로 ver2→ver3 재병합용 룰 미적용 |
| 4. DB 백업 | 폴더 복사만으로는 불완전 → **현재 기준 백업 1회 실행 권장** |
| 5. ver3 Docker 분리 | PostgreSQL 5433, postgres_data_ver3 / Qdrant 6343·6344, qdrant-data-ver3 적용 (§4 체크리스트) |
| 6. ver2 복구 | ver3를 별도 포트·볼륨으로 두면 ver2 설정 변경 없이 이어서 작업 가능 |
| 7. 첫 Git 커밋·푸시 | **PBA-ver3 리팩토링 환경 세팅 완료** (2026-02-08, origin/main) |

---

## 7. ver3 리팩토링 준비 상태 체크 (검증용)

전체 ver3 리팩토링 준비 여부 확인 시 아래 항목을 점검한다.

| # | 항목 | 확인 |
|---|------|------|
| 1 | **docker-compose** | postgres: pab-postgres-ver3, 5433, postgres_data_ver3 / qdrant: qdrant-ver3, 6343·6344, qdrant-data-ver3 / backend: pab-backend-ver3, 8001 |
| 2 | **.env.example** | POSTGRES_PORT=5433, QDRANT_PORT=6343 (호스트 접속·백업용) |
| 3 | **백업/복원** | backup.sh, restore.sh 존재. restore 시 QDRANT_STORAGE_DIR=qdrant-data-ver3, POSTGRES_PORT=5433 사용 |
| 4 | **E2E/Playwright** | baseURL 8001 (또는 BASE_URL env). smoke/e2e 주석에 ver3 포트 명시 |
| 5 | **.gitignore** | qdrant-data/, qdrant-data-ver3/ |
| 6 | **DB 데이터** | (선택) backup 복원 완료 시 Postgres 테이블·Qdrant 컬렉션 확인 |
| 7 | **README** | ver3 포트(8001, 5433, 6343) 및 플랜 문서 링크 |

모두 충족 시 **ver3 리팩토링 준비 완료**로 본다.

---

## 참고

- 백업 스크립트: [scripts/backup/backup.sh](../../scripts/backup/backup.sh), [scripts/backup/restore.sh](../../scripts/backup/restore.sh)
- Phase 11-1 백업 절차: [phase-11-1-0-plan.md](../phases/phase-11-1/phase-11-1-0-plan.md) §4
