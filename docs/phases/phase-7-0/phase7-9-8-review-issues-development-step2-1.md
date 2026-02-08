# Phase 7.9.8: 2단계 Step 2-1: 대화 기록 저장 상세 문서

**작성일**: 2026-01-10  
**상태**: ✅ 완료

---

## 📋 작업 개요

ask.js에 로컬 스토리지 기반 대화 기록 저장 기능을 추가하여 페이지 새로고침 후에도 대화 기록을 유지하고, 내보내기 및 삭제 기능 제공

---

## 🔧 수정된 파일

### 1. `web/src/pages/ask.html`

**변경 사항**:

대화 기록 헤더에 관리 버튼 추가:

```html
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
  <h2 style="margin: 0;">대화 기록</h2>
  <div style="display: flex; gap: 10px;">
    <button onclick="exportChatHistory('json')">📥 JSON 내보내기</button>
    <button onclick="exportChatHistory('markdown')">📥 Markdown 내보내기</button>
    <button onclick="clearChatHistory()">🗑️ 삭제</button>
  </div>
</div>
```

---

### 2. `web/public/js/ask.js`

**주요 변경 사항**:

#### 1. 상수 정의

```javascript
const CHAT_HISTORY_KEY = "ai_ask_chat_history";
const MAX_HISTORY_ITEMS = 50;
```

#### 2. 로컬 스토리지 로드 함수

```javascript
function loadChatHistoryFromStorage() {
  // 로컬 스토리지에서 JSON 파싱
  // 최대 개수 제한 적용
  // 대화 기록 표시
}
```

#### 3. 로컬 스토리지 저장 함수

```javascript
function saveChatHistoryToStorage() {
  // JSON.stringify로 저장
  // 용량 초과 시 오래된 항목 삭제
}
```

#### 4. 대화 기록 표시 함수

```javascript
function displayChatHistory() {
  // XSS 방지를 위한 이스케이프 처리
  // 최신순으로 표시 (reverse)
}
```

#### 5. 내보내기 함수

```javascript
function exportChatHistory(format) {
  // JSON 또는 Markdown 형식으로 변환
  // Blob 생성 및 다운로드
}
```

#### 6. 삭제 함수

```javascript
function clearChatHistory() {
  // 확인 다이얼로그
  // 로컬 스토리지에서 삭제
}
```

#### 7. 대화 기록 데이터 구조

```javascript
{
  question: string,
  answer: string,
  sources: array,
  timestamp: string (ISO format)
}
```

---

## 💾 저장 형식

### 로컬 스토리지

**키**: `ai_ask_chat_history`  
**값**: JSON 문자열 (배열)

```json
[
  {
    "question": "질문 내용",
    "answer": "답변 내용",
    "sources": [...],
    "timestamp": "2026-01-10T12:00:00.000Z"
  }
]
```

### 내보내기 형식

#### JSON 형식

```json
[
  {
    "question": "...",
    "answer": "...",
    "sources": [...],
    "timestamp": "..."
  }
]
```

#### Markdown 형식

```markdown
## 대화 1

**질문:**
질문 내용

**답변:**
답변 내용

**참고 문서:**

- 파일명 (유사도: 85.0%)

---
```

---

## ✅ 검증 완료

- ✅ 린터 오류 없음
- ✅ XSS 방지 (escapeHtml 사용)
- ✅ 로컬 스토리지 용량 초과 처리

---

## 🧪 테스트 계획

### 기능 테스트

1. **대화 기록 저장**

   - 질문 후 로컬 스토리지에 저장 확인
   - 브라우저 개발자 도구에서 확인

2. **대화 기록 복원**

   - 페이지 새로고침 후 대화 기록 유지 확인
   - 여러 대화 후 복원 확인

3. **JSON 내보내기**

   - 파일 다운로드 확인
   - JSON 형식 정확성 확인

4. **Markdown 내보내기**

   - 파일 다운로드 확인
   - Markdown 형식 정확성 확인

5. **대화 기록 삭제**

   - 확인 다이얼로그 표시 확인
   - 삭제 후 로컬 스토리지 비움 확인

6. **최대 개수 제한**

   - 50개 초과 시 오래된 항목 삭제 확인

7. **용량 초과 처리**
   - 로컬 스토리지 용량 초과 시 처리 확인

---

## 📝 다음 단계

3단계: 라벨 삭제 확인 진행 예정
