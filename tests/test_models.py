# Copyright (c) 2026 Martial Systems LLC

import numpy as np

from inrain.config import FEATURE_NAMES
from inrain.features import matrix_x
from inrain.fixture import build_fixture
from inrain.models import fit_pack
from inrain.split import TRAIN_END64, august_2026_mask, row_masks


def test_fixture_hgb_recovers_planted_bias() -> None:
    pack = build_fixture()
    train, hold = row_masks(pack)
    assert not np.any(train & august_2026_mask(pack.dates))
    assert pack.dates[train].max() <= TRAIN_END64
    fit = fit_pack(pack)
    assert fit["n_train"] > 200
    assert fit["n_holdout"] > 200
    assert fit["n_holdout_stations"] >= 4
    assert fit["august_2026_in_train"] is False
    assert fit["random_split"] is False
    assert fit["station_leak"] is False
    assert fit["gauge_as_feature"] is False
    ident = fit["skill"]["identity"]["rmse_in"]
    hgb = fit["skill"]["hgb"]["rmse_in"]
    ridge = fit["skill"]["ridge"]["rmse_in"]
    idw = fit["skill"]["idw"]
    assert hgb < ident * 0.85
    assert ridge < ident
    assert idw["n"] > 200
    assert np.isfinite(idw["rmse_in"])
    assert fit["skill"]["hgb"]["name"] == "HGB"
    x = matrix_x(pack)
    assert x.shape[1] == len(FEATURE_NAMES)
    assert "gauge" not in FEATURE_NAMES
    assert "p_sfha" not in FEATURE_NAMES
    assert np.isfinite(x[train]).all()
    # Identity should be wet-biased on the planted east overestimate.
    assert fit["skill"]["identity"]["bias_in"] > 0.02
