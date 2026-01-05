# geotoolkit

`geotoolkit` is a small Python library for basic vector-based geoprocessing.
It provides utilities for reading and writing GeoJSON data, coordinate transformation between EPSG codes, geometric buffering, clipping, and nearest distance calculations.
The library is lightweight and does not rely on GDAL, making it suitable for environments such as macOS ARM.

---

## Features

### GeoJSON I/O
- `read_geojson(path)`
- `write_geojson(obj, path)`

### Coordinate Transformation
- `to_epsg(feature_or_fc, epsg_from, epsg_to)`
  Converts a geometry, Feature, or FeatureCollection between coordinate systems.

### Geometric Operations
- `buffer(geometry, dist_m)`
  Creates a metric buffer around a geometry.

- `clip(feature_or_fc, clipper_geom)`
  Clips a Feature or FeatureCollection using a polygon.

- `nearest(a_geom, b_geom)`
  Computes nearest distance and returns nearest points.

---

## Relation to practice lectures

This project is developed based on the coding patterns and examples introduced in the practice lectures of the course.

- Vector data handling and GeoJSON input/output follow the workflows demonstrated in the practice sessions.
- Coordinate reference system transformations and metric-based operations are implemented following the geospatial data handling examples.
- Geometric operations such as buffering, clipping (intersection), and nearest-distance computation are adapted from the shapely-based examples shown in the geo-algorithms practice notebooks.
- The overall project structure, including the Python package layout, demo scripts, unit tests, and documentation, is inspired by the example library development and self-assessment exercises.

For testing, the vector dataset `search_points.geojson` provided in the P3 geoprocessing practice is reused.  
Since it is already provided in a metric coordinate reference system (EPSG:32632), it can be used directly for buffer and nearest-distance computations.

## Installation

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the library in editable mode:

```bash
pip install -e .
```

---

## Project Structure

```
geotoolkit/
│
├── geotoolkit/
│   ├── io.py
│   ├── project.py
│   ├── analysis.py
│   ├── utils.py (optional)
│   └── __init__.py
│
├── data/
│   └── sample.geojson
│
├── out/
│
├── tests/
│   ├── test_project.py
│   └── test_analysis.py
│
├── demo.py
├── README.md
├── setup.cfg
└── pyproject.toml
```

---

## Usage Example

```python
from geotoolkit.io import read_geojson, write_geojson
from geotoolkit.project import to_epsg
from geotoolkit.analysis import buffer, clip, nearest

# Load sample data in EPSG:4326
fc = read_geojson("data/sample.geojson")

# Reproject to EPSG:3857 for metric operations
fc_m = to_epsg(fc, 4326, 3857)

# Extract a polygon and a point
poly = [f for f in fc_m["features"] if f["geometry"]["type"] == "Polygon"][0]["geometry"]
pt = [f for f in fc_m["features"] if f["geometry"]["type"] == "Point"][0]["geometry"]

# Generate a 500 m buffer around the polygon
buf = buffer(poly, 500)
write_geojson(buf, "out/buffer_500m.geojson")

# Clip all features to the buffer
clipped = clip(fc_m, buf)
write_geojson(clipped, "out/clipped_features.geojson")

# Compute nearest distance from the point to the polygon
dist, a, b = nearest(pt, poly)
print("Nearest distance (m):", dist)
```

Run the example:

```bash
python demo.py
```

Output files will appear in the `out/` directory.

---

## Unit Tests

Run tests with pytest:

```bash
pytest -q
```

Expected output:

```
2 passed
```

---

## Notes

- Distance-based operations must be performed in a metric CRS (e.g., EPSG:3857 or UTM).
- Input data must follow the GeoJSON specification.
- This library focuses on essential vector operations rather than full GIS functionality.

---

## License

MIT License.# geotoolkit

`geotoolkit` is a small Python library for basic vector-based geoprocessing.
It provides utilities for reading and writing GeoJSON data, coordinate transformation between EPSG codes, geometric buffering, clipping, and nearest distance calculations.
The library is lightweight and does not rely on GDAL, making it suitable for environments such as macOS ARM.

---

## Features

### GeoJSON I/O
- `read_geojson(path)`
- `write_geojson(obj, path)`

### Coordinate Transformation
- `to_epsg(feature_or_fc, epsg_from, epsg_to)`
  Converts a geometry, Feature, or FeatureCollection between coordinate systems.

### Geometric Operations
- `buffer(geometry, dist_m)`
  Creates a metric buffer around a geometry.

- `clip(feature_or_fc, clipper_geom)`
  Clips a Feature or FeatureCollection using a polygon.

- `nearest(a_geom, b_geom)`
  Computes nearest distance and returns nearest points.

---

## Installation

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the library in editable mode:

```bash
pip install -e .
```

---

## Project Structure

```
geotoolkit/
│
├── geotoolkit/
│   ├── io.py
│   ├── project.py
│   ├── analysis.py
│   ├── utils.py (optional)
│   └── __init__.py
│
├── data/
│   └── sample.geojson
│
├── out/
│
├── tests/
│   ├── test_project.py
│   └── test_analysis.py
│
├── demo.py
├── README.md
├── setup.cfg
└── pyproject.toml
```

---

## Usage Example

```python
from geotoolkit.io import read_geojson, write_geojson
from geotoolkit.project import to_epsg
from geotoolkit.analysis import buffer, clip, nearest

# Load sample data in EPSG:4326
fc = read_geojson("data/sample.geojson")

# Reproject to EPSG:3857 for metric operations
fc_m = to_epsg(fc, 4326, 3857)

# Extract a polygon and a point
poly = [f for f in fc_m["features"] if f["geometry"]["type"] == "Polygon"][0]["geometry"]
pt = [f for f in fc_m["features"] if f["geometry"]["type"] == "Point"][0]["geometry"]

# Generate a 500 m buffer around the polygon
buf = buffer(poly, 500)
write_geojson(buf, "out/buffer_500m.geojson")

# Clip all features to the buffer
clipped = clip(fc_m, buf)
write_geojson(clipped, "out/clipped_features.geojson")

# Compute nearest distance from the point to the polygon
dist, a, b = nearest(pt, poly)
print("Nearest distance (m):", dist)
```

Run the example:

```bash
python demo.py
```

Output files will appear in the `out/` directory.

---

## Unit Tests

Run tests with pytest:

```bash
pytest -q
```

Expected output:

```
2 passed
```

---

## Notes

- Distance-based operations must be performed in a metric CRS (e.g., EPSG:3857 or UTM).
- Input data must follow the GeoJSON specification.
- This library focuses on essential vector operations rather than full GIS functionality.

---

## License

MIT License.