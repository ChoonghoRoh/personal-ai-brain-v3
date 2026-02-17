# Planner 작업지시 가이드

**버전**: 6.0-renewal-4th  
**대상**: planner 팀원  
**용도**: PLANNING 단계 실행 프로세스 및 출력 형식

---

## 실행 프로세스

### 1. Team Lead로부터 계획 분석 요청 수신

```
[1] Team Lead: SendMessage → planner에게 "Phase X-Y 계획 분석 요청"
    (master-plan, navigation, 이전 Phase summary 등 전달)
  │
  ▼
[2] planner: [ROLES/planner.md](../ROLES/planner.md) §2 SSOT·리스크 확인
    - status 파일 ssot_version 일치 여부
    - current_state, blockers 확인
  │
  ▼
[3] planner: 요구사항 분석, Task 분해 (도메인 태그·담당 팀원·완료 기준)
  │
  ▼
[4] planner: G1 준비 여부 점검 (완료 기준 명확, Task 3~7개, 프론트 동선 기술)
  │
  ▼
[5] planner: SendMessage → Team Lead에게 분석 결과 반환
    (아래 출력 형식 참조)
```

### 2. 출력 시 유의사항

- **쓰기 권한 없음**: planner는 파일 생성/수정하지 않음. 결과는 SendMessage로만 전달.
- **shutdown_request 수신 시**: SendMessage(type: "shutdown_response", approve: true) 후 종료.

---

## 출력 형식 (권장)

Team Lead에게 SendMessage로 반환할 때 아래 구조 사용 권장.

```markdown
## Planner 분석 결과 — Phase X-Y

### SSOT·리스크
- SSOT 버전: (일치/불일치)
- 리스크: (목록 또는 없음)

### Task 분해
| Task ID | 도메인 | 담당 팀원 | 요약 | 완료 기준 요약 |
|---------|--------|----------|------|----------------|
| X-Y-1   | [DB]   | backend-dev | ...  | ...         |
| X-Y-2   | [BE]   | backend-dev | ...  | ...         |
| X-Y-3   | [FE]   | frontend-dev | ... | ...         |
...

### G1 준비 여부
- 완료 기준 명확: 예/아니오
- Task 수: N (3~7 범위 여부)
- 프론트엔드 동선/구조 기술: 예/아니오
```

---

## 참조

- 역할·Task 분해 기준: [ROLES/planner.md](../ROLES/planner.md)
- 워크플로우·상태: [3-workflow.md](../3-workflow.md) §1, §3

---

**문서 관리**: 버전 6.0-renewal-4th, 단독 사용(4th 세트만 참조)
