# geotoolkit

`geotoolkit` is a small Python library for basic vector-based geoprocessing.
It provides utilities for reading and writing GeoJSON data, coordinate transformation between EPSG codes, geometric buffering, clipping, and nearest distance calculations.
The library is lightweight and does not rely on GDAL, making it suitable for environments such as macOS ARM.

---

## Features

### GeoJSON I/O
- `read_geojson(path)`
- `write_geojson(obj, path)`
- `write_csv(data_list, path)` (Export a CSV report)

### Coordinate Transformation
- `to_epsg(feature_or_fc, epsg_from, epsg_to)`  
  Converts a geometry, Feature, or FeatureCollection between coordinate systems.

### Geometric Operations
- `buffer(geometry, dist_m)`  
  Creates a (metric) buffer around a geometry.

- `clip(feature_or_fc, clipper_geom)`  
  Clips a Feature or FeatureCollection using a polygon.

- `nearest(a_geom, b_geom)`  
  Computes nearest distance and returns nearest points.

- `get_area(geometry)` (Area calculation)
- `get_length(geometry)` (Length / perimeter calculation)
- `is_contained(container_geom, content_geom)` (Containment check)

### Visualization
- `plot_features(feature_collection, title="...", output_path="...")` (Save a PNG plot)

---

## Relation to practice lectures

This project is developed based on the coding patterns and examples introduced in the practice lectures of the course.

- Vector data handling and GeoJSON input/output follow the workflows demonstrated in the practice sessions.
- Coordinate reference system transformations and metric-based operations are implemented following the geospatial data handling examples.
- Geometric operations such as buffering, clipping (intersection), and nearest-distance computation are adapted from the shapely-based examples shown in the geo-algorithms practice notebooks.
- The overall project structure, including the Python package layout, demo scripts, unit tests, and documentation, is inspired by the example library development and self-assessment exercises.

> ✅ **Update note (aligned with the current code)**  
> `demo.py` reads `data/sample.geojson` and reprojects it from EPSG:4326 to EPSG:3857 before any metric operations. This is important because buffering and distance calculations assume metric units (meters).

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

### Dependencies (based on imports in the code)

Your code currently uses these third‑party libraries:

- `shapely` (geometry operations: buffer / intersection / nearest / area / length / contains)
- `pyproj` (EPSG coordinate transformations)
- `matplotlib` (saving visualizations to PNG)

If your `pyproject.toml`/`setup.cfg` does not yet declare these dependencies, you can install them manually:

