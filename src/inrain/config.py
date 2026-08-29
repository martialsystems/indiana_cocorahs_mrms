# Copyright (c) 2026 Martial Systems LLC
"""Locked Indiana CoCoRaHS vs RadarOnly MRMS contract. Does not read p_sfha."""

from __future__ import annotations

from datetime import date

QUESTION = "Does RadarOnly MRMS match CoCoRaHS daily rain at held-out Indiana stations?"
USER_AGENT = "MartialSystemsResearch/indiana_cocorahs_mrms"
MAX_FIGURES = 2
WY2024_END = date(2024, 9, 30)
HOLDOUT_START = date(2024, 10, 1)
IN_LAT = (37.77, 41.76)
IN_LON = (-88.10, -84.78)
BLOCK_DEG = 0.5
HOLDOUT_BLOCK_STRIDE = 4
HOLDOUT_BLOCK_OFFSET = 0
MIN_STATION_DAYS = 30
MIN_LIVE_DAYS = 30
OBS_HOUR_MIN = 5.0
OBS_HOUR_MAX = 9.0
WET_DAY_IN = 0.10
MM_PER_INCH = 25.4
MRMS_ZERO_MM = 0.01
IDW_K = 8
IDW_POWER = 2.0
PRODUCT = "RadarOnly_QPE_24H"
REFUSED_PRODUCTS = ("GaugeCorr", "MultiSensor")
LIVE_WINDOWS = (
    (date(2024, 7, 1), date(2024, 9, 30)),
    (date(2025, 7, 1), date(2025, 9, 30)),
    (date(2026, 7, 1), date(2026, 8, 20)),
)
COCORAHS_EXPORT_URL = (
    "https://data.cocorahs.org/export/exportreports.aspx"
    "?ReportType=Daily&Format=CSV&State=IN"
    "&StartDate={start}&EndDate={end}&ReportDateType=reportdate"
)
MRMS_URL = (
    "https://noaa-mrms-pds.s3.amazonaws.com/CONUS/RadarOnly_QPE_24H_00.00/"
    "{stamp}/MRMS_RadarOnly_QPE_24H_00.00_{stamp}-120000.grib2.gz"
)
RADARS = (
    ("KIND", 39.7075, -86.2803),
    ("KIWX", 41.3586, -85.7000),
    ("KVWX", 38.2603, -87.7247),
    ("KILN", 39.4203, -83.8217),
    ("KLOT", 41.6044, -88.0847),
    ("KLVX", 37.9753, -85.9439),
)
# Simplified Indiana ring for the bias map. Residual, not a political boundary product.
INDIANA_RING = (
    (-87.53, 41.76),
    (-84.82, 41.76),
    (-84.78, 41.32),
    (-84.82, 39.17),
    (-84.90, 38.77),
    (-85.41, 38.12),
    (-86.04, 37.93),
    (-86.51, 37.77),
    (-87.61, 37.89),
    (-88.10, 37.84),
    (-88.10, 38.88),
    (-87.53, 39.17),
    (-87.53, 41.27),
    (-87.53, 41.76),
)
FEATURE_NAMES = (
    "mrms_in",
    "mrms_nbhd_in",
    "lat",
    "lon",
    "sin_doy",
    "cos_doy",
    "range_km",
)
LOCKED_LIVE_COMMIT = "ac36f0f7892a90ab38626406e5797387427a4b32"
LIVE_BIAS_SUBTITLE = (
    "Residual at held-out stations, not water. 12Z 24h vs 7am local; volunteer QC."
)
FIXTURE_BIAS_SUBTITLE = (
    "Fixture planted east bias. Does not rescue live skill."
)
HUC8_REFUSED = "05120201"
