# Copyright (c) 2026 Martial Systems LLC
"""Same-day IDW of train-block CoCoRaHS. Radar-free bar. k nearest, power 2."""

from __future__ import annotations

import numpy as np

from inrain.config import IDW_K, IDW_POWER
from inrain.radar import haversine_km


def idw_predict(
    *,
    train_lat: np.ndarray,
    train_lon: np.ndarray,
    train_y: np.ndarray,
    train_day: np.ndarray,
    pred_lat: np.ndarray,
    pred_lon: np.ndarray,
    pred_day: np.ndarray,
    k: int = IDW_K,
    power: float = IDW_POWER,
) -> np.ndarray:
    """Predict at pred rows from same-calendar-day train gauges only."""
    train_lat = np.asarray(train_lat, dtype=float)
    train_lon = np.asarray(train_lon, dtype=float)
    train_y = np.asarray(train_y, dtype=float)
    train_day = np.asarray(train_day).astype("datetime64[D]")
    pred_lat = np.asarray(pred_lat, dtype=float)
    pred_lon = np.asarray(pred_lon, dtype=float)
    pred_day = np.asarray(pred_day).astype("datetime64[D]")
    out = np.full(pred_lat.shape[0], np.nan, dtype=float)
    if train_y.size == 0 or pred_lat.size == 0:
        return out
    days = np.unique(pred_day)
    for day in days:
        pi = np.where(pred_day == day)[0]
        ti = np.where(train_day == day)[0]
        if pi.size == 0 or ti.size == 0:
            continue
        tlat, tlon, ty = train_lat[ti], train_lon[ti], train_y[ti]
        n_use = min(int(k), int(ti.size))
        for idx in pi:
            dist = haversine_km(tlat, tlon, float(pred_lat[idx]), float(pred_lon[idx]))
            dist = np.where(dist < 1e-6, 1e-6, dist)
            order = np.argpartition(dist, n_use - 1)[:n_use]
            w = dist[order] ** (-float(power))
            sw = float(w.sum())
            if sw <= 0.0:
                continue
            out[idx] = float(np.dot(w, ty[order]) / sw)
    return out
