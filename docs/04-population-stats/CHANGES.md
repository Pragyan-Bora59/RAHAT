## 25 Aug 2026 — Dynamic population exposure computation

**Files touched:** `src/habitation/assess_exposure.py`, `outputs/tables/habitation_exposure.csv`

**Problem:** The "Est. Affected Pop" was a static string "18,900" in the dashboard, and individual habitation populations didn't reflect the flood extent.

**Root cause:** No logic existed to proportionally estimate affected people based on the severity of the flood hitting the village.

**Fix implemented:** Inside `assess_exposure.py`, the `affected_pop` is now calculated dynamically per date using the following heuristic: `affected_population = habitation_population * impact_factor`. The `impact_factor` is explicitly tied to the underlying hazard class for that date (Red=90%, Orange=60%, Yellow=20%, Green=0%).

**Why this approach:** This satisfies the project requirement for an "explainable" calculation. Instead of a black box, a commander can see that a village in an orange zone is assumed to have 60% of its population exposed, and this math holds true across the temporal tabs.

**Data / assumptions used:** The baseline populations used for the representative coordinates are synthetic estimates representing roughly the Jonai block density, as exact Census polygon joins were out of scope. The impact ratios (0.9, 0.6, 0.2, 0.0) are transparent assumptions.

**How to verify:** Run `python src/habitation/assess_exposure.py` and inspect `outputs/tables/habitation_exposure.csv`. The `Affected_Pop` column should change based on the `Date` and `Hazard_Class`.
