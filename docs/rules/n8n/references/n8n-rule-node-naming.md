n8n 노드 명명 규칙 (Node Naming Rules)

목적

이 문서는 n8n 워크플로우에서 사용하는 노드 이름의 표준 규칙을 정의한다.

목표는 다음과 같다:
• 노드 이름만 보고도 역할과 책임을 즉시 파악할 수 있을 것
• 워크플로우를 사람이 보지 않아도 AI가 구조적으로 이해·생성·수정할 수 있을 것
• Phase, 자동화, 로그, 오류 추적 시 일관된 기준점으로 작동할 것

⸻

기본 원칙 1. 노드 이름은 기능 단위로만 작성한다
• Phase, Step, 순서 정보는 포함하지 않는다
• 맥락은 워크플로우 이름과 변수로 관리한다 2. 모든 노드는 Prefix 기반으로 역할을 명확히 한다
• 노드 타입이 이름 첫 글자에서 바로 드러나야 한다 3. 동사 + 대상(Object) 구조를 유지한다
• 무엇을 하는 노드인지 한 문장으로 해석 가능해야 한다

⸻

노드 이름 기본 형식

<PREFIX>\_<Verb><Object>

예시:
• JS_SetNextPhaseId
• GPT_CreatePlan
• CMD_WritePlanFile

⸻

Prefix 규칙 (노드 타입별)

Prefix 대상 노드 유형 설명
JS* Code (JavaScript) 데이터 가공, 계산, 파싱 로직
GPT* LLM 호출 GPT / Claude 등 AI 응답 생성
CMD* Execute Command 쉘, CLI, 스크립트 실행
DB* Database PostgreSQL 등 DB 읽기/쓰기
IF* If 조건 분기 판단
LOOP* Loop / Split 반복 처리
FILE* Binary File 파일 읽기/쓰기
DISCORD* Discord Discord 메시지 / 승인 / 알림
SET* Set 변수 설정
HTTP* HTTP Request 외부 API 호출
TEST* 테스트용 테스트·실험 노드
TEMP* 임시용 임시 처리, 추후 제거 대상

⸻

동사(Verb) 사용 규칙

동사는 행동 중심으로 통일한다.

권장 동사
• Create : 생성
• Set : 값 설정
• Parse : 파싱
• Check : 조건 확인
• Validate : 검증
• Generate : 생성 (AI 결과)
• Insert : DB 삽입
• Update : DB 갱신
• Read : 읽기
• Write : 쓰기
• Send : 전송
• Receive : 수신

예시
• DB_InsertWorkflowPlan
• FILE_ReadPlanFile
• DISCORD_SendApprovalRequest

⸻

Object(대상) 명명 규칙
• 단수형 사용
• 워크플로우 전반에서 동일한 개념은 동일한 Object 명칭 사용

예시
• PhaseId
• Plan
• TodoList
• TaskPlan
• TestPlan
• ApprovalResult

⸻

금지 규칙 (절대 사용하지 않음)

❌ Phase / Step / 순서 번호 포함
• Phase8_CreatePlan_JS
• Step3_WriteFile

❌ 추상적이거나 의미 없는 이름
• ProcessData
• HandleThis

❌ 한 노드에 여러 책임 포함
• JS_ParseAndSaveAndNotify

⸻

네이밍 일관성 예시

GPT 노드 패턴

GPT_CreatePlan
GPT_CreateTodoList
GPT_CreateTaskPlan
GPT_CreateTestPlan

CMD 노드 패턴

CMD_WritePlanFile
CMD_WriteTodoFile
CMD_WriteTaskFile

DB 노드 패턴

DB_InsertWorkflowPlan
DB_UpdateApprovalStatus
DB_SelectPendingTasks

⸻

테스트 / 임시 노드 규칙
• 실험용 노드는 반드시 Prefix로 구분
• 최종 워크플로우에서는 제거 또는 교체 대상

예시:
• TEST_DiscordWebhook
• TEMP_ParsePlanResult

⸻

이 규칙의 철학

이 명명 규칙은 단순한 스타일 가이드가 아니다.
• 사람이 읽기 위한 규칙이면서
• AI가 생성·판단·수정하기 위한 인터페이스 규칙이다.

노드 이름은 곧 의사결정 단위이며,
이 규칙은 워크플로우를 코드가 아닌 구조화된 사고 체계로 다루기 위한 기반이다.

⸻

적용 범위
• 모든 n8n 워크플로우
• Phase 자동화 / 승인 루프 / 테스트 자동화 / 리포트 생성
• 향후 AI 기반 워크플로우 자동 생성 로직

⸻

변경 관리
• 규칙 변경 시 반드시 버전 관리 문서에 기록
• Prefix 추가 시 전체 워크플로우 영향 검토 필수

⸻

문서 상태: Active Rule
권장 적용 시작 Phase: Phase 8 이후 전체
