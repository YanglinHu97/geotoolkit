# tests/test_query.py
import random
from geotoolkit.query import tag_points_within, filter_points_within

def _make_square_poly(x0=0.0, y0=0.0, x1=10.0, y1=10.0):
    return {
        "type": "Polygon",
        "coordinates": [[
            (x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)
        ]]
    }

def _make_points_fc(points):
    return {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "properties": {"id": i+1}, "geometry": {"type": "Point", "coordinates": (x, y)}}
            for i, (x, y) in enumerate(points)
        ]
    }

def test_tag_points_within_naive_vs_indexed_covers():
    poly = _make_square_poly()

    # mix of inside/outside points
    random.seed(0)
    pts = []
    for _ in range(25):
        pts.append((random.uniform(1, 9), random.uniform(1, 9)))      # inside
    for _ in range(25):
        pts.append((random.uniform(20, 30), random.uniform(20, 30)))  # outside

    points_fc = _make_points_fc(pts)

    a = tag_points_within(points_fc, poly, prop="inside", use_index=False, mode="covers")
    b = tag_points_within(points_fc, poly, prop="inside", use_index=True, mode="covers")

    assert [ft["properties"]["inside"] for ft in a["features"]] == [ft["properties"]["inside"] for ft in b["features"]]
    assert sum(ft["properties"]["inside"] for ft in b["features"]) > 0

def test_tag_points_within_naive_vs_indexed_contains():
    poly = _make_square_poly()

    # include boundary point to differentiate contains vs covers
    points_fc = {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "properties": {"id": 1}, "geometry": {"type": "Point", "coordinates": (5.0, 5.0)}},   # inside
            {"type": "Feature", "properties": {"id": 2}, "geometry": {"type": "Point", "coordinates": (0.0, 0.0)}},   # boundary
            {"type": "Feature", "properties": {"id": 3}, "geometry": {"type": "Point", "coordinates": (20.0, 20.0)}}, # outside
        ]
    }

    a = tag_points_within(points_fc, poly, prop="inside", use_index=False, mode="contains")
    b = tag_points_within(points_fc, poly, prop="inside", use_index=True, mode="contains")

    # contains: boundary should be False
    assert [ft["properties"]["inside"] for ft in a["features"]] == [True, False, False]
    assert [ft["properties"]["inside"] for ft in b["features"]] == [True, False, False]

def test_filter_points_within_indexed_covers():
    poly = _make_square_poly()
    points_fc = {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "properties": {"id": 1}, "geometry": {"type": "Point", "coordinates": (5.0, 5.0)}},
            {"type": "Feature", "properties": {"id": 2}, "geometry": {"type": "Point", "coordinates": (20.0, 20.0)}},
        ]
    }
    inside = filter_points_within(points_fc, poly, use_index=True, mode="covers")
    assert len(inside["features"]) == 1
    assert inside["features"][0]["properties"]["id"] == 1

