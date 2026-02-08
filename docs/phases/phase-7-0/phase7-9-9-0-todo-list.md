# Phase 7.9.9: 코드 개선 작업 TODO 리스트

**작성일**: 2026-01-10  
**기준 문서**: [phase7-9-9-review-report.md](./phase7-9-9-review-report.md)

---

## 📋 작업 개요

총 **43개 작업 항목** (보안 취약점 6개 + 개선점 37개)

---

## 🔴 우선순위 1: 보안 취약점 수정 (XSS)

### 7-9-9-0: Dashboard 메뉴 XSS 취약점 수정

- **파일**: `web/public/js/dashboard.js`
- **문제**: innerHTML 직접 사용
- **작업 내용**:
  1. `utils.js`의 `escapeHtml` 함수 import 확인
  2. 모든 `innerHTML` 사용 부분 찾기
  3. 사용자 입력 데이터는 `escapeHtml`로 이스케이프 처리
  4. 마크다운 렌더링은 `text-formatter.js` 또는 DOMPurify 사용
- **예상 시간**: 30분
- **테스트**: Dashboard 페이지에서 XSS 공격 시도 (스크립트 태그 입력)

### 7-9-9-1: Search 메뉴 XSS 취약점 수정

- **파일**: `web/public/js/search.js`
- **문제**: innerHTML 직접 사용
- **작업 내용**:
  1. 검색 결과 표시 부분에서 `innerHTML` 사용 확인
  2. `escapeHtml` 함수 적용
  3. 검색어 하이라이팅은 안전한 방식으로 구현
- **예상 시간**: 20분
- **테스트**: 검색 결과에 스크립트 태그 포함 시도

### 7-9-9-2: Knowledge 메뉴 XSS 취약점 수정

- **파일**: `web/public/js/knowledge.js`
- **문제**: innerHTML 직접 사용
- **작업 내용**:
  1. 청크 목록 렌더링 부분 확인 (이미 `escapeHtml` 사용 중인지 확인)
  2. 미사용 부분 수정
  3. 청크 내용 표시 부분 안전성 검증
- **예상 시간**: 20분
- **테스트**: 청크 내용에 스크립트 태그 포함 시도

### 7-9-9-3: Reason 메뉴 XSS 취약점 수정

- **파일**: `web/public/js/reason.js`
- **문제**: innerHTML 직접 사용
- **작업 내용**:
  1. Reasoning 결과 표시 부분 확인
  2. `displayResults` 함수에서 안전한 렌더링 적용
  3. 컨텍스트 표시 부분 검토
- **예상 시간**: 25분
- **테스트**: Reasoning 결과에 스크립트 태그 포함 시도

### 7-9-9-4: Ask 메뉴 XSS 취약점 수정

- **파일**: `web/public/js/ask.js`
- **문제**: innerHTML 직접 사용
- **작업 내용**:
  1. AI 답변 표시 부분 확인
  2. 대화 기록 표시 부분 안전성 검증
  3. 마크다운 렌더링 안전 처리
- **예상 시간**: 25분
- **테스트**: AI 답변에 스크립트 태그 포함 시도

### 7-9-9-5: Logs 메뉴 XSS 취약점 수정

- **파일**: `web/public/js/logs.js`
- **문제**: innerHTML 직접 사용
- **작업 내용**:
  1. 로그 표시 부분 확인 (이미 `<script>` 태그 제거 로직 있음)
  2. 추가 안전성 강화
  3. Markdown 렌더링 부분 DOMPurify 적용 검토
- **예상 시간**: 20분
- **테스트**: 로그 내용에 스크립트 태그 포함 시도

---

## 🟡 우선순위 2: 긴 함수 분리 (Frontend)

### 7-9-9-6: Dashboard.js - loadDashboard 함수 분리

