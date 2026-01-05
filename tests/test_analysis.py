from geotoolkit.io import read_geojson
from geotoolkit.project import to_epsg
from geotoolkit.analysis import buffer, clip, nearest, get_bbox, get_centroid

def test_buffer_clip_nearest():
    fc = read_geojson("data/sample.geojson")
    fc_m = to_epsg(fc, 4326, 3857)

    poly = [f for f in fc_m["features"] if f["geometry"]["type"]=="Polygon"][0]["geometry"]
    pt = [f for f in fc_m["features"] if f["geometry"]["type"]=="Point"][0]["geometry"]

    buf = buffer(poly, 100)
    assert buf["type"] == "Polygon"

    clipped = clip(fc_m, buf)
    assert clipped["type"] == "FeatureCollection"
    assert len(clipped["features"]) >= 1

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
