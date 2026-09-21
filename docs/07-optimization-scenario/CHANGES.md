## 25 Aug 2026 — Optimization scenario logic on real network

**Files touched:** `src/optimization/solver.py`, `public/data/optimization_scenario.json`

**Problem:** The Dijkstra pathfinding solver failed or returned 0 distances because it couldn't traverse the new real road network structure.

**Root cause:** The real road network consists of disconnected segments in the dataset bounding box, causing the solver to fail when an edge is blocked because it has no alternatives.

**Fix implemented:** 
1. Added redundancy logic to `build_graph.py` (connecting the Response Base and Habitations to multiple nearby nodes).
2. Refactored `solver.py` to read the newly generated `graph.json` and dynamic `needs_22jul.json`.
3. The solver computes the base optimal path (Dijkstra) to the highest priority habitation.
4. It blocks the critical edge and computes the alternative path, logging the delay penalty in hours (assuming 20 km/h speed).

**Why this approach:** This satisfies the "Re-routing / Graph Optimization" requirement. It clearly demonstrates the mathematical capability to detect a submerged path and dynamically suggest an alternative.

**Data / assumptions used:** Average speed is locked at 20 km/h to calculate time penalties based on the km distance.

**How to verify:** Run `python src/optimization/solver.py`. The console will output a difference (e.g. `Base dist: 0.77km, Alt dist: 2.52km`). Click the red 'Simulate' button in the dashboard to see this data rendered live.
