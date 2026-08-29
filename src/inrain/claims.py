# Copyright (c) 2026 Martial Systems LLC
"""Fail closed: bias map is residual, RadarOnly is the independent QPE."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

from inrain.errors import ClaimBanError

_BANS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("casualty", re.compile(r"\b(deaths?|fatalit(?:y|ies)|casualt(?:y|ies)|killed)\b", re.I)),
    ("climate", re.compile(r"\b(cmip\d*|downscal(?:e|ed|ing)|gcm)\b", re.I)),
    ("p100", re.compile(r"\b100-year\s+exceedance\b", re.I)),
    ("flood_warning", re.compile(r"\bflood warning\b|\bemergency forecast\b", re.I)),
    ("flood_ai", re.compile(r"\bflood AI\b", re.I)),
    ("qpf", re.compile(r"\bQPF is (?:the |an )?independent\b", re.I)),
    ("p_sfha_feat", re.compile(r"\bp_sfha as (?:a )?(?:feature|label|forecast)\b", re.I)),
    ("firm", re.compile(r"\bbias (?:map|layer) is (?:a |the )?FIRM\b", re.I)),
    ("bias_wet", re.compile(r"\bbias (?:map|layer) is (?:a |the )?(?:wet mask|inundation)\b", re.I)),
    ("bias_water", re.compile(r"\bbias (?:map|layer) is (?:a |the )?water\b", re.I)),
    ("gaugecorr_indep", re.compile(r"\bGaugeCorr is independent\b", re.I)),
    ("fixture_rescues", re.compile(r"\bfixture (?:skill|RMSE) rescues live\b", re.I)),
    ("train_fema", re.compile(r"\btrain(?:ed|ing)? (?:a )?(?:flood )?model on FEMA\b", re.I)),
)


def scan_text(text: str) -> list[str]:
    return [name for name, pat in _BANS if pat.search(text or "")]


def require_clean(text: str, *, source: str) -> None:
    hits = scan_text(text)
    if hits:
        raise ClaimBanError(f"{source}: banned claims {hits}")
    if "—" in (text or ""):
        raise ClaimBanError(f"{source}: em dash")


def require_paths_clean(paths: Iterable[Path]) -> None:
    for path in paths:
        if path.is_file():
            require_clean(path.read_text(encoding="utf-8"), source=str(path))
