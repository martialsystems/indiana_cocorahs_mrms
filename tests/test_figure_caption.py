# Copyright (c) 2026 Martial Systems LLC

from inrain.config import LIVE_BIAS_SUBTITLE, LOCKED_LIVE_COMMIT
from inrain.figure import scatter_subtitle


def test_live_captions_name_radar_and_clock() -> None:
    fit = {
        "skill": {
            "identity": {"rmse_in": 0.13306947137742373},
            "hgb": {"rmse_in": 0.14050355160274344},
        }
    }
    sub = scatter_subtitle(fit, live=True)
    assert sub.startswith("RadarOnly 0.133")
    assert "HGB 0.141" in sub
    assert "Ridge" not in sub
    assert "12Z 24h vs 7am local" in sub
    assert "volunteer QC" in sub
    assert "12Z 24h vs 7am local" in LIVE_BIAS_SUBTITLE
    assert "volunteer QC" in LIVE_BIAS_SUBTITLE
    assert LOCKED_LIVE_COMMIT.startswith("ac36f0f")
    first, sep, rest = sub.partition(". ")
    assert sep
    assert "0.133" in first
    assert "12Z" in rest
