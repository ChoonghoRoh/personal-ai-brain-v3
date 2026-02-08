# Task 10-2-4: history_trace 타임라인

**우선순위**: 10-2 내 4순위  
**예상 작업량**: 2일  
**의존성**: Phase 10-1 완료 후 권장  
**상태**: ✅ 완료

**기반 문서**: [phase-10-2-0-todo-list.md](../phase-10-2-0-todo-list.md)  
**작업 순서**: [phase-10-navigation.md](../../phase-10-navigation.md)

---

## 1. 개요

### 1.1 목표

Reasoning **history_trace** 모드의 의사결정 히스토리를 **타임라인**으로 시각화한다.

### 1.2 시각화 대상

| 유형              | 내용                       |
| ----------------- | -------------------------- |
| 수직 타임라인     | 이벤트·결정 시점 순서 표시 |
| Before/After 비교 | (선택) 변경 전후 비교      |

### 1.3 라이브러리

- **Timeline.js** (또는 동등)

---

## 2. 파일 변경 계획

### 2.1 신규/수정

| 파일 경로                                  | 용도                                   |
| ------------------------------------------ | -------------------------------------- |
| 프론트엔드: Timeline.js 연동·컴포넌트      | history_trace 결과 → 타임라인 렌더링   |
| `web/src/pages/reason.html` (또는 해당 뷰) | history_trace 시각화 영역 추가         |
| (선택) 파서                                | LLM 응답 → 타임라인 이벤트 데이터 변환 |

---

## 3. 작업 체크리스트

### 3.1 도입·연동

- [ ] Timeline.js(또는 동등) 도입
- [ ] history_trace 결과 전용 표시 영역 추가

### 3.2 데이터·시각화

- [ ] history_trace 결과 → 타임라인 이벤트 데이터 변환
- [ ] 수직 타임라인 표시
- [ ] Before/After 비교(선택) 구현

### 3.3 UI

- [ ] Reasoning 페이지에 history_trace 시각화 영역 추가
- [ ] 모드가 history_trace일 때만 해당 영역 표시

---

## 4. 참고 문서

- [Phase 10-2 Plan](../phase-10-2-0-plan.md)
- [Phase 10-2 Todo List](../phase-10-2-0-todo-list.md)
- [Phase 10 Master Plan](../../phase-10-master-plan.md) 부록 A — Timeline.js
- Reasoning API: `backend/routers/reasoning/reason.py` (mode=history_trace)
