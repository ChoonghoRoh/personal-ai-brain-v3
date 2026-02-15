# Phase 7.6: 키워드 추출 및 자동 라벨링 테스트 시나리오

## 🎯 테스트 목표

키워드 추출 및 자동 라벨링 기능이 정상적으로 작동하는지 검증합니다.

## 📋 테스트 전제 조건

### 환경 준비

1. **서버 실행**

   ```bash
   python scripts/start_server.py
   ```

2. **데이터베이스 초기화 및 문서 임베딩**

   ```bash
   python scripts/embed_and_store.py
   ```

3. **필수 패키지 확인**
   - `openai` (선택적, OpenAI API 사용 시)
   - `gpt4all` (선택적, GPT4All 사용 시)

### 테스트 데이터

- `docs/` 폴더의 .md 파일들
- `brain/` 폴더의 .md 파일들 (하위 폴더 포함)

---

## 🧪 테스트 시나리오

### 시나리오 1: 정규식 기반 키워드 추출 (기본)

**목적**: 정규식 기반 키워드 추출이 정상 작동하는지 확인

**절차**:

1. `docs` 폴더의 .md 파일에서 키워드 추출 실행
2. 추출된 키워드 확인
3. 라벨 자동 생성 확인
4. 청크 자동 라벨링 확인

**실행 명령**:

```bash
python scripts/extract_keywords_and_labels.py --docs-only
```

**예상 결과**:

- ✅ 각 .md 파일에서 키워드 추출 성공
- ✅ 추출된 키워드로 라벨 자동 생성
- ✅ 해당 문서의 청크에 키워드 매칭하여 라벨 연결
- ✅ 라벨 상태: `status="suggested"`, `source="ai"`

**검증 방법**:

```sql
-- 생성된 라벨 확인
SELECT * FROM labels WHERE label_type = 'keyword' ORDER BY id DESC LIMIT 10;

-- 자동 라벨링된 청크 확인
SELECT kl.*, l.name, kc.content
FROM knowledge_labels kl
JOIN labels l ON kl.label_id = l.id
JOIN knowledge_chunks kc ON kl.chunk_id = kc.id
WHERE kl.source = 'ai' AND kl.status = 'suggested'
ORDER BY kl.created_at DESC LIMIT 10;
```

---

### 시나리오 2: brain 폴더 포함 키워드 추출

**목적**: brain 폴더의 기존 파일도 키워드 추출이 되는지 확인

**절차**:

1. `docs` + `brain` 폴더 모두에서 키워드 추출 실행
2. 하위 폴더의 파일도 포함되는지 확인
3. 중복 처리 방지 확인

**실행 명령**:

```bash
python scripts/extract_keywords_and_labels.py
```

**예상 결과**:

- ✅ `docs/` 폴더의 모든 .md 파일 처리
- ✅ `brain/` 폴더의 모든 하위 폴더 .md 파일 처리
  - `brain/system/*.md`
  - `brain/projects/*/*.md`
- ✅ 중복 파일은 한 번만 처리

**검증 방법**:

- 콘솔 출력에서 처리된 파일 목록 확인
- 각 파일의 키워드 추출 결과 확인

---

### 시나리오 3: LLM 기반 키워드 추출 (GPT4All)

**목적**: LLM을 사용한 키워드 추출이 정상 작동하는지 확인

**절차**:

1. GPT4All을 사용한 키워드 추출 실행
2. 정규식 기반과 비교하여 키워드 품질 확인
3. 불용어 자동 필터링 확인

**실행 명령**:

```bash
python scripts/extract_keywords_and_labels.py --llm
```

**예상 결과**:

- ✅ LLM 기반 키워드 추출 성공
- ✅ 문맥을 이해한 의미 있는 키워드 추출
- ✅ 불용어 자동 필터링
- ✅ 정규식 기반보다 더 정확한 키워드

**검증 방법**:

- 추출된 키워드 목록 확인
- 키워드가 문서 내용과 관련 있는지 확인
- 불용어(것, 수, 등)가 제외되었는지 확인

---

### 시나리오 4: LLM 기반 키워드 추출 (OpenAI API)

**목적**: OpenAI API를 사용한 키워드 추출이 정상 작동하는지 확인

**전제 조건**:

- `OPENAI_API_KEY` 환경 변수 설정

**절차**:

1. OpenAI API를 사용한 키워드 추출 실행
2. GPT4All과 비교하여 키워드 품질 확인

**실행 명령**:

```bash
export OPENAI_API_KEY="your-api-key"
python scripts/extract_keywords_and_labels.py --llm --openai
```

