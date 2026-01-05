import sys
import os
import json
import time
import matplotlib.pyplot as plt
from geotoolkit.io import read_geojson, write_geojson, write_csv
from geotoolkit.project import to_epsg
from geotoolkit.analysis import (
    buffer, clip, nearest,
    get_area, get_length, is_contained,
    nearest_optimized,
    get_bbox, get_centroid, get_envelope
)

from geotoolkit.viz import plot_features
from geotoolkit.query import tag_points_within, filter_points_within
from geotoolkit.knn import knn_points
from shapely.geometry import shape

# [NEW] Import raster module safely
try:
    from geotoolkit.raster import sample_raster_at_points, generate_synthetic_raster
    HAS_RASTERIO = True
except ImportError:
    HAS_RASTERIO = False


# ==========================================
# 1. Global Preparation Stage
# ==========================================
print("Initializing data, please wait...")
try:
    # Ensure the output directory exists
    if not os.path.exists("out"):
        os.makedirs("out")
        
    # Load the raw data (WGS84 Lat/Lon)
    fc = read_geojson("data/sample.geojson")
    
    # Project data to a metric system (EPSG:3857) so we can calculate distances in meters
    fc_m = to_epsg(fc, 4326, 3857)
    
    # Extract the main Polygon and Point geometry for use in tasks
    poly = [f for f in fc_m["features"] if f["geometry"]["type"] == "Polygon"][0]["geometry"]
    pt = [f for f in fc_m["features"] if f["geometry"]["type"] == "Point"][0]["geometry"]
    print("Data loading and transformation complete.")
except Exception as e:
    # Exit if data loading fails (critical error)
    print(f"Initialization failed: {e}")
    sys.exit(1)

# ==========================================
# 2. Define Function Tasks
# ==========================================

def task_buffer():
    """Task 1: Generate Buffer"""
    print("\n>>> Executing [1] Buffer Analysis...")
    
    # Simple interaction: allow user to input distance
    user_dist = input("Enter buffer distance (meters, default 500): ").strip()
    # Validate input: use 500 if input is not a number
    dist = float(user_dist) if user_dist.isdigit() else 500
    
    # Perform buffer calculation
    buf = buffer(poly, dist)
    
    # Save result to file
    write_geojson(buf, "out/buffer_500m.geojson")
    print(f" -> Generated {dist}m buffer, saved to out/buffer_500m.geojson")
    
    # Display the area of the new buffer
    print(f" -> Buffer Area: {get_area(buf):.2f} sq. meters")
    return buf

def task_clip():
    """Task 2: Clip Features"""
    print("\n>>> Executing [2] Clip Operation...")
    
    # Generate a temporary 500m buffer to use as the "cookie cutter"
    clipper = buffer(poly, 500) 
    
    # Clip the original features using the clipper
    clipped = clip(fc_m, clipper)
    
    # Save clipped results
    write_geojson(clipped, "out/clipped_features.geojson")
    print(" -> Clipping complete, result saved to out/clipped_features.geojson")

def task_nearest():
    """Task 3: Calculate Nearest Distance (Standard)"""
    print("\n>>> Executing [3] Calculate Nearest Distance (Brute Force)...")
    # Calculate Euclidean distance between the point and the polygon
    t0 = time.time()
    dist, a, b = nearest(pt, poly)
    t1 = time.time()
    print(f" -> Nearest distance: {dist:.2f} meters")
    print(f" -> Calculation time: {(t1-t0)*1000:.4f} ms")

def task_analysis():
    """Task 4: Geometric Attribute Analysis"""
    print("\n>>> Executing [4] Geometric Attribute Analysis...")
    
    # Create temporary geometry for analysis
    temp_buf = buffer(poly, 500)
    
    # Calculate perimeter
    perimeter = get_length(temp_buf)
    
    # Check if the point is strictly inside the buffer
    is_inside = is_contained(temp_buf, pt)
    
    print(f" -> Buffer Perimeter: {perimeter:.2f} meters")
    print(f" -> Is original point inside buffer: {is_inside}")

