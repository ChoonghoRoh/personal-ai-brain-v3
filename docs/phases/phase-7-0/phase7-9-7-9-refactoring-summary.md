# Phase 7.9.7-9: 코드 리팩토링 및 AI 질의 기능 개선

**작성일**: 2026-01-10  
**Phase**: 7.9.7, 7.9.8, 7.9.9

---

## 📋 작업 개요

프론트엔드 코드 구조 개선 및 AI 질의 기능의 품질 향상을 위한 작업을 수행했습니다.

---

## 🔧 Phase 7.9.7: 스크립트 분리 작업

### 목표
모든 HTML 파일의 인라인 JavaScript를 외부 파일로 분리하여 코드 유지보수성과 재사용성을 향상시킵니다.

### 작업 내용

#### 1. 스크립트 분리 대상 파일
총 14개 HTML 파일의 인라인 스크립트를 외부 JavaScript 파일로 분리:

**일반 페이지:**
- `dashboard.html` → `dashboard.js`
- `knowledge.html` → `knowledge.js`
- `search.html` → `search.js`
- `ask.html` → `ask.js`
- `reason.html` → `reason.js`
- `logs.html` → `logs.js`
- `document.html` → `document.js`

**Knowledge 관련 페이지:**
- `knowledge-detail.html` → `knowledge-detail.js`
- `knowledge-label-matching.html` → `knowledge-label-matching.js`
- `knowledge-relation-matching.html` → `knowledge-relation-matching.js`
- `knowledge-admin.html` → `knowledge-admin.js`

**Admin 페이지:**
- `admin/labels.html` → `admin-labels.js`
- `admin/approval.html` → `admin-approval.js`
- `admin/groups.html` → `admin-groups.js`

#### 2. 생성된 JavaScript 파일
총 19개 외부 JavaScript 파일 생성:

**페이지별 스크립트 (14개):**
- `knowledge.js`
- `dashboard.js`
- `document.js`
- `search.js`
- `ask.js`
- `reason.js`
- `logs.js`
- `knowledge-detail.js`
- `knowledge-label-matching.js`
- `knowledge-relation-matching.js`
- `knowledge-admin.js`
- `admin-labels.js`
- `admin-approval.js`
- `admin-groups.js`

**공통 컴포넌트 (5개):**
- `layout-component.js` - 레이아웃 초기화
- `header-component.js` - 헤더 렌더링
- `document-utils.js` - 문서 관련 유틸리티
- `text-formatter.js` - 텍스트 포맷팅 (마크다운 파싱 등)
- `admin-common.js` - Admin 페이지 공통 함수

#### 3. 테스트 결과
- ✅ 모든 JavaScript 파일 문법 검사 통과
- ✅ 모든 페이지 HTTP 200 응답 확인
- ✅ 모든 JavaScript 파일 접근 가능 확인
- ✅ 인라인 스크립트 완전 제거 확인

### 효과
- 코드 유지보수성 향상
- 스크립트 재사용성 증가
- HTML 파일 크기 감소
- 브라우저 캐싱 효율 향상

---

## 🎨 Phase 7.9.8: CSS 분리 작업

### 목표
`knowledge-admin.html`의 인라인 CSS를 제거하여 외부 CSS 파일만 사용하도록 개선합니다.

### 작업 내용

#### 1. 인라인 CSS 제거
- **대상 파일**: `web/src/pages/knowledge-admin.html`
- **제거된 CSS**: 9-610줄 (약 600줄)
- **결과**: 파일 크기 883줄 → 281줄

#### 2. 외부 CSS 파일 사용
- 기존에 생성된 `web/public/css/knowledge-admin.css` 파일만 사용
- 인라인 스타일 완전 제거

### 효과
- HTML 파일 크기 대폭 감소
- CSS 관리 용이성 향상
- 브라우저 캐싱 효율 향상

---

## 🤖 Phase 7.9.9: AI 질의 기능 개선

### 목표
AI 질의 기능의 답변 품질을 향상시키고 컨텍스트 윈도우 초과 문제를 해결합니다.