**예상 결과**:

- ✅ OpenAI API 기반 키워드 추출 성공
- ✅ GPT4All보다 더 정확한 키워드 추출
- ✅ 문맥 이해 기반 키워드 추출

**검증 방법**:

- 추출된 키워드 목록 확인
- 키워드 품질 평가

---

### 시나리오 5: API 엔드포인트를 통한 키워드 추출

**목적**: REST API를 통한 문서별 키워드 추출이 정상 작동하는지 확인

**절차**:

1. 서버 실행 확인
2. 문서 ID 조회
3. API 호출하여 키워드 추출
4. 결과 확인

**실행 명령**:

```bash
# 문서 목록 조회
curl http://localhost:8001/api/documents | jq '.[0].id'

# 키워드 추출 (정규식 기반)
curl -X POST "http://localhost:8001/api/knowledge/documents/1/extract-keywords?top_n=10&use_llm=false" | jq

# 키워드 추출 (LLM 기반)
curl -X POST "http://localhost:8001/api/knowledge/documents/1/extract-keywords?top_n=10&use_llm=true" | jq
```

**예상 결과**:

- ✅ API 호출 성공 (200 OK)
- ✅ 키워드 목록 반환
- ✅ 생성된 라벨 수 반환
- ✅ 라벨링된 청크 수 반환

**응답 형식**:

```json
{
  "document_id": 1,
  "keywords": ["키워드1", "키워드2", ...],
  "labels_created": 5,
  "chunks_labeled": 10
}
```

---

### 시나리오 6: 중복 라벨 방지

**목적**: 동일한 키워드로 여러 번 실행해도 중복 라벨이 생성되지 않는지 확인

**절차**:

1. 첫 번째 실행: 키워드 추출 및 라벨 생성
2. 두 번째 실행: 동일한 키워드로 다시 실행
3. 중복 라벨 생성 여부 확인

**실행 명령**:

```bash
# 첫 번째 실행
python scripts/extract_keywords_and_labels.py --docs-only

# 두 번째 실행 (동일한 파일)
python scripts/extract_keywords_and_labels.py --docs-only
```

**예상 결과**:

- ✅ 첫 번째 실행: 새 라벨 생성
- ✅ 두 번째 실행: 기존 라벨 재사용 (중복 생성 없음)
- ✅ 동일한 청크에 중복 라벨 연결 방지

**검증 방법**:

```sql
-- 라벨 중복 확인
SELECT name, COUNT(*) as count
FROM labels
WHERE label_type = 'keyword'
GROUP BY name
HAVING COUNT(*) > 1;

-- 청크 라벨 중복 확인
SELECT chunk_id, label_id, COUNT(*) as count
FROM knowledge_labels
GROUP BY chunk_id, label_id
HAVING COUNT(*) > 1;
```

---

### 시나리오 7: 문서가 DB에 없는 경우 처리

**목적**: 문서가 DB에 저장되지 않은 경우 적절한 메시지가 표시되는지 확인

**절차**:

1. DB에 없는 파일 경로로 키워드 추출 시도
2. 오류 메시지 확인

**예상 결과**:

- ✅ "⚠️ 문서를 찾을 수 없음: {file_path}" 메시지 출력
- ✅ "💡 팁: 먼저 'python scripts/embed_and_store.py'를 실행하여 문서를 DB에 저장하세요." 안내 메시지 출력
- ✅ 스크립트는 계속 실행되어 다른 파일 처리

---

### 시나리오 8: 빈 파일 처리

**목적**: 빈 파일이나 내용이 없는 파일 처리 확인

**절차**:

1. 빈 .md 파일 생성
2. 키워드 추출 실행
3. 처리 결과 확인

**예상 결과**:

- ✅ 빈 파일은 스킵하거나 빈 키워드 리스트 반환
- ✅ 오류 없이 다음 파일 처리 계속

---

### 시나리오 9: 대용량 파일 처리

**목적**: 큰 파일도 정상적으로 처리되는지 확인

**절차**:

1. 큰 .md 파일 (예: 10,000줄 이상) 생성
2. 키워드 추출 실행
3. 처리 시간 및 결과 확인

**예상 결과**:

- ✅ 대용량 파일도 정상 처리
- ✅ LLM 사용 시 토큰 제한 고려 (3000자 제한)
- ✅ 처리 시간이 합리적 범위 내

---

### 시나리오 10: 한글/영문 혼합 문서 처리

**목적**: 한글과 영문이 혼합된 문서도 정상 처리되는지 확인

