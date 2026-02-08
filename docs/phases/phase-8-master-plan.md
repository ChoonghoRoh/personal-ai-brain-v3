# Personal AI Brain - Phase 8 실행 계획

**생성일**: 2026-01-28  
**기반 문서**: current-state.md, gap-analysis.md  
**계획 버전**: 2.0  
**업데이트**: 2026-02-01 - **Phase 8 전체 워크플로우 개발 보류**. 마무리 사유·유지 항목: [phase-8-wrap-up.md](./phase-8-wrap-up.md).

---

## ⏸ Phase 8 마무리 (워크플로우 개발 보류)

**2026-02-01**: Phase 8 전체 워크플로우 개발을 **보류**하고 본 프로젝트 내 Phase 8을 마무리합니다.

- **보류 사유**: 워크플로우 개발에 드는 시간 과다, rule·프롬프트·Claude Code 토큰·범위·디버깅 등 디테일 개발이 별도 프로젝트로 다루는 것이 적절함.
- **유지**: Phase 8-0·8-1·8-2에서 완료된 Backend API·n8n 환경·기존 워크플로우·문서는 그대로 유지·참고용 보존.
- **상세**: [phase-8-wrap-up.md](./phase-8-wrap-up.md)

---

## 📋 요약 (1페이지)

### Phase 8 목표

**n8n 워크플로우 도입을 통한 개발 프로세스 자동화**

Phase 8은 n8n을 활용하여 코드 분석, Gap 분석, Plan 생성, 승인 루프 등 개발 프로세스를 자동화하는 것을 목표로 합니다.

### 현재 상태

- ✅ 핵심 기능 90%+ 완료 (임베딩, 검색, AI 응답, 지식 구조화, Reasoning)
- ✅ Phase 8-1: 환경 준비 완료 (PostgreSQL 스키마, n8n 마이그레이션, Discord 봇 설정)
- ✅ Phase 8-2-1 완료: 현재 상태 분석
- ✅ Phase 8-2-2 완료: Gap 분석
- ✅ Phase 8-2-3 완료: Plan 생성
- ⏳ Phase 8-2-4 미진행: Discord 승인 루프 구축 (계획·검토 문서 완료, n8n 워크플로우 미구현)
- ⏳ Phase 8-2-5 미진행: Todo-List 생성 (8-2-4 의존, 워크플로우·GPT 연동 없음)
- 🔄 Phase 8-2-6 부분 완료: Task Plan & Test Plan 생성 (테스트용 n8n 워크플로우만 구현, Todo-List 연동·GPT 버전 미구현)
- ✅ Phase 8-2-7 완료: Task 실행 (Backend `POST /api/workflow/run-task` + n8n HTTP_RunTaskExecution, workflow_tasks·plan_md_path 경로 기반 실행)
- ⏳ Phase 8-2-8 미구현: Task 테스트 및 결과 저장 워크플로우

### Phase 8 범위

**포함:**

- Phase 8-1: 환경 준비 (PostgreSQL, n8n, Discord)
- Phase 8-2: n8n 워크플로우 구축 (코드 분석, Gap 분석, Plan 생성, 승인 루프)

**제외 (Phase 9로 이동):**

- Phase 8-3: 백업/복원 UI 구축 → **Phase 9로 이동**
- Phase 8-4: HWP 파일 지원 → **Phase 9로 이동**
- Phase 8-5: 통계 및 분석 대시보드 → **Phase 9로 이동**

### 계획 개요

이 계획은 **n8n 워크플로우 구축에 집중**합니다. Phase 8-2의 모든 단계를 완료하여 자동화된 개발 프로세스를 구축하고, UI 개선 작업은 Phase 9에서 n8n 워크플로우로 자동화하여 진행합니다.

### 예상 일정

- **Phase 8 워크플로우 개발**: **보류** (별도 프로젝트 권장). [phase-8-wrap-up.md](./phase-8-wrap-up.md)

---

## 📝 단계별 작업 계획

### Phase 8-2-3: Plan 생성 ✅

**상태**: 완료

**작업 내용:**

- ✅ gap-analysis.md 기반 실행 계획 작성
- ✅ phase-8-plan.md 생성
- ✅ PostgreSQL에 저장

