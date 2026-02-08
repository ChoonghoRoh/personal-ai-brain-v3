# Task 11-2-3: 버전 관리·Publish/Rollback·Audit Log (상세 설계)

**우선순위**: 11-2 내 3순위
**예상 작업량**: 0.5일
**의존성**: 11-2-1·11-2-2 완료
**상태**: ✅ 완료
**비고**: **구현은 다음 Phase에서 진행.** 이번 Task에서는 디테일한 설계만 수행.

**기반 문서**: [phase-11-2-0-todo-list.md](../phase-11-2-0-todo-list.md)
**Plan**: [phase-11-2-0-plan.md](../phase-11-2-0-plan.md)
**작업 순서**: [phase-11-navigation.md](../../phase-11-navigation.md)

---

## 1. 개요

### 1.1 목표

버전 관리·Publish/Rollback·Audit Log **API 스펙**을 설계하고, 상태 전이·기록 규칙을 정의한다. 설계 문서를 산출물로 남기며, **API 구현은 다음 Phase**에서 설계 문서 기반으로 진행한다.

### 1.2 적용 대상 리소스

버전 관리가 필요한 리소스:
- **templates** (AdminTemplate)
- **prompt_presets** (AdminPromptPreset)
- **rag_profiles** (AdminRagProfile)

버전 관리 없이 Audit Log만 기록하는 리소스:
- **schemas** (AdminSchema)
- **context_rules** (AdminContextRule)
- **policy_sets** (AdminPolicySet)

---

## 2. 상태 전이 설계

### 2.1 상태 흐름

```
[draft] ─── publish ───> [published]
   ↑                          │
   │                          │
   └────── rollback ──────────┘
           (새 draft 버전 생성)
```

### 2.2 상태 정의

| 상태 | 설명 | 편집 가능 | 서비스 사용 |
|------|------|----------|------------|
| `draft` | 작성 중 | ✅ | ❌ |
| `published` | 배포됨 | ❌ (새 버전 생성 필요) | ✅ |
| `archived` | 보관 (선택적) | ❌ | ❌ |

### 2.3 상태 전이 규칙

| 전이 | 조건 | 결과 |
|------|------|------|
| draft → published | Publish API 호출 + change_reason 필수 | status='published', published_at=NOW(), version 유지 |
| published → draft | 수정 시도 시 | 새 레코드 생성 (version+1, status='draft'), 원본 유지 |
| published → draft (rollback) | Rollback API 호출 | 지정 버전의 content를 복사한 새 draft 생성 |

---

## 3. 버전 관리 API 스펙

### 3.1 Publish API

**대상**: templates, prompt_presets, rag_profiles

```
POST /api/admin/{resource}/{id}/publish
```

**Request Body**:
```json
{
  "change_reason": "string (필수, 변경 사유)"
}
```

**Response** (200 OK):
```json
{
  "id": "uuid",
  "version": 1,
  "status": "published",
  "published_at": "2026-02-06T00:00:00Z",
  "message": "Template published successfully"
}
```

**에러 케이스**:
- 400: 이미 published 상태
- 404: 리소스 없음
- 422: change_reason 누락

**처리 로직**:
1. 현재 상태가 draft인지 확인
2. status를 published로 변경
3. published_at을 현재 시간으로 설정
4. Audit Log에 'publish' 액션 기록

---

### 3.2 Version History API

**대상**: templates, prompt_presets, rag_profiles

```
GET /api/admin/{resource}/{id}/versions
```

**Query Parameters**:
- `limit`: int (기본값 5, 최대 20)

**Response** (200 OK):
```json
{
  "items": [
    {
      "version": 2,
      "status": "draft",
      "created_at": "2026-02-06T01:00:00Z",
      "published_at": null,
      "changed_by": "admin",
      "change_reason": "신규 수정"
    },
    {
      "version": 1,
      "status": "published",
      "created_at": "2026-02-05T00:00:00Z",
      "published_at": "2026-02-05T12:00:00Z",
      "changed_by": "admin",
      "change_reason": "최초 배포"
    }
  ],
  "total": 2
}
```

**구현 방식**:
- audit_logs 테이블에서 해당 record_id의 변경 이력 조회
- 또는 별도 version_history 테이블 생성 (확장 시)

---

### 3.3 Rollback API

**대상**: templates, prompt_presets, rag_profiles

```
POST /api/admin/{resource}/{id}/rollback
```

