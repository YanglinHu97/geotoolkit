# Geometric operations implemented following the patterns introduced
# in the geo-algorithms practice notebooks (buffer, intersection, nearest).

from __future__ import annotations

from typing import Any, Dict, Tuple
from shapely.geometry import shape, mapping
from shapely.ops import nearest_points

# Geometric operations implemented following the patterns introduced
# in the geo-algorithms practice notebooks (buffer, intersection, nearest).

JsonDict = Dict[str, Any]

def buffer(geometry: JsonDict, dist_m: float) -> JsonDict:
    """
    Create a buffer around a geometry.

    Notes
    -----
    Distance-based operations require a metric CRS (e.g., EPSG:3857 or UTM).
    """
    g = shape(geometry)
    return mapping(g.buffer(dist_m))


def clip(feature_or_fc: JsonDict, clipper_geom: JsonDict) -> JsonDict:
    """
    Clip a Feature or FeatureCollection by a polygon (intersection).

    Returns
    -------
    GeoJSON FeatureCollection
        Always returns a FeatureCollection. If nothing intersects, returns an
        empty FeatureCollection (features=[]). This keeps the return type stable.
    """
    clipper = shape(clipper_geom)
    t = feature_or_fc.get("type")

    def _clip_feature(ft: JsonDict) -> JsonDict | None:
        geom = shape(ft["geometry"])
        inter = geom.intersection(clipper)
        if inter.is_empty:
            return None
        return {
            "type": "Feature",
            "properties": ft.get("properties", {}),
            "geometry": mapping(inter),
        }

    # FeatureCollection
    if t == "FeatureCollection":
        out_feats = []
        for ft in feature_or_fc.get("features", []):
            clipped_ft = _clip_feature(ft)
            if clipped_ft is not None:
                out_feats.append(clipped_ft)
        return {"type": "FeatureCollection", "features": out_feats}

    # Feature -> wrap into a FeatureCollection for stable return type
    if t == "Feature":
        clipped_ft = _clip_feature(feature_or_fc)
        return {"type": "FeatureCollection", "features": [] if clipped_ft is None else [clipped_ft]}

    # Geometry only -> return geometry intersection
    inter = shape(feature_or_fc).intersection(clipper)
    return mapping(inter)


def nearest(a_geom: JsonDict, b_geom: JsonDict) -> Tuple[float, JsonDict, JsonDict]:
    """
    Compute nearest distance and nearest points between two geometries.

    Notes
    -----
    Distances are meaningful only in a metric CRS.
    """
    A = shape(a_geom)
    B = shape(b_geom)

    pA, pB = nearest_points(A, B)
    return (pA.distance(pB), mapping(pA), mapping(pB))

# --- 新增功能: 几何属性计算 ---

def get_area(geometry: JsonDict) -> float:
    """
    计算几何体的面积。
    注意：输入数据必须是投影坐标系（如米），否则计算结果无意义。
    """
    return shape(geometry).area

def get_length(geometry: JsonDict) -> float:
    """
    计算几何体的长度（对于多边形则是周长）。
    注意：输入数据必须是投影坐标系（如米）。
    """
    return shape(geometry).length

# --- 新增功能: 空间关系判断 ---

def is_contained(container_geom: JsonDict, content_geom: JsonDict) -> bool:
    """
    判断 content_geom (如点) 是否完全在 container_geom (如多边形) 内部。
    """
    return shape(container_geom).contains(shape(content_geom))