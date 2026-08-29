# Copyright (c) 2026 Martial Systems LLC

from pathlib import Path

import pytest

from inrain.errors import FetchError
from inrain.fetch import fetch_live
from inrain.mrms import assert_radar_only_url, mrms_url
from datetime import date


def test_radar_only_url() -> None:
    assert_radar_only_url(mrms_url(date(2024, 8, 15)))
    with pytest.raises(FetchError, match="not RadarOnly"):
        assert_radar_only_url(
            "https://example/CONUS/GaugeCorr_QPE_24H_00.00/20240815/x.grib2.gz"
        )
    with pytest.raises(FetchError, match="not RadarOnly"):
        assert_radar_only_url(
            "https://example/CONUS/MultiSensor_QPE_24H_Pass2_00.00/20240815/x.grib2.gz"
        )


def test_empty_cocorahs_stops(tmp_path: Path) -> None:
    def getter(url: str) -> bytes:
        if "cocorahs" in url:
            return b"ObservationDate,ObservationTime,StationNumber,Latitude,Longitude,TotalPrecipAmt\n"
        raise FetchError("no MRMS in this test")

    with pytest.raises(FetchError, match="empty"):
        fetch_live(cache_dir=tmp_path, getter=getter)
