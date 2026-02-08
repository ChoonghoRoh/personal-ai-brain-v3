# n8n Workflow 구축 Todo List

## 🎯 프로젝트 목표

Phase별 AI 협업 개발 자동화 시스템 구축

---

## 📋 Phase 8-1-0: 환경 준비 (1-2일)

### 8-1-1 Discord 봇 설정

- [x] Discord Developer Portal 접속
- [x] 새 Application 생성
- [x] Bot 생성 및 Token 발급
- [x] Bot 권한 설정 (메시지 읽기/쓰기, 반응 추가/읽기)
- [x] 서버에 봇 초대
- [x] Webhook URL 발급 (채널별)
- [x] n8n에 Discord credentials 등록

**예상 시간:** 30분  
**필요:** Discord 계정

---

### 8-1-1 Discord 봇 설정

- [x] OpenAI API 키 발급 (GPT용)
- [x] Anthropic API 키 확인 (또는 Claude Pro 인증)
- [x] n8n에 API credentials 등록
- [x] 테스트 API 호출 (각각 1회씩)

**예상 시간:** 20분  
**비용:** API 키 발급 무료, 사용량만 과금

---

### 8-1-3 PostgreSQL 스키마 설계 ✅

- [x] 데이터베이스 테이블 설계 및 생성
- [x] 인덱스 생성
- [x] 외래키 관계 설정
- [x] CRUD 테스트 (삽입/조회/수정/삭제) 완료

**상세 내용:** [phase8-1-1-database-schema-n8n-setting.md](./phase8-1-1-database-schema-n8n-setting.md) 참조

**생성된 테이블:**

- `workflow_phases` - Phase 정보 관리
- `workflow_plans` - Plan 문서 저장
- `workflow_approvals` - 승인 루프 관리
- `workflow_tasks` - Task 정보
- `workflow_test_results` - 테스트 결과

**다음 단계:**

- [x] n8n에서 PostgreSQL Credential 등록
- [x] n8n 연결 테스트

**예상 시간:** 1시간 (완료)  
**완료 기준:** ✅ 테이블 생성 및 연결 확인 완료

---

### 8-1-2 n8n PostgreSQL 마이그레이션 ✅

- [x] PostgreSQL n8n 데이터베이스 생성
- [x] docker-compose.yml PostgreSQL 설정 활성화
- [x] n8n 컨테이너 재시작 (PostgreSQL 모드)
- [x] PostgreSQL 테이블 자동 생성 확인
- [x] n8n 웹 인터페이스 접속 확인

**예상 시간:** 30분 (완료)  
**완료 기준:** ✅ n8n이 PostgreSQL로 정상 작동

**상세 내용:** [phase8-1-2-n8n-postgresql-migration.md](./phase8-1-2-n8n-postgresql-migration.md) 참조

**마이그레이션 결과:**
- n8n이 PostgreSQL `n8n` 데이터베이스 사용
- 프로젝트 메인 DB와 통합 관리
- 향후 확장성 확보

---

## 📋 Phase 8-2: Sub-workflow 1 구축 (2-3일)

### 8-2-1 코드 분석 워크플로우 (Claude Code)

- [ ] n8n 컨테이너 재시작 (볼륨 마운트 포함) ✅
- [ ] n8n에서 "Code Analysis" 워크플로우 생성
- [ ] Manual Trigger 노드 추가
- [ ] Execute Command 노드 (Claude Code CLI 실행)
  ```bash
  cd /workspace/project && claude "
  1. backend 폴더 전체 코드 분석
  2. 현재 구현 상태 정리
  3. current-state.md 파일 생성
  "
  ```
- [ ] Read Binary Files 노드 (current-state.md 읽기)
- [ ] PostgreSQL 노드 (phases 테이블에 저장)
- [ ] 테스트 실행 및 검증

**예상 시간:** 2시간  
**완료 기준:** current-state.md 생성 및 DB 저장 확인

**상세 가이드:** [phase8-2-1-code-analysis-workflow-guide.md](./phase8-2-1-code-analysis-workflow-guide.md) 참조

**n8n 컨테이너 설정:**

docker-compose로 통합 관리됩니다. 상세 내용은 [phase8-3-1-docker-compose-integration-guide.md](./phase8-3-1-docker-compose-integration-guide.md) 참조

**이전 개별 실행 방식 (참고용):**

```bash
docker run -d \
  --name n8n \
  -p 5678:5678 \
  -v n8n_data:/home/node/.n8n \
  -v /Users/map-rch/WORKS/personal-ai-brain-v2:/workspace/project \
  n8nio/n8n
```

