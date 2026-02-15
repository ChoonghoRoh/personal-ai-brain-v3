# Personal AI Brain Ver3 — Cursor 리더 리뷰 보고서

**작성일시**: 2026-02-09 14:30  
**역할**: 총괄 아키텍트 및 프로젝트 매니저 (Lead Orchestrator)  
**관점**: 아키텍처·인터페이스·에이전트 역할·규칙 준수·배포 가능성

---

## 1. 리뷰 요약

| 항목 | 상태 | 비고 |
|------|------|------|
| 기술 스택·폴더 구조 | ✅ 양호 | Backend(FastAPI)·Web(Vanilla JS)·DB(PostgreSQL·Qdrant)·Ollama 일관 |
| 에이전트 역할 설정 | ✅ 정상 | Cursor·Claude·Copilot·Gemini 각 페르소나 적용 위치 확정 |
| API·Backend 구조 | ✅ 양호 | 라우터·서비스 계층 분리, Admin API·Reasoning·지식·검색 등 정리됨 |
| 프론트엔드 구조 | ✅ 양호 | web/public/js·css, 페이지별 모듈, ESM·On-Premise 방향 유지 |
| 문서·Base URL 일관성 | ⚠️ 개선 권장 | ver3는 8001인데 다수 문서가 8000으로 기재 |
| 규칙·컨벤션 | ✅ 양호 | docs/README·Phase·rules·AGENTS.md 단일 소스 유지 |

---

## 2. 프로젝트 개요 (리더 관점)

### 2.1 기술 스택

| 구분 | 기술 | 비고 |
|------|------|------|
| Backend | FastAPI, Python 3.11+ | pyproject.toml, mypy·ruff 설정 |
| Frontend | Vanilla JS (ESM), HTML, CSS | Bootstrap·Material Design, CDN 배제(On-Premise) |
| DB | PostgreSQL 15, Qdrant | ver3: 호스트 5433, 6343 |
| LLM | Ollama (로컬) | exaone3.5:2.4b / qwen2.5:3b 등 |
| 테스트 | Playwright (E2E), pytest | ver3 baseURL 8001 반영됨 |
| 배포 | Docker Compose | n8n Phase 8 보류로 기본 비기동 |

### 2.2 폴더 구조 (핵심만)

```
personal-ai-brain-v3/
├── backend/          # FastAPI: routers/, services/, models/, middleware/
├── web/              # 정적: public/{js,css}, src/pages/ (HTML)
├── docs/             # 문서: README/, phases/, rules/, overview/, webtest/, devtest/
├── brain/            # 시스템·프로젝트 메타 (work_log, context, todo 등)
├── scripts/          # DB·백업·devtool·n8n 스크립트
├── e2e/              # Playwright E2E 스펙
├── tests/            # pytest
├── .cursor/rules/    # Cursor 리더 페르소나 (alwaysApply)
├── .claude/           # Claude 백엔드 페르소나 (CLAUDE.md → BACKEND.md)
├── .github/           # Copilot 지침 (copilot-instructions.md → QA.md)
└── .gemini/           # Gemini 프론트 페르소나 (settings.json → FRONTEND.md)
```

---

## 3. 에이전트 역할 설정 점검

| 도구 | 적용 위치 | 역할 문서 | 세션 시 유지 |
|------|-----------|-----------|--------------|
| **Cursor** | `.cursor/rules/leader-persona.mdc` | LEADER.md | ✅ alwaysApply: true |
| **Claude Code** | `.claude/CLAUDE.md` | BACKEND.md | ✅ 프로젝트 열 때 로드 |
| **Copilot** | `.github/copilot-instructions.md` | QA.md | ✅ QA 페르소나로 수정 완료(최근) |
| **Gemini** | `.gemini/settings.json` | FRONTEND.md (persona_file) | ✅ 세션·컨텍스트 설정 있음 |

**단일 소스**: 모든 페르소나 정의는 `docs/rules/role/` 하위(LEADER, BACKEND, QA, FRONTEND)에서만 관리되며, AGENTS.md는 인덱스 역할만 수행함.

---

## 4. 아키텍처·인터페이스

