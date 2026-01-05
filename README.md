# geotoolkit

`geotoolkit` is a small Python library for basic vector-based geoprocessing.
It provides utilities for reading and writing GeoJSON data, coordinate transformation between EPSG codes, geometric buffering, clipping, and nearest distance calculations.
The library is lightweight and does not rely on GDAL, making it suitable for environments such as macOS ARM.

---

## Features

### GeoJSON I/O
- `read_geojson(path)` — read GeoJSON into a Python `dict`.
- `write_geojson(obj, path)` — write GeoJSON to disk (pretty-printed).
- `write_csv(data_list, path)` — export a CSV report from a list of dictionaries.

### Coordinate Transformation
- `to_epsg(feature_or_fc, epsg_from, epsg_to)`  
  Converts a geometry / Feature / FeatureCollection between coordinate systems (EPSG codes).

### Geometric Operations
- `buffer(geometry, dist_m)`  
  Creates a buffer around a geometry (distance units depend on the CRS).

- `clip(feature_or_fc, clipper_geom)`  
  Clips a Feature or FeatureCollection using a polygon (intersection).

- `nearest(a_geom, b_geom)`  
  Computes nearest distance and returns nearest points.

- `get_area(geometry)` — area of a geometry.
- `get_length(geometry)` — length/perimeter of a geometry.
- `is_contained(container_geom, content_geom)` — containment test (`contains`).

#### Spatial Indexing & Geometry Extraction (NEW)
- `nearest_optimized(search_geom, target_collection)`  
  Uses `shapely.strtree.STRtree` to quickly find a nearest neighbor geometry from a FeatureCollection.

- `get_centroid(geometry)`  
  Returns the centroid of a geometry (as a GeoJSON Point).

- `get_envelope(geometry)`  
  Returns the minimum bounding rectangle (envelope) of a geometry (as a GeoJSON Polygon).

### Visualization
- `plot_features(feature_collection, title="...", output_path="...")`  
  Saves a PNG plot of a FeatureCollection.

Visualization supports multiple “feature roles” via `feature.properties.type`:
- `Original` — reference polygon outline (black dashed line)
- `Centroid` — derived centroid points (green)
- `Envelope` — derived envelope polygons (orange dash-dot)
- default polygons (e.g., buffer/clip) — filled polygon layer
- default points — input points (red)

---

## Relation to practice lectures

This project is developed based on the coding patterns and examples introduced in the practice lectures of the course.

- Vector data handling and GeoJSON input/output follow the workflows demonstrated in the practice sessions.
- Coordinate reference system transformations and metric-based operations are implemented following the geospatial data handling examples.
- Geometric operations such as buffering, clipping (intersection), and nearest-distance computation are adapted from the shapely-based examples shown in the geo-algorithms practice notebooks.
- The overall project structure, including the Python package layout, demo scripts, unit tests, and documentation, is inspired by the example library development and self-assessment exercises.

> ✅ **Update note (aligned with the current code)**  
> `demo.py` reads `data/sample.geojson` and reprojects it from EPSG:4326 to EPSG:3857 before metric operations. This matters because buffering, area, length, and distance are meaningful only in a metric CRS (meters).

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

- `shapely` (geometry operations, including STRtree spatial indexing)
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
│   ├── viz.py
│   └── __init__.py
│
├── data/
│   └── sample.geojson
│
├── out/                  # generated outputs (created automatically by demo.py)
│
├── tests/
│   ├── test_project.py
│   └── test_analysis.py
│
├── demo.py               # interactive console demo
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

`demo.py` provides an interactive console menu. You can run a single task, or run multiple tasks by entering comma-separated values (e.g., `1,6` or `5,8`).  
It also accepts Chinese commas (`，`) and treats both commas and spaces as separators.

### What happens before the menu appears (global preparation)

When the script starts, it performs a one-time initialization:

1. Ensures the `out/` directory exists.
2. Loads raw data from `data/sample.geojson` (WGS84 lon/lat).
3. Reprojects the data to EPSG:3857 (meters) for metric operations.
4. Extracts:
   - the first `Polygon` geometry as `poly`
   - the first `Point` geometry as `pt`

If initialization fails, the program exits immediately.

### Start

```bash
python demo.py
```

### Menu items

- `[1] Generate Buffer`
- `[2] Clip Features`
- `[3] Calculate Nearest Distance` (standard / brute force, with timing)
- `[4] Geometric Analysis` (perimeter + containment check)
- `[5] Visualize Results` (smart mode with linkage + overlays)
- `[6] Generate Report (Export CSV)` (linked mode)
- `[7] High-Speed Search (STRtree) [NEW!]`
- `[8] Extract Centroids/Envelopes [NEW!]`

Exit by typing any of: `0`, `q`, `quit`, `exit`.

---

### Task 1: Generate Buffer

Creates a buffer around the main polygon.

- Interaction:
  - Prompts for buffer distance in meters (default `500`).
  - Note: the input check uses `str.isdigit()`, so decimals like `12.5` are treated as invalid and will fall back to `500`.
- Output:
  - GeoJSON: `out/buffer_500m.geojson`
  - Console: prints the buffer area (square meters)

> Note: the output filename remains `buffer_500m.geojson` even if you enter a distance other than 500.

---

### Task 2: Clip Features

Clips the full FeatureCollection using a temporary **500m buffer** as the clipper geometry.

- Output:
  - GeoJSON: `out/clipped_features.geojson`

---

