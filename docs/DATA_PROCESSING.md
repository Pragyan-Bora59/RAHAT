# Data Processing Pipeline

This document traces how raw data in the RAHAT prototype moves from initial files to the browser dashboard.

## 1. Sentinel-1 SAR Data
**Raw:** `.tif` GeoTIFFs (11 Jul, 18 Jul, 22 Jul). (Note: 28 Jul was corrupted in source and is handled as a fallback in UI).
**Processing:** `src/flood/process_flood.py`
**Transformation:** Hard threshold (`< 0.1`) is applied to extract dark water pixels. Outputs binary `flood_[date].tif`.
**Browser Export:** `src/dashboard/export_overlays.py` converts these TIFFs into transparent `PNG` images (colored blue) and extracts the geographical bounding box to `bounds.json`.
**Dashboard:** Leaflet uses `L.imageOverlay` to map the PNG precisely over the basemap.

## 2. Terrain Data (DEM)
**Raw:** `COP30_Jonai.tif`
**Processing:** `src/terrain/process_dem.py`
**Transformation:** `numpy.gradient` derives slope magnitude from elevation pixels. Outputs `dem.tif` and `slope.tif`.
**Usage:** Fed directly into the Hazard Scoring module.

## 3. Hazard Scoring
**Raw:** `flood_22jul_active.tif`, `dem.tif`, `slope.tif`
**Processing:** `src/hazard/score_hazard.py`
**Transformation:** Min-Max normalization and weighted overlay to produce `hazard_map.tif` (classes 1-4).
**Browser Export:** Exported to `hazard_map.png` with a Green/Yellow/Orange/Red colormap.

## 4. Habitations
**Raw:** Synthesized representative coordinates for Jonai-Murkongselek.
**Processing:** `src/habitation/assess_exposure.py`
**Transformation:** Intersects point coordinates with the `hazard_map.tif` to determine the village's risk class. Generates random population data for scenario purposes.
**Browser Export:** Outputs `public/geojson/habitations.geojson`.

## 5. Needs and Resources
**Raw:** `current_resource_inventory.csv` (from DDMP).
**Processing:** `src/needs/prioritize.py` and `src/resources/prepare_baseline.py`
**Transformation:** Cleans columns, sorts by hazard priority, and generates JSON endpoints.
**Browser Export:** Outputs `public/data/needs.json` and `public/data/resources.json`.

## 6. Road Network and Optimization
**Raw:** Built from habitation geometries to ensure a routable topological graph for the UI. (The raw 2.5 million row GeoParquet was bypassed to maintain prototype speed and stability).
**Processing:** `src/routing/build_graph.py` and `src/optimization/solver.py`
**Transformation:** Creates nodes/edges, calculates Haversine distances, runs Dijkstra's algorithm for base and blocked scenarios.
**Browser Export:** Outputs `public/data/graph.json`, `public/data/optimization_scenario.json`, and `public/geojson/roads.geojson`.
