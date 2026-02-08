Phase Auto Checker v1

기준 workflow: Phase Auto Checker v1 (n8n)

이 문서는 Phase Auto Checker v1 workflow가
• 어떤 파일들을 참조하고
• 어떤 순서로 실행되며
• 어떤 판단 기준으로 다음 Phase 문서를 생성하는지
를 설명하는 개발·유지보수용 설계 문서다.

⸻

1. Workflow 목적

이 workflow의 목적은 다음을 자동으로 수행하는 것이다. 1. 현재 Phase 디렉토리 상태를 파일 기준으로 검사 2. Phase 종료 조건 충족 여부 판단 3. 필요 시 Final Summary 생성 4. Final Summary를 근거로 다음 Phase Plan 자동 생성 5. 생성된 Plan 문서의 구조 검증

즉,

Phase의 상태를 코드가 아닌 문서로 판단하고,
문서 상태에 따라 다음 설계를 자동 생성하는 엔진

이다.

⸻

2. 참조 파일 구조

2.1 Phase 산출물 디렉토리

경로:

docs/phases/{phaseDirId}/

검사 대상 파일 패턴:
• {phaseFileBase}-plan.md
• {phaseFileBase}-todo-list.md
• {phaseFileBase}-user-test-results.md
• {phaseFileBase}-final-summary-report.md
• {phaseFileBase}(-N)?-_-change-report.md
• {phaseFileBase}(-N)?-_-test-report.md

이 파일들의 존재 여부 조합으로 Phase 상태를 판단한다.

⸻

2.2 규칙 / 판단 문서 (AI 헌법)

아래 문서들은 AI 판단과 생성의 기준으로 사용된다.

docs/ai/ai-rule-phase-naming.md
docs/ai/ai-rule-phase-auto-generation.md
docs/ai/ai-rule-decision.md
docs/prompts/phase-auto-create-prompt.md
docs/prompts/phase-plan-guide-prompt.md

역할:
• Phase 명명 규칙 정의
• Phase 증가 규칙 정의
• Plan 문서 구조 강제
• GPT 출력 통제

⸻

2.3 시스템 컨텍스트 문서

README.md

    •	전체 프로젝트 개요 제공
    •	참고용 (직접 판단 로직에는 영향 없음)

⸻

2.4 Workflow Node Nameing 규칙 문서

docs > n8n > rules > n8n node nameing Rules.md

    •	워크플로우 생성시 노드의 이름 생성 규칙을 정의
    • 노드 이름만 보고도 역할과 책임을 즉시 파악할 수 있을 것
    • 워크플로우를 사람이 보지 않아도 AI가 구조적으로 이해·생성·수정할 수 있을 것
    • Phase, 자동화, 로그, 오류 추적 시 일관된 기준점으로 작동할 것

노드 이름 기본 형식

<PREFIX>\_<Verb><Object>

⸻

3. 전체 실행 흐름

STEP 0. Manual Trigger
• 수동 실행 트리거
• 개발/테스트 단계용
• 향후 자동 감시 트리거로 대체 가능

⸻

STEP 1. Phase ID 설정

SET_PhaseId

예시:

phaseDirId : Testphase1-0
phaseFileBase: Testphase1-0-0

모든 파일 경로와 판단의 기준점이 된다.

⸻

STEP 2. Phase 파일 목록 수집

CMD_ListPhaseFiles
• 현재 Phase 디렉토리의 파일 목록을 조회
• Phase 산출물 현황 파악용

⸻

STEP 3. Phase 규칙 로딩

CMD_LoadPhaseRules
• ai-rule / decision / prompt 문서를 전부 로딩
• 규칙 존재 여부 및 GPT 입력용 텍스트로 사용

⸻

STEP 4. Phase 상태 판별 (핵심 로직)

JS_CheckPhaseArtifacts

생성되는 주요 판단 플래그:
• hasPlan
• hasTodo
• hasChecklist
• hasUserTestResults
• hasFinalSummary
• needFinalSummary
• hasTaskReports
• canCreatePlan
• hasRules

핵심 판단 규칙:

needFinalSummary =
hasUserTestResults && !hasFinalSummary

⸻

STEP 5. Final Summary 생성 여부 분기

IF_NeedFinalSummary

5-1. Final Summary가 필요한 경우
• GEN_CreateFinalSummary
• {phaseFileBase}-final-summary-report.md 생성
• Frontmatter 자동 삽입
• CMD_VerifyFinalSummary
• 생성 여부 검증

5-2. 이미 존재하는 경우
• 생성 스킵
• 기존 Final Summary 로딩 단계로 이동

⸻

STEP 6. Final Summary 로딩

CMD_LoadFinalSummary
• Phase 종료 근거 문서
• 다음 Phase Plan 생성의 핵심 입력

⸻

STEP 7. 다음 Phase ID 계산

JS_SetNextPhaseId

규칙 예시:

Testphase1-0 → Testphase1-1
Testphase1-0-0 → Testphase1-1-0

다음 Phase의 디렉토리와 파일 베이스를 계산한다.

⸻

STEP 8. Phase Plan Guide 로딩

CMD_LoadPhasePlanGuide
• phase-plan-guide-prompt.md 로드
• GPT 출력 구조를 100% 고정

⸻

STEP 9. GPT 기반 다음 Phase Plan 생성

GPT_CreatePlan

입력 구성:
• Phase Plan Guide
• Phase Rules
• Final Summary
• Next Phase Meta 정보

출력 규칙:
• Markdown 본문만 허용
• 지정된 섹션 구조 필수
• 설명/주석/코드블록 금지

⸻

STEP 10. Plan 파일 저장

CMD_WritePlanFile

결과 파일:

docs/phases/{nextPhaseDirId}/{nextPhaseFileBase}-plan.md

⸻

STEP 11. Plan 구조 검증

CMD_VerifyPlan

검증 항목:
• 파일 존재 여부
• 최소 크기 (200 bytes 이상)
• 필수 섹션 존재 여부

필수 섹션:
• Phase 목적
• Phase 배경
• 성공 기준 (Done Definition)
• Scope (포함 / 제외)
• 주요 전략
• 예상 리스크
• 다음 단계 연결
• 판단 근거

⸻

4. Workflow 성격 요약

이 workflow는 다음 철학을 가진다.
• 파일 시스템을 상태 머신으로 사용
• 문서 존재 여부가 Phase 상태를 결정
• AI는 판단자가 아닌 규칙 집행자
• 사람 개입 없이 다음 설계 초안까지 자동 생성

즉,

문서 = 상태
상태 = 다음 행동 트리거

라는 구조를 실험·검증하는 핵심 엔진이다.

⸻

5. 향후 리팩토링 분리 기준 (가이드)

권장 분리 단위: 1. Phase 상태 체크 workflow 2. Final Summary 생성 workflow 3. Next Phase Plan 생성 workflow 4. Approval / Notification workflow (Discord 등)

이 문서는 위 분리를 위한 기준 문서로 사용된다.
