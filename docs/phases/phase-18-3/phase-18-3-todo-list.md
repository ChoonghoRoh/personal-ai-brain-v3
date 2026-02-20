# Phase 18-3 TODO List

## Task 18-3-1: 순차 진행 Step UI 컴포넌트
- [ ] Step 1~4 프레임 컴포넌트 생성 (reason-steps.js)
- [ ] Step 상태 관리 (pending/active/completed)
- [ ] reason.html에 Step 컨테이너 삽입
- [ ] 기존 progress-stages 영역과 통합

## Task 18-3-2: SSE → Step 전환 연동
- [ ] reason-control.js handleSSEEvent에서 Step 전환 호출
- [ ] stage 1→Step1, stage 2→Step2 매핑
- [ ] answer_token→Step3 활성화, done→Step4 표시
- [ ] 기존 updateProgressStage 연동 유지

## Task 18-3-3: 모드 예시 화면 삽입
- [ ] 4개 모드 × 예시 1건씩 정의
- [ ] 모드 select 변경 시 예시 표시
- [ ] 예시 컴포넌트 (reason-mode-examples.js)

## Task 18-3-4: CSS 재구성
- [ ] reason.css → reason-base.css + reason-form.css 분리
- [ ] reason-sections.css → reason-results.css + reason-actions.css 분리
- [ ] reason-steps.css 신규 생성
- [ ] reason.html link 태그 업데이트
- [ ] 시각적 동일성 확인

## Task 18-3-5: Step 2 중간 결과 미리보기
- [ ] answer_token을 Step 2 영역에 실시간 표시
- [ ] Step 3로 전환 시 전체 답변으로 교체
- [ ] BE 변경 필요 시 최소화

## Task 18-3-6: 세션 스레드 UI 개선
- [ ] Step 4 후속 작업 버튼 영역 통합
- [ ] 이어서 질문 / PDF / 공유 / 저장 → Step 4 내 배치
- [ ] continue-question-area 리팩토링
