# SSOT 버전 관리 (4th iteration)

**통합 릴리스**: `v6.0-renewal-4th`  
**릴리스 날짜**: 2026-02-17  
**전략**: **단독 사용** — claude/ 의존 제거, 4th 세트만으로 SSOT 완결

---

## 릴리스 정보

| 항목 | 내용 |
|------|------|
| **버전** | 6.0-renewal-4th (4th iteration) |
| **이전 버전** | 5.0-renewal-r3 (3rd) |
| **변경 사유** | claude 의존성 제거, 팀 라이프사이클·Phase Chain·Planner 포함, 단독 사용 가능 |
| **핵심 원칙** | **다른 SSOT 폴더(claude/ 등) 참조 없이** iterations/4th 만으로 동작 |

---

## 4th 파일 목록

| 경로 | 용도 |
|------|------|
| `0-entrypoint.md` | 진입점, 코어 개념, 팀 라이프사이클(§3.9), FRESH 규칙, 상세 링크는 4th 내부만 |
| `1-project.md` | 프로젝트·팀 구성·역할, 참조는 4th 내부만 |
| `2-architecture.md` | 인프라·BE/FE 구조·DB, 참조는 4th 내부만 |
| `3-workflow.md` | 상태 머신, ENTRYPOINT, 품질 게이트, **Phase Chain (§8)** |
| `PERSONA/LEADER.md` | Team Lead 페르소나 (docs/rules/role → 4th 통합) |
| `PERSONA/BACKEND.md` | Backend Developer 페르소나 |
| `PERSONA/FRONTEND.md` | Frontend Developer 페르소나 |
| `PERSONA/QA.md` | Verifier/Tester 페르소나 |
| `PERSONA/PLANNER.md` | **신규** Planner 페르소나 |
| `ROLES/planner.md` | **신규** Planner 역할 (Task 분해, G1, 출력 형식) |
| `ROLES/backend-dev.md` | Backend Developer (claude 링크 제거) |
| `ROLES/frontend-dev.md` | Frontend Developer (claude 링크 제거) |
| `ROLES/verifier.md` | Verifier (claude 링크 제거) |
| `ROLES/tester.md` | Tester (claude 링크 제거) |
| `GUIDES/planner-work-guide.md` | **신규** Planner 작업지시 |
| `GUIDES/backend-work-guide.md` | Backend 작업지시 |
| `GUIDES/frontend-work-guide.md` | Frontend 작업지시 |
| `GUIDES/verifier-work-guide.md` | Verifier 검증 프로세스 |
| `GUIDES/tester-work-guide.md` | Tester 테스트 프로세스 |
| `VERSION.md` | 본 문서 |

---

## Breaking Changes (3rd → 4th)

| 변경 항목 | 변경 내용 |
|----------|----------|
| **claude 의존 제거** | 모든 "기반: claude/", "➜ [상세 ...](../claude/...)" 제거. 참조는 4th 내부(0~3, ROLES, GUIDES)만 |
| **단독 사용** | claude 폴더를 지우고 4th만 사용해도 SSOT 완결. 3rd는 claude 참조가 있어 단독 불가였음 |
| **팀 라이프사이클** | 0-entrypoint §3.9에 TeamCreate → Task 스폰 → TaskCreate/Update/SendMessage → shutdown_request → TeamDelete 루프 명시 |
| **Phase Chain** | 3-workflow.md §8에 Phase Chain 정의·실행 프로토콜·/clear 복구·CHAIN-1~9 규칙 포함 (기존 claude 3-workflow-ssot §9 이식) |
| **Planner** | ROLES/planner.md, GUIDES/planner-work-guide.md 신규. G1·Task 분해·출력 형식 4th 내부에만 정의 |
| **ENTRYPOINT** | Step 6 "팀 상태 확인" 명시, 상세는 4th 3-workflow만 참조 |
| **PERSONA 통합** | docs/rules/role/ Charter 4종을 4th PERSONA/로 복사·통합. Planner 전용 PLANNER.md 신규. 4th 내부 링크는 모두 PERSONA/*.md 참조 |

---

## 권장 사용

- **기본 진입점**: `iterations/4th/0-entrypoint.md`  
- **SSOT 갱신 시**: 4th의 0~3·ROLES·GUIDES를 정답(Source of Truth)으로 유지. claude/는 참조하지 않아도 됨.  
- **Phase Chain 실행**: [3-workflow.md](3-workflow.md) §8 Phase Chain 참조.

---

## 변경 이력

### v6.0-renewal-4th (2026-02-17)
- **신규**: iterations/4th 폴더, 0-entrypoint·1-project·2-architecture·3-workflow (claude 링크 제거)
- **신규**: ROLES/planner.md, GUIDES/planner-work-guide.md
- **신규**: 3-workflow.md §8 Phase Chain (자동 순차 실행 프로토콜)
- **신규**: PERSONA/ — LEADER, BACKEND, FRONTEND, QA, PLANNER (페르소나 5종, docs/rules/role/ → 4th 통합)
- **변경**: 팀 라이프사이클 §3.9 루프 명시 (0-entrypoint)
- **변경**: 4th 내 Charter 링크 전부 PERSONA/*.md 로 변경
- **제거**: 모든 claude/ 참조

---

**문서 관리**: 버전 6.0-renewal-4th, 단독 사용(4th 세트만으로 SSOT 완결)
