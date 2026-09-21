# RAHAT Flood-Response Prototype: Datasets, APIs, and Sources

Here is a synchronized and categorized breakdown of the datasets, APIs, and their respective sources used in the RAHAT flood-response prototype for the Dhemaji district. 

### 1. Flood & Topographical Data
These datasets form the foundation for identifying flood extents, elevation drops, and calculating hazard scores.

| Dataset / API | Description | Primary Source | Link / Access |
| :--- | :--- | :--- | :--- |
| **Observed Flood Extent** | Historical and near-real-time inundation mapping. | **NRSC/NDEM (ISRO)** | NDEM Hydrological Portal |
| **Sentinel-1 SAR** (API) | Cloud-penetrating radar data used to programmatically generate flood masks. | **Google Earth Engine (GEE)** | `COPERNICUS/S1_GRD` collection via GEE API, or Copernicus Data Space |
| **Digital Elevation Model (DEM)** | 30m resolution terrain and slope data (Copernicus GLO-30). | **OpenTopography / AWS** | OpenTopography Portal or AWS S3 (`s3://raster/COP30/`) |
| **River/Drainage Network** | Hydrological context for the Brahmaputra floodplain (Jiadhal, Gainodi, etc.). | **India-WRIS / Bhuvan** | Bhuvan Water Sector |

### 2. Administrative & Demographic Data
Used to map the boundaries of the district and calculate population exposure to prioritize needs.

| Dataset / API | Description | Primary Source | Link / Access |
| :--- | :--- | :--- | :--- |
| **Admin Boundaries & Habitations** | District, block, panchayat, and village/habitation boundaries (600,000+ points). | **India Geodata** (Community-maintained) | India Geodata GitHub |
| **Baseline Population** | Official village-wise population, household, and demographic data. | **Census 2011 (data.gov.in)** | Primary Census Abstract - Assam |
| **Gridded Population** | 100m/1km resolution population estimates for geospatial clipping. | **WorldPop** | WorldPop India Counts |

### 3. Infrastructure & Transport Data
Crucial for building the road graph, generating routes using the Dijkstra algorithm, and simulating road/bridge blockages.

| Dataset / API | Description | Primary Source | Link / Access |
| :--- | :--- | :--- | :--- |
| **Road Network** | Routable road geometries (PMGSY/GeoSadak rural roads, highways). | **OpenStreetMap (Geofabrik)** | Geofabrik NE-Zone Extract |
| **Bridge Infrastructure** | Specific coordinates of bridges to simulate chokepoints and structural failures. | **Overpass API** (OSM) | Overpass Turbo query: `way["bridge"](area:...)` |

### 4. Emergency, Health & Relief Data
Used as the "source" nodes for dispatching resources (medical teams, boats, food, water) to the affected habitations.

| Dataset / API | Description | Primary Source | Link / Access |
| :--- | :--- | :--- | :--- |
| **Shelters / Relief Centres** | List of official flood shelters and relief camps. | **Dhemaji DDMP** | Dhemaji Disaster Management Plan 2024-25 (PDF) |
| **Hospitals (PHCs/CHCs)** | Public health facilities used as hubs for medical dispatch. | **Assam Health Dept / India Geodata** | India Geodata Repo |
| **Police / Fire Stations** | Dispatch bases for rescue boats and personnel. | **India Geodata / OSM** | Filtered `amenity=police` via OSM/Geofabrik |
| **Resource Inventory** | Real-time quantities of food, water, boats, and medical teams available at bases. | **Internal Operational Data** | Generated internally (JSON table) based on actual physical stockpiles. |

*(Current Resource Distribution in the Prototype)*:
- **Jonai Response Base**: 1,200,000 kg of Food, 15,000 Liters of Water, 36 Rescue Boats. *(Aggregated from FCI Godown & PHE Division)*
- **Police Stations**: 40 Rescue Boats.
- **Jonai CHC (Hospital)**: 6 Medical Teams.
- **Dhemaji HQ**: 1 Rescue Boat.

### Summary of APIs Used in the Pipeline:
1. **Google Earth Engine (GEE) Python API**: Used to programmatically pull Sentinel-1 satellite imagery and calculate the Otsu threshold to generate binary flood masks.
2. **Overpass API (Overpass Turbo)**: Used to query OpenStreetMap data dynamically (specifically extracting tagged items like `bridge=yes`, `amenity=hospital`, or `amenity=police` within the Dhemaji bounding box).
3. **Leaflet.js API**: The frontend mapping library used to synchronize and render all of the above GeoJSON layers (roads, flood masks, nodes, and custom dynamic routing lines) onto the interactive dashboard.
