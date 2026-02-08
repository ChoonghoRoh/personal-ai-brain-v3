# Task 11-3-2: 템플릿·프리셋·RAG 프로필 편집 화면

**우선순위**: 11-3 내 2순위  
**예상 작업량**: 3.5일  
**의존성**: 11-3-1 완료  
**상태**: ⏳ 대기

**기반 문서**: [phase-11-3-0-todo-list.md](../phase-11-3-0-todo-list.md)  
**Plan**: [phase-11-3-0-plan.md](../phase-11-3-0-plan.md)  
**작업 순서**: [phase-11-navigation.md](../../phase-11-navigation.md)

---

## 1. 개요

### 1.1 목표

**템플릿·프리셋·RAG 프로필** 각각에 대해 목록·상세·편집 화면을 구현하고, 공통 폼·유효성·에러 표시를 admin-common 또는 전용 모듈로 확장한다. API 연동은 11-3-4에서 통합한다.

---

## 2. 파일 변경 계획

### 2.1 신규 생성

| 파일 경로 | 용도 |
|-----------|------|
| `web/src/pages/admin/` (또는 settings/) | 템플릿·프리셋·RAG 프로필 목록·상세·편집 HTML |
| `web/public/js/admin/` (또는 settings/) | 해당 페이지용 JS |
| `web/public/css/admin/` (또는 settings/) | 해당 페이지용 CSS |

### 2.2 수정

| 파일 경로 | 용도 |
|-----------|------|
| `web/public/js/admin/admin-common.js` (필요 시) | 공통 폼·유효성·에러·로딩 확장 |

---

## 3. 작업 체크리스트 (Done Definition)

### 3.1 11-3-2a: 템플릿 목록·상세·편집

- [ ] 템플릿 목록 화면 (테이블/카드, status 필터)
- [ ] 템플릿 상세 뷰
- [ ] 템플릿 편집 폼 (name, template_type, content, output_format, citation_rule 등)
- [ ] Draft 저장·Publish 버튼 UI
- [ ] HTML/JS/CSS 작성, task 문서화

### 3.2 11-3-2b: 프리셋 목록·상세·편집

- [ ] 프리셋 목록 화면 (task_type 필터)
- [ ] 프리셋 상세 뷰
- [ ] 프리셋 편집 폼 (system_prompt, model_name, temperature, top_p, max_tokens, constraints 등)
- [ ] HTML/JS/CSS 작성

### 3.3 11-3-2c: RAG 프로필 목록·상세·편집

- [ ] RAG 프로필 목록 화면
- [ ] RAG 프로필 상세 뷰
- [ ] RAG 프로필 편집 폼 (chunk_size, chunk_overlap, top_k, score_threshold, use_rerank 등)
- [ ] HTML/JS/CSS 작성

### 3.4 11-3-2d: 공통 폼·유효성·에러 표시

- [ ] 입력 유효성·필수 필드 처리
- [ ] API 에러 메시지 표시(showError 등 재사용)
- [ ] 로딩 상태 표시(선택)
- [ ] admin-common 또는 전용 모듈 확장

---

## 4. 참조

- [phase-11-3-0-plan.md](../phase-11-3-0-plan.md) §5.2
- [phase-11-master-plan-sample.md](../../phase-11-master-plan-sample.md) — Admin UI 화면 설계 참고
