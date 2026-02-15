---
doc_type: implementation-guide
guide_domain: improvement-roadmap
version: 1.0
status: active
owner: human
last_updated: 2026-02-06
---

# 개선 방안 실행 가이드

**목적**: Phase 기반 자동개발 방법론의 리스크를 해결하기 위한 구체적인 실행 계획 및 체크리스트 제공

---

## 1. Phase 1 개선 사항 (긴급, 1주일)

### 1.1 개선 항목 1: Done Definition 양식 표준화

#### 목표

- 모든 Phase/Task의 Done Definition을 일관된 양식으로 표준화
- 검증 기준 명확화로 재작업 감소

#### 현재 상태

- 각 Task 문서에서 Done Definition 형식이 불일치
- 검증 항목이 모호하거나 누락됨
- 완료 판정 시 해석 차이 발생

#### 개선 방안

**1단계: 표준 양식 정의** (2시간)

```markdown
## 완료 기준 (Done Definition)

### 기능 요구사항

- [ ] 기능 1 구현 (구체적 설명)
- [ ] 기능 2 구현 (구체적 설명)
- [ ] 기능 3 구현 (구체적 설명)

### 테스트

- [ ] 단위 테스트 통과 (커버리지 80% 이상)
- [ ] E2E 테스트 통과 (해당 Phase 시나리오)
- [ ] 회귀 테스트 통과 (선행 Phase 기능)

### 코드 품질

- [ ] 코드 리뷰 승인
- [ ] 린터/형식 검사 통과
- [ ] 성능 목표 달성 (예: 응답시간 <500ms)

### 문서

- [ ] 사용자 가이드 작성
- [ ] 변경 이력 문서화
- [ ] API 문서 업데이트 (해당 시)
```

**2단계: 기존 Task 문서 마이그레이션** (6시간)

```bash
# 대상 폴더
docs/phases/phase-*/tasks/
docs/phases/phase-*/

# 마이그레이션 절차
for each task_document:
    1. 기존 Done Definition 섹션 추출
    2. 표준 양식으로 변환
    3. 누락된 항목 추가
    4. 검증 후 merge
```

**3단계: 검증 자동화** (2시간)

```python
# scripts/validate_done_definition.py
import re
from pathlib import Path

def validate_done_definition(task_doc_path):
    """
    Task 문서의 Done Definition 검증
    """
    doc_text = Path(task_doc_path).read_text(encoding='utf-8')

    required_sections = [
        "기능 요구사항",
        "테스트",
        "코드 품질",
        "문서"
    ]

    errors = []
    for section in required_sections:
        if section not in doc_text:
            errors.append(f"Missing section: {section}")

    # 체크리스트 형식 검증
    if "- [ ]" not in doc_text:
        errors.append("Done Definition must use checklist format (- [ ])")

    return errors

# 사용 예
if __name__ == "__main__":
    task_files = Path("docs/phases").rglob("*-task.md")
    for task_file in task_files:
        errors = validate_done_definition(task_file)
        if errors:
            print(f"❌ {task_file}")
            for error in errors:
                print(f"   - {error}")
        else:
            print(f"✅ {task_file}")
```

#### 체크리스트

- [ ] 표준 양식 문서 작성 및 공유
- [ ] Phase 10-1 Task 마이그레이션 (파일럿)
- [ ] 검증 스크립트 구현
- [ ] 전체 Task 일괄 마이그레이션
- [ ] 검증 자동화 CI/CD 통합

#### 예상 효과

- ✅ 재작업 감소: 40%
- ✅ Task 검증 시간: 50% 단축
- ✅ 완료 판정 일관성: 90% 향상

---

### 1.2 개선 항목 2: Health-check 자동화

#### 목표

- 테스트 실행 전 환경 자동 검증
- 환경 오류로 인한 테스트 실패 사전 방지

#### 현재 상태

- 환경 구축 수작업 (Backend 기동, DB 연결 등)
- 오류 발생 시 원인 파악 어려움
- 반복 수동 설정으로 시간 낭비

#### 개선 방안

**1단계: Backend Health-check 엔드포인트** (1시간)

