## 25 Aug 2026 — Real vector network integration (Roads & Bridges)

**Files touched:** `src/routing/build_graph.py`, `public/data/graph.json`, `public/geojson/roads.geojson`, `public/geojson/bridges.geojson`

**Problem:** The original prototype rendered a purely synthetic, abstract "hub-and-spoke" line network between habitations instead of real roads, and didn't map critical infrastructure like bridges.

**Root cause:** The backend didn't parse the provided OSM geodatabases (Survey of India Parquet files).

**Fix implemented:** Modified `build_graph.py` to:
1. Load `SOI_Roads.parquet` and `SOI_Bridges.parquet` using pandas.
2. Filter millions of rows in sub-seconds by directly querying the `bbox` struct for the Jonai cluster bounding box (approx Lon: 94.8-95.3, Lat: 27.6-27.9).
3. Use `shapely.wkb` to parse the Well-Known Binary geometry and extract coordinates for only the local subset.
4. Construct a NetworkX graph where road segment vertices become graph nodes and LineStrings become edges with exact haversine distances as weights.
5. Snap the Representative Habitations and the Response Base to the nearest road nodes to join them to the graph.

**Why this approach:** Using actual roads grounds the optimization demo in reality. Filtering by bounding box *before* parsing WKB ensures the script runs in seconds instead of minutes, which is crucial for a fast demo reset.

**Data / assumptions used:** We assume any extracted `LineString` from the dataset is a traversable road for boats/IRBs during floods. Distance is calculated via Haversine.

**How to verify:** Run `python src/routing/build_graph.py`. The output will log ~144 roads and ~147 bridges extracted. The dashboard map will now display the intricate actual road layout instead of straight abstract lines.
