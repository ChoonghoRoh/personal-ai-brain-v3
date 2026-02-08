# Phase 7.7: Keyword Grouping & Category Layer Upgrade

## 0. 개요

Phase 7.7은 **키워드 그룹(테마)과 문서 카테고리 레이어를 추가**하여, 지식을 더 사람 친화적으로 정리하고 Reasoning/검색/관리 UX를 개선하는 단계이다.

Phase 7.5~7.6에서 이미 다음을 구축했다.
- Trustable Knowledge Pipeline (청크 승인/거절, AI 라벨/관계 추천)
- 키워드 자동 추출 및 자동 라벨링
- Knowledge Studio / Reasoning Lab / Knowledge Admin v0

Phase 7.7의 핵심 방향은 다음과 같다.

> **“키워드 → 키워드 그룹 → 문서/청크”의 계층을 명확히 만들고,
>  카드형 매칭 UI를 통해 라벨/그룹/관계를 쉽게 관리할 수 있게 한다.**

---

## 1. 목표

### 1.1 구조적 목표

1. 키워드를 단일 태그 수준에서 **키워드 그룹(테마)** 단위로 확장
2. 문서 카테고리/프로젝트/도메인 레이어를 명시적으로 도입
3. 청크(knowledge_chunk)가 키워드/키워드 그룹/카테고리와 연결되는 구조를 정리

### 1.2 UX 목표

1. 기존의 "리스트 + 버튼" 중심 UI 위에 **카드 기반 매칭 보드**를 추가
2. 마우스 클릭만으로도:
   - 그룹 생성/수정/삭제
   - 그룹에 키워드 추가/제거
   - 청크에 키워드/키워드 그룹 연결
   - 청크 간 관계(유사/관련) 연결
   을 편하게 수행할 수 있게 한다.
3. 다중 선택 및 한 번에 연결/해제 가능한 "매칭 모드"를 제공

### 1.3 Reasoning/검색 목표

1. 키워드 하나뿐 아니라 **키워드 그룹 단위**로 Reasoning 컨텍스트를 선택 가능
2. 프로젝트/카테고리/키워드 그룹 조합으로 질문을 던질 수 있도록 필터 확장
3. 승인된 지식(approved chunks) + 확정 관계(confirmed relations)만 사용한다는 원칙 유지

---

## 2. DB 스키마 상세 설계

### 2.1 labels 테이블 확장

#### 2.1.1 요구사항

- 기존 `labels` 테이블은 라벨의 이름, 타입, 설명 정도를 관리
- Phase 7.7에서는 다음을 추가로 필요로 함
  - **라벨 타입 세분화**: `keyword`, `keyword_group`, `category`, `project`, `domain` 등
  - **계층 구조**: 키워드가 어떤 그룹(테마)에 속하는지 표현 (`parent_label_id`)
  - (선택) UI용 색상 정보(`color`)

#### 2.1.2 변경 후 스키마 (논리)

```text
labels
- id              (PK, int)
- name            (varchar)
- label_type      (varchar)   # 'keyword' | 'keyword_group' | 'category' | 'project' | 'domain' | ...
- parent_label_id (int, FK → labels.id, nullable)
- description     (text, nullable)
- color           (varchar, nullable)   # UI에서 그룹/카테고리 구분용
- created_at      (timestamp)
- updated_at      (timestamp)
```

#### 2.1.3 label_type 사용 규칙

- `keyword`
  - 자동 추출 키워드, 수동 추가 키워드 모두 포함
  - 선택적으로 `parent_label_id`를 통해 `keyword_group`에 속할 수 있음

- `keyword_group`
  - 특정 테마/주제를 나타내는 상위 개념
  - 예: `AI 인프라`, `지식 구조 설계`, `농업ON 서비스 기획`
  - `parent_label_id`는 일반적으로 `NULL` (필요시 상위 그룹도 가능)

- `category` / `project` / `domain`
  - 문서/청크의 상위 분류(프로젝트/도메인/업무 카테고리)
  - 문서/청크에 직접 연결되어 필터링 기준으로 사용

---

### 2.2 chunk_labels 테이블 재사용

기존 `chunk_labels` 테이블을 그대로 사용하되, 여기에 **키워드 그룹과 카테고리도 연결**될 수 있도록 한다.

