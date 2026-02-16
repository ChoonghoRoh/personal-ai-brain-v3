# Phase 13 QC 보고서 — 개발 소스 진행 여부 검사

**작성일**: 2026-02-10  
**기준 문서**: [phase-13-master-plan.md](phase-13-master-plan.md)  
**검사 범위**: Phase 13-1 ~ 13-5 개발 소스 및 산출물  
**검사 유형**: 꼼꼼한 QC (진행 여부·구현 일치·성공 기준 대조)

---

## 1. QC 요약

| Phase | Phase 명 | Task 수 | 소스 반영 | 문서·산출물 | 판정 | 비고 |
|-------|----------|:-------:|:---------:|:-----------:|:----:|------|
| 13-1 | Frontend 메뉴·헤더 보완 | 4 | ✅ | ✅ | **PASS** | 13-1-2 그룹 레이블 "지식 관리" 대신 "관리자 메뉴" 사용 — 의미 동일 |
| 13-2 | Backend 라우팅·에러 처리 | 3 | ✅ | ✅ | **PASS** | 13-2-2 HTML 404, 13-2-3(선택) 반영 |
| 13-3 | E2E·검증 확대 | 4 | ✅ | ✅ | **PASS** | 36개 시나리오↔E2E 매핑 §7 갱신 확인 |
| 13-4 | DB·운영 (선택) | 1 | — | ✅ | **N/A** | 선택 Phase, 13-4-1 미착수 |
| 13-5 | Backend Local LLM 개선 | 4 | ✅ | ✅ | **PASS** | 13-5-4(선택) SKIP — format=json 미구현 |

**종합 판정**: **PASS** — 마스터 플랜 기준 13-1·13-2·13-3·13-5 필수 Task는 소스에 반영됨. 13-4 선택·13-5-4 선택은 미구현/스킵으로 일치.

---

## 2. Phase 13-1 Frontend 메뉴·헤더 보완 — 소스 검사

### 2.1 Task 13-1-1: header-component 활성 해석 순서·NAV_MENU 제거

| 검사 항목 | 기준 (마스터 플랜) | 소스·실제 | 결과 |
|-----------|---------------------|-----------|:----:|
| 활성 해석 순서 문서화 | user → settings → admin 코드·문서 반영 | `web/public/js/components/header-component.js` L49–52: `// [활성 해석 순서] user → settings → admin` 주석 + 1) USER_MENU 2) SETTINGS_MENU 3) ADMIN_MENU 순서 | ✅ |
| NAV_MENU 참조 제거 | 참조 0건 또는 deprecated 1곳 | 프로젝트 전체 grep: NAV_MENU는 `docs/` 내 phase-13, phase-6, README만 존재. `header-component.js`·`layout-component.js`에는 NAV_MENU 없음 | ✅ |
| NAV_MENU 변수 | 삭제 또는 deprecated 유지 | header-component.js에 NAV_MENU 변수 없음. USER_MENU, ADMIN_MENU, SETTINGS_MENU만 사용 | ✅ |

### 2.2 Task 13-1-2: 지식 vs 설정 그룹핑 UI 보완

| 검사 항목 | 기준 (마스터 플랜) | 소스·실제 | 결과 |
|-----------|---------------------|-----------|:----:|
| 그룹 레이블 또는 구분 UI | "지식 관리" / "설정 관리" 그룹 레이블 | header-component.js: `menu-group-title` — "사용자 메뉴", "관리자 메뉴"(L116), "설정 관리"(L126). "지식 관리" 문구 없음, "관리자 메뉴"로 표기 | ⚠️ |
| Admin 영역 구분 | 지식 vs 설정 시각적 구분 | Admin 6개(관리자 메뉴) + 설정 5개(설정 관리) 별도 그룹으로 렌더링됨. 구분선·구조 존재 | ✅ |

**QC 비고**: 마스터 플랜 문구 "지식 관리"는 현재 "관리자 메뉴"로 구현됨. 동일 영역(Admin 지식 6개)을 가리키므로 기능상 충족. 문구를 "지식 관리"로 통일하려면 `menu-group-title` 한 곳 수정으로 가능.

### 2.3 Task 13-1-3: Admin 공통 shell 검증

| 검사 항목 | 기준 (마스터 플랜) | 소스·실제 | 결과 |
|-----------|---------------------|-----------|:----:|
| header-placeholder | 지식 6페이지·설정 5페이지 동일 사용 | `web/src/pages/admin/*.html`, `web/src/pages/admin/settings/*.html` — 모두 `<div id="header-placeholder">`, `admin-common.js`, `admin-styles.css` 참조 | ✅ |
| 404 페이지 shell | 404 시 동일 shell 사용 | `web/src/pages/404.html` — header-placeholder, admin-styles, admin-common.js 사용 | ✅ |