**절차**:

1. 한글/영문 혼합 .md 파일 생성
2. 키워드 추출 실행
3. 한글 및 영문 키워드 추출 확인

**예상 결과**:

- ✅ 한글 키워드 정상 추출
- ✅ 영문 키워드도 추출 가능 (정규식 기반)
- ✅ LLM 사용 시 더 정확한 키워드 추출

---

## ✅ 통합 테스트 체크리스트

### 기본 기능

- [ ] 정규식 기반 키워드 추출 작동
- [ ] LLM 기반 키워드 추출 작동 (GPT4All)
- [ ] LLM 기반 키워드 추출 작동 (OpenAI API)
- [ ] brain 폴더 하위 폴더 포함 처리
- [ ] docs 폴더 하위 폴더 포함 처리

### 데이터 처리

- [ ] 라벨 자동 생성
- [ ] 청크 자동 라벨링
- [ ] 중복 라벨 방지
- [ ] 중복 청크 라벨 방지

### API 기능

- [ ] REST API 키워드 추출 작동
- [ ] API 응답 형식 정확
- [ ] 오류 처리 적절

### 예외 처리

- [ ] DB에 없는 문서 처리
- [ ] 빈 파일 처리
- [ ] 대용량 파일 처리
- [ ] 한글/영문 혼합 문서 처리

---

## 📊 성능 기준

- **처리 속도**: 파일당 평균 1초 이내 (정규식 기반)
- **LLM 처리 속도**: 파일당 평균 5초 이내 (GPT4All)
- **메모리 사용**: 파일당 평균 50MB 이내
- **정확도**: 추출된 키워드 중 80% 이상이 문서와 관련 있음

---

## 🔍 검증 SQL 쿼리

### 1. 생성된 라벨 확인

```sql
SELECT id, name, label_type, description, created_at
FROM labels
WHERE label_type = 'keyword'
ORDER BY created_at DESC;
```

### 2. 자동 라벨링된 청크 확인

```sql
SELECT
    kl.id,
    kl.chunk_id,
    kl.label_id,
    l.name as label_name,
    kl.status,
    kl.source,
    kl.confidence,
    kc.content as chunk_content_preview,
    d.file_path
FROM knowledge_labels kl
JOIN labels l ON kl.label_id = l.id
JOIN knowledge_chunks kc ON kl.chunk_id = kc.id
JOIN documents d ON kc.document_id = d.id
WHERE kl.source = 'ai' AND kl.status = 'suggested'
ORDER BY kl.created_at DESC
LIMIT 20;
```

### 3. 문서별 라벨링 통계

```sql
SELECT
    d.file_path,
    COUNT(DISTINCT kl.label_id) as label_count,
    COUNT(kl.id) as chunk_label_count
FROM documents d
LEFT JOIN knowledge_chunks kc ON d.id = kc.document_id
LEFT JOIN knowledge_labels kl ON kc.id = kl.chunk_id AND kl.source = 'ai'
GROUP BY d.id, d.file_path
ORDER BY label_count DESC;
```

### 4. 키워드별 사용 빈도

```sql
SELECT
    l.name as keyword,
    COUNT(kl.id) as usage_count,
    COUNT(DISTINCT kc.document_id) as document_count
FROM labels l
LEFT JOIN knowledge_labels kl ON l.id = kl.label_id
LEFT JOIN knowledge_chunks kc ON kl.chunk_id = kc.id
WHERE l.label_type = 'keyword'
GROUP BY l.id, l.name
ORDER BY usage_count DESC;
```

---

## 📝 테스트 실행 순서

1. **환경 준비**

   ```bash
   python scripts/embed_and_store.py
   ```

2. **기본 기능 테스트**

   ```bash
   python scripts/extract_keywords_and_labels.py --docs-only
   ```

3. **전체 폴더 테스트**

   ```bash
   python scripts/extract_keywords_and_labels.py
   ```

4. **LLM 테스트** (선택적)

   ```bash
   python scripts/extract_keywords_and_labels.py --llm
   ```

5. **API 테스트**

   ```bash
   curl -X POST "http://localhost:8001/api/knowledge/documents/1/extract-keywords?top_n=10&use_llm=false"
   ```

6. **결과 검증**
   - SQL 쿼리로 데이터 확인
   - Knowledge Admin UI에서 확인

---

## 🎯 성공 기준

- ✅ 모든 시나리오 통과
- ✅ 오류 없이 실행 완료
- ✅ 데이터 정합성 유지
- ✅ 성능 기준 충족
- ✅ 사용자 경험 만족
