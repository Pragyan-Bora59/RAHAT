# RAHAT — SIH26191 Prototype

**Flood Hazard-Based Red-Zone Identification & Emergency Response Optimization System**
Built for the Smart India Hackathon (SIH26191 — Ministry of Home Affairs).

## Overview
RAHAT is an operational command tool that converts raw Sentinel-1 satellite observations into explainable emergency response plans. It identifies flood hazard red zones, assesses vulnerable habitations, and optimizes rescue/relief routing using official government resource baselines.

The detailed demonstration cluster is **Jonai–Murkongselek, Dhemaji District, Assam**.

## Architecture & Major Modules
1. **Flood Processing (`src/flood/`)**: Extracts binary flood masks from 4 temporal Sentinel-1 SAR observations.
2. **Terrain Analysis (`src/terrain/`)**: Derives physical gradients (slope) from the COP30 DEM.
3. **Hazard Scoring (`src/hazard/`)**: Computes a transparent, weighted Red-Zone map (Green, Yellow, Orange, Red) based on flood presence, low elevation, and flat slopes.
4. **Exposure & Needs (`src/habitation/`, `src/needs/`)**: Intersects habitations with the hazard map to prioritize rescue and medical needs.
5. **Optimization (`src/optimization/`, `src/routing/`)**: Solves a logistical network graph using Dijkstra's algorithm to route resources and simulates road-closure disruptions.
6. **Command Dashboard (`src/dashboard/`)**: A pure HTML/CSS/TypeScript frontend to visualize the data and present recommendations to commanders.

## Data Sources
- **Observed:** Sentinel-1 SAR (July 2026 Dhemaji event)
- **Observed:** Copernicus 30m DEM (COP30)
- **Official Government Baseline:** DDMP Dhemaji 2024-25 (Shelters, SDRF, Resources)
- **Derived:** Hazard Maps, Flood Masks, Route Graphs

## Installation and Execution

### Requirements
- Python 3.10+
- `rasterio`, `numpy`, `pillow` (for backend processing)
- Node.js & npm (for frontend dashboard)

### 1. Run Data Pipeline
If you wish to re-generate the data from the raw datasets:
```bash
python src/flood/process_flood.py
python src/terrain/process_dem.py
python src/hazard/score_hazard.py
python src/habitation/assess_exposure.py
python src/needs/prioritize.py
python src/resources/prepare_baseline.py
python src/routing/build_graph.py
python src/optimization/solver.py
python src/dashboard/export_overlays.py
```

### 2. Run the Dashboard
```bash
npm install
npm run dev
```
Open `http://localhost:3000` in your browser.

## Documentation
Please refer to the `docs/` directory for exhaustive explanations of the methodology, code, and concepts:
- `docs/CONCEPTS.md`: Theoretical learning notes.
- `docs/CODE_EXPLANATION.md`: How the major scripts work.
- `docs/DATA_PROCESSING.md`: The complete data pipeline.
- `docs/FLOOD_METHOD.md`: SAR change-detection methodology.
- `docs/HAZARD_SCORING.md`: Explainable weighted-overlay logic.
- `docs/OPTIMIZATION.md`: Network routing and disruption simulation.
- `docs/DEMO_SCRIPT.md`: Guide for presenting the project.

## Known Limitations
- The 28 July SAR dataset was corrupted in the source and is handled gracefully as a fallback in the UI.
- The routing network uses a synthetic simplified topology for the prototype to avoid complex WKB parsing of the 2.5 million row GeoParquet without heavy GIS libraries.
- The population values for the specific representative coordinates are scenario approximations for demonstration purposes.
