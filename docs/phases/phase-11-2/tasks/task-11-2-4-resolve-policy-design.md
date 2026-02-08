# Task 11-2-4: 정책 해석(resolve) API (상세 설계)

**우선순위**: 11-2 내 4순위
**예상 작업량**: 0.5일
**의존성**: 11-2-3 설계 참고
**상태**: ✅ 완료
**비고**: **구현은 다음 Phase에서 진행.** 이번 Task에서는 디테일한 설계만 수행.

**기반 문서**: [phase-11-2-0-todo-list.md](../phase-11-2-0-todo-list.md)
**Plan**: [phase-11-2-0-plan.md](../phase-11-2-0-plan.md)
**작업 순서**: [phase-11-navigation.md](../../phase-11-navigation.md)

---

## 1. 개요

### 1.1 목표

정책 해석(**resolve**) API의 **스펙**(엔드포인트·입출력)과 **Reasoning(reason.py) 연동 방식·우선순위 규칙**을 설계한다. 설계 문서를 산출물로 남기며, **구현·reason.py 연동은 다음 Phase**에서 설계 문서 기반으로 진행한다.

### 1.2 목적

policy_sets 테이블에 저장된 여러 정책 중, 특정 요청 컨텍스트(project_id, user_group 등)에 **적용되어야 할 최종 정책**을 해석(resolve)하여 반환한다. Reasoning Lab(reason.py) 호출 시 이 API를 통해 적절한 template, prompt_preset, rag_profile을 자동으로 선택한다.

---

## 2. 정책 우선순위 규칙

### 2.1 우선순위 결정 기준

policy_sets의 적용 대상 및 우선순위:

```
우선순위 높음 ←───────────────────────────────────── 우선순위 낮음
[project_id 특정] > [user_group 특정] > [전역 (project_id=null)]
```

### 2.2 우선순위 해석 로직

1. **is_active = true**인 정책만 대상
2. **effective_from ≤ NOW() ≤ effective_until** (유효 기간 내)
3. **project_id 매칭**: 요청의 project_id와 일치하는 정책 우선
4. **user_group 매칭**: 요청의 user_group과 일치하는 정책
5. **전역 정책**: project_id = null인 정책 (fallback)
6. **priority 필드**: 동일 레벨 내에서 priority DESC로 정렬

### 2.3 우선순위 흐름

```python
def resolve_policy(project_id, user_group):
    # 1. 프로젝트 특정 + 사용자 그룹 특정
    policy = find_policy(project_id=project_id, user_group=user_group)
    if policy: return policy

    # 2. 프로젝트 특정 + 사용자 그룹 무관
    policy = find_policy(project_id=project_id, user_group=None)
    if policy: return policy

    # 3. 사용자 그룹 특정 + 프로젝트 무관
    policy = find_policy(project_id=None, user_group=user_group)
    if policy: return policy

    # 4. 전역 정책 (fallback)
    policy = find_policy(project_id=None, user_group=None)
    return policy
```

---

## 3. Resolve API 스펙

### 3.1 Policy Resolve API

```
GET /api/admin/policy-sets/resolve
```

**Query Parameters**:
- `project_id`: int (선택, 프로젝트 ID)
- `user_group`: string (선택, 사용자 그룹)

**Response** (200 OK):
```json
{
  "resolved_policy": {
    "id": "uuid",
    "name": "전역 기본 정책",
    "priority": 0,
    "match_type": "global"
  },
  "template": {
    "id": "uuid",
    "name": "기본 의사결정 문서",
    "template_type": "decision_view",
    "content": "# {{title}}...",
    "status": "published"
  },
  "prompt_preset": {
    "id": "uuid",
    "name": "의사결정 프리셋",
    "task_type": "decision",
    "model_name": "qwen2.5:7b",
    "temperature": 0.7,
    "system_prompt": "...",
    "status": "published"
  },
  "rag_profile": {
    "id": "uuid",
    "name": "기본 RAG 프로필",
    "chunk_size": 1000,
    "top_k": 5,
    "score_threshold": 0.7,
    "status": "published"
  },
  "match_info": {
    "match_type": "global",
    "matched_project_id": null,
    "matched_user_group": null,
    "fallback_used": true
  }
}
```

**Response (404)** - 적용 가능한 정책 없음:
```json
{
  "detail": "No active policy found for the given context",
  "context": {
    "project_id": 1,
    "user_group": "developers"
  }
}
```

### 3.2 match_type 값

| match_type | 설명 |
|------------|------|
| `project_user` | project_id + user_group 모두 매칭 |
| `project` | project_id만 매칭 |
| `user_group` | user_group만 매칭 |
| `global` | 전역 정책 (fallback) |

---

## 4. Reasoning (reason.py) 연동 설계