```bash
pip install shapely pyproj matplotlib
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

## Interactive Demo Console (`demo.py`) — recommended workflow (matches the current code)

`demo.py` provides an interactive console menu. You can run a single task, or run multiple tasks by entering comma-separated values (e.g., `1,6`).

Start:

```bash
python demo.py
```

You will see a menu with tasks such as:

- `[1] Generate Buffer`
- `[2] Clip Features`
- `[3] Compute Nearest Distance`
- `[4] Geometry Checks (Analysis)`
- `[5] Visualize Results`
- `[6] Export CSV Report`

Exit by typing any of: `0`, `q`, `quit`, `exit`.

### Task 1: Generate Buffer

- Data source: reads `data/sample.geojson`, then projects to EPSG:3857 (meters) before calculations.
- Interaction: prompts for the buffer distance in meters (default is `500`).
- Output:
  - `out/buffer_500m.geojson` (buffer result)
  - Prints the buffer area (square meters) using `get_area()`.

> Note: The output filename is fixed as `buffer_500m.geojson`, but the actual buffer distance comes from your input.

### Task 2: Clip Features

- Clipper geometry: a **fixed 500m buffer** around the original polygon is used as the clipper.
- Input: the projected FeatureCollection `fc_m`.
- Output:
  - `out/clipped_features.geojson`

### Task 3: Compute Nearest Distance

- Computes the nearest distance from the point to the polygon.
- The unit depends on CRS; in EPSG:3857 it is interpreted as meters.
- Output: prints the distance to the console.

### Task 4: Geometry Checks (Analysis)

- Creates a fixed 500m buffer first, then:
  - Computes its perimeter using `get_length()`
  - Checks whether the original point is inside the buffer using `is_contained()`

### Task 5: Visualize Results

The visualization logic automatically chooses what to plot:

- If `out/clipped_features.geojson` exists: plot the clipped results.
- Else if `out/buffer_500m.geojson` exists: plot the buffer result (supports both FeatureCollection and plain Polygon geometry).
- Otherwise: plot the original input data.

Output file:

- `out/visualization_result.png`

On Windows, the script attempts to open the generated image automatically.

> The plot labels use EPSG:3857 meter-based axes.

### Task 6: Export CSV Report

Exports a CSV report of **point-to-original-polygon** distances, including whether each point lies inside a reference buffer.

#### 6.1 Data selection (exactly as implemented)

- Which points are analyzed:
  - If `out/clipped_features.geojson` exists, only points from the clipped output are analyzed.
  - Otherwise, all points from the original input are analyzed.

- Which buffer is used for the `Inside_Buffer` column:
  - If `out/buffer_500m.geojson` exists, it is loaded and used as the reference buffer.
  - Otherwise, a default `buffer(poly, 500)` is used as the reference.

#### 6.2 CSV columns (exactly as produced)

Each point becomes one row, with:

- `ID`: running index starting at 1
- `Name`: from `properties.name` if present, otherwise `Point_1`, `Point_2`, ...
- `Data_Source`: indicates whether the point came from the original data or from clipped output
- `Distance_to_Polygon`: nearest distance to the original polygon (meters in EPSG:3857), rounded to 2 decimals
- `Inside_Buffer (...)`: `Yes`/`No`, with the source of the buffer noted in the header (e.g., default 500m vs loaded from file)

Output file:

- `out/distance_report.csv`

On Windows, the script attempts to open the generated CSV automatically.

---

## API Reference (based on the current implementation)

### `geotoolkit.io`

#### `read_geojson(path)`
Reads a GeoJSON file and returns a Python `dict`. Raises `FileNotFoundError` if the file does not exist.

#### `write_geojson(obj, path)`
Writes a GeoJSON `dict` to disk (UTF‑8, indent=2). Creates parent directories automatically.

#### `write_csv(data_list, path)`
Writes a list of dictionaries to a CSV file.

- If `data_list` is empty, prints a message and returns.
- Uses the keys of the first dictionary as header fields.
- Writes using UTF‑8.

---

### `geotoolkit.project`

#### `to_epsg(feature_or_fc, epsg_from, epsg_to)`
Reprojects GeoJSON objects between EPSG coordinate systems. Supports:

- `FeatureCollection` → returns a new FeatureCollection
- `Feature` → returns a new Feature
- Geometry dict → returns a new geometry dict

Uses `pyproj.Transformer` with `always_xy=True`.

---

### `geotoolkit.analysis`

#### `buffer(geometry, dist_m)`
Buffers a geometry by `dist_m` (units depend on CRS; meters in metric CRS). Returns a GeoJSON geometry dict.

#### `clip(feature_or_fc, clipper_geom)`
Clips input using a polygon clipper.

- Input `FeatureCollection` → returns a clipped FeatureCollection (may be empty)
- Input `Feature` → returns a FeatureCollection (for consistent output type)
- Input geometry dict → returns an intersection geometry dict

#### `nearest(a_geom, b_geom)`
Returns `(distance, nearest_point_on_a, nearest_point_on_b)`. Distance units depend on CRS.

#### `get_area(geometry)`
Returns the area (units depend on CRS; square meters in metric CRS).

#### `get_length(geometry)`
Returns length/perimeter (units depend on CRS; meters in metric CRS).

#### `is_contained(container_geom, content_geom)`
Returns a boolean indicating whether `container_geom` contains `content_geom`.

---

### `geotoolkit.viz`

#### `plot_features(feature_collection, title="GeoJSON Plot", output_path="out/plot.png")`
Saves a PNG plot for a FeatureCollection.

- Supports `Point` and `Polygon`.
- If a polygon has `properties.type == "Original"`, it is emphasized with a dashed outline (to match `demo.py` behavior).
- Axis labels indicate EPSG:3857 meter-based coordinates.

---

## Notes

- Distance-based operations must be performed in a metric CRS (e.g., EPSG:3857 or UTM).
- Input data must follow the GeoJSON specification.
- This library focuses on essential vector operations rather than full GIS functionality.

---

## Unit Tests

If your repository includes `tests/`, you can run:

```bash
pytest -q
```

---

## License

MIT License.
