# 시스템 컨텍스트

**최종 업데이트**: 2026-01-07 05:46:21

## 시스템 개요

Personal AI Brain은 로컬 환경에서 실행되는 개인 지식 관리 시스템입니다.

## 주요 기능

1. **문서 임베딩**: Markdown, PDF, DOCX 파일을 벡터로 변환하여 저장
2. **의미 기반 검색**: 자연어 쿼리로 관련 문서 검색
3. **자동 변경 감지**: 파일 변경 시 자동으로 임베딩 갱신
4. **Git 자동 커밋**: 시스템 변경사항 자동 기록

## 디렉토리 구조

- `brain/projects/`: 프로젝트별 문서
- `brain/reference/`: 참고 자료
- `brain/inbox/`: 임시 문서
- `brain/archive/`: 아카이브
- `brain/system/`: 시스템 관리 파일
- `collector/`: 원본 문서 (PDF, DOCX 등)

## 사용 스크립트

- `embed_and_store.py`: 문서 임베딩 및 저장
- `search_and_query.py`: 검색 및 질의
- `watcher.py`: 파일 변경 감지 및 자동 갱신
- `auto_commit.py`: Git 자동 커밋
- `collector.py`: 문서 수집 및 변환
- `system_agent.py`: 시스템 상태 관리

## 현재 상태

시스템이 정상 작동 중입니다.
