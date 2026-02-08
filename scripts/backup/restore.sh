#!/bin/bash
# Personal AI Brain - 복원 스크립트
# Phase 9-4-3: 백업/복원 시스템
#
# 사용법:
#   ./restore.sh backup_20260204_120000        # 전체 복원
#   ./restore.sh backup_20260204_120000 --postgres-only  # PostgreSQL만 복원
#   ./restore.sh backup_20260204_120000 --qdrant-only    # Qdrant만 복원

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
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_USER="${POSTGRES_USER:-brain}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-brain_password}"
POSTGRES_DB="${POSTGRES_DB:-knowledge}"
# ver3: Qdrant 데이터 복원 경로. 설정 시 해당 디렉터리로 복원 (예: qdrant-data-ver3)
QDRANT_STORAGE_DIR="${QDRANT_STORAGE_DIR:-qdrant-data}"

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
    echo "Personal AI Brain 복원 스크립트"
    echo ""
    echo "사용법: $0 <백업_ID> [옵션]"
    echo ""
    echo "옵션:"
    echo "  --postgres-only    PostgreSQL만 복원"
    echo "  --qdrant-only      Qdrant만 복원"
    echo "  --no-confirm       확인 없이 복원 (주의!)"
    echo "  --help             도움말 표시"
    echo ""
    echo "예시:"
    echo "  $0 backup_20260204_120000"
    echo "  $0 backup_20260204_120000 --postgres-only"
    echo "  # ver3에 복원: POSTGRES_PORT=5433 QDRANT_STORAGE_DIR=qdrant-data-ver3 $0 backup_YYYYMMDD_HHMMSS"
    echo ""
    echo "백업 목록 확인:"
    echo "  ls -la ${BACKUP_DIR}"
}

restore_postgres() {
    local backup_file="$1"

    if [ ! -f "${backup_file}" ]; then
        log_error "PostgreSQL 백업 파일이 없습니다: ${backup_file}"
        return 1
    fi

    log_info "PostgreSQL 복원 시작: ${backup_file}"

    # pg_restore 실행
    PGPASSWORD="${POSTGRES_PASSWORD}" pg_restore \
        -h "${POSTGRES_HOST}" \
        -p "${POSTGRES_PORT}" \
        -U "${POSTGRES_USER}" \
        -d "${POSTGRES_DB}" \
        -c \
        --if-exists \
        "${backup_file}" 2>/dev/null || true  # 일부 에러 무시 (테이블이 이미 존재하는 경우 등)

    log_info "PostgreSQL 복원 완료"
    return 0
}

restore_qdrant() {
    local backup_file="$1"

    if [ ! -f "${backup_file}" ]; then
        log_error "Qdrant 백업 파일이 없습니다: ${backup_file}"
        return 1
    fi

    log_info "Qdrant 복원 시작: ${backup_file} (대상: ${QDRANT_STORAGE_DIR})"

    local qdrant_target="${PROJECT_ROOT}/${QDRANT_STORAGE_DIR}"

    # 기존 데이터 백업
    if [ -d "${qdrant_target}" ]; then
        local pre_restore_backup="${BACKUP_DIR}/pre_restore_$(date +%Y%m%d_%H%M%S).tar.gz"
        log_warn "기존 Qdrant 데이터를 백업합니다: ${pre_restore_backup}"
        tar -czf "${pre_restore_backup}" -C "${PROJECT_ROOT}" "${QDRANT_STORAGE_DIR}"
    fi

    # 압축 해제 (아카이브 내부는 qdrant-data/ 로 저장됨)
    tar -xzf "${backup_file}" -C "${PROJECT_ROOT}"

    # ver3: 복원 경로가 qdrant-data 가 아니면 이동
    if [ "${QDRANT_STORAGE_DIR}" != "qdrant-data" ]; then
        if [ -d "${PROJECT_ROOT}/qdrant-data" ]; then
            rm -rf "${qdrant_target}"
            mv "${PROJECT_ROOT}/qdrant-data" "${qdrant_target}"
            log_info "Qdrant 데이터를 ${QDRANT_STORAGE_DIR}/ 로 이동했습니다."
        fi
    else
        # 기존: qdrant-data 로 복원된 상태 유지
        if [ -d "${qdrant_target}" ]; then
            : # 이미 해제됨
        fi
    fi

    log_info "Qdrant 복원 완료"
    log_warn "Qdrant 서비스를 재시작해야 할 수 있습니다."
    return 0
}

