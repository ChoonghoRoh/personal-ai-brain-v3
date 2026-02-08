# Task 11-5-6: 공유·저장 고도화 (§2.4)

**우선순위**: 11-5 내 6순위 (선택)
**예상 작업량**: 0.5~1일
**의존성**: 11-5-2 완료
**상태**: ✅ 완료

**기반 문서**: [phase-11-5-0-todo-list.md](../phase-11-5-0-todo-list.md)
**Plan**: [phase-11-5-0-plan.md](../phase-11-5-0-plan.md)
**고도화 검토 상세**: [phase-10-improvement-plan.md](../phase-10-improvement-plan.md) **§2.4**
**작업 순서**: [phase-11-navigation.md](../../phase-11-navigation.md)

---

## 1. 개요

### 1.1 목표

**phase-10-improvement-plan §2.4** 표에 따른 **공유·저장** 고도화를 구현·검증한다. 공유 URL·의사결정 문서 항목을 다룬다.

### 1.2 §2.4 표 항목 (phase-10-improvement-plan)

| 항목              | 현황                           | 고도화 방향                                                     | 우선순위 |
| ----------------- | ------------------------------ | --------------------------------------------------------------- | -------- |
| **공유 URL**      | 10-4-2 공유 URL 생성/조회 완료 | 만료 기간·비공개 옵션·조회 제한                                 | 중       |
| **의사결정 문서** | 10-4-3 저장/조회/삭제 API 완료 | 버전 표시·검색·필터, Admin 설정(Phase 11)과 연동 시 템플릿 반영 | 중       |

---

## 2. 작업 범위 (파일 변경 계획)

### 2.1 수정·신규 (계획에 따름)

| 구분     | 내용                                                    |
| -------- | ------------------------------------------------------- |
| **코드** | `web/`, `backend/` — 공유 URL·의사결정 문서 API·UI 경로 |
| **문서** | `docs/phases/phase-11-5/` — task report                 |

---

## 3. 작업 체크리스트 (Done Definition)

- [x] **공유 URL**: 만료(expires_in_days)·비공개(is_private)·조회(view_count) (reason_store.py, models.py, migration)
- [x] **의사결정 문서**: 검색(q) title/summary 필터 (list_decisions)
- [x] 산출물: [task-11-5-6-report.md](task-11-5-6-report.md)

---

## 4. 참조·비고

- **선택 Task**: 11-5-2 완료 후 선택 실행.
- [phase-10-improvement-plan.md](../phase-10-improvement-plan.md) §2.4
