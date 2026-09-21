# Code Explanation

This document explains the major scripts comprising the RAHAT system.

## 1. `src/flood/process_flood.py`
**Purpose:** Converts temporal Sentinel-1 SAR inputs into binary flood masks.
**Algorithm:**
- Iterates over the defined temporal sequence.
- Opens the TIFF using `rasterio`.
- Applies a hard threshold (`< 0.1` for backscatter products) to isolate dark pixels (water).
- Writes the resulting binary array `(1=Flood, 0=Dry)` back to disk as a new GeoTIFF with the original CRS and Transform.
**Why:** SAR backscatter over water drops dramatically due to specular reflection.

## 2. `src/terrain/process_dem.py`
**Purpose:** Derives physical terrain attributes from the COP30 DEM.
**Algorithm:**
- Uses `numpy.gradient` to compute the spatial derivative (slope) in the X and Y directions.
- Calculates the magnitude of the gradient array.
**Why:** Slope dictates water behavior. Flat areas pool water; steep areas drain. This physical intuition grounds the hazard scoring.

## 3. `src/hazard/score_hazard.py`
**Purpose:** Combines flood and terrain data into the final 1-4 Red-Zone map.
**Algorithm:**
- Loads the weights from `config/hazard_weights.yaml`.
- Normalizes elevation (min-max scaling, inverted so low elevation = high penalty).
- Normalizes slope (inverted so flat slope = high penalty).
- Computes `(Flood * W1) + (Elev * W2) + (Slope * W3)`.
- Applies `np.where` thresholds to bucket into 1, 2, 3, or 4.
**Why:** A transparent, non-ML multi-criteria evaluation allows emergency commanders to trust the output.

## 4. `src/routing/build_graph.py`
**Purpose:** Constructs a road network connecting the Relief Base to the habitations.
**Algorithm:**
- Uses the Haversine formula to compute great-circle distance between coordinates.
- Generates node objects for habitations and a base.
- Generates edge objects connecting nodes, calculating the km distance as the edge weight.
- Outputs both a logical graph (`graph.json`) and a spatial layer (`roads.geojson`).
**Why:** Optimization requires a mathematically defined network.

## 5. `src/optimization/solver.py`
**Purpose:** Finds the optimal route for a priority mission and handles road closures.
**Algorithm:**
- Uses a priority queue (`heapq`) to implement Dijkstra's algorithm.
- Computes the shortest path from the Base to the target habitation.
- Simulates a disruption by identifying a critical edge in the path and removing it from the graph.
- Re-runs Dijkstra's to find the alternative route.
- Computes delays (`Distance / Speed`) and outputs metrics to `optimization_scenario.json`.

## 6. `src/dashboard/ts/main.ts`
**Purpose:** The single-screen command frontend.
**Logic:**
- Initializes Leaflet map (`L.map`).
- Uses `Promise.all` and `fetch` to load JSON/GeoJSON endpoints from `public/data/`.
- Overlays the flood TIFFs (exported as PNGs) using `L.imageOverlay`.
- Listens for DOM clicks on the "Simulate Road Closure" button.
- Updates the DOM metrics and redraws the `routesLayer` in red/cyan to visually explain the re-routing.
**Why:** Built in pure HTML/CSS/TypeScript for extreme portability without heavy frameworks like React, fitting the government-prototype constraint.
