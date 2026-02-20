# Phase 18-2: 지식 구조 UI (폴더 트리 + 통합 트리)

## 목표

Document의 file_path를 파싱하여 가상 폴더 트리를 구성하고, Project→폴더→문서→청크 통합 지식 트리를 제공한다.

## Task 구조

| Task | 내용 | 도메인 | 담당 |
|------|------|--------|------|
| 18-2-1 | Document 폴더 계층 API (file_path 파싱 가상 트리) | [BE] | backend-dev |
| 18-2-2 | 폴더 트리뷰 UI 컴포넌트 | [FE] | frontend-dev |
| 18-2-3 | 통합 지식 트리 API (Project/폴더/Document/Chunk) | [BE] | backend-dev |
| 18-2-4 | 통합 트리뷰 페이지 UI | [FE] | frontend-dev |
| 18-2-5 | Breadcrumb 전역 네비게이션 | [FE] | frontend-dev |

## 병렬 실행

- BE: 18-2-1 → 18-2-3 (순차)
- FE: 18-2-2 (18-2-1 후) → 18-2-4 (18-2-3 후) → 18-2-5

## 핵심 기술 결정

- DB 스키마 변경 없음 — file_path 파싱으로 가상 트리
- Document 모델: file_path(String) 필드 존재 확인
- 통합 트리: knowledge.py + graph.py 기존 패턴 활용