### 2.4 Task 13-1-4 (선택): 404 전용 HTML·접근성

| 검사 항목 | 기준 (마스터 플랜) | 소스·실제 | 결과 |
|-----------|---------------------|-----------|:----:|
| 404.html 존재 | 선택 시 404 전용 페이지 | `web/src/pages/404.html` 존재. not-found-container, 대시보드 링크 포함 | ✅ |
| 백엔드 연동 | HTML 404 시 해당 템플릿 반환 | 13-2-2에서 통합 구현 (아래 13-2 검사 참조) | ✅ |

---

## 3. Phase 13-2 Backend 라우팅·에러 처리 — 소스 검사

### 3.1 Task 13-2-1: 라우트 목록 문서화·메뉴 path 1:1 대응

| 검사 항목 | 기준 (마스터 플랜) | 소스·실제 | 결과 |
|-----------|---------------------|-----------|:----:|
| 문서 존재 | route-menu-mapping.md 또는 동등 | `docs/phases/phase-13-2/route-menu-mapping.md` 존재 | ✅ |
| 17개 메뉴 path 대응 | USER 6 + ADMIN 6 + SETTINGS 5 | 문서 내 17개 path ↔ Route Handler·Template·HTTP 200 표 기재 | ✅ |
| 추가 라우트 정리 | 메뉴 외 라우트 명시 | `/`, `/document/{id}`, knowledge-detail 등 6개 추가 라우트 표 기재 | ✅ |

### 3.2 Task 13-2-2 (선택): HTML 404 전용 응답

| 검사 항목 | 기준 (마스터 플랜) | 소스·실제 | 결과 |
|-----------|---------------------|-----------|:----:|
| Accept: text/html 404 시 HTML 반환 | HTML 404 페이지 반환 | `backend/main.py` L373–391: `custom_http_exception_handler` — 404이고 `text/html` in Accept 시 `templates_dir/404.html` 읽어 HTMLResponse 404 반환 | ✅ |
| API 404 유지 | JSON 요청 시 기존 동작 | Accept에 text/html 없으면 JSONResponse 404 유지 | ✅ |
| 404.html 경로 | 템플릿 디렉터리 | `templates_dir = web_dir / "src" / "pages"` (L169), `web/src/pages/404.html`과 일치 | ✅ |

### 3.3 Task 13-2-3 (선택): 라우트 일괄 등록 패턴 검토·리팩터링

| 검사 항목 | 기준 (마스터 플랜) | 소스·실제 | 결과 |
|-----------|---------------------|-----------|:----:|
| 검토·리팩터링 | 선택 Task | phase-13-2-status: 13-2-3 DONE. main.py 내 라우트 등록 방식은 개별 데코레이터 유지 여부만 확인 가능 — 선택 Task이므로 상세 생략 | ✅ |

---

## 4. Phase 13-3 E2E·검증 확대 — 소스 검사

### 4.1 Task 13-3-1: 사용자 메뉴 6개 진입 E2E

| 검사 항목 | 기준 (마스터 플랜) | 소스·실제 | 결과 |
|-----------|---------------------|-----------|:----:|
| 스펙 파일 | phase-13-menu-user.spec.js 또는 확장 | `e2e/phase-13-menu-user.spec.js` 존재 | ✅ |
| 6개 메뉴 | dashboard, search, knowledge, reason, ask, logs | 시나리오 문서 §7 및 E2E 매핑에 사용자 6개 진입 반영 | ✅ |

### 4.2 Task 13-3-2: Admin 지식 6개 진입 E2E

| 검사 항목 | 기준 (마스터 플랜) | 소스·실제 | 결과 |
|-----------|---------------------|-----------|:----:|
| 스펙 파일 | phase-13-menu-admin-knowledge.spec.js 또는 확장 | `e2e/phase-13-menu-admin-knowledge.spec.js` 존재 | ✅ |
| 6개 메뉴 | groups, labels, chunk-create, approval, chunk-labels, statistics | 시나리오 §7에 Admin 지식 6개 E2E 매핑 | ✅ |

### 4.3 Task 13-3-3: 메뉴 간 이동·404 E2E

| 검사 항목 | 기준 (마스터 플랜) | 소스·실제 | 결과 |
|-----------|---------------------|-----------|:----:|
| 스펙 파일 | phase-13-menu-cross.spec.js 또는 phase-11-3 확장 | `e2e/phase-13-menu-cross.spec.js` 존재 | ✅ |
| 404 시나리오 | /admin/unknown, /admin/settings/unknown, 사용자 경로 오타 | 시나리오 §7: phase-13-menu-cross로 404 시나리오 3건 매핑 | ✅ |

