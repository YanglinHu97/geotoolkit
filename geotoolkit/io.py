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


def write_csv(data_list, path):
    """
    将字典列表写入 CSV 文件
    :param data_list: 包含字典的列表，例如 [{'ID':1, 'Val':10}, {'ID':2, 'Val':20}]
    :param path: 保存路径
    """
    if not data_list:
        print("没有数据需要写入 CSV")
        return
    
    # 获取表头 (取第一行数据的 keys)
    keys = data_list[0].keys()
    
    try:
        # newline='' 是为了防止在 Windows 下出现空行
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader() # 写入表头
            writer.writerows(data_list) # 写入数据
        print(f" -> CSV 文件已保存: {path}")
    except Exception as e:
        print(f" [错误] 写入 CSV 失败: {e}")