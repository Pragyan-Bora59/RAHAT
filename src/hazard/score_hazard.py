import os
import yaml
import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling

def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def normalize_array(arr, invert=False):
    """Normalize array to 0-1 range. If invert, lower values become closer to 1."""
    valid = np.isfinite(arr)
    if not np.any(valid):
        return np.zeros_like(arr)
        
    arr_min = np.min(arr[valid])
    arr_max = np.max(arr[valid])
    
    if arr_max == arr_min:
        return np.zeros_like(arr)
        
    norm = (arr - arr_min) / (arr_max - arr_min)
    if invert:
        norm = 1.0 - norm
        
    norm[~valid] = 0
    return norm

def score_hazard_for_date(flood_path, out_path, dem, meta, dem_transform, dem_crs, slope_norm, flow_norm, weights, thresholds):
    if not os.path.exists(flood_path):
        print(f"Skipping {flood_path}, not found.")
        return

    # Reproject flood to match DEM grid
    flood_aligned = np.zeros_like(dem, dtype=np.float32)
    with rasterio.open(flood_path) as src_flood:
        reproject(
            source=rasterio.band(src_flood, 1),
            destination=flood_aligned,
            src_transform=src_flood.transform,
            src_crs=src_flood.crs,
            dst_transform=dem_transform,
            dst_crs=dem_crs,
            resampling=Resampling.nearest
        )
    
    dem_norm = normalize_array(dem, invert=True)      # Lower elevation = higher risk
    flood_norm = flood_aligned                        # Already 0 or 1
    
    score = (
        flood_norm * weights['active_flood'] +
        dem_norm * weights['elevation_low'] +
        slope_norm * weights['slope_flat'] +
        flow_norm * weights['flow_accumulation']
    )
    
    # 1: Green, 2: Yellow, 3: Orange, 4: Red
    hazard_class = np.ones_like(score, dtype=np.uint8) # Default green
    hazard_class[score >= thresholds['yellow']] = 2
    hazard_class[score >= thresholds['orange']] = 3
    hazard_class[score >= thresholds['red']] = 4
    
    meta.update(dtype='uint8')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with rasterio.open(out_path, 'w', **meta) as dst:
        dst.write(hazard_class, 1)
        
    print(f"Hazard map saved to {out_path}")

def main():
    config = load_config(r"d:\flood\config\hazard_weights.yaml")
    weights = config['weights']
    thresholds = config['thresholds']
    
    dem_path = r"d:\flood\data\terrain\dem.tif"
    slope_path = r"d:\flood\data\terrain\slope.tif"
    flow_path = r"d:\flood\data\terrain\flow_accumulation.tif"
    
    with rasterio.open(dem_path) as src_dem:
        dem = src_dem.read(1)
        meta = src_dem.meta.copy()
        dem_transform = src_dem.transform
        dem_crs = src_dem.crs
        
    with rasterio.open(slope_path) as src_slope:
        slope = src_slope.read(1)
        
    with rasterio.open(flow_path) as src_flow:
        flow = src_flow.read(1)
        
    print("Normalizing base terrain features...")
    slope_norm = normalize_array(slope, invert=True)
    flow_norm = normalize_array(flow, invert=False)
    
    dates = [
        ("flood_11jul_baseline.tif", "hazard_map_11jul.tif"),
        ("flood_18jul_onset.tif", "hazard_map_18jul.tif"),
        ("flood_22jul_active.tif", "hazard_map_22jul.tif"),
        ("flood_28jul_persistence.tif", "hazard_map_28jul.tif")
    ]
    
    for in_name, out_name in dates:
        flood_path = os.path.join(r"d:\flood\data\flood", in_name)
        out_path = os.path.join(r"d:\flood\data\flood", out_name)
        score_hazard_for_date(flood_path, out_path, dem, meta, dem_transform, dem_crs, slope_norm, flow_norm, weights, thresholds)

if __name__ == "__main__":
    main()