- **파일**: `web/public/js/dashboard.js`
- **문제**: `loadDashboard` 함수가 183줄 (너무 김)
- **작업 내용**:
  1. 함수 분석 및 책임 분리
  2. 하위 함수 추출:
     - `loadSystemStats()` - 시스템 통계 로드
     - `loadRecentActivities()` - 최근 활동 로드
     - `loadDocuments()` - 문서 목록 로드
     - `loadSystemStatus()` - 시스템 상태 로드
  3. 각 함수를 독립적으로 테스트 가능하도록 분리
- **예상 시간**: 1시간
- **테스트**: Dashboard 페이지 정상 동작 확인

### 7-9-9-7: Dashboard.js - 기타 긴 함수 분리

- **파일**: `web/public/js/dashboard.js`
- **문제**:
  - `loadAnalytics` (60줄)
  - `displayDocuments` (59줄)
  - `testVenvPackages` (73줄)
  - `testGpt4All` (82줄)
- **작업 내용**:
  1. 각 함수의 책임 분석
  2. 재사용 가능한 작은 함수로 분리
  3. 공통 로직은 유틸리티 함수로 추출
- **예상 시간**: 1.5시간
- **테스트**: 각 기능별 테스트

### 7-9-9-8: Knowledge.js - loadChunks 함수 분리

- **파일**: `web/public/js/knowledge.js`
- **문제**: `loadChunks` 함수가 140줄
- **작업 내용**:
  1. 청크 로딩 로직과 렌더링 로직 분리
  2. 하위 함수 추출:
     - `fetchChunks()` - API 호출
     - `renderChunkList()` - 청크 목록 렌더링
     - `setupChunkEventListeners()` - 이벤트 리스너 설정
- **예상 시간**: 45분
- **테스트**: Knowledge 페이지 정상 동작 확인

### 7-9-9-9: Reason.js - runReasoning 함수 분리

- **파일**: `web/public/js/reason.js`
- **문제**: `runReasoning` 함수가 104줄
- **작업 내용**:
  1. Reasoning 실행 로직과 결과 처리 분리
  2. 하위 함수 추출:
     - `prepareReasoningRequest()` - 요청 데이터 준비
     - `executeReasoning()` - API 호출
     - `processReasoningResult()` - 결과 처리
- **예상 시간**: 45분
- **테스트**: Reason 페이지 정상 동작 확인

### 7-9-9-10: Reason.js - displayResults 함수 분리

- **파일**: `web/public/js/reason.js`
- **문제**: `displayResults` 함수가 96줄
- **작업 내용**:
  1. 결과 표시 로직 분리
  2. 하위 함수 추출:
     - `renderSummary()` - 요약 표시
     - `renderConclusion()` - 결론 표시
     - `renderContext()` - 컨텍스트 표시
     - `renderSteps()` - 단계별 로그 표시
- **예상 시간**: 40분
- **테스트**: Reason 결과 표시 정상 동작 확인

### 7-9-9-11: Ask.js - askQuestion 함수 분리

- **파일**: `web/public/js/ask.js`
- **문제**: `askQuestion` 함수가 102줄
- **작업 내용**:
  1. 질의 처리 로직 분리
  2. 하위 함수 추출:
     - `prepareQuestionRequest()` - 요청 데이터 준비
     - `executeQuestion()` - API 호출
     - `displayAnswer()` - 답변 표시
     - `updateConversationHistory()` - 대화 기록 업데이트
- **예상 시간**: 45분
- **테스트**: Ask 페이지 정상 동작 확인

---

## 🟡 우선순위 2: 긴 함수 분리 (Backend)

### 7-9-9-12: Reason.py - reason 함수 분리

- **파일**: `backend/routers/reason.py`
- **문제**: `reason` 함수가 169줄
- **작업 내용**:
  1. 함수 분석 및 책임 분리
  2. 하위 함수 추출:
     - `prepare_reasoning_context()` - 컨텍스트 준비
     - `execute_reasoning()` - Reasoning 실행
     - `format_reasoning_result()` - 결과 포맷팅
  3. 각 함수를 독립적으로 테스트 가능하도록 분리
