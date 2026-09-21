## 25 Aug 2026 — Generate dynamic temporal hazard maps

**Files touched:** `src/hazard/score_hazard.py`, `data/flood/hazard_map_*.tif`

**Problem:** The single Hazard Map was previously generated from only one hardcoded flood mask (22 Jul), so when users switched timeline tabs, the hazard colorations didn't reflect the selected date.

**Root cause:** The `score_hazard.py` pipeline was built for a single state and did not iterate through the different temporal outputs from the flood module.

**Fix implemented:** Refactored `score_hazard.py` to iterate over all four flood masks (`11jul`, `18jul`, `22jul`, `28jul`). The script aligns each date's mask to the master DEM grid and applies the physics-based scoring (flood + elevation + slope + flow accumulation) to generate a separate `hazard_map_*.tif` for each stage.

**Why this approach:** This aligns the physical hazard calculation strictly with the actual temporal satellite observation. It proves to the judges that the "Red Zones" genuinely shift based on where the water is currently observed, modified by the terrain.

**Data / assumptions used:** Assumes the DEM (COP30) and derived terrain features (Slope, Flow) are constant across the 18 days, while the water mask changes.

**How to verify:** Run `python src/hazard/score_hazard.py` and verify that 4 distinct hazard `.tif` files appear in `data/flood/`.