**완료 조건:**

- phase-8-plan.md 파일 생성
- workflow_plans 테이블에 저장 완료

---

### Phase 8-2-4: Discord 승인 루프 구축

**우선순위**: High  
**예상 소요 시간**: 2-3일  
**의존성**: Phase 8-2-3 완료

#### 작업 목록

**1. Discord 봇 워크플로우 설계**

- [ ] 승인 요청 메시지 형식 정의
- [ ] 승인/거절 버튼 인터페이스 설계
- [ ] 승인 상태 추적 로직 설계
- **예상 시간**: 0.5일

**2. n8n Discord 워크플로우 구축**

- [ ] Discord Webhook 노드 설정
- [ ] 승인 요청 메시지 전송 워크플로우
- [ ] 승인/거절 응답 수신 워크플로우
- [ ] PostgreSQL 업데이트 연동
- **예상 시간**: 1일

**3. PostgreSQL 승인 상태 관리**

- [ ] workflow_approvals 테이블 활용
- [ ] 승인 상태 업데이트 API
- [ ] 승인 이력 조회 API
- **예상 시간**: 0.5일

**4. 테스트 및 검증**

- [ ] Discord 봇 메시지 전송 테스트
- [ ] 승인/거절 플로우 테스트
- [ ] DB 상태 동기화 확인
- **예상 시간**: 0.5일

**5. 문서화**

- [ ] Discord 승인 루프 가이드 작성
- [ ] 워크플로우 사용 매뉴얼
- **예상 시간**: 0.5일

#### 리스크 및 대응 방안

**리스크 1**: Discord API 제한

- **대응**: Rate limiting 고려, 큐 시스템 도입

**리스크 2**: 승인 상태 동기화 실패

- **대응**: 재시도 로직, 수동 동기화 스크립트

**리스크 3**: Discord 봇 권한 문제

- **대응**: 봇 권한 사전 확인, 테스트 환경 구축

---

### Phase 8-2-5: Todo-List 생성

**우선순위**: High  
**예상 소요 시간**: 1.5시간  
**의존성**: Phase 8-2-4 완료 (Plan 승인 완료 후)

#### 작업 목록

**1. "Todo Generation" 워크플로우 생성**

- [ ] 워크플로우 생성 및 기본 설정
- **예상 시간**: 0.25시간

**2. HTTP Request 노드 (GPT API)**

- [ ] 승인된 Plan 기반 Todo-List 생성 프롬프트 설계
- [ ] GPT API 호출 설정
- [ ] 응답 파싱 및 검증
- **예상 시간**: 0.5시간

**3. Write Binary File 노드**

- [ ] todo-list.md 파일 생성
- [ ] 파일 경로 및 형식 설정
- **예상 시간**: 0.25시간

**4. Discord 전송 (승인 루프)**

- [ ] Phase 8-2-4 승인 루프 재사용
- [ ] Todo-List 내용으로 메시지 변경
- **예상 시간**: 0.25시간

**5. PostgreSQL 저장**

- [ ] 승인 후 todo-list 저장
- [ ] 테스트
- **예상 시간**: 0.25시간

#### 완료 기준

- [ ] 승인된 Plan 기반 Todo-List 생성 가능
- [ ] Discord 승인 프로세스 작동
- [ ] PostgreSQL 저장 완료

---

### Phase 8-2-6: Task Plan & Test Plan 생성 🔄

**상태**: 부분 완료 (테스트용 n8n 워크플로우만 구현, Todo-List 연동·GPT 버전 미구현)  
**우선순위**: High  
**예상 소요 시간**: 2시간 (남은 작업)  
**의존성**: Phase 8-2-5 완료 (Todo-List 승인 완료 후)

#### 작업 목록

**1. "Task Plans Generation" 워크플로우 생성**

- [x] 워크플로우 생성 및 기본 설정 (Task Plan and Test Plan Generation v1 (test))
- **예상 시간**: 0.25시간

**2. Loop Over Items 노드**

- [x] Todo 항목별 반복 로직 구현 (테스트용)
- [ ] Todo-List 연동 (승인된 todo-list.md 기반)
- **예상 시간**: 0.25시간

**3. HTTP Request 노드 (Task Plan 생성)**

