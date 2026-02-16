# Phase 15-4-1: 지식관리 지정 폴더 ↔ DB 매핑 규칙

**작성일**: 2026-02-16
**Phase**: 15-4-1 [DOC]
**선행**: Phase 15-1 (지정 폴더·파일관리) 완료

---

## 1. 개요

지식관리 지정 폴더(`KNOWLEDGE_FOLDER_PATH`)의 파일들이 DB 테이블(documents, projects, labels, knowledge_chunks)과 어떻게 매핑되는지 정의한다.

---

## 2. 폴더 경로 → Document 매핑

### 2.1 경로 규칙

| 항목 | 규칙 |
|------|------|
| **기본 폴더** | `brain/knowledge/` (PROJECT_ROOT 기준 상대 경로) |
| **DB 설정** | `system_settings.key = 'knowledge.folder_path'` (우선순위 1) |
| **환경변수** | `KNOWLEDGE_FOLDER_PATH` (우선순위 2, 기본값) |
| **file_path 저장** | 절대 경로 (`/full/path/to/file.md`) — `folder_service.save_uploaded_file` 참조 |

### 2.2 Document 필드 매핑

| Document 필드 | 매핑 소스 | 예시 |
|---------------|-----------|------|
| `file_path` | 파일 절대 경로 | `/home/user/project/brain/knowledge/report.md` |
| `file_name` | 파일명 | `report.md` |
| `file_type` | 확장자 (`.`제거) | `md`, `pdf`, `docx` |
| `size` | 파일 시스템 `stat().st_size` | 12345 |
| `project_id` | 프로젝트 매핑 규칙 (§3) | NULL 또는 Project.id |
| `category_label_id` | 카테고리 분류 규칙 (§4) | Label.id (category 타입) |

---

## 3. 폴더 구조 → Project 매핑

### 3.1 매핑 정책

지식관리 폴더의 **1단계 하위 디렉토리**를 Project로 매핑할 수 있다.

```
brain/knowledge/
├── backend/          → project_id: "backend" Project
├── frontend/         → project_id: "web" Project
├── docs/             → project_id: "docs" Project
├── planning/         → project_id: NULL (매핑 없음) 또는 자동 생성
└── report.md         → project_id: NULL (루트 파일)
```

### 3.2 매핑 규칙

| 조건 | 매핑 |
|------|------|
| 하위 폴더명이 기존 Project.name과 일치 | 해당 `project_id` 할당 |
| 하위 폴더명이 Project에 없음 | `project_id = NULL` (미분류) |
| 루트 파일 (하위 폴더 없음) | `project_id = NULL` |
| 시드 스크립트 실행 시 | `--with-knowledge` 옵션으로 knowledge 폴더 파일을 Project 매핑하여 시드 |

### 3.3 자동 Project 생성 (선택)

시드 시 `--auto-project` 플래그가 있으면, 폴더명으로 Project를 자동 생성:

```python
# 예: brain/knowledge/새프로젝트/ → Project(name="새프로젝트", path="brain/knowledge/새프로젝트")
```

---

## 4. 파일 → Label(Category) 매핑

### 4.1 카테고리 분류 규칙

파일 경로·내용 기반으로 `labels` 테이블의 `category` 타입 라벨을 자동 할당한다.

| 카테고리 | 경로 패턴 | 설명 |
|----------|-----------|------|
| `development` | `phase`, `task`, `impl` | 개발 관련 문서 |
| `planning` | `planning`, `roadmap`, `master-plan` | 기획·계획 문서 |
| `review` | `qc`, `verification`, `test-report` | QC·검증 문서 |
| `rules` | `rules`, `SSOT`, `ssot`, `policy` | 규칙·정책 문서 |
| `ai` | `llm`, `reasoning`, `prompt`, `ai` | AI·추론 관련 문서 |
| `general` | (기타 모든 경로) | 일반 문서 |

### 4.2 라벨 할당 방식

```python
def classify_document(file_path: str) -> str:
    """경로 기반 카테고리 분류 (기존 seed_sample_data.py 동일 로직)"""
    path_lower = file_path.lower()
    if "phase" in path_lower and ("task" in path_lower or "plan" in path_lower):
        return "development"
    if "planning" in path_lower or "master-plan" in path_lower:
        return "planning"
    if "qc" in path_lower or "verification" in path_lower:
        return "review"
    if "rules" in path_lower or "ssot" in path_lower:
        return "rules"
    if "llm" in path_lower or "reasoning" in path_lower or "ai" in path_lower:
        return "ai"
    return "general"
```

### 4.3 AI 자동화 연동 (Phase 15-2)

- AI 자동화 워크플로우(`/api/automation/run-full`)는 문서의 청크에 **키워드·라벨**을 자동 생성
- 자동 생성된 라벨은 `knowledge_labels.source = 'ai'`, `status = 'suggested'`로 저장
- 승인 후 `status = 'confirmed'`로 변경

---

## 5. 청크 → Labels 연결

### 5.1 knowledge_labels 매핑

| 필드 | 규칙 |
|------|------|
| `chunk_id` | KnowledgeChunk.id |
| `label_id` | Label.id (keyword, domain, category 등) |
| `confidence` | 수동: 1.0, AI 생성: 0.0~1.0 |
| `source` | `"human"` (수동) 또는 `"ai"` (자동화) |
| `status` | `"confirmed"` (수동/승인) 또는 `"suggested"` (AI 미승인) |

### 5.2 knowledge_relations 매핑

| 필드 | 규칙 |
|------|------|
| `source_chunk_id` | 소스 청크 ID |
| `target_chunk_id` | 타겟 청크 ID |
| `relation_type` | `references`, `similar`, `parent_child`, `related`, `extends` |
| `confidence` | 0.0~1.0 |
| `source` | `"human"` 또는 `"ai"` |

---

## 6. 시드 데이터 흐름

```
[시드 실행]
     │
     ▼
[1] Projects 생성/매핑
     │
     ▼
[2] Labels 생성 (category, keyword, domain)
     │
     ▼
[3] Documents 생성 (--with-knowledge 시 지정 폴더 포함)
     │  ├── file_path = 절대 경로
     │  ├── project_id = 폴더명 ↔ Project 매핑
     │  └── category_label_id = 경로 기반 분류
     │
     ▼
[4] KnowledgeChunks 생성 (heading 기반 분할)
     │
     ▼
[5] KnowledgeLabels 연결 (keyword 라벨 랜덤 할당)
     │
     ▼
[6] KnowledgeRelations 생성 (청크 간 관계)
```

---

## 7. 허용 파일 확장자

`folder_service.ALLOWED_EXTENSIONS` 기준:

```
.md, .txt, .pdf, .docx, .hwp, .hwpx, .xlsx, .xls, .pptx, .ppt
```

시드 스크립트에서도 동일 확장자 목록을 사용하여 일관성 유지.
