# Copyright (c) 2026 Martial Systems LLC
"""Spatial block holdout. Random row splits are banned. Train stations never test."""

from __future__ import annotations

import numpy as np

from inrain.config import (
    BLOCK_DEG,
    HOLDOUT_BLOCK_OFFSET,
    HOLDOUT_BLOCK_STRIDE,
    HOLDOUT_START,
    IN_LAT,
    IN_LON,
    WY2024_END,
)
from inrain.errors import SplitError
from inrain.pack import RainPack

TRAIN_END64 = np.datetime64(WY2024_END.isoformat())
HOLDOUT_START64 = np.datetime64(HOLDOUT_START.isoformat())
AUG2026_START = np.datetime64("2026-08-01")
AUG2026_END = np.datetime64("2026-08-31")


def as_day(dates: np.ndarray) -> np.ndarray:
    return np.asarray(dates).astype("datetime64[D]")


def august_2026_mask(dates: np.ndarray) -> np.ndarray:
    d = as_day(dates)
    return (d >= AUG2026_START) & (d <= AUG2026_END)


def block_keys(lat: np.ndarray, lon: np.ndarray) -> np.ndarray:
    ilat = np.floor((np.asarray(lat, dtype=float) - IN_LAT[0]) / BLOCK_DEG).astype(np.int32)
    ilon = np.floor((np.asarray(lon, dtype=float) - IN_LON[0]) / BLOCK_DEG).astype(np.int32)
    return np.char.add(np.char.add(ilat.astype(str), ":"), ilon.astype(str))


def holdout_block_set(keys: np.ndarray) -> set[str]:
    uniq = sorted(set(np.asarray(keys).astype(str).tolist()))
    return {k for i, k in enumerate(uniq) if i % HOLDOUT_BLOCK_STRIDE == HOLDOUT_BLOCK_OFFSET}


def station_holdout_ids(pack: RainPack) -> set[str]:
    """Stations whose block is held out. One station cannot sit in both sets."""
    keys = block_keys(pack.lat, pack.lon)
    held = holdout_block_set(keys)
    ids = np.asarray(pack.station_id).astype(str)
    return set(ids[np.isin(keys, list(held))].tolist())


def row_masks(pack: RainPack) -> tuple[np.ndarray, np.ndarray]:
    d = as_day(pack.dates)
    ids = np.asarray(pack.station_id).astype(str)
    hold_ids = station_holdout_ids(pack)
    in_hold_st = np.isin(ids, list(hold_ids))
    train = (~in_hold_st) & (d <= TRAIN_END64)
    hold = in_hold_st & (d >= HOLDOUT_START64)
    return train, hold


def assert_split(pack: RainPack, train: np.ndarray, holdout: np.ndarray) -> None:
    """Refuse station leak, overlap, empty sides, August 2026 in train, shuffled rows."""
    d = as_day(pack.dates)
    ids = np.asarray(pack.station_id).astype(str)
    train = np.asarray(train, dtype=bool)
    holdout = np.asarray(holdout, dtype=bool)
    if train.shape != d.shape or holdout.shape != d.shape:
        raise SplitError("split masks do not match rows")
    if not train.any():
        raise SplitError("train is empty")
    if not holdout.any():
        raise SplitError("holdout is empty")
    if np.any(train & holdout):
        raise SplitError("train and holdout overlap")
    if np.any(train & august_2026_mask(d)):
        raise SplitError("August 2026 in train")
    train_ids = set(ids[train].tolist())
    hold_ids = set(ids[holdout].tolist())
    leak = train_ids & hold_ids
    if leak:
        raise SplitError(f"station leak {sorted(leak)[:8]}")
    if d[train].max() >= d[holdout].min():
        raise SplitError("not a temporal date cut on top of spatial holdout")
