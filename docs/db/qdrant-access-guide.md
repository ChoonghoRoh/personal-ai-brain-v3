# Qdrant 접속 가이드

## 📋 개요

Qdrant는 벡터 데이터베이스로, 문서 임베딩을 저장하고 의미 기반 검색을 제공합니다.

## 🔧 연결 정보

- **웹 대시보드**: `http://localhost:6333/dashboard`
- **REST API**: `http://localhost:6333`
- **gRPC API**: `localhost:6334`
- **컨테이너명**: `qdrant`

## 🌐 웹 대시보드 접속

### 브라우저에서 접속

1. **웹 브라우저 열기**
2. 다음 URL 접속: `http://localhost:6333/dashboard`
3. Qdrant 웹 인터페이스가 표시됩니다

### 대시보드 기능

- **컬렉션 목록**: 저장된 벡터 컬렉션 확인
- **포인트 검색**: 벡터 검색 및 유사도 검색
- **통계 정보**: 컬렉션별 포인트 수, 차원 등
- **API 문서**: REST API 문서 확인

## 🔌 REST API 사용

### 기본 엔드포인트

**헬스 체크:**
```bash
curl http://localhost:6333/health
```

**컬렉션 목록:**
```bash
curl http://localhost:6333/collections
```

**특정 컬렉션 정보:**
```bash
curl http://localhost:6333/collections/{collection_name}
```

**컬렉션 내 포인트 검색:**
```bash
curl -X POST http://localhost:6333/collections/{collection_name}/points/search \
  -H "Content-Type: application/json" \
  -d '{
    "vector": [0.1, 0.2, ...],
    "limit": 10
  }'
```

### Python 클라이언트 사용

```python
from qdrant_client import QdrantClient

# 클라이언트 생성
client = QdrantClient(host="localhost", port=6333)

# 컬렉션 목록 조회
collections = client.get_collections()
print(collections)

# 컬렉션 정보 조회
collection_info = client.get_collection("your_collection_name")
print(collection_info)

# 벡터 검색
search_results = client.search(
    collection_name="your_collection_name",
    query_vector=[0.1, 0.2, ...],
    limit=10
)
```

## 📊 프로젝트에서 사용하는 컬렉션

### 기본 컬렉션

프로젝트에서 사용하는 컬렉션은 보통 `knowledge` 또는 `documents`입니다.

**컬렉션 확인:**
```bash
curl http://localhost:6333/collections
```

**컬렉션 상세 정보:**
```bash
curl http://localhost:6333/collections/knowledge
```

## 🛠️ 문제 해결

### Qdrant가 실행되지 않을 때

```bash
# 컨테이너 상태 확인
docker compose ps qdrant

# 컨테이너 로그 확인
docker compose logs qdrant

# 컨테이너 재시작
docker compose restart qdrant
```

### 포트 충돌

다른 서비스가 6333 포트를 사용하고 있을 수 있습니다.

```bash
# 포트 사용 확인
lsof -i :6333
lsof -i :6334
```

### 데이터 확인

```bash
# 컬렉션 목록 확인
curl http://localhost:6333/collections

# 특정 컬렉션의 포인트 수 확인
curl http://localhost:6333/collections/knowledge | jq '.result.points_count'
```

## 📝 유용한 명령어

### 컬렉션 삭제 (주의!)

```bash
curl -X DELETE http://localhost:6333/collections/{collection_name}
```

### 컬렉션 재생성

프로젝트의 `scripts/embed_and_store.py`를 사용:

```bash
cd /Users/map-rch/WORKS/personal-ai-brain-v2
source scripts/venv/bin/activate
python scripts/embed_and_store.py --recreate
```

### 데이터 백업

Qdrant 데이터는 `./qdrant-data` 디렉토리에 저장됩니다.

```bash
# 데이터 백업
tar -czf qdrant_backup_$(date +%Y%m%d_%H%M%S).tar.gz qdrant-data/

# 데이터 복원
tar -xzf qdrant_backup_YYYYMMDD_HHMMSS.tar.gz
```

## 🔗 관련 문서

- [docker-compose-integration-guide.md](../phases/phase-8-0/phase8-3-1-docker-compose-integration-guide.md) - Docker Compose 통합 관리
- [Qdrant 공식 문서](https://qdrant.tech/documentation/)
- [Qdrant Python 클라이언트](https://github.com/qdrant/qdrant-client)

---

**작성일**: 2026-01-28  
**버전**: 1.0
