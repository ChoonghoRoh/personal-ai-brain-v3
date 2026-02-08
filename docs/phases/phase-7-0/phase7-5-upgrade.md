# Phase 7.5: Upgrade Proposal

🎯 목표

Phase 7를 “Reasoning 가능한 플랫폼”에서 “지식을 안정적으로 축적·관리·확장하는 AI Knowledge System” 으로 업그레이드한다.

핵심 방향은 다음과 같다.
• AI가 초안(Draft)을 만들고, 관리자가 승인(Approve)하는 Trustable Knowledge Pipeline 구축
• 라벨·관계·유사도 추천을 자동화하여 관리자의 작업 부담 최소화
• Reasoning이 사용하는 지식을 승인된 지식으로만 제한하여 품질 보장

⸻

✅ 주요 변화 요약

1️⃣ 청크 관리 구조 변경

단계 상태 설명
초안 생성 draft AI가 자동 생성
관리자 검토 draft → approved or rejected UI에서 승인/거절
운영 사용 approved Reasoning 기본 사용 대상

⸻

2️⃣ AI Assisted Knowledge 관리 기능 추가

✔️ AI 라벨 추천 기능
• 청크 텍스트 기반 자동 라벨 제안
• confidence 점수 포함
• 관리자가 확인 후 채택 → confirmed

✔️ AI 관계/유사도 추천 기능
• 임베딩 기반 유사 청크 추천
• 관계 생성 후보 점선 상태로 표시
• 관리자가 확정하면 실선으로 전환

⸻

🧩 데이터 구조 확장

📌 knowledge_chunks

id
document_id
text
status (draft / approved / rejected)
source (ai_generated / human_created)
approved_at
approved_by
created_at
updated_at
version

⸻

📌 chunk_labels

chunk_id
label_id
status (suggested / confirmed / rejected)
source (ai / human)
confidence (float)

⸻

📌 chunk_relations

source_chunk_id
target_chunk_id
relation_type (similar / cause_effect / etc)
score
confirmed (bool)
source (ai / human)

⸻

🖥️ UI 업그레이드 방향

Knowledge Admin
• Chunk Approval Center 신설
• 상태별 필터 (draft / approved / rejected)
• 각 청크 상세 화면에서:
• AI 추천 라벨 블록
• 유사 청크 블록
• [Approve] [Reject] 버튼

Knowledge Studio Graph
• 확정 관계 → 실선
• AI 제안 관계 → 점선 + 승인/거절 가능

⸻

🔌 API 확장 계획

/api/knowledge/chunks/approve
• 청크 승인 처리

/api/knowledge/chunks/reject
• 초안 거절 처리

/api/knowledge/labels/suggest
• 청크 기반 자동 라벨 추천

/api/knowledge/relations/suggest
• 유사도 기반 관계 추천

⸻

🧪 테스트 전략

1️⃣ 데이터 없는 상태 정상 작동 확인 (이미 완료 패턴 유지)
2️⃣ Draft → Approval workflow end-to-end 테스트
3️⃣ 승인된 지식만 Reasoning 사용하는지 확인
4️⃣ AI Suggestion 품질 검증 (테스트 데이터 활용)

⸻

🚀 결과 기대 효과
• 사람이 일일이 태깅하지 않아도 되는 반자동 Knowledge System 완성
• 관리자가 신뢰할 수 있는 승인 기반 지식 운영 구조 확보
• Phase 8+ 확장(지식 클러스터링 / 온톨로지 / 지식 그래프 고도화) 기반 마련

⸻

📌 다음 단계 실행 계획
• DB 스키마 확장
• Admin UI Approval Center 추가
• AI Suggestion Backend 활성화
• Graph 점선 제안 기능 적용
• Phase 7.5 통합 테스트 진행
