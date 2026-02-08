# 이슈 및 향후 진행

**수정 시**: 알려진 이슈·향후 계획 변경 시 이 파일을 갱신. AI가 "다음에 뭘 할지" 판단할 때 참고.

---

## 알려진 이슈·개발 과정 (요약)

| 구분 | 내용 |
|------|------|
| **Phase 8 워크플로우** | 보류. n8n 워크플로우 개발은 별도 프로젝트 권장. [phase-8-wrap-up.md](../phases/phase-8-wrap-up.md) |
| **n8n Docker** | 기본 실행 시 n8n 컨테이너는 기동하지 않음. `docker-compose.yml`에서 n8n 서비스·n8n_data 볼륨이 주석 처리됨. 재활성화 시 해당 블록 주석 해제. |
| **리팩토링 시** | n8n 관련 부분(n8n 서비스, docs/n8n, Phase 8-2 워크플로우 전용 문서·JSON)은 제외하고 진행. [phase-8-wrap-up.md](../phases/phase-8-wrap-up.md) §본 프로젝트 리팩토링 시 |

---

## 향후 계획 (요약)

| 항목 | 상태 | 비고 |
|------|------|------|
| HWP 파일 지원 | 계획 | Phase 9 등으로 이관 가능 |
| 통계·분석 대시보드 | 계획 | |
| 백업·복원 시스템 | 계획 | |
| Phase 8 전체 워크플로우 개발 | **보류** | [phase-8-wrap-up.md](../phases/phase-8-wrap-up.md) — 별도 프로젝트 권장 |
| Phase 8-2-4 Discord 승인 루프 | 보류 | n8n 워크플로우 구축 필요 |
| Phase 8-2-5 Todo-List 생성 | 보류 | 8-2-4 의존 |
| Phase 8-2-8 Task 테스트·결과 저장 | 보류 | workflow_test_results·task-N-result.md |

---

## 완료된 기능 (체크용)

- 자동 기록·Git 자동 커밋·PDF/DOCX 지원·시스템 관리 AI·통합 작업 로그
- Web UI(대시보드, 검색, 문서 뷰어, Ask, Logs, Knowledge, Reason, Admin)
- PostgreSQL 지식 DB·라벨·관계·Reasoning Pipeline·Knowledge Studio/Admin
- 키워드 추출·자동 라벨링·Trustable Knowledge Pipeline·Ollama 전환
- Phase 8.0.0 성능 최적화·인격체 모델
- Phase 8.1~8.3: n8n DB·Task Plan v1/v2·Task 실행 API·Docker·Ollama

상세: [03-development-progress.md](./03-development-progress.md), [03-phase-1-4.md](./03-phase-1-4.md), [03-phase-5-7.md](./03-phase-5-7.md), [03-phase-8.md](./03-phase-8.md), `docs/phases/phase8-master-plan.md`.
