# Copyright (c) 2026 Martial Systems LLC
"""Live CoCoRaHS + RadarOnly. 404/empty stops. No PRISM, Daymet, or Stage IV."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any, Callable

import numpy as np

from inrain.cocorahs import fetch_reports
from inrain.config import LIVE_WINDOWS, MIN_LIVE_DAYS, PRODUCT
from inrain.errors import FetchError
from inrain.http import get_bytes
from inrain.mrms import cache_day, sample_stations
from inrain.pack import RainPack
from inrain.pair import assemble, days_in_windows


def _concat_reports(windows: tuple[tuple[date, date], ...], getter) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for start, end in windows:
        rows.extend(fetch_reports(start=start, end=end, getter=getter))
    if not rows:
        raise FetchError("CoCoRaHS export empty after QC")
    return rows


def fetch_live(
    *,
    cache_dir: Path,
    windows: tuple[tuple[date, date], ...] = LIVE_WINDOWS,
    getter: Callable[[str], bytes] = get_bytes,
) -> tuple[RainPack, dict[str, Any]]:
    reports = _concat_reports(windows, getter)
    want_days = set(days_in_windows(windows))
    by_day: dict[date, list[dict[str, Any]]] = {}
    for rec in reports:
        d: date = rec["date"]
        if d not in want_days:
            continue
        by_day.setdefault(d, []).append(rec)
    if len(by_day) < MIN_LIVE_DAYS:
        raise FetchError(f"fewer than {MIN_LIVE_DAYS} CoCoRaHS days")

    dates: list[np.datetime64] = []
    sid: list[str] = []
    lat: list[float] = []
    lon: list[float] = []
    gauge: list[float] = []
    mrms: list[float] = []
    nbhd: list[float] = []
    used_days = 0
    for day in sorted(by_day):
        recs = by_day[day]
        slat = np.array([r["lat"] for r in recs], dtype=float)
        slon = np.array([r["lon"] for r in recs], dtype=float)
        path = cache_day(day, cache_dir, getter=getter)
        cell, neigh = sample_stations(path, slat, slon)
        ok = np.isfinite(cell) & np.isfinite(neigh)
        if not int(ok.sum()):
            raise FetchError(f"MRMS sample empty {day.isoformat()}")
        used_days += 1
        for i, rec in enumerate(recs):
            if not ok[i]:
                continue
            dates.append(np.datetime64(day.isoformat()))
            sid.append(rec["station_id"])
            lat.append(rec["lat"])
            lon.append(rec["lon"])
            gauge.append(rec["gauge_in"])
            mrms.append(float(cell[i]))
            nbhd.append(float(neigh[i]))

    if used_days < MIN_LIVE_DAYS:
        raise FetchError(f"fewer than {MIN_LIVE_DAYS} paired MRMS days")
    pack = assemble(
        dates=np.array(dates, dtype="datetime64[D]"),
        station_id=np.array(sid, dtype=object),
        lat=np.array(lat, dtype=float),
        lon=np.array(lon, dtype=float),
        gauge_in=np.array(gauge, dtype=float),
        mrms_in=np.array(mrms, dtype=float),
        mrms_nbhd_in=np.array(nbhd, dtype=float),
        source="live",
        extra={"n_mrms_days": used_days, "n_cocorahs_rows": len(reports)},
    )
    pack.product = PRODUCT
    meta = {
        "n_mrms_days": used_days,
        "n_cocorahs_rows": len(reports),
        "product": PRODUCT,
        "cache_dir": str(cache_dir),
    }
    return pack, meta
