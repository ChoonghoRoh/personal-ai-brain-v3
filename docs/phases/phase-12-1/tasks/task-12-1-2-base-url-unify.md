# Task 12-1-2: [FS] Base URL 8001 통일 (코드+문서)

**우선순위**: 12-1 내 2순위
**예상 작업량**: 중 (코드 1파일 + 문서 106파일 치환)
**의존성**: 없음
**상태**: ✅ 완료

**기반 문서**: `phase-12-1-todo-list.md`
**Plan**: `phase-12-1-plan.md`
**작업 순서**: `phase-12-navigation.md`

---

## 1. 개요

### 1.1 목표

외부 노출 포트를 8001로 통일하고, 코드와 문서에서 8000 하드코딩을 제거한다. 컨테이너 내부 포트(8000)와 호스트 노출 포트(8001)를 이원화하여 혼동을 방지한다.

---

## 2. 파일 변경 계획

### 2.1 수정

| 파일 | 변경 내용 |
|------|----------|
| `backend/config.py` | `EXTERNAL_PORT = get_env_int("EXTERNAL_PORT", 8001)` 추가 |
| `backend/main.py` | FastAPI servers URL에 EXTERNAL_PORT 반영 |
| `.env.example` | EXTERNAL_PORT 설정 문서화 |
| `docs/**` (106파일) | localhost:8000 → localhost:8001 일괄 치환 |

---

## 3. 작업 체크리스트

- [x] `backend/config.py` EXTERNAL_PORT 환경변수 추가
- [x] `backend/main.py` FastAPI servers URL 수정
- [x] `.env.example` 포트 설정 문서화
- [x] `docs/` 내 localhost:8000 → localhost:8001 일괄 치환 (346건)
- [x] Grep 검증: 코드 파일에서 `localhost:8000` 0건

---

## 4. 참조

- Phase 12 Master Plan §12-1-2
- docker-compose.yml: `"8001:8000"` 포트 매핑