### 4.1 현재 reason.py 구조

```python
class ReasonRequest(BaseModel):
    mode: str = "design_explain"
    inputs: Dict
    question: Optional[str] = None
    filters: Optional[ReasonFilters] = None
    model: Optional[str] = None
```

### 4.2 연동 확장 설계

**ReasonRequest 확장**:
```python
class ReasonRequest(BaseModel):
    mode: str = "design_explain"
    inputs: Dict
    question: Optional[str] = None
    filters: Optional[ReasonFilters] = None
    model: Optional[str] = None
    # Phase 11 추가
    project_id: Optional[int] = None  # policy resolve용
    user_group: Optional[str] = None  # policy resolve용
    use_policy: bool = True  # True면 Admin 정책 적용
```

### 4.3 연동 흐름

```
[reason.py POST /api/reason]
    ↓
[use_policy=True?]
    ↓ Yes
[GET /api/admin/policy-sets/resolve?project_id=X&user_group=Y]
    ↓
[resolved: template, prompt_preset, rag_profile]
    ↓
[dynamic_reasoning_service에 전달]
    ↓
- system_prompt = prompt_preset.system_prompt
- temperature = prompt_preset.temperature
- RAG 파라미터 = rag_profile.chunk_size, top_k, score_threshold
- 출력 템플릿 = template.content
```

### 4.4 reason.py 수정 위치 (다음 Phase)

```python
# backend/routers/reasoning/reason.py

@router.post("", response_model=ReasonResponse)
async def reason(request: ReasonRequest, db: Session = Depends(get_db)):
    # Phase 11: Admin 정책 resolve
    if request.use_policy:
        resolved = await resolve_policy_for_reasoning(
            db, request.project_id, request.user_group
        )
        # resolved에서 prompt_preset, rag_profile 추출
        model = resolved.prompt_preset.model_name or request.model
        temperature = resolved.prompt_preset.temperature
        # ... RAG 파라미터 적용
    else:
        # 기존 로직 (하드코딩된 설정)
        ...
```

---

## 5. 관련 서비스 설계

### 5.1 PolicyResolverService

```python
# backend/services/admin/policy_resolver.py

class PolicyResolverService:
    def __init__(self, db: Session):
        self.db = db

    async def resolve(
        self,
        project_id: Optional[int] = None,
        user_group: Optional[str] = None
    ) -> ResolvedPolicy:
        """우선순위에 따라 적용할 정책 해석"""
        # 우선순위 로직 구현
        pass

    async def get_template(self, policy: PolicySet) -> Template:
        """정책에 연결된 published 템플릿 조회"""
        pass

    async def get_prompt_preset(self, policy: PolicySet) -> PromptPreset:
        """정책에 연결된 published 프리셋 조회"""
        pass

    async def get_rag_profile(self, policy: PolicySet) -> RagProfile:
        """정책에 연결된 published RAG 프로필 조회"""
        pass
```

### 5.2 ResolvedPolicy 응답 모델

```python
# backend/routers/admin/schemas_pydantic.py

class ResolvedPolicyResponse(BaseModel):
    resolved_policy: PolicySetResponse
    template: Optional[TemplateResponse]
    prompt_preset: Optional[PresetResponse]
    rag_profile: Optional[RagProfileResponse]
    match_info: MatchInfo

class MatchInfo(BaseModel):
    match_type: str  # project_user, project, user_group, global
    matched_project_id: Optional[int]
    matched_user_group: Optional[str]
    fallback_used: bool
```

---

## 6. 구현 파일 계획 (다음 Phase)

| 파일 경로 | 용도 |
|-----------|------|
| `backend/services/admin/policy_resolver.py` | PolicyResolverService |
| `backend/routers/admin/policy_set_crud.py` (확장) | /resolve 엔드포인트 추가 |
| `backend/routers/admin/schemas_pydantic.py` (확장) | ResolvedPolicyResponse 등 |
| `backend/routers/reasoning/reason.py` (수정) | use_policy, policy resolve 연동 |

---

## 7. 체크리스트 (Done Definition)

- [x] 정책 해석(resolve) API 스펙(엔드포인트·입출력) 설계
- [x] Reasoning(reason.py) 연동 방식·우선순위 규칙 설계
- [x] 설계 문서 작성 (본 문서)
- [ ] 구현·reason.py 연동은 다음 Phase에서 설계 문서 기반으로 진행

---

## 8. 참조

- [phase-11-2-0-plan.md](../phase-11-2-0-plan.md) §5.4
- [phase-11-master-plan-sample.md](../../phase-11-master-plan-sample.md) — 정책 해석 API 참고
- [backend/routers/reasoning/reason.py](../../../../backend/routers/reasoning/reason.py) — 현재 Reasoning API
