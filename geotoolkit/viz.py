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
        # Extract properties to check for custom flags (like 'Original')
        props = feature.get("properties", {})
        
        # Styling logic based on geometry type
        if geom_type == 'Point':
            # Plot points as red dots ('ro')
            # zorder=5 ensures points appear on top of polygons
            ax.plot(geom.x, geom.y, 'ro', markersize=6, label='Point', zorder=5)
            
        elif geom_type == 'Polygon':
            # Extract x and y coordinates of the polygon exterior
            x, y = geom.exterior.xy
            
            # Special Style: If it is the original polygon (marked as 'Original' in demo.py)
            # Use black dashed lines to differentiate it from the result
            if props.get("type") == "Original":
                ax.plot(x, y, 'k--', linewidth=1.5, label='Original Polygon')
            else:
                # Default Style: Buffer or regular polygon
                # Use blue outline and semi-transparent fill
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