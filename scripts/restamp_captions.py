#!/usr/bin/env python3
# Copyright (c) 2026 Martial Systems LLC
"""Restamp live PNG footers from locked skill JSON. Does not re-fit."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO), str(REPO / "src")]

from inrain.config import LIVE_BIAS_SUBTITLE  # noqa: E402
from inrain.figure import write_bias_map  # noqa: E402


def main() -> int:
    log_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "logs" / "in_live"
    report = json.loads((log_dir / "stage_c_report.json").read_text(encoding="utf-8"))
    write_bias_map(
        log_dir / "bias_map.png",
        fit={"station_bias": report["station_bias"]},
        title="Held-out station mean RadarOnly minus CoCoRaHS",
        subtitle=LIVE_BIAS_SUBTITLE,
    )
    print(LIVE_BIAS_SUBTITLE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
