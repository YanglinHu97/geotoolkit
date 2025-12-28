# GeoJSON I/O utilities adapted from vector data handling practice examples.

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Union

# GeoJSON I/O utilities adapted from vector data handling practice examples.

JsonDict = Dict[str, Any]
PathLike = Union[str, Path]

def read_geojson(path: PathLike) -> JsonDict:
    """Read a GeoJSON file and return it as a Python dictionary."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"GeoJSON not found: {p}")
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)

def write_geojson(obj: JsonDict, path: PathLike) -> None:
    """Write a GeoJSON dictionary to disk."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)