---

### 8-2-2 Gap 분석 워크플로우

- [ ] "Gap Analysis" 워크플로우 생성
- [ ] 이전 워크플로우 완료 시 트리거
- [ ] Read Binary Files (phases/\*_/_.md 기존 문서)
- [ ] Execute Command (Claude Code)
  ```bash
  claude "
  current-state.md와 기존 문서 비교
  gap-analysis.md 작성
  "
  ```
- [ ] PostgreSQL 노드 (gap_analysis_md 저장)
- [ ] 테스트 실행

**예상 시간:** 1.5시간  
**완료 기준:** gap-analysis.md 생성 확인

---

### 8-2-3 Plan 생성 워크플로우 (GPT)

- [ ] "Plan Generation" 워크플로우 생성
- [ ] HTTP Request 노드 (OpenAI API)
- [ ] Prompt 설계:

  ```
  Input:
  - current-state.md
  - gap-analysis.md
  - 기존 phase 문서들

  Task:
  현실적인 Phase-X Plan 작성
  기존 패턴 유지
  ```

- [ ] Write Binary File 노드 (phase-X-plan-v1.md)
- [ ] PostgreSQL 노드 (plans 테이블에 저장)
- [ ] 테스트: 실제 Plan 생성

**예상 시간:** 2시간  
**완료 기준:** Plan 문서 생성 및 읽기 가능

---

### 8-2-4 Discord 승인 루프

- [ ] Discord Webhook 노드 (Plan 전송)
- [ ] 메시지 포맷 설계:

  ```
  📋 Phase-X Plan v1

  [Plan 내용 요약]

  반응으로 응답해주세요:
  ✅ 승인
  ✏️ 수정 필요 (댓글로 피드백)
  ❌ 거절
  ```

- [ ] Wait 노드 (Discord Webhook Trigger 대기)
- [ ] Discord Trigger 워크플로우 생성
  - Message Reaction 감지
  - Message Reply 수집
- [ ] IF 노드 (반응별 분기)
  ```
  IF ✅ → 다음 단계
  IF ✏️ → GPT 수정 → 재전송
  IF ❌ → 중단
  ```
- [ ] Loop 구현 (최대 5회)
- [ ] PostgreSQL (approvals 테이블에 기록)
- [ ] 전체 루프 테스트

**예상 시간:** 4시간 (가장 복잡)  
**완료 기준:** 실제 승인 루프 작동 확인

---

### 8-2-5 Todo-List 생성

- [ ] "Todo Generation" 워크플로우
- [ ] HTTP Request (GPT API)
- [ ] Prompt: 확정된 Plan 기반 Todo-List 생성
- [ ] Discord 전송 (승인 루프 동일)
- [ ] PostgreSQL 저장
- [ ] 테스트

**예상 시간:** 1.5시간  
**완료 기준:** Todo-List 승인 프로세스 작동

---

### 8-2-6 Task Plan & Test Plan 생성

- [ ] "Task Plans Generation" 워크플로우
- [ ] Loop Over Items (Todo 항목별)
- [ ] HTTP Request (GPT API) - Task Plan 생성
- [ ] HTTP Request (GPT API) - Test Plan 생성
- [ ] Write Binary Files (task-N-plan.md, task-N-test.md)
- [ ] PostgreSQL (tasks 테이블)
- [ ] Discord 알림 (간단 승인)
- [ ] 테스트

**예상 시간:** 2시간  
**완료 기준:** Task별 문서 자동 생성

---

### 8-2-7 Task 실행 워크플로우 ✅

- [x] Backend API `POST /api/workflow/run-task` 구현
- [x] n8n 워크플로우: **HTTP_RunTaskExecution** (Execute Command 대신 Backend HTTP 호출)
- [x] DB_SelectPendingTask → JS_PrepareTaskPayload → HTTP_RunTaskExecution → JS_SetTaskStatusFromResponse → DB_UpdateTaskStatus
- [ ] (선택) DISCORD_SendTaskComplete, 8-2-8 트리거

**상세:** [phase8-2-7-task-execution-workflow.md](./phase8-2-7-task-execution-workflow.md)

**참고:** n8n 컨테이너에 Python/Claude CLI가 없어도 동작 (실행은 Backend에서 수행).

---

## 📋 Phase 8-3: Sub-workflow 2 구축 (1-2일) → **Phase 9로 이동**

### 8-3-1 개발 시작 알림

- [ ] "Development Start" 워크플로우
- [ ] Discord Webhook (Cursor 작업 알림)
- [ ] 메시지 포맷:

  ```
  💻 Task-1 개발 시작

  📄 Task Plan: [링크/요약]

  Cursor에서 작업 후 "/done task-1" 입력해주세요
  ```

