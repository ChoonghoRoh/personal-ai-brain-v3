#!/bin/bash
# Personal AI Brain - 백업 스크립트
# Phase 9-4-3: 백업/복원 시스템
#
# 사용법:
#   ./backup.sh                    # 전체 백업
#   ./backup.sh --type incremental # 증분 백업
#   ./backup.sh --postgres-only    # PostgreSQL만 백업
#   ./backup.sh --qdrant-only      # Qdrant만 백업

set -e

# 스크립트 위치 기준 프로젝트 루트 찾기
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# 환경 변수 로드
if [ -f "${PROJECT_ROOT}/.env" ]; then
    export $(grep -v '^#' "${PROJECT_ROOT}/.env" | xargs)
fi

# 기본값 설정
BACKUP_DIR="${BACKUP_DIR:-${PROJECT_ROOT}/backups}"
BACKUP_TYPE="${BACKUP_TYPE:-full}"
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_USER="${POSTGRES_USER:-brain}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-brain_password}"
POSTGRES_DB="${POSTGRES_DB:-knowledge}"
QDRANT_HOST="${QDRANT_HOST:-localhost}"
QDRANT_PORT="${QDRANT_PORT:-6333}"

# 백업 ID 생성
BACKUP_ID="backup_$(date +%Y%m%d_%H%M%S)"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_ID}"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 함수 정의
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_help() {
    echo "Personal AI Brain 백업 스크립트"
    echo ""
    echo "사용법: $0 [옵션]"
    echo ""
    echo "옵션:"
    echo "  --type TYPE        백업 타입 (full/incremental), 기본값: full"
    echo "  --postgres-only    PostgreSQL만 백업"
    echo "  --qdrant-only      Qdrant만 백업"
    echo "  --output DIR       백업 출력 디렉토리"
    echo "  --help             도움말 표시"
    echo ""
    echo "환경 변수:"
    echo "  POSTGRES_HOST      PostgreSQL 호스트 (기본값: localhost)"
    echo "  POSTGRES_PORT      PostgreSQL 포트 (기본값: 5432)"
    echo "  POSTGRES_USER      PostgreSQL 사용자 (기본값: brain)"
    echo "  POSTGRES_PASSWORD  PostgreSQL 비밀번호"
    echo "  POSTGRES_DB        PostgreSQL 데이터베이스 (기본값: knowledge)"
    echo "  QDRANT_HOST        Qdrant 호스트 (기본값: localhost)"
    echo "  QDRANT_PORT        Qdrant 포트 (기본값: 6333)"
    echo "  BACKUP_DIR         백업 디렉토리 (기본값: ./backups)"
}

backup_postgres() {
    log_info "PostgreSQL 백업 시작..."

    local backup_file="${BACKUP_PATH}/postgres.dump"

    # pg_dump 실행
    PGPASSWORD="${POSTGRES_PASSWORD}" pg_dump \
        -h "${POSTGRES_HOST}" \
        -p "${POSTGRES_PORT}" \
        -U "${POSTGRES_USER}" \
        -d "${POSTGRES_DB}" \
        -F c \
        -f "${backup_file}"

    if [ $? -eq 0 ]; then
        local size=$(du -h "${backup_file}" | cut -f1)
        log_info "PostgreSQL 백업 완료: ${backup_file} (${size})"
        return 0
    else
        log_error "PostgreSQL 백업 실패"
        return 1
    fi
}

