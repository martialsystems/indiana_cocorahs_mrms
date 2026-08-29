# Copyright (c) 2026 Martial Systems LLC
"""Leak-free station-day features. CoCoRaHS is the label, never a column."""

from __future__ import annotations

import numpy as np

from inrain.config import FEATURE_NAMES
from inrain.pack import RainPack


def matrix_x(pack: RainPack) -> np.ndarray:
    d = np.asarray(pack.dates).astype("datetime64[D]")
    y = d.astype("datetime64[Y]")
    doy = (d - y).astype("timedelta64[D]").astype(int) + 1
    ang = 2.0 * np.pi * doy / 365.25
    x = np.column_stack(
        [
            np.asarray(pack.mrms_in, dtype=float),
            np.asarray(pack.mrms_nbhd_in, dtype=float),
            np.asarray(pack.lat, dtype=float),
            np.asarray(pack.lon, dtype=float),
            np.sin(ang),
            np.cos(ang),
            np.asarray(pack.range_km, dtype=float),
        ]
    )
    if x.shape[1] != len(FEATURE_NAMES):
        raise RuntimeError("feature width drifted")
    return x


def label_y(pack: RainPack) -> np.ndarray:
    return np.asarray(pack.gauge_in, dtype=float)
