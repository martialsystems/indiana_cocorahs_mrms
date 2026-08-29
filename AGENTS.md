# Agent notes: indiana_cocorahs_mrms

Public GitHub. MIT. Question: Does RadarOnly MRMS match CoCoRaHS daily rain at held-out Indiana stations?

Live answer at `ac36f0f`: MRMS RadarOnly is close; a tree does not beat it on amount. RMSE 0.133 in, CSI 0.82. HGB 0.141. IDW 0.209. Ridge 0.124 then MAE 0.049 vs 0.048 is noise, not a method. Do not chase 0.009 in RMSE. Do not re-fit. Fixture HGB does not rescue live.

This is a new tree. Do not restamp https://github.com/martialsystems/white_river_rain_stage. That repo forbids hourly MRMS as v1 and forbids starting the next rain tree from its snapshot.

Spatial block holdout is the split. Random row splits are banned. Train stations never appear in test. RadarOnly is the independent QPE. GaugeCorr and MultiSensor Pass2 are refused as "independent." Fetch-or-stop: empty CoCoRaHS or 404 MRMS stops. Do not substitute PRISM, Daymet, or Stage IV.

This tree does not read `p_sfha`. Do not edit indiana_flood_completion, Nora HAND, FIM, or rain-stage. Do not paint a wet mask. Two figures max. Fixture skill does not rescue live. Bias map is residual, not water.

`qpeforge/` is the GraphForge pin: no `p_sfha`, spatial holdout, RadarOnly fetch-or-stop, claim bans.

Next, if any: when radar misses (hours, lake-effect, 7am split), as a new tree, or stop. Not from `ac36f0f`. Not GaugeCorr.

## Verify

`python3 ~/agent_laws_verify_before_done/vbd_gate.py check --app-root . --claim-done`

`vbd.runtime.json` runs `.venv/bin/python -m pytest`, `scripts/run_fixture.py`, and `qpeforge/scripts/sanity_qpeforge.py`. Do not use stock `/usr/bin/python3 -m pytest`: it has no rasterio.
