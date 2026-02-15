# Task 13-5-2: [BE] 토큰 관리 정밀화

**우선순위**: 13-5 내 2순위 (독립)
**예상 작업량**: 중대 (1.5일)
**의존성**: 없음 (ContextManager 독립 수정)
**상태**: TODO

**기반 문서**: `phase-13-5-todo-list.md`
**Plan**: `phase-13-5-plan.md`

---

## 1. 개요

### 1.1 현재 상태

토큰 수 계산이 `chars // 4` 근사치 의존. 한글 환경에서 오차가 크고, Context Window 초과(HTTP 400) 위험.

### 1.2 목표

tiktoken 또는 transformers Tokenizer를 도입하여 정확한 토큰 수를 계산하고, 모델별 최대 컨텍스트(4k~32k)에 맞춰 RAG 범위를 동적 조정한다.

---

## 2. 파일 변경 계획

| 파일 | 변경 내용 |
|------|----------|
| `requirements.txt` | tiktoken 또는 transformers 추가 |
| 토큰 계산 유틸리티 (신규 또는 기존 확장) | 모델별 토크나이저·토큰 수 계산 |
| ContextManager (해당 파일) | chars//4 → 정확 토큰 계산, 동적 조정 |

---

## 3. 작업 체크리스트

- [ ] 토크나이저 라이브러리 선택 (tiktoken 우선 — 경량)
- [ ] 의존성 추가
- [ ] 토큰 계산 유틸리티 구현
- [ ] ContextManager 한국어 친화 수정
- [ ] RAG 범위 동적 조정
- [ ] 회귀 확인

---

## 4. 참조

- Phase 13 Master Plan §L-2
