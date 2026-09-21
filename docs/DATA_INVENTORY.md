# RAHAT Data Inventory

This inventory documents all available spatial and operational datasets discovered in the workspace prior to prototype development.

## 1. Sentinel-1 Flood Observations (SAR Data)
* **July 10, 2026 (~11 July PRE-FLOOD):** `datasets/flood data/july 10/S1D_IW_GRDH_...F7D3.SAFE`
  * **Type:** Sentinel-1 GRDH Level-1
  * **Intended Use:** Pre-flood baseline condition.
  * **Preprocessing:** SNAP/Python workflow (Orbit, Calibration, Terrain Correction, dB).
* **July 17, 2026 (18 July ONSET):** `datasets/flood data/july17/S1D_IW_GRDH_...7B2A.SAFE`
  * **Type:** Sentinel-1 GRDH Level-1
  * **Intended Use:** Flood onset / initial expansion.
* **July 22, 2026 (ACTIVE FLOOD):** `datasets/flood data/july22/S1D_IW_GRDH_...6A41.SAFE`
  * **Type:** Sentinel-1 GRDH Level-1
  * **Intended Use:** Active flood state / Red-zone mapping.
* **July 28/29, 2026 (LATE FLOOD / PERSISTENCE):** `datasets/flood data/july22/S1D_...D90B.zip.crdownload`
  * **Type:** ❌ **MISSING / CORRUPTED** (.crdownload)
  * **Note:** The persistence/late flood dataset failed to download completely. We will need to re-download this to complete the temporal sequence, or simulate/adjust the temporal methodology for the 4th state.

## 2. Terrain & Physics
* **COP30 DEM:** `datasets/DEM/rasters_COP30.tar.gz`
  * **Type:** GeoTIFF (compressed)
  * **Intended Use:** Elevation, Slope, Flow Direction, Flow Accumulation.
  * **Preprocessing:** Decompression, clipping to Dhemaji, derivation of terrain metrics.

## 3. Habitations, Population & Boundaries
* **Administrative Boundaries:** `datasets/DEM/districtshape/` (.shp, .dbf)
  * **Intended Use:** Dhemaji district mask.
* **Population / Census 2011:** `datasets/population/PCA_CDB_1809_F_Census.xls`
  * **Type:** Tabular (Excel)
  * **Intended Use:** Extract demographic baseline for affected habitations.
* **Villages / Habitations:** ❌ **MISSING**
  * **Note:** A dedicated point/polygon layer for villages is missing. Will require extracting points from Census data or using a placeholder scenario point-set for the Jonai–Murkongselek cluster.

## 4. Infrastructure & Accessibility
* **Roads Network:** `datasets/roads and infrastructure/SOI_Roads.parquet` (and Bridges, Causeways, Culverts).
  * **Type:** GeoParquet (Survey of India).
  * **Intended Use:** Road graph construction, accessibility scoring, routing optimization.
* **Rivers / Waterways:** `datasets/Healthcare/waterways+ps/north-eastern-zone-260822-free.gpkg.zip`
  * **Type:** GeoPackage.
  * **Intended Use:** Background context and waterway access.

## 5. Government Facilities & Response Bases
* **Healthcare Facilities:** `datasets/Healthcare/INDIA_HEALTH_FACILITIES_NIC.geojson`
  * **Type:** GeoJSON
  * **Intended Use:** Medical urgency assessment and safe destinations.
* **Police Stations:** `datasets/police stations/INDIA_POLICE_STATIONS.geojson`
  * **Type:** GeoJSON
  * **Intended Use:** Incident response bases.
* **Shelters / Relief Camps:** Data embedded in `current_resource_inventory_updated.csv` and PDF reports.
  * **Intended Use:** Candidate safe destinations for relocation.

## 6. Official Government Resource Baseline
* **Resource Inventory:** `datasets/shelters and resources/current_resource_inventory_updated.csv`
  * **Type:** CSV
  * **Source:** Extracted from Dhemaji DDMP 2024-25.
  * **Intended Use:** Baseline capacity for rescue teams, boats, and relief supplies.
