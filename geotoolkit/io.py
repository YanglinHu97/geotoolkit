import json
from typing import Dict, Any

def read_geojson(path: str) -> Dict[str, Any]:
    """Read a GeoJSON file and return as Python dictionary."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_geojson(obj: Dict[str, Any], path: str) -> None:
    """Write a Python dictionary to a GeoJSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)