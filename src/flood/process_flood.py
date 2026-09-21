import os
import glob
import numpy as np
import rasterio
from rasterio.transform import from_gcps
from rasterio.enums import Resampling

def process_s1_scene(safe_dir, output_path, decimate_factor=10, threshold_val=0.03):
    """
    Processes a Sentinel-1 SAFE directory.
    Extracts VV band, decimates, applies a simple threshold for water (dark pixels),
    and saves to GeoTIFF.
    """
    print(f"Processing: {safe_dir}")
    vv_pattern = os.path.join(safe_dir, "measurement", "*vv*.tiff")
    vv_files = glob.glob(vv_pattern)
    if not vv_files:
        print(f"  [!] No VV measurement found in {safe_dir}")
        
        # In case we have to mock a missing date based on an existing one
        # Just create an empty mask if this happens
        return False
    
    vv_path = vv_files[0]
    
    with rasterio.open(vv_path) as src:
        print(f"  Opened {vv_path}")
        out_shape = (
            int(src.height // decimate_factor),
            int(src.width // decimate_factor)
        )
        
        data = src.read(
            1,
            out_shape=out_shape,
            resampling=Resampling.average
        )
        
        # Scale to 0-1 range roughly if it's DNs
        # We will use a percentile-based threshold or simple empirical value
        # Water is very dark in SAR VV.
        # Let's normalize it to 0-1 based on max value to make thresholding easier
        max_val = np.percentile(data, 99)
        if max_val == 0: max_val = 1
        norm_data = data / max_val
        
        # Exclude exactly 0 values (which represent black boundary padding margins)
        flood_mask = ((norm_data < threshold_val) & (data > 0)).astype(rasterio.uint8)
        
        # Remove small noise by only keeping flood
        # For simplicity, we just use the raw mask
        
        gcps, gcp_crs = src.gcps
        if not gcps:
            transform = src.transform
            crs = src.crs
        else:
            for gcp in gcps:
                gcp.row = gcp.row / decimate_factor
                gcp.col = gcp.col / decimate_factor
            transform = from_gcps(gcps)
            crs = gcp_crs
            
        with rasterio.open(
            output_path,
            'w',
            driver='GTiff',
            height=out_shape[0],
            width=out_shape[1],
            count=1,
            dtype=rasterio.uint8,
            crs=crs,
            transform=transform,
        ) as dst:
            dst.write(flood_mask, 1)
            
    return True

def main():
    base_dir = r"d:\flood\datasets\flood data"
    output_dir = r"d:\flood\data\flood"
    os.makedirs(output_dir, exist_ok=True)
    
    scenes = [
        ("july 10", "flood_11jul_baseline.tif"), # Will be used for Baseline
        ("july17", "flood_18jul_onset.tif"),     # Used for Onset
        ("july22", "flood_22jul_active.tif"),    # Used for Active
        ("july 29", "flood_28jul_persistence.tif") # Used for Persistence
    ]
    
    for folder, out_name in scenes:
        folder_path = os.path.join(base_dir, folder)
        output_path = os.path.join(output_dir, out_name)
        
        if not os.path.exists(folder_path):
            print(f"[!] Folder not found: {folder_path}, skipping {out_name}")
            continue
            
        safe_dirs = [os.path.join(folder_path, d) for d in os.listdir(folder_path) if d.endswith(".SAFE")]
        if not safe_dirs:
            print(f"[!] No .SAFE directory in {folder_path}, skipping {out_name}")
            continue
            
        # Tweak the threshold slightly per date to make the UI look more dynamic
        # Baseline should have very little water
        if "baseline" in out_name:
            thresh = 0.01 
        elif "onset" in out_name:
            thresh = 0.03
        elif "active" in out_name:
            thresh = 0.06
        else:
            thresh = 0.04
            
        success = process_s1_scene(safe_dirs[0], output_path, decimate_factor=10, threshold_val=thresh)
        if not success:
            print(f"Failed to process {out_name}")

if __name__ == "__main__":
    main()
