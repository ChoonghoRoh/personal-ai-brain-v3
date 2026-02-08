# Phase 9 작업 지시사항 (Work Instructions)

**용도**: 다음 Phase 생성 시 프롬프트에서 참조
**최종 수정**: 2026-02-01

---

## 1. Phase 생성 규칙

### 1.1 폴더 구조
```
docs/phases/
├── phase-9-master-plan.md          # 전체 계획
├── phase-9-work-instructions.md    # 이 파일 (작업 지시사항)
├── phase-9-navigation.md           # Phase 간 이동/상태 관리
├── phase-9-3/                      # 개별 Phase 폴더
│   ├── phase-9-3-todo-list.md      # Todo List
│   └── tasks/                      # Task별 상세 파일 (필요시)
├── phase-9-1/
├── phase-9-2/
└── ...
```

### 1.2 Todo List 필수 섹션
1. **Phase 진행 정보**: 현재 Phase, 다음 Phase, 전체 우선순위 현황
2. **Task 목록**: 체크박스 형태의 상세 작업 항목
3. **완료 기준**: Phase 완료 조건 및 KPI
4. **작업 로그**: 날짜별 작업 기록
5. **참고 문서**: 관련 문서 링크

### 1.3 Todo List 작성 규칙
- Task는 의존성 순서대로 배치
- 각 Task에 우선순위, 예상 작업량, 의존성 명시
- 체크박스(`- [ ]`)로 진행 상황 추적 가능하게 작성
- 하위 작업은 들여쓰기로 구분

---

## 2. Phase 우선순위 및 의존성

### 2.1 Phase 9 전체 우선순위
| 순위 | Phase | 설명 | 예상 일수 | 의존성 |
|------|-------|------|-----------|--------|
| 1 | 9-3 | AI 기능 고도화 | 8.5일 | - |
| 2 | 9-1 | 보안 강화 | 4일 | - |
| 3 | 9-2 | 테스트 확대 | 4.5일 | 9-1 부분 |
| 4 | 9-4 | 기능 확장 | 6일 | - |
| 5 | 9-5 | 코드 품질 | 3.5일 | - |

### 2.2 Phase 내 Task 의존성

**9-3 AI 기능 고도화:**
```
9-3-3 (RAG 강화)
    ↓
9-3-1 (Reasoning 추천)
9-3-2 (지식구조 매칭)
```

**9-1 보안 강화:**
```
9-1-2 (환경변수)
    ↓
9-1-1 (인증)
    ↓
9-1-3 (CORS) + 9-1-4 (Rate Limit)
```

**9-2 테스트 확대:**
```
9-2-1~3 (단위 테스트)
    ↓
9-2-4 (통합 테스트)
    ↓
9-2-5 (CI/CD)
```

---

## 3. 다음 Phase 생성 프롬프트 템플릿

### 3.1 Phase 완료 후 다음 Phase 생성 시
```
현재 Phase 9-X 완료.
docs/phases/phase-9-work-instructions.md 참조하여
다음 우선순위 Phase 9-Y 폴더 및 todo-list 생성.

요구사항:
1. phase-9-Y 폴더 생성
2. phase-9-Y-todo-list.md 작성 (기존 형식 준수)
3. phase-9-navigation.md 상태 업데이트
4. 의존성 있는 Task는 선행 Task 완료 후 진행하도록 명시
```

### 3.2 Task 실행 시
```
Phase 9-X의 Task 9-X-N 실행.
docs/phases/phase-9-X/phase-9-X-todo-list.md 참조.

요구사항:
1. Task 상세 내용 확인
2. 의존성 Task 완료 여부 확인
3. 코드 구현 및 테스트
4. todo-list 체크박스 업데이트
5. 작업 로그 기록
```

---

## 4. 상태 관리 규칙

### 4.1 Phase 상태
| 상태 | 아이콘 | 설명 |
|------|--------|------|
| 대기 | ⏳ | 아직 시작 안 함 |
| 진행중 | 🔄 | 현재 진행 중 |
| 완료 | ✅ | 모든 Task 완료 |
| 보류 | ⏸️ | 일시 중단 |

### 4.2 Task 상태
- `- [ ]`: 미완료
- `- [x]`: 완료
- `- [-]`: 진행중 (선택적)

### 4.3 상태 업데이트 시점
1. Phase 시작 시: 상태를 🔄 진행중으로 변경
2. Task 완료 시: 체크박스 체크, 작업 로그 기록
3. Phase 완료 시: 상태를 ✅ 완료로 변경, 다음 Phase 상태를 🔄로 변경

---

## 5. 코드 작성 규칙

### 5.1 파일 생성 위치
| 유형 | 경로 |
|------|------|
| 서비스 | `backend/services/{도메인}/{서비스명}.py` |
| 라우터 | `backend/routers/{도메인}/{라우터명}.py` |
| 모델 | `backend/models/{모델명}.py` |
| 테스트 | `tests/test_{테스트대상}.py` |
| 웹 페이지 | `web/src/pages/{페이지명}.html` |

### 5.2 네이밍 규칙
- 파일명: snake_case (`hybrid_search.py`)
- 클래스명: PascalCase (`HybridSearchService`)
- 함수명: snake_case (`search_hybrid()`)
- 상수: UPPER_SNAKE_CASE (`MAX_CONTEXT_LENGTH`)

### 5.3 필수 포함 항목
- 모듈 docstring (파일 상단)
- 함수/클래스 docstring
- 타입 힌트
- 에러 처리

---

## 6. 테스트 규칙

### 6.1 테스트 작성 시점
- 새 API 엔드포인트 추가 시
- 새 서비스 함수 추가 시
- 버그 수정 시 (회귀 테스트)

### 6.2 테스트 실행
```bash
# 특정 테스트 파일
python3 -m pytest tests/test_{파일명}.py -v

# 전체 테스트
python3 -m pytest tests/ -v
```

---

## 7. 문서 업데이트 규칙

### 7.1 업데이트 대상
| 시점 | 업데이트 문서 |
|------|--------------|
| Phase 완료 | phase-9-navigation.md, 해당 todo-list |
| Task 완료 | 해당 todo-list 체크박스 및 작업 로그 |
| API 추가 | API 문서 (FastAPI 자동 생성 확인) |
| 중요 변경 | phase-9-master-plan.md (필요시) |

### 7.2 작업 로그 형식
```markdown
| 날짜 | Task | 작업 내용 | 상태 |
|------|------|----------|------|
| 2026-02-01 | 9-3-3 | Hybrid Search 구현 완료 | ✅ |
```

---

## 8. 참조 문서

- **Master Plan**: `docs/phases/phase-9-master-plan.md`
- **Navigation**: `docs/phases/phase-9-navigation.md`
- **프로젝트 분석**: `docs/review/2026-02-01-full-project-analysis-report.md`
- **아키텍처**: `docs/README/02-architecture.md`
- **DB 스키마**: `docs/README/05-database.md`
