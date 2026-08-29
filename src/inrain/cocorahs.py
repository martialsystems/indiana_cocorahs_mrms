# Copyright (c) 2026 Martial Systems LLC
"""CoCoRaHS Indiana daily reports. Daily only. Trace is 0.00. NA dropped."""

from __future__ import annotations

import csv
import io
from datetime import date, datetime
from typing import Any

import numpy as np

from inrain.config import (
    COCORAHS_EXPORT_URL,
    IN_LAT,
    IN_LON,
    OBS_HOUR_MAX,
    OBS_HOUR_MIN,
)
from inrain.errors import FetchError
from inrain.http import get_bytes


def _hour(text: str) -> float | None:
    raw = (text or "").strip()
    if not raw:
        return None
    for fmt in ("%I:%M %p", "%H:%M"):
        try:
            t = datetime.strptime(raw, fmt)
            return t.hour + t.minute / 60.0
        except ValueError:
            continue
    return None


def parse_precip(text: str) -> float | None:
    raw = (text or "").strip()
    if not raw or raw.upper() == "NA":
        return None
    if raw.upper() == "T":
        return 0.0
    try:
        return float(raw)
    except ValueError:
        return None


def parse_csv(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    reader = csv.DictReader(io.StringIO(text))
    for rec in reader:
        sid = (rec.get("StationNumber") or "").strip()
        if not sid.startswith("IN-"):
            continue
        precip = parse_precip(rec.get("TotalPrecipAmt") or "")
        if precip is None:
            continue
        hour = _hour(rec.get("ObservationTime") or "")
        if hour is None or hour < OBS_HOUR_MIN or hour > OBS_HOUR_MAX:
            continue
        try:
            lat = float(rec.get("Latitude") or "nan")
            lon = float(rec.get("Longitude") or "nan")
            day = date.fromisoformat((rec.get("ObservationDate") or "").strip())
        except ValueError:
            continue
        if not (IN_LAT[0] <= lat <= IN_LAT[1] and IN_LON[0] <= lon <= IN_LON[1]):
            continue
        if precip < 0.0:
            continue
        rows.append(
            {
                "station_id": sid,
                "lat": lat,
                "lon": lon,
                "date": day,
                "gauge_in": precip,
            }
        )
    return rows


def fetch_reports(
    *,
    start: date,
    end: date,
    getter=get_bytes,
) -> list[dict[str, Any]]:
    url = COCORAHS_EXPORT_URL.format(
        start=f"{start.month}/{start.day}/{start.year}",
        end=f"{end.month}/{end.day}/{end.year}",
    )
    raw = getter(url)
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise FetchError("CoCoRaHS export is not text") from exc
    if "StationNumber" not in text.splitlines()[0] if text.splitlines() else True:
        raise FetchError("CoCoRaHS export missing StationNumber")
    rows = parse_csv(text)
    if not rows:
        raise FetchError("CoCoRaHS export empty after QC")
    return rows


def to_arrays(rows: list[dict[str, Any]]) -> dict[str, np.ndarray]:
    n = len(rows)
    dates = np.empty(n, dtype="datetime64[D]")
    sid = np.empty(n, dtype=object)
    lat = np.empty(n, dtype=float)
    lon = np.empty(n, dtype=float)
    gauge = np.empty(n, dtype=float)
    for i, rec in enumerate(rows):
        dates[i] = np.datetime64(rec["date"].isoformat())
        sid[i] = rec["station_id"]
        lat[i] = rec["lat"]
        lon[i] = rec["lon"]
        gauge[i] = rec["gauge_in"]
    return {"dates": dates, "station_id": sid, "lat": lat, "lon": lon, "gauge_in": gauge}
