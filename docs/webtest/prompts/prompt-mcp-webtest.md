# MCP(Cursor) 웹 테스트 — 복사용 프롬프트

**용도**: Cursor Agent에서 MCP 브라우저로 phase 웹 체크리스트를 수행할 때, **복사해 붙여 넣기**용 지시문입니다.  
**가이드**: [mcp-cursor-test-guide.md](../mcp-cursor-test-guide.md)

---

## Phase 9-1 (보안 강화)

체크리스트 문서를 @로 붙인 뒤 아래 중 하나를 붙여 넣습니다.

**기본 (결과/비고만 기록):**

```
@docs/phases/phase-9-1/phase-9-1-web-user-checklist.md

이 문서의 "메뉴(라우터)별 시나리오 체크리스트"를 따라
가상 브라우저(MCP)에서 http://localhost:8000 기준으로 순서대로 수행해 줘.
각 시나리오(W1.1~W9.x)별로 접속·동작·결과를 확인하고, 결과/비고란에 통과(OK)·실패·비고를 기록해 줘.
```

**개발자 관점:**

```
@docs/phases/phase-9-1/phase-9-1-web-user-checklist.md
@docs/webtest/personas.md
@docs/webtest/prompts/prompt-developer.md

phase-9-1 웹 체크리스트를 가상 브라우저에서 http://localhost:8000 기준으로 순서대로 수행해 줘.
개발자 관점(버그·에러·API·재현 단계)으로 발견 사항을 기록해 줘.
```

---

## Phase 9-3 (AI 기능 고도화)

**기본:**

```
@docs/phases/phase-9-3/phase-9-3-web-user-checklist.md

phase-9-3 웹 체크리스트를 가상 브라우저(MCP)에서 http://localhost:8000 기준으로 순서대로 수행해 줘.
결과는 체크리스트의 결과/비고 형식으로 기록해 줘.
```

---

## 공통 (phase 번호만 바꿔 쓰기)

```
@docs/phases/phase-X-Y/phase-X-Y-web-user-checklist.md

phase-X-Y 웹 체크리스트를 가상 브라우저(MCP)에서 http://localhost:8000 기준으로 순서대로 수행해 줘.
각 시나리오별 접속·동작·결과를 확인하고, 결과/비고란에 기록해 줘.
```

- **X-Y** 를 테스트할 phase 번호로 치환 (예: 9-1, 9-3).
