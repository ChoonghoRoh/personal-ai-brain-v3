# Web 사용자 테스트 페르소나

**용도**: **AI가 사람 대신** 가상 브라우저에서 웹 테스트를 수행할 때, (1) **동작 검증 대상**인 사용자(일반 웹 사용자)와 (2) **AI가 취할 테스트 성향·관점**(기획자/개발자/UI·UX 디자이너)을 정의합니다. 사람이 수동으로 테스트할 때도 같은 관점을 적용할 수 있습니다.

---

## 1. 기준 페르소나: 일반 웹 사용자

테스트 시 **동작을 검증할 대상**은 일반 웹 사용자입니다. AI는 이 사용자처럼 행동하며 시나리오를 진행합니다.

- **정의**: 웹 사이트를 일상적으로 사용하는 사람. 기술에 익숙하지 않을 수 있으며, 메뉴·버튼·안내 문구에 의존해서 화면을 탐색합니다.
- **목표**: 실제 사용자에 가깝게 **메뉴 진입 → 화면 동작 → 결과 확인**이 자연스럽게 이루어지는지 검증합니다.
- **테스트 시**: 체크리스트 시나리오를 “일반 웹 사용자처럼” 따라가며, 막히는 곳·헷갈리는 곳·불명확한 안내가 있는지 확인합니다.

---

## 2. AI 테스트 수행 시 지정할 관점 (3가지)

**AI가** 가상 브라우저에서 체크리스트를 수행할 때, **어떤 성향으로 무엇을 보고 어떻게 기록할지**를 정하기 위한 관점입니다. 아래 중 하나를 지정하면 AI가 그 관점에 맞춰 테스트를 수행하고 발견 사항을 기록합니다.

| 관점               | 역할                          | 확인 초점                                 | 상세 가이드                                                                          |
| ------------------ | ----------------------------- | ----------------------------------------- | ------------------------------------------------------------------------------------ |
| **꼼꼼한 기획자**  | 요구사항·시나리오·플로우 검증 | 요구사항 일치, 플로우 정합성, 안내·문서화 | [frontend-webtest-prompt-planner.md](frontend-webtest-prompt-planner.md)             |
| **개발자**         | 버그·에러·동작 검증           | 콘솔/API, 재현 단계, 예상 vs 실제         | [frontend-webtest-prompt-developer.md](frontend-webtest-prompt-developer.md)         |
| **UI·UX 디자이너** | 시인성·일관성·사용성 검증     | 레이아웃, 접근성, 클릭/입력 흐름          | [frontend-webtest-prompt-uiux-designer.md](frontend-webtest-prompt-uiux-designer.md) |

- **꼼꼼한 기획자**: 시나리오와 기획서/요구사항 일치 여부, 단계별 플로우 자연스러움, 메시지·라벨·안내 문구 명확성, 예외/에러 시 사용자 안내를 중점적으로 봅니다.
- **개발자**: 버그·에러·콘솔/네트워크·성능·엣지케이스를 중점적으로 보고, 재현 단계와 예상/실제 동작을 기록합니다.
- **UI·UX 디자이너**: 시인성·일관성·접근성·사용성·시각적 계층을 중점적으로 보고, 버튼/링크 식별, 레이아웃·여백, 오류 메시지 가독성 등을 기록합니다.

각 관점의 구체적인 "무엇을 보고 어떻게 기록할지"는 위 테이블의 상세 가이드 링크를 참고하세요.

---

## 3. 활용방안 (AI가 테스트 수행할 때)

### 3.1 언제 쓰는가

- **AI 에이전트**(Cursor 등)가 **브라우저 MCP**로 가상 브라우저를 조작해 체크리스트를 실행할 때
- AI에게 “체크리스트대로 테스트해 줘”만 하면, **무엇에 초점을 두고 어떤 형식으로 기록할지**가 불명확함
- **personas.md + 관점별 prompt**를 함께 전달하면, AI가 **지정한 관점(기획자/개발자/UIUX)**으로 동작·기록함

### 3.2 어떻게 쓰는가

1. **테스트 지시 시 전달할 문서**
   - **필수**: 해당 phase의 **테스트 계획** + **웹 체크리스트** (예: `phase-9-3-user-test-plan.md`, `phase-9-3-web-user-checklist.md`)
   - **관점 지정**: **personas.md** + **관점 하나의 prompt** (`frontend-webtest-prompt-planner.md` 또는 `frontend-webtest-prompt-developer.md` 또는 `frontend-webtest-prompt-uiux-designer.md`)

2. **지시문 예시**
   - 기획자 관점:
     "@docs/rules/frontend/references/frontend-webtest-phase-9-3-user-test-plan.md @docs/rules/frontend/references/frontend-phase-9-3-web-user-checklist.md @docs/rules/frontend/references/frontend-webtest-personas.md @docs/rules/frontend/references/frontend-webtest-prompt-planner.md 를 참고해서, phase-9-3 웹 체크리스트를 가상 브라우저에서 순서대로 수행해 줘. **꼼꼼한 기획자** 관점으로 발견 사항을 기록해."
   - 개발자 관점:
     “위 문서들 대신 prompt-developer.md 를 포함해서 **개발자** 관점으로 테스트 수행해 줘.”
   - UI·UX 관점:
     “prompt-uiux-designer.md 를 포함해서 **UI·UX 디자이너** 관점으로 테스트 수행해 줘.”

3. **결과**
   - AI가 체크리스트 시나리오대로 브라우저에서 이동·클릭·입력 후, **선택한 관점**에 맞춰 발견 사항(버그·불명확한 안내·시인성 이슈 등)을 정리해 줌
   - 결과는 체크리스트의 “결과/비고” 형식이나 테스트 계획의 요약 표에 맞춰 기록하도록 요청하면 됨

### 3.3 참고

- 브라우저 MCP 사용 가능 여부·Base URL 조건은 [frontend-webtest-setup-guide.md](frontend-webtest-setup-guide.md) 3.3절 참고.
