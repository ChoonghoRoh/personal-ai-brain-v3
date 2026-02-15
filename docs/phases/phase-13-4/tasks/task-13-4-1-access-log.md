# Task 13-4-1: [DB] (선택) 메뉴/페이지 접근 로그 테이블 도입

**우선순위**: 선택
**예상 작업량**: 중 (1일)
**의존성**: 없음 (독립)
**상태**: TODO (선택)

---

## 1. 목표

메뉴/페이지별 접근 로그를 수집하여 운영 분석에 활용한다. `page_access_log` 테이블을 설계·마이그레이션하고, 기록 로직을 구현한다.

## 2. 스키마 설계 (안)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | SERIAL PK | 기본키 |
| path | VARCHAR(255) | 접근 경로 |
| method | VARCHAR(10) | HTTP 메서드 |
| user_agent | TEXT | User-Agent (선택) |
| ip_address | VARCHAR(45) | 클라이언트 IP (선택) |
| accessed_at | TIMESTAMP | 접근 시각 (기본: now()) |

## 3. 작업 체크리스트

- [ ] 테이블 스키마 설계
- [ ] SQLAlchemy 모델 정의
- [ ] Alembic 마이그레이션 생성·적용
- [ ] 접근 로그 기록 미들웨어 구현
- [ ] 동작 확인

## 4. 참조

- Phase 13 Master Plan §D-3