- [ ] 테스트

**예상 시간:** 30분  
**완료 기준:** Discord 알림 수신

---

### 8-3-2 완료 감지

- [ ] Discord Trigger 워크플로우 수정
- [ ] Message Content 필터 (/done 명령어)
- [ ] Code 노드 (task 이름 추출)
- [ ] PostgreSQL (tasks 상태 업데이트)
- [ ] 다음 워크플로우 트리거
- [ ] 테스트 (/done 입력 → 자동 진행)

**예상 시간:** 1시간  
**완료 기준:** 명령어 감지 작동

---

### 8-3-3 (Optional) Cursor 자동화 시도

- [ ] Flask API 서버 구축
  ```python
  @app.route('/cursor/execute', methods=['POST'])
  def execute_task():
      task = request.json['task']
      # Cursor API 호출 (가능하다면)
      # 또는 파일 생성으로 알림
      return {'status': 'started'}
  ```
- [ ] n8n HTTP Request 노드
- [ ] 실험 및 검증
- [ ] 작동 안 하면 Skip

**예상 시간:** 2시간 (선택)  
**완료 기준:** 자동화 가능 여부 판단

---

## 📋 Phase 8-4: Sub-workflow 3 구축 (2일) → **Phase 9로 이동**

### 8-4-1 테스트 실행 (Claude Code)

- [ ] "Testing" 워크플로우 생성
- [ ] Execute Command (Claude Code)
  ```bash
  claude "
  1. 완성된 코드 읽기
  2. Test Plan 기반 테스트 실행
  3. 결과를 test-result.md에 작성
  "
  ```
- [ ] Read Binary Files (test-result.md)
- [ ] PostgreSQL (test_results 테이블)
- [ ] 테스트

**예상 시간:** 1.5시간  
**완료 기준:** 테스트 결과 수집

---

### 8-4-2 결과 보고서 생성 (GPT)

- [ ] HTTP Request (GPT API)
- [ ] Prompt: 테스트 결과 → 결과 보고서
- [ ] Write Binary File (task-N-result.md)
- [ ] Discord 전송 (참고용)
- [ ] 테스트

**예상 시간:** 1시간  
**완료 기준:** 보고서 문서 생성

---

### 8-4-3 종합 보고서

- [ ] "Summary Report" 워크플로우
- [ ] Loop Over Items (모든 Task 결과)
- [ ] HTTP Request (GPT API) - 종합 분석
- [ ] 완료/미완료/보완점 정리
- [ ] Write Binary File (phase-test-summary.md)
- [ ] Discord 전송
- [ ] 테스트

**예상 시간:** 1.5시간  
**완료 기준:** 종합 보고서 생성

---

## 📋 Phase 8-5: Sub-workflow 4 구축 (1일) → **Phase 9로 이동**

### 8-5-1 User 테스트 문서 수집

- [ ] Discord 메시지 전송 (User 테스트 요청)
- [ ] Discord Trigger (User 입력 대기)
- [ ] Message Content 저장
- [ ] Write Binary File (user-test.md)
- [ ] PostgreSQL 저장
- [ ] 테스트

**예상 시간:** 1시간  
**완료 기준:** User 입력 저장

---

### 8-5-2 최종 Phase 보고서

- [ ] "Final Report" 워크플로우
- [ ] Read Binary Files (AI 테스트 + User 테스트)
- [ ] HTTP Request (GPT API)
- [ ] Prompt:
  ```
  - Phase 결과 종합
  - 다음 Phase 제안
  ```
- [ ] Write Binary File (phase-X-final.md)
- [ ] Discord 전송
- [ ] 테스트

**예상 시간:** 1.5시간  
**완료 기준:** 최종 보고서 생성

---

### 8-5-3 Git 통합

- [ ] Execute Command 노드
  ```bash
  git add .
  git commit -m "Phase-X completed"
  git push
  ```
- [ ] Discord 완료 알림
- [ ] PostgreSQL (phase 상태 → completed)
- [ ] 테스트

**예상 시간:** 30분  
**완료 기준:** Git push 성공

---

## 📋 Phase 8-6: 통합 및 테스트 (2-3일)

### 8-6-1 Main Orchestrator 구축

- [ ] "Phase Orchestrator" 메인 워크플로우
- [ ] 모든 Sub-workflow 연결
- [ ] Error Handling 추가
- [ ] Retry 로직 구현
- [ ] 상태 모니터링

**예상 시간:** 3시간  
**완료 기준:** 전체 플로우 연결

