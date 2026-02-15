# Phase 9-3: 사용자 테스트 계획

**대상 Phase**: 9-3 (AI 기능 고도화)  
**목표**: Phase 9-3 범위의 웹 기능을 일반 웹 사용자 관점으로 검증합니다.

---

## 1. 범위

다음 화면·기능을 대상으로 합니다. (기존 웹 체크리스트와 동일)

- 대시보드 (/dashboard)
- 검색 (/search) — Task 9-3-3 RAG
- AI 질의 (/ask) — Task 9-3-3 RAG
- Reasoning Lab (/reason) — Task 9-3-1
- 지식 구조 목록·상세·라벨/관계 매칭 (/knowledge, /knowledge-detail, /knowledge-label-matching, /knowledge-relation-matching)
- 지식 관리·청크 승인 (/knowledge-admin)
- 청크 승인 센터 (/admin/approval)
- 청크 관리 (/admin/chunk-labels)
- 청크 생성 (/admin/chunk-create)

---

## 2. 참고 문서

| 문서                                                                                                                            | 용도                                               |
| ------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| [docs/phases/phase-9-3/phase-9-3-web-user-checklist.md](../../phases/phase-9-3/phase-9-3-web-user-checklist.md)                 | 웹 시나리오 체크리스트 (메뉴별 시나리오·결과/비고) |
| [docs/phases/phase-9-3/phase-9-3-api-verification-checklist.md](../../phases/phase-9-3/phase-9-3-api-verification-checklist.md) | API 검증 (참고용)                                  |

---

## 3. 테스트 환경

- **Base URL**: http://localhost:8001
- **백엔드**: Docker Compose 또는 로컬 uvicorn으로 기동 (상세: [web-user-test-setup-guide.md](../web-user-test-setup-guide.md))
- **브라우저**: Chrome, Edge 등 최신 데스크톱 브라우저 권장
- **선택**: AI 질의·Reasoning·키워드 추천 테스트 시 Ollama(로컬 LLM) 동작 필요

---

## 4. 수행 절차

[phase-unit-user-test-guide.md](../phase-unit-user-test-guide.md)에 따릅니다.

1. 본 테스트 계획에서 범위·목표·시나리오 확인
2. [phase-9-3-web-user-checklist.md](../../phases/phase-9-3/phase-9-3-web-user-checklist.md) 체크리스트대로 브라우저에서 실행
3. 일반 웹 사용자 관점 유지 ([personas.md](../personas.md))
4. 관점별 프롬프트([prompts/](../prompts/)) 중 하나 선택 후 발견 사항 기록
5. 결과는 체크리스트의 “결과/비고”란 또는 아래 요약 표에 기록

---

## 5. E2E 자동 실행 (Playwright)

체크리스트를 **Playwright E2E**로 자동 실행할 수 있습니다. 백엔드가 Base URL에서 기동 중이어야 합니다.

```bash
npx playwright test phase-9-3
# 또는
npm run test:e2e -- --grep "phase-9-3"
```

- **스펙 파일**: 프로젝트 루트 `e2e/phase-9-3.spec.js` (체크리스트 W1.x ~ W12.x에 대응)
- **상세**: [web-user-test-setup-guide.md](../web-user-test-setup-guide.md) 3.2절

---

## 6. 개발·테스트 최종 요약 및 관점별 보고서

3관점(Planner / Developer / Designer) 결과를 통합한 **최종 요약 문서**와, 관점별 상세 보고서는 아래에서 확인합니다.

| 문서                                                                           | 용도                                                  |
| ------------------------------------------------------------------------------ | ----------------------------------------------------- |
| **[phase-9-3-final-summary.md](phase-9-3-final-summary.md)**                   | 개발·테스트 최종 보고 (3관점 통합, 액션 아이템, 결론) |
| [reports/phase-9-3-report-planner.md](reports/phase-9-3-report-planner.md)     | 꼼꼼한 기획자 관점 상세                               |
| [reports/phase-9-3-report-developer.md](reports/phase-9-3-report-developer.md) | 개발자 관점 상세                                      |
| [reports/phase-9-3-report-uiux.md](reports/phase-9-3-report-uiux.md)           | UI·UX 디자이너 관점 상세                              |

---

## 7. 결과 기록 요약

| 메뉴(라우터)                  | 총 항목 | 성공 | 실패 | 비고 |
| ----------------------------- | ------- | ---- | ---- | ---- |
| 대시보드                      |         |      |      |      |
| 검색                          |         |      |      |      |
| Ask                           |         |      |      |      |
| Reasoning Lab                 |         |      |      |      |
| 지식 구조·상세·라벨/관계 매칭 |         |      |      |      |
| 지식 관리·청크 승인           |         |      |      |      |
| 청크 관리·청크 생성           |         |      |      |      |
| **합계**                      |         |      |      |      |

**테스트 수행일**: \_\_\_\_\_\_\_\_  
**테스트 수행자**: \_\_\_\_\_\_\_\_  
**관점(기획자/개발자/UIUX)**: \_\_\_\_\_\_\_\_
