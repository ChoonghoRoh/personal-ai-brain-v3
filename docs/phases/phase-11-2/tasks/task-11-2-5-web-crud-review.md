# Task 11-2-5: Web에서 CRUD 필요 부분 검토·다음 Phase 연계

**우선순위**: 11-2 내 5순위
**예상 작업량**: 0.5일
**의존성**: 11-2-1·11-2-2 완료
**상태**: ✅ 완료
**비고**: **Web 기능 개발은 Phase 11-3에서 진행.** 이번 Task는 검토·적용 검토·연계 조치만 수행.

**기반 문서**: [phase-11-2-0-todo-list.md](../phase-11-2-0-todo-list.md)
**Plan**: [phase-11-2-0-plan.md](../phase-11-2-0-plan.md)
**작업 순서**: [phase-11-navigation.md](../../phase-11-navigation.md)

---

## 1. 개요

### 1.1 목표

Web(Admin 설정 관리 화면)에서 필요한 **CRUD 목록**을 정리하고, 11-2-1·11-2-2 API와 **매핑·부족한 엔드포인트 적용 검토**를 수행한다. Phase 11-3에서 구현할 항목·우선순위·연계 사항을 문서화하고, **실제 Web 개발은 Phase 11-3**에서 진행하도록 조치한다.

---

## 2. 구현된 API 현황 (Phase 11-2)

### 2.1 Task 11-2-1 API (Schema, Template, PromptPreset)

| 리소스 | 엔드포인트 | 메서드 | 용도 |
|--------|-----------|--------|------|
| Schema | `/api/admin/schemas` | GET | 목록 조회 (필터·페이징) |
| Schema | `/api/admin/schemas/{id}` | GET | 단건 조회 |
| Schema | `/api/admin/schemas` | POST | 생성 |
| Schema | `/api/admin/schemas/{id}` | PUT | 수정 |
| Schema | `/api/admin/schemas/{id}` | DELETE | 삭제 |
| Template | `/api/admin/templates` | GET | 목록 조회 (필터·페이징) |
| Template | `/api/admin/templates/{id}` | GET | 단건 조회 |
| Template | `/api/admin/templates` | POST | 생성 |
| Template | `/api/admin/templates/{id}` | PUT | 수정 |
| Template | `/api/admin/templates/{id}` | DELETE | 삭제 |
| PromptPreset | `/api/admin/presets` | GET | 목록 조회 (필터·페이징) |
| PromptPreset | `/api/admin/presets/{id}` | GET | 단건 조회 |
| PromptPreset | `/api/admin/presets` | POST | 생성 |
| PromptPreset | `/api/admin/presets/{id}` | PUT | 수정 |
| PromptPreset | `/api/admin/presets/{id}` | DELETE | 삭제 |

### 2.2 Task 11-2-2 API (RAG Profile, Policy Set)

| 리소스 | 엔드포인트 | 메서드 | 용도 |
|--------|-----------|--------|------|
| RAG Profile | `/api/admin/rag-profiles` | GET | 목록 조회 (필터·페이징) |
| RAG Profile | `/api/admin/rag-profiles/{id}` | GET | 단건 조회 |
| RAG Profile | `/api/admin/rag-profiles` | POST | 생성 |
| RAG Profile | `/api/admin/rag-profiles/{id}` | PUT | 수정 |
| RAG Profile | `/api/admin/rag-profiles/{id}` | DELETE | 삭제 |
| Policy Set | `/api/admin/policy-sets` | GET | 목록 조회 (필터·페이징) |
| Policy Set | `/api/admin/policy-sets/{id}` | GET | 단건 조회 |
| Policy Set | `/api/admin/policy-sets` | POST | 생성 |
| Policy Set | `/api/admin/policy-sets/{id}` | PUT | 수정 |
| Policy Set | `/api/admin/policy-sets/{id}` | DELETE | 삭제 |

---

## 3. Web Admin UI 필요 기능 목록

### 3.1 필요 화면 구성

| 화면 | 경로 | 필요 API | 우선순위 |
|------|------|----------|----------|
| Admin 레이아웃/네비게이션 | `/admin` | - | 1 (기반) |
| Schema 관리 | `/admin/schemas` | schemas CRUD | 2 |
| Template 편집기 | `/admin/templates` | templates CRUD | 1 (핵심) |
| PromptPreset 편집기 | `/admin/presets` | presets CRUD | 1 (핵심) |
| RAG Profile 관리 | `/admin/rag-profiles` | rag-profiles CRUD | 2 |
| Policy Set 대시보드 | `/admin/policy-sets` | policy-sets CRUD | 2 |
| Audit Log 뷰어 | `/admin/audit-logs` | audit-logs 조회 | 3 |
| 버전 히스토리 | `/admin/templates/{id}/versions` | versions API | 3 |

### 3.2 화면별 필요 기능

