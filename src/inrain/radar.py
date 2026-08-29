# Copyright (c) 2026 Martial Systems LLC
"""Range to the nearest WSR-88D used for Indiana."""

from __future__ import annotations

import numpy as np

from inrain.config import RADARS

_R_KM = 6371.0


def haversine_km(lat1: np.ndarray, lon1: np.ndarray, lat2: float, lon2: float) -> np.ndarray:
    p1 = np.radians(np.asarray(lat1, dtype=float))
    p2 = np.radians(float(lat2))
    dphi = np.radians(float(lat2) - np.asarray(lat1, dtype=float))
    dl = np.radians(float(lon2) - np.asarray(lon1, dtype=float))
    a = np.sin(dphi / 2.0) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2.0) ** 2
    return 2.0 * _R_KM * np.arcsin(np.sqrt(np.clip(a, 0.0, 1.0)))


def nearest_radar_km(lat: np.ndarray, lon: np.ndarray) -> np.ndarray:
    lat = np.asarray(lat, dtype=float)
    lon = np.asarray(lon, dtype=float)
    best = np.full(lat.shape, np.inf, dtype=float)
    for _name, rlat, rlon in RADARS:
        d = haversine_km(lat, lon, rlat, rlon)
        best = np.minimum(best, d)
    return best
