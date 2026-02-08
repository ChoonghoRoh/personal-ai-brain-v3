# Task 10-3-3: PDF 내보내기

**우선순위**: 10-3 내 3순위  
**예상 작업량**: 1.5일  
**의존성**: 10-3-2  
**상태**: ✅ 완료

**기반 문서**: [phase-10-3-0-todo-list.md](../phase-10-3-0-todo-list.md)  
**작업 순서**: [phase-10-navigation.md](../../phase-10-navigation.md)

---

## 1. 개요

### 1.1 목표

Reasoning **결과 영역을 PDF로 내보내기** 기능을 구현한다. 사용자가 분석 결과를 PDF 파일로 저장·공유할 수 있도록 한다.

### 1.2 라이브러리

- **jsPDF**, **html2canvas** (또는 동등)

---

## 2. 파일 변경 계획

### 2.1 신규/수정

| 파일 경로                              | 용도                          |
| -------------------------------------- | ----------------------------- |
| 프론트엔드: PDF 생성 스크립트·컴포넌트 | 결과 영역 캡처 → PDF 생성     |
| Reasoning 페이지                       | "PDF 내보내기" 버튼·동작 연동 |

---

## 3. 작업 체크리스트

### 3.1 도입·구현

- [ ] jsPDF, html2canvas(또는 동등) 도입
- [ ] Reasoning 결과 영역을 PDF로 내보내기 버튼·동작 구현
  - [ ] 결과 DOM 영역 캡처 (html2canvas 등)
  - [ ] PDF 생성·다운로드

### 3.2 품질

- [ ] 레이아웃·한글 등 출력 품질 확인
- [ ] 시각화(차트·다이어그램)가 PDF에 포함되는지 검증

---

## 4. 참고 문서

- [Phase 10-3 Plan](../phase-10-3-0-plan.md)
- [Phase 10-3 Todo List](../phase-10-3-0-todo-list.md)
- [Phase 10 Master Plan](../../phase-10-master-plan.md) 부록 A — jsPDF, html2canvas
- [Task 10-3-2 시각화 라이브러리](task-10-3-2-viz-library.md)
