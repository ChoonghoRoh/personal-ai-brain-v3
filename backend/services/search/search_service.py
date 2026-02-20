"""검색 서비스"""
import hashlib
import json
import time
from typing import List, Dict, Optional
from functools import lru_cache
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer

try:
    import redis as redis_lib
except ImportError:
    redis_lib = None

from backend.config import QDRANT_HOST, QDRANT_PORT, COLLECTION_NAME, EMBEDDING_MODEL


class SearchCache:
    """간단한 메모리 캐시 구현"""
    
    def __init__(self, ttl: int = 3600):  # 기본 1시간 TTL
        self.cache = {}
        self.ttl = ttl
    
    def get(self, key: str) -> Optional[Dict]:
        """캐시에서 값 가져오기"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Dict):
        """캐시에 값 저장"""
        self.cache[key] = (value, time.time())
    
    def clear(self):
        """캐시 초기화"""
        self.cache.clear()
    
    def get_stats(self) -> Dict:
        """캐시 통계"""
        return {
            'backend': 'memory',
            'size': len(self.cache),
            'ttl': self.ttl
        }


class RedisSearchCache:
    """Redis 기반 검색 캐시 (Phase 15-4)"""

    def __init__(self, redis_url: str, ttl: int = 3600, db: int = 1):
        if redis_lib is None:
            raise ImportError("redis 패키지가 설치되지 않았습니다")
        self.ttl = ttl
        self.prefix = "search_cache:"
        base_url = redis_url.rsplit("/", 1)[0] if "/" in redis_url else redis_url
        url_with_db = f"{base_url}/{db}"
        self._redis = redis_lib.from_url(url_with_db, decode_responses=True)
        self._redis.ping()

    def get(self, key: str) -> Optional[Dict]:
        raw = self._redis.get(self.prefix + key)
        if raw is not None:
            return json.loads(raw)
        return None

    def set(self, key: str, value: Dict):
        self._redis.setex(
            self.prefix + key,
            self.ttl,
            json.dumps(value, ensure_ascii=False, default=str),
        )

    def clear(self):
        cursor = 0
        while True:
            cursor, keys = self._redis.scan(cursor, match=self.prefix + "*", count=100)
            if keys:
                self._redis.delete(*keys)
            if cursor == 0:
                break

    def get_stats(self) -> Dict:
        cursor, count = 0, 0
        while True:
            cursor, keys = self._redis.scan(cursor, match=self.prefix + "*", count=100)
            count += len(keys)
            if cursor == 0:
                break
        return {"backend": "redis", "size": count, "ttl": self.ttl}


def _create_search_cache(ttl: int = 3600):
    """Redis 우선, 실패 시 메모리 폴백 (Phase 15-4)"""
    from backend.config import REDIS_URL, REDIS_SEARCH_CACHE_DB
    if REDIS_URL:
        try:
            cache = RedisSearchCache(REDIS_URL, ttl=ttl, db=REDIS_SEARCH_CACHE_DB)
            print(f"[SearchCache] Redis 캐시 활성화 (TTL={ttl}s, DB={REDIS_SEARCH_CACHE_DB})")
            return cache
        except Exception as e:
            print(f"[SearchCache] Redis 연결 실패, 메모리 캐시 폴백: {e}")
    return SearchCache(ttl=ttl)


class SearchService:
    """검색 서비스 클래스"""
    
    def __init__(self, enable_cache: bool = True, cache_ttl: int = None):
        from backend.config import REDIS_SEARCH_CACHE_TTL
        self.client = None
        self.model = None
        ttl = cache_ttl if cache_ttl is not None else REDIS_SEARCH_CACHE_TTL
        self.cache = _create_search_cache(ttl) if enable_cache else None
        self._initialize()
    
    def _initialize(self):
        """초기화"""
        try:
            self.client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
            self.model = SentenceTransformer(EMBEDDING_MODEL)
        except Exception as e:
            print(f"검색 서비스 초기화 오류: {e}")
    
    def _get_cache_key(self, query: str, top_k: int, offset: int = 0, filters: Optional[Dict] = None) -> str:
        """캐시 키 생성"""
        key_data = f"{query}:{top_k}:{offset}:{str(filters) if filters else ''}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _create_qdrant_filter(self, filters: Optional[Dict] = None) -> Optional[Filter]:
        """Qdrant 필터 생성"""
        if not filters:
            return None

        conditions = []

        # 파일 경로 필터
        if filters.get('file_path'):
            conditions.append(
                FieldCondition(
                    key="file_path",
                    match=MatchValue(value=filters['file_path'])
                )
            )

        # 청크 인덱스 필터
        if filters.get('chunk_index') is not None:
            conditions.append(
                FieldCondition(
                    key="chunk_index",
                    match=MatchValue(value=filters['chunk_index'])
                )
            )

        # status 필터 (Phase 18-4: approved/draft/rejected)
        if filters.get('status'):
            conditions.append(
                FieldCondition(
                    key="status",
                    match=MatchValue(value=filters['status'])
                )
            )

        if not conditions:
            return None

        return Filter(must=conditions)
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        offset: int = 0,
        filters: Optional[Dict] = None,
        use_cache: bool = True,
        search_mode: str = "semantic",
    ) -> Dict:
        """문서 검색 (최적화된 버전).

        Args:
            query: 검색 쿼리
            top_k: 반환할 결과 수
            offset: 페이징 오프셋
            filters: 필터 조건 (file_path, chunk_index 등)
            use_cache: 캐시 사용 여부
            search_mode: "semantic" | "keyword" | "hybrid" (기본 semantic, 하위 호환)

        Returns:
            {
                'results': List[Dict],  # 검색 결과
                'total': int,
                'offset': int,
                'limit': int
            }
        """
        if not self.client or not self.model:
            return {'results': [], 'total': 0, 'offset': offset, 'limit': top_k}
        
        # 캐시 확인
        cache_key = None
        if use_cache and self.cache:
            cache_key = self._get_cache_key(query, top_k, offset, filters)
            cached_result = self.cache.get(cache_key)
            if cached_result:
                return cached_result
        
        try:
            # 쿼리 임베딩 생성
            query_embedding = self.model.encode(query).tolist()
            
            # Qdrant 필터 생성
            qdrant_filter = self._create_qdrant_filter(filters)
            
            # Qdrant에서 검색 (페이징 지원)
            # offset + top_k만큼 가져온 후 offset부터 top_k개 반환
            limit = offset + top_k
            results = self.client.query_points(
                collection_name=COLLECTION_NAME,
                query=query_embedding,
                limit=limit,
                query_filter=qdrant_filter
            )
            
            # 결과 포맷팅
            documents = []
            points = results.points[offset:offset + top_k] if offset > 0 else results.points[:top_k]
            
            for result in points:
                documents.append({
                    'document_id': str(result.id),
                    'file': result.payload.get('file_path', ''),
                    'score': float(result.score),
                    'snippet': result.payload.get('content', '')[:200] + '...',
                    'content': result.payload.get('content', ''),
                    'chunk_index': result.payload.get('chunk_index', 0)
                })
            
            # 전체 결과 수 추정 (실제로는 정확하지 않지만 대략적인 값)
            total = len(results.points) if len(results.points) < limit else limit + 1
            
            result = {
                'results': documents,
                'total': total,
                'offset': offset,
                'limit': top_k
            }
            
            # 캐시 저장
            if use_cache and self.cache and cache_key:
                self.cache.set(cache_key, result)
            
            return result
        except Exception as e:
            print(f"검색 오류: {e}")
            return {'results': [], 'total': 0, 'offset': offset, 'limit': top_k}
    
    def search_simple(self, query: str, top_k: int = 5, use_cache: bool = True) -> List[Dict]:
        """간단한 검색 (하위 호환성). use_cache=False 시 매 요청마다 새로 검색."""
        result = self.search(query, top_k=top_k, offset=0, use_cache=use_cache)
        return result["results"]
    
    def clear_cache(self):
        """캐시 초기화"""
        if self.cache:
            self.cache.clear()
    
    def get_cache_stats(self) -> Dict:
        """캐시 통계"""
        if self.cache:
            return self.cache.get_stats()
        return {'enabled': False}


# 싱글톤 인스턴스
_search_service = None

def get_search_service() -> SearchService:
    """검색 서비스 인스턴스 가져오기"""
    global _search_service
    if _search_service is None:
        _search_service = SearchService()
    return _search_service

