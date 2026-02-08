#!/usr/bin/env python3
"""
검색 성능 벤치마크 테스트 스크립트
"""
import time
import statistics
from typing import List, Dict
import sys
from pathlib import Path

# 프로젝트 루트 경로 설정
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.services.search.search_service import SearchService, get_search_service


def benchmark_search(
    search_service: SearchService,
    queries: List[str],
    top_k: int = 5,
    iterations: int = 3,
    use_cache: bool = True
) -> Dict:
    """검색 성능 벤치마크"""
    
    print(f"\n{'='*60}")
    print(f"검색 성능 벤치마크 테스트")
    print(f"{'='*60}")
    print(f"쿼리 수: {len(queries)}")
    print(f"top_k: {top_k}")
    print(f"반복 횟수: {iterations}")
    print(f"캐시 사용: {use_cache}")
    print(f"{'='*60}\n")
    
    # 캐시 초기화
    if not use_cache:
        search_service.clear_cache()
    
    all_times = []
    cache_hits = 0
    cache_misses = 0
    
    for iteration in range(iterations):
        print(f"\n[반복 {iteration + 1}/{iterations}]")
        iteration_times = []
        
        for i, query in enumerate(queries, 1):
            start_time = time.time()
            
            # 첫 번째 반복이 아니면 캐시 히트 가능
            is_first_iteration = iteration == 0
            
            result = search_service.search(
                query=query,
                top_k=top_k,
                offset=0,
                use_cache=use_cache
            )
            
            elapsed_time = time.time() - start_time
            iteration_times.append(elapsed_time)
            all_times.append(elapsed_time)
            
            if not is_first_iteration and use_cache:
                cache_hits += 1
            else:
                cache_misses += 1
            
            print(f"  쿼리 {i}/{len(queries)}: {query[:50]:<50} | {elapsed_time*1000:.2f}ms | 결과: {len(result.get('results', []))}개")
        
        avg_time = statistics.mean(iteration_times)
        print(f"  평균 응답 시간: {avg_time*1000:.2f}ms")
    
    # 통계 계산
    if all_times:
        stats = {
            'total_queries': len(queries) * iterations,
            'total_time': sum(all_times),
            'avg_time': statistics.mean(all_times),
            'median_time': statistics.median(all_times),
            'min_time': min(all_times),
            'max_time': max(all_times),
            'std_dev': statistics.stdev(all_times) if len(all_times) > 1 else 0,
            'queries_per_second': len(queries) * iterations / sum(all_times) if sum(all_times) > 0 else 0,
            'cache_hits': cache_hits,
            'cache_misses': cache_misses,
            'cache_hit_rate': cache_hits / (cache_hits + cache_misses) if (cache_hits + cache_misses) > 0 else 0
        }
    else:
        stats = {}
    
    return stats


def benchmark_pagination(
    search_service: SearchService,
    query: str,
    page_size: int = 10,
    num_pages: int = 5
) -> Dict:
    """페이징 성능 벤치마크"""
    
    print(f"\n{'='*60}")
    print(f"페이징 성능 벤치마크 테스트")
    print(f"{'='*60}")
    print(f"쿼리: {query}")
    print(f"페이지 크기: {page_size}")
    print(f"페이지 수: {num_pages}")
    print(f"{'='*60}\n")
    
    times = []
    
    for page in range(num_pages):
        offset = page * page_size
        start_time = time.time()
        
        result = search_service.search(
            query=query,
            top_k=page_size,
            offset=offset,
            use_cache=False  # 페이징 테스트는 캐시 없이
        )
        
        elapsed_time = time.time() - start_time
        times.append(elapsed_time)
        
        print(f"  페이지 {page + 1}: offset={offset}, limit={page_size} | {elapsed_time*1000:.2f}ms | 결과: {len(result.get('results', []))}개")
    
    if times:
        stats = {
            'total_pages': num_pages,
            'avg_time': statistics.mean(times),
            'median_time': statistics.median(times),
            'min_time': min(times),
            'max_time': max(times)
        }
    else:
        stats = {}
    
    return stats


def print_stats(stats: Dict, title: str = "벤치마크 결과"):
    """통계 출력"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    
    if not stats:
        print("통계 데이터가 없습니다.")
        return
    
    print(f"\n[성능 지표]")
    print(f"  총 쿼리 수: {stats.get('total_queries', 'N/A')}")
    print(f"  총 소요 시간: {stats.get('total_time', 0)*1000:.2f}ms")
    print(f"  평균 응답 시간: {stats.get('avg_time', 0)*1000:.2f}ms")
    print(f"  중앙값 응답 시간: {stats.get('median_time', 0)*1000:.2f}ms")
    print(f"  최소 응답 시간: {stats.get('min_time', 0)*1000:.2f}ms")
    print(f"  최대 응답 시간: {stats.get('max_time', 0)*1000:.2f}ms")
    print(f"  표준 편차: {stats.get('std_dev', 0)*1000:.2f}ms")
    
    if 'queries_per_second' in stats:
        print(f"  초당 쿼리 수: {stats.get('queries_per_second', 0):.2f}")
    
    if 'cache_hit_rate' in stats:
        print(f"\n[캐시 통계]")
        print(f"  캐시 히트: {stats.get('cache_hits', 0)}")
        print(f"  캐시 미스: {stats.get('cache_misses', 0)}")
        print(f"  캐시 히트율: {stats.get('cache_hit_rate', 0)*100:.2f}%")
    
    print(f"{'='*60}\n")


def main():
    """메인 함수"""
    # 테스트 쿼리 목록
    test_queries = [
        "Python 프로그래밍",
        "데이터베이스 쿼리",
        "머신러닝 알고리즘",
        "웹 개발",
        "API 설계",
        "프로젝트 관리",
        "코드 리뷰",
        "테스트 자동화",
        "성능 최적화",
        "보안 강화"
    ]
    
    # 검색 서비스 초기화
    print("검색 서비스 초기화 중...")
    search_service = get_search_service()
    
    # 1. 기본 검색 성능 테스트 (캐시 없음)
    print("\n[1단계] 기본 검색 성능 테스트 (캐시 없음)")
    stats_no_cache = benchmark_search(
        search_service=search_service,
        queries=test_queries[:5],  # 처음 5개만
        top_k=5,
        iterations=1,
        use_cache=False
    )
    print_stats(stats_no_cache, "기본 검색 성능 (캐시 없음)")
    
    # 2. 캐시 사용 검색 성능 테스트
    print("\n[2단계] 캐시 사용 검색 성능 테스트")
    stats_with_cache = benchmark_search(
        search_service=search_service,
        queries=test_queries[:5],
        top_k=5,
        iterations=3,  # 3번 반복하여 캐시 효과 확인
        use_cache=True
    )
    print_stats(stats_with_cache, "캐시 사용 검색 성능")
    
    # 3. 페이징 성능 테스트
    print("\n[3단계] 페이징 성능 테스트")
    pagination_stats = benchmark_pagination(
        search_service=search_service,
        query=test_queries[0],
        page_size=10,
        num_pages=5
    )
    print_stats(pagination_stats, "페이징 성능")
    
    # 4. 캐시 통계
    cache_stats = search_service.get_cache_stats()
    print(f"\n[캐시 상태]")
    print(f"  캐시 크기: {cache_stats.get('size', 0)}")
    print(f"  TTL: {cache_stats.get('ttl', 0)}초")
    print(f"  활성화: {cache_stats.get('enabled', False)}")
    
    print("\n벤치마크 테스트 완료!")


if __name__ == "__main__":
    main()
