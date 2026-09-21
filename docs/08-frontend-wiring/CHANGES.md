## 25 Aug 2026 - UI dynamic integration

**Files touched:** `src/dashboard/index.html`, `src/dashboard/ts/main.js`

**Problem:** The UI was previously static, relying on hardcoded numbers and single files that didn't change when clicking the timeline buttons.

**Root cause:** The timeline buttons only swapped the flood image overlay and didn't trigger data refetches.

**Fix implemented:**
1. Modified `main.js` to dynamically fetch the correct `needs_[date].json` based on the selected timeline state.
2. Updated the habitation markers on the map to change colors and tooltip values dynamically based on the current date's hazard class and affected population.
3. Added the real `bridges.geojson` to the Leaflet map as small markers to visualize critical choke points.
4. Added new metric cards in `index.html` to display the newly computed aggregate requirements (e.g., Food Required, Rescue Boats Required) which update per date.
5. Wired the "Simulate Road Closure" button to use the new `optimization_scenario.json` outputted by the Dijkstra solver on the real road network.

**Why this approach:** It creates a "living" dashboard that reacts to time progression exactly how a real commander would need during an evolving emergency, without the overhead of a full backend database.

**Data / assumptions used:** The UI assumes the backend scripts (Modules 01 to 07) have been run to generate all the necessary static JSONs in `public/`.

**How to verify:** Open the dashboard in a browser. Click the timeline buttons (11 Jul to 28 Jul). Observe the habitations changing colors, the Affected Population updating, the Required Resources updating, and the top priority table shifting. Click the "Simulate Road Closure" button to see the route dynamically snap to the alternative path.

---

## 26 Aug 2026 - Interactive Dynamic Re-routing & Facility Routing

**Files touched:** `src/dashboard/index.html`, `src/dashboard/ts/main.js`

**Problem:** 
1. The road blockage feature only acted on a hardcoded road segment. 
2. Blocking a road only updated the visual UI and didn't immediately recalculate active routes (evacuation or custom).
3. The user could not route to nearest critical facilities like Hospitals or Police Stations.

**Fix implemented:**
1. **Dynamic Re-routing:** Updated the `btn-block-road` listener in `main.js` to read the road ID from a new input field (`input-block-road`). Modified `calculateCustomRoute` and `calculateEvacuationRoute`'s internal Dijkstra algorithm to completely ignore the edge matching `state.blockedEdgeId`. Re-wired the listeners to automatically re-trigger the active route if a block is placed or lifted.
2. **Facility Routing:** Added "Nearest Hospital" and "Nearest Police" buttons under the Evacuation planner. Implemented `calculateFacilityRoute(sourceName, facilityType)` in `main.js` which runs a Dijkstra pathfinding scan across the road graph targeting nodes where `type === 'hospital'` or `type === 'police'`.
3. **UI Enhancements:** Highlighted the "Req. Water" metric in the top dashboard and updated the leaflet popups to expose the new Children Estimates and Boat Logistics calculations.
4. **Map-Click Interaction:** Removed the manual text input for blocking roads. Instead, users can now directly click on any road segment or bridge on the Leaflet map to open a popup that allows them to block/unblock that specific segment immediately. The system automatically finds the closest road edge to a clicked bridge.
5. **Clickability UX Improvements:** Increased the visual weights of the road networks (2 -> 4) and the circle radii of the habitations (7 -> 9), bridges (4 -> 6), and facilities (6 -> 8) to make clicking them with a mouse significantly easier without needing to zoom in aggressively.

**Why this approach:** Making routing responsive directly in the frontend via a JS Dijkstra implementation allows for instant, interactive planning without requiring a backend server. Map-click interactions provide a vastly superior UX for incident commanders compared to typing in raw edge IDs.

**How to verify:** Enter an active route using Evacuation or Custom routing. Click on any road segment or bridge marker on the map to open its popup, then click the "Block" button. The route will instantly snap to an alternative path avoiding that segment.