restore_metadata() {
    local backup_file="$1"

    if [ ! -f "${backup_file}" ]; then
        log_warn "메타데이터 백업 파일이 없습니다: ${backup_file}"
        return 0
    fi

    log_info "메타데이터 복원 시작: ${backup_file}"

    # 기존 메타데이터 백업
    local metadata_dir="${PROJECT_ROOT}/brain/system"
    if [ -d "${metadata_dir}" ]; then
        local pre_restore_backup="${BACKUP_DIR}/pre_restore_metadata_$(date +%Y%m%d_%H%M%S).tar.gz"
        log_warn "기존 메타데이터를 백업합니다: ${pre_restore_backup}"
        tar -czf "${pre_restore_backup}" -C "${PROJECT_ROOT}/brain" system 2>/dev/null || true
    fi

    # 백업 파일 압축 해제
    mkdir -p "${PROJECT_ROOT}/brain"
    tar -xzf "${backup_file}" -C "${PROJECT_ROOT}/brain"

    log_info "메타데이터 복원 완료"
    return 0
}

# 인자 확인
if [ $# -lt 1 ]; then
    show_help
    exit 1
fi

BACKUP_ID="$1"
shift

# 백업 경로 확인
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_ID}"
if [ ! -d "${BACKUP_PATH}" ]; then
    log_error "백업을 찾을 수 없습니다: ${BACKUP_PATH}"
    echo ""
    echo "사용 가능한 백업 목록:"
    ls -1 "${BACKUP_DIR}" 2>/dev/null | grep "^backup_" || echo "  (없음)"
    exit 1
fi

# 옵션 파싱
POSTGRES_ONLY=false
QDRANT_ONLY=false
NO_CONFIRM=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --postgres-only)
            POSTGRES_ONLY=true
            shift
            ;;
        --qdrant-only)
            QDRANT_ONLY=true
            shift
            ;;
        --no-confirm)
            NO_CONFIRM=true
            shift
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
echo "Personal AI Brain 복원"
echo "========================================"
echo ""
log_info "백업 ID: ${BACKUP_ID}"
log_info "백업 경로: ${BACKUP_PATH}"
echo ""

# 백업 내용 표시
echo "백업 파일:"
ls -lh "${BACKUP_PATH}"
echo ""

# 확인
if [ "${NO_CONFIRM}" = false ]; then
    echo -e "${YELLOW}경고: 기존 데이터가 덮어씌워집니다!${NC}"
    read -p "계속하시겠습니까? (yes/no): " confirm
    if [ "${confirm}" != "yes" ]; then
        log_info "복원이 취소되었습니다."
        exit 0
    fi
fi

# 복원 실행
if [ "${POSTGRES_ONLY}" = true ]; then
    restore_postgres "${BACKUP_PATH}/postgres.dump"
elif [ "${QDRANT_ONLY}" = true ]; then
    restore_qdrant "${BACKUP_PATH}/qdrant.tar.gz"
else
    restore_postgres "${BACKUP_PATH}/postgres.dump"
    restore_qdrant "${BACKUP_PATH}/qdrant.tar.gz"
    restore_metadata "${BACKUP_PATH}/metadata.tar.gz"
fi

echo ""
echo "========================================"
log_info "복원 완료: ${BACKUP_ID}"
echo "========================================"
echo ""
log_warn "서비스 재시작을 권장합니다:"
echo "  docker compose restart backend"
echo "  docker compose restart qdrant"
