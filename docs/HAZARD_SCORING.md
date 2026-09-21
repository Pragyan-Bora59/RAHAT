# Explainable Hazard Scoring

The RAHAT system uses a transparent, weighted multi-criteria approach to generate the Red-Zone hazard map. This ensures that every classification can be explained to emergency commanders without relying on opaque machine learning models.

## Input Features

The scoring system (`src/hazard/score_hazard.py`) ingests three primary layers:
1. **Flood Extent (`flood_22jul_active.tif`)**: The observed inundation mask derived from Sentinel-1.
2. **Elevation (`dem.tif`)**: Bare-earth elevation from the COP30 DEM.
3. **Slope (`slope.tif`)**: The calculated steepness of the terrain.

## Normalization and Weights

Because elevation and slope operate on different scales, they are normalized. 
- Lower elevations represent higher risk (water pools at the bottom).
- Lower slopes represent higher risk (flat areas drain slowly).

The weights are defined externally in `config/hazard_weights.yaml` so they can be easily tuned by experts without altering the code:

```yaml
weights:
  flood_presence: 0.60
  elevation_penalty: 0.25
  slope_penalty: 0.15
```

## The Scoring Formula

For every pixel, a raw continuous score is calculated:

`Raw Score = (Flood * 0.60) + (Normalized_Elev_Penalty * 0.25) + (Normalized_Slope_Penalty * 0.15)`

## Classification Thresholds

The continuous score is then bucketed into four actionable classes based on defined thresholds:

- **Class 4 (Red Zone) - Critical Hazard**: Score >= 0.70. Areas actively flooded in low-lying, flat terrain.
- **Class 3 (Orange Zone) - High Hazard**: Score >= 0.50. Areas near floodwaters or at high risk due to terrain.
- **Class 2 (Yellow Zone) - Moderate Hazard**: Score >= 0.30. Areas with elevated risk but currently dry or on slight slopes.
- **Class 1 (Green Zone) - Low/No Hazard**: Score < 0.30. Safe, elevated terrain.

## Explaining a Red Zone
If a commander asks "Why is this village in a Red Zone?", the system's logic dictates:
"The area is currently showing active inundation from the July 22 satellite pass (60% weight). Furthermore, it sits at a critically low elevation relative to the district (25% weight) and is on completely flat terrain (15% weight), meaning the water will not drain and poses an immediate threat to life."
