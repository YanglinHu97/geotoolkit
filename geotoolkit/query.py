# geotoolkit/query.py
from __future__ import annotations

from typing import Any, Dict, List

from shapely.geometry import shape, mapping
from shapely.strtree import STRtree

JsonDict = Dict[str, Any]


def _iter_point_features(fc: JsonDict) -> List[JsonDict]:
    """Return only Point features from a FeatureCollection."""
    if fc.get("type") != "FeatureCollection":
        raise ValueError("points_fc must be a GeoJSON FeatureCollection")
    feats = fc.get("features", [])
    return [ft for ft in feats if ft.get("geometry", {}).get("type") == "Point"]


def tag_points_within(
    points_fc: JsonDict,
    polygon_geom: JsonDict,
    prop: str = "inside",
    use_index: bool = False,
    mode: str = "contains",
) -> JsonDict:
    """
    Tag each point feature with a boolean property indicating whether it is inside polygon_geom.

    Parameters
    ----------
    points_fc : GeoJSON FeatureCollection (Points)
    polygon_geom : GeoJSON Geometry (Polygon / MultiPolygon)
    prop : property name to store the boolean tag
    use_index : if True, use STRtree spatial index to reduce candidate checks
    mode : 'contains' (strict) or 'covers' (includes boundary)

    Returns
    -------
    GeoJSON FeatureCollection (Points only, properties preserved + tag added)
    """
    poly = shape(polygon_geom)

    if mode not in ("contains", "covers"):
        raise ValueError("mode must be 'contains' or 'covers'")

    point_feats = _iter_point_features(points_fc)

    # Prepare output features (copy properties safely)
    out_features: List[JsonDict] = []

    if not use_index:
        # Baseline: O(n)
        for ft in point_feats:
            pt = shape(ft["geometry"])
            inside = poly.contains(pt) if mode == "contains" else poly.covers(pt)
            props = dict(ft.get("properties", {}))
            props[prop] = bool(inside)
            out_features.append({"type": "Feature", "properties": props, "geometry": mapping(pt)})
        return {"type": "FeatureCollection", "features": out_features}

    # Indexed: build STRtree on point geometries
    pts = [shape(ft["geometry"]) for ft in point_feats]
    tree = STRtree(pts)

    # STRtree.query(poly) returns candidate geometries whose bbox intersects poly bbox
    # STRtree.query returns INDICES in Shapely 2.x
    candidate_idx = set(tree.query(poly))

    for i, (ft, pt) in enumerate(zip(point_feats, pts)):
        if i in candidate_idx:
            inside = poly.covers(pt) if mode == "covers" else poly.contains(pt)
        else:
            inside = False

        props = dict(ft.get("properties", {}))
        props[prop] = bool(inside)
        out_features.append({
            "type": "Feature",
            "properties": props,
            "geometry": mapping(pt),
        })


    return {"type": "FeatureCollection", "features": out_features}


def filter_points_within(
    points_fc: JsonDict,
    polygon_geom: JsonDict,
    use_index: bool = False,
    mode: str = "contains",
) -> JsonDict:
    """
    Filter point features that are inside polygon_geom.

    Returns
    -------
    GeoJSON FeatureCollection (only inside points)
    """
    tagged = tag_points_within(points_fc, polygon_geom, prop="_inside", use_index=use_index, mode=mode)
    inside_feats = [ft for ft in tagged["features"] if ft.get("properties", {}).get("_inside") is True]

    # Remove helper prop
    for ft in inside_feats:
        ft["properties"].pop("_inside", None)

    return {"type": "FeatureCollection", "features": inside_feats}
