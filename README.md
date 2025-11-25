geotoolkit

geotoolkit is a small Python library for basic vector-based geospatial processing.
It provides simple utilities for reading and writing GeoJSON data, performing coordinate system transformations, generating geometric buffers, clipping features, and computing nearest distances between geometries.

The library is lightweight and does not depend on GDAL. It is designed to run reliably on environments such as macOS ARM.

⸻

Features

GeoJSON I/O
	•	Read a GeoJSON file into a Python dictionary
	•	Write a GeoJSON dictionary back to disk

Coordinate System Transformation
	•	Convert geometries, Features, or FeatureCollections between EPSG codes
	•	Based on pyproj and supports any CRS available through PROJ

Geometric Operations
	•	Buffering (in meters, requires metric CRS)
	•	Clipping Features or FeatureCollections using a polygon
	•	Nearest distance computation between geometries

⸻

    Installation

Create and activate a virtual environment:
````markdown
```python
python3 -m venv .venv
source .venv/bin/activate
```
