#!/usr/bin/env python3
"""
Phase 8.0.0 작업 내용을 work_log.json에 추가
"""
import json
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SYSTEM_DIR = PROJECT_ROOT / "brain" / "system"
WORK_LOG_JSON = SYSTEM_DIR / "work_log.json"

# Phase 8.0.0 작업 항목들
phase8_entries = [
    {
        "timestamp": "2026-01-10T12:00:00.000000",
        "date": "2026-01-10",
        "time": "12:00:00",
        "action": "optimization",
        "description": "Phase 8.0.0: 검색 성능 최적화 - Qdrant 쿼리 최적화, 인덱싱 전략 개선, 캐싱 메커니즘 도입, 페이징 최적화",
        "files": [
            "backend/services/search_service.py",
            "backend/routers/search.py",
            "scripts/devtool/benchmark_search.py",
            "docs/dev/phase8-0-0-0-search-performance-optimization-test-report.md",
            "docs/dev/phase8-0-0-0-search-performance-optimization-change-report.md"
        ],
        "metadata": {
            "phase": "8.0.1",
            "status": "completed",
            "type": "optimization",
            "details": "검색 캐싱 메커니즘 도입, Qdrant 필터링 및 페이징 최적화, HNSW 인덱싱 개선"
        }
    },
    {
        "timestamp": "2026-01-10T12:30:00.000000",
        "date": "2026-01-10",
        "time": "12:30:00",
        "action": "optimization",
        "description": "Phase 8.0.0: 임베딩 성능 최적화 - 배치 처리 최적화, 병렬 처리 개선",
        "files": [
            "scripts/backend/embed_and_store.py",
            "requirements.txt",
            "docs/dev/phase8-0-0-7-embedding-performance-optimization-test-report.md",
            "docs/dev/phase8-0-0-7-embedding-performance-optimization-change-report.md"
        ],
        "metadata": {
            "phase": "8.0.2",
            "status": "completed",
            "type": "optimization",
            "details": "배치 임베딩 생성 (배치 크기 32), tqdm을 사용한 진행률 표시"
        }
    },
    {
        "timestamp": "2026-01-10T13:00:00.000000",
        "date": "2026-01-10",
        "time": "13:00:00",
        "action": "optimization",
        "description": "Phase 8.0.0: 데이터베이스 쿼리 최적화 - 인덱스 추가, N+1 쿼리 해결, 쿼리 실행 계획 분석",
        "files": [
            "backend/models/models.py",
            "backend/models/database.py",
            "backend/routers/knowledge.py",
            "backend/routers/reason.py",
            "scripts/db/analyze_slow_queries.py",
            "docs/dev/phase8-0-0-1-database-query-optimization-test-report.md",
            "docs/dev/phase8-0-0-1-database-query-optimization-change-report.md"
        ],
        "metadata": {
            "phase": "8.0.3",
            "status": "completed",
            "type": "optimization",
            "details": "주요 필드에 인덱스 추가, N+1 쿼리 해결 (eager loading), 연결 풀 최적화"
        }
    },
    {
        "timestamp": "2026-01-10T13:30:00.000000",
        "date": "2026-01-10",
        "time": "13:30:00",
        "action": "feature",
        "description": "Phase 8.0.0: 맥락 이해 및 연결 강화 - 의미적 유사도 계산, 시간적 맥락 추적, 주제별 클러스터링",
        "files": [
            "backend/services/context_service.py",
            "backend/routers/context.py",
            "requirements.txt",
            "docs/dev/phase8-0-0-2-context-understanding-enhancement-test-report.md",
            "docs/dev/phase8-0-0-2-context-understanding-enhancement-change-report.md"
        ],
        "metadata": {
            "phase": "8.0.4",
            "status": "completed",
            "type": "feature",
            "details": "의미적 유사도 계산, 시간적 맥락 추적, K-means 클러스터링, 계층 구조 추론, 참조 감지"
        }
    },
    {
        "timestamp": "2026-01-10T14:00:00.000000",
        "date": "2026-01-10",
        "time": "14:00:00",
        "action": "feature",
        "description": "Phase 8.0.0: 기억 시스템 구축 - 장기/단기/작업 기억 시스템 구현",
        "files": [
            "backend/models/models.py",
            "backend/services/memory_service.py",
            "backend/routers/memory.py",
            "docs/dev/phase8-0-0-3-memory-system-test-report.md",
            "docs/dev/phase8-0-0-3-memory-system-change-report.md"
        ],
        "metadata": {
            "phase": "8.0.5",
            "status": "completed",
            "type": "feature",
            "details": "Memory 모델 추가, 장기/단기/작업 기억 시스템, 중요도 점수, 만료 시간 관리"
        }
    },
    {
        "timestamp": "2026-01-10T14:30:00.000000",
        "date": "2026-01-10",
        "time": "14:30:00",
        "action": "feature",
        "description": "Phase 8.0.0: 페이징 기능 추가 - 주요 페이지에 페이징 구현",
        "files": [
            "web/public/js/pagination-component.js",
            "backend/routers/knowledge.py",
            "backend/routers/approval.py",
            "backend/routers/logs.py",
            "docs/dev/phase8-0-0-4-pagination-feature-test-report.md",
            "docs/dev/phase8-0-0-4-pagination-feature-change-report.md"
        ],
        "metadata": {
            "phase": "8.0.11",
            "status": "completed",
            "type": "feature",
            "details": "페이징 기능 이미 구현 완료 확인 - 공통 컴포넌트 및 API 지원"
        }
    },
    {
        "timestamp": "2026-01-10T15:00:00.000000",
        "date": "2026-01-10",
        "time": "15:00:00",
        "action": "feature",
        "description": "Phase 8.0.0: 백업 및 복원 시스템 - 자동 백업 스케줄링, 증분 백업, 복원 기능",
        "files": [
            "scripts/devtool/backup_system.py",
            "backend/routers/backup.py",
            "docs/dev/phase8-0-0-5-backup-restore-system-test-report.md",
            "docs/dev/phase8-0-0-5-backup-restore-system-change-report.md"
        ],
        "metadata": {
            "phase": "8.0.16",
            "status": "completed",
            "type": "feature",
            "details": "PostgreSQL 백업 (pg_dump), Qdrant 백업 (tar.gz), 메타데이터 백업, 복원 및 검증 기능"
        }
    },
    {
        "timestamp": "2026-01-10T15:30:00.000000",
        "date": "2026-01-10",
        "time": "15:30:00",
        "action": "feature",
        "description": "Phase 8.0.0: 데이터 무결성 보장 - Qdrant-PostgreSQL 동기화 개선, 데이터 검증 강화",
        "files": [
            "backend/services/integrity_service.py",
            "backend/routers/integrity.py",
            "docs/dev/phase8-0-0-6-data-integrity-test-report.md",
            "docs/dev/phase8-0-0-6-data-integrity-change-report.md"
        ],
        "metadata": {
            "phase": "8.0.17",
            "status": "completed",
            "type": "feature",
            "details": "Qdrant-PostgreSQL 동기화 체크, 데이터 일관성 검증, 고아 레코드 자동 수정"
        }
    },
    {
        "timestamp": "2026-01-10T16:00:00.000000",
        "date": "2026-01-10",
        "time": "16:00:00",
        "action": "feature",
        "description": "Phase 8.0.0: 대화 기록 영구 저장 - 서버에 대화 기록 저장, 검색 기능",
        "files": [
            "backend/models/models.py",
            "backend/routers/conversations.py",
            "web/public/js/ask.js",
            "docs/dev/phase8-0-0-9-conversation-persistent-storage-test-report.md",
            "docs/dev/phase8-0-0-9-conversation-persistent-storage-change-report.md"
        ],
        "metadata": {
            "phase": "8.0.13",
            "status": "completed",
            "type": "feature",
            "details": "Conversation 모델 추가, 대화 기록 저장/조회/검색 API, 세션 ID 관리"
        }
    },
    {
        "timestamp": "2026-01-10T16:30:00.000000",
        "date": "2026-01-10",
        "time": "16:30:00",
        "action": "feature",
        "description": "Phase 8.0.0: 고급 검색 기능 - 복합 검색, 날짜 범위 검색, 필터링",
        "files": [
            "backend/routers/search.py",
            "docs/dev/phase8-0-0-10-advanced-search-feature-test-report.md",
            "docs/dev/phase8-0-0-10-advanced-search-feature-change-report.md"
        ],
        "metadata": {
            "phase": "8.0.14",
            "status": "completed",
            "type": "feature",
            "details": "복합 검색 기본 구조, 날짜 범위 검색, 파일 형식/프로젝트/라벨 필터링"
        }
    },
    {
        "timestamp": "2026-01-10T17:00:00.000000",
        "date": "2026-01-10",
        "time": "17:00:00",
        "action": "feature",
        "description": "Phase 8.0.0: 정렬 옵션 추가 - 주요 페이지에 정렬 옵션 추가",
        "files": [
            "backend/routers/knowledge.py",
            "backend/routers/approval.py",
            "backend/routers/logs.py",
            "backend/routers/search.py",
            "docs/dev/phase8-0-0-14-sorting-options-test-report.md",
            "docs/dev/phase8-0-0-14-sorting-options-change-report.md"
        ],
        "metadata": {
            "phase": "8.0.14-1",
            "status": "completed",
            "type": "feature",
            "details": "청크 목록 정렬 (날짜, 인덱스, 제목), 승인 대기 청크 정렬, 로그 정렬, 검색 결과 정렬"
        }
    },
    {
        "timestamp": "2026-01-10T17:30:00.000000",
        "date": "2026-01-10",
        "time": "17:30:00",
        "action": "feature",
        "description": "Phase 8.0.0: 일괄 작업 기능 - 관리자 페이지에 일괄 작업 기능 추가",
        "files": [
            "backend/routers/approval.py",
            "docs/dev/phase8-0-0-15-batch-operations-test-report.md",
            "docs/dev/phase8-0-0-15-batch-operations-change-report.md"
        ],
        "metadata": {
            "phase": "8.0.15-1",
            "status": "completed",
            "type": "feature",
            "details": "일괄 승인 API, 일괄 거절 API"
        }
    },
    {
        "timestamp": "2026-01-10T18:00:00.000000",
        "date": "2026-01-10",
        "time": "18:00:00",
        "action": "feature",
        "description": "Phase 8.0.0: 답변 스트리밍 - 실시간으로 답변 표시",
        "files": [
            "backend/routers/ai.py",
            "docs/dev/phase8-0-0-16-answer-streaming-test-report.md",
            "docs/dev/phase8-0-0-16-answer-streaming-change-report.md"
        ],
        "metadata": {
            "phase": "8.0.15-3",
            "status": "completed",
            "type": "feature",
            "details": "스트리밍 API (SSE), 실시간 답변 전송"
        }
    },
    {
        "timestamp": "2026-01-10T18:30:00.000000",
        "date": "2026-01-10",
        "time": "18:30:00",
        "action": "feature",
        "description": "Phase 8.0.0: 결과 저장/공유 - Reasoning 결과 및 AI 답변 저장 및 공유",
        "files": [
            "backend/models/models.py",
            "backend/routers/reasoning_results.py",
            "docs/dev/phase8-0-0-17-result-save-share-test-report.md",
            "docs/dev/phase8-0-0-17-result-save-share-change-report.md"
        ],
        "metadata": {
            "phase": "8.0.15-4",
            "status": "completed",
            "type": "feature",
            "details": "ReasoningResult 모델 추가, 결과 저장/조회/삭제 API"
        }
    },
    {
        "timestamp": "2026-01-10T19:00:00.000000",
        "date": "2026-01-10",
        "time": "19:00:00",
        "action": "improvement",
        "description": "Phase 8.0.0: 에러 처리 및 로깅 개선 - 구조화된 로깅, 에러 추적 시스템",
        "files": [
            "backend/services/logging_service.py",
            "backend/routers/error_logs.py",
            "docs/dev/phase8-0-0-11-error-handling-logging-test-report.md",
            "docs/dev/phase8-0-0-11-error-handling-logging-change-report.md"
        ],
        "metadata": {
            "phase": "8.0.18",
            "status": "completed",
            "type": "improvement",
            "details": "구조화된 로깅 (JSON 형식), 에러 추적 시스템, 에러 통계 API"
        }
    },
    {
        "timestamp": "2026-01-10T19:30:00.000000",
        "date": "2026-01-10",
        "time": "19:30:00",
        "action": "security",
        "description": "Phase 8.0.0: 보안 취약점 점검 및 수정 - 의존성 취약점 스캔, 입력 검증 강화",
        "files": [
            "scripts/devtool/security_scan.py",
            "backend/middleware/security.py",
            "backend/utils/validation.py",
            "docs/dev/phase8-0-0-12-security-vulnerability-check-test-report.md",
            "docs/dev/phase8-0-0-12-security-vulnerability-check-change-report.md"
        ],
        "metadata": {
            "phase": "8.0.19",
            "status": "completed",
            "type": "security",
            "details": "보안 스캔 스크립트, 보안 헤더 미들웨어, 입력 검증 유틸리티"
        }
    },
    {
        "timestamp": "2026-01-10T20:00:00.000000",
        "date": "2026-01-10",
        "time": "20:00:00",
        "action": "documentation",
        "description": "Phase 8.0.0: API 문서화 개선 - OpenAPI 스펙 완성, API 예제 추가",
        "files": [
            "backend/main.py",
            "backend/routers/knowledge.py",
            "docs/dev/phase8-0-0-13-api-documentation-improvement-test-report.md",
            "docs/dev/phase8-0-0-13-api-documentation-improvement-change-report.md"
        ],
        "metadata": {
            "phase": "8.0.20",
            "status": "completed",
            "type": "documentation",
            "details": "OpenAPI 스펙 개선, API 설명 및 예제 추가"
        }
    },
    {
        "timestamp": "2026-01-10T20:30:00.000000",
        "date": "2026-01-10",
        "time": "20:30:00",
        "action": "test",
        "description": "Phase 8.0.0: 테스트 커버리지 향상 - 단위/통합/E2E 테스트 추가",
        "files": [
            "tests/__init__.py",
            "tests/conftest.py",
            "tests/test_search_service.py",
            "tests/test_models.py",
            "tests/test_api_routers.py",
            "pytest.ini",
            "requirements.txt",
            "docs/dev/phase8-0-0-18-test-coverage-test-report.md",
            "docs/dev/phase8-0-0-18-test-coverage-change-report.md"
        ],
        "metadata": {
            "phase": "8.0.21",
            "status": "completed",
            "type": "test",
            "details": "pytest 설정, 단위 테스트, 통합 테스트 구조 생성"
        }
    },
    {
        "timestamp": "2026-01-10T21:00:00.000000",
        "date": "2026-01-10",
        "time": "21:00:00",
        "action": "feature",
        "description": "Phase 8.0.0: 자동화 강화 - 스마트 라벨링, 자동 관계 추론, 스케줄링 기능",
        "files": [
            "backend/services/automation_service.py",
            "backend/routers/automation.py",
            "docs/dev/phase8-0-0-19-automation-enhancement-test-report.md",
            "docs/dev/phase8-0-0-19-automation-enhancement-change-report.md"
        ],
        "metadata": {
            "phase": "8.0.15",
            "status": "completed",
            "type": "feature",
            "details": "자동 라벨링, 배치 자동 라벨링, 자동 관계 추론 API"
        }
    },
    {
        "timestamp": "2026-01-10T21:30:00.000000",
        "date": "2026-01-10",
        "time": "21:30:00",
        "action": "feature",
        "description": "Phase 8.0.0: 학습 및 적응 시스템 - 사용자 패턴 학습, 피드백 기반 개선",
        "files": [
            "backend/services/learning_service.py",
            "backend/routers/learning.py",
            "docs/dev/phase8-0-0-20-learning-adaptation-test-report.md",
            "docs/dev/phase8-0-0-20-learning-adaptation-change-report.md"
        ],
        "metadata": {
            "phase": "8.0.6",
            "status": "completed",
            "type": "feature",
            "details": "사용자 패턴 학습, 피드백 시스템, 피드백 기반 개선"
        }
    },
    {
        "timestamp": "2026-01-10T22:00:00.000000",
        "date": "2026-01-10",
        "time": "22:00:00",
        "action": "feature",
        "description": "Phase 8.0.0: 일관성 있는 인격 유지 - 인격 프로필 정의, 모순 감지 메커니즘",
        "files": [
            "backend/services/personality_service.py",
            "backend/routers/personality.py",
            "docs/dev/phase8-0-0-21-personality-consistency-test-report.md",
            "docs/dev/phase8-0-0-21-personality-consistency-change-report.md"
        ],
        "metadata": {
            "phase": "8.0.7",
            "status": "completed",
            "type": "feature",
            "details": "인격 프로필 정의, 모순 감지, 모순 해결 프로세스"
        }
    },
    {
        "timestamp": "2026-01-10T22:30:00.000000",
        "date": "2026-01-10",
        "time": "22:30:00",
        "action": "feature",
        "description": "Phase 8.0.0: 자기 인식 및 메타 인지 - 지식 불확실성 표시, 신뢰도 점수 계산",
        "files": [
            "backend/services/metacognition_service.py",
            "backend/routers/metacognition.py",
            "docs/dev/phase8-0-0-22-metacognition-test-report.md",
            "docs/dev/phase8-0-0-22-metacognition-change-report.md"
        ],
        "metadata": {
            "phase": "8.0.8",
            "status": "completed",
            "type": "feature",
            "details": "신뢰도 점수 계산, 지식 불확실성 표시, 불확실성 맵"
        }
    },
    {
        "timestamp": "2026-01-10T23:00:00.000000",
        "date": "2026-01-10",
        "time": "23:00:00",
        "action": "feature",
        "description": "Phase 8.0.0: 추론 체인 강화 - 다단계 추론 체인 구현, 추론 과정 시각화",
        "files": [
            "backend/services/reasoning_chain_service.py",
            "backend/routers/reasoning_chain.py",
            "docs/dev/phase8-0-0-23-reasoning-chain-enhancement-test-report.md",
            "docs/dev/phase8-0-0-23-reasoning-chain-enhancement-change-report.md"
        ],
        "metadata": {
            "phase": "8.0.9",
            "status": "completed",
            "type": "feature",
            "details": "다단계 추론 체인 구현, 추론 과정 시각화 데이터 생성"
        }
    },
    {
        "timestamp": "2026-01-10T23:30:00.000000",
        "date": "2026-01-10",
        "time": "23:30:00",
        "action": "feature",
        "description": "Phase 8.0.0: 지식 통합 및 세계관 구성 - 지식 통합 알고리즘, 모순 해결 전략",
        "files": [
            "backend/services/knowledge_integration_service.py",
            "backend/routers/knowledge_integration.py",
            "docs/dev/phase8-0-0-24-knowledge-integration-test-report.md",
            "docs/dev/phase8-0-0-24-knowledge-integration-change-report.md"
        ],
        "metadata": {
            "phase": "8.0.10",
            "status": "completed",
            "type": "feature",
            "details": "지식 통합 알고리즘, 모순 해결 전략, 세계관 구성"
        }
    },
    {
        "timestamp": "2026-01-11T00:00:00.000000",
        "date": "2026-01-11",
        "time": "00:00:00",
        "action": "feature",
        "description": "Phase 8.0.0: 파일 형식 지원 확장 - Excel, PowerPoint, 이미지 OCR, HWP 지원",
        "files": [
            "backend/services/file_parser_service.py",
            "backend/routers/file_parser.py",
            "requirements.txt",
            "docs/dev/phase8-0-0-25-file-format-support-test-report.md",
            "docs/dev/phase8-0-0-25-file-format-support-change-report.md"
        ],
        "metadata": {
            "phase": "8.0.12",
            "status": "completed",
            "type": "feature",
            "details": "Excel (.xlsx, .xls), PowerPoint (.pptx, .ppt), 이미지 OCR (.jpg, .jpeg, .png, .gif), HWP 기본 구조"
        }
    },
    {
        "timestamp": "2026-01-11T00:30:00.000000",
        "date": "2026-01-11",
        "time": "00:30:00",
        "action": "system",
        "description": "Phase 8.0.0: 전체 작업 완료 - 26개 작업 항목 모두 완료 (성능 최적화, 기능 확장, 안정성 강화, 인격체 모델 구축)",
        "files": [
            "docs/dev/phase8-0-0-final-summary-report.md",
            "docs/dev/phase8-0-0-summary-report.md"
        ],
        "metadata": {
            "phase": "8.0.0",
            "status": "completed",
            "type": "phase_completion",
            "tasks_completed": 26,
            "services_created": 11,
            "routers_created": 14,
            "scripts_created": 4,
            "reports_generated": 52,
            "details": "검색/임베딩/DB 성능 최적화, 맥락 이해/기억 시스템/자동화/학습 시스템 구축, 백업/무결성/에러 처리/보안 강화, 인격체 모델 기능 추가, 파일 형식 지원 확장"
        }
    }
]

# 기존 JSON 로드
if WORK_LOG_JSON.exists():
    try:
        with open(WORK_LOG_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
        existing_entries = data.get('entries', [])
    except:
        existing_entries = []
else:
    existing_entries = []

# 기존 항목과 새 항목 병합 (중복 제거)
existing_timestamps = {e.get('timestamp') for e in existing_entries}
new_entries = [e for e in phase8_entries if e.get('timestamp') not in existing_timestamps]

# 모든 항목 합치기
all_entries = existing_entries + new_entries

# timestamp 순으로 정렬
all_entries.sort(key=lambda x: x.get('timestamp', ''))

data = {
    'entries': all_entries,
    'last_update': datetime.now().isoformat()
}

with open(WORK_LOG_JSON, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"✅ Phase 8.0.0 작업 로그 추가 완료")
print(f"✅ {len(new_entries)}개의 새 항목이 추가되었습니다.")
print(f"총 {len(all_entries)}개의 항목이 있습니다.")
