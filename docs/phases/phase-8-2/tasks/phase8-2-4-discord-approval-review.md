# Phase 8-2-4: Discord 승인 루프 구축 - 검토 문서

**작성일**: 2026-01-28  
**검토 목적**: Phase 8-2-4 구현 전 사전 검토 및 준비  
**예상 소요 시간**: 2-3일  
**우선순위**: High

---

## 📋 개요

Phase 8-2-4는 n8n 워크플로우와 Discord를 연동하여 Plan 문서에 대한 승인 루프를 구축하는 작업입니다. 사용자가 Discord에서 Plan을 검토하고 승인/거절/수정 요청을 할 수 있도록 합니다.

---

## 🎯 목표

### 주요 목표

1. **Discord를 통한 승인 요청 전송**
   - Plan 문서를 Discord 메시지로 전송
   - 승인/거절/수정 요청 버튼 제공

2. **승인 상태 관리**
   - 사용자 응답을 PostgreSQL에 저장
   - 승인 이력 추적

3. **자동화된 워크플로우**
   - n8n에서 전체 프로세스 자동화
   - 승인 상태에 따른 다음 단계 자동 진행

---

## 📊 현재 준비 상태

### ✅ 완료된 작업

1. **Discord 봇 설정** (Phase 8-1-1)
   - ✅ Discord Developer Portal 접속
   - ✅ 새 Application 생성
   - ✅ Bot 생성 및 Token 발급
   - ✅ Bot 권한 설정 (메시지 읽기/쓰기, 반응 추가/읽기)
   - ✅ 서버에 봇 초대
   - ✅ Webhook URL 발급 (채널별)
   - ✅ n8n에 Discord credentials 등록

2. **PostgreSQL 스키마** (Phase 8-1-1)
   - ✅ `workflow_phases` 테이블 생성
   - ✅ `workflow_plans` 테이블 생성
   - ✅ `workflow_approvals` 테이블 생성
   - ✅ 인덱스 및 외래키 관계 설정

3. **n8n 환경** (Phase 8-1-2, 8-3-1)
   - ✅ n8n PostgreSQL 마이그레이션 완료
   - ✅ Docker Compose 통합 완료
   - ✅ Execute Command 노드 활성화

### 📋 workflow_approvals 테이블 구조

```sql
CREATE TABLE workflow_approvals (
    id SERIAL PRIMARY KEY,
    phase_id INT REFERENCES workflow_phases(id) ON DELETE CASCADE,
    step VARCHAR(50),
    version INT,
    feedback TEXT,
    approved BOOLEAN,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**필드 설명:**

- `phase_id`: 승인 대상 Phase ID
- `step`: 승인 단계 (예: "plan-review", "todo-review")
- `version`: Plan 버전 번호
- `feedback`: 사용자 피드백 (수정 요청 시)
- `approved`: 승인 여부 (true/false)
- `created_at`: 승인 요청 시간

---

## 🔧 구현 계획

### 1. Discord 봇 워크플로우 설계

#### 1.1 승인 요청 메시지 형식

**메시지 구조:**

```
📋 Phase-8 Plan v1 승인 요청

**Phase**: Phase-8-Current-State
**버전**: 1
**생성일**: 2026-01-28

**계획 요약:**
- Phase 8-2-4: Discord 승인 루프 구축 (2-3일)
- Phase 8-3: 백업/복원 UI 구축 (1-2일)
- Phase 8-4/8-5: 선택적 작업 (2-3일씩)

**전체 계획**: [링크 또는 첨부파일]

반응으로 응답해주세요:
✅ 승인
✏️ 수정 필요 (댓글로 피드백)
❌ 거절
```

**구현 방법:**

- n8n Discord Webhook 노드 사용
- 메시지에 반응(emoji) 추가 가능하도록 설정
- Plan 내용은 파일 첨부 또는 링크 제공

#### 1.2 승인/거절 버튼 인터페이스

**옵션 A: Discord 반응(Reaction) 사용** (권장)

- 장점: 간단하고 Discord 네이티브
- 단점: 반응 감지가 복잡할 수 있음

**옵션 B: Discord Slash Command 사용**

- 장점: 구조화된 입력
- 단점: 봇에 Slash Command 등록 필요

**옵션 C: Discord Message Components (버튼) 사용**

- 장점: 가장 직관적
- 단점: Discord.js 라이브러리 필요, n8n에서 직접 지원 안 함

**권장 방법**: **옵션 A (반응 사용)**

- n8n Discord Trigger로 반응 감지
- ✅ (checkmark) = 승인
- ✏️ (pencil) = 수정 필요
- ❌ (cross) = 거절

#### 1.3 승인 상태 추적 로직

**상태 흐름:**

```
1. Plan 생성 → status: 'draft'
2. Discord 전송 → status: 'pending_approval'
3. 사용자 반응:
   - ✅ 승인 → status: 'approved', workflow_approvals에 기록
   - ✏️ 수정 필요 → status: 'revision_requested', feedback 저장
   - ❌ 거절 → status: 'rejected', workflow_approvals에 기록