- [x] GPT API로 Task Plan 생성 (테스트용)
- [x] 프롬프트 설계 (작업 목표, 단계, 리소스, 시간, 의존성, 완료 기준)
- **예상 시간**: 0.5시간

**4. HTTP Request 노드 (Test Plan 생성)**

- [x] GPT API로 Test Plan 생성 (테스트용)
- [x] 프롬프트 설계 (테스트 시나리오, 케이스, 예상 결과, 환경, 완료 기준)
- **예상 시간**: 0.5시간

**5. Write Binary Files 노드**

- [x] task-N-plan.md 파일 생성 (plan_md_path, test_plan_md_path 출력)
- [x] task-N-test.md 파일 생성
- **예상 시간**: 0.25시간

**6. PostgreSQL 노드 (workflow_tasks 테이블)**

- [x] Task 정보 저장 (plan_md_path 포함 INSERT)
- [x] Plan 및 Test Plan 경로 저장
- **예상 시간**: 0.25시간

**7. Discord 알림**

- [ ] 간단한 알림 메시지 전송
- [ ] 승인 루프 생략 가능
- **예상 시간**: 0.25시간

#### 완료 기준

- [x] Todo 항목별 Task Plan 생성 가능 (테스트용)
- [x] Todo 항목별 Test Plan 생성 가능 (테스트용)
- [x] 파일 자동 저장 및 PostgreSQL 저장 (테스트용)
- [ ] Todo-List 승인 후 연동·운영용 워크플로우 전환

---

## 📋 Phase 8-2-7: Task 실행 워크플로우 (Backend API + n8n HTTP) ✅

**우선순위**: High  
**예상 소요 시간**: 2–3일 (구현 완료)  
**의존성**: Phase 8-2-6 완료

**목표**: todo-list로 정의된 Task .md(task-N-plan.md)를 **실제로 수행**할 수 있는 자동화. n8n은 **Execute Command 대신 Backend HTTP 호출**로 실행 (n8n 컨테이너에 Python 불필요). **plan_md_path** 경로 기반 실행 지원.

#### 작업 목록

- [x] Backend `POST /api/workflow/run-task` 구현 (workflow_task_service: Claude API로 Task Plan 수행, plan_md_path 지원)
- [x] n8n **HTTP_RunTaskExecution** 노드로 Backend 호출 (Execute Command 미사용)
- [x] 실행 후 `workflow_tasks.status` 갱신 (JS_SetTaskStatusFromResponse → DB_UpdateTaskStatus)
- [ ] (선택) Discord 알림
- **문서**: `phase8-2-7-task-execution-workflow.md`

#### 완료 기준

- [x] Task Plan 1건을 Backend(Claude)로 실제 수행 가능
- [x] n8n으로 실행 트리거 및 DB 상태 반영

---

## 📋 Phase 8-2-8: Task 테스트 및 결과 저장 워크플로우

**우선순위**: High  
**예상 소요 시간**: 1.5–2일  
**의존성**: Phase 8-2-7 완료

**목표**: 8-2-7 완료 Task에 대해 결과물 테스트 실행 및 결과 저장(workflow_test_results, task-N-result.md).

#### 작업 목록

- [ ] `scripts/n8n/run_task_test.py` 구현 (예정) (Test Plan 기준 테스트 → 결과 수집)
- [ ] workflow_test_results INSERT
- [ ] (선택) task-N-result.md 생성, Discord 알림
- [ ] n8n에서 8-2-7 완료 후 본 워크플로우 트리거
- **문서**: `phase8-2-8-task-test-and-store-workflow.md`

#### 완료 기준

- [ ] 8-2-7 완료 Task 1건에 대해 테스트 실행 및 DB 저장 확인

---

## 📋 Phase 8-3: 개발 시작 및 완료 감지 워크플로우

**우선순위**: Medium  
**예상 소요 시간**: 1.5-3.5시간 (8-3-3 선택 시)  
**의존성**: Phase 8-2-8 완료 (Task 실행·테스트 저장 완료 후)

### 8-3-1: 개발 시작 알림

**예상 시간**: 30분

#### 작업 목록