```text
chunk_labels
- id          (PK, int)
- chunk_id    (FK → knowledge_chunks.id)
- label_id    (FK → labels.id)
- status      (varchar)  # 'suggested' | 'confirmed' | 'rejected'
- source      (varchar)  # 'ai' | 'human'
- confidence  (float, nullable)
- created_at  (timestamp)
```

사용 규칙:
- `label_type = 'keyword'` 라벨 → 청크에 개별 키워드 태그로 연결
- `label_type = 'keyword_group'` 라벨 → 청크에 테마 단위로 연결
- `label_type = 'category'` / `project` / `domain` 라벨 → 상위 분류로 연결

---

### 2.3 documents 테이블 카테고리 연계

문서 레벨에서 카테고리/프로젝트를 직접 연결하기 위해 다음과 같이 확장한다.

```text
documents
- id               (PK, int)
- project_id       (FK → projects.id, nullable)
- document_path    (varchar)
- title            (varchar)
- doc_type         (varchar)
- created_at       (timestamp)
- updated_at       (timestamp)
- category_label_id (int, FK → labels.id, nullable)   # label_type IN ('category', 'project', 'domain')
```

사용 예:
- `category_label_id` → `project:personal_ai_brain` 라벨
- 또는 `domain:agrion`, `category:ai_research` 등으로 유연하게 사용 가능

---

### 2.4 label_embeddings 테이블 (선택, 확장용)

키워드/그룹/카테고리 간의 유사도를 계산하고, "유사 키워드/그룹 추천" 기능을 위해 라벨 자체 임베딩을 저장하는 테이블을 추가한다.

```text
label_embeddings
- label_id        (PK, FK → labels.id)
- embedding       (vector or jsonb)  # DB 타입에 따라 결정
- updated_at      (timestamp)
```

임베딩 생성 전략:
- `keyword`
  - 해당 키워드가 붙은 청크 임베딩들의 평균값
- `keyword_group`
  - 그룹에 속한 키워드 임베딩의 평균값
  - 또는 그룹 설명 텍스트를 임베딩한 값
- `category`/`project`
  - 그 카테고리에 속한 문서/청크 임베딩의 평균값

이 테이블은 Phase 7.7에서 필수는 아니지만, 아래 기능들에서 사용 가능하다.
- 유사 키워드 추천
- 유사 키워드 그룹 추천
- 카테고리 간 관계 분석

---

## 3. API 상세 설계

### 3.1 키워드 그룹 관리 API

#### 3.1.1 키워드 그룹 목록 조회

- **Method**: `GET`
- **Path**: `/api/labels/groups`
- **Query Params**:
  - `q` (optional): 그룹 이름 검색 키워드
  - `limit` (optional, default=50)
  - `offset` (optional, default=0)

- **동작**:
  - `label_type = 'keyword_group'` 인 라벨만 반환

- **Response (예시)**

```json
[
  {
    "id": 1,
    "name": "AI 인프라",
    "label_type": "keyword_group",
    "description": "벡터 DB, 임베딩, GPU 등 인프라 관련 키워드 그룹",
    "color": "#4F46E5",
    "created_at": "2026-01-07T10:00:00",
    "updated_at": "2026-01-07T10:10:00"
  }
]
```

---

#### 3.1.2 키워드 그룹 생성

- **Method**: `POST`
- **Path**: `/api/labels/groups`

- **Request Body (예시)**

```json
{
  "name": "AI 인프라",
  "description": "벡터 DB, 임베딩, GPU 등 인프라 관련 키워드 그룹",
  "color": "#4F46E5"
}
```

- **동작**:
  - `labels` 테이블에 `label_type = 'keyword_group'`으로 라벨 생성

- **Response (예시)**

```json
{
  "id": 1,
  "name": "AI 인프라",
  "label_type": "keyword_group",
  "description": "벡터 DB, 임베딩, GPU 등 인프라 관련 키워드 그룹",
  "color": "#4F46E5"
}
```

---

#### 3.1.3 키워드 그룹 수정

- **Method**: `PATCH`
- **Path**: `/api/labels/groups/{group_id}`

- **Request Body (예시)**

```json
{
  "name": "AI 인프라(Backend)",
  "description": "백엔드 인프라 중심 AI 키워드 그룹",
  "color": "#4338CA"
}
```

- **동작**:
  - 이름/설명/색상만 수정 (label_type은 변경 불가)

---