- **예상 시간**: 1시간
- **테스트**: Reason API 엔드포인트 테스트

### 7-9-9-13: AI.py - ask_question 함수 분리

- **파일**: `backend/routers/ai.py`
- **문제**: `ask_question` 함수가 219줄
- **작업 내용**:
  1. 질의 처리 로직 분리
  2. 하위 함수 추출:
     - `prepare_question_context()` - 컨텍스트 준비
     - `execute_ai_query()` - AI 질의 실행
     - `format_ai_response()` - 응답 포맷팅
     - `update_conversation_memory()` - 대화 메모리 업데이트
- **예상 시간**: 1.5시간
- **테스트**: Ask API 엔드포인트 테스트

---

## 🟢 우선순위 3: 공통 모듈 활용 및 리팩토링

### 7-9-9-14: Search.js - 공통 모듈 활용

- **파일**: `web/public/js/search.js`
- **문제**: 공통 모듈 미사용
- **작업 내용**:
  1. `utils.js`의 `escapeHtml` 함수 활용
  2. `text-formatter.js`의 마크다운 렌더링 함수 활용
  3. 중복 코드 제거
- **예상 시간**: 30분
- **테스트**: Search 페이지 정상 동작 확인

### 7-9-9-15: Knowledge.js - 공통 모듈 활용

- **파일**: `web/public/js/knowledge.js`
- **문제**: 공통 모듈 미사용
- **작업 내용**:
  1. `document-utils.js` 활용 검토
  2. `text-formatter.js` 활용
  3. 공통 렌더링 로직 추출
- **예상 시간**: 30분
- **테스트**: Knowledge 페이지 정상 동작 확인

### 7-9-9-16: Reason.js - 공통 모듈 활용

- **파일**: `web/public/js/reason.js`
- **문제**: 공통 모듈 미사용
- **작업 내용**:
  1. `text-formatter.js`의 마크다운 렌더링 활용
  2. 공통 UI 컴포넌트 활용
  3. 중복 코드 제거
- **예상 시간**: 30분
- **테스트**: Reason 페이지 정상 동작 확인

### 7-9-9-17: Ask.js - 공통 모듈 활용

- **파일**: `web/public/js/ask.js`
- **문제**: 공통 모듈 미사용
- **작업 내용**:
  1. `text-formatter.js` 활용
  2. 대화 기록 관리 공통 함수 추출
  3. 중복 코드 제거
- **예상 시간**: 30분
- **테스트**: Ask 페이지 정상 동작 확인

### 7-9-9-18: Logs.js - 공통 모듈 활용

- **파일**: `web/public/js/logs.js`
- **문제**: 공통 모듈 미사용
- **작업 내용**:
  1. `text-formatter.js`의 마크다운 렌더링 활용
  2. 로그 필터링 공통 함수 추출
  3. 중복 코드 제거
- **예상 시간**: 30분
- **테스트**: Logs 페이지 정상 동작 확인

### 7-9-9-19: Admin 메뉴들 - 공통 모듈 활용

- **파일**:
  - `web/public/js/admin-labels.js`
  - `web/public/js/admin-groups.js`
  - `web/public/js/admin-approval.js`
- **문제**: 공통 모듈 미사용
- **작업 내용**:
  1. `admin-common.js` 활용 강화
  2. 공통 UI 패턴 추출
  3. 중복 코드 제거
- **예상 시간**: 1시간
- **테스트**: 각 Admin 페이지 정상 동작 확인

---

## 🟢 우선순위 3: 중복 코드 제거

### 7-9-9-20: Dashboard.js - 중복 코드 제거

- **파일**: `web/public/js/dashboard.js`
- **문제**: 중복 코드 블록 발견
- **작업 내용**:
  1. 중복 코드 패턴 분석
  2. 공통 함수로 추출
  3. 모든 사용처 업데이트
- **예상 시간**: 30분
- **테스트**: Dashboard 페이지 정상 동작 확인

