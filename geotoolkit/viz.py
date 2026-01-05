import matplotlib.pyplot as plt
from shapely.geometry import shape

def plot_features(feature_collection, title="GeoJSON Plot", output_path="out/plot.png"):
    # Initialize a square figure to better represent maps
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_title(title, fontsize=14, fontweight='bold')
    
    # Iterate and plot each feature in the collection
    for feature in feature_collection["features"]:
        # Convert GeoJSON feature to Shapely geometry for easy coordinate extraction
        geom = shape(feature["geometry"])
        geom_type = geom.geom_type
        # Extract properties to check for custom flags
        props = feature.get("properties", {})
        feat_type = props.get("type", "")
        viz_type = props.get("_viz_type", "") # [NEW] Special internal flag for visualization style
        
        # Styling logic based on geometry type and properties
        if geom_type == 'Point':
            if feat_type == "Centroid":
                # Centroids: Green dots
                ax.plot(geom.x, geom.y, 'go', markersize=8, label='Centroid', zorder=10)
            elif viz_type == "SampledPoint":
                # [NEW] Raster Sampled Points: Blue dots with text value
                ax.plot(geom.x, geom.y, 'bo', markersize=6, label='Sampled Value', zorder=6)
                val = props.get("raster_value", 0)
                # Annotate the value next to the point
                ax.text(geom.x + 20, geom.y + 20, f"{val:.1f}", fontsize=9, color='blue', zorder=7)
            else:
                # Standard Points: Red dots
                ax.plot(geom.x, geom.y, 'ro', markersize=6, label='Point', zorder=5)
            
        elif geom_type == 'Polygon':
            x, y = geom.exterior.xy
            
            if feat_type == "Original":
                # Original Polygon: Black dashed line
                ax.plot(x, y, 'k--', linewidth=1.5, label='Original Polygon')
            
            elif feat_type == "Envelope":
                # Envelope: Orange dash-dot line
                ax.plot(x, y, color='orange', linestyle='-.', linewidth=2, label='Envelope', zorder=4)
                
            else:
                # Default (Buffer/Clip): Blue outline and fill
                ax.plot(x, y, color='#6699cc', alpha=0.8, linewidth=2)
                ax.fill(x, y, color='#6699cc', alpha=0.3)

    # Important: Set aspect ratio to 'equal' so the map doesn't look stretched
    ax.set_aspect('equal')
    
    # Add grid lines for easier distance estimation
    ax.grid(True, linestyle='--', alpha=0.5) 
    
    # Add axis labels with unit information
    ax.set_xlabel("X Coordinates (Meters EPSG:3857)", fontsize=10)
    ax.set_ylabel("Y Coordinates (Meters EPSG:3857)", fontsize=10)
    
    # Save the figure to disk
    plt.savefig(output_path, dpi=150)
    
    # Close the plot to free up memory
    plt.close()
    print(f" -> Visualization image saved to: {output_path}")