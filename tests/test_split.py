# Copyright (c) 2026 Martial Systems LLC

import numpy as np
import pytest

from inrain.errors import SplitError
from inrain.fixture import build_fixture
from inrain.split import assert_split, row_masks, station_holdout_ids


def test_fixture_no_station_leak() -> None:
    pack = build_fixture()
    train, hold = row_masks(pack)
    assert_split(pack, train, hold)
    train_ids = set(pack.station_id[train].astype(str))
    hold_ids = set(pack.station_id[hold].astype(str))
    assert train_ids.isdisjoint(hold_ids)
    assert station_holdout_ids(pack) == hold_ids
    assert train.any() and hold.any()


def test_station_leak_refused() -> None:
    pack = build_fixture()
    train, hold = row_masks(pack)
    hold[np.where(train)[0][0]] = True
    with pytest.raises(SplitError, match="overlap"):
        assert_split(pack, train, hold)


def test_same_station_both_sides_refused() -> None:
    pack = build_fixture()
    n = pack.n_obs
    train = np.zeros(n, dtype=bool)
    hold = np.zeros(n, dtype=bool)
    train[0] = True
    hold[-1] = True
    pack.station_id[0] = pack.station_id[-1]
    pack.dates[0] = np.datetime64("2024-09-01")
    pack.dates[-1] = np.datetime64("2025-07-01")
    with pytest.raises(SplitError, match="station leak"):
        assert_split(pack, train, hold)


def test_august_2026_in_train_refused() -> None:
    pack = build_fixture()
    n = pack.n_obs
    train = np.zeros(n, dtype=bool)
    hold = np.zeros(n, dtype=bool)
    train[0] = True
    hold[-1] = True
    pack.dates[0] = np.datetime64("2026-08-15")
    pack.dates[-1] = np.datetime64("2026-08-16")
    pack.station_id[0] = "IN-FX-99"
    pack.station_id[-1] = "IN-FX-98"
    with pytest.raises(SplitError, match="August 2026"):
        assert_split(pack, train, hold)
