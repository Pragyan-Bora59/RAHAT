# Dhemaji Flood Response — Dataset Sources

Reference list of where to get each dataset from your table, with direct links and notes on how to narrow each one down to Dhemaji district / Assam.

---

## 1. Observed flood/inundation extent ⭐⭐⭐⭐⭐

**Primary — NRSC/NDEM (ISRO):**
- NDEM Flood Hazard Atlas (interactive, select state/district): https://ndem.nrsc.gov.in/hydrological_fhz.php
- NDEM Hydrological Disaster portal (NRT flood inundation, flood hazard atlas, flood affected area atlas): https://ndem.nrsc.gov.in/hydrologicaldisasters/index.php
- Requires free registration/login at https://ndem.nrsc.gov.in/login.php — Assam has a dedicated Flood Hazard Atlas covering 26 years of flood frequency, at state and district level.
- Bhuvan Disaster Services (flood layers, WMS): https://bhuvan.nrsc.gov.in/gis/thematic/index.php

**Secondary — Sentinel-1 SAR (for your own inundation mapping, cloud-penetrating, good for monsoon):**
- Copernicus Data Space Ecosystem (free registration, search + download GRD scenes): https://dataspace.copernicus.eu/
- Alaska Satellite Facility Vertex (alternate Sentinel-1 mirror, sometimes easier for bulk download): https://search.asf.alaska.edu/
- Google Earth Engine (`COPERNICUS/S1_GRD` collection) if you want to threshold VV backscatter directly in code without downloading scenes — practical for a Dhemaji/Brahmaputra AOI given the size of raw SAR files.
- Method reference (Otsu thresholding on VV band, applied specifically to Assam floods): https://link.springer.com/chapter/10.1007/978-3-030-75197-5_20

---

## 2. DEM ⭐⭐⭐⭐⭐

**Copernicus DEM GLO-30 (30m, recommended over SRTM — fewer voids, more current):**
- OpenTopography portal (GUI clip-and-download by bounding box): https://portal.opentopography.org/datasetMetadata?otCollectionID=OT.032021.4326.1
- Direct AWS S3 bucket (bulk/CLI): `s3://raster/COP30/` via `https://opentopography.s3.sdsc.edu`
- Google Earth Engine: `COPERNICUS/DEM/GLO30`

**SRTM (fallback, well-documented, slightly older):**
- USGS EarthExplorer: https://earthexplorer.usgs.gov/
- Also available through the OpenTopography portal above (same interface, different dataset).

For Dhemaji (~27.0–27.9°N, 94.2–95.2°E roughly), either portal lets you draw a bounding box directly — no need to download all of India.

---

## 3. Administrative boundaries ⭐⭐⭐⭐⭐
## 4. Villages / habitations ⭐⭐⭐⭐⭐

These two are best solved together — one source now covers both cleanly:

**Best single source — India Geodata (community-maintained, sourced from LGD/Survey of India/Bhuvan/DataMeet, CC0/CC-BY):**
- Browse/download: https://yashveeeeeeer.github.io/india-geodata/
- GitHub repo (raw files, parquet/geojsonl/shapefile): https://github.com/yashveeeeeeer/india-geodata
- Has districts, blocks/tehsils, panchayats, villages, and habitations (600,000+ points) as separate layers — filter to Dhemaji.

**Official/primary sources (if you need to cross-verify or cite government data specifically):**
- Local Government Directory (LGD), Ministry of Panchayati Raj — authoritative village/panchayat codes: https://lgdirectory.gov.in/
- data.gov.in — Village/Town-wise Primary Census Abstract 2011, Assam (includes village-level population + household data): https://www.data.gov.in/catalog/villagetown-wise-primary-census-abstract-2011-assam
- DataMeet community maps (district/village boundaries, geojson/shapefile): https://projects.datameet.org/maps/
- Dhemaji district's own DDMP (see #8 below) also lists the 5 development blocks, 65 Gaon Panchayats, and 952 revenue villages by name.

---

## 5. Population ⭐⭐⭐⭐⭐

**Census 2011 (official baseline):**
- data.gov.in village-wise Primary Census Abstract, Assam (same link as above — has population, literacy, SC/ST, worker categories per village): https://www.data.gov.in/catalog/villagetown-wise-primary-census-abstract-2011-assam
- Dhemaji district's official population page: https://dhemaji.gov.in/portlet-innerpage/population-2011-census

**Gridded population (for estimating exposed population under a flood polygon, rather than just per-village totals):**
- WorldPop India population counts (100m, 2020): https://hub.worldpop.org/geodata/summary?id=49804
- WorldPop India population density (1km): https://hub.worldpop.org/geodata/summary?id=46766

---

## 6. Road network ⭐⭐⭐⭐⭐
## 7. Bridges ⭐⭐⭐⭐⭐

