# Phase 11-1-0 Plan — DB 스키마·마이그레이션

**Phase ID**: 11-1  
**Phase 명**: DB 스키마·마이그레이션  
**Z**: 0 (초기 설계)  
**기준 문서**: [phase-11-master-plan.md](../phase-11-master-plan.md)  
**명명 규칙**: [ai-rule-phase-naming.md](../../ai/ai-rule-phase-naming.md)

---

## 1. Phase Goal

Admin 설정을 저장할 **7종 테이블(schemas, templates, prompt_presets, rag_profiles, context_rules, policy_sets, audit_logs)** 의 DB 스키마·마이그레이션·시딩을 구축한다.  
**기존 테이블·데이터는 변경하지 않고 신규 테이블만 추가**하며, 단계별 검증 후 다음 Task로 진행한다.

---

## 2. Scope

### 2.1 In Scope

| Task ID | 항목 | 예상 |
|---------|------|------|
| 11-1-1 | schemas, templates, prompt_presets 테이블 설계·마이그레이션 | 1일 |
| 11-1-2 | rag_profiles, context_rules, policy_sets 테이블 설계·마이그레이션 | 1일 |
| 11-1-3 | audit_logs 테이블, 초기 시딩 스크립트, 관계 검증 | 0.5~1일 |

### 2.2 Out of Scope

- Admin API·Admin UI(Phase 11-2·11-3), 통합 테스트·운영 매뉴얼(Phase 11-4)은 본 Phase 제외.
- 멀티 테넌시·A/B 테스트는 마스터 플랜 Out of Scope와 동일.
- **기존 테이블(projects, documents, knowledge_chunks, labels 등) 스키마 변경·데이터 마이그레이션은 하지 않음.**

---

## 3. DB 검증·데이터 무손실 계획 및 실행 방법

### 3.1 원칙

| 원칙 | 내용 |
|------|------|
| **신규 테이블만 추가** | 기존 테이블에 ALTER TABLE 등 스키마 변경을 하지 않고, Admin 설정용 테이블만 CREATE. |
| **기존 데이터 무손실** | 마이그레이션 스크립트는 INSERT만 하거나 시딩 스크립트로 초기 데이터 삽입. 기존 테이블 데이터는 읽기/삭제하지 않음. |
| **검증 후 다음 단계** | 각 Task 완료 시 정해진 검증(테이블 존재·행 수·FK·회귀)을 수행하고, 통과 시에만 다음 Task 착수. |

### 3.2 데이터 무손실을 위한 실행 순서

1. **마이그레이션 전**  
   - 백업 실행(§4 참조).  
   - 해당 Task에서 추가하는 **테이블 목록**과 **기존 코드 사용처**를 정리(영향도 §6 참조).  
2. **마이그레이션 작성**  
   - CREATE TABLE만 사용. 기존 테이블 참조 시 FK는 신규 테이블 → 기존 테이블 방향만 허용(필요 시). 기존 테이블 컬럼 추가는 Phase 11-1 범위에서 하지 않음.  
3. **마이그레이션 실행**  
   - 개발/스테이징 환경에서 먼저 실행.  
4. **검증**  
   - 테이블 존재, 시딩 행 수, FK 제약, 인덱스 존재 확인.  
   - 기존 서비스(Backend API·Frontend) 회귀 확인(해당 Task 영향 범위).  
5. **문제 발생 시**  
   - 백업에서 PostgreSQL만 복원(`scripts/backup/restore.sh <backup_id> --postgres-only`).  
   - 원인 분석 후 마이그레이션 스크립트 수정·재실행.

### 3.3 검증 체크리스트(공통)

- [ ] 신규 테이블만 생성되었는지 확인(기존 테이블 스키마 변경 없음).
- [ ] 시딩된 행 수가 기대값과 일치하는지 확인.
- [ ] FK·UNIQUE·NOT NULL 등 제약 조건 오류 없이 조회/삽입 가능한지 확인.
- [ ] 기존 Backend/Frontend 동작(해당 Task 영향도 범위) 회귀 없음.

---

## 4. 백업 방법

### 4.1 마이그레이션 전 필수 백업

