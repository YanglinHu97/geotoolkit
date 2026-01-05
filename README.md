# geotoolkit

`geotoolkit` is a small Python library for vector-based geospatial processing built around GeoJSON data structures.
It provides a compact set of utilities for reading and writing GeoJSON files, coordinate transformation between EPSG codes, common geometric operations (buffering, clipping, nearest distance), as well as spatial queries and K-nearest-neighbor (KNN) analysis on point data.
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

### Spatial Query (Point-in-Polygon)
- `tag_points_within(points_fc, polygon_geom, prop="inside", use_index=False, mode="contains")`  
  Tag each point with a boolean property indicating whether it lies inside (or is covered by) the polygon.

- `filter_points_within(points_fc, polygon_geom, use_index=False, mode="contains")`  
  Return only the point features that lie inside (or are covered by) the polygon.

> Both functions can optionally use a Shapely `STRtree` spatial index (`use_index=True`) to speed up queries on large point sets.

### K-Nearest Neighbors (KNN)
- `knn_points(points_fc, target_point_geom, k=10, use_index=False)`  
  Return the top‑k nearest point features to a target point, with `distance_m` and `knn_rank` added to properties.
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
│   ├── viz.py
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
from geotoolkit.knn import knn_points
from geotoolkit.query import filter_points_within

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

# Filtering points that lie inside a given polygon
points = read_geojson("data/generated_points.geojson")
polygon = read_geojson("data/sample.geojson")["features"][0]["geometry"]
inside_points = filter_points_within(points, polygon, use_index=True)

# K-nearest-neighbor (KNN) queries can be used to find the closest points to a target geometry.
points = read_geojson("data/generated_points.geojson")
target = read_geojson("data/sample.geojson")["features"][1]["geometry"]
topk = knn_points(points, target, k=10, use_index=True)

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
- `[7] Batch Query (Generated Points) [Baseline vs Index]`
- `[8] Geometry Summary (bbox / centroid)`
- `[9] KNN Top-K Nearest Points`

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

### Task 7: Batch Query on Generated Points (Baseline vs Spatial Index)

This task demonstrates **point-in-polygon** queries on a larger point set (e.g., 1000 points) and compares:

 - **Baseline** (`use_index=False`): checks each point against the polygon (O(n))
 - **Indexed** (`use_index=True`): uses a Shapely `STRtree` to reduce candidate checks

 **Input**

 - `data/generated_points.geojson` (expected to already be in **EPSG:3857**)
 - Reference geometry: a 500m buffer around the original polygon from `data/sample.geojson`

 **What it runs**

 - `tag_points_within(..., use_index=False)` + `filter_points_within(..., use_index=False, mode="covers")`
 - `tag_points_within(..., use_index=True)`  + `filter_points_within(..., use_index=True, mode="covers")`

 **Outputs**

 - `out/generated_points_tagged.geojson` (all points + an `inside` boolean property)
 - `out/generated_points_inside_buffer.geojson` (only inside/covers points)
 - `out/generated_points_inside_buffer.png` (visualization of inside points + original polygon + buffer)

 ---

 ### Task 8: Geometry Summary (bbox + centroid + area/length)

This task generates a compact **CSV summary** for key geometries using:

 - `get_bbox(geometry)` → `(minx, miny, maxx, maxy)`
 - `get_centroid(geometry)` → centroid as a GeoJSON `Point`
 - `get_area(geometry)` / `get_length(geometry)` for polygon-like geometries

 **Geometries summarized**

 - `original_polygon` (from `data/sample.geojson`, projected to EPSG:3857)
 - `buffer_500m` (buffer around the polygon)
 - `generated_points` (treated as a `MultiPoint` collection; area/length are not applicable)

 **Output**

 - `out/geometry_summary.csv`

 ---

 ### Task 9: KNN — Find K Nearest Points to the Target Point

This task finds the **top‑k nearest points** (from `data/generated_points.geojson`) to a **target point** (the point contained in `data/sample.geojson`, projected to EPSG:3857).

 - Supports baseline scan (`use_index=False`) or an accelerated candidate search using `STRtree` (`use_index=True`).
 - Each returned point feature is enriched with:
   - `distance_m`: distance to the target point (meters in EPSG:3857)
   - `knn_rank`: 1..k rank

 **Outputs**

 - `out/knn_topk.geojson` (top‑k points with rank and distance)
 - `out/knn_topk.png` (standalone plot highlighting polygon, buffer, target point, and top‑k points)

 > Tip: for the visualization in Task 9, the script generates a dedicated figure (`plot_knn`) rather than reusing Task 5’s “smart mode” plot, so the top‑k result is always clearly highlighted.


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

#### `get_bbox(geometry)`
Returns `(minx, miny, maxx, maxy)` for a GeoJSON geometry, based on Shapely `bounds`.

#### `get_centroid(geometry)`
Returns the centroid of a GeoJSON geometry as a GeoJSON `Point` geometry dict.

---

### `geotoolkit.viz`

#### `plot_features(feature_collection, title="GeoJSON Plot", output_path="out/plot.png")`
Saves a PNG plot for a FeatureCollection.

- Supports `Point` and `Polygon`.
- If a polygon has `properties.type == "Original"`, it is emphasized with a dashed outline (to match `demo.py` behavior).
- Axis labels indicate EPSG:3857 meter-based coordinates.


---

### `geotoolkit.query`

#### `tag_points_within(points_fc, polygon_geom, prop="inside", use_index=False, mode="contains")`
Tags each point feature with a boolean property (default: `inside`) indicating whether the point is inside the polygon.

- `mode="contains"`: strict (boundary is **not** considered inside)
- `mode="covers"`: inclusive (boundary **is** considered inside)
- `use_index=True`: uses Shapely `STRtree` to reduce candidate checks

#### `filter_points_within(points_fc, polygon_geom, use_index=False, mode="contains")`
Returns a FeatureCollection containing only point features that are inside/covers the polygon.

---

### `geotoolkit.knn`

#### `knn_points(points_fc, target_point_geom, k=10, use_index=False)`
Returns a FeatureCollection containing the top‑k nearest point features to the target point.

Each returned feature gets:
- `distance_m`: distance to the target (units depend on CRS; meters in EPSG:3857)
- `knn_rank`: rank from 1..k

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
