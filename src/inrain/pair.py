# Copyright (c) 2026 Martial Systems LLC
"""Inner join CoCoRaHS station-days to RadarOnly samples. Eligible stations only."""

from __future__ import annotations

from collections import defaultdict
from datetime import date

import numpy as np

from inrain.config import MIN_STATION_DAYS
from inrain.errors import FetchError
from inrain.pack import RainPack
from inrain.radar import nearest_radar_km


def _station_xy(station_id: np.ndarray, lat: np.ndarray, lon: np.ndarray) -> dict[str, tuple[float, float]]:
    out: dict[str, tuple[float, float]] = {}
    for sid, y, x in zip(station_id.astype(str), lat, lon):
        out.setdefault(str(sid), (float(y), float(x)))
    return out


def eligible_stations(station_id: np.ndarray, n_min: int = MIN_STATION_DAYS) -> set[str]:
    counts: dict[str, int] = defaultdict(int)
    for sid in np.asarray(station_id).astype(str):
        counts[str(sid)] += 1
    return {sid for sid, n in counts.items() if n >= n_min}


def assemble(
    *,
    dates: np.ndarray,
    station_id: np.ndarray,
    lat: np.ndarray,
    lon: np.ndarray,
    gauge_in: np.ndarray,
    mrms_in: np.ndarray,
    mrms_nbhd_in: np.ndarray,
    source: str,
    extra: dict | None = None,
) -> RainPack:
    ok = (
        np.isfinite(gauge_in)
        & np.isfinite(mrms_in)
        & np.isfinite(mrms_nbhd_in)
        & np.isfinite(lat)
        & np.isfinite(lon)
    )
    dates = dates[ok]
    station_id = np.asarray(station_id)[ok]
    lat = lat[ok]
    lon = lon[ok]
    gauge_in = gauge_in[ok]
    mrms_in = mrms_in[ok]
    mrms_nbhd_in = mrms_nbhd_in[ok]
    keep = eligible_stations(station_id)
    if not keep:
        raise FetchError("no station has enough paired days")
    mask = np.isin(station_id.astype(str), list(keep))
    lat = lat[mask]
    lon = lon[mask]
    pack = RainPack(
        dates=dates[mask],
        station_id=station_id[mask],
        lat=lat,
        lon=lon,
        gauge_in=gauge_in[mask],
        mrms_in=mrms_in[mask],
        mrms_nbhd_in=mrms_nbhd_in[mask],
        range_km=nearest_radar_km(lat, lon),
        source=source,
        extra=dict(extra or {}),
    )
    pack.extra["n_eligible_stations"] = pack.n_stations
    return pack


def days_in_windows(windows: tuple[tuple[date, date], ...]) -> list[date]:
    out: list[date] = []
    for start, end in windows:
        d = start
        while d <= end:
            out.append(d)
            d = date.fromordinal(d.toordinal() + 1)
    return out
