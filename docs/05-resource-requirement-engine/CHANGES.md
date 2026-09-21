## 25 Aug 2026 - Explainable resource requirement engine

**Files touched:** `src/needs/prioritize.py`, `public/data/needs_*.json`

**Problem:** The dashboard only showed what resources were available (Official Government Baseline), but had no way of knowing what was actually *needed*, making gap analysis impossible.

**Root cause:** The backend didn't translate the affected population numbers into concrete physical requirements.

**Fix implemented:** Rewrote `prioritize.py` to calculate explicit quantitative requirements for each habitation per date. The requirements use transparent, explainable formulas:
- Food: 0.5 kg (rice/dal) per affected person per day.
- Water: 3.0 liters per person per day.
- Medical: 1 mobile medical team per 500 affected people.
- Rescue Boats: 1 boat per 20 affected people (with a 1.5x multiplier if the habitation's accessibility is "Poor" due to Red Zone hazard).
These numbers are aggregated and output into `needs_11jul.json`, `needs_18jul.json`, etc.

**Why this approach:** Using transparent per-capita multipliers instead of a hidden ML algorithm directly satisfies the project's requirement for explainability. The commander can easily verify the math in their head. Grouping by date ensures the required resources properly scale up and down as the flood expands and recedes across the timeline.

**Data / assumptions used:** The per-capita rates are standard disaster response heuristics.

**How to verify:** Run `python src/needs/prioritize.py` and inspect the resulting `needs_[date].json` files. They should contain an `aggregate_needs` block with the computed totals.

---

## 26 Aug 2026 - Advanced Priority Scoring and Logistics

**Files touched:** `src/needs/prioritize.py`, `public/data/needs_*.json`

**Problem:** The prioritization score was a simple combination of hazard class and population. It did not account for vulnerable demographics like children. Additionally, the boat requirement calculation assumed one round trip per boat, leading to inflated numbers.

**Fix implemented:** 
- **Cost Function:** Updated the sorting `score` in `prioritize.py`. The formula is now `score = (hazard_class * 50) + (children_est * 0.5) + (affected_pop * 0.1)`. This heavily weights the hazard severity, followed by the estimated number of children, and then general population.
- **Children Estimation:** Added logic to estimate children as 30% of the affected population.
- **Boat Logistics:** Updated the boat requirement calculation to account for multiple trips per day (`TRIPS_PER_BOAT_DAY = 5`). The new formula is `boats = affected_pop / (PERSONS_PER_BOAT * TRIPS_PER_BOAT_DAY)`.

**Why this approach:** This creates a more realistic and nuanced logistical framework. Prioritizing children introduces a crucial humanitarian variable into the algorithm.

**How to verify:** Run `python src/needs/prioritize.py` and verify the `needs_[date].json` outputs contain the `children_est` field and that the order of `habitations` reflects the new heavily weighted cost function.
