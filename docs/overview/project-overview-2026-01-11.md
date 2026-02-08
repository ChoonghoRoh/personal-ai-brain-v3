# Personal AI Brain v2 - 프로젝트 개요

**작성일**: 2026-01-11  
**최종 업데이트**: 2026-01-11 00:37:00

---

## 🎯 프로젝트 개요

**Personal AI Brain v2**는 로컬 환경에서 실행되는 개인 지식 관리 및 AI 추론 시스템입니다.

### 핵심 개념

- **벡터 기반 지식 저장**: 문서를 임베딩하여 의미 기반 검색 가능
- **AI 추론 시스템**: 컨텍스트 기반 추론 및 답변 생성
- **자동화 워크플로우**: 문서 수집, 임베딩, 라벨링 자동화
- **지식 구조화**: 라벨, 관계, 프로젝트 기반 지식 조직화

---

## 📊 시스템 아키텍처

### 기술 스택

**백엔드**:

- FastAPI (Python 웹 프레임워크)
- PostgreSQL (메타데이터 저장)
- Qdrant (벡터 데이터베이스)
- Sentence Transformers (임베딩 모델)
- GPT4All (로컬 LLM)

**프론트엔드**:

- Vanilla JavaScript
- HTML/CSS
- Jinja2 템플릿

**인프라**:

- Docker (Qdrant, PostgreSQL)
- Python 가상환경

---

## 🚀 주요 기능

### 1. 문서 관리

- **다양한 형식 지원**: Markdown, PDF, DOCX, Excel, PowerPoint, 이미지 OCR
- **자동 임베딩**: 문서를 벡터로 변환하여 Qdrant에 저장
- **의미 기반 검색**: 자연어 쿼리로 관련 문서 검색
- **캐싱 시스템**: 검색 결과 캐싱으로 성능 최적화

### 2. 지식 구조화

- **청크 단위 관리**: 문서를 의미 단위로 분할
- **라벨 시스템**: 키워드, 카테고리, 테마 기반 라벨링
- **관계 추론**: 청크 간 의미적 관계 자동 추론
- **프로젝트 조직**: 프로젝트별 지식 그룹화

### 3. AI 추론 시스템

- **맥락 이해**: 문서 간 의미적 연결 및 시간적 맥락 추적
- **기억 시스템**: 장기/단기/작업 기억으로 컨텍스트 유지
- **추론 체인**: 다단계 추론 과정 시각화
- **지식 통합**: 모순 감지 및 해결, 세계관 구성

### 4. 메타 인지

- **신뢰도 점수**: 라벨/관계 확인 상태 기반 신뢰도 계산
- **불확실성 표시**: 높음/중간/낮음 레벨 분류
- **학습 및 적응**: 사용자 패턴 학습 및 피드백 기반 개선

### 5. 자동화

- **자동 라벨링**: 키워드 기반 라벨 자동 추천
- **자동 관계 추론**: 유사도 기반 관계 제안
- **파일 변경 감지**: 자동 임베딩 갱신
- **Git 자동 커밋**: 변경사항 자동 기록

---

## 📈 개발 진행 상황

### Phase 8.0.0 (현재)

**완료된 작업**:

- ✅ 검색 성능 최적화 (캐싱, 페이징, 정렬)
- ✅ 임베딩 성능 최적화 (배치 처리)
- ✅ 데이터베이스 쿼리 최적화 (인덱스, N+1 해결)
- ✅ 맥락 이해 및 연결 강화
- ✅ 기억 시스템 구축
- ✅ 학습 및 적응 시스템
- ✅ 인격 유지 시스템
- ✅ 메타 인지 시스템
- ✅ 추론 체인 강화
- ✅ 지식 통합 및 세계관 구성
- ✅ 페이징 기능 추가
- ✅ 파일 형식 지원 확장
- ✅ 대화 기록 영구 저장
- ✅ 고급 검색 기능
- ✅ 정렬 옵션 추가
- ✅ 자동화 강화
- ✅ 백업 및 복원 시스템
- ✅ 데이터 무결성 보장
- ✅ 에러 처리 및 로깅 개선
- ✅ 보안 취약점 점검
- ✅ API 문서화 개선

**테스트 현황**:

- 총 테스트: 96개
- 성공: 88개 (91.7%)
- 실패: 8개 (우선순위 낮음)

---

## 📝 최근 작업 내역 (2026-01-07 ~ 2026-01-11)

### 2026-01-11

- ✅ Phase 8.0.0 API 테스트 완료
- ✅ 실패한 API 항목 수정
- ✅ 체크리스트 크로스 체크 테스트
- ✅ 에러 리포트 작성

### 2026-01-10

- ✅ Phase 7.9.7: 스크립트 분리 (14개 HTML → 19개 JS)
- ✅ Phase 7.9.8: CSS 분리 (600줄 인라인 CSS 제거)
- ✅ Phase 7.9.9: AI 질의 기능 개선
- ✅ Phase 7.9.10: keyword-group-manager.js 리팩토링

### 2026-01-09

- ✅ Phase 7.9.5: Chunk 제목 필드 추가
- ✅ Phase 7.9: GPT4All 추론적 답변 개선

### 2026-01-08

- ✅ Phase 7.8: Knowledge Admin 메뉴 분리

### 2026-01-07

- ✅ Phase 7 완료: Trustable Knowledge Pipeline 구축
- ✅ Phase 7.7: 키워드 그룹 및 카테고리 레이어

---

## 📊 프로젝트 통계

### 코드베이스 규모

- **Python 파일**: 약 50+ 개
- **JavaScript 파일**: 약 30+ 개
- **HTML 파일**: 약 15+ 개
- **API 엔드포인트**: 100+ 개

### 주요 모듈

**백엔드 라우터** (24개):

- search, system, documents, ai, logs, labels, relations, reason, knowledge
- approval, suggestions, context, memory, backup, integrity
- conversations, error_logs, reasoning_results, automation
- learning, personality, metacognition, reasoning_chain
- knowledge_integration, file_parser

**서비스** (12개):

- search_service, system_service, context_service, memory_service
- learning_service, personality_service, metacognition_service
- reasoning_chain_service, knowledge_integration_service
- automation_service, file_parser_service, integrity_service

---

## 🎯 시스템 특징

### 1. 성능 최적화

- **검색 캐싱**: 99.2% 성능 개선 (241ms → 2ms)
- **배치 임베딩**: 3-5배 성능 향상
- **데이터베이스 최적화**: N+1 쿼리 95% 감소

### 2. 지능형 기능

- **맥락 이해**: 의미적 유사도, 시간적 맥락, 클러스터링
- **기억 시스템**: 장기/단기/작업 기억 분리 관리
- **메타 인지**: 신뢰도 점수, 불확실성 표시
- **추론 체인**: 다단계 추론 과정 추적

### 3. 자동화

- **자동 라벨링**: 키워드 기반 라벨 추천
- **자동 관계 추론**: 유사도 기반 관계 제안
- **파일 변경 감지**: 자동 임베딩 갱신
- **Git 자동 커밋**: 변경사항 자동 기록

---

## 📚 관련 문서

- [Phase 8.0.0 최종 요약](./phase8-0-0-final-summary-report.md)
- [Phase 8.0.0 테스트 요약](./phase8-0-0-test-summary.md)
- [Phase 8.0.0 API 수정 리포트](./phase8-0-0-api-fix-report.md)
- [Phase 8.0.0 테스트 에러 리포트](./phase8-0-0-test-error-report-001.md)
- [작업 로그 요약](../../brain/system/work_log_summary.md)

---

**작성 완료**: 2026-01-11 00:37:00
