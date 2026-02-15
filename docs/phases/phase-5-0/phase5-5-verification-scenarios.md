# Phase 5.5: Personal AI Brain - 검증 시나리오

본 문서는 Personal AI Brain 시스템의 전체 기능을 검증하기 위한 시나리오를 제공합니다.

**작성일**: 2026-01-07  
**대상 버전**: Phase 5.5 완료 버전

---

## 📋 검증 시나리오 개요

### 검증 범위

- ✅ Phase 1: 기본 구조 및 핵심 기능
- ✅ Phase 2: 자동화 시스템
- ✅ Phase 3: 통합 작업 기록 시스템
- ✅ Phase 4: 웹 인터페이스
- ✅ Phase 5: 지식 구조화 및 Reasoning 시스템

### 검증 환경

- **OS**: macOS / Linux
- **Python**: 3.12+
- **Docker**: Qdrant, PostgreSQL 컨테이너 실행 필요
- **포트**:
  - 6333: Qdrant
  - 5432: PostgreSQL
  - 8000: FastAPI 웹 서버

---

## 1️⃣ 시스템 시작 및 기본 검증

### 1.1 인프라 준비 상태 확인

```bash
# Qdrant 컨테이너 확인
docker ps | grep qdrant
# 예상 결과: qdrant 컨테이너 실행 중

# PostgreSQL 컨테이너 확인
docker ps | grep pab-postgres
# 예상 결과: pab-postgres 컨테이너 실행 중

# Qdrant 연결 테스트
curl http://localhost:6333/collections
# 예상 결과: JSON 응답 (컬렉션 목록)

# PostgreSQL 연결 테스트
docker exec pab-postgres psql -U brain -d knowledge -c "SELECT version();"
# 예상 결과: PostgreSQL 버전 정보
```

**검증 기준**: 모든 컨테이너가 정상 실행 중이어야 함

---

### 1.2 데이터베이스 스키마 확인

```bash
# PostgreSQL 테이블 확인
docker exec pab-postgres psql -U brain -d knowledge -c "\dt"
# 예상 결과: 다음 테이블 존재
# - projects
# - documents
# - knowledge_chunks
# - labels
# - knowledge_labels
# - knowledge_relations

# Qdrant 컬렉션 확인
curl http://localhost:6333/collections/brain_documents
# 예상 결과: brain_documents 컬렉션 정보
```

**검증 기준**: 모든 필수 테이블과 컬렉션이 존재해야 함

---

### 1.3 웹 서버 시작 및 헬스 체크

```bash
# 웹 서버 시작
cd scripts
source venv/bin/activate
python start_server.py &

# 헬스 체크
sleep 3
curl http://localhost:8001/health
# 예상 결과: {"status":"ok"}
```

**검증 기준**: 서버가 정상 시작되고 헬스 체크가 성공해야 함

---

## 2️⃣ Phase 1 검증: 기본 구조 및 핵심 기능

### 2.1 문서 임베딩 및 저장

```bash
# 문서 임베딩 실행
cd scripts
source venv/bin/activate
python embed_and_store.py

# 검증 항목:
# 1. Markdown 파일 수집 확인
# 2. 임베딩 생성 확인
# 3. Qdrant 저장 확인
# 4. PostgreSQL 저장 확인
```

**검증 기준**:

- ✅ 모든 .md 파일이 처리되어야 함
- ✅ Qdrant에 벡터가 저장되어야 함
- ✅ PostgreSQL에 프로젝트/문서/청크 정보가 저장되어야 함

**검증 명령어**:

```bash
# Qdrant 포인트 수 확인
curl http://localhost:6333/collections/brain_documents | jq '.result.points_count'

# PostgreSQL 데이터 확인
docker exec pab-postgres psql -U brain -d knowledge -c "SELECT COUNT(*) FROM knowledge_chunks;"
docker exec pab-postgres psql -U brain -d knowledge -c "SELECT COUNT(*) FROM documents;"
docker exec pab-postgres psql -U brain -d knowledge -c "SELECT COUNT(*) FROM projects;"
```

---

### 2.2 의미 기반 검색

