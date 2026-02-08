# Phase 8 마무리: n8n 워크플로우 개발 보류

**작성일**: 2026-02-01  
**관련 문서**: [phase8-master-plan.md](./phase8-master-plan.md), [phase8-2-6-task-test-plan-generation.md](./phase-8-2/tasks/phase8-2-6-task-test-plan-generation.md), [phase8-2-7-task-execution-workflow.md](./phase-8-2/tasks/phase8-2-7-task-execution-workflow.md)

---

## 결론

**Phase 8 전체 워크플로우 개발을 보류하고, 본 프로젝트(Personal AI Brain) 내 Phase 8을 여기서 마무리합니다.**  
워크플로우 자동화까지 완성하려면 rule·프롬프트·Claude Code 토큰·범위 등 디테일한 개발·디버깅에 드는 시간이 과도하므로, **별도 프로젝트로 진행하는 것이 적절**하다는 판단입니다.

---

## 보류 사유 (정리)

1. **개발 시간 과다**
   - 워크플로우 개발에 사용하는 시간이 지나치게 많음.
   - 본 프로젝트의 핵심(지식 저장·검색·Reasoning·웹 UI 등) 대비, 자동화 파이프라인 구축에 투입되는 비중이 큼.

2. **자동화를 위한 선행 작업 규모**
   - **Rule·프롬프트 개발**: Phase/Task 규약, todo-list 형식, plan_md_path 규칙 등 일관된 rule과 프롬프트가 필요하며, 이만으로도 별도 설계·검증이 필요함.
   - **Claude Code 토큰 비용**: CLI 기반 실행은 토큰 사용량이 크고, 범위·재시도·폴백 정책 등 비용과 품질 사이 조정이 필요함.
   - **범위 설정**: 어떤 Task까지 자동 실행할지, 어디서 사람이 끼어들지 등 경계를 정하는 데 추가 설계와 실험이 필요함.
   - **디버깅·안정화**: n8n ↔ Backend ↔ Claude Code CLI 연동, 에러 처리, 타임아웃, 로그 추적 등 디테일한 개발·디버깅 시간이 많이 소요됨.

3. **별도 프로젝트가 적합한 이유**
   - 위 항목들은 “개발 프로세스 자동화”라는 하나의 도메인으로 묶을 수 있음.
   - 별도 저장소/프로젝트로 두면 rule·프롬프트·워크플로우·비용 실험을 본 프로젝트와 분리해 집중할 수 있음.
   - Personal AI Brain은 “지식 브레인” 기능에 집중하고, 자동화 파이프라인은 필요 시 해당 별도 프로젝트와 연동하는 구성이 합리적임.

---

## Phase 8에서 유지·완료된 것

- **Phase 8-0**: 성능 최적화·인격체 모델 등 (완료된 작업 유지).
- **Phase 8-1**: PostgreSQL 스키마, n8n 마이그레이션, Discord 등 환경 준비 (완료된 부분 유지).
- **Phase 8-2**:  
  - Backend API: `POST /api/workflow/generate-task-plan`(Task Plan만), `POST /api/workflow/run-task`(Claude Code CLI) 등 **현행 구현 유지**.  
  - n8n 워크플로우: Task Plan Generation v2 (phase-folder) 등 **이미 만든 워크플로우·문서는 참고용으로 보존**.  
  - **신규 워크플로우 개발·연동은 보류** (8-2-4 Discord 승인 루프, 8-2-5 Todo-List 생성, 8-2-8 Task 테스트·결과 저장 등).

---

## 향후 진행 방향

- **본 프로젝트**: Phase 8은 “워크플로우 개발 보류” 상태로 마무리. 필요 시 Phase 9(백업/복원, HWP, 대시보드 등) 또는 다른 기능으로 진행.
- **워크플로우 자동화**: rule·프롬프트·Claude Code 비용·범위를 다루는 **별도 프로젝트**에서 설계·개발·실험 후, 필요하면 본 프로젝트와 연동하는 방식을 권장.

---

## 본 프로젝트 리팩토링 시 (n8n 제외)

**본 프로젝트를 리팩토링할 때는 n8n 관련 부분을 제외하고 진행하세요.**

- **Docker**: `docker-compose.yml`에서 n8n 서비스·n8n_data 볼륨은 이미 주석 처리되어 있음. 리팩토링 대상에서 제외.
- **대상 제외**: n8n 서비스 정의, n8n_data 볼륨, `docs/n8n/` 디렉터리, Phase 8-2 n8n 워크플로우 전용 문서·JSON은 리팩토링 범위에 넣지 않음.
- **유지·참고**: Backend `/api/workflow/*`, PostgreSQL workflow_* 테이블, `docs/phases/phase-8-*` 문서는 “과거 Phase 8 산출물”로 보존해 두고, 리팩토링 시 구조만 정리하면 됨.

상세: 루트 `docker-compose.yml` 상단 주석 참고.

---

**문서 버전**: 1.1  
**최종 업데이트**: 2026-02-01 — n8n Docker 주석 처리, 리팩토링 시 n8n 제외 안내 추가
