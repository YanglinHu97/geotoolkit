import pytest
from shapely.geometry import shape, Point, Polygon
from geotoolkit.analysis import (
    buffer, clip, nearest,
    # [NEW] Import new functions
    nearest_optimized, get_centroid, get_envelope
)
from geotoolkit.project import to_epsg
from geotoolkit.io import read_geojson

def test_buffer_clip():
    """Test standard buffer and clip operations."""
    # 1. Create a simple square polygon
    poly_geom = {
        "type": "Polygon",
        "coordinates": [[[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]]]
    }
    
    # 2. Buffer it
    buf = buffer(poly_geom, 5)
    assert buf["type"] == "Polygon"
    assert shape(buf).area > shape(poly_geom).area
    
    # 3. Clip
    # Create a feature collection with a point inside and a point outside
    fc = {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "geometry": {"type": "Point", "coordinates": [5, 5]}, "properties": {}},
            {"type": "Feature", "geometry": {"type": "Point", "coordinates": [100, 100]}, "properties": {}}
        ]
    }
    clipped = clip(fc, buf)
    assert len(clipped["features"]) == 1

def test_nearest_brute_force():
    """Test standard nearest neighbor calculation."""
    poly_geom = {
        "type": "Polygon",
        "coordinates": [[[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]]]
    }
    pt_geom = {"type": "Point", "coordinates": [15, 5]}
    
    dist, p1, p2 = nearest(pt_geom, poly_geom)
    # Distance from (15,5) to vertical line at x=10 is 5
    assert abs(dist - 5.0) < 1e-6

# ==========================================
# [NEW] Tests for Added Features
# ==========================================

def test_spatial_indexing_vs_brute_force():
    """
    [NEW] Test if the optimized STRtree search returns the exact same result 
    as the brute-force method.
    """
    try:
        # Load real data for a realistic test
        fc = read_geojson("data/sample.geojson")
        fc_m = to_epsg(fc, 4326, 3857)
    except FileNotFoundError:
        pytest.skip("sample.geojson not found, skipping integration test.")

    # Extract a point and the collection of polygons
    pt = [f for f in fc_m["features"] if f["geometry"]["type"]=="Point"][0]["geometry"]
    
    # 1. Run Standard Nearest (Benchmark)
    # We find the nearest polygon manually to compare
    min_dist_std = float("inf")
    for f in fc_m["features"]:
        if f["geometry"]["type"] == "Polygon":
            d, _, _ = nearest(pt, f["geometry"])
            if d < min_dist_std:
                min_dist_std = d
    
    # 2. Run Optimized Nearest (STRtree)
    dist_opt, _ = nearest_optimized(pt, fc_m)
    
    # 3. Assert Equality
    # The results must be identical (allowing for tiny floating point errors)
    assert abs(min_dist_std - dist_opt) < 1e-6, "Spatial Indexing result mismatch!"

def test_geometric_features():
    """[NEW] Test Centroid and Envelope calculation."""
    # Create a simple square: 0,0 to 10,10
    poly_geom = {
        "type": "Polygon",
        "coordinates": [[[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]]]
    }
    
    # 1. Test Centroid
    cent = get_centroid(poly_geom)
    assert cent["type"] == "Point"
    # Centroid of this square should be exactly at (5, 5)
    assert abs(cent["coordinates"][0] - 5.0) < 1e-6
    assert abs(cent["coordinates"][1] - 5.0) < 1e-6
    
    # 2. Test Envelope
    env = get_envelope(poly_geom)
    assert env["type"] == "Polygon"
    # Envelope of a rectangle is the rectangle itself
    assert abs(shape(env).area - 100.0) < 1e-6