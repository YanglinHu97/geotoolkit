# GeoJSON I/O utilities adapted from vector data handling practice examples.

from __future__ import annotations
import csv
import json
from pathlib import Path
from typing import Any, Dict, Union

# GeoJSON I/O utilities adapted from vector data handling practice examples.

JsonDict = Dict[str, Any]
PathLike = Union[str, Path]

def read_geojson(path: PathLike) -> JsonDict:
    """Read a GeoJSON file and return it as a Python dictionary."""
    p = Path(path)
    # Verify file existence to prevent runtime crashes later
    if not p.exists():
        raise FileNotFoundError(f"GeoJSON not found: {p}")
    
    # Open with UTF-8 encoding to handle special characters correctly
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)

def write_geojson(obj: JsonDict, path: PathLike) -> None:
    """Write a GeoJSON dictionary to disk."""
    p = Path(path)
    # Ensure the directory exists (e.g., create 'out/' if missing)
    p.parent.mkdir(parents=True, exist_ok=True)
    
    # Write file with pretty printing (indent=2) for readability
    # ensure_ascii=False allows writing non-English characters properly
    with p.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def write_csv(data_list, path):
    """
    Write a list of dictionaries to a CSV file.
    :param data_list: List containing dictionaries, e.g., [{'ID':1, 'Val':10}, {'ID':2, 'Val':20}]
    :param path: Save path
    """
    # Safety check: do nothing if the list is empty
    if not data_list:
        print("No data to write to CSV")
        return
    
    # Extract headers dynamically from the keys of the first dictionary
    keys = data_list[0].keys()
    
    try:
        # newline='' is crucial on Windows to prevent blank lines between rows
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader() # Write the header row (column names)
            writer.writerows(data_list) # Write all data rows
        print(f" -> CSV file saved: {path}")
    except Exception as e:
        print(f" [Error] Failed to write CSV: {e}")