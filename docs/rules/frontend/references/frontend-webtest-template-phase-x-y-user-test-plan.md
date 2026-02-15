# Phase X-Y: 사용자 테스트 계획 (템플릿)

**대상 Phase**: phase-X-Y (Phase X-Y 이름)  
**목표**: Phase X-Y 범위의 웹 기능을 일반 웹 사용자 관점으로 검증합니다.

---

## 1. 범위

다음 화면·기능을 대상으로 합니다. (해당 phase 웹 체크리스트와 동일하게 작성)

- (화면1) (/경로1)
- (화면2) (/경로2)
- …

---

## 2. 참고 문서

| 문서                                                                                                            | 용도                                                         |
| --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| docs/phases/phase-X-Y/phase-X-Y-web-user-checklist.md | 웹 시나리오 체크리스트 (해당 phase에 체크리스트가 있는 경우) |
| (기타)                                                                                                          | API 검증 등 참고 문서                                        |

---

## 3. 테스트 환경

- **Base URL**: http://localhost:8001
- **백엔드**: [frontend-webtest-setup-guide.md](frontend-webtest-setup-guide.md) 참조
- **브라우저**: Chrome, Edge 등 권장
- **선택**: 해당 phase에서 필요한 DB/LLM/외부 서비스 요구사항

---

## 4. 수행 절차

[frontend-webtest-phase-unit-user-test-guide.md](frontend-webtest-phase-unit-user-test-guide.md)에 따릅니다.

1. 본 테스트 계획에서 범위·목표·시나리오 확인
2. 해당 phase 웹 체크리스트대로 브라우저에서 실행
3. 일반 웹 사용자 관점 유지 ([frontend-webtest-personas.md](frontend-webtest-personas.md))
4. 관점별 프롬프트([docs/webtest/prompts/](../../../webtest/prompts/)) 중 하나 선택 후 발견 사항 기록
5. 결과는 체크리스트의 “결과/비고”란 또는 아래 요약 표에 기록

---

## 5. 결과 기록 요약

| 메뉴(라우터) | 총 항목 | 성공 | 실패 | 비고 |
| ------------ | ------- | ---- | ---- | ---- |
| (메뉴1)      |         |      |      |      |
| **합계**     |         |      |      |      |

**테스트 수행일**: \_\_\_\_\_\_\_\_  
**테스트 수행자**: \_\_\_\_\_\_\_\_  
**관점(기획자/개발자/UIUX)**: \_\_\_\_\_\_\_\_

---

**템플릿 사용법**: 이 파일을 `docs/webtest/phase-<X>-<Y>/phase-<X>-<Y>-user-test-plan.md` 로 복사한 뒤, "phase-X-Y", "Phase X-Y 이름", 범위·참고 문서를 해당 phase에 맞게 치환하세요.
