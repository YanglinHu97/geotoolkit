from geotoolkit.knn import knn_points

def test_knn_points_basic():
    points_fc = {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "properties": {"id": 1}, "geometry": {"type": "Point", "coordinates": (0.0, 0.0)}},
            {"type": "Feature", "properties": {"id": 2}, "geometry": {"type": "Point", "coordinates": (1.0, 0.0)}},
            {"type": "Feature", "properties": {"id": 3}, "geometry": {"type": "Point", "coordinates": (5.0, 0.0)}},
        ],
    }
    target = {"type": "Point", "coordinates": (0.0, 0.0)}
    top2 = knn_points(points_fc, target, k=2, use_index=True)

    assert top2["type"] == "FeatureCollection"
    assert len(top2["features"]) == 2
    assert top2["features"][0]["properties"]["id"] == 1
    assert top2["features"][1]["properties"]["id"] == 2
    assert top2["features"][0]["properties"]["distance_m"] <= top2["features"][1]["properties"]["distance_m"]
