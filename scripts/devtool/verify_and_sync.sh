#!/bin/bash
# 데이터 일관성 확인 및 동기화 스크립트

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$SCRIPT_DIR" || exit 1

# 가상환경 활성화
source venv/bin/activate

echo "========================================"
echo "데이터 일관성 확인 및 동기화"
echo "========================================"
echo ""

# 1. 데이터 일관성 확인
echo "[1/2] 데이터 일관성 확인 중..."
python check_data_sync.py

SYNC_STATUS=$?

if [ $SYNC_STATUS -eq 0 ]; then
    echo ""
    echo "✅ 데이터가 이미 동기화되어 있습니다."
    exit 0
fi

# 2. 동기화 실행
echo ""
echo "[2/2] 데이터 동기화 실행 중..."
python sync_data.py

SYNC_RESULT=$?

if [ $SYNC_RESULT -eq 0 ]; then
    echo ""
    echo "✅ 데이터 동기화 완료!"
    exit 0
else
    echo ""
    echo "❌ 데이터 동기화 실패"
    exit 1
fi

