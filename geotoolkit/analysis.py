from typing import Dict, Any, Tuple
from shapely.geometry import shape, mapping
from shapely.ops import unary_union, nearest_points

def buffer(geometry: Dict[str, Any], dist_m: float) -> Dict[str, Any]:
    """
    Create a buffer around a geometry.
    Input must be in a meter-based CRS (e.g., EPSG:3857).
    """
    g = shape(geometry)
    return mapping(g.buffer(dist_m))


def clip(feature_or_fc: Dict[str, Any], clipper_geom: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clip a Feature or FeatureCollection by a polygon.
    CRS of inputs must match.
    """
    clipper = shape(clipper_geom)
    t = feature_or_fc.get("type")

    # FeatureCollection
    if t == "FeatureCollection":
        out_feats = []
        for ft in feature_or_fc["features"]:
            geom = shape(ft["geometry"])
            inter = geom.intersection(clipper)
            if not inter.is_empty:
                out_feats.append({
                    "type": "Feature",
                    "properties": ft.get("properties", {}),
                    "geometry": mapping(inter)
                })
        return {"type": "FeatureCollection", "features": out_feats}

    # Feature
    elif t == "Feature":
        geom = shape(feature_or_fc["geometry"])
        inter = geom.intersection(clipper)
        if inter.is_empty:
            return None
        return {
            "type": "Feature",
            "properties": feature_or_fc.get("properties", {}),
            "geometry": mapping(inter)
        }

    # Geometry only
    else:
        inter = shape(feature_or_fc).intersection(clipper)
        return mapping(inter)


def nearest(a_geom: Dict[str, Any], b_geom: Dict[str, Any]) -> Tuple[float, Dict[str, Any], Dict[str, Any]]:
    """
    Compute nearest distance and nearest points between two geometries.
    CRS must be metric for meaningful distance.
    """
    A = shape(a_geom)
    B = shape(b_geom)

    # union multiparts for simplicity
    aU = unary_union([A])
    bU = unary_union([B])

    pA, pB = nearest_points(aU, bU)
    return (pA.distance(pB), mapping(pA), mapping(pB))