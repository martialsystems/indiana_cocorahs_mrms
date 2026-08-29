# Operator checklist

1. Fixture Stage 0 green: CI oracle only. Does not rescue live skill.
2. Live table is `logs/in_live/stage_c_report.json`: RadarOnly 0.133 RMSE, Ridge 0.124, HGB 0.141, IDW 0.209. Do not re-fit to chase that table.
3. Live `run_live.py` exit 2 on empty CoCoRaHS or 404 RadarOnly.
4. Skill table is held-out stations only. Identity (RadarOnly) and IDW are the bars. HGB is the ML.
5. Figure 2 caption: residual at held-out stations, not water. Train stations omitted.
6. At most two figures. Product figures are `logs/in_live/`.
7. Do not call GaugeCorr independent. Do not start hourly local-tz matching from this snapshot.
8. Push public `martialsystems/indiana_cocorahs_mrms`.