### 7-9-9-21: Dashboard.css - 중복 코드 제거

- **파일**: `web/public/css/dashboard.css`
- **문제**: 중복 스타일 블록 발견
- **작업 내용**:
  1. 중복 CSS 패턴 분석
  2. 공통 클래스로 추출
  3. 모든 사용처 업데이트
- **예상 시간**: 20분
- **테스트**: Dashboard 페이지 스타일 확인

---

## 🔵 우선순위 4: 복잡도 감소

### 7-9-9-22: Dashboard.js - 중첩 깊이 감소

- **파일**: `web/public/js/dashboard.js`
- **문제**: 최대 8단계 중첩
- **작업 내용**:
  1. 깊은 중첩 부분 식별
  2. Early return 패턴 적용
  3. Guard clause 패턴 적용
  4. 함수 분리로 중첩 감소
- **예상 시간**: 45분
- **테스트**: Dashboard 페이지 정상 동작 확인

### 7-9-9-23: Search.js - 중첩 깊이 감소

- **파일**: `web/public/js/search.js`
- **문제**: 최대 8단계 중첩
- **작업 내용**:
  1. 깊은 중첩 부분 식별
  2. Early return 패턴 적용
  3. 함수 분리
- **예상 시간**: 30분
- **테스트**: Search 페이지 정상 동작 확인

### 7-9-9-24: Knowledge.js - 중첩 깊이 감소

- **파일**: `web/public/js/knowledge.js`
- **문제**: 최대 8단계 중첩
- **작업 내용**:
  1. 깊은 중첩 부분 식별
  2. Early return 패턴 적용
  3. 함수 분리
- **예상 시간**: 30분
- **테스트**: Knowledge 페이지 정상 동작 확인

### 7-9-9-25: Reason.js - 중첩 깊이 감소

- **파일**: `web/public/js/reason.js`
- **문제**: 최대 8단계 중첩
- **작업 내용**:
  1. 깊은 중첩 부분 식별
  2. Early return 패턴 적용
  3. 함수 분리
- **예상 시간**: 30분
- **테스트**: Reason 페이지 정상 동작 확인

### 7-9-9-26: Ask.js - 중첩 깊이 감소

- **파일**: `web/public/js/ask.js`
- **문제**: 최대 9단계 중첩
- **작업 내용**:
  1. 깊은 중첩 부분 식별
  2. Early return 패턴 적용
  3. 함수 분리
- **예상 시간**: 30분
- **테스트**: Ask 페이지 정상 동작 확인

### 7-9-9-27: AI.py - 중첩 깊이 감소

- **파일**: `backend/routers/ai.py`
- **문제**: 최대 6단계 중첩
- **작업 내용**:
  1. 깊은 중첩 부분 식별
  2. Early return 패턴 적용
  3. 함수 분리
- **예상 시간**: 30분
- **테스트**: Ask API 엔드포인트 테스트

---

## 🔵 우선순위 4: 에러 처리 개선

### 7-9-9-28: Admin-approval.js - 비동기 에러 처리 개선

- **파일**: `web/public/js/admin-approval.js`
- **문제**: 비동기 함수의 에러 처리가 부족
- **작업 내용**:
  1. 모든 async 함수에 try-catch 추가
  2. 에러 메시지 사용자 친화적으로 표시
  3. 에러 로깅 추가
- **예상 시간**: 20분
- **테스트**: Admin Approval 페이지 에러 시나리오 테스트

---

## 🔵 우선순위 4: 코드 품질 개선

### 7-9-9-29: Dashboard.js - 매직 넘버 상수화

- **파일**: `web/public/js/dashboard.js`
- **문제**: 매직 넘버가 많음
- **작업 내용**:
  1. 매직 넘버 식별
  2. 상수로 정의 (파일 상단 또는 설정 객체)
  3. 모든 사용처 업데이트
- **예상 시간**: 20분
- **테스트**: Dashboard 페이지 정상 동작 확인

---

