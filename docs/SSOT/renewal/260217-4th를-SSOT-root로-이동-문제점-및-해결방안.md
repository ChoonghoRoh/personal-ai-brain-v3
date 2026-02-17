# 4th 폴더를 docs/SSOT 루트로 옮길 경우 — 문제점 및 해결 방안

**작성일**: 2026-02-17  
**가정**: `docs/SSOT/renewal/iterations/4th/` 내용을 `docs/SSOT/` 루트로 이동(파일·폴더만 옮기고 내부 구조 유지).

---

## 1. 이동 후 예상 구조

```
docs/SSOT/
├── 0-entrypoint.md      ← 4th에서 이동
├── 1-project.md
├── 2-architecture.md
├── 3-workflow.md
├── VERSION.md
├── PERSONA/
├── ROLES/
├── GUIDES/
├── claude/              ← 기존 유지
├── backup/              ← 기존 유지
├── copilot/             ← 기존 유지
└── renewal/             ← 기존 유지 (iterations/4th 는 제거 또는 빈 폴더/리다이렉트)
    ├── iterations/1st, 2nd, 3rd
    ├── 0-entrypoint.md, 1-project.md, ...
    └── ...
```

---

## 2. 문제점 및 해결 방안

### 2.1 4th 내부 상대 경로 (문제 없음)

| 항목 | 내용 |
|------|------|
| **상황** | 4th 내부 링크는 모두 상대 경로(`../0-entrypoint.md`, `../PERSONA/BACKEND.md` 등). |
| **이동 후** | 폴더 구조(0,1,2,3, PERSIONA, ROLES, GUIDES)를 그대로 유지하면 상대 경로는 **그대로 유효**. |
| **해결** | **추가 조치 없음.** 이동만 하면 됨. |

---

### 2.2 4th 문서 내 "iterations/4th" 문구 (경로·정체성)

