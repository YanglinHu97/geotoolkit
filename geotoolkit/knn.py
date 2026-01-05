# geotoolkit/knn.py
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from shapely.geometry import shape, mapping
from shapely.strtree import STRtree

JsonDict = Dict[str, Any]


def _iter_point_features(fc: JsonDict) -> List[JsonDict]:
    if fc.get("type") != "FeatureCollection":
        raise ValueError("points_fc must be a GeoJSON FeatureCollection")
    feats = fc.get("features", [])
    return [ft for ft in feats if ft.get("geometry", {}).get("type") == "Point"]


def knn_points(
    points_fc: JsonDict,
    target_point_geom: JsonDict,
    k: int = 10,
    use_index: bool = False,
) -> JsonDict:
    """
    Return k nearest points to a target Point (GeoJSON geometry dict).

    Output: FeatureCollection of top-k point Features, each with added property:
      - distance_m: distance to target (units depend on CRS; meters in EPSG:3857)
    """
    if k <= 0:
        raise ValueError("k must be > 0")

    target = shape(target_point_geom)
    if target.geom_type != "Point":
        raise ValueError("target_point_geom must be a Point geometry")

    point_feats = _iter_point_features(points_fc)
    pts = [shape(ft["geometry"]) for ft in point_feats]

    # candidate selection
    if not use_index:
        cand_idx = range(len(pts))
    else:
        # Shapely 2.x: STRtree.query returns indices
        tree = STRtree(pts)

        # start with a small search radius and expand until we have enough candidates
        radius = 50.0  # meters (in EPSG:3857)
        cand_idx_set = set()

        # expand a few rounds; for 1000 points this is plenty
        for _ in range(8):
            envelope = target.buffer(radius)
            idxs = tree.query(envelope)
            cand_idx_set.update(list(idxs))
            if len(cand_idx_set) >= k:
                break
            radius *= 2

        # if still not enough, fall back to all points
        cand_idx = cand_idx_set if len(cand_idx_set) >= k else range(len(pts))

    # compute distances
    dist_list: List[Tuple[float, int]] = []
    for i in cand_idx:
        d = target.distance(pts[i])
        dist_list.append((d, i))

    dist_list.sort(key=lambda x: x[0])
    topk = dist_list[: min(k, len(dist_list))]

    out_features: List[JsonDict] = []
    for rank, (d, i) in enumerate(topk, start=1):
        ft = point_feats[i]
        props = dict(ft.get("properties", {}))
        props["distance_m"] = float(d)
        props["knn_rank"] = rank
        out_features.append({"type": "Feature", "properties": props, "geometry": mapping(pts[i])})

    return {"type": "FeatureCollection", "features": out_features}