| 시점 | 명령 | 비고 |
|------|------|------|
| **Phase 11-1 착수 전** | `./scripts/backup/backup.sh` | 전체(PostgreSQL + Qdrant + 메타데이터). |
| **각 Task 마이그레이션 실행 직전** | `./scripts/backup/backup.sh --postgres-only` | PostgreSQL만 백업. Task 단위 롤백용. |

### 4.2 백업 실행 방법

- **위치**: 프로젝트 루트에서 실행.  
- **전체 백업**: `./scripts/backup/backup.sh`  
- **PostgreSQL만(권장)**: `./scripts/backup/backup.sh --postgres-only`  
- **백업 저장 경로**: 기본값 `./backups/backup_YYYYMMDD_HHMMSS/`.  
- **환경 변수**: `.env`의 `POSTGRES_*`, `BACKUP_DIR` 등.  
- **참고**: [scripts/backup/backup.sh](../../../scripts/backup/backup.sh), [scripts/backup/restore.sh](../../../scripts/backup/restore.sh).

### 4.3 복원 방법(마이그레이션 롤백 시)

- `./scripts/backup/restore.sh <backup_id> --postgres-only`  
- 확인 프롬프트 후 기존 DB가 덮어씌워지므로, 반드시 백업 ID를 확인한 뒤 실행.

---

## 5. 개발 진행 절차(공통)

각 Task는 아래 순서로 진행한다. **영향도 검증 완료 후** 개발(마이그레이션 작성)을 시작하고, **단계별 테스트 검증 통과 후** 다음 단계로 이동한다.

```
[1] 영향도 검증
    → 해당 Task에서 추가하는 테이블이 Backend/Frontend에서 사용되는지 조사.
    → Phase 11-1에서는 신규 테이블만 추가하므로 기존 코드 사용처는 없음.
    → 조사 결과를 task 문서에 기록.

[2] 백업 실행
    → scripts/backup/backup.sh --postgres-only

[3] 마이그레이션·시딩 개발
    → Alembic 또는 SQL/스크립트 작성 및 실행

[4] 단계별 테스트 검증(§7)
    → 해당 Task의 검증 항목 모두 통과할 때까지 수정·재실행

[5] 통과 시
    → Task report 작성, 다음 Task 착수(11-1-1 → 11-1-2 → 11-1-3)
```

---

## 6. Task별 상세 검증 및 Backend/Frontend 영향도

### 6.1 Task 11-1-1 (schemas, templates, prompt_presets)

| 항목 | 내용 |
|------|------|
| **추가 테이블** | schemas, templates, prompt_presets. |
| **기존 테이블 변경** | 없음. |
| **Backend 영향도** | 없음. 현재 Backend는 해당 테이블을 사용하지 않음(Phase 11-2에서 API 구현). |
| **Frontend 영향도** | 없음. 현재 Web은 해당 테이블을 직접 사용하지 않음. |
| **검증 항목** | ① 세 테이블 존재. ② 시딩 행 수(phase-11-master-plan-sample 기준). ③ NOT NULL/UNIQUE 등 제약으로 인한 오류 없음. ④ 기존 서비스(대시보드·Reasoning·지식 등) 회귀 없음. |

### 6.2 Task 11-1-2 (rag_profiles, context_rules, policy_sets)

| 항목 | 내용 |
|------|------|
| **추가 테이블** | rag_profiles, context_rules, policy_sets. |
| **FK 관계** | policy_sets → templates 등(샘플 설계 기준). 신규 테이블 간 또는 신규→기존 참조만. |
| **기존 테이블 변경** | 없음. |
| **Backend 영향도** | 없음. Phase 11-2에서 사용 예정. |
| **Frontend 영향도** | 없음. Phase 11-3에서 사용 예정. |
| **검증 항목** | ① 세 테이블 존재. ② FK·시딩 정상. ③ 기존 서비스 회귀 없음. |

### 6.3 Task 11-1-3 (audit_logs, 시딩, 관계 검증)

