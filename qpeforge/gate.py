# Copyright (c) 2026 Martial Systems LLC
"""Call sites for refuse laws."""

from __future__ import annotations

from typing import Any

from qpeforge._bootstrap import ensure_paths

ensure_paths()

from graphforge.product_law import require_law

from qpeforge.graphs.claim_bans import build_graph as build_claims
from qpeforge.graphs.fetch_radar_only import build_graph as build_fetch
from qpeforge.graphs.no_p_sfha import build_graph as build_p
from qpeforge.graphs.spatial_split import build_graph as build_split


def require_no_p_sfha(**flags: Any) -> None:
    thread_id = str(flags.pop("thread_id", "qpe_p"))
    state = {
        "p_sfha_feature": False,
        "p_sfha_label": False,
        "p_sfha_figure": False,
        "p_sfha_import": False,
    }
    state.update(flags)
    require_law(
        build_p(),
        state,
        allow_decisions=["allow"],
        law_id="qpe.no_p_sfha",
        thread_id=thread_id,
        raise_error=True,
    )


def require_split(**flags: Any) -> None:
    thread_id = str(flags.pop("thread_id", "qpe_split"))
    state = {
        "spatial_ok": True,
        "station_leak": False,
        "random_split": False,
        "august_2026_in_train": False,
        "gauge_as_feature": False,
    }
    state.update(flags)
    require_law(
        build_split(),
        state,
        allow_decisions=["allow"],
        law_id="qpe.spatial_split",
        thread_id=thread_id,
        raise_error=True,
    )


def require_fetch(**flags: Any) -> None:
    thread_id = str(flags.pop("thread_id", "qpe_fetch"))
    state = {
        "cocorahs_ok": False,
        "mrms_ok": False,
        "product_is_radar_only": False,
        "product_is_gauge_corr": False,
        "substitute_prism": False,
        "substitute_stageiv": False,
    }
    state.update(flags)
    require_law(
        build_fetch(),
        state,
        allow_decisions=["allow"],
        law_id="qpe.fetch_radar_only",
        thread_id=thread_id,
        raise_error=True,
    )


def require_claims(**flags: Any) -> None:
    thread_id = str(flags.pop("thread_id", "qpe_claims"))
    state = {
        "bias_as_wet_mask": False,
        "bias_as_water": False,
        "flood_warning": False,
        "gaugecorr_independent": False,
        "n_figures": 2,
    }
    state.update(flags)
    require_law(
        build_claims(),
        state,
        allow_decisions=["allow"],
        law_id="qpe.claim_bans",
        thread_id=thread_id,
        raise_error=True,
    )
