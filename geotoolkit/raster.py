# Raster processing utilities.
# Includes Point Sampling and synthetic data generation for testing.

from __future__ import annotations
import os
import numpy as np
from typing import Any, Dict, List
import rasterio
from rasterio.transform import from_origin
from shapely.geometry import shape

JsonDict = Dict[str, Any]

def sample_raster_at_points(points_fc: JsonDict, raster_path: str) -> JsonDict:
    """
    Extract raster values at the coordinates of point features.
    
    Parameters
    ----------
    points_fc : GeoJSON FeatureCollection
        Collection containing Point features.
    raster_path : str
        Path to the raster file (e.g., .tif).
        
    Returns
    -------
    GeoJSON FeatureCollection
        New collection where each point has a new property 'raster_value'.
    """
    # Deep copy features to avoid modifying original list in place immediately
    # (Simple list comprehension suffices here)
    features_out = []
    
    # Open the raster file
    try:
        src = rasterio.open(raster_path)
    except Exception as e:
        print(f"[Error] Could not open raster file: {e}")
        return points_fc

    with src:
        # Prepare coordinates list for batch sampling
        # Filter only Points
        valid_feats = [f for f in points_fc.get("features", []) 
                       if f.get("geometry", {}).get("type") == "Point"]
        
        coords = []
        for f in valid_feats:
            geom = f["geometry"]
            # GeoJSON coordinates are [x, y]
            coords.append((geom["coordinates"][0], geom["coordinates"][1]))
            
        # Sample the raster
        # src.sample returns a generator of arrays (one value per band)
        # We assume single-band raster (DEM) for this example
        sampled_values = list(src.sample(coords))
        
        # Assign values back to features
        for i, f in enumerate(valid_feats):
            # Create a copy of the feature to keep data flow clean
            new_feat = f.copy()
            new_feat["properties"] = f.get("properties", {}).copy()
            
            # Get value (band 1)
            val = sampled_values[i][0]
            
            # Handle NoData or valid values
            new_feat["properties"]["raster_value"] = float(val)
            features_out.append(new_feat)
            
    return {"type": "FeatureCollection", "features": features_out}


def generate_synthetic_raster(
    target_path: str, 
    bounds: tuple[float, float, float, float], 
    resolution: float = 10.0
) -> None:
    """
    Generate a synthetic GeoTIFF (DEM-like) covering the given bounds.
    Used for testing when no real data is available.
    
    Parameters
    ----------
    target_path : Output path for .tif file.
    bounds : (minx, miny, maxx, maxy) in the target CRS (e.g. EPSG:3857).
    resolution : Pixel size in map units (meters).
    """
    minx, miny, maxx, maxy = bounds
    
    # Add some buffer to bounds to ensure points are well inside
    pad = 100.0
    minx -= pad; miny -= pad; maxx += pad; maxy += pad
    
    width = int((maxx - minx) / resolution)
    height = int((maxy - miny) / resolution)
    
    # Create an affine transform for the raster
    # (west, north, xsize, ysize) - Note: ysize is usually negative for north-up images
    transform = from_origin(minx, maxy, resolution, resolution)
    
    # Generate fake elevation data (e.g., a simple gradient + random noise)
    # x indices
    x = np.linspace(0, 100, width)
    # y indices
    y = np.linspace(0, 100, height)
    X, Y = np.meshgrid(x, y)
    
    # Equation: Z = X + Y (simple diagonal slope)
    data = (X + Y).astype(rasterio.float32)
    
    # Write to file
    new_dataset = rasterio.open(
        target_path,
        'w',
        driver='GTiff',
        height=height,
        width=width,
        count=1,
        dtype=data.dtype,
        crs='EPSG:3857', # Assuming we are working in Web Mercator
        transform=transform,
    )
    
    new_dataset.write(data, 1)
    new_dataset.close()
    print(f" -> Generated synthetic raster: {target_path}")