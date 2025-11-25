from geotoolkit.io import read_geojson
from geotoolkit.project import to_epsg
from geotoolkit.analysis import buffer, clip, nearest

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