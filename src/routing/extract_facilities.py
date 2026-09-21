import os
import json

def extract_facilities():
    # Jonai cluster bbox
    min_lon, max_lon = 94.8, 95.3
    min_lat, max_lat = 27.6, 27.9
    
    out_dir = r"d:\flood\public\geojson"
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Police Stations
    police_path = r"d:\flood\datasets\police stations\INDIA_POLICE_STATIONS.geojson"
    police_features = []
    if os.path.exists(police_path):
        with open(police_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for feature in data.get('features', []):
                coords = feature['geometry']['coordinates']
                lon, lat = coords[0], coords[1]
                if min_lon <= lon <= max_lon and min_lat <= lat <= max_lat:
                    police_features.append(feature)
                    
    with open(os.path.join(out_dir, "police.geojson"), 'w', encoding='utf-8') as f:
        json.dump({"type": "FeatureCollection", "features": police_features}, f, indent=2)
        
    print(f"Extracted {len(police_features)} police stations.")
    
    # 2. Hospitals
    hosp_path = r"d:\flood\datasets\Healthcare\INDIA_HEALTH_FACILITIES_NIC.geojson"
    hosp_features = []
    if os.path.exists(hosp_path):
        with open(hosp_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for feature in data.get('features', []):
                if not feature.get('geometry'): continue
                coords = feature['geometry']['coordinates']
                lon, lat = coords[0], coords[1]
                if min_lon <= lon <= max_lon and min_lat <= lat <= max_lat:
                    hosp_features.append(feature)
                    
    with open(os.path.join(out_dir, "hospitals.geojson"), 'w', encoding='utf-8') as f:
        json.dump({"type": "FeatureCollection", "features": hosp_features}, f, indent=2)
        
    print(f"Extracted {len(hosp_features)} hospitals.")

if __name__ == "__main__":
    extract_facilities()