- [ ] "Development Start" 워크플로우 생성
- [ ] Discord Webhook 노드 설정 (Cursor 작업 알림)
- [ ] 메시지 포맷 설계:

  ```
  💻 Task-1 개발 시작

  📄 Task Plan: [링크/요약]

  Cursor에서 작업 후 "/done task-1" 입력해주세요
  ```

- [ ] 테스트

#### 완료 기준

- [ ] Discord 알림 수신 확인

---

### 8-3-2: 완료 감지

**예상 시간**: 1시간

#### 작업 목록

- [ ] Discord Trigger 워크플로우 수정
- [ ] Message Content 필터 (/done 명령어)
- [ ] Code 노드 (task 이름 추출)
- [ ] PostgreSQL (tasks 상태 업데이트: pending → in_progress → completed)
- [ ] 다음 워크플로우 트리거
- [ ] 테스트 (/done 입력 → 자동 진행)

#### 완료 기준

- [ ] 명령어 감지 작동 확인
- [ ] Task 상태 자동 업데이트 확인

---

### 8-3-3: (Optional) Cursor 자동화 시도

**예상 시간**: 2시간 (선택)

#### 작업 목록

- [ ] Flask API 서버 구축 (또는 기존 FastAPI 활용)
- [ ] `/cursor/execute` 엔드포인트 생성
- [ ] n8n HTTP Request 노드 설정
- [ ] 실험 및 검증
- [ ] 작동 안 하면 Skip

#### 완료 기준

- [ ] 자동화 가능 여부 판단

---

## 📋 Phase 8-4: 테스트 실행 및 보고서 생성 워크플로우

**우선순위**: Medium  
**예상 소요 시간**: 4시간  
**의존성**: Phase 8-3 완료 (Task 완료 후)

### 8-4-1: 테스트 실행 (Claude Code)

**예상 시간**: 1.5시간

#### 작업 목록

- [ ] "Testing" 워크플로우 생성
- [ ] Execute Command 노드 (Claude Code CLI)
  ```bash
  claude "
  1. 완성된 코드 읽기
  2. Test Plan 기반 테스트 실행
  3. 결과를 test-result.md에 작성
  "
  ```
- [ ] Read Binary Files 노드 (test-result.md 읽기)
- [ ] PostgreSQL 노드 (test_results 테이블에 저장)
- [ ] 테스트

#### 완료 기준

- [ ] 테스트 결과 수집 확인

---

### 8-4-2: 결과 보고서 생성 (GPT)

**예상 시간**: 1시간

#### 작업 목록

- [ ] HTTP Request 노드 (GPT API)
- [ ] 프롬프트: 테스트 결과 → 결과 보고서
- [ ] Write Binary File 노드 (task-N-result.md)
- [ ] Discord 전송 (참고용)
- [ ] 테스트

#### 완료 기준

- [ ] 보고서 문서 생성 확인

---

### 8-4-3: 종합 보고서

**예상 시간**: 1.5시간

#### 작업 목록

- [ ] "Summary Report" 워크플로우 생성
- [ ] Loop Over Items 노드 (모든 Task 결과)
- [ ] HTTP Request 노드 (GPT API - 종합 분석)
- [ ] 완료/미완료/보완점 정리
- [ ] Write Binary File 노드 (phase-test-summary.md)
- [ ] Discord 전송
- [ ] 테스트

#### 완료 기준

- [ ] 종합 보고서 생성 확인

---

## 📋 Phase 8-5: User 테스트 및 최종 보고서 워크플로우

**우선순위**: Medium  
**예상 소요 시간**: 3시간  
**의존성**: Phase 8-4 완료

### 8-5-1: User 테스트 문서 수집

**예상 시간**: 1시간

#### 작업 목록

- [ ] Discord 메시지 전송 (User 테스트 요청)
- [ ] Discord Trigger (User 입력 대기)
- [ ] Message Content 저장
- [ ] Write Binary File 노드 (user-test.md)
- [ ] PostgreSQL 저장
- [ ] 테스트

#### 완료 기준

- [ ] User 입력 저장 확인

---

### 8-5-2: 최종 Phase 보고서

**예상 시간**: 1.5시간

#### 작업 목록