def task_optimized_search():
    """Task 7: High-Speed Search (Spatial Indexing)"""
    print("\n>>> Executing [7] High-Speed Search (STRtree Indexing)...")
    
    # To demonstrate speed, let's search against the entire collection
    # 1. Standard Search (Benchmark)
    print(" -> Running standard search (for comparison)...")
    t_start = time.time()
    # Simulating a heavier load by looping through features manually
    for f in fc_m["features"]:
        nearest(pt, f["geometry"])
    t_std = time.time() - t_start
    
    # 2. Optimized Search
    print(" -> Running STRtree optimized search...")
    t_start = time.time()
    # Build tree and search
    dist, geom = nearest_optimized(pt, fc_m)
    t_opt = time.time() - t_start
    
    print(f" -> Found nearest distance: {dist:.2f} meters")
    print(f" -> [Time Comparison] Standard: {t_std*1000:.4f} ms | Indexed: {t_opt*1000:.4f} ms")
    if t_std > 0:
        print(f" -> Optimization Factor: {t_std/t_opt:.1f}x faster")

def task_geo_features():
    """Task 8: Extract Centroids & Envelopes"""
    print("\n>>> Executing [8] Extracting Geometric Features...")
    
    geo_features = []
    
    # Loop through all polygons in the dataset
    polygons = [f for f in fc_m["features"] if f["geometry"]["type"] == "Polygon"]
    
    print(f" -> Processing {len(polygons)} polygons...")
    
    for poly_feat in polygons:
        geom = poly_feat["geometry"]
        
        # 1. Get Centroid
        cent = get_centroid(geom)
        geo_features.append({
            "type": "Feature",
            "properties": {"type": "Centroid"},
            "geometry": cent
        })
        
        # 2. Get Envelope (Bounding Box)
        env = get_envelope(geom)
        geo_features.append({
            "type": "Feature",
            "properties": {"type": "Envelope"},
            "geometry": env
        })
        
    write_geojson({"type": "FeatureCollection", "features": geo_features}, "out/geo_features.geojson")
    print(" -> Saved Centroids and Envelopes to out/geo_features.geojson")


