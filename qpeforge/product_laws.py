# Copyright (c) 2026 Martial Systems LLC
"""Four refuse laws. Verify-before-done is the finish gate."""

from __future__ import annotations

from typing import Any


def laws() -> list[dict[str, Any]]:
    from qpeforge.graphs.claim_bans import build_graph as claim_bans
    from qpeforge.graphs.fetch_radar_only import build_graph as fetch_radar
    from qpeforge.graphs.no_p_sfha import build_graph as no_p_sfha
    from qpeforge.graphs.spatial_split import build_graph as spatial_split

    return [
        {
            "id": "qpe.no_p_sfha",
            "build": no_p_sfha,
            "state": {
                "p_sfha_feature": False,
                "p_sfha_label": False,
                "p_sfha_figure": False,
                "p_sfha_import": False,
            },
            "allow_decisions": ["allow"],
        },
        {
            "id": "qpe.spatial_split",
            "build": spatial_split,
            "state": {
                "spatial_ok": True,
                "station_leak": False,
                "random_split": False,
                "august_2026_in_train": False,
                "gauge_as_feature": False,
            },
            "allow_decisions": ["allow"],
        },
        {
            "id": "qpe.fetch_radar_only",
            "build": fetch_radar,
            "state": {
                "cocorahs_ok": True,
                "mrms_ok": True,
                "product_is_radar_only": True,
                "product_is_gauge_corr": False,
                "substitute_prism": False,
                "substitute_stageiv": False,
            },
            "allow_decisions": ["allow"],
        },
        {
            "id": "qpe.claim_bans",
            "build": claim_bans,
            "state": {
                "bias_as_wet_mask": False,
                "bias_as_water": False,
                "flood_warning": False,
                "gaugecorr_independent": False,
                "n_figures": 2,
            },
            "allow_decisions": ["allow"],
        },
    ]
