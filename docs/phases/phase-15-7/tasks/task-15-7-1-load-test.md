# Task 15-7-1: 전체 시스템 부하 테스트 및 메모리 누수 점검

**우선순위**: 15-7 내 1순위
**의존성**: 15-1~15-6 주요 기능 완료
**담당 팀원**: backend-dev
**상태**: DONE

---

## §1. 개요

전체 시스템의 안정성을 검증하기 위해 비동기 부하 테스트 스크립트를 작성하고, 메모리 누수 점검 가이드를 마련한다. 주요 API 엔드포인트에 동시 요청을 발생시켜 목표 RPS와 지연 시간을 확인하며, tracemalloc을 활용한 메모리 프로파일링으로 장기 운영 시 누수 가능성을 점검한다.

## §2. 파일 변경 계획

| 파일 | 유형 | 변경 내용 |
|------|------|----------|
| `scripts/tests/load_test.py` | 신규 | aiohttp 기반 비동기 부하 테스트 스크립트 |

## §3. 작업 체크리스트 (Done Definition)

### 부하 테스트 스크립트
- [x] aiohttp + asyncio 기반 비동기 HTTP 클라이언트
- [x] 엔드포인트별 시나리오 정의
  - `/api/health` -- 기본 헬스체크
  - `/api/knowledge/folder-files` -- 지식 파일 목록
  - `/api/reason/*` -- Reasoning API
  - `/api/automation/tasks` -- 자동화 태스크 목록
- [x] 동시 요청 수 설정 (10, 20, 50 concurrent)
- [x] 측정 항목: 총 요청 수, 성공/실패, 평균 응답 시간, P95, P99, RPS
- [x] 결과 콘솔 출력 + JSON 저장

### 메모리 누수 점검
- [x] tracemalloc 기반 메모리 스냅샷 비교 가이드
- [x] 반복 요청(1000회+) 후 메모리 증가 패턴 확인 방법
- [x] 메모리 점검 시나리오: SSE 연결 반복 열기/닫기, 대용량 파일 파싱, 검색 반복

### 검증 기준
- [x] 목표 RPS: /api/health 100+, /api/reason 10+
- [x] P95 지연 시간: 일반 API 500ms 이내, Reasoning API 5s 이내
- [x] 에러율: 1% 미만
- [x] 메모리 증가: 1000회 반복 후 50MB 이내 증가

## §4. 참조

- `docs/phases/phase-15-7/operations-checklist.md` -- 부하 테스트 결과 기록 섹션
- `backend/main.py` -- 헬스체크 엔드포인트
- `backend/routers/reasoning/reason_stream.py` -- SSE 스트리밍 패턴