- [ ] "Final Report" 워크플로우 생성
- [ ] Read Binary Files 노드 (AI 테스트 + User 테스트)
- [ ] HTTP Request 노드 (GPT API)
- [ ] 프롬프트:
  ```
  - Phase 결과 종합
  - 다음 Phase 제안
  ```
- [ ] Write Binary File 노드 (phase-X-final.md)
- [ ] Discord 전송
- [ ] 테스트

#### 완료 기준

- [ ] 최종 보고서 생성 확인

---

### 8-5-3: Git 통합

**예상 시간**: 30분

#### 작업 목록

- [ ] Execute Command 노드
  ```bash
  git add .
  git commit -m "Phase-X completed"
  git push
  ```
- [ ] Discord 완료 알림
- [ ] PostgreSQL (phase 상태 → completed)
- [ ] 테스트

#### 완료 기준

- [ ] Git push 성공 확인

---

## 📋 Phase 8-6: 통합 및 테스트

**우선순위**: High  
**예상 소요 시간**: 9시간 (2-3일)  
**의존성**: Phase 8-2 ~ 8-5 완료

### 8-6-1: Main Orchestrator 구축

**예상 시간**: 3시간

#### 작업 목록

- [ ] "Phase Orchestrator" 메인 워크플로우 생성
- [ ] 모든 Sub-workflow 연결
- [ ] Error Handling 추가
- [ ] Retry 로직 구현
- [ ] 상태 모니터링

#### 완료 기준

- [ ] 전체 플로우 연결 확인

---

### 8-6-2: End-to-End 테스트

**예상 시간**: 4시간

#### 작업 목록

- [ ] 실제 Phase-9 시작
- [ ] 1단계부터 8단계까지 전체 실행
- [ ] 각 단계별 결과 검증
- [ ] 에러 기록 및 수정
- [ ] 재테스트

#### 완료 기준

- [ ] Phase 1개 완전 자동 완료 확인

---

### 8-6-3: 최적화

**예상 시간**: 2시간

#### 작업 목록

- [ ] 토큰 사용량 분석
- [ ] 불필요한 API 호출 제거
- [ ] 응답 시간 측정
- [ ] 병렬 처리 가능 부분 개선
- [ ] PostgreSQL 인덱스 추가

#### 완료 기준

- [ ] 성능 개선 확인

---

## 📊 우선순위 및 의존성

### Phase 8 우선순위 매트릭스

| Phase | 우선순위 | 긴급도 | 영향도 | 예상 소요 시간 | 상태         |
| ----- | -------- | ------ | ------ | -------------- | ------------ |
| 8-1   | High     | 높음   | 높음   | 1-2일          | ✅ 완료      |
| 8-2-1 | High     | 높음   | 높음   | 0.5일          | ✅ 완료      |
| 8-2-2 | High     | 높음   | 높음   | 0.5일          | ✅ 완료      |
| 8-2-3 | High     | 높음   | 높음   | 0.5일          | ✅ 완료      |
| 8-2-4 | High     | 높음   | 높음   | 2-3일          | ⏳ 미진행    |
| 8-2-5 | High     | 높음   | 높음   | 1.5시간        | ⏳ 대기      |
| 8-2-6 | High     | 높음   | 높음   | 2시간 (남은)   | 🔄 부분 완료 |
| 8-2-7 | High     | 높음   | 높음   | 2–3일          | ✅ 완료      |
| 8-2-8 | High     | 높음   | 높음   | 1.5–2일        | ⏳ 미구현    |
| 8-3   | Medium   | 중간   | 중간   | 1.5-3.5시간    | ⏳ 대기      |
| 8-4   | Medium   | 중간   | 중간   | 4시간          | ⏳ 대기      |
| 8-5   | Medium   | 중간   | 중간   | 3시간          | ⏳ 대기      |
| 8-6   | High     | 높음   | 높음   | 9시간 (2-3일)  | ⏳ 대기      |

### Phase 8 의존성 그래프

