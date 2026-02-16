# Phase 15-1 Plan: 지식관리 지정 폴더 & 파일 관리

**Phase**: 15-1
**작성일**: 2026-02-16
**상태**: G1 PASS

---

## 1. 목표

지식관리 시스템에 **지정 폴더 기반 파일 관리** 기능을 추가한다.
- 관리자가 지식 문서를 저장할 폴더 경로를 설정
- 폴더 내 파일 목록 조회, 업로드, 동기화 API 제공
- 파일관리 전용 Admin UI 페이지 구현

## 2. 범위

| 포함 | 제외 |
|------|------|
| 지정 폴더 경로 설정 API (GET/PUT) | AI 자동화 워크플로우 (15-2) |
| 폴더 파일 목록 API | Reasoning 연동 (15-3) |
| 파일 업로드/동기화 API | 사용자 관리/보안 (15-5, 15-6) |
| 파일관리 Admin UI 페이지 | |

## 3. 설계 결정

| 결정 | 선택 | 근거 |
|------|------|------|
| 폴더 경로 저장 | 환경변수 기본값 + DB 오버라이드 | Admin UI에서 변경 가능하도록 |
| 라우터 위치 | `backend/routers/knowledge/folder_management.py` 신규 | 기존 knowledge prefix 활용 |
| 서비스 위치 | `backend/services/knowledge/folder_service.py` 신규 | 폴더 스캔 + DB 매칭 분리 |
| UI 페이지 경로 | `/admin/knowledge-files` | 기존 Admin 메뉴 구조와 일관 |
| 파일 파싱 | 기존 FileParserService 재사용 | 중복 구현 방지 |

## 4. 리스크

| 리스크 | 영향 | 대응 |
|--------|------|------|
| file_path 규칙 충돌 | 중 | 프로젝트 루트 기준 상대경로로 통일 |
| 대용량 폴더 스캔 성능 | 중 | 재귀 depth 제한 + 페이징 |
| 기존 ingest 파이프라인 중복 | 중 | file_path unique + upsert 처리 |

## 5. 참조

- `docs/phases/phase-15-master-plan.md` — Phase 15 전체 계획
- `docs/SSOT/claude/2-architecture-ssot.md` — 기술 스택, 코드 구조
- `backend/services/ingest/file_parser_service.py` — 파일 파싱 재사용
