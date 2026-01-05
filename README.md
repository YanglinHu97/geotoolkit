
# geotoolkit

`geotoolkit` is a lightweight Python library designed for basic vector-based geospatial processing. It provides utilities for essential operations such as:

- **Reading and writing GeoJSON** data
- **Coordinate transformations** between EPSG codes
- **Geometric operations**, such as buffering, clipping, and nearest distance calculations

The library is deliberately kept minimalistic and **does not rely on the complex GDAL library**, which makes it especially suitable for environments such as macOS ARM, where installing GDAL might be cumbersome or impractical. It is designed to be easy to use and fast for typical geospatial operations in Python.

---

## Table of Contents

1. [Features](#features)
2. [Installation](#installation)
3. [Dependencies](#dependencies)
4. [Usage](#usage)
   1. [Reading and Writing GeoJSON](#reading-and-writing-geojson)
   2. [Coordinate Transformation](#coordinate-transformation)
   3. [Geometric Operations](#geometric-operations)
5. [Testing](#testing)
6. [Directory Structure](#directory-structure)
7. [License](#license)
8. [Contributing](#contributing)
9. [Acknowledgements](#acknowledgements)

---

## Features

`geotoolkit` offers a selection of tools for geospatial data handling and analysis:

### GeoJSON I/O

`geotoolkit` provides convenient functions to read and write **GeoJSON** data, which is a widely used format for encoding a variety of geographic data structures.

- **`read_geojson(path)`**  
  Reads GeoJSON data from the given file path and returns it as a Python `dict`. This function is useful for loading geospatial data stored in GeoJSON format for further processing in Python.

  Example:
  ```python
  geo_data = read_geojson('path/to/your/file.geojson')
  ```

- **`write_geojson(obj, path)`**  
  Writes a Python object (usually a `dict` containing geospatial data) to a GeoJSON file at the specified path. This function can be used to save processed or generated geospatial data back into a GeoJSON file for future use or sharing.

  Example:
  ```python
  write_geojson(geo_data, 'path/to/output.geojson')
  ```

### Coordinate Transformation

Geospatial data often comes in different coordinate reference systems (CRS). `geotoolkit` allows for easy transformation between different EPSG codes.

- **`transform_coordinates(geometry, from_epsg, to_epsg)`**  
  Transforms the coordinates of a given geometry from one EPSG code to another. EPSG codes represent different spatial reference systems (e.g., EPSG:4326 for WGS84, EPSG:3857 for Web Mercator). This function supports transforming any geometry between these systems.

  Example:
  ```python
  transformed_geometry = transform_coordinates(geometry, from_epsg=4326, to_epsg=3857)
  ```

### Geometric Operations

Perform common geometric operations directly on geometries with the help of `geotoolkit`:

- **`buffer(geometry, distance)`**  
  Creates a buffer around the input geometry by a given distance. A buffer represents a zone around a geometry, which is often used in proximity analysis, to find areas within a certain distance from a given shape.

  Example:
  ```python
  buffered_geometry = buffer(geometry, distance=1000)  # Buffer in meters
  ```

- **`clip(geometry, boundary)`**  
  Clips a geometry to a specified boundary (typically a polygon). This operation is commonly used to restrict geometries to a particular area or region of interest. The clipping geometry serves as the boundary that the input geometry will be clipped to.

  Example:
  ```python
  clipped_geometry = clip(geometry, boundary)
  ```

- **`nearest_distance(geometry1, geometry2)`**  
  Computes the shortest distance between two geometries. This can be useful in a variety of situations, such as determining the distance between points, between a point and a polygon, or even between two polygons.

  Example:
  ```python
  distance = nearest_distance(geometry1, geometry2)
  ```

---

## Installation

To install the `geotoolkit` library and its dependencies, simply run the following command in your terminal:

```bash
pip install shapely matplotlib rasterio pyproj numpy geotoolkit
```

This will install the latest stable version of `geotoolkit` along with its required dependencies.

If you're working in a specific environment (like a virtual environment), make sure that the environment is activated before running the install command.

---

## Dependencies

`geotoolkit` has a few dependencies that are automatically installed when you install the library via `pip`:

- **`numpy`**  
  A core dependency for handling numerical operations, especially for matrix and array-based computations that are common in geometric transformations and distance calculations.

- **`shapely`**  
  Provides efficient geometric operations, such as buffering and clipping. It's a key component for working with geometries in `geotoolkit`.

- **`pyproj`**  
  A Python interface to PROJ, which allows for coordinate transformation between different EPSG codes. It supports converting geospatial data between different coordinate systems.

---

## Usage

Once installed, `geotoolkit` can be used easily in your Python scripts or interactive Python sessions.

### Reading and Writing GeoJSON

GeoJSON is a popular format for storing and exchanging geospatial data. Use the following functions to read and write GeoJSON files:

```python
from geotoolkit import read_geojson, write_geojson

# Reading GeoJSON data from a file
geo_data = read_geojson('path/to/your/file.geojson')

# Writing GeoJSON data to a new file
write_geojson(geo_data, 'path/to/output.geojson')
```

### Coordinate Transformation

You can transform geometries from one spatial reference system (EPSG) to another using the `transform_coordinates` function:

```python
from geotoolkit import transform_coordinates

# Example: Transforming coordinates from EPSG:4326 (WGS 84) to EPSG:3857 (Web Mercator)
transformed_geometry = transform_coordinates(geometry, from_epsg=4326, to_epsg=3857)
```

### Geometric Operations

You can perform several geometric operations, such as buffering, clipping, and finding nearest distances, using the following functions:

```python
from geotoolkit import buffer, clip, nearest_distance

# Buffering a geometry by a specified distance (in meters)
buffered_geometry = buffer(geometry, distance=1000)

# Clipping a geometry to a boundary (e.g., polygon)
clipped_geometry = clip(geometry, boundary)

# Calculating the nearest distance between two geometries
distance = nearest_distance(geometry1, geometry2)
```

---

## Testing

To test `geotoolkit` and ensure all functionality is working as expected, navigate to the project directory and run the following command:

```bash
pytest
```

This command will run all the tests in the `tests/` folder. It is highly recommended to run the tests after making any changes to ensure that everything is functioning as intended.

---

## Directory Structure

The project is organized as follows:

```plaintext
geotoolkit/
│
├── geotoolkit/
│   ├── data/
│      ├── world_cities.py
│   ├── io.py
│   ├── project.py
│   ├── analysis.py
│   ├── viz.py
│   ├── query.py
│   ├── knn.py
│   ├── raster.py              # optional: requires rasterio + numpy
│   └── __init__.py
│
├── data/
│   ├── sample.geojson
│   ├── generated_points.geojson
│   ├── search_points.geojson
│   └── sample_dem.tif          # used by demo task [12]
│
├── out/                         # generated outputs (created automatically by demo.py)
│
├── tests/
│   ├── test_project.py
│   ├── test_analysis.py
│   ├── test_query.py
│   ├── test_knn.py
│   ├── test_practice_data.py
│   └── test_raster.py           # skipped if rasterio not installed
│
├── demo.py
├── README.md
├── setup.cfg
└── pyproject.toml
```

---

## License

`geotoolkit` is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for more details.

---

## Contributing

We welcome contributions to `geotoolkit`. If you'd like to contribute, follow these steps:

1. **Fork** the repository.
2. **Create a new branch** for your feature or bug fix.
3. **Make your changes** and ensure all tests pass.
4. **Submit a pull request** with a description of the changes you've made.

Before contributing, make sure to run the tests to confirm that everything works as expected:

```bash
pytest
```

---

## Acknowledgements

We would like to acknowledge the creators of the libraries and tools that `geotoolkit` depends on:

- **`numpy`** – For numerical computing and array operations.
- **`shapely`** – For geometric operations.
- **`pyproj`** – For coordinate transformations.

These libraries enable `geotoolkit` to provide efficient geospatial processing with minimal external dependencies.

---

### Thank You for Using `geotoolkit`!

We hope `geotoolkit` serves your geospatial processing needs effectively. If you have any feedback, feature requests, or encounter any issues, please open an issue in the [GitHub repository](https://github.com/yourusername/geotoolkit).