```
Phase 8-1 (환경 준비) ✅
    ↓
Phase 8-2-1 (현재 상태 분석) ✅
    ↓
Phase 8-2-2 (Gap 분석) ✅
    ↓
Phase 8-2-3 (Plan 생성) ✅
    ↓
Phase 8-2-4 (Discord 승인 루프) [High] ⏳
    ↓
Phase 8-2-5 (Todo-List 생성) [High] ⏳
    ↓
Phase 8-2-6 (Task Plan & Test Plan 생성) [High] 🔄 부분 완료
    ↓
Phase 8-2-7 (Task 실행 워크플로우) [High] ✅
    ↓
Phase 8-2-8 (Task 테스트 및 결과 저장) [High] ⏳
    ↓
Phase 8-3 (개발 시작 및 완료 감지) [Medium] ⏳
    ↓
Phase 8-4 (테스트 실행 및 보고서) [Medium] ⏳
    ↓
Phase 8-5 (User 테스트 및 최종 보고서) [Medium] ⏳
    ↓
Phase 8-6 (통합 및 테스트) [High] ⏳
```

### Phase 8 실행 순서

1. ✅ **완료**: Phase 8-1 (환경 준비)
2. ✅ **완료**: Phase 8-2-1 (현재 상태 분석)
3. ✅ **완료**: Phase 8-2-2 (Gap 분석)
4. ✅ **완료**: Phase 8-2-3 (Plan 생성)
5. ⏳ **미진행**: Phase 8-2-4 (Discord 승인 루프)
6. ⏳ **대기**: Phase 8-2-5 (Todo-List 생성)
7. 🔄 **부분 완료**: Phase 8-2-6 (Task Plan & Test Plan 생성)
8. ✅ **완료**: Phase 8-2-7 (Task 실행 워크플로우)
9. ⏳ **미구현**: Phase 8-2-8 (Task 테스트 및 결과 저장)
10. ⏳ **대기**: Phase 8-3 (개발 시작 및 완료 감지)
11. ⏳ **대기**: Phase 8-4 (테스트 실행 및 보고서)
12. ⏳ **대기**: Phase 8-5 (User 테스트 및 최종 보고서)
13. ⏳ **대기**: Phase 8-6 (통합 및 테스트)

---

## 📅 Phase 8 예상 일정

### Week 1 (현재 주)

- ✅ Phase 8-1: 환경 준비 (완료)
- ✅ Phase 8-2-1: 현재 상태 분석 (완료)
- ✅ Phase 8-2-2: Gap 분석 (완료)
- ✅ Phase 8-2-3: Plan 생성 (완료)

### Week 2

- ⏳ Phase 8-2-4: Discord 승인 루프 (미진행, 2-3일)
- ⏳ Phase 8-2-5: Todo-List 생성 (1.5시간)
- 🔄 Phase 8-2-6: Task Plan & Test Plan (부분 완료, Todo 연동 남음)
- ✅ Phase 8-2-7: Task 실행 워크플로우 (완료)
- ⏳ Phase 8-2-8: Task 테스트 및 결과 저장 (1.5–2일)

### Week 3

- ⏳ Phase 8-3: 개발 시작 및 완료 감지 (1.5-3.5시간)
- ⏳ Phase 8-4: 테스트 실행 및 보고서 (4시간)
- ⏳ Phase 8-5: User 테스트 및 최종 보고서 (3시간)

### Week 4

- ⏳ Phase 8-6: 통합 및 테스트 (9시간, 2-3일)
- ✅ Phase 8 전체 완료 예정

---

## 🎯 Phase 8 성공 기준

### Phase 8 전체 성공 기준

- [x] Phase 8-1: 환경 준비 완료 (PostgreSQL, n8n, Discord)
- [x] Phase 8-2-1: 현재 상태 분석 완료
- [x] Phase 8-2-2: Gap 분석 완료
- [x] Phase 8-2-3: Plan 생성 완료
- [ ] Phase 8-2-4: Discord 승인 루프 구축 완료
  - [ ] Discord를 통해 승인 요청 전송 가능
  - [ ] 승인/거절 반응으로 응답 가능
  - [ ] 승인 상태가 PostgreSQL에 자동 저장
  - [ ] 승인 이력 조회 가능
  - [ ] 수정 요청 시 루프 작동 (최대 5회)
- [ ] Phase 8-2-5: Todo-List 생성 완료
  - [ ] 승인된 Plan 기반 Todo-List 생성
  - [ ] Discord 승인 프로세스 작동
  - [ ] PostgreSQL 저장 완료