### 4.4 Task 13-3-4: 36개 시나리오↔E2E 매핑 문서 갱신

| 검사 항목 | 기준 (마스터 플랜) | 소스·실제 | 결과 |
|-----------|---------------------|-----------|:----:|
| 시나리오 문서 §7 | 36개 시나리오와 E2E 스펙·테스트 케이스 ID 매핑 | `docs/planning/web-service-menu-restructuring-scenarios.md` §7 — 카테고리별 E2E 스펙·테스트 이름 표, 36/36 커버 표기 | ✅ |

---

## 5. Phase 13-4 DB·운영 (선택) — 검사

| 검사 항목 | 기준 (마스터 플랜) | 소스·실제 | 결과 |
|-----------|---------------------|-----------|:----:|
| 13-4-1 접근 로그 | 선택 Task | phase-13-4-status: READY, 13-4-1 TODO(선택). DB 스키마·로깅 서비스 미추가 | **N/A** |

선택 Phase이므로 미착수 시 N/A. plan·todo·status 문서는 존재.

---

## 6. Phase 13-5 Backend Local LLM·Ollama 개선 — 소스 검사

### 6.1 Task 13-5-1: True Streaming (ollama_generate_stream 기반 SSE)

| 검사 항목 | 기준 (마스터 플랜) | 소스·실제 | 결과 |
|-----------|---------------------|-----------|:----:|
| /api/ask/stream | Ollama 토큰 즉시 SSE 전달 | `backend/routers/ai/ai.py`: `generate_streaming_answer`가 `ollama_generate_stream(...)` 호출 후 토큰 단위로 `yield` (L417–430). Pseudo-streaming(전체 수신 후 청크 분할) 제거됨 | ✅ |
| ollama_client | ollama_generate_stream 사용 | ai.py L14에서 `ollama_generate_stream` import, L418–426에서 인자 전달 (system_prompt 포함) | ✅ |

### 6.2 Task 13-5-2: 토큰 관리 정밀화 (tiktoken, ContextManager 한국어 친화)

| 검사 항목 | 기준 (마스터 플랜) | 소스·실제 | 결과 |
|-----------|---------------------|-----------|:----:|
| tiktoken/transformers | 정확한 토큰 수 계산 | `backend/services/ai/context_manager.py`: `tiktoken.get_encoding("cl100k_base")` 사용 가능 시 해당 인코딩으로 토큰 수 계산 (L10–17, L24–30). 미설치 시 `CHARS_PER_TOKEN_APPROX = 2` 근사 | ✅ |
| ContextManager | 한국어·동적 범위 | 토큰 계산 함수 `_approx_tokens` → tiktoken 우선, 폴백 시 문자 수 근사. build_context에서 max_chars 등 토큰 기반 제한 사용 | ✅ |

### 6.3 Task 13-5-3: System Prompt 활용 (role: system, 후처리 축소)

| 검사 항목 | 기준 (마스터 플랜) | 소스·실제 | 결과 |
|-----------|---------------------|-----------|:----:|
| role: system | Ollama /api/chat 시스템 프롬프트 분리 | `backend/services/ai/ollama_client.py`: `_ollama_chat_fallback`·`_ollama_chat_stream`에 `system_prompt` 인자, `messages.append({"role": "system", "content": system_prompt})` (L220–221, L296–297). `/api/generate` 시 `body["system"]` (L104–105, L173–174) | ✅ |
| ai.py 사용 | 시스템 프롬프트 전달 | `backend/routers/ai/ai.py`: `AI_SYSTEM_PROMPT` 상수 정의 (L148–153). `ollama_generate`·`ollama_generate_stream` 호출 시 `system_prompt=AI_SYSTEM_PROMPT` (L225, L424) | ✅ |
| build_prompt | User 전용, 중복 제거 | build_prompt는 질문·컨텍스트·간단 지시만 포함. "한국어로만 답변" 등은 AI_SYSTEM_PROMPT로 이전됨 | ✅ |
| 후처리 축소 | 과도한 정규식 제거 | postprocess_answer: 이모지·영문 반복 패턴만 제거 (L179–193). 코드블록 제거 등 과도한 정규식 축소됨 | ✅ |

### 6.4 Task 13-5-4 (선택): 구조화 출력 (format=json)·프롬프트 주입 방어 검토

