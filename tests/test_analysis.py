from shapely.geometry import shape
from geotoolkit.io import read_geojson
from geotoolkit.project import to_epsg
from geotoolkit.analysis import (
    buffer, clip, nearest,
    nearest_optimized,
    get_bbox, get_centroid, get_envelope
)


def test_buffer_clip_nearest():
    """Test standard geometric operations (Buffer, Clip, Nearest)."""
    # 1. Prepare Data
    fc = read_geojson("data/sample.geojson")
    fc_m = to_epsg(fc, 4326, 3857)

    poly = [f for f in fc_m["features"] if f["geometry"]["type"]=="Polygon"][0]["geometry"]
    pt = [f for f in fc_m["features"] if f["geometry"]["type"]=="Point"][0]["geometry"]

    # 2. Test Buffer
    buf = buffer(poly, 100)
    assert buf["type"] == "Polygon"
    # Area of buffer should be larger than original polygon
    assert shape(buf).area > shape(poly).area

    # 3. Test Clip
    clipped = clip(fc_m, buf)
    assert clipped["type"] == "FeatureCollection"
    # Since we clip with a buffer of the polygon itself, the polygon should remain
    assert len(clipped["features"]) >= 1

    # 4. Test Nearest (Brute Force)
    dist, a, b = nearest(pt, poly)
    assert dist >= 0
    
def test_bbox_centroid_basic():
    # simple rectangle polygon: centroid is exactly (5, 5)
    poly = {
        "type": "Polygon",
        "coordinates": [[
            (0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0), (0.0, 0.0)
        ]]
    }

    assert get_bbox(poly) == (0.0, 0.0, 10.0, 10.0)

    c = get_centroid(poly)
    assert c["type"] == "Point"
    assert c["coordinates"] == (5.0, 5.0)


def test_spatial_indexing():
    """
    [NEW] Test if the optimized STRtree search returns the exact same result
    as the brute-force method.
    """
    fc = read_geojson("data/sample.geojson")
    fc_m = to_epsg(fc, 4326, 3857)

    pt = [f for f in fc_m["features"] if f["geometry"]["type"] == "Point"][0]["geometry"]

    # 1. Run Standard Nearest
    poly_geom = [f for f in fc_m["features"] if f["geometry"]["type"] == "Polygon"][0]["geometry"]
    dist_std, _, _ = nearest(pt, poly_geom)

    # 2. Run Optimized Nearest
    dist_opt, _ = nearest_optimized(pt, fc_m)

    # 3. Assert Equality
    assert abs(dist_std - dist_opt) < 1e-6, "Spatial Indexing result mismatch!"


def test_geometric_features():
    """[NEW] Test Centroid and Envelope calculation."""
    fc = read_geojson("data/sample.geojson")
    fc_m = to_epsg(fc, 4326, 3857)
    poly = [f for f in fc_m["features"] if f["geometry"]["type"] == "Polygon"][0]["geometry"]

    # 1. Test Centroid
    cent = get_centroid(poly)
    assert cent["type"] == "Point"
    # For a simple convex polygon, the centroid must be strictly inside it
    assert shape(poly).contains(shape(cent))

    # 2. Test Envelope
    env = get_envelope(poly)
    assert env["type"] == "Polygon"
    assert shape(env).area >= shape(poly).area

