# Flood Processing Methodology

This document outlines the methodology used to process the four Sentinel-1 temporal states into actionable flood masks for the RAHAT prototype.

## The Temporal Sequence

The project utilizes four SAR (Synthetic Aperture Radar) observations to track the evolution of the Dhemaji flood event:

1. **~11 July — Pre-flood baseline**: Represents the dry/normal state of the district.
2. **18 July — Flood onset**: The initial expansion of floodwaters.
3. **22 July — Active flood**: The peak inundation state.
4. **~28 July — Late flood / persistence**: The receding phase where water persists in low-lying areas.

## Data Processing Steps

Due to missing or corrupted raw SAR data in the provided workspace, the prototype relies on processing available GeoTIFFs using `rasterio` and `numpy`.

### 1. Preprocessing and Alignment
All raster inputs are opened and read. In a production system, these would undergo SAR-specific preprocessing (calibration, speckle filtering, terrain correction). For this prototype, we assume the input TIFFs are already backscatter or classified products.

### 2. Thresholding / Change Detection
The core logic for flood extraction is implemented in `src/flood/process_flood.py`.

- We apply an intensity threshold to isolate dark pixels (which correspond to water due to specular reflection of the radar pulse).
- A base threshold (e.g., `< 0.1`) is used to classify a pixel as "water".

### 3. Mask Generation
For each date, a binary mask is generated:
- `1` = Flooded
- `0` = Not Flooded

### 4. Quality Control
To reduce false positives (noise), small isolated clusters of pixels are cleaned. In the prototype, this is handled via basic morphological operations or masking against known permanent water bodies if data is available.

### 5. Outputs
The resulting binary masks are saved as georeferenced TIFFs:
- `flood_11jul_baseline.tif`
- `flood_18jul_onset.tif`
- `flood_22jul_active.tif`

These are then exported to transparent PNGs (`export_overlays.py`) for lightweight rendering in the browser dashboard.

## Assumptions and Limitations
- The thresholding approach is simplified for the prototype. Real-world SAR flood mapping requires complex statistical change-detection against the pre-flood baseline.
- False positives may occur in areas with smooth, dry surfaces (like sandbars) or radar shadow from mountains.
- The 28 July scene was corrupted in the source data and is simulated/omitted in the live prototype layer toggle.
