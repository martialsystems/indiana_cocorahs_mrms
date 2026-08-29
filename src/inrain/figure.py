# Copyright (c) 2026 Martial Systems LLC
"""Two figures: holdout scatter, then held-out station bias map."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from inrain.claims import require_clean
from inrain.config import (
    FIXTURE_BIAS_SUBTITLE,
    INDIANA_RING,
    LIVE_BIAS_SUBTITLE,
    MAX_FIGURES,
    QUESTION,
)
from inrain.errors import FigureCapError


def _cap(n: int) -> None:
    if n > MAX_FIGURES:
        raise FigureCapError(f"this tree stops at {MAX_FIGURES} figures")


def _subsample(n: int, *, cap: int = 4000, seed: int = 0) -> np.ndarray:
    if n <= cap:
        return np.arange(n)
    rng = np.random.default_rng(seed)
    return np.sort(rng.choice(n, size=cap, replace=False))


def write_scatter(dest: Path, *, fit: dict[str, Any], title: str, subtitle: str) -> Path:
    require_clean(title, source="fig1_title")
    require_clean(subtitle, source="fig1_sub")
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ho = fit["holdout"]
    y = np.asarray(ho["gauge_in"], dtype=float)
    ident = np.asarray(ho["identity_in"], dtype=float)
    hgb = np.asarray(ho["hgb_in"], dtype=float)
    idx = _subsample(y.size)
    y, ident, hgb = y[idx], ident[idx], hgb[idx]
    hi = float(np.nanmax([y.max(), ident.max(), hgb.max(), 1.0]))
    sk = fit["skill"]
    fig, axes = plt.subplots(1, 2, figsize=(8.2, 4.2))
    panels = (
        (axes[0], ident, sk["identity"]["rmse_in"], "RadarOnly"),
        (axes[1], hgb, sk["hgb"]["rmse_in"], "HGB"),
    )
    for ax, pred, rmse, name in panels:
        ax.scatter(y, pred, s=6, alpha=0.35, c="#334155", linewidths=0)
        ax.plot([0, hi], [0, hi], color="#b91c1c", lw=1.0)
        ax.set_xlim(0, hi)
        ax.set_ylim(0, hi)
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlabel("CoCoRaHS (in)")
        ax.set_ylabel(f"{name} (in)")
        ax.set_title(f"{name} RMSE {rmse:.3f} in", fontsize=9)
    fig.suptitle(title, fontsize=10)
    fig.text(0.5, 0.02, subtitle, ha="center", fontsize=8)
    fig.subplots_adjust(bottom=0.16, top=0.86, wspace=0.28)
    dest.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(dest, dpi=130)
    plt.close(fig)
    return dest


def write_bias_map(dest: Path, *, fit: dict[str, Any], title: str, subtitle: str) -> Path:
    require_clean(title, source="fig2_title")
    require_clean(subtitle, source="fig2_sub")
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = fit["station_bias"]
    lon = np.array([r["lon"] for r in rows], dtype=float)
    lat = np.array([r["lat"] for r in rows], dtype=float)
    b = np.array([r["bias_in"] for r in rows], dtype=float)
    ring = np.asarray(INDIANA_RING, dtype=float)
    vmax = max(0.15, float(np.nanpercentile(np.abs(b), 95)))
    fig, ax = plt.subplots(figsize=(6.4, 6.6))
    ax.plot(ring[:, 0], ring[:, 1], color="#64748b", lw=1.1)
    sc = ax.scatter(lon, lat, c=b, cmap="RdBu_r", vmin=-vmax, vmax=vmax, s=28, edgecolors="#0f172a", linewidths=0.3)
    cb = fig.colorbar(sc, ax=ax, fraction=0.046, pad=0.04)
    cb.set_label("mean RadarOnly minus CoCoRaHS (in)", fontsize=8)
    ax.set_xlabel("lon")
    ax.set_ylabel("lat")
    ax.set_title(title, fontsize=10)
    ax.set_aspect("equal", adjustable="box")
    fig.text(0.5, 0.02, subtitle, ha="center", fontsize=8)
    fig.subplots_adjust(bottom=0.12, top=0.90)
    dest.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(dest, dpi=130)
    plt.close(fig)
    return dest


def write_two(log_dir: Path, *, fit: dict[str, Any], live: bool = False) -> list[Path]:
    sub = LIVE_BIAS_SUBTITLE if live else FIXTURE_BIAS_SUBTITLE
    ranking = (
        f"Ridge {fit['skill']['ridge']['rmse_in']:.3f} in RMSE, "
        f"RadarOnly {fit['skill']['identity']['rmse_in']:.3f}, "
        f"HGB {fit['skill']['hgb']['rmse_in']:.3f}, "
        f"held-out stations"
    )
    require_clean(QUESTION, source="question")
    paths = [
        write_scatter(
            log_dir / "scatter.png",
            fit=fit,
            title="Held-out CoCoRaHS vs RadarOnly and HGB",
            subtitle=ranking,
        ),
        write_bias_map(
            log_dir / "bias_map.png",
            fit=fit,
            title="Held-out station mean RadarOnly minus CoCoRaHS",
            subtitle=sub,
        ),
    ]
    _cap(len(paths))
    return paths