backup_qdrant() {
    log_info "Qdrant 백업 시작..."

    local qdrant_data="${PROJECT_ROOT}/qdrant-data"
    local backup_file="${BACKUP_PATH}/qdrant.tar.gz"

    if [ ! -d "${qdrant_data}" ]; then
        log_warn "Qdrant 데이터 디렉토리가 없습니다: ${qdrant_data}"

        # Qdrant API로 스냅샷 생성 시도
        log_info "Qdrant 스냅샷 API 사용 시도..."
        local snapshot_response=$(curl -s -X POST "http://${QDRANT_HOST}:${QDRANT_PORT}/collections/brain_documents/snapshots" 2>/dev/null)

        if echo "${snapshot_response}" | grep -q "name"; then
            log_info "Qdrant 스냅샷 생성됨"
            echo "${snapshot_response}" > "${BACKUP_PATH}/qdrant_snapshot.json"
            return 0
        else
            log_warn "Qdrant 스냅샷 생성 실패 (컬렉션이 없거나 연결 실패)"
            return 0  # 경고만 하고 계속 진행
        fi
    fi

    # 데이터 디렉토리 압축
    tar -czf "${backup_file}" -C "${PROJECT_ROOT}" qdrant-data

    if [ $? -eq 0 ]; then
        local size=$(du -h "${backup_file}" | cut -f1)
        log_info "Qdrant 백업 완료: ${backup_file} (${size})"
        return 0
    else
        log_error "Qdrant 백업 실패"
        return 1
    fi
}

backup_metadata() {
    log_info "메타데이터 백업 시작..."

    local metadata_dir="${PROJECT_ROOT}/brain/system"
    local backup_file="${BACKUP_PATH}/metadata.tar.gz"

    if [ ! -d "${metadata_dir}" ]; then
        log_warn "메타데이터 디렉토리가 없습니다: ${metadata_dir}"
        return 0
    fi

    tar -czf "${backup_file}" -C "${PROJECT_ROOT}/brain" system

    if [ $? -eq 0 ]; then
        local size=$(du -h "${backup_file}" | cut -f1)
        log_info "메타데이터 백업 완료: ${backup_file} (${size})"
        return 0
    else
        log_error "메타데이터 백업 실패"
        return 1
    fi
}

create_manifest() {
    log_info "매니페스트 생성..."

    local manifest_file="${BACKUP_PATH}/manifest.json"

    cat > "${manifest_file}" << EOF
{
    "backup_id": "${BACKUP_ID}",
    "type": "${BACKUP_TYPE}",
    "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "source": {
        "postgres_host": "${POSTGRES_HOST}",
        "postgres_db": "${POSTGRES_DB}",
        "qdrant_host": "${QDRANT_HOST}"
    },
    "files": [
$(ls -1 "${BACKUP_PATH}" | grep -v manifest.json | while read f; do
    size=$(stat -f%z "${BACKUP_PATH}/${f}" 2>/dev/null || stat -c%s "${BACKUP_PATH}/${f}" 2>/dev/null || echo 0)
    echo "        {\"name\": \"${f}\", \"size\": ${size}},"
done | sed '$ s/,$//')
    ]
}
EOF

    log_info "매니페스트 생성 완료: ${manifest_file}"
}

# 옵션 파싱
POSTGRES_ONLY=false
QDRANT_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --type)
            BACKUP_TYPE="$2"
            shift 2
            ;;
        --postgres-only)
            POSTGRES_ONLY=true
            shift
            ;;
        --qdrant-only)
            QDRANT_ONLY=true
            shift
            ;;
        --output)
            BACKUP_DIR="$2"
            shift 2
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            log_error "알 수 없는 옵션: $1"
            show_help
            exit 1
            ;;
    esac
done

# 메인 실행
echo "========================================"
echo "Personal AI Brain 백업"
echo "========================================"
echo ""
log_info "백업 타입: ${BACKUP_TYPE}"
log_info "백업 ID: ${BACKUP_ID}"
log_info "백업 경로: ${BACKUP_PATH}"
echo ""

# 백업 디렉토리 생성
mkdir -p "${BACKUP_PATH}"

# 백업 실행
if [ "${POSTGRES_ONLY}" = true ]; then
    backup_postgres
elif [ "${QDRANT_ONLY}" = true ]; then
    backup_qdrant
else
    backup_postgres
    backup_qdrant
    backup_metadata
fi

# 매니페스트 생성
create_manifest

echo ""
echo "========================================"
log_info "백업 완료: ${BACKUP_ID}"
log_info "위치: ${BACKUP_PATH}"
echo "========================================"
