#!/usr/bin/env bash
# Docker Compose 실행 시 호스트(로컬) gpt4all 설치 여부를 체크해
# GPT4ALL_HOST_AVAILABLE 환경 변수로 백엔드에 전달합니다.
# 사용: ./scripts/docker-compose-up.sh [docker compose 옵션]
# 예: ./scripts/docker-compose-up.sh -d

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# 호스트 Python에서 gpt4all import 가능 여부 확인
if python3 -c "import gpt4all" 2>/dev/null; then
  export GPT4ALL_HOST_AVAILABLE=yes
  echo "[docker-compose-up] 로컬 gpt4all 감지됨 → GPT4ALL_HOST_AVAILABLE=yes"
else
  export GPT4ALL_HOST_AVAILABLE=no
  echo "[docker-compose-up] 로컬 gpt4all 미설치 → GPT4ALL_HOST_AVAILABLE=no"
fi

exec docker compose up "$@"
