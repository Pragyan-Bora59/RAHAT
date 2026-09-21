# RAHAT Concepts & Learning Notes

This document explains the core concepts behind the RAHAT prototype. It is designed to help the SIH presentation team understand the "why" and "how" of the system.

## 1. Sentinel-1 SAR and Flood Mapping

### What it is
Sentinel-1 is a constellation of radar satellites operated by the European Space Agency. SAR (Synthetic Aperture Radar) uses microwaves to "see" the Earth's surface regardless of cloud cover or darkness.

### Why RAHAT uses it
During monsoon floods in Assam, the sky is perpetually cloudy. Optical satellites (like Sentinel-2 or Landsat) cannot see the ground. SAR can penetrate the clouds, making it the only reliable way to map active floods.

### How it works conceptually
SAR emits a radar pulse and measures the backscatter (the energy reflected back). Water acts like a mirror—it reflects the radar pulse away from the satellite, resulting in very low backscatter (it appears black in the imagery). Land and vegetation scatter the pulse in many directions, returning a stronger signal (appearing gray/white).

### Implementation
We use four temporal states (Pre-flood baseline, Onset, Active, Persistence). By comparing the active flood image against the pre-flood baseline, we can isolate the pixels that suddenly turned dark, identifying them as new floodwaters.

### Assumptions & Limitations
- **Assumption:** Dark areas that appear during the flood event are water.
- **Limitation:** Very smooth surfaces (like airport runways or dry sand) can also appear dark (false positives). Flooded forests might appear bright because the water bounces the signal into the tree trunks and back to the satellite (double-bounce effect, causing false negatives).

---

## 2. Digital Elevation Model (DEM) & Terrain Analysis

### What it is
A DEM (like Copernicus COP30) is a 3D grid representing the bare-earth elevation of the terrain.

### Why RAHAT uses it
Floods are driven by gravity. Understanding the terrain helps explain *why* an area is flooded, *how severe* the hazard is, and *which roads* are likely to be submerged.

### How it works conceptually
- **Elevation:** Lower areas are more prone to flooding.
- **Slope:** Flat areas accumulate water; steep areas drain quickly.
- **Flow Accumulation:** Simulates where water will naturally gather based on the topography.

### Implementation
We use `rasterio` and NumPy arrays to compute the slope from the DEM using a finite-difference gradient. We then use this slope as a physical penalty factor in the Hazard Scoring module.

---

## 3. Explainable Hazard Scoring

### What it is
A multi-criteria evaluation system that assigns a risk class (Green, Yellow, Orange, Red) to every pixel.

### Why RAHAT uses it
We cannot rely on a "Black Box" Machine Learning model. Emergency responders need to know *why* an area is classified as high risk. If a rescue boat is deployed, the commander must trust the rationale.

### Implementation
We use a weighted overlay approach defined in `config/hazard_weights.yaml`. 
For example: `Score = (Flood Presence * 0.5) + (Low Elevation * 0.3) + (Low Slope * 0.2)`.
This makes the output entirely traceable and transparent.

---

## 4. Accessibility and Network Graphs

### What it is
A mathematical representation of the road network. Intersections/habitations are "Nodes," and the roads connecting them are "Edges."

### Why RAHAT uses it
To deliver relief, we need to know the fastest route. In floods, the shortest physical distance is often blocked or submerged.

### Implementation
We use Dijkstra's algorithm to find the shortest path from the Relief Base to the Priority Habitation. When a road is simulated as "closed" due to flooding, the edge is removed from the graph, and the algorithm re-calculates the next best alternative (re-optimization).

---

## 5. HTML/CSS/TypeScript Architecture

### What it is
The frontend technologies used to build the command dashboard.

### Why RAHAT uses it
To provide a lightweight, browser-based interface without the overhead of heavy frameworks like React or Angular. This ensures fast load times and simple deployment, ideal for government command centers running on modest hardware.

### Implementation
- **State Management:** A simple TypeScript state object tracks the selected time period and UI toggles.
- **Leaflet Map:** Used to render the base map, raster overlays (PNG exports of the TIFFs), and GeoJSON vectors (roads, habitations).
- **Client-Side Simulation:** When the user clicks "Simulate Road Closure," the frontend reads the pre-calculated `optimization_scenario.json` and instantly updates the route visualization and metric panels via DOM manipulation.