| 항목 | 내용 |
|------|------|
| **문제** | 다수 문서에 "본 iterations/4th 세트", "iterations/4th 만으로", "4th iteration", "기본 진입점: iterations/4th/0-entrypoint.md" 등 **경로·정체성** 문구가 있음. 이동 후에는 경로가 `docs/SSOT/`가 되므로 오해·불일치 발생. |
| **영향 파일** | 0-entrypoint, 1-project, 2-architecture, 3-workflow, VERSION, PERSONA/*.md, ROLES/*.md, GUIDES/*.md, PERSONA/README.md |
| **해결 방안** | 1) **일괄 치환**: "iterations/4th" → "docs/SSOT"(또는 "본 SSOT 루트"), "4th 세트" → "SSOT 세트" 등으로 문구 정리. 2) **버전명 유지**: "6.0-renewal-4th", "4th iteration"은 **버전/이력**으로 남겨 두고, 경로만 "docs/SSOT"로 통일. |

---

### 2.3 4th를 가리키는 외부 문서 링크

| 항목 | 내용 |
|------|------|
| **문제** | 다른 문서에서 `docs/SSOT/renewal/iterations/4th/` 또는 `iterations/4th/`를 링크·경로로 참조하면 이동 후 **깨짐**. |
| **영향 파일** | `renewal/260217-1600-SSOT-claude-vs-3rd-비교분석리포트.md`, `renewal/260217-4th-PERSONA-연결파일-조사.md`, `renewal/260217-4th-외부문서참조-조사.md` |
| **해결 방안** | 위 문서들에서 "iterations/4th", "renewal/iterations/4th"를 **docs/SSOT** 또는 **docs/SSOT/0-entrypoint.md** 등 새 경로로 치환. 비교 리포트·조사 문서는 "4th 위치: 이전 iterations/4th → 현재 docs/SSOT 루트"로 문구·표 한 번 정리. |

---

### 2.4 AGENTS.md / .cursor / .vscode (도구 설정)

| 항목 | 내용 |
|------|------|
| **문제** | 4th PERSONA를 쓰도록 설정해 두었다면 경로가 `docs/SSOT/renewal/iterations/4th/PERSONA/`에서 `docs/SSOT/PERSONA/`로 바뀜. |
| **해결 방안** | AGENTS.md, .cursor/rules, .vscode/settings 등에서 **4th(SSOT) 진입점·PERSONA 경로**를 `docs/SSOT/0-entrypoint.md`, `docs/SSOT/PERSONA/*.md`로 변경. (현재 docs/rules/role만 쓸 경우 해당 설정은 그대로 두면 됨.) |

---

### 2.5 renewal/iterations/4th 폴더 처리

| 항목 | 내용 |
|------|------|
| **문제** | 4th 내용을 옮긴 뒤 `renewal/iterations/4th/`를 그대로 두면 빈 폴더 또는 구버전 잔여로 혼선. 삭제하면 위 2.3의 구경로 링크가 모두 404. |
| **해결 방안** | 1) **삭제**: 이동 완료·외부 링크 수정(2.3) 후 `renewal/iterations/4th/` 삭제. 2) **리다이렉트용 README**: 폴더에 README.md만 두고 "4th는 docs/SSOT 루트로 이동됨. 진입점: docs/SSOT/0-entrypoint.md" 안내. 3) **심볼릭 링크**: 사용하지 않는 것이 좋음(도구·Git 호환 이슈). |

---

### 2.6 docs/SSOT 루트와 renewal 루트 파일명 충돌

| 항목 | 내용 |
|------|------|
| **상황** | `renewal/0-entrypoint.md`, `renewal/1-project.md` 등이 이미 존재. 4th를 SSOT 루트로 옮기면 `docs/SSOT/0-entrypoint.md`, `docs/SSOT/1-project.md`가 생김. |
| **판단** | 경로가 다름(docs/SSOT/ vs docs/SSOT/renewal/)이므로 **파일명 충돌 없음**. SSOT 루트가 "실제 기본 진입점", renewal 루트는 "renewal 계열 진입점"으로 역할만 구분하면 됨. |
| **해결** | 추가 조치 없음. 필요 시 renewal/ README에 "기본 SSOT 진입점은 상위 docs/SSOT/0-entrypoint.md" 안내 추가. |

---

### 2.7 4th가 참조하는 외부 경로 (docs/phases, docs/rules)

| 항목 | 내용 |
|------|------|
| **상황** | 4th 문서가 `docs/phases/...`, `docs/rules/templates/...`, `docs/rules/ai/...`를 참조. 모두 **리포지터리 루트 기준** 경로. |
| **이동 후** | 4th가 docs/SSOT/로 옮겨도 해당 경로는 그대로 유효(루트 기준이므로). |
| **해결** | **수정 불필요.** |

---

## 3. 작업 순서 제안

1. **4th 내용을 docs/SSOT 루트로 복사·이동** (기존 claude/, renewal/, backup/, copilot/ 은 유지).
2. **4th 내부 문구 정리**: "iterations/4th" → "docs/SSOT" 또는 "본 SSOT", "4th 세트" → "SSOT 세트" 등 일괄 치환(버전명 6.0-renewal-4th는 유지).
3. **renewal 쪽 문서 수정**: 비교분석리포트, PERSONA 연결파일 조사, 외부문서참조 조사에서 4th 경로를 docs/SSOT(또는 docs/SSOT/0-entrypoint.md)로 변경.
4. **선택**: AGENTS.md·.cursor·.vscode에서 SSOT/PERSONA 경로를 docs/SSOT/PERSONA로 지정.
5. **renewal/iterations/4th 처리**: 삭제 또는 README로 "docs/SSOT로 이동됨" 안내.
6. **VERSION.md(이동된 파일)**: "기본 진입점: docs/SSOT/0-entrypoint.md"로 수정.

---

## 4. 요약

| 구분 | 문제 | 해결 |
|------|------|------|
| **내부 상대 링크** | 없음 | 구조 유지 시 그대로 동작 |
| **문서 내 경로·정체성 문구** | "iterations/4th" 등 | "docs/SSOT"/"SSOT 세트" 등으로 치환 |
| **외부에서 4th 링크** | 깨짐 | renewal 쪽 문서 경로 수정 |
| **도구 설정** | PERSONA/ 진입점 경로 | docs/SSOT/PERSONA, docs/SSOT/0-entrypoint로 변경 |
| **iterations/4th 폴더** | 빈 폴더/404 | 삭제 또는 README 리다이렉트 안내 |
| **docs/phases, docs/rules** | 무관 | 변경 없음 |

이동 자체는 **폴더 구조만 유지하면 기술적 리스크가 작고**, 정리 작업은 **문구 치환·외부 링크 수정·설정 경로 변경**으로 해결 가능함.

---

**문서 상태**: 4th → docs/SSOT 루트 이동 시 문제점·해결방안 정리 완료.
