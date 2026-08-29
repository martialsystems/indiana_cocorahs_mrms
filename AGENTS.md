# Agent notes: indiana_cocorahs_mrms

Public GitHub. MIT. Question: Does RadarOnly MRMS match CoCoRaHS daily rain at held-out Indiana stations?

Live answer: RadarOnly RMSE 0.133 in on 177 held-out stations. Ridge 0.124 (MAE 0.049 vs 0.048). HGB 0.141. IDW 0.209. Fixture HGB does not rescue live. Do not re-fit to chase that table.

This is a new tree. Do not restamp https://github.com/martialsystems/white_river_rain_stage. That repo forbids hourly MRMS as v1 and forbids starting the next rain tree from its snapshot.

Spatial block holdout is the split. Random row splits are banned. Train stations never appear in test. RadarOnly is the independent QPE. GaugeCorr and MultiSensor Pass2 are refused as "independent." Fetch-or-stop: empty CoCoRaHS or 404 MRMS stops. Do not substitute PRISM, Daymet, or Stage IV.

This tree does not read `p_sfha`. Do not edit indiana_flood_completion, Nora HAND, FIM, or rain-stage. Do not paint a wet mask. Two figures max. Fixture skill does not rescue live. Bias map is residual, not water.

`qpeforge/` is the GraphForge pin: no `p_sfha`, spatial holdout, RadarOnly fetch-or-stop, claim bans.

Do not start hourly 7am local-tz sums, Central-county clocks, or GaugeCorr as v1.

## Verify

`python3 ~/agent_laws_verify_before_done/vbd_gate.py check --app-root . --claim-done`

`vbd.runtime.json` runs `.venv/bin/python -m pytest`, `scripts/run_fixture.py`, and `qpeforge/scripts/sanity_qpeforge.py`. Do not use stock `/usr/bin/python3 -m pytest`: it has no rasterio.