#### 3.1.4 키워드 그룹 삭제

- **Method**: `DELETE`
- **Path**: `/api/labels/groups/{group_id}`

- **동작**:
  - `labels`에서 해당 group 라벨 삭제
  - 이 그룹에 속한 키워드의 `parent_label_id`를 `NULL`로 변경
  - `chunk_labels`에서 이 그룹 라벨이 연결된 항목은 그대로 유지/삭제 중 선택 (초기 버전: 유지)

---

### 3.2 그룹 내 키워드 관리 API

#### 3.2.1 그룹 내 키워드 목록 조회

- **Method**: `GET`
- **Path**: `/api/labels/groups/{group_id}/keywords`

- **동작**:
  - `labels`에서 `label_type = 'keyword'`이고 `parent_label_id = group_id`인 라벨 반환

- **Response (예시)**

```json
[
  {
    "id": 10,
    "name": "벡터 DB",
    "label_type": "keyword",
    "parent_label_id": 1
  },
  {
    "id": 11,
    "name": "임베딩",
    "label_type": "keyword",
    "parent_label_id": 1
  }
]
```

---

#### 3.2.2 그룹에 키워드 추가

- **Method**: `POST`
- **Path**: `/api/labels/groups/{group_id}/keywords`

- **Request Body (옵션 2가지)**

1) 기존 키워드 ID를 그룹에 연결

```json
{
  "keyword_ids": [10, 11, 12]
}
```

2) 새 키워드 생성 + 그룹 연결

```json
{
  "keyword_names": ["벡터 DB", "임베딩", "Qdrant"]
}
```

- **동작**:
  - mode 1: 해당 ID의 `labels` 레코드에 `parent_label_id = group_id` 설정
  - mode 2: 없는 키워드를 `label_type='keyword'`로 생성 후 `parent_label_id=group_id`

---

#### 3.2.3 그룹에서 키워드 제거

- **Method**: `DELETE`
- **Path**: `/api/labels/groups/{group_id}/keywords/{keyword_id}`

- **동작**:
  - `labels`에서 해당 keyword의 `parent_label_id`를 `NULL`로 변경
  - 키워드 라벨 자체는 삭제하지 않음

---

### 3.3 청크 ↔ 키워드/그룹 라벨 연결 API

청크에 키워드/키워드 그룹/카테고리를 연결하는 API를 정리한다.

#### 3.3.1 청크에 라벨 추가

- **Method**: `POST`
- **Path**: `/api/knowledge/chunks/{chunk_id}/labels`

- **Request Body (예시)**

```json
{
  "label_ids": [1, 10, 11],
  "status": "confirmed",
  "source": "human"
}
```

- **동작**:
  - `chunk_labels`에 `(chunk_id, label_id)` 조합을 생성하거나 상태/소스를 업데이트
  - label_id는 keyword/keyword_group/category 등 어떤 타입도 허용

---

#### 3.3.2 청크에서 라벨 제거

- **Method**: `DELETE`
- **Path**: `/api/knowledge/chunks/{chunk_id}/labels`

- **Request Body (예시)**

```json
{
  "label_ids": [1, 10]
}
```

- **동작**:
  - 해당 `(chunk_id, label_id)` 조합을 `chunk_labels`에서 삭제 또는 `status='rejected'`로 업데이트 (초기 버전: 삭제)

---

#### 3.3.3 청크 라벨 목록 조회

- **Method**: `GET`
- **Path**: `/api/knowledge/chunks/{chunk_id}/labels`

- **동작**:
  - 해당 청크의 모든 라벨 + 라벨 타입 정보 반환

- **Response (예시)**

```json
{
  "chunk_id": 100,
  "labels": [
    {
      "id": 1,
      "name": "AI 인프라",
      "label_type": "keyword_group",
      "status": "confirmed"
    },
    {
      "id": 10,
      "name": "벡터 DB",
      "label_type": "keyword",
      "status": "confirmed"
    }
  ]
}
```

---

### 3.4 카테고리/프로젝트 라벨 API (문서/청크 레벨)

#### 3.4.1 문서 카테고리 설정

- **Method**: `POST`
- **Path**: `/api/documents/{document_id}/category`

- **Request Body (예시)**

```json
{
  "label_id": 200   
}
```

- **동작**:
  - `documents.category_label_id = label_id`
  - `label_id`는 `label_type IN ('category', 'project', 'domain')`여야 함