### Task 3: Calculate Nearest Distance (Standard / Brute Force)

Computes the nearest distance between `pt` and `poly` using the standard approach.

- Output:
  - Nearest distance (meters in EPSG:3857)
  - Runtime in milliseconds

---

### Task 4: Geometric Analysis

Runs basic geometry checks on a temporary **500m buffer**:

- Perimeter: `get_length(temp_buf)`
- Containment: `is_contained(temp_buf, pt)`

Outputs perimeter (meters) and whether the point is strictly inside the buffer.

---

### Task 5: Visualize Results (Smart Mode with Linkage)

Generates `out/visualization_result.png`.

#### 5.1 Base layer selection (priority order)

1. If `out/clipped_features.geojson` exists → display clipped results
2. Else if `out/buffer_500m.geojson` exists → display buffer results
3. Else → display original reprojected data (`fc_m`)

#### 5.2 Overlay layer (linked to Task 8)

If `out/geo_features.geojson` exists (generated by Task 8), it is loaded and added as an overlay on top of the base map.

#### 5.3 Context layers (when displaying processed results)

If the base layer is Buffer/Clip (i.e., processed results), the visualization also appends:

- The original polygon outline with `properties.type = "Original"` (reference outline)
- All original points (context layer)

---

### Task 6: Generate Report (Export CSV) — Linked Mode

Exports `out/distance_report.csv`.

This report computes, for each target point:

- distance to the original polygon
- whether it lies inside a reference buffer

#### 6.1 Which points are analyzed?

- If `out/clipped_features.geojson` exists → analyze only points from the clipped output
- Otherwise → analyze all points from the original dataset

#### 6.2 Which buffer is used for the `Inside_Buffer` column?

- If `out/buffer_500m.geojson` exists → load it as the reference standard
- Otherwise → use a default `buffer(poly, 500)` as the reference

#### 6.3 CSV columns (exactly as produced)

- `ID` — running index starting at 1
- `Name` — from `properties.name` if present, otherwise `Point_#`
- `Data_Source` — indicates the input set used (clipped vs raw)
- `Distance_to_Polygon` — rounded to 2 decimals
- `Inside_Buffer (<source>)` — `Yes`/`No` (header includes the reference source)

---

### Task 7: High-Speed Search (STRtree Indexing) [NEW!]

Demonstrates a performance comparison between:

1. **Standard search (benchmark):** loops through all features and repeatedly calls `nearest(pt, feature_geometry)`
2. **Optimized search:** calls `nearest_optimized(pt, fc_m)` using `STRtree`

Outputs:

- nearest distance found (meters)
- time comparison (standard vs indexed, milliseconds)
- an “Optimization Factor” (how many times faster)

> Note: This is a demo benchmark; the standard search intentionally loops through the full dataset to simulate heavier work.

---

### Task 8: Extract Centroids/Envelopes [NEW!]

Derives geometric features for each polygon in the dataset:

- centroid (Point) with `properties.type = "Centroid"`
- envelope / bounding rectangle (Polygon) with `properties.type = "Envelope"`

Output:

- GeoJSON: `out/geo_features.geojson` (FeatureCollection of derived features)

Tip: Run Task 8 and then Task 5 to visualize these derived features as an overlay layer.

---

## API Reference (based on the current implementation)

### `geotoolkit.io`

#### `read_geojson(path)`
Reads a GeoJSON file and returns a Python `dict`. Raises `FileNotFoundError` if the file does not exist.

#### `write_geojson(obj, path)`
Writes a GeoJSON `dict` to disk (UTF‑8, indent=2). Creates parent directories automatically.

#### `write_csv(data_list, path)`
Writes a list of dictionaries to a CSV file (UTF‑8).

- If `data_list` is empty, prints a message and returns.
- Uses the keys of the first dictionary as CSV headers.

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
Clips input using a polygon clipper (intersection).

- Input `FeatureCollection` → returns a clipped FeatureCollection (may be empty)
- Input `Feature` → returns a FeatureCollection (consistent output type)
- Input geometry dict → returns an intersection geometry dict

#### `nearest(a_geom, b_geom)`
Returns `(distance, nearest_point_on_a, nearest_point_on_b)`. Distance units depend on CRS.

#### `get_area(geometry)`
Returns the area (units depend on CRS; square meters in metric CRS).

#### `get_length(geometry)`
Returns length/perimeter (units depend on CRS; meters in metric CRS).

#### `is_contained(container_geom, content_geom)`
Returns a boolean indicating whether `container_geom` strictly contains `content_geom`.

#### `nearest_optimized(search_geom, target_collection)` (NEW)
Builds an `STRtree` index from the target FeatureCollection and returns:

- `distance: float`
- `nearest_geom: GeoJSON geometry dict`

#### `get_centroid(geometry)` (NEW)
Returns centroid as a GeoJSON Point geometry dict.

#### `get_envelope(geometry)` (NEW)
Returns envelope (minimum bounding rectangle) as a GeoJSON Polygon geometry dict.

---

### `geotoolkit.viz`

#### `plot_features(feature_collection, title="GeoJSON Plot", output_path="out/plot.png")`
Saves a PNG plot for a FeatureCollection.

- Supports `Point` and `Polygon` geometries.
- Adds grid lines, equal aspect ratio, and EPSG:3857 meter-based axis labels.
- Applies special styles based on `feature.properties.type`:
  - `Original` → black dashed outline
  - `Centroid` → green point
  - `Envelope` → orange dash-dot outline

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
