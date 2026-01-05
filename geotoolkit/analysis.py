# Geometric operations implemented following the patterns introduced
# in the geo-algorithms practice notebooks (buffer, intersection, nearest).

from __future__ import annotations

from typing import Any, Dict, Tuple
from shapely.geometry import shape, mapping
from shapely.ops import nearest_points

JsonDict = Dict[str, Any]

def buffer(geometry: JsonDict, dist_m: float) -> JsonDict:
    """
    Create a buffer around a geometry.

    Notes
    -----
    Distance-based operations require a metric CRS (e.g., EPSG:3857 or UTM).
    """
    # Convert the input GeoJSON dict to a Shapely geometry object for calculation
    g = shape(geometry)
    
    # Perform the buffer operation using Shapely
    # Then convert the result back to a GeoJSON dictionary using mapping()
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
    # Convert the clipper geometry (the cookie cutter) to a Shapely object
    clipper = shape(clipper_geom)
    t = feature_or_fc.get("type")

    # Internal helper function to clip a single Feature
    def _clip_feature(ft: JsonDict) -> JsonDict | None:
        # Convert feature geometry to Shapely
        geom = shape(ft["geometry"])
        
        # Calculate intersection (the overlapping part)
        inter = geom.intersection(clipper)
        
        # If there is no intersection, discard this feature
        if inter.is_empty:
            return None
            
        # Return a new Feature preserving original properties
        return {
            "type": "Feature",
            "properties": ft.get("properties", {}),
            "geometry": mapping(inter), # Convert back to GeoJSON
        }

    # Case A: Input is a FeatureCollection (a list of features)
    if t == "FeatureCollection":
        out_feats = []
        # Loop through every feature in the collection
        for ft in feature_or_fc.get("features", []):
            clipped_ft = _clip_feature(ft)
            # Only add features that actually intersected
            if clipped_ft is not None:
                out_feats.append(clipped_ft)
        return {"type": "FeatureCollection", "features": out_feats}

    # Case B: Input is a single Feature
    # We wrap it into a FeatureCollection to maintain a consistent return type
    if t == "Feature":
        clipped_ft = _clip_feature(feature_or_fc)
        # Return empty list if clipped away, else list with one item
        return {"type": "FeatureCollection", "features": [] if clipped_ft is None else [clipped_ft]}

    # Case C: Input is a raw Geometry (e.g. just a Polygon)
    # Simply return the geometric intersection
    inter = shape(feature_or_fc).intersection(clipper)
    return mapping(inter)


def nearest(a_geom: JsonDict, b_geom: JsonDict) -> Tuple[float, JsonDict, JsonDict]:
    """
    Compute nearest distance and nearest points between two geometries.

    Notes
    -----
    Distances are meaningful only in a metric CRS.
    """
    # Convert both inputs to Shapely objects
    A = shape(a_geom)
    B = shape(b_geom)

    # nearest_points returns a tuple of the two closest points (Point on A, Point on B)
    pA, pB = nearest_points(A, B)
    
    # Calculate Euclidean distance and return points in GeoJSON format
    return (pA.distance(pB), mapping(pA), mapping(pB))

# --- New Features: Geometric Attribute Calculation ---

def get_area(geometry: JsonDict) -> float:
    """
    Calculate the area of a geometry.
    Note: Input data must be in a projected coordinate system (e.g., meters) for meaningful results.
    """
    # .area is a property of Shapely geometry objects
    return shape(geometry).area

def get_length(geometry: JsonDict) -> float:
    """
    Calculate the length of a geometry (perimeter for polygons).
    Note: Input data must be in a projected coordinate system (e.g., meters).
    """
    # .length computes perimeter for Polygons or length for LineStrings
    return shape(geometry).length

def is_contained(container_geom: JsonDict, content_geom: JsonDict) -> bool:
    """
    Determine if content_geom (e.g., a Point) is strictly inside container_geom (e.g., a Polygon).
    """
    # .contains() returns True only if no points of the second geometry lie in the exterior of the first
    return shape(container_geom).contains(shape(content_geom))