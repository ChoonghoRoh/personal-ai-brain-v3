# Task 2: reason-common.js 작성 (common 레이어)

**순서**: 2/7  
**기준 문서**: [reason-lab-refactoring-design.md](../../reason-lab-refactoring-design.md)  
**산출물**: `web/public/js/reason/reason-common.js`  
**예상 라인**: ~120줄

---

## 1. 목표

**데이터 로드·페이지 공통 유틸**을 한 파일로 분리한다.  
프로젝트/라벨 옵션 로드, 시드 청크 로드, URL 파라미터 처리 등을 담당한다.

---

## 2. 담당 내용

| 함수/로직                  | 내용                                                                               |
| -------------------------- | ---------------------------------------------------------------------------------- |
| **loadReasoningOptions()** | /api/knowledge/projects, /api/labels 호출 후 projects-select, labels-select 채우기 |
| **loadSeedChunk(chunkId)** | /api/knowledge/chunks/:id 호출 후 question 필드에 내용 설정                        |
| **시드 초기화**            | URLSearchParams에서 seed_chunk 읽어서 있으면 loadSeedChunk(seedChunkId) 호출       |
| **(선택) showLoading**     | reason 전용 로딩 메시지 표시 — 전용일 경우만 common에 둠                           |

---

## 3. 작업 체크리스트

- [ ] `web/public/js/reason/reason-common.js` 파일 생성
- [ ] loadReasoningOptions 이관 (기존 reason.js에서 제거)
- [ ] loadSeedChunk 이관
- [ ] URL 파라미터·시드 처리 로직 이관 또는 common 로드 시 한 번 호출
- [ ] escapeHtml 등 utils 사용 시 의존 명시
- [ ] control·진입점에서 호출 가능하도록 전역 또는 ReasonCommon 네임스페이스로 공개

---

## 4. 의존성

- **reason-model**: 필요 시 모드·상수 참조
- **utils**: escapeHtml (옵션 렌더 시)

---

## 5. 완료 기준

- reason-common.js가 설계서 4.2절 내용을 만족한다.
- 옵션 로드·시드 청크 로드가 기존과 동일하게 동작한다.