```python
# backend/main.py
from fastapi import FastAPI, HTTPException
from datetime import datetime

app = FastAPI()

@app.get("/health")
async def health_check():
    """
    서비스 상태 확인 엔드포인트
    - 서비스 가용성
    - DB 연결 상태
    - 의존성 서비스 상태
    """
    try:
        # DB 연결 확인
        db_status = check_database()

        # Qdrant 연결 확인
        vector_store_status = check_vector_store()

        return {
            "status": "ok",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "components": {
                "database": db_status,
                "vector_store": vector_store_status,
                "llm": "ok"  # LLM 서비스 상태
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )

def check_database():
    """DB 연결 상태 확인"""
    try:
        # DB 쿼리 실행
        db.execute("SELECT 1")
        return "healthy"
    except Exception:
        return "unhealthy"

def check_vector_store():
    """Vector store(Qdrant) 연결 상태 확인"""
    try:
        # Qdrant API 호출
        response = requests.get("http://localhost:6333/health")
        return "healthy" if response.status_code == 200 else "unhealthy"
    except Exception:
        return "unhealthy"
```

**2단계: 환경 검증 스크립트** (1시간)

```bash
#!/bin/bash
# scripts/verify-env.sh

set -e

echo "🔍 Verifying test environment..."
echo ""

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

errors=0

# 1. Backend 확인
echo "Checking Backend service..."
if curl -s http://localhost:8001/health | grep -q '"status".*"ok"'; then
    echo -e "${GREEN}✅${NC} Backend is running"
else
    echo -e "${RED}❌${NC} Backend not running or health check failed"
    echo "   Run: python backend/main.py"
    ((errors++))
fi

# 2. PostgreSQL 확인
echo "Checking PostgreSQL..."
if pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo -e "${GREEN}✅${NC} PostgreSQL is running"
else
    echo -e "${RED}❌${NC} PostgreSQL not running"
    echo "   Run: docker-compose up postgres"
    ((errors++))
fi

# 3. Qdrant 확인
echo "Checking Qdrant vector store..."
if curl -s http://localhost:6333/health | grep -q '"ok"'; then
    echo -e "${GREEN}✅${NC} Qdrant is running"
else
    echo -e "${RED}❌${NC} Qdrant not running"
    echo "   Run: docker-compose up qdrant"
    ((errors++))
fi

# 4. Base URL 연결성 확인
echo "Checking Base URL connectivity..."
if curl -s http://localhost:8001 > /dev/null 2>&1; then
    echo -e "${GREEN}✅${NC} Base URL is accessible"
else
    echo -e "${RED}❌${NC} Base URL not accessible"
    ((errors++))
fi

# 5. 테스트 데이터베이스 확인
echo "Checking test database..."
if PGPASSWORD=postgres psql -h localhost -U postgres -d personal_ai_brain_test -c "SELECT 1" > /dev/null 2>&1; then
    echo -e "${GREEN}✅${NC} Test database is ready"
else
    echo -e "${YELLOW}⚠️${NC}  Test database not initialized"
    echo "   Run: python scripts/init-test-db.py"
fi

echo ""
if [ $errors -eq 0 ]; then
    echo -e "${GREEN}✅ All environment checks passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ $errors environment check(s) failed!${NC}"
    exit 1
fi
```

**3단계: webtest.py 통합** (1시간)

```python
# scripts/webtest.py (수정)

import subprocess
import sys

def verify_environment():
    """환경 검증 실행"""
    print("Verifying test environment...")
    result = subprocess.run(
        ["bash", "scripts/verify-env.sh"],
        capture_output=True,
        text=True
    )

    print(result.stdout)
    if result.returncode != 0:
        print("❌ Environment verification failed!")
        print(result.stderr)
        sys.exit(1)

    print("✅ Environment verified!")

def main():
    if len(sys.argv) < 2:
        print("Usage: python webtest.py [PHASE] [ACTION]")
        sys.exit(1)

    phase = sys.argv[1]
    action = sys.argv[2] if len(sys.argv) > 2 else "start"

    # 환경 검증 (모든 명령 전에 실행)
    verify_environment()

    if action == "start":
        # E2E 실행
        run_e2e(phase)
    # ... 기타 로직
```