```bash
# 검색 테스트
python search_and_query.py "프로젝트 목적"

# 검증 항목:
# 1. 검색어 임베딩 생성
# 2. Qdrant에서 유사도 검색
# 3. 검색 결과 반환
```

**검증 기준**:

- ✅ 관련 문서가 검색되어야 함
- ✅ 유사도 점수가 표시되어야 함
- ✅ 문서 내용이 표시되어야 함

**검증 명령어**:

```bash
# API를 통한 검색 테스트
curl "http://localhost:8001/api/search?q=프로젝트&limit=3" | jq
```

---

## 3️⃣ Phase 2 검증: 자동화 시스템

### 3.1 파일 변경 감지

```bash
# watcher.py 실행 (백그라운드)
python watcher.py &

# 테스트 파일 수정
echo "# 테스트 추가" >> brain/projects/alpha-project/test.md

# 검증 항목:
# 1. 파일 변경 감지
# 2. 자동 임베딩 갱신
# 3. 작업 로그 기록
```

**검증 기준**:

- ✅ 파일 변경이 감지되어야 함
- ✅ 변경된 파일이 재임베딩되어야 함
- ✅ work_log.md에 기록되어야 함

**검증 명령어**:

```bash
# 작업 로그 확인
tail -20 brain/system/work_log.md | grep "file_change"
```

---

### 3.2 Git 자동 커밋

```bash
# 파일 수정
echo "# 변경사항" >> brain/projects/alpha-project/test.md

# 자동 커밋 실행
python auto_commit.py

# 검증 항목:
# 1. 변경사항 감지
# 2. 자동 커밋 실행
# 3. 작업 로그 기록
```

**검증 기준**:

- ✅ 변경사항이 자동으로 커밋되어야 함
- ✅ 커밋 메시지가 자동 생성되어야 함
- ✅ work_log.md에 기록되어야 함

**검증 명령어**:

```bash
# Git 로그 확인
git log --oneline -5

# 작업 로그 확인
tail -20 brain/system/work_log.md | grep "commit"
```

---

### 3.3 문서 수집 (PDF/DOCX)

```bash
# collector/ 디렉토리에 PDF/DOCX 파일 배치
# (테스트 파일 필요)

# 문서 수집 실행
python collector.py

# 검증 항목:
# 1. PDF/DOCX 파일 감지
# 2. Markdown 변환
# 3. brain/inbox/로 이동
```

**검증 기준**:

- ✅ PDF/DOCX 파일이 감지되어야 함
- ✅ Markdown으로 변환되어야 함
- ✅ brain/inbox/에 저장되어야 함

---

### 3.4 시스템 상태 관리

```bash
# 시스템 상태 생성
python system_agent.py

# 검증 항목:
# 1. brain/system/status.md 생성/업데이트
# 2. brain/system/context.md 생성/업데이트
# 3. brain/system/todo.md 생성/업데이트
```

**검증 기준**:

- ✅ 모든 시스템 파일이 생성/업데이트되어야 함
- ✅ Qdrant 상태가 반영되어야 함
- ✅ 파일 통계가 정확해야 함

**검증 명령어**:

```bash
# 시스템 파일 확인
ls -la brain/system/*.md
cat brain/system/status.md
```

---

## 4️⃣ Phase 3 검증: 통합 작업 기록 시스템

### 4.1 작업 로그 기록

```bash
# 작업 로그 확인
python work_logger.py recent 10

# 검증 항목:
# 1. 최근 작업 목록 표시
# 2. 날짜별 그룹화
# 3. 작업 타입별 분류
```

**검증 기준**:

- ✅ 최근 작업이 표시되어야 함
- ✅ 날짜별로 정리되어야 함
- ✅ 작업 타입이 명확해야 함

**검증 명령어**:

```bash
# 작업 로그 파일 확인
cat brain/system/work_log.md | head -50
cat brain/system/work_log.json | jq '.entries | length'
```

---

### 4.2 작업 로그 정리

```bash
# 오래된 항목 정리 (90일 이전)
python work_logger.py cleanup 90

# 검증 항목:
# 1. 오래된 항목 삭제
# 2. work_log.json 업데이트
# 3. work_log.md 재생성
```

**검증 기준**:

