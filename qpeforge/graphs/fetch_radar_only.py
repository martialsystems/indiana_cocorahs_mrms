# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

from typing import Any

from qpeforge.graphs._common import binary_graph


def _evaluate(state: dict[str, Any]) -> dict[str, Any]:
    v: list[str] = []
    if not state.get("cocorahs_ok"):
        v.append("cocorahs_empty")
    if not state.get("mrms_ok"):
        v.append("mrms_empty_or_404")
    if not state.get("product_is_radar_only"):
        v.append("not_radar_only")
    if state.get("product_is_gauge_corr"):
        v.append("gauge_corr")
    if state.get("substitute_prism"):
        v.append("prism")
    if state.get("substitute_stageiv"):
        v.append("stageiv")
    return {"violations": v, "events": [{"node": "evaluate", "ok": not v}]}


def build_graph():
    return binary_graph(
        name="qpe.fetch_radar_only",
        evaluate=_evaluate,
        extra=[
            "cocorahs_ok",
            "mrms_ok",
            "product_is_radar_only",
            "product_is_gauge_corr",
            "substitute_prism",
            "substitute_stageiv",
        ],
    )