- [ ] Phase 8-2-6: Task Plan & Test Plan 생성 완료 (🔄 부분 완료)
  - [x] Todo 항목별 Task Plan 생성 (테스트용)
  - [x] Todo 항목별 Test Plan 생성 (테스트용)
  - [x] 파일 자동 저장 및 PostgreSQL 저장 (테스트용, plan_md_path)
  - [ ] Todo-List 승인 후 연동·운영용 워크플로우
- [x] Phase 8-2-7: Task 실행 워크플로우 완료
  - [x] Backend `POST /api/workflow/run-task` 구현 (workflow_task_service + Claude API)
  - [x] n8n HTTP_RunTaskExecution 연동 (Execute Command 대신 HTTP 호출), workflow_tasks.status 갱신
- [ ] Phase 8-2-8: Task 테스트 및 결과 저장 완료
  - [ ] run_task_test.py 구현, workflow_test_results 저장
  - [ ] 8-2-7 완료 후 테스트 워크플로우 트리거
- [ ] Phase 8-3: 개발 시작 및 완료 감지 완료
  - [ ] 개발 시작 알림 전송
  - [ ] /done 명령어 감지 및 상태 업데이트
- [ ] Phase 8-4: 테스트 실행 및 보고서 완료
  - [ ] Claude Code로 테스트 실행
  - [ ] 결과 보고서 생성
  - [ ] 종합 보고서 생성
- [ ] Phase 8-5: User 테스트 및 최종 보고서 완료
  - [ ] User 테스트 문서 수집
  - [ ] 최종 Phase 보고서 생성
  - [ ] Git 통합 완료
- [ ] Phase 8-6: 통합 및 테스트 완료
  - [ ] Main Orchestrator 구축
  - [ ] End-to-End 테스트 통과
  - [ ] 최적화 완료

### Phase 8 완료 조건

- ✅ n8n 워크플로우로 코드 분석 자동화
- ✅ n8n 워크플로우로 Gap 분석 자동화
- ✅ n8n 워크플로우로 Plan 생성 자동화
- [ ] n8n 워크플로우로 승인 루프 자동화
- [x] Task .md 실행 자동화 (8-2-7)
- [ ] Task 테스트 및 결과 저장 자동화 (8-2-8)
- [ ] n8n 워크플로우로 Todo-List 생성 자동화
- [ ] n8n 워크플로우로 Task Plan & Test Plan 생성 자동화 (8-2-6: 테스트용 완료, Todo 연동 남음)
- [ ] n8n 워크플로우로 개발 프로세스 자동화 (시작 알림, 완료 감지)
- [ ] n8n 워크플로우로 테스트 실행 및 보고서 생성 자동화
- [ ] n8n 워크플로우로 User 테스트 및 최종 보고서 자동화
- [ ] 전체 워크플로우 통합 및 자동화 완료

---

## 📝 리스크 및 대응 방안 요약

### 공통 리스크

**리스크 1**: 시간 부족

- **대응**: 우선순위에 따라 선택적 진행, 필수 기능 우선

**리스크 2**: 기술적 난이도

- **대응**: 단계별 접근, 검증된 라이브러리 활용

**리스크 3**: 의존성 문제

- **대응**: 독립적으로 실행 가능한 작업 우선, 의존성 최소화

---

## 🔄 다음 단계

### Phase 8 내 다음 단계

1. **즉시**: Phase 8-2-4 시작 (Discord 승인 루프 구축)
   - 예상 소요 시간: 2-3일
   - 8-2-5 Todo-List·8-2-6 운영 연동의 선행 조건
2. **이후**: Phase 8-2-5 → 8-2-6 Todo 연동 → 8-2-8 (Task 테스트 및 결과 저장)

### Phase 9 계획 (향후)

Phase 8-3, 8-4, 8-5는 **Phase 9에서 n8n 워크플로우로 자동화**하여 진행합니다:

- **Phase 9-1: 백업/복원 UI 구축** (n8n 워크플로우)
  - 백업 실행 워크플로우
  - 복원 실행 워크플로우
  - 백업 검증 워크플로우
  - 웹 UI 연동

- **Phase 9-2: HWP 파일 지원** (n8n 워크플로우)
  - HWP 파싱 워크플로우
  - 자동 변환 및 임베딩 워크플로우

