# Copyright (c) 2026 Martial Systems LLC
"""Identity, IDW, Ridge, HGB on held-out stations. Inches."""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from inrain.config import FEATURE_NAMES, WET_DAY_IN
from inrain.features import label_y, matrix_x
from inrain.idw import idw_predict
from inrain.pack import RainPack
from inrain.split import assert_split, row_masks, station_holdout_ids


def rmse(y: np.ndarray, yhat: np.ndarray) -> float:
    err = np.asarray(y, dtype=float) - np.asarray(yhat, dtype=float)
    return float(np.sqrt(np.mean(err * err)))


def mae(y: np.ndarray, yhat: np.ndarray) -> float:
    return float(np.mean(np.abs(np.asarray(y, dtype=float) - np.asarray(yhat, dtype=float))))


def bias(y: np.ndarray, yhat: np.ndarray) -> float:
    """Predictor minus gauge."""
    return float(np.mean(np.asarray(yhat, dtype=float) - np.asarray(y, dtype=float)))


def csi(y: np.ndarray, yhat: np.ndarray, *, thr: float = WET_DAY_IN) -> float:
    o = np.asarray(y, dtype=float) >= thr
    p = np.asarray(yhat, dtype=float) >= thr
    hit = int(np.sum(o & p))
    den = int(np.sum(o | p))
    if den == 0:
        return float("nan")
    return hit / den


def _skill(y: np.ndarray, yhat: np.ndarray) -> dict[str, float]:
    finite = np.isfinite(y) & np.isfinite(yhat)
    yy, pp = y[finite], yhat[finite]
    if yy.size == 0:
        return {"rmse_in": float("nan"), "mae_in": float("nan"), "bias_in": float("nan"), "csi_010": float("nan"), "n": 0}
    return {
        "rmse_in": rmse(yy, pp),
        "mae_in": mae(yy, pp),
        "bias_in": bias(yy, pp),
        "csi_010": csi(yy, pp),
        "n": int(yy.size),
    }


def fit_pack(pack: RainPack) -> dict[str, Any]:
    train, hold = row_masks(pack)
    assert_split(pack, train, hold)
    x = matrix_x(pack)
    y = label_y(pack)
    ok = np.isfinite(x).all(axis=1) & np.isfinite(y)
    train = train & ok
    hold = hold & ok
    if not train.any() or not hold.any():
        from inrain.errors import SplitError

        raise SplitError("no valid rows in train or holdout")

    y_tr, y_ho = y[train], y[hold]
    x_tr, x_ho = x[train], x[hold]
    yhat_id = np.asarray(pack.mrms_in, dtype=float)[hold]

    # Same-day IDW donors are train-block stations on the prediction day, including
    # holdout-period days. ML training rows stop at WY2024; the interpolator does not.
    hold_ids = station_holdout_ids(pack)
    donor = ~np.isin(np.asarray(pack.station_id).astype(str), list(hold_ids)) & ok
    yhat_idw = idw_predict(
        train_lat=pack.lat[donor],
        train_lon=pack.lon[donor],
        train_y=y[donor],
        train_day=pack.dates[donor],
        pred_lat=pack.lat[hold],
        pred_lon=pack.lon[hold],
        pred_day=pack.dates[hold],
    )

    ridge = Pipeline([("scale", StandardScaler()), ("ridge", Ridge(alpha=1.0))])
    ridge.fit(x_tr, y_tr)
    yhat_ridge = ridge.predict(x_ho)

    hgb = HistGradientBoostingRegressor(
        max_depth=4,
        max_iter=120,
        learning_rate=0.08,
        min_samples_leaf=20,
        l2_regularization=0.1,
        random_state=0,
    )
    hgb.fit(x_tr, y_tr)
    yhat_hgb = hgb.predict(x_ho)

    st_ho = np.asarray(pack.station_id, dtype=str)[hold]
    lat_ho = np.asarray(pack.lat, dtype=float)[hold]
    lon_ho = np.asarray(pack.lon, dtype=float)[hold]
    uniq = np.unique(st_ho)
    station_bias = []
    for sid in uniq:
        m = st_ho == sid
        station_bias.append(
            {
                "station_id": str(sid),
                "lat": float(lat_ho[m][0]),
                "lon": float(lon_ho[m][0]),
                "n": int(m.sum()),
                "bias_in": bias(y_ho[m], yhat_id[m]),
                "hgb_bias_in": bias(y_ho[m], yhat_hgb[m]),
            }
        )

    return {
        "n_train": int(train.sum()),
        "n_holdout": int(hold.sum()),
        "n_train_stations": int(np.unique(pack.station_id[train]).shape[0]),
        "n_holdout_stations": int(uniq.shape[0]),
        "feature_names": list(FEATURE_NAMES),
        "skill": {
            "identity": {**_skill(y_ho, yhat_id), "name": "RadarOnly"},
            "idw": {**_skill(y_ho, yhat_idw), "name": "IDW"},
            "ridge": {**_skill(y_ho, yhat_ridge), "name": "Ridge"},
            "hgb": {**_skill(y_ho, yhat_hgb), "name": "HGB"},
        },
        "holdout": {
            "dates": pack.dates[hold],
            "station_id": st_ho,
            "lat": lat_ho,
            "lon": lon_ho,
            "gauge_in": y_ho,
            "identity_in": yhat_id,
            "idw_in": yhat_idw,
            "ridge_in": yhat_ridge,
            "hgb_in": yhat_hgb,
        },
        "station_bias": station_bias,
        "august_2026_in_train": False,
        "random_split": False,
        "station_leak": False,
        "gauge_as_feature": False,
    }
