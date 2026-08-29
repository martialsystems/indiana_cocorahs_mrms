# Copyright (c) 2026 Martial Systems LLC
"""RadarOnly 24H at 12Z. GaugeCorr and MultiSensor are refused."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import numpy as np
import rasterio
from rasterio.windows import from_bounds

from inrain.config import (
    IN_LAT,
    IN_LON,
    MM_PER_INCH,
    MRMS_URL,
    MRMS_ZERO_MM,
    PRODUCT,
    REFUSED_PRODUCTS,
)
from inrain.errors import FetchError
from inrain.http import get_bytes

_PAD_DEG = 0.03


def mrms_url(day: date) -> str:
    stamp = day.strftime("%Y%m%d")
    return MRMS_URL.format(stamp=stamp)


def assert_radar_only_url(url: str) -> None:
    if "GaugeCorr" in url or "MultiSensor" in url:
        raise FetchError("URL is not RadarOnly")
    if PRODUCT not in url:
        raise FetchError("URL is not RadarOnly_QPE_24H")


def _element_ok(tags: dict[str, str]) -> None:
    elem = str(tags.get("GRIB_ELEMENT") or "")
    for token in REFUSED_PRODUCTS:
        if token in elem:
            raise FetchError(f"GRIB is {elem}, not {PRODUCT}")
    if "RadarOnly" not in elem:
        raise FetchError(f"GRIB is {elem or 'unknown'}, not {PRODUCT}")


def cache_day(day: date, dest_dir: Path, *, getter=get_bytes) -> Path:
    assert_radar_only_url(mrms_url(day))
    dest_dir.mkdir(parents=True, exist_ok=True)
    path = dest_dir / f"{day.strftime('%Y%m%d')}.grib2.gz"
    if path.is_file() and path.stat().st_size > 0:
        return path
    body = getter(mrms_url(day))
    if not body:
        raise FetchError(f"empty MRMS {day.isoformat()}")
    path.write_bytes(body)
    return path


def sample_stations(
    path: Path,
    lat: np.ndarray,
    lon: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Inches at the cell and 3x3 mean. path is a .grib2 or .grib2.gz."""
    lat = np.asarray(lat, dtype=float)
    lon = np.asarray(lon, dtype=float)
    src = str(path)
    if src.endswith(".gz"):
        src = f"/vsigzip/{path.resolve()}"
    with rasterio.open(src) as ds:
        _element_ok(ds.tags(1) if ds.count else {})
        west, south, east, north = IN_LON[0] - _PAD_DEG, IN_LAT[0] - _PAD_DEG, IN_LON[1] + _PAD_DEG, IN_LAT[1] + _PAD_DEG
        win = from_bounds(west, south, east, north, ds.transform)
        grid = ds.read(1, window=win)
        transform = ds.window_transform(win)
    grid = np.asarray(grid, dtype=float)
    grid = np.where(grid < MRMS_ZERO_MM, 0.0, grid)
    inv = ~transform
    rows = np.empty(lat.shape, dtype=int)
    cols = np.empty(lon.shape, dtype=int)
    for i in range(lat.size):
        c, r = inv * (float(lon[i]), float(lat[i]))
        rows[i] = int(np.floor(r))
        cols[i] = int(np.floor(c))
    h, w = grid.shape
    cell = np.full(lat.shape, np.nan, dtype=float)
    nbhd = np.full(lat.shape, np.nan, dtype=float)
    for i in range(lat.size):
        r, c = int(rows[i]), int(cols[i])
        if r < 0 or c < 0 or r >= h or c >= w:
            continue
        cell[i] = grid[r, c]
        r0, r1 = max(0, r - 1), min(h, r + 2)
        c0, c1 = max(0, c - 1), min(w, c + 2)
        nbhd[i] = float(np.nanmean(grid[r0:r1, c0:c1]))
    return cell / MM_PER_INCH, nbhd / MM_PER_INCH
