#!/usr/bin/env python3
# Copyright (c) 2026 Martial Systems LLC
"""Live CoCoRaHS + RadarOnly. 404/empty stops. Does not substitute PRISM, Daymet, or Stage IV."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO), str(REPO / "src")]

from inrain.errors import FetchError  # noqa: E402
from inrain.pipeline import run_live  # noqa: E402


def main() -> int:
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "logs" / "in_live"
    cache = Path(sys.argv[2]) if len(sys.argv) > 2 else REPO / "data" / "raw" / "mrms"
    try:
        report = run_live(dest, cache_dir=cache)
    except FetchError as exc:
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "fetch_stop.txt").write_text(str(exc) + "\n", encoding="utf-8")
        print(exc)
        return 2
    print(report["question"])
    print(report["skill"])
    print(report["figures"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
