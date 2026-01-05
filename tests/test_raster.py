import os
import pytest
import shutil
from geotoolkit.io import read_geojson
from geotoolkit.project import to_epsg

# Try importing raster modules; skip tests if rasterio is not installed
try:
    from geotoolkit.raster import sample_raster_at_points, generate_synthetic_raster
    HAS_RASTERIO = True
except ImportError:
    HAS_RASTERIO = False

@pytest.mark.skipif(not HAS_RASTERIO, reason="rasterio not installed")
def test_raster_sampling_workflow():
    """
    Test the full raster workflow: 
    1. Generate synthetic raster.
    2. Sample points from it.
    3. Verify values.
    """
    # Setup paths
    test_raster_path = "out/test_synthetic.tif"
    
    # Ensure output dir exists
    if not os.path.exists("out"):
        os.makedirs("out")

    # 1. Define bounds for synthetic raster (0,0 to 100,100)
    bounds = (0.0, 0.0, 100.0, 100.0)
    
    # 2. Generate Raster
    generate_synthetic_raster(test_raster_path, bounds, resolution=10.0)
    assert os.path.exists(test_raster_path), "Synthetic raster was not created."

    # 3. Create a dummy FeatureCollection with points
    # Point A at (10, 10) -> Expected Value: X+Y = 10+10 = 20
    # Point B at (50, 50) -> Expected Value: X+Y = 50+50 = 100
    points_fc = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "Point A"},
                "geometry": {"type": "Point", "coordinates": [10.0, 10.0]}
            },
            {
                "type": "Feature",
                "properties": {"name": "Point B"},
                "geometry": {"type": "Point", "coordinates": [50.0, 50.0]}
            }
        ]
    }

    # 4. Run Sampling
    result_fc = sample_raster_at_points(points_fc, test_raster_path)
    
    # 5. Assertions
    assert len(result_fc["features"]) == 2
    
    val_a = result_fc["features"][0]["properties"].get("raster_value")
    val_b = result_fc["features"][1]["properties"].get("raster_value")
    
    assert val_a is not None, "Raster value not found in properties"
    
    # Since the synthetic raster formula is Z = X + Y, we check approximate values
    # Note: Raster pixel centers might align slightly differently, so we use a tolerance
    assert abs(val_a - 20.0) < 2.0, f"Expected approx 20.0, got {val_a}"
    assert abs(val_b - 100.0) < 2.0, f"Expected approx 100.0, got {val_b}"

    # Cleanup (optional)
    if os.path.exists(test_raster_path):
        os.remove(test_raster_path)