---

#### 3.4.2 카테고리별 문서 목록 조회

- **Method**: `GET`
- **Path**: `/api/documents`

- **Query Params**:
  - `category_label_id` (optional)
  - `label_type` (optional) – 필터링 용도

- **동작**:
  - `category_label_id` 조건이 있으면 해당 카테고리 문서만 반환

---

### 3.5 Reasoning 필터 확장 API

Reasoning API에 키워드 그룹/카테고리 필터를 추가한다.

#### 3.5.1 Reasoning 요청 스키마 확장

- **Path**: `POST /api/reason`

- **Request Body (추가 필드)**

```json
{
  "mode": "design_explain",
  "filters": {
    "project_ids": [1, 2],
    "category_label_ids": [200, 201],
    "keyword_group_ids": [1, 3],
    "keyword_ids": [10, 11]
  },
  "question": "Phase 7.7 설계 방향을 설명해줘"
}
```

- **동작**:
  - 필터 정보는 다음 순서로 적용한다.
    1. project / category 필터로 문서/청크 1차 제한
    2. keyword_group / keyword 필터로 관련 청크 추가 필터링
    3. 승인된 청크(`status='approved'`)만 컨텍스트 후보로 사용

---

## 4. UI/UX 상세 설계 (카드 & 매칭 모드)

### 4.1 Keyword Group Management 보드

사용 위치: `/knowledge-admin` 내 탭 또는 별도 경로 `/knowledge-admin#groups`

#### 4.1.1 레이아웃

- 상단 Bar
  - 검색 입력창 (그룹/키워드 이름 검색)
  - [매칭 모드 ON/OFF] 토글 버튼

- 좌측 컬럼: **키워드 그룹 카드 리스트**
  - 각 카드: 그룹 이름, 설명, 색상, 포함된 키워드 수

- 우측 컬럼: **키워드 카드 리스트**
  - 각 카드: 키워드 이름, 사용 횟수, 속한 그룹 이름

- 하단 고정 바: **선택 요약 + 일괄 적용 버튼**
  - 텍스트 예: `선택된 그룹: AI 인프라 · 선택된 키워드: 7개`
  - 버튼: `[이 그룹에 연결] [연결 해제] [선택 취소]`

#### 4.1.2 상호작용

1. 매칭 모드 ON
2. 좌측에서 그룹 카드 하나 클릭 → "선택된 그룹" 상태
3. 우측 키워드 카드 여러 개 클릭 → 선택 토글
4. 하단에서 [이 그룹에 연결] 클릭 → API 호출
   - `POST /api/labels/groups/{group_id}/keywords`
   - body: `{ "keyword_ids": [...] }`

- 선택 상태는 CSS 클래스(`.selected`)로 표시
- 매칭 모드 OFF 시 선택 상태 초기화

---

### 4.2 청크 상세 + 라벨 매칭 카드

사용 위치: `/knowledge` (Knowledge Studio)에서 특정 청크 선택 시 우측 패널

#### 4.2.1 레이아웃

- 상단: 청크 미리보기 (제목/앞부분 텍스트 1~2줄)
- 중단: 본문 일부
- 하단: 라벨 영역
  - [연결된 키워드 그룹] 칩 리스트
  - [연결된 키워드] 칩 리스트
- 우측/하단: "라벨 매칭" 카드 패널

#### 4.2.2 라벨 칩 동작

- 칩 클릭: 선택 토글 (스타일만 변경)
- 칩의 X 버튼: 해당 라벨 삭제
  - `DELETE /api/knowledge/chunks/{chunk_id}/labels` 호출

#### 4.2.3 라벨 매칭 카드 패널

탭 구성:
- `추천 키워드`
- `추천 그룹`

각 카드 내용:
- 라벨 이름
- 라벨 타입 (키워드/그룹)
- 추천 이유 (공유 키워드/청크 수 등)
- [추가] 버튼

동작:
- [추가] 클릭 →
  - `POST /api/knowledge/chunks/{chunk_id}/labels`
  - body: `{ "label_ids": [라벨ID], "status": "confirmed", "source": "human" }`
- 이미 연결된 라벨은 "연결됨" 상태로 비활성화

---

### 4.3 청크 관계(유사도/관련성) 매칭 보드

사용 위치: `/knowledge`에서 청크 선택 후 "관계" 탭

