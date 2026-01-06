Here is the updated `README.md`. I have preserved the original structure and introduction as requested, while strictly updating the feature lists, usage examples, demo workflows, and API references to match the code you provided (specifically the new **Spatial Buffer Analysis**, **World Cities** integration, and **Raster** capabilities).

All content has been converted to English.

```markdown
# geotoolkit

`geotoolkit` is a small Python library for vector-based geospatial processing built around GeoJSON data structures.
It provides a compact set of utilities for reading and writing GeoJSON files, coordinate transformation between EPSG codes, common geometric operations (buffering, clipping, nearest distance), as well as spatial queries, K-nearest-neighbor (KNN) analysis, and radius searches on point data.
The library is lightweight and does not rely on GDAL, making it suitable for environments such as macOS ARM.

> **Note**
> - The statement "does not rely on GDAL" applies primarily to the **vector components**: core dependencies are `shapely` and `pyproj`.
> - The repository also includes `geotoolkit/raster.py` (requiring `rasterio` + `numpy`) for the **raster sampling** demo task. This functionality is imported within a try-except block, so the rest of the library functions correctly even if these optional dependencies are not installed.

---

## Table of Contents

- [Features](#features)
- [Relation to practice lectures](#relation-to-practice-lectures)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [GeoJSON Data Model](#geojson-data-model)
- [Usage Example](#usage-example)
- [Interactive Demo Console (demo.py)](#interactive-demo-console-demopy--recommended-workflow)
  - [Recommended execution order](#recommended-execution-order)
  - [Dependency map](#dependency-map)
  - [Menu items](#menu-items)
  - [Demo output index](#demo-output-index)
- [API Reference (by module)](#api-reference-by-module)
- [Notes & Pitfalls](#notes--pitfalls)
- [Unit Tests](#unit-tests)
- [License](#license)

---

## Features

### GeoJSON I/O
- `read_geojson(path)` — read GeoJSON into a Python `dict`.
- `write_geojson(obj, path)` — write GeoJSON to disk (pretty-printed).
- `write_csv(data_list, path)` — export a CSV report from a list of dictionaries.

### Coordinate Transformation
- `to_epsg(feature_or_fc, epsg_from, epsg_to)`  
  Converts a geometry / Feature / FeatureCollection between coordinate systems (EPSG codes).

> **Implementation note:** Uses `pyproj.Transformer(..., always_xy=True)` + `shapely.ops.transform()`.

### Geometric Operations
- `buffer(geometry, dist_m)` — creates a buffer around a geometry.
- `clip(feature_or_fc, clipper_geom)` — clips a Feature/Collection using a polygon (intersection).
- `nearest(a_geom, b_geom)` — computes nearest distance and returns nearest points (Brute Force).
- `get_area(geometry)` — area of a geometry.
- `get_length(geometry)` — length/perimeter of a geometry.
- `is_contained(container_geom, content_geom)` — strict containment test.

#### Spatial Indexing & Geometry Extraction
- `nearest_optimized(search_geom, target_collection)` — uses `shapely.strtree.STRtree` for fast nearest neighbor search.
- `get_centroid(geometry)` — returns the centroid (GeoJSON Point).
- `get_envelope(geometry)` — returns the MBR (GeoJSON Polygon).
- `get_bbox(geometry)` — returns `(minx, miny, maxx, maxy)`.

### Visualization
- `plot_features(feature_collection, ...)` — saves a PNG plot.
- Supports multiple visualization roles:
    - **Standard**: Red points, Blue polygons.
    - **Analysis**: "Centroid" (Green), "Envelope" (Orange).
    - **Sampled/Query**: "SampledPoint" (Blue dots with text annotation for `raster_value` or `distance`).

### Spatial Query (Point-in-Polygon & Radius Search)
- `tag_points_within(...)` — Tag points with a boolean property if inside a polygon.
- `filter_points_within(...)` — Return only points inside a polygon.
- **[NEW]** `filter_points_by_distance(points_fc, center_coords, radius, ...)`  
  Finds points within a specific radius of a center coordinate. Supports spatial indexing (`STRtree`) for performance.

### K-Nearest Neighbors (KNN)
- `knn_points(points_fc, target_point, k=10, ...)` — Returns top-k nearest points with `distance_m` and `knn_rank` properties.

### Real-World Data Integration (NEW)
- Includes a built-in `WORLD_CITIES` database (dictionary of major cities) for realistic spatial analysis demos.

### Raster Sampling (Optional)
- `sample_raster_at_points(...)` — Samples a raster (e.g., DEM) at point coordinates.
- `generate_synthetic_raster(...)` — Generates a synthetic GeoTIFF for testing.

---

## Relation to practice lectures

This project is developed based on the coding patterns and examples introduced in the practice lectures of the course.

- **Vector handling**: GeoJSON I/O workflows match practice sessions.
- **Projections**: Coordinate transformations follow standard `pyproj` usage.
- **Algorithms**: Buffering, clipping, and distance logic are adapted from `shapely`-based notebooks.
- **Structure**: The package layout, tests, and documentation reflect the library development exercises.

> **Update Note:** `demo.py` automatically reprojects `data/sample.geojson` from EPSG:4326 (Lat/Lon) to EPSG:3857 (Web Mercator) to ensure metric operations (buffer, distance, area) are mathematically valid.

---

## Installation

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate  # Or .venv\Scripts\activate on Windows

```

