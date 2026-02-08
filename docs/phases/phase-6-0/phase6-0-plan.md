# Phase 6.0: Personal AI Brain – 실행 전략 문서

Knowledge & Reasoning Front 서비스 핵심 구축 요약
🎯 목적

Phase 5에서 구축된 지식 구조(라벨 + 관계) & Reasoning Pipeline을
웹 UI에서 직접 확인·활용 가능한 서비스로 제공한다.

✅ 반드시 구축해야 하는 핵심 기능
1️⃣ Knowledge Studio (/knowledge)

지식 구조 탐색 UI

필수 요소

라벨 필터 & 리스트

라벨 선택 시 해당 청크 목록 표시

청크 선택 시:

본문 표시

연결 라벨 표시

관계(in/out) 표시

“이 청크로 Reasoning 시작” 버튼

필수 API

GET /api/labels

GET /api/knowledge/chunks?label_id=...

GET /api/knowledge/chunks/{id}

2️⃣ Reasoning Lab (/reason)

Reasoning Pipeline 실행 및 시각화 화면

필수 요소

질문 입력

Reasoning 모드 선택 (combine / analyze / suggest)

프로젝트·라벨 등 필터 선택

실행 버튼

결과 UI

최종 답변

사용된 컨텍스트 청크 목록

관계 목록

Reasoning 단계 로그

필수 API

POST /api/reason

🔗 화면 연결 흐름 (필수)
Document Viewer

“지식 구조 보기” → /knowledge?chunk_id=...

“이 청크로 Reasoning” → /reason?seed_chunk=...

Dashboard

메뉴에 추가

Knowledge

Reason

Reasoning Quick Start 간단 카드

🏗️ 구현 변경 범위 (최소 단위)
Front

knowledge.html 신규

reason.html 신규

dashboard.html 네비게이션 및 연결 버튼 추가

Backend

labels API 보완

knowledge chunks 조회 API 제공

relations 조회 API 제공

reasoning API 응답 구조 정리

✅ 완료 기준 (Done)

/knowledge 정상 탐색 가능

/reason 정상 Reasoning 실행 및 시각화

문서 ↔ 지식 ↔ Reasoning 연결 UX 확보

기본 오류 처리 및 안정성 확보

📌 가장 중요한 한 줄 요약

지식 구조를 “보이게” 만들고, Reasoning 과정을 “이해 가능하게” 만드는 UI 구축이 Phase 6의 핵심이다.
