# Copyright (c) 2026 Martial Systems LLC


class GateError(RuntimeError):
    """Stage hard gate failed."""


class ClaimBanError(GateError):
    """Report text hit a banned claim."""


class FetchError(GateError):
    """CoCoRaHS or RadarOnly MRMS 404/empty, or a refused substitute product."""


class SplitError(GateError):
    """Spatial holdout leaked a train station, or a random row shuffle."""


class FigureCapError(GateError):
    """This tree stops at two figures."""
