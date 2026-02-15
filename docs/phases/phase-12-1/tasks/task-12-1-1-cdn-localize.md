# Task 12-1-1: [FE] CDN 로컬화 (marked/mermaid/chart.js/html2canvas/jspdf)

**우선순위**: 12-1 내 1순위
**예상 작업량**: 중 (5개 라이브러리 다운로드 + HTML 4파일 수정)
**의존성**: 없음
**상태**: ✅ 완료

**기반 문서**: `phase-12-1-todo-list.md`
**Plan**: `phase-12-1-plan.md`
**작업 순서**: `phase-12-navigation.md`

---

## 1. 개요

### 1.1 목표

On-Premise 원칙에 따라 외부 CDN 참조를 제거하고, 5개 라이브러리를 `web/public/libs/`에 로컬 배치하여 폐쇄망 환경에서도 정상 동작하도록 한다.

### 1.2 대상 라이브러리

| 라이브러리 | 버전 | 용도 |
|-----------|------|------|
| marked.js | latest | Markdown 파싱 |
| mermaid.js | v10.x | 다이어그램 시각화 |
| chart.js | v4.x | 데이터 시각화 |
| html2canvas | v1.4.1 | 스크린샷 |
| jsPDF | v2.5.1 UMD | PDF 생성 |

---

## 2. 파일 변경 계획

### 2.1 신규 생성

| 파일 | 용도 |
|------|------|
| `web/public/libs/marked/marked.min.js` | Markdown 파서 |
| `web/public/libs/mermaid/mermaid.min.js` | 다이어그램 |
| `web/public/libs/chartjs/chart.min.js` | 차트 |
| `web/public/libs/html2canvas/html2canvas.min.js` | 스크린샷 |
| `web/public/libs/jspdf/jspdf.umd.min.js` | PDF |

### 2.2 수정

| 파일 | 변경 내용 |
|------|----------|
| `web/src/pages/reason.html` | CDN 4건 → `/static/libs/` 로컬 경로 |
| `web/src/pages/admin/statistics.html` | chart.js CDN → 로컬 |
| `web/src/pages/logs.html` | marked.js CDN → 로컬 |
| `web/src/pages/document.html` | marked.js CDN → 로컬 |

---

## 3. 작업 체크리스트

- [x] `web/public/libs/` 디렉토리 생성
- [x] 5개 라이브러리 다운로드 및 배치
- [x] HTML 파일 CDN → 로컬 경로 수정 (4파일)
- [x] Grep 검증: `cdn.jsdelivr.net`, `cdnjs.cloudflare`, `unpkg.com` 0건
- [x] 페이지 로드 확인

---

## 4. 참조

- Phase 12 Master Plan §12-1-1
- FRONTEND.md Charter: "외부 CDN 절대 금지, 모든 라이브러리 로컬 배치"
