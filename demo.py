import sys
import os
import json
import time
from geotoolkit.io import read_geojson, write_geojson, write_csv
from geotoolkit.project import to_epsg
from geotoolkit.analysis import (
    buffer, clip, nearest, get_area, get_length, is_contained,
    nearest_optimized, get_centroid, get_envelope
)
from geotoolkit.viz import plot_features

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

    # Fallback: Original Data
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

    # --- Context Layers ---
    # Always add original Polygon outline for reference if we are showing Buffer/Clip
    if has_processed_data:
        viz_features.append({"type": "Feature", "geometry": poly, "properties": {"type": "Original"}})
        
    # Always add original Points for context
    if has_processed_data:
         points = [f for f in fc_m["features"] if f["geometry"]["type"] == "Point"]
         viz_features.extend(points)

    # Plot
    final_title = " / ".join(title_parts)
    output_file = "out/visualization_result.png"
    try:
        plot_features({"type": "FeatureCollection", "features": viz_features}, title=final_title, output_path=output_file)
        if sys.platform == "win32": os.startfile(os.path.abspath(output_file))
    except Exception as e:
        print(f" [Error] Plotting failed: {e}")

def task_report():
    """Task 6: Generate Excel/CSV Report (Linked Mode)"""
    print("\n>>> Executing [6] Generating Distance Report...")
    
    report_data = []
    
    # ==========================================
    # 1. Determine Data Source (Which points to analyze?)
    # ==========================================
    path_clip = "out/clipped_features.geojson"
    target_points = []
    data_source_desc = ""

    # Check if Task 2 (Clip) was run. If so, analyze ONLY the clipped points.
    if os.path.exists(path_clip):
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

        row = {
            "ID": i + 1,
            "Name": p_name,
            "Data_Source": data_source_desc,
            "Distance_to_Polygon": round(d, 2),
            f"Inside_Buffer ({ref_source_desc})": "Yes" if in_buf else "No"
        }
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
    "7": ("High-Speed Search (STRtree) [NEW!]", task_optimized_search),
    "8": ("Extract Centroids/Envelopes [NEW!]", task_geo_features)
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