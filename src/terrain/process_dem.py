import rasterio
import numpy as np
from scipy import ndimage
import os
from rasterio.enums import Resampling

def calculate_slope(dem, cell_size=30.0):
    """
    Calculates slope from DEM using simple numpy gradients.
    """
    dy, dx = np.gradient(dem, cell_size, cell_size)
    slope = np.arctan(np.sqrt(dx**2 + dy**2)) * (180.0 / np.pi)
    return slope.astype(np.float32)

def calculate_d8_flow(dem):
    """
    Simplified D8 Flow Direction and Accumulation using an iterative or local proxy.
    This is a prototype implementation. A true D8 recursive accumulation is slow in pure python.
    We will use a simplified convolution-based approach for the prototype.
    """
    print("  Calculating D8 Flow Direction...")
    # Pad DEM to handle edges
    padded_dem = np.pad(dem, pad_width=1, mode='edge')
    
    # 8-directional kernels to find steepest descent
    directions = [
        (1, 0, 1), (1, 1, 2), (0, 1, 4), (-1, 1, 8),
        (-1, 0, 16), (-1, -1, 32), (0, -1, 64), (1, -1, 128)
    ]
    
    flow_dir = np.zeros_like(dem, dtype=np.uint8)
    max_drop = np.zeros_like(dem, dtype=np.float32)
    
    for dy, dx, d_val in directions:
        # Calculate drop
        neighbor = padded_dem[1+dy:1+dy+dem.shape[0], 1+dx:1+dx+dem.shape[1]]
        drop = dem - neighbor
        
        # Adjust for diagonals
        if dy != 0 and dx != 0:
            drop /= np.sqrt(2.0)
            
        update_mask = drop > max_drop
        flow_dir[update_mask] = d_val
        max_drop[update_mask] = drop[update_mask]

    print("  Calculating Simplified Flow Accumulation...")
    # Prototype shortcut: local convergence proxy instead of global recursive accumulation
    # We count how many neighbors flow into each pixel
    flow_acc = np.ones_like(dem, dtype=np.float32)
    
    # For a full flow acc, we'd need a topological sort. 
    # For this prototype, we'll just run a few iterations of local accumulation
    # to highlight drainage features.
    for _ in range(5): 
        new_acc = np.copy(flow_acc)
        for dy, dx, d_val in directions:
            # Shift flow acc from neighbors that point to us
            shifted_dir = np.roll(flow_dir, shift=(dy, dx), axis=(0, 1))
            shifted_acc = np.roll(flow_acc, shift=(dy, dx), axis=(0, 1))
            
            # The opposite direction value
            opposite = {1:16, 2:32, 4:64, 8:128, 16:1, 32:2, 64:4, 128:8}[d_val]
            # Add to accumulation if neighbor points to us
            new_acc += np.where(shifted_dir == opposite, shifted_acc, 0)
        flow_acc = new_acc

    return flow_dir, flow_acc

def process_dem(input_path, output_dir):
    print(f"Processing DEM: {input_path}")
    
    with rasterio.open(input_path) as src:
        # Read the DEM at 1/5th resolution to speed up flow routing for the prototype
        decimate_factor = 5
        out_shape = (
            int(src.height // decimate_factor),
            int(src.width // decimate_factor)
        )
        
        print(f"  Downsampling from {src.shape} to {out_shape} for rapid processing")
        dem = src.read(
            1,
            out_shape=out_shape,
            resampling=Resampling.bilinear
        )
        
        # Calculate cell size in meters (assuming EPSG:4326, 1 deg ~ 111km)
        transform = src.transform
        cell_size = transform[0] * decimate_factor * 111320.0
        
        print("  Calculating Slope...")
        slope = calculate_slope(dem, cell_size)
        
        flow_dir, flow_acc = calculate_d8_flow(dem)
        
        # Scale transform
        new_transform = transform * transform.scale(
            (src.width / out_shape[1]),
            (src.height / out_shape[0])
        )
        
        meta = src.meta.copy()
        meta.update({
            "height": out_shape[0],
            "width": out_shape[1],
            "transform": new_transform,
            "dtype": 'float32',
            "compress": 'lzw'
        })
        
        # Save outputs
        os.makedirs(output_dir, exist_ok=True)
        
        print("  Saving slope.tif")
        with rasterio.open(os.path.join(output_dir, 'slope.tif'), 'w', **meta) as dst:
            dst.write(slope, 1)
            
        print("  Saving flow_direction.tif")
        meta.update(dtype='uint8')
        with rasterio.open(os.path.join(output_dir, 'flow_direction.tif'), 'w', **meta) as dst:
            dst.write(flow_dir, 1)
            
        print("  Saving flow_accumulation.tif")
        meta.update(dtype='float32')
        with rasterio.open(os.path.join(output_dir, 'flow_accumulation.tif'), 'w', **meta) as dst:
            dst.write(flow_acc, 1)
            
        print("  Saving downsampled dem.tif")
        with rasterio.open(os.path.join(output_dir, 'dem.tif'), 'w', **meta) as dst:
            dst.write(dem.astype(np.float32), 1)

if __name__ == "__main__":
    dem_path = r"d:\flood\data\terrain\dem.tif"
    out_dir = r"d:\flood\data\terrain"
    # To prevent overwriting the source dem.tif, we save it as dem_processed.tif
    temp_dem = r"d:\flood\data\terrain\dem_temp.tif"
    if os.path.exists(dem_path):
        os.rename(dem_path, temp_dem)
        process_dem(temp_dem, out_dir)
    else:
        print(f"Error: {dem_path} not found.")
