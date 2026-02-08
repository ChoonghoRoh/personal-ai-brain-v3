# Task 5: reason.js 축소 (진입점·기능)

**순서**: 5/7  
**기준 문서**: [reason-lab-refactoring-design.md](../../reason-lab-refactoring-design.md)  
**산출물**: `web/public/js/reason/reason.js` (축소본)  
**예상 라인**: ~180줄 (500줄 이하)

---

## 1. 목표

**초기화·이벤트 바인딩**만 남기고, 나머지 로직은 model / common / control / render로 이관된 상태를 전제로 reason.js를 축소한다.

---

## 2. 담당 내용

| 구분                 | 내용                                                                                             |
| -------------------- | ------------------------------------------------------------------------------------------------ |
| **DOMContentLoaded** | initLayout(), renderHeader(…), loadOllamaModelOptions("reason-model"), loadReasoningOptions()    |
| **모드 설명**        | mode select change → mode-description 갱신 (MODE_DESCRIPTIONS 사용)                              |
| **취소 버튼**        | click → cancelReasoning (control)                                                                |
| **폼 submit**        | runReasoning(event); return false (control)                                                      |
| **시드**             | URL에 seed_chunk 있으면 loadSeedChunk(seedChunkId) 호출 (common) — 또는 common 로드 시 자동 처리 |
| **전역 노출**        | runReasoning, cancelReasoning, switchContextTab — HTML onclick 등에서 사용 가능하도록 유지       |

---

## 3. 작업 체크리스트

- [ ] reason.js에서 model/common/render/control로 이관된 코드 제거
- [ ] DOMContentLoaded 내부에 초기화·바인딩만 유지
- [ ] 모드 설명 업데이트는 ReasonModel.MODE_DESCRIPTIONS 참조
- [ ] runReasoning, cancelReasoning은 control 모듈 함수 호출로 위임
- [ ] switchContextTab은 render 모듈 함수 호출로 위임
- [ ] 파일 라인 수 500줄 이하(~180줄) 확인
- [ ] 스크립트 로드 순서 주석 유지: model → common → render → control → reason.js

---

## 4. 의존성

- **reason-model**: MODE_DESCRIPTIONS
- **reason-common**: loadReasoningOptions, loadSeedChunk
- **reason-control**: runReasoning, cancelReasoning
- **reason-render**: switchContextTab (HTML에서 직접 호출 시)
- **layout/header/ollama**: initLayout, renderHeader, loadOllamaModelOptions (기존과 동일)

---

## 5. 완료 기준

- reason.js가 설계서 4.5절 내용을 만족한다.
- 페이지 로드 시 레이아웃·헤더·옵션·모드 설명·취소/실행 바인딩이 기존과 동일하게 동작한다.