### 4.1 Backend API 구조

- **라우터**: auth, search, documents, system, ask, knowledge, approval, relations, reasoning, admin, cognitive, automation, ingest 등 용도별 분리.
- **서비스**: search, ai, knowledge, reasoning, cognitive, system, ingest 등 — 라우터와 1:1 대응하지 않으나 도메인 단위로 정리됨.
- **모델**: `models.py`, `admin_models.py`, `database.py` — Admin 설정(schemas, templates, presets, rag_profiles, policy_sets, audit_logs) 별도 모델 유지.

### 4.2 Frontend ↔ Backend 경계

- 메뉴별 HTML·JS·CSS 매핑이 `docs/overview/cursor-overview-260208.md` 등에 정리되어 있음.
- API prefix와 페이지 경로 대응이 문서화되어 있어, 백엔드(Claude)·프론트(Gemini) 간 인터페이스 충돌 방지에 유리함.

### 4.3 Base URL 불일치 (리더 권장 사항)

- **실제 ver3**: `docker-compose.yml` → 호스트 `8001`, Playwright `baseURL` → `8001` (또는 BASE_URL).
- **문서 다수**: `docs/overview/cursor-overview-260208.md`, webtest, devtest, rules 일부가 **8000** 기준으로 기재.
- **권장**:  
  - “ver3 기본 Base URL은 8001”을 docs/README 또는 02-architecture에 명시하고,  
  - 신규·수정 문서는 8001 기준으로 통일하거나, “ver3: 8001, ver2: 8000” 표기로 정리.

---

## 5. 규칙·컨벤션

- **문서 분류**: docs/README/04-rules-and-conventions.md, Phase taxonomy, n8n·AI 룰 링크 유지.
- **Phase**: phase-X-master-plan, phase-X-navigation, phase-X-Y task 문서 체계 유지.
- **코드 품질**: pyproject.toml(mypy, ruff), E2E(Playwright), 통합 테스트(docs/devtest) 연동됨.

---

## 6. 배포·운영 관점

- Docker Compose로 postgres, qdrant, backend 기동 가능. n8n은 주석 처리로 기본 미기동.
- README·빠른 시작·Phase 요약 링크가 정리되어 있어 온보딩에 유리함.
- 백업/복원·무결성 검사 API·Audit Log 등 운영 요소가 Phase 9·11에서 반영됨.

---

## 7. 결론 및 권장 사항

### 7.1 유지할 점

- 에이전트 역할이 도구별로 명확히 배치되어 있고, 페르소나는 `docs/rules/role/` 단일 소스로 관리됨.
- Backend/Web/DB/테스트 구조와 문서 체계가 Phase·기능 단위로 잘 정리되어 있음.
- On-Premise·Vanilla JS·ESM 방침이 프론트엔드 Charter와 일치함.

### 7.2 리더 권장 조치

1. **Base URL 통일**: ver3 기본을 8001로 고정하고, overview·webtest·devtest·rules 내 예시 URL을 8001 기준으로 점진 수정(또는 “ver3: 8001” 명시).
2. **API 명세 가시성**: OpenAPI(/docs)는 유지되므로, 신규 API 추가 시 Claude(Gemini)에 “API 명세 먼저 확정” 원칙만 재강조하면 됨.
3. **배포 전 QC**: Copilot(QA) 역할이 copilot-instructions에 반영된 상태이므로, 배포 전 Copilot으로 코드 리뷰·테스트·보안 점검을 한 번 더 수행하도록 팀에 안내.

---

**문서**: 이 보고서는 Cursor Lead Orchestrator 역할로 프로젝트를 리뷰한 결과이며, `docs/overview/` 에서 동일 형식(`cursor-lead-orchestrator-overview-YYMMDD-HHMM.md`)으로 추가 리뷰를 적재할 수 있음.

**참조**: [AGENTS.md](../../AGENTS.md), [docs/rules/role/LEADER.md](../rules/role/LEADER.md), [docs/README/02-architecture.md](../README/02-architecture.md), [docs/overview/cursor-overview-260208.md](cursor-overview-260208.md)