- ✅ 오래된 항목이 삭제되어야 함
- ✅ JSON과 Markdown이 동기화되어야 함

---

## 5️⃣ Phase 4 검증: 웹 인터페이스

### 5.1 대시보드

**검증 시나리오**:

1. 브라우저에서 `http://localhost:8001/dashboard` 접속
2. 다음 항목 확인:
   - 시스템 상태 표시
   - 통계 카드 (문서 수, Qdrant 포인트, 프로젝트 수, 총 작업 수)
   - 최근 작업 목록
   - 자동화 상태
   - 최근 업데이트 문서
   - 활동 분석 차트
   - 문서 목록

**검증 기준**:

- ✅ 모든 섹션이 정상 표시되어야 함
- ✅ 데이터가 실시간으로 로드되어야 함
- ✅ 문서 목록에서 문서 클릭 시 문서 뷰어로 이동해야 함

**API 검증**:

```bash
# 시스템 상태 API
curl http://localhost:8001/api/system/status | jq

# 로그 통계 API
curl http://localhost:8001/api/logs/stats | jq
```

---

### 5.2 검색 페이지

**검증 시나리오**:

1. 브라우저에서 `http://localhost:8001/search` 접속
2. 검색어 입력 (예: "프로젝트")
3. 다음 항목 확인:
   - 검색 결과 표시
   - 검색어 하이라이팅
   - 검색 히스토리 표시
   - 추천 문서 표시
   - 결과 클릭 시 문서 뷰어로 이동

**검증 기준**:

- ✅ 검색 결과가 정확해야 함
- ✅ 하이라이팅이 정상 작동해야 함
- ✅ 히스토리가 저장되어야 함

**API 검증**:

```bash
# 검색 API
curl "http://localhost:8001/api/search?q=test&limit=5" | jq
```

---

### 5.3 문서 뷰어

**검증 시나리오**:

1. 대시보드에서 문서 클릭
2. 다음 항목 확인:
   - 문서 제목 및 경로 표시
   - Markdown 렌더링
   - 코드 블록 하이라이팅
   - 네비게이션 메뉴

**검증 기준**:

- ✅ 문서가 정상적으로 표시되어야 함
- ✅ Markdown이 HTML로 렌더링되어야 함
- ✅ 오류 없이 로드되어야 함

**API 검증**:

```bash
# 문서 API
curl "http://localhost:8001/api/documents" | jq '.[0]'
curl "http://localhost:8001/api/documents/brain/system/status.md" | jq
```

---

### 5.4 AI 질의 페이지

**검증 시나리오**:

1. 브라우저에서 `http://localhost:8001/ask` 접속
2. 질문 입력 (예: "프로젝트 목적은?")
3. 다음 항목 확인:
   - AI 응답 표시
   - 참고 문서 목록
   - 컨텍스트 사용 옵션
   - 대화 기록

**검증 기준**:

- ✅ AI 응답이 생성되어야 함
- ✅ 참고 문서가 표시되어야 함
- ✅ 컨텍스트가 반영되어야 함

**API 검증**:

```bash
# AI 질의 API
curl -X POST http://localhost:8001/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "프로젝트 목적", "context_enabled": true, "top_k": 3}' | jq
```

---

### 5.5 로그 뷰어

**검증 시나리오**:

1. 브라우저에서 `http://localhost:8001/logs` 접속
2. 다음 항목 확인:
   - 타임라인 뷰
   - 날짜별 필터
   - 액션별 필터
   - 검색 기능
   - 통계 패널

**검증 기준**:

- ✅ 작업 이력이 타임라인으로 표시되어야 함
- ✅ 필터링이 정상 작동해야 함
- ✅ 통계가 정확해야 함

**API 검증**:

```bash
# 로그 API
curl "http://localhost:8001/api/logs?limit=10" | jq
curl "http://localhost:8001/api/logs/stats" | jq
```

---

## 6️⃣ Phase 5 검증: 지식 구조화 및 Reasoning

### 6.1 PostgreSQL 데이터 검증

