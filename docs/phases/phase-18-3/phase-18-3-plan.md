# Phase 18-3 Plan: Reasoning 페이지 리뉴얼

## 목표
Reasoning 페이지에 순차 진행 Step UI 추가, SSE 이벤트 매핑, 모드 예시 화면, CSS 재구성, 중간 결과 미리보기, 세션 스레드 개선.

## Task 구조

| Task | 내용 | 도메인 | 의존성 |
|------|------|--------|--------|
| 18-3-1 | 순차 진행 Step UI 컴포넌트 | [FE] | 없음 |
| 18-3-2 | SSE 이벤트 → Step 전환 연동 | [FE] | 18-3-1 |
| 18-3-3 | 모드 선택 시 예시 화면 삽입 | [FE] | 없음 |
| 18-3-4 | CSS 재구성 (reason.css + reason-sections.css 분리) | [FE] | 18-3-1 |
| 18-3-5 | Step 2 중간 결과 미리보기 | [FE][BE] | 18-3-2 |
| 18-3-6 | 세션 스레드 UI 개선 | [FE] | 18-3-1 |

## 실행 계획
1. 18-3-1, 18-3-3 병행 (독립)
2. 18-3-1 완료 후 → 18-3-2, 18-3-4, 18-3-6 병행
3. 18-3-2 완료 후 → 18-3-5
4. 전체 완료 → G2/G3 검증

## CSS 재구성 목표
```
현재:
  reason.css (607줄)           ← 혼재
  reason-sections.css (597줄)  ← 혼재

TO-BE:
  reason-base.css (~200줄)      ← 변수, 테마, 접근성
  reason-form.css (~150줄)      ← 입력 폼, 모드 선택
  reason-steps.css (~200줄)     ← Step 1~4 순차 진행 (신규)
  reason-results.css (~200줄)   ← 결과 표시, 시각화, 탭
  reason-actions.css (~100줄)   ← 세션, 히스토리, 모달
  reason-advanced.css (유지)    ← 모드별 시각화 전용
```

## 위험 요소
- CSS 분리 시 기존 스타일 깨짐 주의
- SSE 이벤트 타입 변경 없이 FE Step 매핑만 수행
- BE 변경 최소화 (18-3-5에서만 필요 시)
