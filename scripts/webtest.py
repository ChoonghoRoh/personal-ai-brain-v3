#!/usr/bin/env python3
"""
Web 테스트 실행 스크립트 — [webtest: X-Y start] 명령으로 phase 단위 E2E 웹테스트 자동 실행.

사용법:
  python3 scripts/webtest.py 9-1 start   # phase 9-1 E2E 실행 (e2e/phase-9-1.spec.js 있으면)
  python3 scripts/webtest.py 9-3 start   # phase 9-3 E2E 실행
  npm run webtest:start -- 9-1           # package.json 스크립트 경유 (python 호출)

E2E 스펙이 없는 phase는 실행 불가. 그 경우 docs/webtest/phase-unit-user-test-guide.md
방안 A(MCP) 또는 방안 B(페르소나)로 수동/에이전트 테스트 수행.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def e2e_spec_path(phase: str) -> Path:
    """phase '9-1' -> e2e/phase-9-1.spec.js"""
    return project_root() / "e2e" / f"phase-{phase}.spec.js"


def run_webtest_start(phase: str) -> int:
    root = project_root()
    spec = e2e_spec_path(phase)
    if not spec.exists():
        print(f"[webtest] E2E 스펙 없음: {spec}", file=sys.stderr)
        print(
            "  → 해당 phase용 E2E 스펙을 추가하거나, docs/webtest/phase-unit-user-test-guide.md",
            file=sys.stderr,
        )
        print("    방안 A(MCP) / 방안 B(페르소나)로 테스트를 수행하세요.", file=sys.stderr)
        return 1
    cmd = ["npx", "playwright", "test", str(spec.relative_to(root))]
    print(f"[webtest] 실행: {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=root).returncode


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phase 단위 웹테스트 실행 (webtest: X-Y start)",
        epilog="예: python scripts/webtest.py 9-3 start",
    )
    parser.add_argument(
        "phase",
        metavar="X-Y",
        help="Phase 번호 (예: 9-1, 9-3)",
    )
    parser.add_argument(
        "action",
        nargs="?",
        default="start",
        choices=["start"],
        help="동작 (기본: start)",
    )
    args = parser.parse_args()
    # phase 형식 간단 검사 (숫자-숫자)
    p = args.phase.strip()
    if "-" not in p or len(p.split("-")) != 2:
        print(f"[webtest] 잘못된 phase 형식: {args.phase} (예: 9-1, 9-3)", file=sys.stderr)
        return 1
    if args.action == "start":
        return run_webtest_start(p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
