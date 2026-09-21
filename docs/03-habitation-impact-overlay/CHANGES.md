## 25 Aug 2026 — Dynamic spatial join for habitation impact

**Files touched:** `src/habitation/assess_exposure.py`, `outputs/tables/habitation_exposure.csv`, `public/geojson/habitations.geojson`

**Problem:** Habitations were hardcoded to always show up as "Red / Critical" regardless of the selected date or their physical location on the map.

**Root cause:** The dashboard UI used static arrays and the python script originally only performed a point-in-polygon check for a single hardcoded mask (22 Jul).

**Fix implemented:** Modified `assess_exposure.py` to iterate through the 4 newly generated temporal hazard maps (`hazard_map_11jul.tif`, etc.). It performs a spatial intersection of the habitation coordinates against the raster for each date. The output `habitations.geojson` now contains a `status` dictionary storing the per-date `hazard_class`.

**Why this approach:** By baking the per-date statuses into a single GeoJSON, the frontend can instantly toggle the visual colors of the markers without reloading multiple files, ensuring a snappy prototype feel while still using 100% computed data.

**Data / assumptions used:** We assume the habitation point coordinates are representative of the village center. A village is assigned the exact hazard pixel value it lands on.

**How to verify:** Run `python src/habitation/assess_exposure.py` and inspect `public/geojson/habitations.geojson`. The properties object should have a `status` dictionary with 4 dates.
