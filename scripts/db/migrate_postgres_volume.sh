#!/bin/bash

# PostgreSQL 볼륨 마이그레이션 스크립트
# 기존 볼륨에서 새 docker-compose 볼륨으로 데이터를 마이그레이션합니다.

set -e

OLD_VOLUME="64aa33ed73a3e8438f934d47c4b255aaf16039f83a5d67b6787a447779431d64"
NEW_CONTAINER="pab-postgres"
DB_USER="brain"
DB_NAME="knowledge"
DB_PASSWORD="brain_password"

echo "=========================================="
echo "PostgreSQL 볼륨 마이그레이션 시작"
echo "=========================================="
echo ""

# 1. 기존 볼륨에서 데이터 백업
echo "1. 기존 볼륨에서 데이터 백업 중..."
docker run --rm \
  -v ${OLD_VOLUME}:/var/lib/postgresql/data:ro \
  -e PGPASSWORD=${DB_PASSWORD} \
  postgres:15 \
  pg_dump -U ${DB_USER} -d ${DB_NAME} > /tmp/postgres_backup_$(date +%Y%m%d_%H%M%S).sql

BACKUP_FILE=$(ls -t /tmp/postgres_backup_*.sql | head -1)
echo "   백업 파일: ${BACKUP_FILE}"
echo ""

# 2. 새 컨테이너가 실행 중인지 확인
echo "2. 새 PostgreSQL 컨테이너 확인 중..."
if ! docker ps | grep -q ${NEW_CONTAINER}; then
    echo "   ❌ ${NEW_CONTAINER} 컨테이너가 실행 중이 아닙니다."
    echo "   docker compose up -d postgres 를 먼저 실행하세요."
    exit 1
fi
echo "   ✅ 컨테이너 실행 중"
echo ""

# 3. PostgreSQL이 준비될 때까지 대기
echo "3. PostgreSQL 준비 대기 중..."
until docker exec ${NEW_CONTAINER} pg_isready -U ${DB_USER} -d ${DB_NAME} > /dev/null 2>&1; do
    echo "   대기 중..."
    sleep 2
done
echo "   ✅ PostgreSQL 준비 완료"
echo ""

# 4. 새 컨테이너에 데이터 복원
echo "4. 새 컨테이너에 데이터 복원 중..."
docker exec -i ${NEW_CONTAINER} \
  PGPASSWORD=${DB_PASSWORD} \
  psql -U ${DB_USER} -d ${DB_NAME} < ${BACKUP_FILE}

if [ $? -eq 0 ]; then
    echo "   ✅ 데이터 복원 완료"
else
    echo "   ❌ 데이터 복원 실패"
    exit 1
fi
echo ""

# 5. 테이블 확인
echo "5. 복원된 테이블 확인 중..."
docker exec ${NEW_CONTAINER} \
  PGPASSWORD=${DB_PASSWORD} \
  psql -U ${DB_USER} -d ${DB_NAME} -c "\dt"

echo ""
echo "=========================================="
echo "마이그레이션 완료!"
echo "=========================================="
echo ""
echo "백업 파일 위치: ${BACKUP_FILE}"
echo "백업 파일은 보관하거나 삭제할 수 있습니다."
