# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

from typing import Any

from qpeforge.graphs._common import binary_graph


def _evaluate(state: dict[str, Any]) -> dict[str, Any]:
    v: list[str] = []
    if not state.get("spatial_ok"):
        v.append("not_spatial")
    if state.get("station_leak"):
        v.append("station_leak")
    if state.get("random_split"):
        v.append("random_split")
    if state.get("august_2026_in_train"):
        v.append("august_2026_in_train")
    if state.get("gauge_as_feature"):
        v.append("gauge_as_feature")
    return {"violations": v, "events": [{"node": "evaluate", "ok": not v}]}


def build_graph():
    return binary_graph(
        name="qpe.spatial_split",
        evaluate=_evaluate,
        extra=["spatial_ok", "station_leak", "random_split", "august_2026_in_train", "gauge_as_feature"],
    )