```bash
# 프로젝트 데이터 확인
docker exec pab-postgres psql -U brain -d knowledge -c "SELECT * FROM projects;"

# 문서 데이터 확인
docker exec pab-postgres psql -U brain -d knowledge -c "SELECT id, file_name, file_type FROM documents LIMIT 5;"

# 청크 데이터 확인
docker exec pab-postgres psql -U brain -d knowledge -c "SELECT id, chunk_index, LEFT(content, 50) FROM knowledge_chunks LIMIT 5;"
```

**검증 기준**:

- ✅ 프로젝트 정보가 저장되어야 함
- ✅ 문서 메타데이터가 저장되어야 함
- ✅ 청크 정보가 저장되어야 함

---

### 6.2 라벨 시스템 검증

**API 검증**:

```bash
# 라벨 생성
curl -X POST http://localhost:8001/api/labels \
  -H "Content-Type: application/json" \
  -d '{"name": "implementation", "label_type": "project_phase", "description": "구현 단계"}' | jq

# 라벨 목록 조회
curl http://localhost:8001/api/labels | jq

# 청크에 라벨 추가
curl -X POST "http://localhost:8001/api/labels/chunks/1/labels/1" | jq

# 청크의 라벨 조회
curl "http://localhost:8001/api/labels/chunks/1/labels" | jq
```

**검증 기준**:

- ✅ 라벨 CRUD가 정상 작동해야 함
- ✅ 청크에 라벨을 추가/제거할 수 있어야 함
- ✅ 청크의 라벨을 조회할 수 있어야 함

---

### 6.3 관계 그래프 검증

**API 검증**:

```bash
# 관계 생성
curl -X POST http://localhost:8001/api/relations \
  -H "Content-Type: application/json" \
  -d '{"source_chunk_id": 1, "target_chunk_id": 2, "relation_type": "refers-to", "description": "참조 관계"}' | jq

# 관계 목록 조회
curl http://localhost:8001/api/relations | jq

# 나가는 관계 조회
curl "http://localhost:8001/api/relations/chunks/1/outgoing" | jq

# 들어오는 관계 조회
curl "http://localhost:8001/api/relations/chunks/2/incoming" | jq
```

**검증 기준**:

- ✅ 관계 생성/조회/삭제가 정상 작동해야 함
- ✅ 나가는/들어오는 관계를 조회할 수 있어야 함
- ✅ 관계 타입이 정확해야 함

---

### 6.4 Reasoning Pipeline 검증

**API 검증**:

```bash
# 프로젝트 기반 Reasoning
curl -X POST http://localhost:8001/api/reason \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "combine",
    "inputs": {
      "projects": [1]
    },
    "question": "다음에 뭐하면 좋을까?"
  }' | jq

# 라벨 기반 Reasoning
curl -X POST http://localhost:8001/api/reason \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "analyze",
    "inputs": {
      "labels": ["planning"]
    }
  }' | jq

# 분석 모드
curl -X POST http://localhost:8001/api/reason \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "suggest",
    "inputs": {
      "projects": [1],
      "labels": ["implementation"]
    }
  }' | jq
```

**검증 기준**:

- ✅ 프로젝트 기반 지식 수집이 정상 작동해야 함
- ✅ 라벨 기반 지식 수집이 정상 작동해야 함
- ✅ 관계 추적이 정상 작동해야 함
- ✅ Qdrant 의미 검색이 통합되어야 함
- ✅ Reasoning 결과가 반환되어야 함
- ✅ reasoning_steps가 포함되어야 함

---

## 7️⃣ 통합 시나리오 검증

### 7.1 엔드투엔드 워크플로우

**시나리오**: 새로운 문서 추가부터 검색까지의 전체 흐름

```bash
# 1. 새 문서 생성
echo "# 새 프로젝트 문서" > brain/projects/new-project/doc.md

# 2. 문서 임베딩
python embed_and_store.py

# 3. PostgreSQL 데이터 확인
docker exec pab-postgres psql -U brain -d knowledge -c "SELECT * FROM documents WHERE file_name = 'doc.md';"

# 4. Qdrant 데이터 확인
curl http://localhost:6333/collections/brain_documents | jq '.result.points_count'

# 5. 웹에서 검색
# 브라우저에서 http://localhost:8001/search 접속하여 "새 프로젝트" 검색

# 6. 작업 로그 확인
tail -20 brain/system/work_log.md
```

**검증 기준**:

