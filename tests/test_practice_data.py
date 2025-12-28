import math
from geotoolkit.io import read_geojson
from geotoolkit.project import to_epsg
from geotoolkit.analysis import buffer, clip, nearest


def _get_epsg_from_geojson_crs(fc):
    """
    Try to read EPSG code from GeoJSON 'crs' field like:
    {'type': 'name', 'properties': {'name': 'urn:ogc:def:crs:EPSG::32632'}}
    Returns int EPSG or None.
    """
    crs = fc.get("crs")
    if not crs:
        return None
    props = crs.get("properties", {})
    name = props.get("name", "")
    # common patterns: "EPSG:4326" or "urn:ogc:def:crs:EPSG::32632"
    if "EPSG" in name:
        digits = "".join(ch for ch in name if ch.isdigit())
        return int(digits) if digits else None
    return None


def _finite_point_feature(ft):
    """Return True if feature is a Point with finite x/y coordinates."""
    geom = ft.get("geometry", {})
    if geom.get("type") != "Point":
        return False
    coords = geom.get("coordinates", [])
    if not isinstance(coords, (list, tuple)) or len(coords) < 2:
        return False
    x, y = coords[0], coords[1]
    return isinstance(x, (int, float)) and isinstance(y, (int, float)) and math.isfinite(x) and math.isfinite(y)


def test_practice_search_points_workflow():
    # Load practice points (has CRS: EPSG:32632 in your file)
    fc_points = read_geojson("data/search_points.geojson")

    # Load your sample polygon (assumed EPSG:4326)
    fc_sample = read_geojson("data/sample.geojson")

    # Determine CRS of practice points from GeoJSON
    epsg_points = _get_epsg_from_geojson_crs(fc_points)

    # We want everything in a metric CRS. Use EPSG:32632 if available, otherwise EPSG:3857.
    target_epsg = epsg_points if epsg_points is not None else 3857

    # Reproject polygon into target metric CRS
    fc_sample_m = to_epsg(fc_sample, 4326, target_epsg)
    poly = [f for f in fc_sample_m["features"] if f["geometry"]["type"] == "Polygon"][0]["geometry"]

    # Reproject points only if they are not already in target CRS
    if epsg_points is None:
        # assume lon/lat if unknown
        fc_points_m = to_epsg(fc_points, 4326, target_epsg)
    elif epsg_points != target_epsg:
        fc_points_m = to_epsg(fc_points, epsg_points, target_epsg)
    else:
        fc_points_m = fc_points

    # Pick one finite point
    finite_pts = [ft for ft in fc_points_m.get("features", []) if _finite_point_feature(ft)]
    assert len(finite_pts) > 0, "No finite Point coordinates found in practice dataset"

    # Buffer polygon (meters)
    buf = buffer(poly, 500)
    assert buf["type"] == "Polygon"

    # Clip points to buffer
    clipped = clip(fc_points_m, buf)
    assert clipped["type"] == "FeatureCollection"
    assert len(clipped["features"]) <= len(fc_points_m["features"])

    # Nearest distance between a point and polygon
    pt = finite_pts[0]["geometry"]
    dist, a, b = nearest(pt, poly)
    assert dist >= 0
    assert a["type"] == "Point"
    assert b["type"] == "Point"