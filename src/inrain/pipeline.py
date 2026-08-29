# Copyright (c) 2026 Martial Systems LLC
"""Stage 0 fixture. Live fetch-or-stop. Two figures max."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from inrain.claims import require_clean, require_paths_clean
from inrain.config import LIVE_WINDOWS, PRODUCT, QUESTION
from inrain.fetch import fetch_live
from inrain.figure import write_two
from inrain.fixture import build_fixture
from inrain.models import fit_pack

try:
    from qpeforge.gate import require_claims, require_fetch, require_no_p_sfha, require_split
except ImportError:  # pragma: no cover

    def require_claims(**kwargs):
        del kwargs

    def require_fetch(**kwargs):
        del kwargs

    def require_no_p_sfha(**kwargs):
        del kwargs

    def require_split(**kwargs):
        del kwargs


def _jsonable(report: dict[str, Any]) -> dict[str, Any]:
    skip = {"holdout"}
    out = {k: v for k, v in report.items() if k not in skip}
    return out


def _run(
    log_dir: Path,
    *,
    pack,
    fixture: bool,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    require_no_p_sfha(thread_id="p_sfha")
    require_clean(QUESTION, source="question")
    fit = fit_pack(pack)
    require_split(
        spatial_ok=True,
        station_leak=bool(fit["station_leak"]),
        random_split=bool(fit["random_split"]),
        august_2026_in_train=bool(fit["august_2026_in_train"]),
        gauge_as_feature=bool(fit["gauge_as_feature"]),
        thread_id="split",
    )
    paths = write_two(log_dir, fit=fit, live=not fixture)
    require_claims(n_figures=len(paths), thread_id="claims")
    log_dir.mkdir(parents=True, exist_ok=True)
    report: dict[str, Any] = {
        "stage": "0" if fixture else "C",
        "fixture": fixture,
        "question": QUESTION,
        "product": pack.product,
        "source": pack.source,
        "n_obs": pack.n_obs,
        "n_stations": pack.n_stations,
        "n_train": fit["n_train"],
        "n_holdout": fit["n_holdout"],
        "n_train_stations": fit["n_train_stations"],
        "n_holdout_stations": fit["n_holdout_stations"],
        "units": "inches",
        "skill": fit["skill"],
        "august_2026_in_train": fit["august_2026_in_train"],
        "random_split": fit["random_split"],
        "station_leak": fit["station_leak"],
        "gauge_as_feature": fit["gauge_as_feature"],
        "p_sfha_feature": False,
        "p_sfha_label": False,
        "figures": [p.name for p in paths],
        "holdout": fit["holdout"],
        "station_bias": fit["station_bias"],
        "feature_names": fit["feature_names"],
    }
    if extra:
        report.update(extra)
    name = "stage0_report.json" if fixture else "stage_c_report.json"
    payload = _jsonable(report)
    (log_dir / name).write_text(json.dumps(payload, indent=2, default=str) + "\n")
    require_paths_clean([log_dir / name])
    return report


def stage0_fixture(log_dir: Path) -> dict[str, Any]:
    pack = build_fixture()
    return _run(log_dir, pack=pack, fixture=True)


def run_live(
    log_dir: Path,
    *,
    cache_dir: Path,
    windows: tuple[tuple[date, date], ...] = LIVE_WINDOWS,
) -> dict[str, Any]:
    pack, meta = fetch_live(cache_dir=cache_dir, windows=windows)
    require_fetch(
        cocorahs_ok=True,
        mrms_ok=True,
        product_is_radar_only=pack.product == PRODUCT,
        product_is_gauge_corr=False,
        substitute_prism=False,
        substitute_stageiv=False,
        thread_id="live.fetch",
    )
    return _run(log_dir, pack=pack, fixture=False, extra={"live": meta})
