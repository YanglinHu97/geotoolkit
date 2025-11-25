from geotoolkit.io import read_geojson
from geotoolkit.project import to_epsg
from shapely.geometry import shape

def test_roundtrip_projection():
    # 读入示例数据
    fc = read_geojson("data/sample.geojson")

    # 4326 -> 3857 -> 4326 回环
    fc_m = to_epsg(fc, 4326, 3857)
    fc_back = to_epsg(fc_m, 3857, 4326)

    # 取第一个点，比较几何误差是否极小（经纬度单位下的小数秒级）
    p0 = shape(fc["features"][0]["geometry"])
    p1 = shape(fc_back["features"][0]["geometry"])
    assert p0.distance(p1) < 1e-5