4. 수정 요청 시 → Plan 수정 → status: 'draft' → 다시 2번으로
```

---

### 2. n8n Discord 워크플로우 구축

#### 2.1 워크플로우 구조

```
[Manual Trigger]
    ↓
[Read Binary File] (phase-8-plan.md 읽기)
    ↓
[PostgreSQL] (workflow_plans에서 최신 Plan 조회)
    ↓
[Discord Webhook] (승인 요청 메시지 전송)
    ↓
[Wait] (사용자 응답 대기, 최대 24시간)
    ↓
[Discord Trigger] (반응 감지)
    ↓
[IF] (반응 타입 분기)
    ├─ ✅ 승인 → [PostgreSQL] (approvals 저장, plan status 업데이트)
    ├─ ✏️ 수정 필요 → [PostgreSQL] (feedback 저장, plan status 업데이트)
    └─ ❌ 거절 → [PostgreSQL] (approvals 저장, plan status 업데이트)
```

#### 2.2 주요 노드 설정

**Discord Webhook 노드:**

- Credential: `Discord Webhook-n8n-ai-personal-brain`
- Method: POST
- Content: JSON
- Body:
  ```json
  {
    "content": "📋 Phase-8 Plan v1 승인 요청",
    "embeds": [
      {
        "title": "Phase-8 Plan",
        "description": "계획 요약...",
        "fields": [
          { "name": "Phase", "value": "Phase-8-Current-State", "inline": true },
          { "name": "버전", "value": "1", "inline": true },
          { "name": "생성일", "value": "2026-01-28", "inline": true }
        ]
      }
    ]
  }
  ```

**Discord Trigger 노드:**

- Event: Message Reaction Added
- Channel: 승인 채널 ID
- Emoji Filter: ✅, ✏️, ❌

**PostgreSQL 노드 (승인 저장):**

- Operation: Execute Query
- Query:
  ```sql
  INSERT INTO workflow_approvals (
    phase_id, step, version, feedback, approved, created_at
  ) VALUES (
    $1, 'plan-review', $2, $3, $4, NOW()
  )
  RETURNING id;
  ```

#### 2.3 루프 구현 (최대 5회 수정)

**구조:**

```
[Set] (iteration_count = 0)
    ↓
[Loop] (최대 5회)
    ├─ [IF] (iteration_count < 5)
    │   ├─ [Discord Webhook] (승인 요청)
    │   ├─ [Wait] (응답 대기)
    │   ├─ [Discord Trigger] (반응 감지)
    │   ├─ [IF] (반응 타입)
    │   │   ├─ ✅ 승인 → [Break Loop]
    │   │   ├─ ✏️ 수정 → [Set] (iteration_count++), [Continue Loop]
    │   │   └─ ❌ 거절 → [Break Loop]
    │   └─ [Set] (iteration_count++)
    └─ [IF] (iteration_count >= 5)
        └─ [Error] (최대 반복 횟수 초과)
```

---

### 3. PostgreSQL 승인 상태 관리

#### 3.1 API 엔드포인트 (선택적)

**필요 시 FastAPI 엔드포인트 추가:**

```python
# backend/routers/approval.py에 추가

@router.post("/api/workflow/approvals")
async def create_approval(approval: ApprovalCreate):
    """승인 요청 생성"""
    # workflow_approvals 테이블에 저장
    pass

@router.get("/api/workflow/approvals/{phase_id}")
async def get_approvals(phase_id: int):
    """Phase별 승인 이력 조회"""
    # workflow_approvals 테이블에서 조회
    pass

@router.patch("/api/workflow/plans/{plan_id}/status")
async def update_plan_status(plan_id: int, status: str):
    """Plan 상태 업데이트"""
    # workflow_plans 테이블 업데이트
    pass
```

#### 3.2 승인 상태 조회

**n8n PostgreSQL 노드:**

```sql
-- 승인 이력 조회
SELECT
    a.id,
    a.step,
    a.version,
    a.feedback,
    a.approved,
    a.created_at,
    p.phase_name,
    pl.content as plan_content