def task_viz():
    """Task 5: Visualize Results (Smart Mode with Linkage)"""
    print("\n>>> Executing [5] Generating Visualization...")
    
    viz_features = []
    title_parts = []
    
    # Paths
    path_clip = "out/clipped_features.geojson"
    path_buf = "out/buffer_500m.geojson"
    path_geo = "out/geo_features.geojson"
    # [NEW] Path for sampled raster data
    path_sampled = "out/sampled_points.geojson"
    
    # --- Layer 1: Base Map (Result of Task 1 or 2) ---
    has_processed_data = False
    
    # Priority 1: Clipped Results
    if os.path.exists(path_clip):
        print(f" -> [Display] Detected clip result: {path_clip}")
        try:
            with open(path_clip, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "features" in data: viz_features.extend(data["features"])
                title_parts.append("Clipped")
                has_processed_data = True
        except Exception: pass

    # Priority 2: Buffer Results (if no clip)
    elif os.path.exists(path_buf):
        print(f" -> [Display] Detected buffer file: {path_buf}")
        try:
            with open(path_buf, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "features" in data: viz_features.extend(data["features"])
                elif "type" in data and data["type"] == "Polygon":
                     viz_features.append({"type": "Feature", "properties": {"type": "Buffer"}, "geometry": data})
                title_parts.append("Buffer")
                has_processed_data = True
        except Exception: pass

    else:
        print(" -> No processing results found, displaying original data...")
        viz_features.extend(fc_m["features"])
        title_parts.append("Original Data")

    # --- Layer 2: Geometric Features (Result of Task 8) ---
    # This acts as an overlay regardless of what base map is shown
    if os.path.exists(path_geo):
        print(f" -> [Linkage] Detected geometric features (Centroids/Envelopes)")
        try:
            with open(path_geo, 'r', encoding='utf-8') as f:
                geo_data = json.load(f)
                if "features" in geo_data:
                    viz_features.extend(geo_data["features"])
                title_parts.append("+ Geometry")
        except Exception: pass
        
    # [NEW] --- Layer 3: Raster Sampled Points (Result of Task 12) ---
    if os.path.exists(path_sampled):
        print(f" -> [Linkage] Detected Raster Sampled Points")
        try:
            with open(path_sampled, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "features" in data: 
                    # Add specific tag so viz.py knows to label values
                    for ft in data["features"]:
                        ft["properties"]["_viz_type"] = "SampledPoint"
                    viz_features.extend(data["features"])
                title_parts.append("+ Raster Values")
        except Exception: pass
    elif has_processed_data:
         # Only show original points if we are NOT showing sampled points
         points = [f for f in fc_m["features"] if f["geometry"]["type"] == "Point"]
         viz_features.extend(points)

    # --- Context Layers ---
    # Always add original Polygon outline for reference if we are showing Buffer/Clip
    if has_processed_data:
        viz_features.append({"type": "Feature", "geometry": poly, "properties": {"type": "Original"}})

    # Plot
    final_title = " / ".join(title_parts)
    output_file = "out/visualization_result.png"
    try:
        plot_features({"type": "FeatureCollection", "features": viz_features}, title=final_title, output_path=output_file)
        if sys.platform == "win32": os.startfile(os.path.abspath(output_file))
    except Exception as e:
        print(f" [Error] Plotting failed: {e}")

def task_batch():
    import inspect
    import geotoolkit.query as q

    print("DEBUG demo.py path:", __file__)
    print("DEBUG query.py path:", q.__file__)
    print("DEBUG filter_points_within signature:", inspect.signature(q.filter_points_within))
    print("DEBUG tag_points_within signature:", inspect.signature(q.tag_points_within))

    """Task 7: Batch Query on generated_points.geojson (baseline vs indexed)"""
    print("\n>>> Executing [7] Batch Query on generated_points.geojson ...")

    # 1) load data
    pts_fc = read_geojson("data/generated_points.geojson")  # already EPSG:3857
    pts_m = pts_fc

    # 2) reference buffer (EPSG:3857)
    buf_geom = buffer(poly, 500)

    # 3) baseline
    t0 = time.perf_counter()
    tagged_base = tag_points_within(pts_m, buf_geom, use_index=False)
    inside_base = filter_points_within(pts_m, buf_geom, use_index=False, mode="covers")
    t1 = time.perf_counter()

    # 4) indexed
    t2 = time.perf_counter()
    tagged_idx = tag_points_within(pts_m, buf_geom, use_index=True)
    inside_idx = filter_points_within(pts_m, buf_geom, use_index=True, mode="covers")
    t3 = time.perf_counter()

    # 5) print stats
    print(f" -> baseline: {t1 - t0:.4f}s, indexed: {t3 - t2:.4f}s")
    print(f" -> inside buffer points: {len(inside_idx['features'])} / {len(pts_m['features'])}")

    # 6) save outputs
    write_geojson(tagged_idx, "out/generated_points_tagged.geojson")
    write_geojson(inside_idx, "out/generated_points_inside_buffer.geojson")


    # 7) visualize inside points + context polygon/buffer
    viz_feats = []
    viz_feats.extend(inside_idx["features"])
    viz_feats.append({"type": "Feature", "geometry": poly, "properties": {"type": "Original"}})
    viz_feats.append({"type": "Feature", "geometry": buf_geom, "properties": {"type": "Buffer"}})

    out_png = "out/generated_points_inside_buffer.png"
    plot_features(
        {"type": "FeatureCollection", "features": viz_feats},
        title="Generated Points Inside Buffer",
        output_path=out_png,
    )

    if sys.platform == "win32":
        try:
            os.startfile(os.path.abspath(out_png))
        except Exception:
            pass

def task_geometry_summary():
    print("\n>>> Executing [8] Geometry Summary Report ...")

    rows = []

    # --- Original Polygon ---
    bbox = get_bbox(poly)
    centroid = get_centroid(poly)
    rows.append({
        "name": "original_polygon",
        "geom_type": "Polygon",
        "minx": bbox[0],
        "miny": bbox[1],
        "maxx": bbox[2],
        "maxy": bbox[3],
        "centroid_x": centroid["coordinates"][0],
        "centroid_y": centroid["coordinates"][1],
        "area": get_area(poly),
        "length": get_length(poly),
    })

    # --- Buffer Polygon ---
    buf = buffer(poly, 500)
    bbox = get_bbox(buf)
    centroid = get_centroid(buf)
    rows.append({
        "name": "buffer_500m",
        "geom_type": "Polygon",
        "minx": bbox[0],
        "miny": bbox[1],
        "maxx": bbox[2],
        "maxy": bbox[3],
        "centroid_x": centroid["coordinates"][0],
        "centroid_y": centroid["coordinates"][1],
        "area": get_area(buf),
        "length": get_length(buf),
    })

    # --- Generated Points (as a set) ---
    pts_m = read_geojson("data/generated_points.geojson")  
    pts = [f["geometry"] for f in pts_m["features"] if f["geometry"]["type"] == "Point"]
    pts_geom = {
        "type": "MultiPoint",
        "coordinates": [p["coordinates"] for p in pts]
    }

    bbox = get_bbox(pts_geom)
    centroid = get_centroid(pts_geom)

    rows.append({
        "name": "generated_points",
        "geom_type": "PointCollection",
        "minx": bbox[0],
        "miny": bbox[1],
        "maxx": bbox[2],
        "maxy": bbox[3],
        "centroid_x": centroid["coordinates"][0],
        "centroid_y": centroid["coordinates"][1],
        "area": None,
        "length": None,
    })

    # --- Export CSV ---
    out_csv = "out/geometry_summary.csv"
    write_csv(rows, out_csv)
    print(f" -> Geometry summary saved to {out_csv}")

    if sys.platform == "win32":
        try:
            os.startfile(os.path.abspath(out_csv))
        except Exception:
            pass

def task_knn():
    """Task 9: KNN - find K nearest points from generated_points to the target point in sample.geojson"""
    print("\n>>> Executing [9] KNN Query on generated_points.geojson ...")

    # load generated points (already EPSG:3857)
    pts_fc = read_geojson("data/generated_points.geojson")
    pts_m = pts_fc

    # choose target point: the point from sample.geojson (already projected in init stage)
    target_pt = pt

    # reference buffer for visualization context
    buf_geom = buffer(poly, 500)

    # read k from user
    user_k = input("Enter k (default 10): ").strip()
    k = int(user_k) if user_k.isdigit() else 10

    # compute KNN (baseline + indexed optional)
    use_idx_input = input("Use spatial index? (y/n, default y): ").strip().lower()
    use_index = (use_idx_input != "n")

    topk_fc = knn_points(pts_m, target_pt, k=k, use_index=use_index)

    # print summary
    print(f" -> Found top-{len(topk_fc['features'])} nearest points (use_index={use_index})")
    for ft in topk_fc["features"]:
        pid = ft.get("properties", {}).get("id", ft.get("properties", {}).get("name", "NA"))
        d = ft.get("properties", {}).get("distance_m", None)
        r = ft.get("properties", {}).get("knn_rank", None)
        print(f"    #{r}  id={pid}  dist={d:.2f} m")

    # save GeoJSON
    out_geojson = "out/knn_topk.geojson"
    write_geojson(topk_fc, out_geojson)
    print(f" -> Saved: {out_geojson}")

    # plot
    out_png = "out/knn_topk.png"
    plot_knn(poly, buf_geom, target_pt, topk_fc, out_png)

    # auto-open on Windows
    if sys.platform == "win32":
        try:
            os.startfile(os.path.abspath(out_png))
        except Exception:
            pass


def plot_knn(poly_geom, buf_geom, target_pt_geom, points_fc, output_path):
    """
    Create a standalone plot for KNN result:
    - polygon outline
    - buffer outline
    - target point highlighted
    - top-k points highlighted
    """
    poly_s = shape(poly_geom)
    buf_s = shape(buf_geom)
    tgt_s = shape(target_pt_geom)

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_title("KNN Top-K Points to Target", fontsize=14, fontweight="bold")

    # polygon outline
    if poly_s.geom_type == "Polygon":
        x, y = poly_s.exterior.xy
        ax.plot(x, y, linewidth=1.5)

    # buffer outline
    if buf_s.geom_type == "Polygon":
        x, y = buf_s.exterior.xy
        ax.plot(x, y, linewidth=1.0, linestyle="--")

    # plot top-k points
    xs = []
    ys = []
    for ft in points_fc.get("features", []):
        p = shape(ft["geometry"])
        xs.append(p.x)
        ys.append(p.y)
    ax.scatter(xs, ys, s=30, marker="o")  # top-k points

    # plot target point (bigger + different marker)
    ax.scatter([tgt_s.x], [tgt_s.y], s=120, marker="x")

    ax.set_aspect("equal")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.set_xlabel("X (Meters, EPSG:3857)")
    ax.set_ylabel("Y (Meters, EPSG:3857)")

    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f" -> Visualization image saved to: {output_path}")

def task_raster_sampling():
    """Task 12: Raster Point Sampling (New Feature)"""
    print("\n>>> Executing [12] Raster Point Sampling...")
    if not HAS_RASTERIO:
        print(" [Error] 'rasterio' is not installed. Please run: pip install rasterio")
        return

    raster_path = "data/sample_dem.tif"
    
    # 1. Check if raster exists, if not, generate synthetic one
    if not os.path.exists(raster_path):
        print(f" -> Raster not found at {raster_path}")
        print(" -> Generating synthetic DEM based on sample data extent...")
        
        # Get extent of the entire dataset
        polys = [shape(f["geometry"]) for f in fc_m["features"]]
        minx = min(p.bounds[0] for p in polys)
        miny = min(p.bounds[1] for p in polys)
        maxx = max(p.bounds[2] for p in polys)
        maxy = max(p.bounds[3] for p in polys)
        
        generate_synthetic_raster(raster_path, (minx, miny, maxx, maxy))
        
    # 2. Perform Sampling
    print(f" -> Sampling values from {raster_path}...")
    sampled_fc = sample_raster_at_points(fc_m, raster_path)
    
    # 3. Save Result
    out_path = "out/sampled_points.geojson"
    write_geojson(sampled_fc, out_path)
    
    # Print sample values to console
    for f in sampled_fc["features"]:
        val = f["properties"].get("raster_value")
        print(f"    Point ID: {f['properties'].get('name', 'N/A')} -> Value: {val:.2f}")
        
    print(f" -> Sampling complete. Result saved to {out_path}")

def task_report():
    """Task 6: Generate Excel/CSV Report (Linked Mode)"""
    print("\n>>> Executing [6] Generating Distance Report...")
    
    report_data = []
    
    # ==========================================
    # 1. Determine Data Source (Which points to analyze?)
    # ==========================================
    path_clip = "out/clipped_features.geojson"
    # [NEW] Check for Sampled Points
    path_sampled = "out/sampled_points.geojson"
    
    target_points = []
    data_source_desc = ""

    # Check for Raster Sampling first (richest data)
    if os.path.exists(path_sampled):
        print(f" -> [Linked] Analyzing Raster Sampled Points")
        try:
            with open(path_sampled, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "features" in data: target_points = data["features"]
            data_source_desc = "Raster Sampled"
        except: pass
    
    # Check if Task 2 (Clip) was run.
    elif os.path.exists(path_clip):
        print(f" -> [Linked] Detected clip result, analyzing only remaining features")
        try:
            with open(path_clip, 'r', encoding='utf-8') as f:
                clip_data = json.load(f)
                if "features" in clip_data:
                    target_points = [f for f in clip_data["features"] if f["geometry"]["type"] == "Point"]
                data_source_desc = "Clipped Data (Task 2)"
        except Exception:
            pass
    
    # Fallback: Use all points from original data
    if not target_points:
        if not os.path.exists(path_clip):
            print(f" -> Clip result not found, analyzing all points in original data")
        data_source_desc = "Original Data (Raw)"
        target_points = [f for f in fc_m["features"] if f["geometry"]["type"] == "Point"]

    # ==========================================
    # 2. Determine Reference Standard
    # ==========================================
    path_buf = "out/buffer_500m.geojson"
    reference_geom = None
    ref_source_desc = ""

    if os.path.exists(path_buf):
        try:
            with open(path_buf, 'r', encoding='utf-8') as f:
                buf_data = json.load(f)
                if "type" in buf_data and buf_data["type"] == "Polygon":
                    reference_geom = buf_data
                elif "features" in buf_data:
                    reference_geom = buf_data["features"][0]["geometry"]
                ref_source_desc = "File Read (Task 1)"
                if not os.path.exists(path_clip):
                    print(f" -> [Linked] Buffer file loaded as judgment standard")
        except Exception:
            pass
            
    if reference_geom is None:
        if not os.path.exists(path_buf):
            pass 
        reference_geom = buffer(poly, 500)
        ref_source_desc = "Default 500m"

    # ==========================================
    # 3. Start Calculation
    # ==========================================
    print(f" -> Analyzing {len(target_points)} points based on [{data_source_desc}]...")
    
    for i, pt_feature in enumerate(target_points):
        geom = pt_feature["geometry"]
        d, _, _ = nearest(geom, poly)
        in_buf = is_contained(reference_geom, geom)
        p_name = pt_feature.get("properties", {}).get("name", f"Point_{i+1}")
        props = pt_feature.get("properties", {})

        row = {
            "ID": i + 1,
            "Name": p_name,
            "Data_Source": data_source_desc,
            "Distance_to_Polygon": round(d, 2),
            f"Inside_Buffer ({ref_source_desc})": "Yes" if in_buf else "No"
        }
        
        # [NEW] Add Raster Value if present
        if "raster_value" in props:
            row["Raster_Value"] = round(props["raster_value"], 2)
            
        report_data.append(row)
        
    csv_path = "out/distance_report.csv"
    write_csv(report_data, csv_path)
    
    if sys.platform == "win32":
        try:
            os.startfile(os.path.abspath(csv_path))
        except:
            pass

# ==========================================
# 3. Menu Configuration
# ==========================================

MENU = {
    "1": ("Generate Buffer", task_buffer),
    "2": ("Clip Features", task_clip),
    "3": ("Calculate Nearest Distance", task_nearest),
    "4": ("Geometric Analysis", task_analysis),
    "5": ("Visualize Results", task_viz),
    "6": ("Generate Report (Export CSV)", task_report),
    "7": ("High-Speed Search (STRtree) ", task_optimized_search),
    "8": ("Extract Centroids/Envelopes ", task_geo_features),
    "9": ("Batch Query (Generated Points) [Baseline vs Index]", task_batch),
    "10": ("Geometry Summary (bbox / centroid)", task_geometry_summary),
    "11": ("KNN Top-K Nearest Points", task_knn),
    "12": ("Raster Point Sampling [NEW!]", task_raster_sampling),
}

# ==========================================
# 4. Main Loop Logic
# ==========================================

if __name__ == "__main__":
    while True:
        print("\n" + "="*40)
        print("      GeoToolkit Interactive Console")
        print("="*40)
        for key, (desc, _) in MENU.items():
            print(f" [{key}] {desc}")
        print(" [0] Exit Program")
        print("-" * 40)
        
        user_input = input("Enter function ID (Multi-select e.g. '1,6'): ").strip()
        
        if user_input in ['0', 'q', 'exit', 'quit']:
            print("Exiting program...")
            break
        if not user_input: continue

        selection_keys = user_input.replace("，", ",").replace(",", " ").split()
        
        valid_choice = False
        for key in selection_keys:
            if key in MENU:
                valid_choice = True
                try:
                    MENU[key][1]() 
                except Exception as e:
                    print(f"[Error] Execution failed: {e}")
            else:
                if key != '0': print(f"\n[Warning] Invalid ID '{key}'.")
        
        if valid_choice:
            input("\nTask completed, press [Enter] to return to menu...")
            
    print("Goodbye!")