**Request Body**:
```json
{
  "to_version": 1,
  "change_reason": "string (필수, 롤백 사유)"
}
```

**Response** (200 OK):
```json
{
  "id": "new-uuid (새 draft의 ID)",
  "version": 3,
  "status": "draft",
  "message": "Rolled back to version 1. New draft created.",
  "source_version": 1
}
```

**에러 케이스**:
- 404: 지정 버전 없음
- 422: change_reason 누락

**처리 로직**:
1. audit_logs에서 to_version의 old_values 또는 new_values 조회
2. 해당 버전의 content로 새 draft 레코드 생성
3. version을 현재 최대 버전 + 1로 설정
4. Audit Log에 'rollback' 액션 기록

---

## 4. Audit Log API 스펙

### 4.1 Audit Log 기록 규칙

**기록 대상 액션**:

| 액션 | 설명 | old_values | new_values |
|------|------|------------|------------|
| `create` | 새 레코드 생성 | null | 전체 필드 |
| `update` | 레코드 수정 | 변경 전 필드 | 변경 후 필드 |
| `delete` | 레코드 삭제 | 전체 필드 | null |
| `publish` | 배포 | {status: 'draft'} | {status: 'published', published_at} |
| `rollback` | 롤백 | {version: current} | {version: new, source_version} |

**자동 기록 시점**:
- CRUD API 호출 시 자동 기록 (deps.py 또는 service layer에서 처리)

**기록 필드**:
```json
{
  "table_name": "templates",
  "record_id": "uuid",
  "action": "update",
  "changed_by": "admin",
  "change_reason": "설명 수정",
  "old_values": {"description": "이전 설명"},
  "new_values": {"description": "새 설명"},
  "created_at": "2026-02-06T00:00:00Z"
}
```

---

### 4.2 Audit Log 조회 API

```
GET /api/admin/audit-logs
```

**Query Parameters**:
- `table_name`: string (필터, 예: 'templates')
- `record_id`: uuid (필터, 특정 레코드)
- `action`: string (필터, 예: 'publish')
- `changed_by`: string (필터, 변경자)
- `from_date`: datetime (필터, 시작일)
- `to_date`: datetime (필터, 종료일)
- `limit`: int (기본값 50, 최대 100)
- `offset`: int (기본값 0)

**Response** (200 OK):
```json
{
  "items": [
    {
      "id": "uuid",
      "table_name": "templates",
      "record_id": "uuid",
      "action": "publish",
      "changed_by": "admin",
      "change_reason": "최초 배포",
      "old_values": {"status": "draft"},
      "new_values": {"status": "published", "published_at": "..."},
      "created_at": "2026-02-06T00:00:00Z"
    }
  ],
  "total": 150,
  "limit": 50,
  "offset": 0
}
```

---

### 4.3 Audit Log 단건 조회 API

```
GET /api/admin/audit-logs/{log_id}
```

**Response** (200 OK):
```json
{
  "id": "uuid",
  "table_name": "templates",
  "record_id": "uuid",
  "action": "update",
  "changed_by": "admin",
  "change_reason": "내용 수정",
  "old_values": {"content": "이전 내용..."},
  "new_values": {"content": "새 내용..."},
  "created_at": "2026-02-06T00:00:00Z"
}
```

---

## 5. 구현 파일 계획 (다음 Phase)

| 파일 경로 | 용도 |
|-----------|------|
| `backend/routers/admin/version_crud.py` | Publish, Version History, Rollback API |
| `backend/routers/admin/audit_log_crud.py` | Audit Log 조회 API |
| `backend/services/admin/audit_logger.py` | Audit Log 자동 기록 서비스 |
| `backend/services/admin/version_manager.py` | 버전 관리 로직 |
| `backend/routers/admin/schemas_pydantic.py` (확장) | Publish/Rollback Request/Response 스키마 |

---

## 6. 체크리스트 (Done Definition)

- [x] 버전 관리·Publish/Rollback API 스펙(엔드포인트·요청/응답) 설계
- [x] Audit Log 기록 규칙·조회 API 스펙 설계
- [x] 상태 전이(draft → published) 정의
- [x] 설계 문서 작성 (본 문서)
- [ ] 구현 작업은 다음 Phase에서 설계 문서 기반으로 진행

---

## 7. 참조

- [phase-11-2-0-plan.md](../phase-11-2-0-plan.md) §5.3
- [phase-11-master-plan-sample.md](../../phase-11-master-plan-sample.md) — 버전·Audit API 참고
