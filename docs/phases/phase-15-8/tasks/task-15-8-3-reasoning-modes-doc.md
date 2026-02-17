# Task 15-8-3: 4대 추론 모드 및 Re-ranking, 하이브리드 검색 정리

**우선순위**: 15-8 내 3순위
**의존성**: 없음
**담당 팀원**: backend-dev
**상태**: DONE

---

## §1. 개요

PAB 시스템의 4대 추론 모드(design_explain, risk_review, next_steps, history_trace)와 검색 고도화 전략(Re-ranking, 하이브리드 검색), 캐싱/양자화 정책을 체계적으로 정리한 운영 참조 문서를 작성한다.

## §2. 파일 변경 계획

| 파일 | 유형 | 변경 내용 |
|------|------|----------|
| `docs/phases/phase-15-8/reasoning-modes.md` | 신규 | 4대 추론 모드 + 검색 고도화 + 캐싱/양자화 정책 문서 |

## §3. 작업 체크리스트 (Done Definition)

### 4대 추론 모드 정리
- [x] **design_explain** (설계 설명)
  - 용도: 시스템/컴포넌트 설계 원리 설명, 아키텍처 다이어그램 생성
  - 프롬프트 전략: 구조 분석 + Mermaid 시각화 지시
  - 출력: 설계 설명 텍스트 + Mermaid 다이어그램 코드
- [x] **risk_review** (리스크 검토)
  - 용도: 프로젝트/기술 리스크 식별 및 영향도 평가
  - 프롬프트 전략: 리스크 매트릭스 + 대응 전략
  - 출력: 리스크 항목 테이블 (영향/확률/대응)
- [x] **next_steps** (후속 절차)
  - 용도: 현재 상태 기반 다음 단계 로드맵 생성
  - 프롬프트 전략: 현재 진행 상황 분석 + 우선순위 도출
  - 출력: 단계별 액션 항목 + 타임라인
- [x] **history_trace** (이력 추적)
  - 용도: 의사결정/변경 이력 추적 및 타임라인 생성
  - 프롬프트 전략: 시간순 이벤트 추출 + 인과 관계 분석
  - 출력: 타임라인 목록 + 변경 근거

### 검색 고도화 전략
- [x] **Re-ranking** (Cross-Encoder) 정리
  - 1차 검색 (Bi-Encoder) -> 2차 재순위 (Cross-Encoder)
  - 정확도 목표: 85% -> 95%
  - 지원 모델 및 fallback 전략
- [x] **하이브리드 검색** (Sparse + Dense) 정리
  - Sparse: BM25 기반 키워드 매칭 (고유명사, 약어 대응)
  - Dense: 벡터 유사도 (의미 검색)
  - 결합 전략: Reciprocal Rank Fusion (RRF)

### 캐싱/양자화 정책
- [x] Redis 캐시 정책 (TTL, 무효화, 키 전략)
- [x] Qdrant 양자화 정책 (Scalar, 메모리/정확도 트레이드오프)
- [x] 성능 목표 수치 기록

## §4. 참조

- `docs/phases/phase-15-master-plan.md` -- SS2.3.4 Reasoning 고도화
- `backend/routers/reasoning/` -- Reasoning API 라우터
- `backend/services/search/search_service.py` -- 검색 서비스
- `backend/services/ai/qdrant_client.py` -- Qdrant 클라이언트
- `backend/config.py` -- Redis/Qdrant 설정
