# Copyright (c) 2026 Martial Systems LLC
"""Two figures: holdout scatter, then held-out station bias map."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from inrain.claims import require_clean
from inrain.config import (
    BIAS_MAP_PAD_DEG,
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
    fig, ax = plt.subplots(figsize=(6.8, 7.6))
    ax.plot(ring[:, 0], ring[:, 1], color="#64748b", lw=1.1)
    sc = ax.scatter(
        lon,
        lat,
        c=b,
        cmap="RdBu_r",
        vmin=-vmax,
        vmax=vmax,
        s=28,
        edgecolors="#0f172a",
        linewidths=0.3,
        zorder=3,
        clip_on=True,
    )
    pad = BIAS_MAP_PAD_DEG
    ax.set_xlim(float(ring[:, 0].min()) - pad, float(ring[:, 0].max()) + pad)
    ax.set_ylim(float(ring[:, 1].min()) - pad, float(ring[:, 1].max()) + pad)
    ax.set_aspect("equal", adjustable="box")
    cb = fig.colorbar(sc, ax=ax, fraction=0.046, pad=0.04)
    cb.set_label("mean RadarOnly minus CoCoRaHS (in)", fontsize=8)
    ax.set_xlabel("lon")
    ax.set_ylabel("lat")
    ax.set_title(title, fontsize=10)
    dest.parent.mkdir(parents=True, exist_ok=True)
    _caption(fig, subtitle)
    fig.savefig(dest, dpi=130, bbox_inches="tight", pad_inches=0.18)
    plt.close(fig)
    return dest


def _caption(fig, subtitle: str) -> None:
    lines = [ln.strip() for ln in subtitle.split(". ") if ln.strip()]
    if len(lines) >= 2:
        fig.text(0.5, 0.055, lines[0].rstrip(".") + ".", ha="center", fontsize=8)
        fig.text(0.5, 0.022, ". ".join(lines[1:]), ha="center", fontsize=7.5)
        fig.subplots_adjust(bottom=0.12, top=0.93, left=0.12, right=0.88)
    else:
        fig.text(0.5, 0.03, subtitle, ha="center", fontsize=8)
        fig.subplots_adjust(bottom=0.10, top=0.93, left=0.12, right=0.88)


def scatter_subtitle(fit: dict[str, Any], *, live: bool) -> str:
    ident = float(fit["skill"]["identity"]["rmse_in"])
    hgb = float(fit["skill"]["hgb"]["rmse_in"])
    core = f"RadarOnly {ident:.3f} in RMSE; HGB {hgb:.3f}"
    if live:
        return f"{core}. 12Z 24h vs 7am local; volunteer QC."
    return f"{core}. Fixture; does not rescue live skill."


def restamp_footer(
    path: Path,
    *,
    subtitle: str,
    figsize: tuple[float, float],
    crop_top: float = 0.88,
) -> Path:
    """Replace the footer on an existing PNG. Does not re-fit."""
    require_clean(subtitle, source="footer")
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    img = np.asarray(plt.imread(path), dtype=float)
    if img.max() > 1.0:
        img = img / 255.0
    r1 = max(1, int(img.shape[0] * crop_top))
    crop = img[:r1]
    fig, ax = plt.subplots(figsize=figsize)
    ax.imshow(crop)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("")
    for spine in ax.spines.values():
        spine.set_visible(False)
    lines = [ln.strip() for ln in subtitle.split(". ") if ln.strip()]
    if len(lines) >= 2:
        fig.text(0.5, 0.045, lines[0].rstrip(".") + ".", ha="center", fontsize=8)
        fig.text(0.5, 0.018, ". ".join(lines[1:]), ha="center", fontsize=7.5)
        fig.subplots_adjust(bottom=0.12, top=0.99, left=0.01, right=0.99)
    else:
        fig.text(0.5, 0.03, subtitle, ha="center", fontsize=8)
        fig.subplots_adjust(bottom=0.10, top=0.99, left=0.01, right=0.99)
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return path


def write_two(log_dir: Path, *, fit: dict[str, Any], live: bool = False) -> list[Path]:
    sub = LIVE_BIAS_SUBTITLE if live else FIXTURE_BIAS_SUBTITLE
    require_clean(QUESTION, source="question")
    paths = [
        write_scatter(
            log_dir / "scatter.png",
            fit=fit,
            title="Held-out CoCoRaHS vs RadarOnly and HGB",
            subtitle=scatter_subtitle(fit, live=live),
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
