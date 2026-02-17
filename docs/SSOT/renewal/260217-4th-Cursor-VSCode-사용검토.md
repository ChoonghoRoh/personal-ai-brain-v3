# 4th SSOT 문서 — Cursor·VSCode에서 사용 가능성 검토

**검토일**: 2026-02-17  
**대상**: 4th SSOT 문서(`docs/SSOT/renewal/iterations/4th/`)를 Cursor IDE·VSCode에서 실제로 사용할 수 있는지, 현재 설정과의 관계·한계·적용 방안을 정리.

---

## 1. 요약

| 도구 | 4th 사용 가능 여부 | 현재 참조 | 4th 적용 시 변경 |
|------|---------------------|-----------|------------------|
| **Cursor** | ✅ 가능 | docs/rules/role/LEADER.md (규칙 링크) | 규칙에서 4th PERSONA/LEADER.md(또는 SSOT 진입점) 참조로 변경 |
| **VSCode (Copilot)** | ✅ 가능 | docs/rules/role/QA.md (설정 내 지시문) | 설정에서 4th PERSONA/QA.md·필요 시 ROLES 참조로 변경 |

둘 다 **경로만 4th로 바꾸면** 4th 문서를 사용할 수 있다. Cursor는 추가로 4th 진입점(0-entrypoint)을 규칙으로 넣어 SSOT 전체 맥락을 줄 수 있다.

---

## 2. Cursor에서의 사용

### 2.1 현재 구조

| 항목 | 내용 |
|------|------|
| **규칙 위치** | `.cursor/rules/leader-persona.mdc` |
| **적용 방식** | `alwaysApply: true` — 모든 채팅에 적용 |
| **내용** | 리더 페르소나 요약(인라인) + **전문 문서 링크** `docs/rules/role/LEADER.md` |
| **AGENTS.md** | Cursor는 LEADER.md 페르소나 사용한다고 명시 |

규칙 본문은 짧고, “자세한 건 LEADER.md 참조”로 되어 있음. Cursor가 해당 파일을 언제 로딩하는지는 제품 동작에 따름(링크만 있으면 사용자가 열거나 에이전트가 참조할 때 로딩).

### 2.2 4th 사용 방안

- **방안 A — PERSONA만 4th로**  
  - `leader-persona.mdc`의 링크를  
    `docs/rules/role/LEADER.md` → **`docs/SSOT/renewal/iterations/4th/PERSONA/LEADER.md`** 로 변경.  
  - Cursor 리더 페르소나는 4th PERSONA(통합·SSOT)를 쓰게 됨.

- **방안 B — SSOT 진입점까지 포함**  
  - 기존 리더 규칙은 유지하고, **추가 규칙** 하나 더 둠.  
  - 예: `.cursor/rules/ssot-entry.mdc`  
    - `description`: "SSOT 진입점(Agent Teams용)"  
    - `globs`: (비워두거나 `docs/**`)  
    - `alwaysApply`: false 또는 true  
    - 본문: "Agent Teams·Phase 작업 시 다음 SSOT 진입점을 참조: docs/SSOT/renewal/iterations/4th/0-entrypoint.md"  
  - 0-entrypoint는 약 442줄로, Cursor 권장 규칙 길이(500줄 이하) 안에 들어감.  
  - 필요 시 “전체를 넣지 말고 요약 + 링크만”으로 줄여서 규칙 크기 제어 가능.

- **4th를 docs/SSOT 루트로 이전한 경우**  
  - 위 경로를 **`docs/SSOT/PERSONA/LEADER.md`**, **`docs/SSOT/0-entrypoint.md`** 로 바꾸면 됨.

### 2.3 Cursor 측 한계·유의점

- 규칙에 **파일 경로**만 적는 경우, Cursor가 해당 파일을 **항상 자동으로 컨텍스트에 넣는지는 보장되지 않음**.  
  사용자가 해당 파일을 열거나, 채팅에서 @파일로 지정하면 확실히 사용됨.
- 규칙 본문이 너무 길면(예: 0-entrypoint 전체 442줄) 토큰을 많이 씀.  
  “짧은 요약 + 진입점/역할별 체크리스트 링크”로 두고, 상세는 4th 문서를 열어 보게 하는 구성이 무난함.
- **alwaysApply** 규칙을 너무 많이 두면 모든 대화에 토큰이 들어가므로, SSOT 규칙은 `alwaysApply: false` + `description`으로 “Agent/Phase 관련할 때만” 적용되게 두는 편이 좋을 수 있음.

---

## 3. VSCode에서의 사용 (Copilot)

### 3.1 현재 구조

