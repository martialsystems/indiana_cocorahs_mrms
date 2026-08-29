# Copyright (c) 2026 Martial Systems LLC

import json
from pathlib import Path

from inrain.claims import scan_text
from inrain.config import QUESTION

REPO = Path(__file__).resolve().parents[1]


def test_readme_opens_with_the_question() -> None:
    text = (REPO / "README.md").read_text(encoding="utf-8")
    body = "\n".join(text.splitlines()[1:]).lstrip()
    assert body.startswith(QUESTION)
    assert "RadarOnly" in text
    assert "CoCoRaHS" in text
    assert "held-out" in text
    assert "p_sfha" in text
    assert "white_river_rain_stage" in text
    assert "does not rescue live skill" in text.lower()
    assert "GaugeCorr is independent" not in text
    assert scan_text(text) == []
    assert "—" not in text
    assert "What it is not" not in text
    assert "scatter.png" in text
    assert "bias_map.png" in text
    assert "a tree does not beat it on amount" in text
    assert "12Z 24h vs 7am local" in text
    assert "volunteer QC" in text
    assert "ac36f0f" in text
    assert "Do not chase 0.009" in text
    live = json.loads((REPO / "logs" / "in_live" / "stage_c_report.json").read_text(encoding="utf-8"))
    ident = live["skill"]["identity"]["rmse_in"]
    hgb = live["skill"]["hgb"]["rmse_in"]
    ridge = live["skill"]["ridge"]["rmse_in"]
    assert f"{ident:.3f}" in text
    assert f"{hgb:.3f}" in text
    assert f"{ridge:.3f}" in text
    assert str(live["n_holdout"]) in text
    assert str(live["n_holdout_stations"]) in text
    fixture = json.loads((REPO / "logs" / "stage0_fixture" / "stage0_report.json").read_text(encoding="utf-8"))
    assert f"{fixture['skill']['hgb']['rmse_in']:.3f}" in text
