# Indiana CoCoRaHS vs RadarOnly MRMS

Does RadarOnly MRMS match CoCoRaHS daily rain at held-out Indiana stations?

On this sample, RadarOnly is already close. Held-out RMSE is 0.133 in. Ridge is 0.124 and takes mean bias from +0.013 to +0.001. HGB is 0.141 RMSE. IDW of other CoCoRaHS is 0.209. MAE is 0.048 in for RadarOnly and for HGB; Ridge is 0.049. CSI at 0.10 in is 0.82 (radar), 0.83 (Ridge), 0.84 (HGB). Fixture HGB beating identity does not rescue live skill.

Live science is `logs/in_live/stage_c_report.json`. 685 eligible Indiana stations, 409 train-block, 177 held-out. Train n=30717 through 2024-09-30. Holdout n=19189 from 2024-10-01. RadarOnly 24H at 12Z. This tree does not read `p_sfha`.

Sibling rain-to-stage (Stage IV, Nora): https://github.com/martialsystems/white_river_rain_stage

![Figure 1. Holdout scatter](logs/in_live/scatter.png)

Figure 1. Live holdout: CoCoRaHS versus raw RadarOnly and versus HGB. Ranking is RMSE on 177 held-out stations.

![Figure 2. Bias map](logs/in_live/bias_map.png)

Figure 2. Mean RadarOnly minus CoCoRaHS at held-out stations. Residual, not water. Train stations omitted.

## Live skill (held-out stations)

Locked from `logs/in_live/stage_c_report.json`. Inches. Summers 2024 train, 2025 and 2026 holdout. Identity is raw RadarOnly. IDW uses same-day train-block CoCoRaHS. HGB is the ML.

| Model | RMSE (in) | MAE (in) | Bias (in) | CSI 0.10 in |
|-------|----------:|---------:|----------:|------------:|
| RadarOnly | 0.133 | 0.048 | +0.013 | 0.82 |
| IDW | 0.209 | 0.076 | +0.001 | 0.72 |
| Ridge | 0.124 | 0.049 | +0.001 | 0.83 |
| HGB | 0.141 | 0.048 | -0.004 | 0.84 |

Ridge trims the wet bias. HGB does not beat RadarOnly RMSE at stations it never trained on. IDW of neighboring gauges is worse than radar.

## Why RadarOnly

CoCoRaHS daily reports are the labels. MRMS GaugeCorr and MultiSensor Pass2 ingest gauges. Scoring those products at CoCoRaHS sites is leakage. RadarOnly is independent of the labels. The ML may use RadarOnly, location, season, and range to nearest WSR-88D. It may not use the gauge as a feature.

## Split

0.5° blocks. Every fourth block is holdout. Train stations never test. Dates: train through 2024-09-30, holdout from 2024-10-01. August 2026 is not in train.

## Day match

CoCoRaHS date D versus RadarOnly 24H ending 12Z on D (7am EST). EDT is a 1-hour mismatch. Central-time Indiana counties are a further mismatch. Volunteer QC is the remaining residual risk.

## Stage 0

Synthetic stations and a planted east-multiplicative radar bias so CI trains without NOAA. Fixture HGB RMSE 0.039 vs RadarOnly 0.089 on 1716 holdout rows. That shows the pipeline can recover a planted bias. It is not live skill.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src:. python3 scripts/run_fixture.py logs/stage0_fixture
.venv/bin/python -m pytest tests -q
PYTHONPATH=src:. python3 scripts/run_live.py logs/in_live data/raw/mrms
```

Do not use stock `/usr/bin/python3 -m pytest`: it has no rasterio. HTTP 404 or an empty CoCoRaHS export stops (`run_live.py` exit 2). PRISM, Daymet, and Stage IV are not substitutes. Two figures max, then this tree can stop.

| File | Role |
|------|------|
| [METHODOLOGY.md](METHODOLOGY.md) | Locked contract |
| [AGENTS.md](AGENTS.md) | Agent rules |
| [CHECKLIST.md](CHECKLIST.md) | Operator list |
| `src/inrain/` | CoCoRaHS, RadarOnly clip, spatial split, identity/IDW/Ridge/HGB, figures, claims |
| `qpeforge/` | GraphForge pin: no `p_sfha`, spatial holdout, RadarOnly fetch-or-stop, claim bans |
