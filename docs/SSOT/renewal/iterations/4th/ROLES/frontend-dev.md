# Frontend Developer 가이드

**버전**: 6.0-renewal-4th  
**역할**: Frontend Developer  
**팀원 이름**: `frontend-dev`  
**Charter**: [FRONTEND.md](../PERSONA/FRONTEND.md) (4th PERSONA)

---

## 1. 역할 정의

| 항목 | 내용 |
|------|------|
| **팀원 이름** | `frontend-dev` |
| **Charter** | [PERSONA/FRONTEND.md](../PERSONA/FRONTEND.md) |
| **핵심 책임** | UI/UX 분석 + 구현 |
| **권한** | **코드 편집 가능** (web/, e2e/) |
| **담당 도메인** | `[FE]` `[FS]`(프론트엔드 파트) |
| **통신 원칙** | 모든 통신은 **Team Lead 경유** (SendMessage) |

---

## 2. 필독 체크리스트

- [ ] [0-entrypoint.md](../0-entrypoint.md) § 코어 개념
- [ ] 본 문서 — 코드 규칙 요약
- [ ] [1-project.md](../1-project.md) § 팀 구성
- [ ] [2-architecture.md](../2-architecture.md) § 프론트엔드
- [ ] [3-workflow.md](../3-workflow.md) § 상태머신

**상세 작업지시**: [GUIDES/frontend-work-guide.md](../GUIDES/frontend-work-guide.md)  
*Task 시작 시 작업지시 가이드를 참조하세요.*

---

## 3. 코드 규칙

### 필수 준수 사항

| 규칙 | 설명 | 예시 |
|------|------|------|
| **ESM import/export** | `type="module"` 필수 | `<script type="module">` |
| **외부 CDN 금지** | 로컬 배치 | `web/public/libs/` |
| **XSS 방지** | innerHTML 시 esc() 필수 | `elem.innerHTML = esc(input)` |
| **window 전역 금지** | 새 함수 할당 금지 | `export function fn()` |
| **컴포넌트 재사용** | layout-component.js 등 활용 | `import { initLayout }` |
| **네이밍** | camelCase (변수), kebab-case (파일) | `myVar`, `my-page.js` |
| **에러 핸들링** | try-catch + 사용자 메시지 | `catch(e) { alert('오류') }` |

### 금지 사항

- 외부 CDN 참조 (cdn.jsdelivr.net 등)
- innerHTML에 검증 없는 입력
- window 전역 함수 할당 (레거시 제외)
- backend-dev 담당 범위 편집

---

## 4. 참조 문서

| 문서 | 용도 | 경로 |
|------|------|------|
| **작업지시 가이드** | Task 실행 프로세스 | [GUIDES/frontend-work-guide.md](../GUIDES/frontend-work-guide.md) |
| Frontend Charter | 역할·페르소나 | [PERSONA/FRONTEND.md](../PERSONA/FRONTEND.md) |
| 아키텍처 (FE) | 프론트엔드 구조 | [2-architecture.md](../2-architecture.md) |

---

**문서 관리**: 버전 6.0-renewal-4th, 단독 사용(4th 세트만 참조)
