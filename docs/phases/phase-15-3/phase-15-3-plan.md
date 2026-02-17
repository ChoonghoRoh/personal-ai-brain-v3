# Phase 15-3 Plan: 지정 폴더 파일 Reasoning (UI/Backend/API)

**Phase**: 15-3
**작성일**: 2026-02-17
**상태**: G1 PASS

---

## 1. 목표

지식관리 지정 폴더 또는 선택한 파일(document_ids)에 대해 기존 Reasoning 엔진을 실행하고, 결과를 reasoning_results에 저장·표시하는 전용 API와 FE 진입점을 구현한다.

- `POST /api/reasoning/run-on-documents` — 지정 문서 대상 Reasoning 실행
- `GET /api/reasoning/run-on-documents/status/{task_id}` — 실행 진행 상황 조회
- `GET /api/reasoning/results-by-documents` — 문서별 Reasoning 결과 조회
- FE: 파일관리 화면에서 벌크 선택 + 모드 선택 모달 + Reasoning 실행

## 2. 범위

| 포함 | 제외 |
|------|------|
| 지정 문서 Reasoning 전용 API 3개 | 비동기 백그라운드 실행 (현재는 동기) |
| document_ids / folder_path 기반 트리거 | 폴더별 자동 스케줄링 |
| Reasoning 모드 선택 모달 (4대 모드) | 새 Reasoning 모드 추가 |
| 파일관리 UI 벌크 선택 체크박스 | /reason 페이지 직접 수정 |
| 기존 reason_store 재사용 결과 저장 | 별도 결과 테이블 신규 생성 |

## 3. 설계 결정

| 결정 | 선택 | 근거 |
|------|------|------|
| API 경로 | `/api/reasoning/run-on-documents` | 기존 `/api/reason` 과 분리, 마스터 플랜 §5.2 준수 |
| 실행 방식 | 동기 (추후 비동기 확장 가능) | 초기 구현 단순화, SSE 스트리밍은 기존 `/api/reason/stream` 활용 |
| 결과 저장 | ReasoningResult 테이블 + recommendations.document_ids 필드 | 기존 인프라 재활용, 문서별 결과 필터링 가능 |
| FE 진입점 | 파일관리 화면 체크박스 + 모달 | 사용자 동선: 파일 탐색 → 선택 → Reasoning → 결과 확인 |
| 청크 수집 | 기존 collect_chunks_by_document_ids 재사용 | reason.py에 이미 구현 완료 (Phase 15-3 표기) |

## 4. 리스크

| 리스크 | 영향 | 대응 |
|--------|------|------|
| 대용량 문서 다수 선택 시 응답 지연 | 중 | 청크 20개 제한 + LLM 500 토큰 제한 |
| 동기 실행 시 타임아웃 | 중 | 문서 수 제한 경고 + 추후 비동기 확장 |
| folder_path 매칭 실패 | 저 | file_path LIKE 패턴 + 404 에러 반환 |

## 5. 참조

- `docs/phases/phase-15-master-plan.md` §5 — Phase 15-3 인터페이스 정의
- `backend/routers/reasoning/reason_document.py` — 전용 라우터 (15-3-1 산출물)
- `backend/routers/reasoning/reason.py` — collect_chunks_by_document_ids 등 기존 함수
- `web/public/js/admin/knowledge-files.js` — 벌크 Reasoning UI (15-3-3, 15-3-4 산출물)
