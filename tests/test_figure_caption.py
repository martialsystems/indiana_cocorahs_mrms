# Copyright (c) 2026 Martial Systems LLC

import json
from pathlib import Path

from matplotlib.path import Path as MplPath

from inrain.config import BIAS_MAP_PAD_DEG, INDIANA_RING, LIVE_BIAS_SUBTITLE, LOCKED_LIVE_COMMIT
from inrain.figure import scatter_subtitle, write_bias_map

REPO = Path(__file__).resolve().parents[1]


def test_live_captions_name_radar_and_clock() -> None:
    fit = {
        "skill": {
            "identity": {"rmse_in": 0.13306947137742373},
            "hgb": {"rmse_in": 0.14050355160274344},
        }
    }
    sub = scatter_subtitle(fit, live=True)
    assert sub.startswith("RadarOnly 0.133")
    assert "HGB 0.141" in sub
    assert "Ridge" not in sub
    assert "12Z 24h vs 7am local" in sub
    assert "volunteer QC" in sub
    assert "12Z 24h vs 7am local" in LIVE_BIAS_SUBTITLE
    assert "volunteer QC" in LIVE_BIAS_SUBTITLE
    assert LOCKED_LIVE_COMMIT.startswith("ac36f0f")
    first, sep, rest = sub.partition(". ")
    assert sep
    assert "0.133" in first
    assert "12Z" in rest


def test_live_stations_sit_inside_padded_indiana() -> None:
    report = json.loads((REPO / "logs" / "in_live" / "stage_c_report.json").read_text(encoding="utf-8"))
    ring = MplPath(INDIANA_RING)
    pts = [(row["lon"], row["lat"]) for row in report["station_bias"]]
    inside = ring.contains_points(pts)
    assert inside.all()
    lons = [p[0] for p in INDIANA_RING]
    lats = [p[1] for p in INDIANA_RING]
    assert min(lons) < -87.9 and max(lons) > -85.0
    assert min(lats) < 37.85 and max(lats) > 41.7
    pad = BIAS_MAP_PAD_DEG
    for lon, lat in pts:
        assert min(lons) - pad < lon < max(lons) + pad
        assert min(lats) - pad < lat < max(lats) + pad


def test_bias_map_keeps_margins(tmp_path: Path) -> None:
    report = json.loads((REPO / "logs" / "in_live" / "stage_c_report.json").read_text(encoding="utf-8"))
    dest = tmp_path / "bias_map.png"
    write_bias_map(
        dest,
        fit={"station_bias": report["station_bias"]},
        title="Held-out station mean RadarOnly minus CoCoRaHS",
        subtitle=LIVE_BIAS_SUBTITLE,
    )
    from PIL import Image

    im = Image.open(dest)
    w, h = im.size
    assert w >= 700 and h >= 800
    # Footer caption lives in the bottom strip; it must not be empty white-only
    # at the cost of clipping the state (old crop restamp).
    arr = __import__("numpy").asarray(im.convert("L"))
    bottom = arr[-40:]
    top = arr[:40]
    assert float(bottom.mean()) > 240
    assert float(top.mean()) > 230
