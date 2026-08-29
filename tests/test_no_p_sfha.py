# Copyright (c) 2026 Martial Systems LLC

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
_IMPORT = re.compile(r"(?:from|import)\s+p_sfha\b")


def test_src_does_not_import_p_sfha() -> None:
    hits: list[str] = []
    for path in (REPO / "src").rglob("*.py"):
        for line in path.read_text(encoding="utf-8").splitlines():
            code = line.split("#", 1)[0]
            if _IMPORT.search(code):
                hits.append(f"{path.relative_to(REPO)}: {line.strip()}")
    assert hits == []
