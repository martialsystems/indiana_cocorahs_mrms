# Copyright (c) 2026 Martial Systems LLC

import numpy as np
import pytest

from inrain.cocorahs import parse_csv, parse_precip
from inrain.errors import FetchError
from inrain.pair import assemble, eligible_stations


def test_trace_and_na() -> None:
    assert parse_precip("T") == 0.0
    assert parse_precip("t") == 0.0
    assert parse_precip("NA") is None
    assert parse_precip("0.25") == 0.25


def test_parse_csv_hour_and_bbox() -> None:
    text = (
        "ObservationDate,ObservationTime,StationNumber,Latitude,Longitude,TotalPrecipAmt\n"
        "2024-08-01, 07:00 AM, IN-MD-1, 39.8, -86.1, 0.40\n"
        "2024-08-01, 04:00 AM, IN-MD-2, 39.8, -86.1, 0.10\n"
        "2024-08-01, 07:00 AM, IL-CK-1, 39.8, -86.1, 0.50\n"
        "2024-08-01, 07:00 AM, IN-MD-3, 39.8, -86.1, T\n"
        "2024-08-01, 07:00 AM, IN-MD-4, 39.8, -86.1, NA\n"
    )
    rows = parse_csv(text)
    sids = {r["station_id"] for r in rows}
    assert sids == {"IN-MD-1", "IN-MD-3"}
    by = {r["station_id"]: r["gauge_in"] for r in rows}
    assert by["IN-MD-1"] == 0.40
    assert by["IN-MD-3"] == 0.0


def test_eligible_stations_and_empty() -> None:
    sid = np.array(["A"] * 40 + ["B"] * 5, dtype=object)
    assert eligible_stations(sid, n_min=30) == {"A"}
    with pytest.raises(FetchError, match="enough paired"):
        assemble(
            dates=np.array(["2024-07-01"] * 5, dtype="datetime64[D]"),
            station_id=np.array(["IN-FX-1"] * 5, dtype=object),
            lat=np.full(5, 39.8),
            lon=np.full(5, -86.1),
            gauge_in=np.ones(5),
            mrms_in=np.ones(5),
            mrms_nbhd_in=np.ones(5),
            source="t",
        )
