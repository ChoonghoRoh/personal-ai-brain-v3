---
doc_type: index
index_domain: analysis
version: 1.0
status: active
owner: human
last_updated: 2026-02-06
---

# 규칙 분석 인덱스

**용도**: `docs/rules/` 폴더의 개발 방법론, 규칙 체계, 자동화 프로세스 분석 문서 인덱스

---

## 1. 개발 방법론 분석

| 문서                                                                                               | 설명                                                                      | 최종 수정  |
| -------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- | ---------- |
| [phase-based-development-methodology-analysis.md](phase-based-development-methodology-analysis.md) | Phase 기반 자동개발 방법론의 구조, 효율성, 리스크, 장단점, 개선 방안 분석 | 2026-02-06 |

---

## 2. 분석 범위

### 2.1 분석 대상 문서

분석은 다음 규칙 문서를 기준으로 수행:

- **공통 규약**: `docs/rules/common/references/common-phase-document-taxonomy.md`
- **AI 규칙**: `docs/rules/ai/references/ai-rule-*.md`
- **Frontend 규칙**: `docs/rules/frontend/references/frontend-rule-*.md`
- **개발 계획**: `docs/rules/common/references/common-phase-*-navigation.md`

### 2.2 분석 핵심 주제

1. **개발 단계 프로세스**
   - 컨셉/기획 설계 (Plan, Navigation)
   - 개발상세 설계 (todo-list, Task)
   - 검증/검사 (Test, Report)
   - 최종검사 (Summary)

2. **사용자 개입 vs 자동 검증**
   - 각 단계별 Human 의사결정 영역
   - 자동화 가능 부분 및 한계
   - 병목 지점 분석

3. **리스크 분석**
   - 구조적 리스크 (Plan 모호성, Done Definition 불명확)
   - 프로세스 리스크 (환경 구축, 회귀 테스트 누락)
   - 자동화 관련 리스크 (AI 신뢰도, MCP 환경)

4. **방법론 평가**
   - 장점 (가시화, 리스크 분산, 자동 검증)
   - 단점 (초기 설계 시간, 문서 오버헤드)
   - 개선 방안 및 우선순위

---

## 3. 주요 발견사항

### 3.1 개발 프로세스 구조

4단계 프로세스로 구성:

```
1단계: 컨셉/기획 설계 (85% Human)
  ↓
2단계: 개발상세 설계 (60% Human)
  ↓
3단계: 검증/검사 (50% Human)
  ↓
4단계: 최종검사 (70% Human)
```

### 3.2 리스크 우선순위 TOP 3

1. **Done Definition 불명확** (점수: 9/10)
   - 영향도: 높음, 가능성: 중간
   - 조치: Done Definition 양식 표준화

2. **환경 구축 오류** (점수: 9/10)
   - 영향도: 높음, 가능성: 중간
   - 조치: Health-check 자동화

3. **회귀 테스트 누락** (점수: 9/10)
   - 영향도: 높음, 가능성: 중간
   - 조치: E2E 자동 체이닝

### 3.3 방법론 평가

**종합 점수: 7.5/10** ✅

**적용 대상**:

- ✅ 중규모 프로젝트 (1~3개월)
- ✅ 팀 규모 2명 이상
- ⚠️ 변화 많은 프로젝트는 신중

---

## 4. 개선 실행 계획

### Phase 1: 긴급 (1주일)

- [ ] Done Definition 양식 표준화
- [ ] Health-check 자동화
- [ ] Phase별 테스트 매트릭스 정의

### Phase 2: 중기 (2주일)

- [ ] 회귀 E2E 자동 체이닝
- [ ] AI 자동 생성물 검증 체크리스트
- [ ] Task 크기 기준 자동 검증

### Phase 3: 장기 (1개월)

- [ ] MCP 설정 자동화
- [ ] Plan 명확성 검증 도구
- [ ] 보안 감사 체크리스트 정의

---

## 5. 참고 문서

| 범주          | 문서 경로                                            |
| ------------- | ---------------------------------------------------- |
| 공통 규약     | `docs/rules/common/common-rules-index.md`            |
| AI 규칙       | `docs/rules/ai/ai-rules-index.md`                    |
| Frontend 규칙 | `docs/rules/frontend/frontend-rule-webtest-index.md` |
| 통합 인덱스   | `docs/rules/rules-index.md`                          |

---

**인덱스 작성**: 2026-02-06
**상태**: Active
