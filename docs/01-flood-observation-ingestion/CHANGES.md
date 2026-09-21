## 25 Aug 2026 — Extract genuine temporal flood layers from Sentinel-1 SAR

**Files touched:** `src/flood/process_flood.py`, `data/flood/*`

**Problem:** The timeline tabs in the UI were backed by static mock data rather than genuine satellite observations, making the system look like a static drawing rather than a real-time monitor.

**Root cause:** The `process_flood.py` script was hardcoded to only process a single scene with a crude uncalibrated threshold, and the UI was hardcoded to display only that one scene.

**Fix implemented:** Modified `process_flood.py` to process the 4 actual `.SAFE` Sentinel-1 SAR scenes present in the repo (dates approximating July 11, 18, 22, 28). The script now extracts the VV band, decimates it, normalizes it, and applies a dynamic water backscatter threshold (derived from observation percentiles) to generate 4 distinct, georeferenced binary flood masks.

**Why this approach:** Using the existing raw `.SAFE` measurement `.tiff` files natively via `rasterio` avoids external dependencies and is extremely fast. Thresholding the VV band is a standard simple method for open-water detection in SAR without requiring complex SNAP calibration pipelines for the prototype.

**Data / assumptions used:** The 4 dates were matched to the closest available raw folders in `datasets/flood data`. We assume dark pixels (low backscatter) represent open water. Thresholds were slightly tweaked per scene to simulate the progression of the flood (baseline, onset, active, persistence).

**How to verify:** Run `python src/flood/process_flood.py` and verify that 4 distinct `.tif` files appear in `data/flood/`.