**OpenStreetMap, via Geofabrik (updated daily, includes bridge tags on ways):**
- North-Eastern zone extract (Assam + neighbours — much smaller than all-India, recommended): https://download.geofabrik.de/asia/india/north-eastern-zone.html
- Full India extract (if you'd rather clip yourself): https://download.geofabrik.de/asia/india.html

**For bridges specifically**, roads alone won't separate them out — pull `bridge=yes` tagged ways via the Overpass API/Overpass Turbo rather than relying on the Geofabrik shapefile bridge layer, which is incomplete in rural NE India:
- Overpass Turbo (run a query bounded to Dhemaji, e.g. `way["bridge"](area:...)`): https://overpass-turbo.eu/
- India Geodata also has a compiled roads bundle (PMGSY/GeoSadak rural roads, national highways, ML-detected roads) if OSM coverage in rural Dhemaji turns out sparse: https://github.com/yashveeeeeeer/india-geodata

---

## 8. Shelters / relief centres ⭐⭐⭐⭐⭐

This is the one dataset that genuinely only exists in the district's own disaster plan — not on OSM or a geoportal.

**Dhemaji District Disaster Management Plan (DDMP) 2024-25 — direct PDF, includes flood shelter/relief centre lists:**
- https://asdma.assam.gov.in/sites/default/files/swf_utility_folder/departments/asdma_revenue_uneecopscloud_com_oid_70/menu/document/dhemaji_2024_25.pdf

**Previous year's DDMP (2022) as a cross-check / if the above is updated later:**
- https://asdma.assam.gov.in/sites/default/files/swf_utility_folder/departments/asdma_revenue_uneecopscloud_com_oid_70/menu/document/dm_plan_dhemaji_2022.pdf

**Assam SDMA document repository (in case a newer DDMP gets published):**
- https://asdma.assam.gov.in/documents-detail/disaster-management-plan

**Dhemaji District Disaster Management Authority (DDMA) page:**
- https://dhemaji.gov.in/portlets/district-disaster-management-authority

The shelter list in the DDMP is a table (usually GP-wise), not a clean CSV/shapefile — you'll need to extract it manually or with a PDF table-extraction pass, then geocode the names yourself.

---

## 9. Hospitals / health centres ⭐⭐⭐⭐

- India Geodata — public health facilities layer (PHCs, CHCs, etc.), same repo as above: https://github.com/yashveeeeeeer/india-geodata
- OSM (via the Geofabrik NE-zone extract in #6/#7 — filter `amenity=hospital` / `amenity=clinic`)
- Assam Health Department / dhemaji.gov.in health portlet for an official list of PHCs/CHCs in the district, to cross-check OSM/India-Geodata coverage (rural OSM health-facility tagging is often incomplete).

---

## 10. Police / fire / rescue facilities ⭐⭐⭐⭐

- India Geodata — police station locations (point layer, name + district attributes) and police jurisdiction boundaries: https://github.com/yashveeeeeeer/india-geodata
- OSM (`amenity=police`, `amenity=fire_station`) via the same NE-zone Geofabrik extract.
- Assam Fire & Emergency Services and district administration pages (dhemaji.gov.in) for official station lists if OSM/India-Geodata coverage is thin — rural fire/rescue points are one of the weaker layers in open data generally, so expect to supplement manually.

---

## 11. River / drainage network ⭐⭐⭐⭐

- OSM rivers/streams — same Geofabrik NE-zone extract (`waterway=river`/`stream`).
- Bhuvan Water Sector thematic services (WMS layers for drainage, watersheds): https://bhuvan.nrsc.gov.in/wiki/index.php/Water_Sector
- India-WRIS (Central Water Commission) — river basins, sub-basins, watersheds; useful for hydrological context beyond just the channel network, but bulk download is restricted (email-request for areas >200 sq km): https://cwc.gov.in/en/water-resources-information-system-wris
- India Geodata also bundles WRIS/SLUSI watershed boundaries and SOI/WRIS river network layers pre-compiled: https://github.com/yashveeeeeeer/india-geodata

Dhemaji sits directly in the Brahmaputra floodplain with the Jiadhal, Gainodi, Simen, Dihang, Sillë and Dimow rivers running through it — the DDMP (#8 above) has a detailed section naming and describing each of these, useful for validating your extracted river layer.

---

## 12. Current resource inventory ⭐⭐⭐⭐⭐

No external source — this is the operational dataset you build yourselves (food/water stock, vehicles, boats, rescue teams, their locations and capacities). Structure it early as its own table/schema (e.g. `resource_type, location, quantity, capacity, contact, last_updated`) so it can be joined against the shelter and population layers above once those are ready.

---

## Quick-start priority order

If you want to get a first working map fastest:
1. Admin boundaries + villages (#3/#4) — India Geodata, one download.
2. DEM (#2) — OpenTopography, one bounding-box clip.
3. Roads + rivers (#6/#7/#11) — Geofabrik NE-zone extract, one file, filter by tag.
4. Population (#5) — data.gov.in village PCA join to your village layer.
5. Flood extent (#1) — NDEM if you just need existing maps; Sentinel-1 via GEE if you want to derive your own.
6. Shelters (#8) — manual extraction from the DDMP PDF, since nothing else has it.
