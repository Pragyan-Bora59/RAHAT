import os
import rasterio
from rasterio.warp import transform_bounds
import numpy as np
from PIL import Image
import json

def export_overlay(tif_path, out_png_path, bounds_list, colormap, nodata_val=None):
    if not os.path.exists(tif_path):
        print(f"Skipping {tif_path}, not found.")
        return
        
    with rasterio.open(tif_path) as src:
        data = src.read(1)
        # Calculate bounds in EPSG:4326 (lon/lat)
        bounds = transform_bounds(src.crs, 'EPSG:4326', *src.bounds)
        bounds_list[os.path.basename(tif_path)] = {
            "southWest": [bounds[1], bounds[0]], # lat, lon
            "northEast": [bounds[3], bounds[2]]
        }
        
        # Create an RGBA image
        h, w = data.shape
        rgba = np.zeros((h, w, 4), dtype=np.uint8)
        
        for val, color in colormap.items():
            mask = data == val
            rgba[mask] = color
            
        if nodata_val is not None:
            rgba[data == nodata_val] = [0, 0, 0, 0] # transparent
            
        img = Image.fromarray(rgba, 'RGBA')
        img.save(out_png_path)
        print(f"Exported {out_png_path}")

def main():
    os.makedirs(r"d:\flood\public\overlays", exist_ok=True)
    bounds_dict = {}
    
    # Colormap for flood masks: 1 = flooded (blue, semi-transparent)
    flood_cmap = {
        1: [0, 102, 204, 150]
    }
    
    # Colormap for Hazard map: 1=Green, 2=Yellow, 3=Orange, 4=Red
    hazard_cmap = {
        1: [34, 139, 34, 100],   # Green
        2: [255, 215, 0, 150],   # Yellow
        3: [255, 140, 0, 150],   # Orange
        4: [220, 20, 60, 150]    # Red
    }
    
    exports = [
        # Flood Masks
        (r"d:\flood\data\flood\flood_11jul_baseline.tif", r"d:\flood\public\overlays\flood_baseline.png", flood_cmap, 0),
        (r"d:\flood\data\flood\flood_18jul_onset.tif", r"d:\flood\public\overlays\flood_onset.png", flood_cmap, 0),
        (r"d:\flood\data\flood\flood_22jul_active.tif", r"d:\flood\public\overlays\flood_active.png", flood_cmap, 0),
        (r"d:\flood\data\flood\flood_28jul_persistence.tif", r"d:\flood\public\overlays\flood_persistence.png", flood_cmap, 0),
        
        # Hazard Maps
        (r"d:\flood\data\flood\hazard_map_11jul.tif", r"d:\flood\public\overlays\hazard_map_11jul.png", hazard_cmap, 0),
        (r"d:\flood\data\flood\hazard_map_18jul.tif", r"d:\flood\public\overlays\hazard_map_18jul.png", hazard_cmap, 0),
        (r"d:\flood\data\flood\hazard_map_22jul.tif", r"d:\flood\public\overlays\hazard_map_22jul.png", hazard_cmap, 0),
        (r"d:\flood\data\flood\hazard_map_28jul.tif", r"d:\flood\public\overlays\hazard_map_28jul.png", hazard_cmap, 0)
    ]
    
    for tif_path, png_path, cmap, nodata in exports:
        export_overlay(tif_path, png_path, bounds_dict, cmap, nodata)
        
    with open(r"d:\flood\public\overlays\bounds.json", 'w') as f:
        json.dump(bounds_dict, f, indent=2)
        
if __name__ == "__main__":
    main()
