# Phase 7.7 남은 작업 체크리스트

**작성일**: 2026-01-07

## 완료 기준 대비 진행 상황

### 1. DB/모델 ✅ 완료

- ✅ `labels.label_type`, `labels.parent_label_id` 적용
- ✅ `documents.category_label_id` 적용
- ⚠️ (선택) `label_embeddings` 테이블 생성 - **선택 사항이므로 제외**

### 2. API ✅ 완료

- ✅ 키워드 그룹 CRUD API 동작 (`GET/POST/PATCH/DELETE /api/labels/groups`)
- ✅ 그룹-키워드 연결/해제 API 동작 (`GET/POST/DELETE /api/labels/groups/{id}/keywords`)
- ✅ 청크-라벨 연결/해제 API 동작 (`POST/DELETE /api/knowledge/chunks/{id}/labels`)
- ✅ Reasoning 필터 확장 적용 (keyword_group/category)

### 3. UI ⚠️ 부분 완료

- ✅ Knowledge Admin에 Keyword Group Management 보드 추가
- ✅ Knowledge Studio 청크 상세에 라벨 매칭 카드 추가
- ❌ **청크 관계 매칭 보드 추가 (기본 버전)** - **미완료**

### 4. Reasoning/검색 ✅ 완료

- ✅ keyword_group, category 필터 기반 Reasoning이 정상 동작
- ✅ 승인된 청크 + 확정 관계만 컨텍스트로 사용되는 기존 원칙 유지

### 5. 문서화 & 테스트 ✅ 완료

- ✅ `docs/dev/phase7-7-upgrade.md` 작성 완료
- ✅ 청크 상세 라벨 매칭 카드 테스트 문서 작성 완료

---

## 남은 작업: 청크 관계 매칭 보드 (4.3)

### 요구사항

**사용 위치**: `/knowledge`에서 청크 선택 후 "관계" 탭

#### 레이아웃

- 좌측: 기준 청크 카드
- 중앙: **이미 연결된 관계 카드 리스트**
- 우측: **AI 추천 관계 카드 리스트**
- 하단: 선택된 추천 관계 요약 + 한 번에 연결 버튼

#### 카드 구조

**기존 관계 카드:**

- 대상 청크 요약 텍스트
- 관계 타입 배지 (`similar`, `explains`, `result_of` 등)
- 확정 여부 (✔ 확정 / ⏳ 제안)
- [해제] 버튼 → 관계 삭제 또는 `confirmed=false`

**추천 관계 카드:**

- 대상 청크 요약 텍스트
- 유사도 점수/막대
- 공유 키워드/그룹 1~3개
- [연결], [무시] 버튼

### 구현 필요 사항

1. **UI 구현**

   - 청크 상세에 "관계" 탭 추가 (현재는 "라벨 매칭"만 있음)
   - 3단 레이아웃 (좌측: 기준 청크, 중앙: 기존 관계, 우측: 추천 관계)
   - 관계 카드 컴포넌트 구현
   - 다중 선택 및 일괄 연결 기능

2. **API 연동**

   - `POST /api/knowledge/relations/suggest` - 관계 추천 조회 (이미 구현됨)
   - `POST /api/knowledge/relations/suggest/{chunk_id}/apply` - 추천 관계 적용 (이미 구현됨)
   - 기존 관계 조회 (이미 `GET /api/knowledge/chunks/{id}`에 포함됨)
   - 관계 삭제/확정 해제 API

3. **기능**
   - 추천 관계 목록 표시
   - 관계 연결/무시 기능
   - 기존 관계 해제 기능
   - 다중 선택 및 일괄 연결

### 현재 상태

- ✅ 관계 추천 API는 이미 구현되어 있음 (`backend/routers/suggestions.py`)
- ✅ 청크 상세에 기존 관계는 표시되고 있음 (나가는/들어오는 관계)
- ✅ 관계 매칭 보드 UI 구현 완료 (Phase 7.9.1)
- ✅ "관계" 탭 구현 완료 (Phase 7.9.1)

---

## 우선순위

### 높음 (필수)

- ✅ 청크 관계 매칭 보드 UI 구현 (Phase 7.9.1 완료)

### 중간 (권장)

- ✅ 관계 카드에 공유 키워드/그룹 표시 (Phase 7.9.1 완료)
- ✅ 유사도 점수 시각화 (막대 그래프) (Phase 7.9.1 완료)

### 낮음 (선택)

- ✅ 다중 선택 및 일괄 연결 기능 (Phase 7.9.1 완료)
- ✅ 관계 타입별 필터링 (Phase 7.9.3 완료)

---

## 완료된 작업 (Phase 7.9.1)

1. ✅ **청크 상세에 "관계" 탭 추가**

   - "라벨 매칭" 탭 옆에 "관계 매칭" 탭 추가 완료
   - 탭 전환 기능 구현 완료

2. ✅ **관계 매칭 보드 레이아웃 구현**

   - 3단 레이아웃 (좌측: 기준 청크, 중앙: 기존 관계, 우측: 추천 관계) 완료
   - 관계 카드 컴포넌트 스타일링 완료
   - 반응형 디자인 적용

3. ✅ **추천 관계 표시 및 연결 기능**

   - API 연동 완료
   - 카드 클릭 및 버튼 동작 구현
   - 다중 선택 및 일괄 연결 기능 구현

4. ✅ **기존 관계 관리 기능**

   - 관계 해제 기능 구현
   - 확정/제안 상태 구분 및 확인 메시지 개선

5. ✅ **추가 기능**
   - 공유 키워드/그룹 표시 (최대 3개)
   - 유사도 점수 시각화 (색상 그라데이션 막대 그래프)
   - 관계 카드 호버 효과 및 선택 상태 표시

## 완료된 추가 작업 (Phase 7.9.3)

1. ✅ **관계 타입별 필터링**
   - 기존 관계 및 추천 관계 영역에 필터 버튼 그룹 추가
   - 관계 타입별 필터링 기능 구현 (similar, explains, result_of, cause_of, refers_to)
   - "전체" 선택 기능
   - 필터 상태 유지
   - 관계 타입별 색상 구분

## 다음 단계 (선택 사항)

1. **테스트 및 문서화**
   - 테스트 시나리오 작성
   - 테스트 수행 및 결과 문서화

---

## 참고 문서

- `docs/dev/phase7-7-upgrade.md` - Phase 7.7 상세 설계 문서 (4.3 섹션)
- `docs/dev/phase7-9-1-relation-matching-board.md` - Phase 7.9.1 개발 문서 (완료)
- `docs/dev/phase7-9-3-relation-type-filtering.md` - Phase 7.9.3 개발 문서 (완료)
- `backend/routers/suggestions.py` - 관계 추천 API 구현
- `web/src/pages/knowledge.html` - Knowledge Studio 페이지 (구현 완료)
