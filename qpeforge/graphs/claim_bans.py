# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

from typing import Any

from qpeforge.graphs._common import binary_graph

_FLAGS = ("bias_as_wet_mask", "bias_as_water", "flood_warning", "gaugecorr_independent")


def _evaluate(state: dict[str, Any]) -> dict[str, Any]:
    v = [k for k in _FLAGS if state.get(k)]
    n = int(state.get("n_figures") or 0)
    if n > 2:
        v.append("figure_cap")
    return {"violations": v, "events": [{"node": "evaluate", "ok": not v}]}


def build_graph():
    return binary_graph(
        name="qpe.claim_bans",
        evaluate=_evaluate,
        extra=[*_FLAGS, "n_figures"],
    )