---

### 8-6-2 End-to-End 테스트

- [ ] 실제 Phase-9 시작
- [ ] 1단계부터 8단계까지 전체 실행
- [ ] 각 단계별 결과 검증
- [ ] 에러 기록 및 수정
- [ ] 재테스트

**예상 시간:** 4시간  
**완료 기준:** Phase 1개 완전 자동 완료

---

### 8-6-3 최적화

- [ ] 토큰 사용량 분석
- [ ] 불필요한 API 호출 제거
- [ ] 응답 시간 측정
- [ ] 병렬 처리 가능 부분 개선
- [ ] PostgreSQL 인덱스 추가

**예상 시간:** 2시간  
**완료 기준:** 성능 개선 확인

---

### 8-6-4 문서화

- [ ] 각 워크플로우 설명 작성
- [ ] 트러블슈팅 가이드
- [ ] Discord 명령어 정리
- [ ] PostgreSQL 스키마 문서
- [ ] README 업데이트

**예상 시간:** 2시간  
**완료 기준:** 문서 완성

---

## 📊 전체 일정 요약

| Phase     | 작업 내용              | 예상 시간     | 우선순위 |
| --------- | ---------------------- | ------------- | -------- |
| Phase 0   | 환경 준비              | 2-3시간       | 🔴 필수  |
| Phase 8-2 | Plan & Tasks (1-3단계) | 13시간        | 🔴 필수  |
| Phase 8-3 | Development (4단계)    | 3.5시간       | 🟡 중요  |
| Phase 8-4 | Testing (5-6단계)      | 4시간         | 🟡 중요  |
| Phase 8-5 | Final Report (7-8단계) | 3시간         | 🟡 중요  |
| Phase 8-6 | 통합 및 테스트         | 11시간        | 🔴 필수  |
| **합계**  |                        | **36-40시간** |          |

**현실적 일정:** 1-2주 (하루 2-4시간 작업 기준)

---

## 💰 예상 비용

### 월간 운영 비용

- **Claude Pro**: $20/월 (분석/테스트)
- **OpenAI API**: $10-20/월 (문서 생성)
- **합계**: **$30-40/월**

### Phase당 비용

- Claude API: $2-3
- GPT API: $2-3
- **합계**: **$4-6/Phase**

---

## ✅ 완료 기준

### MVP (최소 기능)

- [ ] Phase 8-2 워크플로우 작동
- [ ] Discord 승인 루프 작동
- [ ] Plan 문서 자동 생성
- [ ] PostgreSQL 데이터 저장

### 완성 (전체 기능)

- [ ] 8단계 모두 자동화
- [ ] End-to-End 테스트 통과
- [ ] 실제 Phase 1개 완료
- [ ] 문서화 완료

---

## 🚀 다음 액션

**지금 시작할 것 (우선순위 순):**

1. **Discord 봇 생성** (30분)
   - 지금 당장 가능
   - 다른 작업의 기반

2. **PostgreSQL 스키마** ✅ (완료)
   - 데이터 구조 확정
   - 테이블 생성 완료
   - n8n 연결 테스트 (다음 단계)

3. **Phase 8-2-1 - 코드 분석** (2시간)
   - 첫 워크플로우
   - 성취감 빠름

4. **Phase 8-2-3 - Plan 생성** (2시간)
   - 핵심 기능
   - 가시적 결과

5. **Phase 8-2-4 - 승인 루프** (4시간)
   - 가장 복잡
   - 하지만 핵심

---

## 📝 진행 상황 트래킹

현재 완료:

- [x] 전체 계획 수립
- [x] n8n, Qdrant, PostgreSQL 세팅
- [x] Claude Code 설치 및 인증
- [x] **Phase 0.3: PostgreSQL 스키마 설계 및 테이블 생성 완료**
  - workflow_phases, workflow_plans, workflow_approvals, workflow_tasks, workflow_test_results 테이블 생성
  - 인덱스 및 외래키 관계 설정 완료
  - CRUD 테스트 완료
  - 상세 내용: [phase8-1-1-database-schema-n8n-setting.md](./phase8-1-1-database-schema-n8n-setting.md) 참조
- [ ] Phase 0.1: Discord 봇 설정 (다음 단계)
- [ ] Phase 0.2: API 키 준비

---

**다음 단계:**

1. n8n에서 PostgreSQL Credential 등록 및 연결 테스트
2. Discord 봇 설정 (Phase 0.1)
3. API 키 준비 (Phase 0.2)

**준비되셨나요? n8n PostgreSQL 연결부터 진행할까요?** 🚀