Install the library in editable mode:

```bash
pip install -e .

```

### Dependencies

Core dependencies (Vector):

* `shapely`
* `pyproj`
* `matplotlib`

Optional dependencies (Raster):

* `rasterio`
* `numpy`

---

## Project Structure

```text
geotoolkit/
│
├── geotoolkit/
│   ├── data/
│   │   └── world_cities.py    # [NEW] Real-world city coordinates
│   ├── io.py
│   ├── project.py
│   ├── analysis.py
│   ├── viz.py
│   ├── query.py               # Includes buffer, clip, and radius search logic
│   ├── knn.py
│   ├── raster.py              # Optional: raster sampling logic
│   └── __init__.py
│
├── data/
│   ├── sample.geojson
│   ├── generated_points.geojson
│   └── sample_dem.tif         # Generated by Task [12] if missing
│
├── out/                       # Generated outputs
│
├── tests/                     # Unit tests
├── demo.py                    # Interactive Console (Main Entry Point)
├── README.md
├── setup.cfg
└── pyproject.toml

```

---

## GeoJSON Data Model

This library operates directly on **GeoJSON dictionaries** (Python `dict`).

* **FeatureCollection**: `{"type": "FeatureCollection", "features": [...]}`
* **Feature**: `{"type": "Feature", "properties": {...}, "geometry": {...}}`
* **Geometry**: `{"type": "Point", "coordinates": [x, y]}`

---

## Usage Example

```python
from geotoolkit.io import read_geojson, write_geojson
from geotoolkit.project import to_epsg
from geotoolkit.analysis import buffer, clip, nearest
from geotoolkit.query import filter_points_within, filter_points_by_distance

# 1. Load and Project Data
fc = read_geojson("data/sample.geojson")
fc_m = to_epsg(fc, 4326, 3857) # Reproject to meters

# 2. Geometric Ops
poly = fc_m["features"][0]["geometry"]
buf = buffer(poly, 500)
clipped = clip(fc_m, buf)

# 3. Spatial Query (Radius Search)
# Find points within 2km of a specific coordinate
center = (260000, 6250000) # Example EPSG:3857 coords
result = filter_points_by_distance(fc_m, center, radius=2000.0, use_index=True)

print(f"Found {len(result['features'])} points within 2km.")

```

Run the interactive demo:

```bash
python demo.py

```

---

## Interactive Demo Console (`demo.py`) — Recommended Workflow

The `demo.py` script provides a robust interactive menu. It supports multi-task execution (e.g., `1,6`) and handles linkage between different analysis tasks.

### Recommended execution order

Here are three common workflows to demonstrate different capabilities:

**Route A — Vector Analysis (Classic)**

1. `1` **Generate Buffer**: Creates `out/buffer_500m.geojson`.
2. `2` **Clip Features**: Clips points to that buffer.
3. `5` **Visualize**: Automatically overlays the clipped points on top of the buffer.
4. `6` **Report**: Generates a CSV report calculating distances for the clipped points.

**Route B — Spatial Buffer Analysis (Real World Data) [NEW]**

1. `13` **Spatial Buffer Analysis**:
* Select **[2] Real World Cities Database**.
* Input a city name (e.g., "Paris, FR") as the center.
* Input a radius (e.g., 100 km).
* Generates `out/query_radius_result.geojson`.


2. `5` **Visualize**: Automatically detects the query result, visualizing the cities found with their distance annotated.
3. `6` **Report**: Generates a CSV report listing the cities found and their distance to the center.

**Route C — Raster Sampling (Advanced)**

1. `12` **Raster Point Sampling**: Generates/Reads a DEM and samples values for all points.
2. `5` **Visualize**: Plots points in blue, labeled with their sampled raster value.
3. `6` **Report**: Adds a "Raster_Value" column to the generated CSV.

### Dependency map

The demo uses a "Linkage" system: output from one task is automatically picked up by subsequent visualization or reporting tasks.

```text
Task [1] Buffer ----------------------> out/buffer_500m.geojson
   |                                        |
   +----------------------------------------+--> Used by Task [5], [6] as context

Task [2] Clip ------------------------> out/clipped_features.geojson
   |                                        |
   +----------------------------------------+--> Priority input for Task [5], [6]

Task [13] Spatial Query (Radius) -----> out/query_radius_result.geojson
   |                                        |
   +----------------------------------------+--> HIGHEST Priority for Task [5], [6]
                                                 (Displays real city names & distances)

Task [12] Raster Sampling ------------> out/sampled_points.geojson
   |                                        |
   +----------------------------------------+--> Used by Task [5] (labels values)
   +----------------------------------------+--> Used by Task [6] (adds CSV column)

```

