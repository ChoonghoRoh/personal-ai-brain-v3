"""Phase 15-7-1: 부하 테스트 스크립트

사용법:
    python scripts/tests/load_test.py [--base-url http://localhost:8001] [--concurrency 10] [--requests 100]

목표:
    - 주요 API 엔드포인트 응답 시간 P95 < 500ms
    - 에러율 < 1%
    - 동시 접속 10 기준
"""
import argparse
import asyncio
import time
import statistics
from typing import NamedTuple

try:
    import aiohttp
except ImportError:
    print("aiohttp가 필요합니다: pip install aiohttp")
    exit(1)


class Result(NamedTuple):
    endpoint: str
    status: int
    elapsed_ms: float
    error: str | None


# 테스트 대상 엔드포인트
ENDPOINTS = [
    ("GET", "/health/live", None),
    ("GET", "/api/auth/status", None),
    ("GET", "/api/knowledge/chunks?limit=10", None),
    ("GET", "/api/labels?limit=10", None),
    ("GET", "/api/search?q=test&limit=5", None),
    ("GET", "/api/admin/schemas", None),
    ("GET", "/api/admin/templates?limit=10", None),
]


async def send_request(
    session: aiohttp.ClientSession,
    method: str,
    url: str,
    body: dict | None,
) -> Result:
    start = time.monotonic()
    try:
        if method == "GET":
            async with session.get(url) as resp:
                await resp.read()
                elapsed = (time.monotonic() - start) * 1000
                return Result(url, resp.status, elapsed, None)
        else:
            async with session.post(url, json=body) as resp:
                await resp.read()
                elapsed = (time.monotonic() - start) * 1000
                return Result(url, resp.status, elapsed, None)
    except Exception as e:
        elapsed = (time.monotonic() - start) * 1000
        return Result(url, 0, elapsed, str(e))


async def run_load_test(base_url: str, concurrency: int, total_requests: int):
    print(f"부하 테스트 시작: base={base_url}, concurrency={concurrency}, requests={total_requests}")
    print("=" * 70)

    results: list[Result] = []
    semaphore = asyncio.Semaphore(concurrency)

    async def bounded_request(method, path, body):
        async with semaphore:
            url = base_url + path
            return await send_request(session, method, url, body)

    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(total_requests):
            method, path, body = ENDPOINTS[i % len(ENDPOINTS)]
            tasks.append(bounded_request(method, path, body))

        results = await asyncio.gather(*tasks)

    # 분석
    total = len(results)
    errors = [r for r in results if r.status == 0 or r.status >= 500]
    successes = [r for r in results if r.status > 0 and r.status < 500]
    elapsed_list = [r.elapsed_ms for r in results]

    print(f"\n총 요청: {total}")
    print(f"성공: {len(successes)} ({len(successes)/total*100:.1f}%)")
    print(f"에러: {len(errors)} ({len(errors)/total*100:.1f}%)")

    if elapsed_list:
        elapsed_sorted = sorted(elapsed_list)
        p50 = elapsed_sorted[int(len(elapsed_sorted) * 0.5)]
        p95 = elapsed_sorted[int(len(elapsed_sorted) * 0.95)]
        p99 = elapsed_sorted[int(len(elapsed_sorted) * 0.99)]
        avg = statistics.mean(elapsed_list)

        print(f"\n응답 시간:")
        print(f"  평균: {avg:.1f}ms")
        print(f"  P50:  {p50:.1f}ms")
        print(f"  P95:  {p95:.1f}ms")
        print(f"  P99:  {p99:.1f}ms")
        print(f"  최소: {min(elapsed_list):.1f}ms")
        print(f"  최대: {max(elapsed_list):.1f}ms")

        # 합격 판정
        print("\n" + "=" * 70)
        p95_pass = p95 < 500
        error_pass = len(errors) / total < 0.01
        print(f"P95 < 500ms: {'PASS' if p95_pass else 'FAIL'} ({p95:.1f}ms)")
        print(f"에러율 < 1%: {'PASS' if error_pass else 'FAIL'} ({len(errors)/total*100:.2f}%)")

        if p95_pass and error_pass:
            print("\n결과: PASS")
        else:
            print("\n결과: FAIL — 개선 필요")

    # 엔드포인트별 상세
    print("\n엔드포인트별 평균 응답 시간:")
    from collections import defaultdict
    ep_times = defaultdict(list)
    for r in results:
        ep_times[r.endpoint].append(r.elapsed_ms)

    for ep, times in sorted(ep_times.items()):
        avg_t = statistics.mean(times)
        print(f"  {ep:50s} {avg_t:8.1f}ms (n={len(times)})")


def main():
    parser = argparse.ArgumentParser(description="Phase 15-7-1 부하 테스트")
    parser.add_argument("--base-url", default="http://localhost:8001")
    parser.add_argument("--concurrency", type=int, default=10)
    parser.add_argument("--requests", type=int, default=100)
    args = parser.parse_args()

    asyncio.run(run_load_test(args.base_url, args.concurrency, args.requests))


if __name__ == "__main__":
    main()