## ⚪ 우선순위 5: 문서화 개선

### 7-9-9-30: Dashboard.js - 주석 추가

- **파일**: `web/public/js/dashboard.js`
- **작업 내용**:
  1. 주요 함수에 JSDoc 주석 추가
  2. 복잡한 로직에 인라인 주석 추가
  3. 함수 파라미터와 반환값 문서화
- **예상 시간**: 30분

### 7-9-9-31: Search.js - 주석 추가

- **파일**: `web/public/js/search.js`
- **작업 내용**:
  1. 주요 함수에 JSDoc 주석 추가
  2. 복잡한 로직에 인라인 주석 추가
- **예상 시간**: 20분

### 7-9-9-32: Knowledge.js - 주석 추가

- **파일**: `web/public/js/knowledge.js`
- **작업 내용**:
  1. 주요 함수에 JSDoc 주석 추가
  2. 복잡한 로직에 인라인 주석 추가
- **예상 시간**: 20분

### 7-9-9-33: Reason.js - 주석 추가

- **파일**: `web/public/js/reason.js`
- **작업 내용**:
  1. 주요 함수에 JSDoc 주석 추가
  2. 복잡한 로직에 인라인 주석 추가
- **예상 시간**: 20분

### 7-9-9-34: Ask.js - 주석 추가

- **파일**: `web/public/js/ask.js`
- **작업 내용**:
  1. 주요 함수에 JSDoc 주석 추가
  2. 복잡한 로직에 인라인 주석 추가
- **예상 시간**: 20분

### 7-9-9-35: Logs.js - 주석 추가

- **파일**: `web/public/js/logs.js`
- **작업 내용**:
  1. 주요 함수에 JSDoc 주석 추가
  2. 복잡한 로직에 인라인 주석 추가
- **예상 시간**: 20분

### 7-9-9-36: Backend 라우터들 - 주석 추가

- **파일**:
  - `backend/routers/knowledge.py`
  - `backend/routers/reason.py`
  - `backend/routers/ai.py`
  - `backend/routers/labels.py`
  - `backend/routers/logs.py`
  - `backend/routers/approval.py`
- **작업 내용**:
  1. 주요 함수에 docstring 추가
  2. 복잡한 로직에 인라인 주석 추가
  3. API 엔드포인트 문서화
- **예상 시간**: 2시간

### 7-9-9-37: CSS 파일들 - 주석 추가

- **파일**: 모든 CSS 파일
- **작업 내용**:
  1. 주요 섹션에 주석 추가
  2. 복잡한 스타일 규칙 설명
- **예상 시간**: 1시간

---

## 📊 작업 통계

### 우선순위별 작업 수

- 🔴 우선순위 1 (보안): 6개
- 🟡 우선순위 2 (리팩토링): 14개
- 🟢 우선순위 3 (공통 모듈/중복 제거): 8개
- 🔵 우선순위 4 (복잡도/에러 처리): 9개
- ⚪ 우선순위 5 (문서화): 8개

### 예상 총 작업 시간

- 보안 수정: 약 2.5시간
- 리팩토링: 약 10시간
- 공통 모듈/중복 제거: 약 4시간
- 복잡도/에러 처리: 약 4시간
- 문서화: 약 5시간
- **총 예상 시간**: 약 25.5시간

---

## 🚀 실행 가이드

### 1단계: 보안 취약점 수정 (7-9-9-0 ~ 7-9-9-5)

가장 높은 우선순위로 모든 XSS 취약점을 먼저 수정합니다.

### 2단계: 긴 함수 분리 (7-9-9-6 ~ 7-9-9-13)

코드 가독성과 유지보수성을 위해 긴 함수를 분리합니다.

### 3단계: 공통 모듈 활용 (7-9-9-14 ~ 7-9-9-19)

중복 코드를 줄이고 재사용성을 높입니다.

### 4단계: 중복 코드 제거 (7-9-9-20 ~ 7-9-9-21)

중복된 코드 블록을 공통 함수로 추출합니다.

