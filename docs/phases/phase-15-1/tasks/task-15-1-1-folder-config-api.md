# Task 15-1-1: 지정 폴더 경로 설정 API

**우선순위**: 15-1 내 1순위
**의존성**: 없음
**담당 팀원**: backend-dev
**상태**: 대기

---

## §1. 개요

지식관리 전용 폴더 경로를 조회/설정하는 API를 구현한다. 환경변수 기본값 + DB 오버라이드 방식으로 Admin UI에서 경로 변경이 가능하도록 한다.

## §2. 파일 변경 계획

| 파일 | 유형 | 변경 내용 |
|------|------|----------|
| `backend/config.py` | 수정 | `KNOWLEDGE_FOLDER_PATH` 환경변수 기본값 추가 |
| `backend/routers/knowledge/folder_management.py` | 신규 | GET/PUT `/api/knowledge/folder-config` 엔드포인트 |
| `backend/services/knowledge/folder_service.py` | 신규 | 폴더 경로 조회/저장 서비스 로직 |
| `backend/main.py` | 수정 | folder_management 라우터 등록 |
| `tests/test_folder_management.py` | 신규 | API 테스트 |

## §3. 작업 체크리스트 (Done Definition)

- [ ] `GET /api/knowledge/folder-config` → `{ "folder_path": "brain/knowledge", "source": "env" }` 반환
- [ ] `PUT /api/knowledge/folder-config` → body `{ "folder_path": "..." }` 로 경로 변경
- [ ] 환경변수 `KNOWLEDGE_FOLDER_PATH` 미설정 시 기본값 `brain/knowledge`
- [ ] DB에 설정값이 있으면 환경변수보다 우선 (source: "db")
- [ ] `Depends(require_admin_knowledge)` 적용
- [ ] Pydantic 스키마로 입력 검증
- [ ] 존재하지 않는 폴더 경로 설정 시 에러 반환 또는 자동 생성
- [ ] 테스트 파일 존재

## §4. 참조

- `backend/config.py` — 기존 환경변수 패턴 참조
- `backend/routers/admin/` — Admin API 패턴 참조
- `backend/middleware/auth.py` — `require_admin_knowledge` 사용법
