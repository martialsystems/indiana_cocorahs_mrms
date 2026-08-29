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
# Cartographic sketch of Indiana (46 verts). Residual map only, not a legal boundary.
# Lake Michigan bite is in the northwest; Ohio River is the south.
INDIANA_RING = (
    (-85.9901, 41.7597),
    (-84.8070, 41.7597),
    (-84.8070, 41.6940),
    (-84.8016, 40.5000),
    (-84.8180, 39.1034),
    (-84.8947, 39.0596),
    (-84.8125, 38.7857),
    (-84.9878, 38.7803),
    (-85.1740, 38.6872),
    (-85.4314, 38.7310),
    (-85.4205, 38.5338),
    (-85.5902, 38.4517),
    (-85.6560, 38.3257),
    (-85.8312, 38.2764),
    (-85.9243, 38.0245),
    (-86.0394, 37.9587),
    (-86.2639, 38.0518),
    (-86.3022, 38.1669),
    (-86.5213, 38.0409),
    (-86.5049, 37.9313),
    (-86.7294, 37.8930),
    (-86.7952, 37.9916),
    (-87.0471, 37.8930),
    (-87.1293, 37.7889),
    (-87.3812, 37.9368),
    (-87.5127, 37.9040),
    (-87.6003, 37.9752),
    (-87.6824, 37.9040),
    (-87.9344, 37.8930),
    (-88.0275, 37.7999),
    (-88.0603, 37.8656),
    (-88.0001, 38.1011),
    (-87.9234, 38.1504),
    (-87.9508, 38.2764),
    (-87.8358, 38.2928),
    (-87.6551, 38.5064),
    (-87.6222, 38.6379),
    (-87.4962, 38.7803),
    (-87.5127, 38.9555),
    (-87.6386, 39.1691),
    (-87.5400, 39.3499),
    (-87.5400, 41.7104),
    (-87.4250, 41.6447),
    (-87.1183, 41.6447),
    (-86.8226, 41.7597),
    (-85.9901, 41.7597),
)
BIAS_MAP_PAD_DEG = 0.18
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