- ✅ 모든 단계가 정상 작동해야 함
- ✅ 데이터가 모든 시스템에 동기화되어야 함

---

### 7.2 자동화 통합 시나리오

**시나리오**: 파일 변경 → 자동 임베딩 → 자동 커밋 → 로그 기록

```bash
# 1. watcher.py 실행 (백그라운드)
python watcher.py &

# 2. 파일 수정
echo "# 변경사항" >> brain/projects/alpha-project/test.md

# 3. 자동 임베딩 대기 (watcher가 감지)
sleep 5

# 4. 작업 로그 확인
tail -20 brain/system/work_log.md | grep "file_change"

# 5. 자동 커밋
python auto_commit.py

# 6. Git 로그 확인
git log --oneline -1

# 7. 작업 로그 확인
tail -20 brain/system/work_log.md | grep "commit"
```

**검증 기준**:

- ✅ 파일 변경이 자동으로 감지되어야 함
- ✅ 자동 임베딩이 실행되어야 함
- ✅ 자동 커밋이 실행되어야 함
- ✅ 모든 작업이 로그에 기록되어야 함

---

### 7.3 지식 네트워크 구축 시나리오

**시나리오**: 문서 → 라벨링 → 관계 생성 → Reasoning

```bash
# 1. 청크 ID 확인
docker exec pab-postgres psql -U brain -d knowledge -c "SELECT id FROM knowledge_chunks LIMIT 2;"

# 2. 라벨 생성
curl -X POST http://localhost:8001/api/labels \
  -H "Content-Type: application/json" \
  -d '{"name": "planning", "label_type": "project_phase"}' | jq

# 3. 청크에 라벨 추가
curl -X POST "http://localhost:8001/api/labels/chunks/1/labels/1" | jq

# 4. 관계 생성
curl -X POST http://localhost:8001/api/relations \
  -H "Content-Type: application/json" \
  -d '{"source_chunk_id": 1, "target_chunk_id": 2, "relation_type": "refers-to"}' | jq

# 5. Reasoning 실행
curl -X POST http://localhost:8001/api/reason \
  -H "Content-Type: application/json" \
  -d '{"mode": "combine", "inputs": {"projects": [1]}}' | jq
```

**검증 기준**:

- ✅ 라벨이 생성되고 청크에 추가되어야 함
- ✅ 관계가 생성되어야 함
- ✅ Reasoning이 라벨과 관계를 활용해야 함

---

## 8️⃣ 성능 및 안정성 검증

### 8.1 응답 시간 검증

```bash
# API 응답 시간 측정
time curl -s http://localhost:8001/api/search?q=test&limit=5 > /dev/null
time curl -s http://localhost:8001/api/system/status > /dev/null
time curl -s http://localhost:8001/api/documents > /dev/null
time curl -s -X POST http://localhost:8001/api/reason \
  -H "Content-Type: application/json" \
  -d '{"mode": "combine", "inputs": {"projects": [1]}}' > /dev/null
```

**검증 기준**:

- ✅ 검색 API: 1초 이내
- ✅ 시스템 상태 API: 0.5초 이내
- ✅ 문서 목록 API: 0.5초 이내
- ✅ Reasoning API: 3초 이내

---

### 8.2 동시 요청 처리

```bash
# 동시 요청 테스트
for i in {1..10}; do
  curl -s http://localhost:8001/api/search?q=test&limit=1 > /dev/null &
done
wait
```

**검증 기준**:

- ✅ 모든 요청이 정상 처리되어야 함
- ✅ 서버가 안정적으로 동작해야 함

---

### 8.3 데이터 일관성 검증

```bash
# 데이터 일관성 확인 스크립트 실행 (권장)
cd scripts
source venv/bin/activate
python check_data_sync.py

# 또는 자동 동기화 스크립트 실행
python sync_data.py

# 또는 셸 스크립트 실행
./verify_and_sync.sh

# 수동 확인
QDRANT_COUNT=$(curl -s http://localhost:6333/collections/brain_documents | jq '.result.points_count')
PG_COUNT=$(docker exec pab-postgres psql -U brain -d knowledge -t -c "SELECT COUNT(*) FROM knowledge_chunks;")
echo "Qdrant 포인트 수: $QDRANT_COUNT"
echo "PostgreSQL 청크 수: $PG_COUNT"
```

