# Operator checklist

1. Fixture Stage 0 green: CI oracle only. Does not rescue live skill.
2. Science lock `ac36f0f`. Live table: RadarOnly 0.133 RMSE, HGB 0.141, IDW 0.209. Ridge 0.124 then MAE +0.001 in is noise. Do not chase 0.009 in RMSE. Do not re-fit.
3. Live `run_live.py` exit 2 on empty CoCoRaHS or 404 RadarOnly.
4. Skill table is held-out stations only. RadarOnly is the field. HGB is the ML that lost on amount.
5. Figure captions: 12Z 24h vs 7am local; volunteer QC. Residual, not water.
6. At most two figures. Product figures are `logs/in_live/`.
7. GaugeCorr stays out. Rain-stage stays frozen.
8. Next is hours, lake-effect, or 7am split as a new tree, or stop.
9. Push public `martialsystems/indiana_cocorahs_mrms`. Precip gist, not gist 1, not a fourth White River nowcast.
