# Copyright (c) 2026 Martial Systems LLC
"""Synthetic Indiana stations and a planted east radar bias. No HTTP."""

from __future__ import annotations

from datetime import date

import numpy as np

from inrain.config import IN_LAT, IN_LON, LIVE_WINDOWS, PRODUCT
from inrain.pack import RainPack
from inrain.pair import assemble, days_in_windows
from inrain.radar import nearest_radar_km


def _grid_stations(n_lat: int = 6, n_lon: int = 8) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    lats = np.linspace(IN_LAT[0] + 0.25, IN_LAT[1] - 0.25, n_lat)
    lons = np.linspace(IN_LON[0] + 0.25, IN_LON[1] - 0.25, n_lon)
    yy, xx = np.meshgrid(lats, lons, indexing="ij")
    lat = yy.reshape(-1)
    lon = xx.reshape(-1)
    ids = np.array([f"IN-FX-{i+1:02d}" for i in range(lat.size)], dtype=object)
    return ids, lat, lon


def build_fixture(*, seed: int = 7) -> RainPack:
    """True rain plus east-multiplicative RadarOnly bias. Local storms on some sites."""
    rng = np.random.default_rng(seed)
    days = days_in_windows(LIVE_WINDOWS)
    dates_u = np.array([np.datetime64(d.isoformat()) for d in days])
    ids, slat, slon = _grid_stations()
    n_st = ids.size
    n_d = dates_u.size
    lon_min, lon_max = float(slon.min()), float(slon.max())
    east = (slon - lon_min) / max(lon_max - lon_min, 1e-6)

    y = dates_u.astype("datetime64[Y]")
    doy = (dates_u - y).astype("timedelta64[D]").astype(int) + 1
    seasonal = 0.08 + 0.10 * np.sin(2.0 * np.pi * (doy - 80) / 365.25)
    true = rng.gamma(0.35, 0.22, size=(n_d, n_st)) * (0.4 + seasonal)[:, None]
    bursts = rng.random((n_d, n_st)) < 0.07
    true = true + bursts * rng.gamma(1.6, 0.35, size=(n_d, n_st))

    # Localized storms, some centered on eastern (often holdout) stations.
    for _ in range(18):
        di = int(rng.integers(0, n_d))
        si = int(rng.integers(0, n_st))
        dist2 = (slat - slat[si]) ** 2 + (slon - slon[si]) ** 2
        true[di] = true[di] + float(rng.uniform(0.8, 2.2)) * np.exp(-dist2 / (0.18**2))

    true = np.clip(true, 0.0, None)
    gauge = np.clip(true + rng.normal(0.0, 0.02, size=true.shape), 0.0, None)
    mrms = true * (1.0 + 0.70 * east)[None, :] + rng.normal(0.0, 0.03, size=true.shape)
    mrms = np.clip(mrms, 0.0, None)
    nbhd = mrms.copy()
    for j in range(n_st):
        dist2 = (slat - slat[j]) ** 2 + (slon - slon[j]) ** 2
        w = np.exp(-dist2 / (0.35**2))
        nbhd[:, j] = (mrms * w).sum(axis=1) / w.sum()

    dates = np.repeat(dates_u, n_st)
    station_id = np.tile(ids, n_d)
    lat = np.tile(slat, n_d)
    lon = np.tile(slon, n_d)
    pack = assemble(
        dates=dates,
        station_id=station_id,
        lat=lat,
        lon=lon,
        gauge_in=gauge.reshape(-1),
        mrms_in=mrms.reshape(-1),
        mrms_nbhd_in=nbhd.reshape(-1),
        source="fixture",
        extra={"planted_east_bias": 0.70, "n_days": n_d, "product": PRODUCT},
    )
    pack.range_km = nearest_radar_km(pack.lat, pack.lon)
    pack.product = PRODUCT
    return pack


def fixture_windows() -> tuple[tuple[date, date], ...]:
    return LIVE_WINDOWS