**검증 기준**:

- ✅ Qdrant 포인트 수와 PostgreSQL 청크 수가 일치해야 함

**데이터 불일치 해결 방법**:

1. **데이터 일관성 확인**:

   ```bash
   python scripts/check_data_sync.py
   ```

2. **자동 동기화** (권장):

   ```bash
   python scripts/sync_data.py
   # 또는
   ./scripts/verify_and_sync.sh
   ```

3. **수동 재실행**:
   ```bash
   python scripts/embed_and_store.py
   ```

**참고**:

- `sync_data.py`는 관계(relations)를 고려하여 안전하게 데이터를 동기화합니다.
- `embed_and_store.py`는 재실행 시 기존 Qdrant 포인트와 관계를 자동으로 정리합니다.

---

## 9️⃣ 오류 처리 검증

### 9.1 잘못된 입력 처리

```bash
# 존재하지 않는 문서 조회
curl "http://localhost:8001/api/documents/nonexistent.md" | jq

# 존재하지 않는 라벨 조회
curl "http://localhost:8001/api/labels/999" | jq

# 잘못된 관계 생성
curl -X POST http://localhost:8001/api/relations \
  -H "Content-Type: application/json" \
  -d '{"source_chunk_id": 999, "target_chunk_id": 999, "relation_type": "invalid"}' | jq
```

**검증 기준**:

- ✅ 적절한 에러 메시지가 반환되어야 함
- ✅ HTTP 상태 코드가 정확해야 함 (404, 400 등)

---

### 9.2 서비스 중단 시나리오

```bash
# Qdrant 중단
docker stop qdrant

# API 호출 (예상: 에러 응답)
curl http://localhost:8001/api/search?q=test

# PostgreSQL 중단
docker stop pab-postgres

# API 호출 (예상: 에러 응답)
curl http://localhost:8001/api/labels
```

**검증 기준**:

- ✅ 서비스 중단 시 적절한 에러 처리가 되어야 함
- ✅ 서버가 크래시하지 않아야 함

---

## 🔟 최종 검증 체크리스트

### 인프라

- [ ] Qdrant 컨테이너 실행 중
- [ ] PostgreSQL 컨테이너 실행 중
- [ ] 웹 서버 실행 중
- [ ] 모든 포트 정상 작동

### Phase 1

- [ ] 문서 임베딩 정상 작동
- [ ] Qdrant 저장 정상 작동
- [ ] PostgreSQL 저장 정상 작동
- [ ] 검색 기능 정상 작동

### Phase 2

- [ ] 파일 변경 감지 정상 작동
- [ ] 자동 임베딩 정상 작동
- [ ] Git 자동 커밋 정상 작동
- [ ] 문서 수집 정상 작동
- [ ] 시스템 상태 관리 정상 작동

### Phase 3

- [ ] 작업 로그 기록 정상 작동
- [ ] 작업 로그 조회 정상 작동
- [ ] 작업 로그 정리 정상 작동

### Phase 4

- [ ] 대시보드 정상 작동
- [ ] 검색 페이지 정상 작동
- [ ] 문서 뷰어 정상 작동
- [ ] AI 질의 페이지 정상 작동
- [ ] 로그 뷰어 정상 작동

### Phase 5

- [ ] PostgreSQL 데이터 정상 저장
- [ ] 라벨 시스템 정상 작동
- [ ] 관계 그래프 정상 작동
- [ ] Reasoning Pipeline 정상 작동

### 통합

- [ ] 엔드투엔드 워크플로우 정상 작동
- [ ] 자동화 통합 정상 작동
- [ ] 지식 네트워크 구축 정상 작동
- [ ] 성능 기준 충족
- [ ] 오류 처리 정상 작동

---

## 📝 검증 결과 기록

검증 수행 시 다음 정보를 기록하세요:

- **검증 일시**:
- **검증자**:
- **검증 환경**:
- **통과 항목**:
- **실패 항목**:
- **비고**:

---

**작성일**: 2026-01-07  
**최종 업데이트**: 2026-01-07 15:30:00