#### 체크리스트

- [ ] Backend health-check 엔드포인트 구현
- [ ] 환경 검증 스크립트 작성 (verify-env.sh)
- [ ] webtest.py에 환경 검증 통합
- [ ] 동료 테스트 및 피드백
- [ ] 자동화 CI/CD 통합

#### 예상 효과

- ✅ 환경 오류로 인한 테스트 실패: 90% 감소
- ✅ 테스트 시작 전 대기 시간: 80% 단축
- ✅ 오류 원인 파악 시간: 70% 단축

---

### 1.3 개선 항목 3: Phase별 테스트 매트릭스 정의

#### 목표

- Phase별 권장 테스트 방안(E2E/MCP/페르소나) 정의
- 테스트 커버리지 표준화

#### 현재 상태

- 테스트 방안 선택 기준 미정
- 일부 Phase는 MCP만, 일부는 E2E만 → 불균형
- 선행 Phase 회귀 테스트 미실행 위험

#### 개선 방안

**1단계: Phase별 테스트 매트릭스 정의** (1시간)

```markdown
# Phase별 권장 테스트 조합

| Phase ID | Phase 명           | E2E | MCP | 페르소나 | 회귀 | 비고                      |
| -------- | ------------------ | --- | --- | -------- | ---- | ------------------------- |
| 9-1      | 보안 강화          | ✅  | ✅  | ⚠️       | ✅   | 보안 중심, E2E + MCP 필수 |
| 9-3      | AI 기능 고도화     | ✅  | ✅  | ✅       | ✅   | 모든 관점 권장            |
| 10-1     | UX/UI 개선         | ✅  | ✅  | ⚠️       | ✅   | UI 중심, E2E + MCP 필수   |
| 10-2     | 모드별 분석 고도화 | ✅  | ✅  | ⚠️       | ✅   | 분석 기능, E2E + MCP 필수 |
| 10-3     | 결과물 형식 개선   | ✅  | ⚠️  | ⚠️       | ✅   | 선택적, E2E 필수          |
| 10-4     | 고급 기능          | ✅  | ⚠️  | ⚠️       | ✅   | 선택적, E2E 필수          |

### 범례

- ✅: 필수 (반드시 실행)
- ⚠️: 권장 (선택적, 권장)
- ❌: 불필요 (해당 없음)

### 회귀 테스트 정책

- 모든 Phase: Phase 시작 전 선행 Phase E2E 실행 필수
```

**2단계: 테스트 선택 규칙 문서화** (30분)

```markdown
## Phase별 테스트 선택 규칙

### Rule 1: UI 변경이 있는 Phase
```

IF Phase contains UI/Frontend changes
THEN E2E + MCP required (최소)

예: Phase 9-1 (보안 UI), Phase 10-1 (UX 개선) → E2E + MCP 필수

```

### Rule 2: AI 기능 변경이 있는 Phase
```

IF Phase contains AI logic or algorithm changes
THEN Persona approach recommended

예: Phase 9-3 (AI 고도화) → 3관점(기획자/개발자/UI) 페르소나 테스트 권장

```

### Rule 3: 회귀 테스트
```

IF Task or Phase modifies existing functionality
THEN Previous Phase E2E test required

예: Phase 10-2 실행 전 Phase 9-1, 9-3 E2E 실행

```

### Rule 4: 성능 영향 Phase
```

IF Phase might impact performance or scalability
THEN Performance test required

예: Phase 10-2 (분석 고도화) → 성능 테스트 추가

```

```

**3단계: 테스트 자동화 규칙 추가** (30분)