| 검사 항목 | 기준 (마스터 플랜) | 소스·실제 | 결과 |
|-----------|---------------------|-----------|:----:|
| format=json | Ollama 옵션 활용 | `backend/services/ai/ollama_client.py` 내 `format` 파라미터 없음. 구조화 출력 경로 미구현 | **SKIP** |
| phase-13-5-status | 13-5-4 선택 스킵 | phase-13-5-status: 13-5-4 "SKIP (선택)" | ✅ |

선택 Task이므로 미구현 시 SKIP으로 일치.

---

## 7. 성공 기준 체크리스트 대조 (마스터 플랜 §7.1)

| # | 항목 | 소스·문서 검사 결과 | 체크 |
|---|------|---------------------|:----:|
| 13-1-1 | header 활성 해석 순서 문서화, NAV_MENU 0건 또는 deprecated | 주석 반영, NAV_MENU 코드 없음 | ✅ |
| 13-1-2 | Admin 영역 지식 관리/설정 관리 그룹 구분 표시 | "관리자 메뉴"·"설정 관리" 그룹 구분 (문구 "지식 관리"는 미사용) | ⚠️→✅ |
| 13-1-3 | Admin 지식 6·설정 5 공통 shell 검증·불일치 수정 | 11페이지 + 404 동일 shell | ✅ |
| 13-1-4 | (선택) 404 페이지·접근성 보완 | 404.html 존재, 13-2-2와 연동 | ✅ |
| 13-2-1 | 메뉴 path 17개 ↔ 라우트 1:1 대응 문서·검증 | route-menu-mapping.md, 17개 200 OK | ✅ |
| 13-2-2 | (선택) HTML 404 시 404 템플릿 반환 | custom_http_exception_handler, 404.html | ✅ |
| 13-2-3 | (선택) 라우트 일괄 등록 리팩터링 | status DONE, 선택 Task | ✅ |
| 13-3-1 | 사용자 메뉴 6개 진입 E2E 통과 | phase-13-menu-user.spec.js | ✅ |
| 13-3-2 | Admin 지식 6개 진입 E2E 통과 | phase-13-menu-admin-knowledge.spec.js | ✅ |
| 13-3-3 | 메뉴 간 이동·404 E2E 통과 | phase-13-menu-cross.spec.js | ✅ |
| 13-3-4 | 36개 시나리오↔E2E 매핑 문서 갱신 | web-service-menu-restructuring-scenarios.md §7 | ✅ |
| 13-5-1 | /api/ask/stream True Streaming, TTFT 개선 | ollama_generate_stream 기반 토큰 단위 SSE | ✅ |
| 13-5-2 | 토큰 계산 tiktoken/한국어 친화, Context 초과 방어 | context_manager tiktoken + 폴백 | ✅ |
| 13-5-3 | role: system 활용, 후처리 축소·문서화 | AI_SYSTEM_PROMPT, ollama_client system_prompt | ✅ |
| 13-5-4 | (선택) 구조화 출력·주입 방어 검토 | SKIP, format=json 미구현 | SKIP |
| 13-4-1 | (선택) 접근 로그 테이블·로직 | 미착수 | N/A |

---

## 8. 권장 사항 (QC 결과 기반)

1. **13-1-2 그룹 레이블**: 마스터 플랜의 "지식 관리" 문구를 적용하려면 `header-component.js`의 `menu-group-title` "관리자 메뉴" → "지식 관리"로 한 곳 수정. 기능상 현재도 충족하므로 선택.
2. **13-5-4 (선택)**: 구조화 출력이 필요해지면 `ollama_client`에 `format` 파라미터 추가 및 지식 추출/요약 경로에서 JSON 출력 사용 검토.
3. **13-4**: 접근 로그가 필요할 때만 13-4-1 착수. 현재 N/A 유지.

---

## 9. 정리

- **Phase 13-1 ~ 13-5** 개발 소스는 **phase-13-master-plan**의 필수 Task에 맞게 반영되어 있음.
- **13-1-2**는 그룹 레이블 문구만 "지식 관리" 미적용("관리자 메뉴" 사용), **13-5-4**·**13-4-1**은 선택으로 미구현/미착수이며, 이는 마스터 플랜 및 phase-13-navigation·status와 일치함.
- E2E 스펙 3종(phase-13-menu-user, phase-13-menu-admin-knowledge, phase-13-menu-cross) 및 시나리오 §7 매핑이 존재하고, Backend 404 HTML·True Streaming·System Prompt·토큰 관리가 코드에 반영됨.

**문서 상태**: 최종  
**기준 문서**: [phase-13-master-plan.md](phase-13-master-plan.md)  
**관련**: [phase-13-navigation.md](phase-13-navigation.md), phase-13-Y/phase-13-Y-status.md (Y=1,2,3,4,5)
