# Phase 7.7 Keyword Group Management - 추가 실행 항목

## 개선 완료 요약

### ✅ 완료된 개선 사항 (6개)

1. **시나리오 1**: 그룹 카드 색상 표시 개선 ✅
2. **시나리오 2**: 에러/성공 메시지 모달 내부 표시 개선 ✅
3. **시나리오 3**: 버튼 텍스트 변경 및 키워드 자동 연결 ✅
4. **시나리오 4**: 요약 바 그룹 이름 표시 개선 ✅
5. **시나리오 6**: 키워드 소속 그룹 표시 기능 추가 ✅
6. **헤더 렌더링**: 헤더 로드 문제 해결 ✅

---

## 추가 실행 필요 항목

### 🔴 우선순위 높음 (즉시 실행)

#### 1. 매칭 모드 작동 문제 해결 및 테스트

**상태**: ⚠️ 작동 확인 필요

**문제점**:

- 코드 로직은 구현되어 있으나 실제 작동 여부 확인 필요
- 사용자 테스트에서 작동하지 않는다고 보고됨

**실행 계획**:

**Step 1: 브라우저 테스트**

```
1. http://localhost:8000/knowledge-admin 접속
2. "📦 키워드 그룹" 탭 클릭
3. "매칭 모드" 체크박스 활성화
4. 다음 항목들을 순차적으로 테스트:
   - 매칭 모드 ON 시 그룹 카드 클릭 가능한지 확인
   - 그룹 카드 클릭 시 선택 상태(배경색 변경) 확인
   - 키워드 카드 클릭 시 선택 상태 확인
   - 여러 키워드 다중 선택 가능한지 확인
   - 하단 요약 바가 표시되는지 확인
   - 요약 바에 그룹 이름과 키워드 수가 표시되는지 확인
   - "이 그룹에 연결" 버튼 클릭 시 작동하는지 확인
   - 연결 후 키워드가 해당 그룹에 속하는지 확인
   - "선택 취소" 버튼 작동 확인
```

**Step 2: 문제 발견 시 디버깅**

- 브라우저 개발자 도구 콘솔 확인
- JavaScript 에러 확인
- `toggleMatchingMode`, `selectGroup`, `toggleKeywordSelection` 함수 동작 확인
- `updateMatchingUI` 함수 호출 확인

**Step 3: 수정 및 재테스트**

- 문제 발견 시 코드 수정
- 수정 후 재테스트

**예상 작업 시간**: 2-4시간

**참고 파일**:

- `web/src/pages/knowledge-admin.html` (1590-1677 라인)
- 관련 함수: `toggleMatchingMode`, `selectGroup`, `toggleKeywordSelection`, `updateMatchingUI`, `applyGroupKeywords`

---

### 🟡 우선순위 중간 (다음 스프린트)

#### 2. 키워드 추출 품질 개선

**상태**: ⚠️ 개선 필요

**문제점**:

- LLM으로 추천받은 키워드에 "을", "와" 등 조사가 섞여서 등록됨
- 단순 설명글의 단어를 조각 내어 등록되는 문제

**실행 계획**:

**Step 1: 백엔드 로직 개선**

```
1. scripts/extract_keywords_and_labels.py 수정
   - extract_keywords_with_gpt4all 함수 개선
   - 프롬프트에 조사 제거 요청 추가
   - 키워드 후처리 로직 추가 (조사 제거)

2. backend/routers/labels.py 수정
   - suggest_keywords_from_description 함수 개선
   - 추출된 키워드에서 조사 제거 로직 추가
   - 의미 분석 기반 키워드 추출 강화
```

**Step 2: 조사 제거 로직 구현**

```python
# 예시: 조사 제거 함수
def remove_postpositions(keyword: str) -> str:
    """한글 키워드에서 조사 제거"""
    postpositions = ['을', '를', '이', '가', '에', '에서', '와', '과', '의', '로', '으로']
    for post in postpositions:
        if keyword.endswith(post):
            return keyword[:-len(post)]
    return keyword
```

**Step 3: 테스트**

- 다양한 설명으로 키워드 추출 테스트
- 조사가 포함되지 않은 키워드만 추출되는지 확인

**예상 작업 시간**: 4-6시간

**참고 파일**:

- `scripts/extract_keywords_and_labels.py`
- `backend/routers/labels.py` (137-207 라인)

---

### 🟢 우선순위 낮음 (선택적 개선)

#### 3. 색상 선택 UI 개선

**상태**: ⚠️ 사용성 개선

**현재 상태**: 텍스트 입력으로 색상 코드 입력

**실행 계획**:

**옵션 1: 색상 선택 라이브러리 사용**

```
1. 색상 선택 라이브러리 검토
   - @simonwep/pickr
   - vanilla-picker
   - 또는 다른 라이브러리

2. 라이브러리 설치 및 통합
3. web/src/pages/knowledge-admin.html 수정
   - 색상 입력 필드를 색상 선택기로 교체
```

**옵션 2: 간단한 색상 팔레트 UI 직접 구현**

```
1. 미리 정의된 색상 팔레트 제공
2. 사용자가 클릭하여 선택
3. 과거 사용한 색상 재사용 기능 추가 (선택사항)
```

**예상 작업 시간**: 2-3시간

**참고 파일**: `web/src/pages/knowledge-admin.html` (798-802 라인)

---

#### 4. 매칭 모드 토글 디자인 개선

**상태**: ⚠️ UI/UX 개선

**현재 상태**: 체크박스 형태

**실행 계획**:

**Step 1: CSS 토글 스위치 스타일 구현**

```css
.toggle-switch {
  /* 토글 스위치 스타일 */
}
```

**Step 2: HTML 수정**

- 체크박스를 토글 스위치로 교체
- ON/OFF 상태 시각적 표시

**Step 3: JavaScript 수정**

- 토글 상태 변경 이벤트 처리

**예상 작업 시간**: 1-2시간

**참고 파일**: `web/src/pages/knowledge-admin.html` (685-688 라인)

---

## 실행 체크리스트

### 즉시 실행 (우선순위 높음)

- [ ] 매칭 모드 작동 문제 해결 및 테스트
  - [ ] 브라우저에서 매칭 모드 기능 테스트
  - [ ] 문제 발견 시 디버깅
  - [ ] 수정 후 재테스트
  - [ ] 테스트 결과 문서화

### 다음 스프린트 (우선순위 중간)

- [ ] 키워드 추출 품질 개선
  - [ ] 백엔드 로직 개선
  - [ ] 조사 제거 로직 구현
  - [ ] 테스트 및 검증

### 선택적 개선 (우선순위 낮음)

- [ ] 색상 선택 UI 개선
- [ ] 매칭 모드 토글 디자인 개선

---

## 참고 문서

- `docs/dev/phase7-7-keyword-group-user-test-guide.md`: 상세 테스트 가이드 및 개선 결과
- `docs/dev/phase7-7-improvements-summary.md`: 개선 사항 요약
- `docs/dev/phase7-7-keyword-group-test-results.md`: 코드 테스트 결과

---

## 업데이트 일자

2024년
