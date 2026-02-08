# Task 10-2-1: design_explain 시각화 (Mermaid)

**우선순위**: 10-2 내 1순위  
**예상 작업량**: 2일  
**의존성**: Phase 10-1 완료 후 권장  
**상태**: ✅ 완료

**기반 문서**: [phase-10-2-0-todo-list.md](../phase-10-2-0-todo-list.md)  
**작업 순서**: [phase-10-navigation.md](../../phase-10-navigation.md)

---

## 1. 개요

### 1.1 목표

Reasoning **design_explain** 모드의 설계 분석 결과를 **Mermaid 다이어그램**으로 시각화한다.

### 1.2 시각화 대상

| 유형                | 내용                    |
| ------------------- | ----------------------- |
| 아키텍처 다이어그램 | 설계 구조·컴포넌트 관계 |
| 의존성 그래프       | 모듈·서비스 간 의존성   |

### 1.3 라이브러리

- **Mermaid.js**

---

## 2. 파일 변경 계획

### 2.1 신규/수정

| 파일 경로                                  | 용도                                 |
| ------------------------------------------ | ------------------------------------ |
| 프론트엔드: Mermaid 연동 스크립트·컴포넌트 | design_explain 결과 → Mermaid 렌더링 |
| `web/src/pages/reason.html` (또는 해당 뷰) | design_explain 시각화 영역 추가      |
| (선택) 백엔드 또는 프론트 파서             | LLM 응답 → Mermaid 문법 변환         |

---

## 3. 작업 체크리스트

### 3.1 도입·연동

- [ ] Mermaid.js 도입 및 Reasoning 결과 영역에 연동
- [ ] design_explain 결과 전용 표시 영역 추가

### 3.2 변환 로직

- [ ] 설계 분석 결과 → Mermaid 문법 변환 로직 (파서 또는 LLM 후처리)
- [ ] 아키텍처 다이어그램, 의존성 그래프 등 차트 타입 지원

### 3.3 UI

- [ ] `reason.html`(또는 해당 뷰)에 design_explain 결과 시각화 영역 추가
- [ ] 모드가 design_explain일 때만 해당 영역 표시

---

## 4. 참고 문서

- [Phase 10-2 Plan](../phase-10-2-0-plan.md)
- [Phase 10-2 Todo List](../phase-10-2-0-todo-list.md)
- [Phase 10 Master Plan](../../phase-10-master-plan.md) 부록 A — Mermaid.js
- Reasoning API: `backend/routers/reasoning/reason.py` (mode=design_explain)