| 항목 | 내용 |
|------|------|
| **설정 위치** | `.vscode/settings.json` |
| **키** | `github.copilot.chat.codeGeneration.instructions` |
| **내용** | QA·Security Analyst 역할 지시문 + **"Refer to docs/rules/role/QA.md and docs/rules/testing/"** |

Copilot 채팅/코드 생성 시 위 지시문이 적용되고, 문서는 “참조하라”는 경로로만 안내됨. Copilot이 해당 경로 파일을 실제로 읽는지는 제품 동작에 따름.

### 3.2 4th 사용 방안

- **지시문의 참조 경로만 4th로 변경**  
  - `docs/rules/role/QA.md` → **`docs/SSOT/renewal/iterations/4th/PERSONA/QA.md`**  
  - 필요 시 **`docs/SSOT/renewal/iterations/4th/ROLES/verifier.md`**, **`tester.md`** 도 참조하라고 문구 추가 가능.  
    예: "Refer to docs/SSOT/renewal/iterations/4th/PERSONA/QA.md and ROLES/verifier.md, tester.md for review and test criteria."

- **4th를 docs/SSOT 루트로 이전한 경우**  
  - `docs/SSOT/PERSONA/QA.md`, `docs/SSOT/ROLES/verifier.md` 등으로 경로 수정.

### 3.3 VSCode 측 한계·유의점

- **지시문 길이 제한**이 있을 수 있음. 4th 문서 전체를 붙여넣기보다는 “역할 + 참조할 문서 경로”만 두는 편이 안전함.
- Copilot이 **프로젝트 내 파일 경로**를 실제로 열어서 컨텍스트에 넣는지는 제품 동작에 따름. 경로를 정확히 주면 참조 가능성이 높음.

---

## 4. 공통 사항

### 4.1 4th 문서 특성과의 맞음

- 4th는 **단독 사용** 전제로, claude/ 등 다른 SSOT 폴더를 참조하지 않음.
- **PERSONA/** 에 LEADER, BACKEND, FRONTEND, QA, PLANNER가 있어, Cursor(리더)·VSCode(Copilot/QA) 역할과 1:1로 대응함.
- 경로만 바꿔도 **docs/rules/role/** 대신 4th PERSONA를 쓰는 구성이 가능함.

### 4.2 AGENTS.md와의 정합성

- AGENTS.md는 현재 “docs/rules/role/ 단일 소스”라고 되어 있음.
- Cursor·VSCode만 4th를 쓰도록 바꾸면, “Cursor/VSCode는 4th PERSONA 참조, 그 외는 기존 docs/rules/role 유지”처럼 **도구별 소스**를 명시해 두면 정합성 유지에 도움이 됨.
- 또는 4th를 SSOT 루트로 올린 뒤, AGENTS.md를 “기본 페르소나는 docs/SSOT/PERSONA”로 통일할 수도 있음.

---

## 5. 적용 체크리스트 (4th 사용 시)

- [ ] **Cursor**  
  - [ ] `.cursor/rules/leader-persona.mdc`에서 LEADER 링크를 4th PERSONA/LEADER.md로 변경  
  - [ ] (선택) `.cursor/rules/ssot-entry.mdc` 추가 — 4th 0-entrypoint 또는 요약+링크
- [ ] **VSCode**  
  - [ ] `.vscode/settings.json`의 `github.copilot.chat.codeGeneration.instructions`에서 QA 참조 경로를 4th PERSONA/QA.md(및 필요 시 ROLES)로 변경
- [ ] **AGENTS.md**  
  - [ ] “프로젝트 내 적용 위치”에 Cursor/VSCode가 4th PERSONA를 참조한다고 명시 (선택)
- [ ] **4th를 docs/SSOT 루트로 이전한 경우**  
  - [ ] 위 모든 경로를 `docs/SSOT/...` 기준으로 다시 수정

---

## 6. 결론

- **Cursor**: 4th 문서 사용 가능. 리더 페르소나 링크를 4th PERSONA/LEADER.md로 바꾸고, 필요 시 4th 진입점(0-entrypoint)을 규칙으로 추가하면 됨.
- **VSCode**: 4th 문서 사용 가능. Copilot 지시문의 참조 경로를 4th PERSONA/QA.md(및 ROLES)로 바꾸면 됨.
- **한계**: “링크/경로만” 넣는 방식이라, 도구가 해당 파일을 항상 자동 로딩하는지는 보장되지 않음. 사용자가 @파일로 지정하거나, 규칙/지시문을 적절히 쓰면 4th 문서가 실질적으로 사용됨.

---

**문서 상태**: 4th의 Cursor·VSCode 사용 가능성 검토 완료.
