# Phase 15-4 Plan: DB 샘플 고도화 연동

**Phase**: 15-4
**작성일**: 2026-02-16
**상태**: G1 PASS

---

## 1. 목표

지식관리 지정 폴더와 DB 테이블 간의 **매핑 규칙을 정의**하고, 시드 스크립트를 확장하여 **지정 폴더 경로를 포함한 시드**가 가능하도록 한다. 최종적으로 QA 검증 체크리스트를 통해 매핑 정합성, 시드 결과, AI 자동화 연동 여부를 검증한다.

- 지식관리 지정 폴더(`KNOWLEDGE_FOLDER_PATH`) 파일이 documents/projects/labels와 어떻게 매핑되는지 규칙 문서화
- `seed_sample_data.py`에 `--with-knowledge` 옵션을 추가하여 지정 폴더 파일도 시드 대상에 포함
- 검증 체크리스트로 매핑 규칙, 시드 데이터, 동기화, AI 자동화 결과를 체계적으로 QA

## 2. 범위

| 포함 | 제외 |
|------|------|
| 폴더 경로 ↔ DB 매핑 규칙 문서 (mapping-rules.md) | AI 자동화 파이프라인 구현 (15-2) |
| 시드 스크립트 `--with-knowledge` 옵션 확장 | Reasoning 연동 (15-3) |
| QA 검증 체크리스트 (verification-checklist.md) | Admin UI 기능 (15-1) |
| 시드 데이터 정합성 검증 | 사용자 관리/보안 (15-5, 15-6) |

## 3. 설계 결정

| 결정 | 선택 | 근거 |
|------|------|------|
| 매핑 규칙 문서 위치 | `docs/phases/phase-15-4/mapping-rules.md` | Phase 산출물과 함께 관리 |
| 폴더 → Project 매핑 | 1단계 하위 디렉토리 = Project | 깊은 계층은 불필요한 복잡도 유발 |
| 경로 기반 카테고리 분류 | 경로 키워드 패턴 매칭 | AI 분류 전 초기 자동 분류로 충분 |
| 시드 옵션 방식 | `--with-knowledge` CLI 플래그 | 기본 시드와 분리하여 선택적 실행 |
| 파일 경로 저장 형식 | 절대 경로 | 폴더 이동 시에도 참조 일관성 유지 |

## 4. 리스크

| 리스크 | 영향 | 대응 |
|--------|------|------|
| 폴더 경로 변경 시 기존 매핑 불일치 | 중 | sync API로 재동기화, file_path upsert 처리 |
| 대용량 지식 폴더 시드 시간 증가 | 하 | 허용 확장자 필터링 + 재귀 depth 제한 |
| 시드 재실행 시 중복 데이터 생성 | 중 | file_path unique 제약 + upsert 패턴 적용 |

## 5. 참조

- `docs/phases/phase-15-master-plan.md` -- Phase 15 전체 계획
- `docs/phases/phase-15-4/mapping-rules.md` -- 폴더-DB 매핑 규칙 (15-4-1 산출물)
- `docs/phases/phase-15-4/verification-checklist.md` -- QA 검증 체크리스트 (15-4-3 산출물)
- `scripts/db/seed_sample_data.py` -- 시드 스크립트 (15-4-2 수정 대상)
- `backend/services/knowledge/folder_service.py` -- 폴더 서비스 (15-1 산출물)
