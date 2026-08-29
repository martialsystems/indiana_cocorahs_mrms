# Copyright (c) 2026 Martial Systems LLC

from pathlib import Path

from inrain.config import QUESTION
from inrain.errors import FigureCapError
from inrain.figure import _cap
from inrain.pipeline import stage0_fixture


def test_fixture_two_figures(tmp_path: Path) -> None:
    report = stage0_fixture(tmp_path)
    assert report["question"] == QUESTION
    assert report["p_sfha_feature"] is False
    assert report["p_sfha_label"] is False
    assert report["august_2026_in_train"] is False
    assert report["product"] == "RadarOnly_QPE_24H"
    assert (tmp_path / "scatter.png").is_file()
    assert (tmp_path / "bias_map.png").is_file()
    assert report["figures"] == ["scatter.png", "bias_map.png"]
    assert report["units"] == "inches"
    assert (tmp_path / "stage0_report.json").is_file()
    assert report["skill"]["hgb"]["rmse_in"] < report["skill"]["identity"]["rmse_in"]


def test_third_figure_refused() -> None:
    try:
        _cap(3)
        raise AssertionError("cap allowed 3")
    except FigureCapError:
        pass
