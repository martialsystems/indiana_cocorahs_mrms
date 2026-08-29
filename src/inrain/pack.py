# Copyright (c) 2026 Martial Systems LLC
"""Paired station-day rain: CoCoRaHS label, RadarOnly predictor."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from inrain.config import PRODUCT


@dataclass
class RainPack:
    """One row per station-day. Inches. RadarOnly only."""

    dates: np.ndarray
    station_id: np.ndarray
    lat: np.ndarray
    lon: np.ndarray
    gauge_in: np.ndarray
    mrms_in: np.ndarray
    mrms_nbhd_in: np.ndarray
    range_km: np.ndarray
    source: str = "fixture"
    product: str = PRODUCT
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def n_obs(self) -> int:
        return int(self.dates.shape[0])

    @property
    def n_stations(self) -> int:
        return int(np.unique(self.station_id).shape[0])
