# Frontend 작업지시 가이드

**버전**: 1.0 (3rd iteration)  
**대상**: frontend-dev 팀원  
**용도**: Task 실행 프로세스 상세 지침

---

## Task 실행 프로세스

### 1. Task 할당 → 구현 → 보고

```
[1] Team Lead: SendMessage → frontend-dev에게 Task 지시
    "Task X-Y-N: [FE] Admin 설정 UI 페이지 구현
     완료 기준: 페이지 로드 OK, CRUD 동작 확인, 콘솔 에러 0건
     구현 후 SendMessage로 완료 보고"
  │
  ▼
[2] frontend-dev: TaskList 조회 → Task X-Y-N 확인
  │
  ▼
[3] frontend-dev: task-X-Y-N.md 읽기 → 완료 기준(Done Definition) 확인
  │
  ▼
[4] frontend-dev: 파일 3개 생성 (HTML, JS, CSS)
    - web/src/pages/admin/settings.html (템플릿)
    - web/public/js/admin/settings.js (ESM 모듈)
    - web/public/css/admin/settings.css (스타일)
  │
  ▼
[5] frontend-dev: 로컬 테스트 확인 (브라우저 로드, 콘솔 확인)
  │
  ▼
[6] frontend-dev: TaskUpdate(status: "completed")
  │
  ▼
[7] frontend-dev: SendMessage → Team Lead에게 완료 보고
    "Task X-Y-N 구현 완료
     변경 파일:
       - web/src/pages/admin/settings.html (신규 생성, 120줄)
       - web/public/js/admin/settings.js (신규 생성, 200줄)
       - web/public/css/admin/settings.css (신규 생성, 80줄)
     브라우저 테스트: 페이지 로드 OK, CRUD 동작 확인, 콘솔 에러 0건
     확인 요청"
```

### 2. verifier가 FAIL 판정 시 수정

```
[1] Team Lead: verifier 검증 결과 FAIL 수신
  │
  ▼
[2] Team Lead: SendMessage → frontend-dev에게 수정 요청
    "Task X-Y-N 검증 FAIL
     이슈:
       - web/public/js/admin/settings.js line 85: innerHTML 사용 시 esc() 누락
       - web/public/css/admin/settings.css: 외부 CDN 참조 (cdn.jsdelivr.net)
     수정 후 재보고"
  │
  ▼
[3] frontend-dev: 이슈 수정
  │
  ▼
[4] frontend-dev: SendMessage → Team Lead에게 재보고
    "수정 완료, 재검증 요청"
```

---

## 코드 작성 예시

### ESM 모듈 예시

```javascript
// ✅ 올바른 예시
// web/public/js/admin/settings.js
import { get, post, put, del } from '/static/js/utils/api.js';
import { esc } from '/static/js/utils/security.js';

export async function init() {
  const data = await get('/api/admin/settings');
  renderSettings(data);
}

function renderSettings(data) {
  const container = document.getElementById('settings-container');
  container.innerHTML = data.map(item => 
    `<div class="setting-item">${esc(item.name)}</div>`
  ).join('');
}
```

### XSS 방지 예시

```javascript
// ✅ 올바른 예시
import { esc } from '/static/js/utils/security.js';
elem.innerHTML = esc(userInput);

// ❌ 잘못된 예시 (XSS 취약점)
elem.innerHTML = userInput;
```

### 외부 CDN 금지

```html
<!-- ❌ 잘못된 예시 -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

<!-- ✅ 올바른 예시 -->
<script src="/static/libs/bootstrap-5.3.0/js/bootstrap.bundle.min.js"></script>
```

---

**문서 관리**:
- 버전: 1.0 (3rd iteration)
- 최종 수정: 2026-02-17
- 기반: frontend-dev.md § 4 (작업지시 분리)