### Menu items

* `[1] Generate Buffer`
* `[2] Clip Features`
* `[3] Calculate Nearest Distance`
* `[4] Geometric Analysis`
* `[5] Visualize Results` (Smart Mode)
* `[6] Generate Report (Export CSV)`
* `[7] High-Speed Search (STRtree)`
* `[8] Extract Centroids/Envelopes`
* `[9] Batch Query (Generated Points)`
* `[10] Geometry Summary`
* `[11] KNN Top-K Nearest Points`
* `[12] Raster Point Sampling [NEW!]`
* `[13] Spatial Buffer Analysis (Radius Search) [NEW!]`

### Demo output index

| Output file | Generated by | Description |
| --- | --- | --- |
| `out/buffer_500m.geojson` | 1 | Buffer geometry |
| `out/clipped_features.geojson` | 2 | Features inside the buffer |
| `out/geo_features.geojson` | 8 | Centroids and Envelopes |
| `out/query_radius_result.geojson` | 13 | Result of radius search (Real Cities or Points) |
| `out/sampled_points.geojson` | 12 | Points with sampled `raster_value` property |
| `out/visualization_result.png` | 5 | Smart plot of the current analysis state |
| `out/distance_report.csv` | 6 | Detailed CSV report of the active dataset |
| `out/knn_topk.geojson` | 11 | Top-K nearest neighbors results |

---

## API Reference (by module)

<details>
<summary><strong>geotoolkit/io.py</strong></summary>

* **`read_geojson(path)`**: Reads GeoJSON to dict. Raises `FileNotFoundError` if missing.
* **`write_geojson(obj, path)`**: Writes GeoJSON dict to file (UTF-8, indent=2).
* **`write_csv(data_list, path)`**: Writes list of dicts to CSV.

</details>

<details>
<summary><strong>geotoolkit/project.py</strong></summary>

* **`to_epsg(feature_or_fc, epsg_from, epsg_to)`**:
Transforms geometry coordinates between EPSG codes. Supports `Feature`, `FeatureCollection`, or raw `Geometry`.

</details>

<details>
<summary><strong>geotoolkit/analysis.py</strong></summary>

* **`buffer(geometry, dist_m)`**: Returns buffered geometry.
* **`clip(feature_or_fc, clipper_geom)`**: Boolean intersection. Returns `FeatureCollection`.
* **`nearest(a_geom, b_geom)`**: Brute-force nearest point calculation.
* **`nearest_optimized(search_geom, target_collection)`**: STRtree-based nearest neighbor search.
* **`get_area`, `get_length`, `get_centroid`, `get_bbox`, `get_envelope**`: Geometric attribute extractors.

</details>

<details>
<summary><strong>geotoolkit/query.py</strong></summary>

* **`tag_points_within(points_fc, poly, prop="inside", ...)`**:
Adds a boolean property to points indicating containment.
* **`filter_points_within(points_fc, poly, ...)`**:
Returns a new FeatureCollection containing only points inside the polygon.
* **`filter_points_by_distance(points_fc, center_coords, radius, use_index=False)`**:
**[NEW]** Returns a FeatureCollection of points located within `radius` (map units) of `center_coords` (x, y).
* If `use_index=True`, utilizes `STRtree` for performance optimization.
* Adds `distance_to_center` property to results.



</details>

<details>
<summary><strong>geotoolkit/viz.py</strong></summary>

* **`plot_features(feature_collection, title, output_path)`**:
Matplotlib-based visualization. Supports standard styling plus special handling for:
* `_viz_type="SampledPoint"`: Plots point with text annotation (used for Raster and Radius Search results).



</details>

<details>
<summary><strong>geotoolkit/knn.py</strong></summary>

* **`knn_points(points_fc, target_point, k=10, use_index=False)`**:
Returns top-k nearest points with ranking and distance properties.

</details>

<details>
<summary><strong>geotoolkit/raster.py</strong></summary>

* **`sample_raster_at_points(points_fc, raster_path)`**:
Reads a raster file and extracts values at point locations.
* **`generate_synthetic_raster(target_path, bounds)`**:
Creates a test GeoTIFF.

</details>

---

## Notes & Pitfalls

* **Metric System**: Distance-based operations (buffer, radius search, nearest) must be performed in a metric CRS (e.g., EPSG:3857). The demo handles this automatically during initialization.
* **Real World Data**: Task 13 can access the built-in `WORLD_CITIES` database. Note that this task performs a projection from WGS84 to EPSG:3857 in-memory to ensure accurate radius filtering in meters/kilometers.
* **Data Precedence**: If multiple analysis tasks are run (e.g., Clip and Radius Search), Task 5 (Viz) and Task 6 (Report) prioritize the **Radius Search** results as they are considered the most specific "active" dataset.

---

## Unit Tests

If your repository includes `tests/`, you can run:

```bash
pytest -q

```

> Note: `tests/test_raster.py` will be skipped if `rasterio` is not installed.

---

## License

```

MIT License.

```
