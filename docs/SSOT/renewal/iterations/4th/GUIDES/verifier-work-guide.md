# Verifier 작업지시 가이드

**버전**: 6.0-renewal-4th  
**대상**: verifier 팀원  
**용도**: 검증 프로세스 상세 지침

---

## 검증 프로세스

### 1. Team Lead로부터 검증 요청 수신

```
[1] Team Lead: SendMessage → verifier에게 검증 요청 (변경 파일·완료 기준 명시)
[2] verifier: 변경 파일 읽기 (Read, Grep)
[3] verifier: [ROLES/verifier.md](../ROLES/verifier.md) 검증 기준 적용 (Critical/High)
[4] verifier: 이슈 목록 작성
[5] verifier: 판정 결정 (PASS / FAIL / PARTIAL)
[6] verifier: SendMessage → Team Lead에게 판정 보고
```

### 2. 재검증

수정 완료 후 Team Lead가 재검증 요청 → verifier 재검증 → 판정 보고.

---

## 검증 체크리스트

- **백엔드**: ORM 사용, Pydantic 검증, 타입 힌트, 기존 테스트, 에러 핸들링.
- **프론트엔드**: CDN 미사용, innerHTML+esc(), ESM, 콘솔 에러 0건.

➜ 상세: [ROLES/verifier.md](../ROLES/verifier.md), [3-workflow.md](../3-workflow.md) §4 품질 게이트

---

**문서 관리**: 버전 6.0-renewal-4th, 단독 사용(4th 세트만 참조)