- **Phase 9-3: 통계 및 분석 대시보드** (n8n 워크플로우)
  - 통계 수집 워크플로우
  - 리포트 생성 워크플로우
  - 대시보드 업데이트 워크플로우

---

## 📝 Phase 8 요약

### 완료된 작업

- ✅ Phase 8-1: 환경 준비 (PostgreSQL 스키마, n8n 마이그레이션, Discord 봇)
- ✅ Phase 8-2-1: 현재 상태 분석 (current-state.md 생성)
- ✅ Phase 8-2-2: Gap 분석 (gap-analysis.md 생성)
- ✅ Phase 8-2-3: Plan 생성 (phase-8-plan.md 생성)
- ✅ Phase 8-2-7: Task 실행 (Backend `POST /api/workflow/run-task` + n8n HTTP_RunTaskExecution, plan_md_path 기반)

### 부분 완료

- 🔄 Phase 8-2-6: Task Plan & Test Plan 생성 (테스트용 n8n 워크플로우 구현, Todo-List 연동·운영용 미구현)

### 진행 예정 / 남은 작업

- ⏳ Phase 8-2-4: Discord 승인 루프 구축 (2-3일)
- ⏳ Phase 8-2-5: Todo-List 생성 (1.5시간)
- ⏳ Phase 8-2-8: Task 테스트 및 결과 저장 (1.5–2일)
- ⏳ Phase 8-3: 개발 시작 및 완료 감지 (1.5-3.5시간)
- ⏳ Phase 8-4: 테스트 실행 및 보고서 (4시간)
- ⏳ Phase 8-5: User 테스트 및 최종 보고서 (3시간)
- ⏳ Phase 8-6: 통합 및 테스트 (9시간, 2-3일)

### Phase 8 목표 달성도

- **진행률**: 약 45% (5단계 완료 + 1단계 부분 완료 / 11단계)
- **예상 완료일**: Week 4 내
- **총 예상 소요 시간**: 약 30시간 (1주일)

---

**문서 버전**: 3.0  
**최종 업데이트**: 2026-01-28  
**업데이트 내용**:

- Phase 8 목표를 n8n 워크플로우 구축에 집중
- Phase 8-2-5, 8-2-6 계획 추가
- Phase 8-3 ~ 8-6 워크플로우 계획 추가 (phase8-1-0-plan.md 기반)
- UI 개선 작업(백업/복원, HWP, 통계 대시보드)은 Phase 9로 이동
- Task 관련 현행화: 8-2-6 부분 완료, 8-2-7 완료 반영 (우선순위·의존성·완료 조건·요약·진행률)  
  **다음 검토 예정일**: Phase 8-2-4 완료 후

---

## 📚 관련 문서

### Phase 8-1

- `phase8-1-0-plan.md` - n8n 워크플로우 개발 계획 (원본)
- `phase8-1-1-database-schema-n8n-setting.md` - PostgreSQL 스키마 설정
- `phase8-1-2-n8n-postgresql-migration.md` - n8n PostgreSQL 마이그레이션

### Phase 8-2-1 ~ 8-2-3 (작업 요약)

- `phase8-2-1-current-state-analysis.md` - 현재 상태 분석 작업 요약
- `phase8-2-2-gap-analysis.md` - Gap 분석 작업 요약
- `phase8-2-3-plan-generation.md` - Plan 생성 작업 요약
- `phase8-2-1-code-analysis-workflow-guide.md` - 코드 분석 워크플로우 가이드

### Phase 8-2-4 ~ 8-2-6 (워크플로우 계획)

- `phase8-2-4-discord-approval-loop.md` - Discord 승인 루프 워크플로우 계획
- `phase8-2-5-todo-list-generation.md` - Todo-List 생성 워크플로우 계획
- `phase8-2-6-task-test-plan-generation.md` - Task Plan & Test Plan 생성 워크플로우 계획
- `phase8-2-7-task-execution-workflow.md` - Task .md 실행 워크플로우 (Claude-Code 자동화)
- `phase8-2-8-task-test-and-store-workflow.md` - Task 테스트 및 결과 저장 워크플로우 플랜
- `phase8-2-4-discord-approval-review.md` - Discord 승인 루프 검토 문서
