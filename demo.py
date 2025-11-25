from geotoolkit.io import read_geojson, write_geojson
from geotoolkit.project import to_epsg
from geotoolkit.analysis import buffer, clip, nearest

# 1) Load sample data (WGS84)
fc = read_geojson("data/sample.geojson")

# 2) Reproject to EPSG:3857 (meters)
fc_m = to_epsg(fc, 4326, 3857)

# 3) Extract polygon & point
poly = [f for f in fc_m["features"] if f["geometry"]["type"] == "Polygon"][0]["geometry"]
pt = [f for f in fc_m["features"] if f["geometry"]["type"] == "Point"][0]["geometry"]

# 4) Buffer polygon by 500 meters
buf = buffer(poly, 500)
write_geojson(buf, "out/buffer_500m.geojson")

# 5) Clip features to buffer
clipped = clip(fc_m, buf)
write_geojson(clipped, "out/clipped_features.geojson")

# 6) Compute nearest point distance (meters)
dist, a, b = nearest(pt, poly)

print("--- Results ---")
print("Buffered polygon saved to out/buffer_500m.geojson")
print("Clipped features saved to out/clipped_features.geojson")
print("Nearest distance (m):", round(dist, 2))