```python
# scripts/test_recommendation.py

PHASE_TEST_MATRIX = {
    "9-1": {"e2e": True, "mcp": True, "persona": False, "regression": True},
    "9-3": {"e2e": True, "mcp": True, "persona": True, "regression": True},
    "10-1": {"e2e": True, "mcp": True, "persona": False, "regression": True},
    "10-2": {"e2e": True, "mcp": True, "persona": False, "regression": True},
    "10-3": {"e2e": True, "mcp": False, "persona": False, "regression": True},
    "10-4": {"e2e": True, "mcp": False, "persona": False, "regression": True},
}

def get_test_recommendation(phase_id):
    """Phase별 권장 테스트 반환"""
    if phase_id not in PHASE_TEST_MATRIX:
        return None

    tests = PHASE_TEST_MATRIX[phase_id]
    recommendations = []

    if tests["regression"]:
        recommendations.append("Run previous Phase E2E tests")

    if tests["e2e"]:
        recommendations.append(f"python webtest.py {phase_id} start")

    if tests["mcp"]:
        recommendations.append(f"MCP test: Use Cursor @webtest checklist")

    if tests["persona"]:
        recommendations.append(f"Persona test: 3관점(기획자/개발자/UI) 테스트")

    return recommendations

# 사용 예
if __name__ == "__main__":
    phase = "9-1"
    recommendations = get_test_recommendation(phase)
    print(f"Phase {phase} test recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
```

#### 체크리스트

- [ ] Phase별 테스트 매트릭스 문서 작성
- [ ] 테스트 선택 규칙 정의 및 공유
- [ ] test_recommendation.py 스크립트 구현
- [ ] 현재 Phase(10-1) 적용 테스트
- [ ] 모든 Phase에 적용 및 검증

#### 예상 효과

- ✅ 테스트 커버리지: 30% 향상
- ✅ 테스트 선택 시간: 80% 단축
- ✅ 회귀 버그: 50% 감소

---

## 2. Phase 2 개선 사항 (중기, 2주일)

### 2.1 개선 항목 4: 회귀 E2E 자동 체이닝

### 2.2 개선 항목 5: AI 자동 생성물 검증 체크리스트

### 2.3 개선 항목 6: Task 크기 기준 자동 검증

(자세한 내용은 [phase-based-development-methodology-analysis.md](phase-based-development-methodology-analysis.md) §7.2, §7.3 참고)

---

## 3. Phase 3 개선 사항 (장기, 1개월)

### 3.1 개선 항목 7: MCP 설정 자동화

### 3.2 개선 항목 8: Plan 명확성 검증 도구

### 3.3 개선 항목 9: 보안 감사 체크리스트 정의

(자세한 내용은 [phase-based-development-methodology-analysis.md](phase-based-development-methodology-analysis.md) §7.3, §8 참고)

---

## 4. 실행 추진 체계

### 4.1 담당자 할당

| 개선 항목              | 담당자  | 예상 시간 | 시작일     | 완료일     |
| ---------------------- | ------- | --------- | ---------- | ---------- |
| Done Definition 표준화 | AI/QA   | 4시간     | 2026-02-07 | 2026-02-07 |
| Health-check 자동화    | Backend | 2시간     | 2026-02-07 | 2026-02-08 |
| 테스트 매트릭스 정의   | QA      | 2시간     | 2026-02-08 | 2026-02-09 |

### 4.2 진행 현황 추적

- [ ] Phase 1 (1주일) 시작
- [ ] 3개 개선사항 일일 진행 보고
- [ ] 테스트 및 검증
- [ ] Phase 2 (2주일) 시작
- [ ] 전체 개선 계획 진행률 모니터링

### 4.3 검증 기준

각 개선 사항의 성공 기준:

| 개선 항목       | 성공 기준                           |
| --------------- | ----------------------------------- |
| Done Definition | 전체 Task의 90% 이상 표준 양식 적용 |
| Health-check    | 환경 오류 사전 감지율 95% 이상      |
| 테스트 매트릭스 | Phase별 권장 테스트 100% 실행       |

---

## 참고 문서

- [phase-based-development-methodology-analysis.md](phase-based-development-methodology-analysis.md) — 전체 분석 및 개선 방안
- `docs/rules/common/references/common-phase-document-taxonomy.md` — Phase 문서 분류
- `docs/rules/ai/references/ai-rule-task-inspection.md` — Task 검사 규정

---

**가이드 작성**: 2026-02-06
**상태**: Draft (Phase 1 시작 전)
