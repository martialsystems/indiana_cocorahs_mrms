# Methodology: CoCoRaHS vs RadarOnly MRMS in Indiana

Question: Does RadarOnly MRMS match CoCoRaHS daily rain at held-out Indiana stations?

GaugeCorr and MultiSensor Pass2 ingest gauges. CoCoRaHS is in that stream. RadarOnly is the independent field. An ML correction trained on some stations is scored only at stations those models never saw.

## Layers

| Layer | Role | Source |
|-------|------|--------|
| Label | Daily rain at volunteer gauges, inches | CoCoRaHS Daily export, `IN-*`. Trace is 0.00. NA dropped. Multi-day reports are not in this export. Observation time 5:00 to 9:00 local. |
| QPE | 24 h radar-only accumulation ending 12Z, sampled at the gauge, stored as inches | NOAA PDS `RadarOnly_QPE_24H`. Native mm. 404 or empty stops. |
| Neighborhood | 3x3 mean of the same RadarOnly field | texture, not a gauge |
| Range | km to nearest of KIND, KIWX, KVWX, KILN, KLOT, KLVX | beam-height proxy |
| Domain | Indiana bbox | not HUC-8 05120201, not the Nora HAND window |

Day match: CoCoRaHS date D vs MRMS 24 h ending 12Z on D (7am EST). EDT is a 1-hour mismatch. Twelve southwest and five northwest Indiana counties are Central. Documented here. Hourly local-tz sums are a next tree.

## Split

Eligible station: at least 30 paired days in the locked windows. Tile stations into 0.5° blocks. Every fourth block, in sorted-key order, is holdout. Every station in a holdout block is test-only.

Train rows: train-block stations and dates through 2024-09-30. Holdout rows: holdout-block stations and dates from 2024-10-01. August 2026 is not in train. Random row splits are refused. A station id in both masks is refused. CoCoRaHS is the label, never a feature.

Live windows: 2024-07-01 to 2024-09-30 (train-eligible), 2025-07-01 to 2025-09-30 and 2026-07-01 to 2026-08-20 (holdout-eligible).

## Models

Features: RadarOnly cell, 3x3 mean, lat, lon, day-of-year sine and cosine, range to nearest radar.

| Model | Role |
|-------|------|
| Identity | raw RadarOnly |
| IDW | k=8, power 2, same-day train-block CoCoRaHS (including holdout-period days at those stations) |
| Ridge | scaled linear |
| HGB | `HistGradientBoostingRegressor`, the ML |

Metrics on held-out stations, inches: RMSE, MAE, mean bias (predictor minus gauge), wet-day CSI at 0.10 in. Yesterday's gauge is the wrong bar (this is not a stage nowcast).

Live holdout: 177 stations, 19189 rows. RadarOnly RMSE 0.133, MAE 0.048, bias +0.013, CSI 0.82. Ridge 0.124 / 0.049 / +0.001 / 0.83. HGB 0.141 / 0.048 / -0.004 / 0.84. IDW 0.209 / 0.076 / +0.001 / 0.72. Ridge trims bias. HGB does not beat RadarOnly RMSE. Fixture HGB 0.039 vs 0.089 does not replace this table.

## Figures

1. Holdout scatter: CoCoRaHS vs RadarOnly and vs HGB. Caption is the RMSE ranking.
2. Bias map: mean (RadarOnly minus CoCoRaHS) at held-out stations only. Residual, not water.

## Claims

Allowed: Indiana daily rain verification; RadarOnly vs CoCoRaHS; held-out station skill; ML bias correction; bias map as residual.

Banned: 100-year exceedance; p_sfha in the feature matrix or as a forecast; bias map as a FIRM, a wet mask, or water; calling GaugeCorr independent; treating fixture RMSE as live skill; flood warning; climate; a third figure.

## Next tree, if any

Hourly 7am local-tz sums, Central vs Eastern county clocks, or GaugeCorr as an operational (leaky) product. Not from this snapshot.