#### Template 편집기 (핵심)
- [ ] 목록: 필터(template_type, status), 검색, 페이징
- [ ] 상세/편집: Markdown 에디터, 미리보기
- [ ] 생성: 템플릿 타입 선택, 내용 입력
- [ ] Publish/Draft 상태 전환 (다음 Phase API 필요)
- [ ] 버전 히스토리 (다음 Phase API 필요)

#### PromptPreset 편집기 (핵심)
- [ ] 목록: 필터(task_type, status), 검색, 페이징
- [ ] 상세/편집: 모델 선택, Temperature/Top-P 슬라이더, 시스템 프롬프트 편집
- [ ] 제약 조건(constraints) 태그 입력
- [ ] Publish/Draft 상태 전환

#### RAG Profile 관리
- [ ] 목록: 필터(status), 검색, 페이징
- [ ] 상세/편집: Chunk Size/Overlap/Top-K 슬라이더, Score Threshold 입력
- [ ] Rerank 활성화 체크박스
- [ ] Filter Priority JSON 편집

#### Policy Set 대시보드
- [ ] 목록: 프로젝트별 필터, 활성 상태 필터
- [ ] 상세/편집: Template/Preset/RAG Profile 선택 (드롭다운)
- [ ] 우선순위 조정
- [ ] 유효 기간 설정

---

## 4. API 매핑 및 부족 엔드포인트 분석

### 4.1 API 매핑 현황

| Web 기능 | 필요 API | Phase 11-2 제공 | 비고 |
|----------|----------|-----------------|------|
| CRUD 목록 조회 | GET /api/admin/{resource} | ✅ | 필터·페이징 지원 |
| CRUD 단건 조회 | GET /api/admin/{resource}/{id} | ✅ | |
| CRUD 생성 | POST /api/admin/{resource} | ✅ | |
| CRUD 수정 | PUT /api/admin/{resource}/{id} | ✅ | 부분 업데이트 지원 |
| CRUD 삭제 | DELETE /api/admin/{resource}/{id} | ✅ | |
| Publish | POST /api/admin/{resource}/{id}/publish | ❌ | Task 11-2-3 설계 완료, 다음 Phase 구현 |
| Version History | GET /api/admin/{resource}/{id}/versions | ❌ | Task 11-2-3 설계 완료, 다음 Phase 구현 |
| Rollback | POST /api/admin/{resource}/{id}/rollback | ❌ | Task 11-2-3 설계 완료, 다음 Phase 구현 |
| Audit Log 조회 | GET /api/admin/audit-logs | ❌ | Task 11-2-3 설계 완료, 다음 Phase 구현 |
| Policy Resolve | GET /api/admin/policy-sets/resolve | ❌ | Task 11-2-4 설계 완료, 다음 Phase 구현 |

### 4.2 부족 엔드포인트 (다음 Phase 구현 예정)

1. **Publish/Rollback API** - Task 11-2-3 설계 문서 기반
2. **Version History API** - Task 11-2-3 설계 문서 기반
3. **Audit Log 조회 API** - Task 11-2-3 설계 문서 기반
4. **Policy Resolve API** - Task 11-2-4 설계 문서 기반

---

## 5. Phase 11-3 연계 사항

### 5.1 Phase 11-3 구현 항목

| 우선순위 | 항목 | 의존성 |
|----------|------|--------|
| 1 | Admin 레이아웃·네비게이션·라우팅 | - |
| 1 | Template 편집기 (CRUD) | 11-2-1 API |
| 1 | PromptPreset 편집기 (CRUD) | 11-2-1 API |
| 2 | RAG Profile 관리 (CRUD) | 11-2-2 API |
| 2 | Policy Set 대시보드 (CRUD) | 11-2-2 API |
| 3 | Audit Log 뷰어 | Audit API (다음 Phase) |
| 3 | 버전 히스토리 | Version API (다음 Phase) |

### 5.2 Phase 11-3 plan/todo 참조 추가

Phase 11-3 plan/todo에 다음 내용 반영 필요:
- "11-2-5 검토 결과 반영: Web CRUD 필요 목록 및 API 매핑"
- CRUD API는 11-2에서 완료, Version/Audit API는 별도 Phase에서 구현 후 연동

---

## 6. 체크리스트 (Done Definition)

- [x] Web(Admin 설정 관리 화면)에서 필요한 CRUD 목록 정리
- [x] 11-2-1·11-2-2 API와 매핑·부족한 엔드포인트 적용 검토
- [x] Phase 11-3에서 구현할 항목·우선순위·연계 사항 문서화
- [x] 산출물 작성 (본 문서)
- [ ] Phase 11-3 plan/todo에 "11-2-5 검토 결과 반영" 참조 추가

---

## 7. 참조

- [phase-11-2-0-plan.md](../phase-11-2-0-plan.md) §5.5
- [phase-11-3-0-plan.md](../../phase-11-3/phase-11-3-0-plan.md) — Admin UI Plan
- [task-11-2-3-version-audit-design.md](task-11-2-3-version-audit-design.md) — 버전·Audit API 설계
- [task-11-2-4-resolve-policy-design.md](task-11-2-4-resolve-policy-design.md) — 정책 해석 API 설계
