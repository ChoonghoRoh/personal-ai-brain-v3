# Task 10-2-3: next_steps 로드맵

**우선순위**: 10-2 내 3순위  
**예상 작업량**: 2일  
**의존성**: Phase 10-1 완료 후 권장  
**상태**: ✅ 완료

**기반 문서**: [phase-10-2-0-todo-list.md](../phase-10-2-0-todo-list.md)  
**작업 순서**: [phase-10-navigation.md](../../phase-10-navigation.md)

---

## 1. 개요

### 1.1 목표

Reasoning **next_steps** 모드의 다음 단계 제안을 **Phase별 로드맵**(간트·칸반 등)으로 시각화한다.

### 1.2 시각화 대상

| 유형      | 내용                 |
| --------- | -------------------- |
| 간트 차트 | 일정·단계별 타임라인 |
| 칸반 보드 | 단계별 카드 배치     |

### 1.3 라이브러리

- **Gantt.js** 또는 **Custom** 컴포넌트

---

## 2. 파일 변경 계획

### 2.1 신규/수정

| 파일 경로                                  | 용도                             |
| ------------------------------------------ | -------------------------------- |
| 프론트엔드: Gantt/Custom 컴포넌트          | next_steps 결과 → 로드맵 렌더링  |
| `web/src/pages/reason.html` (또는 해당 뷰) | next_steps 시각화 영역 추가      |
| (선택) 파서                                | LLM 응답 → 일정/단계 데이터 변환 |

---

## 3. 작업 체크리스트

### 3.1 도입·연동

- [ ] Gantt.js 또는 Custom 컴포넌트로 Phase별 로드맵 구현
- [ ] next_steps 결과 전용 표시 영역 추가

### 3.2 데이터·시각화

- [ ] next_steps 결과 → 일정/단계 데이터 변환
- [ ] 간트 차트 또는 칸반 보드 형태 표시

### 3.3 UI

- [ ] Reasoning 페이지에 next_steps 시각화 영역 추가
- [ ] 모드가 next_steps일 때만 해당 영역 표시

---

## 4. 참고 문서

- [Phase 10-2 Plan](../phase-10-2-0-plan.md)
- [Phase 10-2 Todo List](../phase-10-2-0-todo-list.md)
- [Phase 10 Master Plan](../../phase-10-master-plan.md) 부록 A — Gantt.js
- Reasoning API: `backend/routers/reasoning/reason.py` (mode=next_steps)