### 5단계: 복잡도 감소 (7-9-9-22 ~ 7-9-9-27)

깊은 중첩을 줄여 코드 가독성을 향상시킵니다.

### 6단계: 에러 처리 개선 (7-9-9-28)

비동기 함수의 에러 처리를 강화합니다.

### 7단계: 코드 품질 개선 (7-9-9-29)

매직 넘버를 상수로 정의합니다.

### 8단계: 문서화 (7-9-9-30 ~ 7-9-9-37)

코드 이해도를 높이기 위한 주석을 추가합니다.

---

## ✅ 체크리스트

각 작업 완료 시 체크:

- [ ] 7-9-9-0: Dashboard XSS 수정
- [ ] 7-9-9-1: Search XSS 수정
- [ ] 7-9-9-2: Knowledge XSS 수정
- [ ] 7-9-9-3: Reason XSS 수정
- [ ] 7-9-9-4: Ask XSS 수정
- [ ] 7-9-9-5: Logs XSS 수정
- [ ] 7-9-9-6: Dashboard.js loadDashboard 분리
- [ ] 7-9-9-7: Dashboard.js 기타 긴 함수 분리
- [ ] 7-9-9-8: Knowledge.js loadChunks 분리
- [ ] 7-9-9-9: Reason.js runReasoning 분리
- [ ] 7-9-9-10: Reason.js displayResults 분리
- [ ] 7-9-9-11: Ask.js askQuestion 분리
- [ ] 7-9-9-12: Reason.py reason 함수 분리
- [ ] 7-9-9-13: AI.py ask_question 함수 분리
- [ ] 7-9-9-14: Search.js 공통 모듈 활용
- [ ] 7-9-9-15: Knowledge.js 공통 모듈 활용
- [ ] 7-9-9-16: Reason.js 공통 모듈 활용
- [ ] 7-9-9-17: Ask.js 공통 모듈 활용
- [ ] 7-9-9-18: Logs.js 공통 모듈 활용
- [ ] 7-9-9-19: Admin 메뉴들 공통 모듈 활용
- [ ] 7-9-9-20: Dashboard.js 중복 코드 제거
- [ ] 7-9-9-21: Dashboard.css 중복 코드 제거
- [ ] 7-9-9-22: Dashboard.js 중첩 깊이 감소
- [ ] 7-9-9-23: Search.js 중첩 깊이 감소
- [ ] 7-9-9-24: Knowledge.js 중첩 깊이 감소
- [ ] 7-9-9-25: Reason.js 중첩 깊이 감소
- [ ] 7-9-9-26: Ask.js 중첩 깊이 감소
- [ ] 7-9-9-27: AI.py 중첩 깊이 감소
- [ ] 7-9-9-28: Admin-approval.js 에러 처리 개선
- [ ] 7-9-9-29: Dashboard.js 매직 넘버 상수화
- [ ] 7-9-9-30: Dashboard.js 주석 추가
- [ ] 7-9-9-31: Search.js 주석 추가
- [ ] 7-9-9-32: Knowledge.js 주석 추가
- [ ] 7-9-9-33: Reason.js 주석 추가
- [ ] 7-9-9-34: Ask.js 주석 추가
- [ ] 7-9-9-35: Logs.js 주석 추가
- [ ] 7-9-9-36: Backend 라우터들 주석 추가
- [ ] 7-9-9-37: CSS 파일들 주석 추가

---

## 📝 참고 사항

1. 각 작업은 독립적으로 실행 가능하도록 설계되었습니다.
2. 작업 순서는 우선순위에 따라 진행하되, 의존성이 있는 경우 순서를 조정할 수 있습니다.
3. 각 작업 완료 후 해당 기능의 정상 동작을 테스트해야 합니다.
4. 리팩토링 작업 시 기존 기능이 정상 동작하는지 반드시 확인해야 합니다.
5. 보안 취약점 수정은 가장 우선적으로 진행해야 합니다.