### 문제점
1. **영어로 답변 생성**: 한국어 질문에도 영어로 답변이 생성됨
2. **불필요한 패턴 반복**: "(토큰 제한 고려하여...)" 같은 패턴이 반복됨
3. **컨텍스트 윈도우 초과**: 프롬프트가 모델의 컨텍스트 윈도우(2048 토큰)를 초과

### 개선 사항

#### 1. 프롬프트 개선
```python
# 개선 전
prompt = f"""컨텍스트를 바탕으로 질문에 답변하세요.
...
답변:"""

# 개선 후
prompt = f"""당신은 한국어로 답변하는 AI 어시스턴트입니다. 
다음 컨텍스트를 바탕으로 질문에 대해 정확하고 유용한 답변을 한국어로 제공하세요.

컨텍스트: ...
질문: ...

지시사항:
- 반드시 한국어로만 답변하세요
- 불필요한 반복, 이모지, 장식적인 표현을 피하세요
- 답변은 간결하고 명확하게 작성하세요

답변:"""
```

#### 2. 컨텍스트 길이 제한
- **전체 컨텍스트**: 최대 1200자로 제한
- **각 문서**: 최대 300자로 제한
- 컨텍스트 윈도우(2048 토큰) 고려하여 안전한 범위로 설정

#### 3. 답변 후처리
- "(토큰 제한 고려하여...)" 패턴 자동 제거
- 반복되는 이모지 제거
- 불필요한 장식 표현 제거

#### 4. 반복 방지 강화
- `repeat_penalty`: 1.1 → 1.2로 증가

#### 5. 자동 재시도 로직
- 컨텍스트 윈도우 초과 오류 발생 시
- 컨텍스트를 절반(600자)으로 줄여서 자동 재시도

### 개선 효과
- ✅ 한국어 답변 생성 보장
- ✅ 불필요한 패턴 제거
- ✅ 컨텍스트 윈도우 초과 문제 해결
- ✅ 답변 품질 향상

---

## 📊 작업 통계

### Phase 7.9.7 (스크립트 분리)
- **분리된 HTML 파일**: 14개
- **생성된 JavaScript 파일**: 19개
- **제거된 인라인 스크립트**: 약 5,000줄 이상
- **테스트 통과율**: 100%

### Phase 7.9.8 (CSS 분리)
- **처리된 파일**: 1개
- **제거된 인라인 CSS**: 약 600줄
- **파일 크기 감소**: 68% (883줄 → 281줄)

### Phase 7.9.9 (AI 질의 개선)
- **수정된 파일**: 1개 (`backend/routers/ai.py`)
- **컨텍스트 길이 제한**: 1200자
- **반복 방지**: repeat_penalty 1.2

---

## 🎯 다음 단계

### 권장 사항
1. **나머지 HTML 파일 CSS 분리**: 다른 HTML 파일에도 인라인 CSS가 있는지 확인
2. **JavaScript 모듈화**: 공통 함수를 더 모듈화하여 재사용성 향상
3. **AI 답변 품질 모니터링**: 실제 사용자 피드백을 통한 추가 개선

### 완료된 작업
- ✅ 모든 HTML 파일 스크립트 분리 완료
- ✅ knowledge-admin.html CSS 분리 완료
- ✅ AI 질의 기능 개선 완료
- ✅ 모든 변경사항 테스트 완료

---

## 📝 관련 파일

### 수정된 파일
- `backend/routers/ai.py` - AI 질의 기능 개선
- `web/src/pages/*.html` - 스크립트 분리 (14개 파일)
- `web/public/js/*.js` - 외부 JavaScript 파일 (19개 파일)
- `web/src/pages/knowledge-admin.html` - CSS 분리

### 생성된 문서
- `docs/dev/phase7-9-7-script-separation-test-results.md` - 스크립트 분리 테스트 결과
- `docs/dev/phase7-9-7-9-refactoring-summary.md` - 본 문서

---

## ✅ 검증 완료

모든 작업이 완료되었으며, 다음 항목들이 검증되었습니다:

1. ✅ 모든 JavaScript 파일 문법 검사 통과
2. ✅ 모든 페이지 HTTP 접근 가능
3. ✅ 인라인 스크립트 완전 제거
4. ✅ AI 질의 기능 한국어 답변 생성 확인
5. ✅ 컨텍스트 윈도우 초과 문제 해결
