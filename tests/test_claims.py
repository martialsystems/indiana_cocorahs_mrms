# Copyright (c) 2026 Martial Systems LLC

from inrain.claims import scan_text
from inrain.config import LIVE_BIAS_SUBTITLE, QUESTION


def test_question_and_bans() -> None:
    assert scan_text(QUESTION) == []
    assert scan_text(LIVE_BIAS_SUBTITLE) == []
    assert "flood_ai" in scan_text("we built flood AI")
    assert "bias_wet" in scan_text("bias map is a wet mask")
    assert "bias_water" in scan_text("bias layer is water")
    assert "gaugecorr_indep" in scan_text("GaugeCorr is independent")
    assert "fixture_rescues" in scan_text("fixture skill rescues live")
    assert "flood_warning" in scan_text("this is a flood warning")
    assert "p_sfha_feat" in scan_text("p_sfha as a feature")
