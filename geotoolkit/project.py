from typing import Dict, Any
from shapely.geometry import shape, mapping
from shapely.ops import transform as shp_transform
from pyproj import Transformer

def _transform_geom(geom_obj: Dict[str, Any], epsg_from: int, epsg_to: int) -> Dict[str, Any]:
    """
    Transform a single GeoJSON geometry dict from epsg_from to epsg_to.
    """
    src = f"EPSG:{epsg_from}"
    dst = f"EPSG:{epsg_to}"
    transformer = Transformer.from_crs(src, dst, always_xy=True)
    g = shape(geom_obj)
    g2 = shp_transform(lambda x, y, z=None: transformer.transform(x, y), g)
    return mapping(g2)

def to_epsg(feature_or_fc: Dict[str, Any], epsg_from: int, epsg_to: int) -> Dict[str, Any]:
    """
    Transform a GeoJSON Feature / FeatureCollection / Geometry between EPSG codes.
    """
    t = feature_or_fc.get("type")
    if t == "FeatureCollection":
        feats = []
        for ft in feature_or_fc["features"]:
            geom2 = _transform_geom(ft["geometry"], epsg_from, epsg_to)
            feats.append({"type": "Feature",
                          "properties": ft.get("properties", {}),
                          "geometry": geom2})
        return {"type": "FeatureCollection", "features": feats}
    elif t == "Feature":
        geom2 = _transform_geom(feature_or_fc["geometry"], epsg_from, epsg_to)
        return {"type": "Feature",
                "properties": feature_or_fc.get("properties", {}),
                "geometry": geom2}
    else:
        # treat as pure geometry dict
        return _transform_geom(feature_or_fc, epsg_from, epsg_to)