Here is the **detailed and expanded English version** of the `README.md`.

I have strictly preserved your original text (especially the "Relation to practice lectures" section). I have significantly expanded the **Features**, **Installation**, and **Usage** sections to reflect the new capabilities (CLI, Visualization, CSV Reporting, and Geometric Attributes) in a detailed, professional manner.

---

```markdown
# geotoolkit

`geotoolkit` is a small Python library for basic vector-based geoprocessing.
It provides utilities for reading and writing GeoJSON data, coordinate transformation between EPSG codes, geometric buffering, clipping, nearest distance calculations, **and data visualization**.
The library is lightweight and does not rely on GDAL, making it suitable for environments such as macOS ARM.

---

## Features

### 1. Data Input/Output & Reporting
- **`read_geojson(path)`**: efficiently loads GeoJSON files into Python dictionaries.
- **`write_geojson(obj, path)`**: serializes FeatureCollections or Geometries back to GeoJSON format.
- **`write_csv(data_list, path)`** [New]: Exports attribute data or analysis reports to **CSV format**. This allows analysis results (e.g., distance tables, containment checks) to be easily opened in Excel or other spreadsheet software.

### 2. Coordinate Transformation
- **`to_epsg(feature_or_fc, epsg_from, epsg_to)`**: Converts a geometry, Feature, or FeatureCollection between coordinate systems (e.g., converting WGS84 lat/lon to EPSG:3857 for metric calculations).

### 3. Geometric Operations
- **`buffer(geometry, dist_m)`**: Creates a metric buffer around a geometry (Point, LineString, or Polygon) with a customizable distance.
- **`clip(feature_or_fc, clipper_geom)`**: Clips a Feature or FeatureCollection using a polygon. Returns only the geometric intersection.
- **`nearest(a_geom, b_geom)`**: Computes the nearest Euclidean distance between two geometries and returns the specific nearest coordinates on both shapes.

### 4. Geometric Analysis [New]
- **`get_area(geometry)`**: Calculates the area of a polygon in the projected unit (e.g., square meters).
- **`get_length(geometry)`**: Calculates the perimeter of a polygon or length of a line.
- **`is_contained(container_geom, content_geom)`**: A spatial predicate that returns `True` if a geometry is strictly inside another (e.g., determining if a point lies within a specific buffer zone).

### 5. Visualization [New]
- **`plot_features(feature_collection, ...)`**: Visualizes vector data directly within Python using `matplotlib`.
    - Supports multiple layers (Points, Polygons).
    - Automatically adjusts aspect ratios to prevent map distortion.
    - Differentiates between "Original Data", "Buffers", and "Clipped Results" through logical styling.

---

## Relation to practice lectures

This project is developed based on the coding patterns and examples introduced in the practice lectures of the course.

- Vector data handling and GeoJSON input/output follow the workflows demonstrated in the practice sessions.
- Coordinate reference system transformations and metric-based operations are implemented following the geospatial data handling examples.
- Geometric operations such as buffering, clipping (intersection), and nearest-distance computation are adapted from the shapely-based examples shown in the geo-algorithms practice notebooks.
- The overall project structure, including the Python package layout, demo scripts, unit tests, and documentation, is inspired by the example library development and self-assessment exercises.

For testing, the vector dataset `search_points.geojson` provided in the P3 geoprocessing practice is reused.  
Since it is already provided in a metric coordinate reference system (EPSG:32632), it can be used directly for buffer and nearest-distance computations.

---

## Installation

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate

```

Install the library in editable mode (this installs required dependencies like `shapely` and `pyproj`):

```bash
pip install -e .

```

**Optional:** To use the new visualization features, you must install `matplotlib`:

```bash
pip install matplotlib

```

---

## Project Structure

```
geotoolkit/
│
├── geotoolkit/
│   ├── io.py           # Handles GeoJSON and CSV I/O
│   ├── project.py      # Coordinate projection logic
│   ├── analysis.py     # Core geometric algorithms (Buffer, Clip, Area, etc.)
│   ├── viz.py          # [New] Visualization logic using matplotlib
│   ├── utils.py (optional)
│   └── __init__.py
│
├── data/
│   └── sample.geojson
│
├── out/                # Directory where results (GeoJSON, PNG, CSV) are saved
│
├── tests/
│   ├── test_project.py
│   └── test_analysis.py
│
├── demo.py             # Main entry point: Interactive CLI
├── README.md
├── setup.cfg
└── pyproject.toml

```

---

## Usage Example

The project has been upgraded with an **Interactive Command-Line Interface (CLI)** in `demo.py`. This allows for a continuous workflow where the output of one task (like buffering) can optionally be used by subsequent tasks (like clipping or reporting).

Run the interactive demo:

```bash
python demo.py

```

### The Interactive Menu

Upon running, you will see a menu listing all available operations. You can run a single task or chain multiple tasks together by separating them with commas.

```text
========================================
      GeoToolkit Interactive Console
========================================
 [1] Buffer Analysis
 [2] Clip Features
 [3] Nearest Distance
 [4] Geometric Attributes
 [5] Visualize Results
 [6] Generate Report (CSV)
 [0] Exit
----------------------------------------
Enter selection (e.g., '1,2,5'): 

```

### Task Descriptions & Workflow Logic

1. **Buffer Analysis**:
* Prompts user for a buffer distance (in meters).
* Generates a buffer around the sample polygon.
* Calculates and prints the area of the resulting buffer.
* Saves result to `out/buffer_500m.geojson`.


2. **Clip Features**:
* Uses the buffer (from Task 1) to clip the original features.
* Useful for isolating data within a specific range.
* Saves result to `out/clipped_features.geojson`.


3. **Nearest Distance**:
* Calculates the Euclidean distance between sample points and the polygon.


4. **Geometric Attributes**:
* Demonstrates the new analysis functions: calculates perimeter and checks point-in-polygon containment.


5. **Visualize Results**:
* **Smart Logic**: Automatically detects which files exist.
* If Task 2 was run, it visualizes the **Clipped** result.
* If only Task 1 was run, it visualizes the **Buffer**.
* Always overlays the original points for context.
* Generates `out/visualization_result.png`.


6. **Generate Report (CSV)**:
* Analyzes all points and exports a detailed table to `out/distance_report.csv`.
* **Smart Logic**: If Task 1 was run with a custom distance (e.g., 200m), the report will use that specific distance to determine if points are "Inside" or "Outside" the buffer.



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

* Distance-based operations must be performed in a metric CRS (e.g., EPSG:3857 or UTM).
* Input data must follow the GeoJSON specification.
* This library focuses on essential vector operations rather than full GIS functionality.

---

## License

MIT License.

```

```
