# geotoolkit

`geotoolkit` is a small Python library for vector-based geospatial processing built around GeoJSON data structures.
It provides a compact set of utilities for reading and writing GeoJSON files, coordinate transformation between EPSG codes, common geometric operations (buffering, clipping, nearest distance), as well as spatial queries and K-nearest-neighbor (KNN) analysis on point data.
The library is lightweight and does not rely on GDAL, making it suitable for environments such as macOS ARM.

> Note  
> - 上述 “does not rely on GDAL” 主要针对 **矢量部分**：核心依赖 `shapely`/`pyproj`。  
> - 仓库中还包含 `geotoolkit/raster.py`（`rasterio` + `numpy`），用于 demo 的 **栅格采样**；该功能在代码中做了 try-import，未安装也不影响其它功能。

---

## Table of Contents

- [Features](#features)
- [Relation to practice lectures](#relation-to-practice-lectures)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [GeoJSON Data Model](#geojson-data-model)
- [Usage Example](#usage-example)
- [Interactive Demo Console (demo.py)](#interactive-demo-console-demopy--recommended-workflow-matches-the-current-code)
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

> Note (from implementation)
> - `read_geojson` raises `FileNotFoundError` if the file does not exist.
> - `write_geojson` creates parent directories automatically and writes UTF-8 (`ensure_ascii=False`, `indent=2`).
> - `write_csv` prints a message and returns if `data_list` is empty; header is taken from the first row’s keys.

### Coordinate Transformation
- `to_epsg(feature_or_fc, epsg_from, epsg_to)`  
  Converts a geometry / Feature / FeatureCollection between coordinate systems (EPSG codes).

> Implementation note  
> Uses `pyproj.Transformer(..., always_xy=True)` + `shapely.ops.transform()`.

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

- `get_bbox(geometry)`  
  Returns bounding box `(minx, miny, maxx, maxy)`.

> Note (important return type)
> - `clip(...)`：
>   - 输入是 `FeatureCollection` → 返回 `FeatureCollection`
>   - 输入是 `Feature` → 返回 `FeatureCollection`（稳定返回类型）
>   - 输入是纯 `Geometry dict` → 返回相交后的 `Geometry dict`

### Visualization
- `plot_features(feature_collection, title="...", output_path="...")`  
  Saves a PNG plot of a FeatureCollection.

Visualization supports multiple “feature roles” via `feature.properties.type`:
- `Original` — reference polygon outline (black dashed line)
- `Centroid` — derived centroid points (green)
- `Envelope` — derived envelope polygons (orange dash-dot)
- default polygons (e.g., buffer/clip) — filled polygon layer
- default points — input points (red)

> Note (from `viz.py`)
> - If `feature.properties._viz_type == "SampledPoint"`: plotted as blue points and annotated with `raster_value`.

### Spatial Query (Point-in-Polygon)
- `tag_points_within(points_fc, polygon_geom, prop="inside", use_index=False, mode="contains")`  
  Tag each point with a boolean property indicating whether it lies inside (or is covered by) the polygon.

- `filter_points_within(points_fc, polygon_geom, use_index=False, mode="contains")`  
  Return only the point features that lie inside (or are covered by) the polygon.

> Both functions can optionally use a Shapely `STRtree` spatial index (`use_index=True`) to speed up queries on large point sets.

### K-Nearest Neighbors (KNN)
- `knn_points(points_fc, target_point_geom, k=10, use_index=False)`  
  Return the top-k nearest point features to a target point, with `distance_m` and `knn_rank` added to properties.

### Raster Sampling (OPTIONAL, in codebase)
- `sample_raster_at_points(points_fc, raster_path)`  
  Samples a raster at point coordinates and writes `properties["raster_value"]` into returned features.

- `generate_synthetic_raster(target_path, bounds, resolution=10.0)`  
  Generates a synthetic GeoTIFF for testing/demo.

> Note  
> - `raster.py` requires `rasterio` and `numpy` and is not declared in `setup.cfg` dependencies.

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

### Dependencies (from `setup.cfg` + runtime imports)

Declared in `setup.cfg`:

- `shapely`
- `pyproj`
- `pandas`
- `matplotlib`

Optional (only for raster sampling in demo / tests):

```bash
pip install rasterio numpy
```

---

## Project Structure

```text
geotoolkit/
│
├── geotoolkit/
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

## GeoJSON Data Model

This library operates directly on **GeoJSON dictionaries** (Python `dict`) without requiring GDAL.

Accepted objects:

- **Geometry**
  ```json
  {"type":"Point","coordinates":[x,y]}
  ```

- **Feature**
  ```json
  {"type":"Feature","properties":{...},"geometry":{...}}
  ```

- **FeatureCollection**
  ```json
  {"type":"FeatureCollection","features":[...]}
  ```

> CRS reminder  
> Distance-based operations require a metric CRS. `demo.py` uses EPSG:3857.

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

---

### Recommended execution order

下面给你两条“最常用、最稳”的执行路线（都严格对应 `demo.py` 的真实联动方式）：

**Route A — 纯矢量（第一次体验推荐）**
1. `1` 生成 buffer（产生 `out/buffer_500m.geojson`）
2. `2` 裁剪（产生 `out/clipped_features.geojson`）
3. `8` 生成 centroid/envelope（产生 `out/geo_features.geojson`）
4. `5` 可视化（自动叠加前述产物）
5. `6` 生成距离报告（会自动优先使用 clip 的点；buffer 作为 inside 判断标准）
6. `10` 生成 bbox/centroid/area/length 汇总 CSV

**Route B — 点集查询 & KNN（性能/算法展示）**
1. `9` 批量点-in-buffer（baseline vs index 对比 + 输出 inside 点图）
2. `11` KNN top-k（输出 `out/knn_topk.geojson` + `out/knn_topk.png`）
3. （可选）`7` STRtree 最近搜索性能对比

**Route C — 栅格采样联动（可选）**
1. `12` 栅格采样（输出 `out/sampled_points.geojson`）
2. `5` 可视化（会识别采样点并标注 `raster_value`）
3. `6` 报告导出（会优先分析 sampled_points，并附加 `Raster_Value` 列）

> Note (代码小细节，按真实行为说明)
> - Task `[1]`：即使输入距离不是 500，输出文件名仍固定为 `out/buffer_500m.geojson`（代码如此写死）。
> - Task `[9] / [10] / [11]`：函数内部打印的 “Executing [x] ...” 文案编号与菜单键不完全一致（属于打印文案遗留），**以菜单显示的编号为准**。

---

### Dependency map

下面是一个“依赖/联动图”（**不是强依赖**，而是“有了哪些输出，哪些任务会自动利用它们”）：

```text
Global init (always):
  data/sample.geojson  --to_epsg-->  fc_m, poly, pt

Task [1] buffer  ---------------------> out/buffer_500m.geojson
   |                                        |
   |                                        +--> Task [6] uses it as Inside_Buffer standard (if exists)
   |                                        +--> Task [5] can display it as base layer (if no clip)
   |
Task [2] clip  -----------------------> out/clipped_features.geojson
   |                                        |
   |                                        +--> Task [5] prefers it as base layer (highest priority)
   |                                        +--> Task [6] prefers its points as report input (if no sampled points)

Task [8] centroid/envelope -----------> out/geo_features.geojson
   |
   +----------------------------------------> Task [5] overlays it (if exists)

Task [12] raster sampling ------------> out/sampled_points.geojson
   |
   +----------------------------------------> Task [5] overlays + labels raster_value
   +----------------------------------------> Task [6] becomes highest-priority report input + adds Raster_Value

Task [9] batch query (generated points) --> tagged/inside geojson + png (self-contained, no need Task [1])
Task [11] knn top-k (generated points) ----> knn_topk.geojson + knn_topk.png (self-contained; uses buffer only for context)
Task [7] STRtree benchmark ----------------> console output only
```

---

### Start

```bash
python demo.py
```

### Menu items

（以下菜单项与 `demo.py` 的 `MENU` 字典一致）

- `[1] Generate Buffer`
- `[2] Clip Features`
- `[3] Calculate Nearest Distance`
- `[4] Geometric Analysis`
- `[5] Visualize Results`
- `[6] Generate Report (Export CSV)`
- `[7] High-Speed Search (STRtree) `
- `[8] Extract Centroids/Envelopes `
- `[9] Batch Query (Generated Points) [Baseline vs Index]`
- `[10] Geometry Summary (bbox / centroid)`
- `[11] KNN Top-K Nearest Points`
- `[12] Raster Point Sampling [NEW!]`

Exit by typing any of: `0`, `q`, `quit`, `exit`.

---

### Demo output index

> 只列出 `demo.py` 实际会写到 `out/` 的文件（按真实文件名），并标注由哪些任务产生/影响。

| Output file | Generated by | Used/overlaid by | Description |
|---|---:|---:|---|
| `out/buffer_500m.geojson` | 1 | 5, 6 | buffer 结果（文件名固定） |
| `out/clipped_features.geojson` | 2 | 5, 6 | clip 后 FeatureCollection |
| `out/geo_features.geojson` | 8 | 5 | centroid + envelope 派生要素 |
| `out/visualization_result.png` | 5 | — | 智能模式可视化（自动选择 base layer + overlays） |
| `out/distance_report.csv` | 6 | — | 距离/inside 报告（可附 Raster_Value） |
| `out/generated_points_tagged.geojson` | 9 | — | generated_points 加 inside 标记（index 版本输出） |
| `out/generated_points_inside_buffer.geojson` | 9 | — | inside/covers 的点集 |
| `out/generated_points_inside_buffer.png` | 9 | — | inside 点集 + polygon/buffer 上下文可视化 |
| `out/geometry_summary.csv` | 10 | — | bbox/centroid/area/length 汇总 |
| `out/knn_topk.geojson` | 11 | — | top-k 最近点（distance_m + knn_rank） |
| `out/knn_topk.png` | 11 | — | KNN 专用绘图（plot_knn） |
| `out/sampled_points.geojson` | 12 | 5, 6 | 采样点集（properties 含 raster_value） |

---

## API Reference (by module)

> Tip  
> 下面所有信息都来自当前仓库代码的函数签名与实现行为；为了美观，按模块折叠展示。

<details>
<summary><strong>geotoolkit/io.py</strong></summary>

### `read_geojson(path)`
**Signature**
- `read_geojson(path: str | pathlib.Path) -> dict`

**Parameters**
- `path`: GeoJSON 文件路径

**Returns**
- GeoJSON as Python `dict`

**Raises**
- `FileNotFoundError`: 文件不存在

---

### `write_geojson(obj, path)`
**Signature**
- `write_geojson(obj: dict, path: str | pathlib.Path) -> None`

**Parameters**
- `obj`: GeoJSON dict
- `path`: 输出路径（会自动创建父目录）

**Returns**
- `None`

**Side effects**
- 写文件：UTF-8，`indent=2`，`ensure_ascii=False`

---

### `write_csv(data_list, path)`
**Signature**
- `write_csv(data_list: list[dict], path: str) -> None`

**Parameters**
- `data_list`: list of dict（第一条的 keys 作为表头）
- `path`: 输出 CSV 路径

**Returns**
- `None`

**Behavior**
- `data_list` 为空：打印 `"No data to write to CSV"` 并返回
- 正常写入：打印 `" -> CSV file saved: ..."`
- 异常：打印 `"[Error] Failed to write CSV: ..."`

</details>

<details>
<summary><strong>geotoolkit/project.py</strong></summary>

### `to_epsg(feature_or_fc, epsg_from, epsg_to)`
**Signature**
- `to_epsg(feature_or_fc: dict, epsg_from: int, epsg_to: int) -> dict`

**Parameters**
- `feature_or_fc`: GeoJSON `FeatureCollection` / `Feature` / raw `Geometry dict`
- `epsg_from`: source EPSG code (e.g., `4326`)
- `epsg_to`: target EPSG code (e.g., `3857`)

**Returns**
- 同类型返回：
  - 输入 `FeatureCollection` → 输出 `FeatureCollection`
  - 输入 `Feature` → 输出 `Feature`
  - 输入 `Geometry dict` → 输出 `Geometry dict`

**Notes**
- 内部使用 `Transformer.from_crs(..., always_xy=True)`，确保按 (x,y) 解释坐标。

</details>

<details>
<summary><strong>geotoolkit/analysis.py</strong></summary>

### `buffer(geometry, dist_m)`
**Signature**
- `buffer(geometry: dict, dist_m: float) -> dict`

**Parameters**
- `geometry`: GeoJSON geometry dict
- `dist_m`: buffer 距离（单位取决于 CRS；EPSG:3857 下为米）

**Returns**
- buffered geometry as GeoJSON dict

---

### `clip(feature_or_fc, clipper_geom)`
**Signature**
- `clip(feature_or_fc: dict, clipper_geom: dict) -> dict`

**Parameters**
- `feature_or_fc`: `FeatureCollection` / `Feature` / raw `Geometry dict`
- `clipper_geom`: polygon geometry dict（作为裁剪面）

**Returns**
- 若输入是 `FeatureCollection` → `FeatureCollection`
- 若输入是 `Feature` → `FeatureCollection`（稳定返回类型）
- 若输入是 raw `Geometry dict` → intersection 后的 `Geometry dict`

**Notes**
- 若无相交：
  - `FeatureCollection` 情况：返回 `{"type":"FeatureCollection","features":[]}`

---

### `nearest(a_geom, b_geom)`
**Signature**
- `nearest(a_geom: dict, b_geom: dict) -> (float, dict, dict)`

**Returns**
- `(distance, nearest_point_on_a, nearest_point_on_b)`
- `nearest_point_on_*` 是 GeoJSON `Point` dict

---

### `get_area(geometry)`
**Signature**
- `get_area(geometry: dict) -> float`

**Returns**
- `shape(geometry).area`

---

### `get_length(geometry)`
**Signature**
- `get_length(geometry: dict) -> float`

**Returns**
- `shape(geometry).length`

---

### `is_contained(container_geom, content_geom)`
**Signature**
- `is_contained(container_geom: dict, content_geom: dict) -> bool`

**Behavior**
- `shape(container).contains(shape(content))`（严格 contains；边界不算 inside）

---

### `nearest_optimized(search_geom, target_collection)`
**Signature**
- `nearest_optimized(search_geom: dict, target_collection: dict) -> (float, dict)`

**Parameters**
- `search_geom`: GeoJSON geometry dict（用于查询）
- `target_collection`: GeoJSON FeatureCollection（从中找最近 geometry）

**Returns**
- `(distance, nearest_geom)`
- `nearest_geom` 是目标集合中最近几何的 GeoJSON geometry dict

**Notes**
- 内部构建 `targets = [shape(f["geometry"]) for f in target_collection["features"]]`
- 使用 `STRtree(targets).nearest(search_shape)` 获取最近项索引

---

### `get_bbox(geometry)`
**Signature**
- `get_bbox(geometry: dict) -> (minx, miny, maxx, maxy)`

**Returns**
- `shape(geometry).bounds`

---

### `get_centroid(geometry)`
**Signature**
- `get_centroid(geometry: dict) -> dict`

**Returns**
- centroid as GeoJSON `Point` dict

---

### `get_envelope(geometry)`
**Signature**
- `get_envelope(geometry: dict) -> dict`

**Returns**
- envelope as GeoJSON `Polygon` dict

</details>

<details>
<summary><strong>geotoolkit/query.py</strong></summary>

### `tag_points_within(points_fc, polygon_geom, prop="inside", use_index=False, mode="contains")`
**Signature**
- `tag_points_within(points_fc: dict, polygon_geom: dict, prop: str="inside", use_index: bool=False, mode: str="contains") -> dict`

**Parameters**
- `points_fc`: FeatureCollection（只处理其中 `Point` features）
- `polygon_geom`: Polygon / MultiPolygon geometry dict
- `prop`: 写入到 properties 的布尔字段名
- `use_index`: 是否使用 `STRtree`（加速候选筛选）
- `mode`:
  - `"contains"`：严格 inside（边界不算）
  - `"covers"`：包含边界

**Returns**
- FeatureCollection（只包含点要素；properties 复制后追加 `prop`）

**Raises**
- `ValueError`: `mode` 非法，或 `points_fc` 不是 FeatureCollection

---

### `filter_points_within(points_fc, polygon_geom, use_index=False, mode="contains")`
**Signature**
- `filter_points_within(points_fc: dict, polygon_geom: dict, use_index: bool=False, mode: str="contains") -> dict`

**Returns**
- FeatureCollection（仅 inside/covers 的点）

**Notes**
- 内部先调用 `tag_points_within(..., prop="_inside")`
- 再过滤 `_inside == True` 并移除该临时字段

</details>

<details>
<summary><strong>geotoolkit/knn.py</strong></summary>

### `knn_points(points_fc, target_point_geom, k=10, use_index=False)`
**Signature**
- `knn_points(points_fc: dict, target_point_geom: dict, k: int=10, use_index: bool=False) -> dict`

**Parameters**
- `points_fc`: FeatureCollection（只考虑其中 `Point` features）
- `target_point_geom`: `Point` geometry dict
- `k`: top-k（必须 > 0）
- `use_index`: 是否使用 `STRtree` 做候选点半径扩张筛选（Shapely 2.x 语义：query 返回 indices）

**Returns**
- FeatureCollection（top-k 点要素，每条追加 properties）：
  - `distance_m`: 到 target 的距离
  - `knn_rank`: 1..k 排名

**Raises**
- `ValueError`: `k <= 0` 或 target 不是 Point 或输入不是 FeatureCollection

</details>

<details>
<summary><strong>geotoolkit/viz.py</strong></summary>

### `plot_features(feature_collection, title="GeoJSON Plot", output_path="out/plot.png")`
**Signature**
- `plot_features(feature_collection: dict, title: str="GeoJSON Plot", output_path: str="out/plot.png") -> None`

**Behavior**
- 支持 `Point` / `Polygon`
- `properties.type` 影响样式：`Original / Centroid / Envelope`
- `properties._viz_type == "SampledPoint"`：绘制并标注 `raster_value`

**Side effects**
- 写 PNG 到 `output_path` 并打印保存提示

</details>

<details>
<summary><strong>geotoolkit/raster.py (optional)</strong></summary>

> Requires: `rasterio`, `numpy`

### `sample_raster_at_points(points_fc, raster_path)`
**Signature**
- `sample_raster_at_points(points_fc: dict, raster_path: str) -> dict`

**Parameters**
- `points_fc`: FeatureCollection（只处理 Point features）
- `raster_path`: `.tif` 等栅格路径

**Returns**
- FeatureCollection（每个点 properties 增加 `raster_value: float`）

**Behavior**
- 若栅格打不开：打印错误并直接返回原 `points_fc`
- 默认按单波段 raster 取 band1

---

### `generate_synthetic_raster(target_path, bounds, resolution=10.0)`
**Signature**
- `generate_synthetic_raster(target_path: str, bounds: (minx,miny,maxx,maxy), resolution: float=10.0) -> None`

**Behavior**
- 在给定 bounds 基础上 pad 100m
- 生成简单的 DEM-like 梯度数据（Z = X + Y）
- 写 GeoTIFF（crs 固定 `EPSG:3857`）

</details>

---

## Notes & Pitfalls

- Distance-based operations must be performed in a metric CRS (e.g., EPSG:3857 or UTM).
- Input data must follow the GeoJSON specification.
- This library focuses on essential vector operations rather than full GIS functionality.

> Practical notes (strictly from current code)
> - `demo.py` 的报告任务 `[6]` 会按优先级选择分析点集：
>   1) `out/sampled_points.geojson`（若存在，且会多一列 `Raster_Value`）
>   2) `out/clipped_features.geojson` 中的点（若存在）
>   3) 否则使用初始化得到的 `fc_m` 中的点
> - `[9]` 批量点查询、`[11]` KNN 使用的是 `data/generated_points.geojson`（代码假设它已经是 EPSG:3857）。

---

## Unit Tests

If your repository includes `tests/`, you can run:

```bash
pytest -q
```

> Note
> - `tests/test_raster.py` will be skipped if `rasterio` is not installed.

---

## License

MIT License.