FROM workflow_approvals a
JOIN workflow_phases p ON a.phase_id = p.id
LEFT JOIN workflow_plans pl ON pl.phase_id = p.id AND pl.version = a.version
WHERE a.phase_id = $1
ORDER BY a.created_at DESC;
```

---

### 4. 테스트 및 검증

#### 4.1 테스트 시나리오

**시나리오 1: 정상 승인**

1. Plan 생성 및 Discord 전송
2. 사용자가 ✅ 반응 추가
3. PostgreSQL에 승인 기록 저장
4. Plan status가 'approved'로 변경

**시나리오 2: 수정 요청**

1. Plan 생성 및 Discord 전송
2. 사용자가 ✏️ 반응 추가 + 댓글로 피드백
3. PostgreSQL에 feedback 저장
4. Plan status가 'revision_requested'로 변경
5. Plan 수정 후 다시 전송 (최대 5회)

**시나리오 3: 거절**

1. Plan 생성 및 Discord 전송
2. 사용자가 ❌ 반응 추가
3. PostgreSQL에 거절 기록 저장
4. Plan status가 'rejected'로 변경

**시나리오 4: 타임아웃**

1. Plan 생성 및 Discord 전송
2. 24시간 내 응답 없음
3. 알림 메시지 전송
4. Plan status 유지 또는 'timeout'으로 변경

#### 4.2 검증 체크리스트

- [ ] Discord 메시지 정상 전송
- [ ] 반응 감지 정상 작동
- [ ] PostgreSQL 저장 정상 작동
- [ ] 상태 업데이트 정상 작동
- [ ] 루프 정상 작동 (수정 요청 시)
- [ ] 타임아웃 처리 정상 작동
- [ ] 에러 처리 정상 작동

---

### 5. 문서화

#### 5.1 가이드 문서 작성

**필요 문서:**

- `docs/phases/phase-8-0/phase8-2-4-discord-approval-guide.md`
  - Discord 승인 루프 사용 가이드
  - 워크플로우 설정 방법
  - 트러블슈팅

#### 5.2 코드 주석

- n8n 워크플로우 각 노드에 설명 추가
- PostgreSQL 쿼리 주석 추가

---

## ⚠️ 리스크 및 대응 방안

### 리스크 1: Discord API 제한

**문제:**

- Discord API Rate Limit (50 requests/second)
- Webhook Rate Limit (30 requests/minute)

**대응:**

- 요청 간격 조절 (최소 2초 간격)
- Rate limit 감지 및 재시도 로직
- 큐 시스템 도입 (필요 시)

### 리스크 2: 승인 상태 동기화 실패

**문제:**

- Discord 반응과 PostgreSQL 상태 불일치
- 네트워크 오류로 인한 저장 실패

**대응:**

- 트랜잭션 사용 (원자성 보장)
- 재시도 로직 구현
- 수동 동기화 스크립트 준비
- 정기적 동기화 체크

### 리스크 3: Discord 봇 권한 문제

**문제:**

- 봇이 메시지를 읽지 못함
- 반응을 추가하지 못함

**대응:**

- 봇 권한 사전 확인 (메시지 읽기, 반응 추가/읽기)
- 테스트 환경에서 사전 검증
- 권한 오류 시 명확한 에러 메시지

### 리스크 4: 반응 감지 실패

**문제:**

- n8n Discord Trigger가 반응을 감지하지 못함
- 여러 사용자가 동시에 반응 추가

**대응:**

- 반응 감지 로직 테스트 강화
- 첫 번째 반응만 처리하도록 설정
- 타임아웃 설정 (24시간)

---

## 📅 예상 일정

### Day 1 (0.5일)

- Discord 봇 워크플로우 설계
- 메시지 형식 정의
- 승인 상태 추적 로직 설계

### Day 2 (1일)

- n8n Discord 워크플로우 구축
- Discord Webhook 노드 설정
- Discord Trigger 노드 설정
- PostgreSQL 연동

### Day 3 (0.5일)

- 테스트 및 검증
- 문서화
- 버그 수정

---

## 🔗 관련 문서

- `docs/phases/phase-8-0/phase8-1-0-plan.md` - Phase 8-1 전체 계획
- `docs/phases/phase-8-0/phase8-1-1-database-schema-n8n-setting.md` - PostgreSQL 스키마
- `docs/phases/phase-8-0/phase8-2-1-code-analysis-workflow-guide.md` - 코드 분석 워크플로우 가이드
- `docs/phases/phase-8-plan.md` - Phase 8 실행 계획
- `docs/phases/gap-analysis.md` - Gap 분석

---

## ✅ 시작 전 체크리스트

- [ ] Discord 봇이 서버에 초대되어 있음
- [ ] Discord Webhook URL 확인
- [ ] n8n에 Discord credentials 등록 확인
- [ ] PostgreSQL `workflow_approvals` 테이블 존재 확인
- [ ] n8n 워크플로우 생성 권한 확인
- [ ] 테스트용 Discord 채널 준비

---

**작성일**: 2026-01-28  
**작성자**: AI Assistant  
**문서 버전**: 1.0  
**다음 단계**: Phase 8-2-4 구현 시작
