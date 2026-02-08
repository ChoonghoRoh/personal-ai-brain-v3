# Phase 7.0: Reasoning UX & Knowledge Management 1차 개선 계획

🎯 Phase 7 목표

현재 시스템의 Reasoning 활용성과 지식 구조 관리 능력을 강화하여,
“엔진은 강력하지만 UX는 투박한 상태”에서
“실제로 쓰기 편하고, 이해 가능한 AI 브레인”으로 진화시키는 단계.

⸻

✅ 핵심 개선 범위

1️⃣ Reasoning 모드 개선

목표
지금의 combine / analyze / suggest 중심 구조를
사람이 직관적으로 이해 가능한 기능 단위 Reasoning 모드로 재정의한다.

개선 방향
• 각 모드에 “사람이 이해하기 쉬운 이름” 부여
• 화면에 용도 설명 제공
• 대표 프리셋 제공

예상 모드
• 설계/배경 설명 모드 (Design Explain)
• 리스크 분석 모드 (Risk Review)
• 다음 단계 제안 모드 (Next Steps)
• 히스토리/맥락 추적 모드 (History Trace)

2️⃣ Reasoning 결과 화면 개편

목표
“AI가 어떤 근거와 흐름으로 답을 만들었는지”를 사람이 이해할 수 있도록 구조화된 UI 제공

새 UI 구조
[결과 요약 (Result)]

- 최종 결론
- 몇 개 문서/지식을 참고했는지 요약

[컨텍스트 (Context)]

- 사용된 문서 목록
- 사용된 청크 목록
- 문서 열기 버튼 제공

[단계 로그 (Reasoning Steps)]

- 단계별 사고 과정 요약
- 추론 흐름 표시

필수 구현 요소
• 결과 / 컨텍스트 / 단계 로그 구분된 UI
• API 응답 구조 개선
• Reasoning Lab 페이지 반영

3️⃣ Knowledge Admin v0 구축

목표
지식 구조를 “조회만 가능한 시스템”에서
→ **“직접 관리 가능한 시스템”**으로 진화

기능 범위 (최소 버전 v0)

라벨 관리
• 라벨 리스트 조회
• 라벨 생성
• 라벨 삭제

청크 라벨 관리
• 특정 청크 선택
• 라벨 부여
• 라벨 제거

화면 경로
• /knowledge-admin

UI 방향
• 관리 UI (테이블 + 버튼)
• 복잡한 그래프 UI는 Phase 7 범위에서 제외

⸻

🔗 연동 영향도

Backend 영향
• Reasoning API 응답 구조 개선
• 라벨 CRUD 안정화
• 청크–라벨 매핑 API 사용

Frontend 영향
• /reason UI 개편
• /knowledge-admin 신규 페이지 추가

⸻

🧪 검증 기준 (Done Definition)

Reasoning UX
• Reasoning 모드의 의미가 직관적으로 이해 가능
• 결과가 단순 텍스트가 아닌 구조화된 정보로 제공
• 컨텍스트 확인 가능
• Reasoning 과정 이해 가능

⸻

Knowledge Admin
• 라벨 생성/삭제 정상 동작
• 청크에 라벨 부여/제거 가능
• Reasoning 반영 확인 가능

⸻

📅 예상 진행 순서

1️⃣ Reasoning 모드 UX 정리
2️⃣ Reasoning 결과 UI 구조화
3️⃣ Knowledge Admin v0 구축
4️⃣ 통합 테스트
5️⃣ 문서화 / 검증 시나리오 추가

⸻

📌 Phase 7 한 줄 정의

Phase 7의 목표는 Reasoning을 “이해 가능하고 신뢰 가능한 도구”로 만들고,
지식 구조를 “관리 가능한 자산”으로 끌어올리는 것이다.

⸻