#### 4.3.1 레이아웃

- 좌측: 기준 청크 카드
- 중앙: **이미 연결된 관계 카드 리스트**
- 우측: **AI 추천 관계 카드 리스트**
- 하단: 선택된 추천 관계 요약 + 한 번에 연결 버튼

#### 4.3.2 카드 구조

- 기존 관계 카드
  - 대상 청크 요약 텍스트
  - 관계 타입 배지 (`similar`, `explains`, `result_of` 등)
  - 확정 여부 (✔ 확정 / ⏳ 제안)
  - [해제] 버튼 → 관계 삭제 또는 `confirmed=false`

- 추천 관계 카드
  - 대상 청크 요약 텍스트
  - 유사도 점수/막대
  - 공유 키워드/그룹 1~3개
  - [연결], [무시] 버튼

---

## 5. 테스트 전략

### 5.1 단위 테스트

- DB 레벨
  - label_type/parent_label_id 제약 조건 테스트
  - 카테고리/프로젝트 라벨 유효성 테스트
- API 레벨
  - 그룹 CRUD
  - 그룹-키워드 추가/제거
  - 청크-라벨 추가/제거
  - Reasoning 필터 조합 테스트

### 5.2 통합 테스트 시나리오 (예시)

1. 새 키워드 그룹 `AI 인프라` 생성
2. 자동 추출된 키워드 중 `벡터 DB`, `임베딩`, `Qdrant`를 그룹에 연결
3. AI 브레인 관련 청크 5개에 `AI 인프라` 그룹 라벨 연결
4. Reasoning Lab에서
   - filter: `keyword_group_ids = [AI 인프라]`
   - 질문: "AI 인프라 관련 설계 의사결정을 요약해줘"
   - → 컨텍스트 청크에 해당 그룹이 연결된 청크들만 포함되는지 확인

---

## 6. 리스크 & 대응

| 리스크 | 설명 | 대응 |
|--------|------|------|
| 라벨 타입 복잡도 증가 | label_type이 늘어나면 관리가 어려울 수 있음 | 초기에는 keyword / keyword_group / category 3가지만 적극 사용, 나머지는 추후 도입 |
| UX 과부하 | 새 UI가 많아져서 복잡해 보일 위험 | 카드/매칭 패턴을 세 화면에서 공통으로 사용하여 학습 비용 최소화 |
| 자동 추천 품질 | 추천 키워드/관계가 부정확할 수 있음 | 항상 suggested 상태로 제공, Human-in-the-loop 승인 구조 유지 |
| 성능 문제 | 유사도 계산/검색이 늘어날 수 있음 | label_embeddings 도입 시 배치 업데이트 + 캐싱 고려 |

---

## 7. Phase 7.7 완료 기준 (Definition of Done)

1. **DB/모델**
   - `labels.label_type`, `labels.parent_label_id` 적용
   - `documents.category_label_id` 적용
   - (선택) `label_embeddings` 테이블 생성

2. **API**
   - 키워드 그룹 CRUD API 동작
   - 그룹-키워드 연결/해제 API 동작
   - 청크-라벨 연결/해제 API 동작
   - Reasoning 필터 확장 적용 (keyword_group/category)

3. **UI**
   - Knowledge Admin에 Keyword Group Management 보드 추가
   - Knowledge Studio 청크 상세에 라벨 매칭 카드 추가
   - 청크 관계 매칭 보드 추가 (기본 버전)

4. **Reasoning/검색**
   - keyword_group, category 필터 기반 Reasoning이 정상 동작
   - 승인된 청크 + 확정 관계만 컨텍스트로 사용되는 기존 원칙 유지

5. **문서화 & 테스트**
   - `docs/dev/phase7-7-upgrade.md` (본 문서) 작성 완료
   - 기본 통합 테스트 스크립트(예: `scripts/test_phase7_7.py`) 추가 및 실행

---

## 8. 이후 확장 아이디어 (Phase 8候補)

- keyword_group / category를 기반으로 한 **온톨로지/트리 구조** 확장
- label_embeddings 기반 **자동 그룹 제안/병합 추천**
- "이 문서/청크는 어떤 테마에 속하나요?"에 대한 자동 분류 에이전트
- 멀티 에이전트 구조에서 프로젝트/카테고리/그룹별 전담 에이전트 구성