| 항목 | 내용 |
|------|------|
| **추가 테이블** | audit_logs. |
| **기존 테이블 변경** | 없음. |
| **Backend/Frontend 영향도** | 없음. Phase 11-2·11-3에서 사용 예정. |
| **검증 항목** | ① audit_logs 테이블 존재. ② 전체 Admin 설정 테이블(schemas~audit_logs) FK·인덱스 검증. ③ 초기 시딩 스크립트 실행·행 수 검증. ④ Phase 10 회귀(Reasoning Lab·E2E 등) 유지. |

---

## 7. 단계별 테스트 검증 후 다음 단계 이동

### 7.1 규칙

- **각 Task 완료 시** 아래 해당 Task의 검증을 모두 수행한다.
- **모든 검증 통과 시에만** 다음 Task(또는 Phase 11-2)로 진행한다.
- 검증 실패 시 원인 조치 후 재검증.

### 7.2 11-1-1 완료 시 검증

- [ ] `schemas`, `templates`, `prompt_presets` 테이블이 DB에 존재하는지 확인.
- [ ] 시딩 데이터 행 수가 기대값과 일치하는지 확인.
- [ ] 기존 기능(대시보드, 검색, 지식, Reasoning Lab 등) 동작 회귀 없음 확인.
- [ ] 위 통과 시 **11-1-2 착수**.

### 7.3 11-1-2 완료 시 검증

- [ ] `rag_profiles`, `context_rules`, `policy_sets` 테이블 존재 및 FK 관계 확인.
- [ ] 시딩·제약 조건 오류 없음 확인.
- [ ] 기존 기능 회귀 없음 확인.
- [ ] 위 통과 시 **11-1-3 착수**.

### 7.4 11-1-3 완료 시 검증

- [ ] `audit_logs` 테이블 존재 확인.
- [ ] 전체 Admin 설정 테이블(7종) 관계·인덱스 검증.
- [ ] 초기 시딩 스크립트 실행 결과·행 수 검증.
- [ ] Phase 10 회귀 테스트(Reasoning Lab·E2E) 유지 확인.
- [ ] 위 통과 시 **Phase 11-2 전달**.

---

## 8. Task 개요

| Task ID | Task 명 | 예상 작업량 | 의존성 |
|---------|---------|-------------|--------|
| 11-1-1 | schemas, templates, prompt_presets 테이블 설계·마이그레이션 | 1일 | 없음 |
| 11-1-2 | rag_profiles, context_rules, policy_sets 테이블 설계·마이그레이션 | 1일 | 11-1-1 검증 통과 후 |
| 11-1-3 | audit_logs, 시딩, 관계 검증 | 0.5~1일 | 11-1-2 검증 통과 후 |

**진행 순서**: 11-1-1 → (검증 통과) → 11-1-2 → (검증 통과) → 11-1-3 → (검증 통과) → Phase 11-2.

---

## 9. Validation / Exit Criteria

- [ ] **11-1-1** schemas, templates, prompt_presets 테이블 마이그레이션 적용·시딩 완료. 검증 통과.
- [ ] **11-1-2** rag_profiles, context_rules, policy_sets 테이블 마이그레이션 적용·시딩 완료. 검증 통과.
- [ ] **11-1-3** audit_logs 테이블 마이그레이션 적용, 초기 시딩·관계 검증 완료. 검증 통과.
- [ ] Phase 10 회귀 테스트 유지 (Reasoning Lab·E2E).
- [ ] 각 Task 산출물: `phase-11-1/tasks/`, `phase-11-1/phase11-1-*-test-report.md`.

---

## 10. 참고 문서

| 문서 | 용도 |
|------|------|
| [phase-11-master-plan.md](../phase-11-master-plan.md) | Phase 11 전체 계획 |
| [phase-11-1-0-todo-list.md](phase-11-1-0-todo-list.md) | 본 Phase 할 일 목록 |
| [phase-11-master-plan-sample.md](../phase-11-master-plan-sample.md) | Admin DB 스키마(SQL) 상세 참고 |
| [scripts/backup/backup.sh](../../../scripts/backup/backup.sh) | 백업 실행 |
| [scripts/backup/restore.sh](../../../scripts/backup/restore.sh) | 복원(롤백) |
| [docs/db/database-create-table-column.md](../../db/database-create-table-column.md) | 테이블·컬럼 생성 가이드 |
