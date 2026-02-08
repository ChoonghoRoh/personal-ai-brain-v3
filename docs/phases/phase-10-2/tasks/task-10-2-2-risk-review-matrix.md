# Task 10-2-2: risk_review 매트릭스

**우선순위**: 10-2 내 2순위  
**예상 작업량**: 2일  
**의존성**: Phase 10-1 완료 후 권장  
**상태**: ✅ 완료

**기반 문서**: [phase-10-2-0-todo-list.md](../phase-10-2-0-todo-list.md)  
**작업 순서**: [phase-10-navigation.md](../../phase-10-navigation.md)

---

## 1. 개요

### 1.1 목표

Reasoning **risk_review** 모드의 리스크 분석 결과를 **심각도/가능성 매트릭스**로 시각화한다.

### 1.2 시각화 대상

| 유형                | 내용                       |
| ------------------- | -------------------------- |
| 5x5 리스크 매트릭스 | 심각도(축) × 가능성(축)    |
| 영향 그래프         | (선택) 리스크 간 영향 관계 |

### 1.3 라이브러리

- **Chart.js** (또는 동등)

---

## 2. 파일 변경 계획

### 2.1 신규/수정

| 파일 경로                                  | 용도                                      |
| ------------------------------------------ | ----------------------------------------- |
| 프론트엔드: Chart.js 연동·컴포넌트         | risk_review 결과 → 매트릭스/그래프 렌더링 |
| `web/src/pages/reason.html` (또는 해당 뷰) | risk_review 시각화 영역 추가              |
| (선택) 파서                                | LLM 응답 → 심각도/가능성 데이터 변환      |

---

## 3. 작업 체크리스트

### 3.1 도입·연동

- [ ] Chart.js(또는 동등) 도입
- [ ] risk_review 결과 전용 표시 영역 추가

### 3.2 데이터·시각화

- [ ] risk_review 결과 → 심각도/가능성 매트릭스 데이터 변환
- [ ] 5x5 리스크 매트릭스 시각화
- [ ] 영향 그래프(선택) 구현

### 3.3 UI

- [ ] Reasoning 페이지에 risk_review 시각화 영역 추가
- [ ] 모드가 risk_review일 때만 해당 영역 표시

---

## 4. 참고 문서

- [Phase 10-2 Plan](../phase-10-2-0-plan.md)
- [Phase 10-2 Todo List](../phase-10-2-0-todo-list.md)
- [Phase 10 Master Plan](../../phase-10-master-plan.md) 부록 A — Chart.js
- Reasoning API: `backend/routers/reasoning/reason.py` (mode=risk_review)
